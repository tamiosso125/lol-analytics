"""Roda um conjunto de perguntas pelo caminho do PRODUTO (`ask`: roteador, base, guarda,
nova tentativa) e grava a saída bruta, sem julgar acerto.

Serve a dois conjuntos (docs/plano_roteamento_nlq.md, Fase 5):
  * desenvolvimento (50 perguntas livres que já foram analisadas e usadas para ajustar o
    sistema: NÃO valem como nota);
  * CEGO (50 perguntas escritas por outra pessoa, rodadas UMA vez depois de congelar o
    sistema: é o número que vai ao TCC).

Protocolo do conjunto cego: o hash dos arquivos que definem o comportamento
(roteador, validador, geração, esquema) e o commit ficam gravados junto da saída; o
sistema não é ajustado depois de ver o resultado. Quem diz se cada resposta está certa
é uma pessoa, lendo a SQL e as linhas (`docs/revisao_nlq_*.md`); este script não decide.

Formato do arquivo de perguntas: uma por linha, "N. pergunta" (linhas em branco e
cabeçalhos sem número são ignorados).

Uso:  python -m src.nlq.avaliar_conjunto --perguntas docs/nlq_perguntas_cegas.txt \\
          --saida reports/nlq_cego_resultado.json --rotulo cego
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))

ARQUIVOS_DO_SISTEMA = ["src/nlq/route.py", "src/nlq/sql_guard.py", "src/nlq/nl_to_sql.py",
                       "src/nlq/schema_context.py"]
LINHA = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")


def ler_perguntas(caminho: Path) -> list[tuple[int, str]]:
    saida = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        m = LINHA.match(linha)
        if m and m.group(2).endswith("?"):
            saida.append((int(m.group(1)), m.group(2)))
    return saida


def _hash(caminho: str) -> str:
    # normaliza o fim de linha: o mesmo texto dá o mesmo hash no Windows e no Linux
    conteudo = (RAIZ / caminho).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(conteudo).hexdigest()[:16]


def _git() -> dict:
    def g(*args):
        return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True).stdout.strip()

    return {"commit": g("rev-parse", "--short", "HEAD"),
            "arquivos_modificados": [l[3:] for l in g("status", "--short").splitlines()
                                     if l[3:] in ARQUIVOS_DO_SISTEMA]}


def _texto(v):
    return v if isinstance(v, (int, float, str, bool)) or v is None else str(v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perguntas", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--rotulo", default="")
    ap.add_argument("--linhas", type=int, default=20, help="linhas guardadas por resultado")
    ap.add_argument("--retomar", action="store_true",
                    help="continua de onde parou, sem refazer as perguntas já gravadas")
    args = ap.parse_args()

    import anthropic

    from src.nlq.nl_to_sql import SqlExecutionError, ask

    perguntas = ler_perguntas(RAIZ / args.perguntas)
    saida = RAIZ / args.saida
    registros: list[dict] = []
    if args.retomar and saida.exists():
        registros = json.loads(saida.read_text(encoding="utf-8")).get("registros", [])
    feitos = {r["n"] for r in registros}

    def recusa(x):
        return bool(x["sql"]) and "não é possível responder" in x["sql"]

    def resumir() -> dict:
        return {
            "perguntas": len(registros),
            "responderam": sum(1 for r in registros if r["status"] == "respondeu"),
            "erro_total": sum(1 for r in registros if r["status"] == "erro"),
            "roteadas_para_uma_base": sum(1 for r in registros if r.get("roteamento", {}).get("classe") in ("solo", "competitivo")),
            "roteadas_para_ambas": sum(1 for r in registros if r.get("roteamento", {}).get("classe") == "ambos"),
            "resultados_total": sum(len(r.get("resultados", [])) for r in registros),
            "resultados_com_erro": sum(1 for r in registros for x in r.get("resultados", []) if x["erro"]),
            "resultados_recusa": sum(1 for r in registros for x in r.get("resultados", []) if not x["erro"] and recusa(x)),
            "resultados_com_nova_tentativa": sum(1 for r in registros for x in r.get("resultados", []) if x["tentativas"] == 2),
        }

    def gravar(completo: bool, interrompido_por: str = "") -> None:
        # grava a CADA pergunta: uma falha externa (ex.: créditos da API) não perde o que já saiu
        saida.parent.mkdir(exist_ok=True)
        saida.write_text(json.dumps({
            "rotulo": args.rotulo, "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "completo": completo, "interrompido_por": interrompido_por,
            "arquivo_de_perguntas": args.perguntas,
            "hash_das_perguntas": hashlib.sha256((RAIZ / args.perguntas).read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16],
            "sistema": {"hashes": {a: _hash(a) for a in ARQUIVOS_DO_SISTEMA}, "git": _git(),
                        "modelo_geracao": "claude-haiku-4-5-20251001", "temperatura": 0},
            "resumo": resumir(), "registros": registros,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    for n, pergunta in perguntas:
        if n in feitos:
            continue
        reg = {"n": n, "pergunta": pergunta}
        try:
            r = ask(pergunta)
            reg["roteamento"] = r["roteamento"]
            reg["resultados"] = [
                {"base": x["base"], "sql": x["sql"], "columns": x["columns"],
                 "n_linhas": len(x["rows"]), "rows": [[_texto(c) for c in l] for l in x["rows"][: args.linhas]],
                 "tentativas": x["tentativas"], "erro": x["erro"]}
                for x in r["resultados"]
            ]
            reg["status"] = "respondeu"
        except SqlExecutionError as exc:
            reg["status"] = "erro"
            reg["erro"] = {"tipo": "execucao", "sql": exc.sql, "cause": str(exc.cause).strip()}
        except ValueError as exc:
            reg["status"] = "erro"
            reg["erro"] = {"tipo": "validacao", "message": str(exc)}
        except anthropic.APIError as exc:
            # falha EXTERNA (créditos, rede, limite): não é resposta do sistema e não entra na
            # medição. Para aqui, guarda o que já saiu e deixa retomar com --retomar.
            gravar(False, f"{type(exc).__name__}: {str(exc)[:200]}")
            print(f"\nINTERROMPIDO na pergunta {n}: {type(exc).__name__}: {str(exc)[:160]}")
            print(f"{len(registros)} perguntas gravadas em {saida}. Rode de novo com --retomar.")
            raise SystemExit(2)
        registros.append(reg)
        gravar(False)
        bases = ",".join(x["base"] for x in reg.get("resultados", [])) or "-"
        print(f"{n:3d} {reg['status']:<9} {bases:<22} {pergunta[:70]}", flush=True)

    gravar(True)
    print("\n", json.dumps(resumir(), ensure_ascii=False))
    print("->", saida)


if __name__ == "__main__":
    main()
