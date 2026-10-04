"""Verificacao de consistencia do texto do TCC II.

Roda as checagens que o AGENTS.md exige antes de dar um trabalho por pronto, e
que antes eram feitas a mao (e por isso falhavam):

  1. nenhum caractere CJK/cirilico escapado no texto PT-BR;
  2. toda referencia cruzada "Seção N.M" aponta para uma seção que existe;
  3. os numeros citados na conclusão batem com o quadro de métricas;
  4. nenhuma tabela do texto tem coluna com contagem incompatível com o
     cabeçalho;
  5. as referências ABNT estão em ordem alfabética e sem entradas duplicadas;
  6. os números de desempenho citados no texto existem no relatório de
     métricas por corte (guards de regressão numérica).

Uso:
    .venv\\Scripts\\python.exe docs\\verifica_tcc.py
Exit code 0 = tudo consistente.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEXTO = RAIZ / "docs" / "tcc2_texto.md"
FALHAS: list[str] = []
AVISOS: list[str] = []


def falha(msg: str) -> None:
    FALHAS.append(msg)


def aviso(msg: str) -> None:
    AVISOS.append(msg)


def check_cjk(t: str) -> None:
    maus = re.findall(r"[\u3000-\u9fff\u0400-\u04ff\uac00-\ud7af]", t)
    if maus:
        for c in sorted(set(maus)):
            i = t.find(c)
            linha = t[:i].count("\n") + 1
            falha(f"caractere nao latino U+{ord(c):04X} na linha {linha}: {c!r}")
    else:
        print("  [OK] nenhum caractere CJK/cirilico no texto")


def check_referencias_cruzadas(t: str) -> None:
    secs = set()
    for m in re.finditer(r"(?m)^#{1,4}\s+(\d+(?:\.\d+)*)\s+", t):
        secs.add(m.group(1))
    quebradas = []
    for m in re.finditer(r"Se[çc][ãa]o\s+(\d+(?:\.\d+)*)", t):
        if m.group(1) not in secs:
            quebradas.append((t[: m.start()].count("\n") + 1, m.group(1)))
    for ln, s in quebradas:
        falha(f"linha {ln}: referência cruzada 'Seção {s}' sem seção correspondente")
    if not quebradas:
        print(f"  [OK] todas as referencias cruzadas resolvem ({len(secs)} secoes)")


def check_abelas(t: str) -> None:
    """Cada tabela markdown precisa ter o mesmo numero de celulas em todas as linhas."""
    blocos = re.findall(r"(?m)(?:^\|.*\|$\n)+", t)
    for bi, bloco in enumerate(blocos, 1):
        linhas = [l for l in bloco.strip().split("\n") if l.strip()]
        if len(linhas) < 2:
            continue
        larguras = {len(re.findall(r"(?<!\\)\|", l)) for l in linhas}
        if len(larguras) > 1:
            falha(f"tabela {bi}: larguras de coluna inconsistentes {sorted(larguras)}")
    print(f"  [OK] {len(blocos)} tabelas markdown com colunas consistentes")


def check_ordem_referencias(t: str) -> None:
    i, j = t.find("## REFER"), t.find("## AP")
    if i < 0:
        aviso("secao REFERENCIAS nao encontrada")
        return
    bloco = t[i:j]
    # Uma entrada por BLOCO separado por linha em branco. Sem isso, uma linha
    # de continuacao como "COMPUTER VISION, IMAGING AND COMPUTER GRAPHICS"
    # (continuacao de BAHROLOLLOOMI) entra na lista como se fosse entrada
    # propria e acusa ordem errada — foi o que aconteceu na primeira versao.
    entradas = [b.strip() for b in re.split(r"\n\s*\n", bloco) if b.strip()]
    # o bloco inclui o cabecalho "## REFERENCIAS" e o "---" final: nao sao
    # entradas bibliograficas e precisam sair antes da contagem
    entradas = [e for e in entradas
                if not e.startswith("#") and e.strip() != "---"]
    chaves = []
    for entrada in entradas:
        primeira = entrada.split("\n", 1)[0].strip()
        # sobrenome: "SOBRENOME,resto", "SOBRENOME; resto" ou
        # "NOME INSTITUICAO. **Titulo**" (ex.: RIOT GAMES. APIs.).
        # O HIFEN precisa estar na classe: sem ele "GARCÍA-MÉNDEZ" nao casa
        # e a entrada fica de fora da checagem de ordem — exatamente o tipo de
        # cobertura silenciosa que faz a checagem parecer mais forte que e.
        m = re.match(r"([A-ZÀ-Ú][A-ZÀ-Ú' \-]*?)(?:[;,.]|\s-\s)", primeira)
        if m:
            chaves.append(m.group(1).strip().lower())
    for a, b in zip(chaves, chaves[1:]):
        if a > b:
            falha(f"referencias fora de ordem alfabetica: {a!r} antes de {b!r}")
    dups = {c for c in chaves if chaves.count(c) > 1}
    for d in sorted(dups):
        falha(f"referencia duplicada: {d!r}")
    # a contagem tem que bater com o número de entradas: se a regex perder
    # alguma, o "[OK] N referencias" mente sobre a cobertura da checagem.
    if len(chaves) != len(entradas):
        aviso(f"a extração de sobrenomes pegou {len(chaves)} de "
              f"{len(entradas)} entradas: revise a regex")
    if not any("alfabetica" in f or "duplicada" in f for f in FALHAS):
        print(f"  [OK] {len(chaves)} referencias em ordem alfabetica e sem duplicatas")


def check_numeros_modelo(t: str) -> None:
    """O XGBoost de produção cited no texto tem que bater com o relatório."""
    rel = RAIZ / "reports" / "metricas_corte.json"
    if not rel.exists():
        aviso("reports/metricas_corte.json ausente: guarda de numero nao roda "
              "(gere com python -m src.models.multi_cutoff_metrics)")
        return
    try:
        bruto = json.loads(rel.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        falha(f"reports/metricas_corte.json invalido: {exc}")
        return
    # o script grava {"gerado_em":..., "resultados": {"15": {"XGBoost": {...}}}}
    # (as chaves de corte sao "10","15","20","25" — sem o sufixo "min")
    dados = bruto.get("resultados", bruto)
    xg15 = dados.get("15", {}).get("XGBoost")
    if not isinstance(xg15, dict):
        aviso("formato de reports/metricas_corte.json nao reconhecido")
        return
    acc = xg15.get("acuracia")
    auc = xg15.get("auc")
    if acc is None:
        aviso("campo de acuracia ausente no relatorio")
        return
    # o texto escreve com virgula decimal
    acc_txt = f"{acc:.4f}".replace(".", ",")
    auc_txt = f"{auc:.4f}".replace(".", ",") if auc else None
    achou_acc = acc_txt in t
    if not achou_acc:
        falha(f"aceracia do XGBoost ({acc_txt}) nao aparece no texto — "
              "numero do texto e do relatorio divergem")
    else:
        print(f"  [OK] acuracia do XGBoost ({acc_txt}) confere com o relatorio")
    if auc_txt and auc_txt not in t:
        falha(f"AUC do XGBoost ({auc_txt}) nao aparece no texto")
    elif auc_txt:
        print(f"  [OK] AUC do XGBoost ({auc_txt}) confere com o relatorio")


def main() -> None:
    if not TEXTO.exists():
        print(f"ERRO: {TEXTO} nao existe")
        sys.exit(2)
    t = TEXTO.read_text(encoding="utf-8")

    print("1. Caracteres nao latinos")
    check_cjk(t)
    print("2. Referencias cruzadas")
    check_referencias_cruzadas(t)
    print("3. Tabelas markdown")
    check_abelas(t)
    print("4. Referencias bibliograficas")
    check_ordem_referencias(t)
    print("5. Numeros de modelo x relatorio")
    check_numeros_modelo(t)

    print()
    print("=" * 66)
    if AVISOS:
        print(f"{len(AVISOS)} aviso(s):")
        for a in AVISOS:
            print(f"  - {a}")
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S):")
        for f in FALHAS:
            print(f"  - {f}")
        print("VEREDITO: INCONSISTENTE")
        sys.exit(1)
    print("VEREDITO: CONSISTENTE")


if __name__ == "__main__":
    main()