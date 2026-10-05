# Plano de fechamento — o que falta

> **DOCUMENTO HISTÓRICO — datado de 2026-10-04, superseded no mesmo dia.**
> Os números de estado abaixo (57 páginas, corpo 29, base de 39.426) eram
> verdade quando o plano foi escrito e **não descrevem o entregável atual**,
> que está em 58 páginas, corpo 30 e duas bases declaradas (41.063
> descritiva, 39.426 de modelagem). O plano foi mantido como registro do que
> foi fechado e de como, não como lista de pendências: os itens marcados
> ✅ estão feitos e os que não estão foram resolvidos por outros caminhos.
> Para o estado atual, ver `docs/diario_execucao.md` e `docs/handoff.md`.

**Data:** 2026-10-04
**Estado do entregável:** 57 páginas, corpo 29 (faixa 25-30), 5 Quadros,
6 Figuras, 18 referências. `smoke`, `validate_predictions`, `verifica_tcc`
(18 checagens), `confere_docx` e `npm run test` (31/31) passam.

Este plano lista o que **ainda está aberto**, com o critério de aceitação de
cada item. Todos os itens foram verificados no arquivo antes de entrarem
aqui; nenhum veio de memória.

A regra do `AGENTS.md` que organiza a prioridade: *"documentação divergente
do código é bug"* e *"número no TCC sempre vem de artefato real"*. O Bloco A
existe porque viola essa regra agora.

---

## Bloco A — Documentação divergente do código — ✅ feito em 2026-10-04

> É o bloco mais importante e o mais rápido. Nenhum item aqui afeta o
> `.docx` que vai ser entregue, e é exatamente por isso que são os mais
> perigosos: passam despercebidos e destroem a confiança de quem retoma o
> projeto.

### A1. `docs/comandos.md` não conhece 8 scripts

Verificado por busca literal: **todos os 8 ausentes**.

| script | o que faz |
|---|---|
| `src/models/multi_cutoff_metrics.py` | quadro do Apêndice C + `reports/metricas_corte.json` |
| `src/models/tune_models_full.py` | grid completo na base final + artefato do tuning |
| `docs/verifica_tcc.py` | 18 checagens de consistência do texto |
| `docs/confere_docx.py` | conformidade formal do `.docx` |
| `docs/recapturar_anexo_a.py` | regrava as 6 capturas |
| `docs/taxa_base_por_corte.py` | taxa de vitória por corte |
| `docs/testa_diferenca_taxas.py` | Wilson + Holm, sustenta o achado da 5.3 |
| `docs/confere_conversao_advantagem.py` | conversão de vantagem, os dois lados |

**Correção:** acrescentar as entradas na ordem de uso, cada uma com o
`python -m ...` ou `.venv\Scripts\python.exe ...` exato e o que ela grava.
**Aceite:** os 8 presentes em `docs/comandos.md`.

### A2. `README.md` afirma base de 10,4 mil partidas

`README.md:147` diz *"Rodar tudo com dados reais (10,4k partidas; métricas
em …)"*. A base é **39.426**, e o número sobreviveu a duas ampliações.

**Correção:** atualizar para a base atual e para as métricas atuais
(XGBoost 0,7621 / AUC 0,8473 no corte de 15 min).
**Aceite:** nenhuma menção a 10,4k nem a 23.133 no `README.md`.

### A3. `docs/handoff.md` diz que o modelo está em 23.133

`handoff.md:20-25` e `:80` ainda descrevem a base do modelo como 23.133 e
citam 33.713. A seção de métricas do mesmo arquivo já foi corrigida — então
o `handoff` se contradiz **dentro de si**.

**Correção:** base do modelo 39.188 (corte de 15 min), base total 39.426,
ampliação da NA1 registrada.
**Aceite:** sem `23.133`/`33.713` no `handoff.md` fora de contexto
histórico explicitamente datado.

---

## Bloco B — Inconsistências internas do texto — ✅ feito em 2026-10-04

### B1. Lista de pendências final com numeração duplicada

Números repetidos na lista: **`1`, `2` e `4`**. Os itens `4.` (Apêndices) e
`4.` (Formatação final) são o mesmo número; `1` e `2` repetem o bloco de
decisões logo acima.

**Correção:** renumerar como lista contínua única.
**Aceite:** sequência 1..n sem repetição.

### B2. Estilo de citação autor-data em dois padrões

A prosa usa "Prodanov e Freitas (2013)", "Birant e Birant (2023)",
"Lundberg e Lee (2017)". Mas há **5 citações entre parênteses em CAIXA
ALTA**: `(PRODANOV; FREITAS, 2013)`, `(GIL, 2002)`, `(CRESWELL; CRESWELL,
2023)`, `(YIN, 2018)`. As mesmas obras aparecem nas duas formas — o que a
NBR 10520 não permite.

**Correção:** normalizar para minúsculas com `e`: `(Prodanov; Freitas, 2013)`,
`(Gil, 2002)`, `(Creswell; Creswell, 2023)`, `(Yin, 2018)`.
**Aceite:** nenhuma citação autor-data em caixa alta.

### B3. Teste (ii) de robustez sem data e sobre base antiga

A 5.3 e a 4.5 afirmam que a taxa por faixa de duração ficou em **44%-47%**.
Essa medição é de **2026-07-08, sobre 23.133 partidas** (diário). O texto não
diz isso, e o número está sendo usado para sustentar um teste de robustez
de um achado que se mediu sobre 39.426.

**Correção:** datar no texto **e** remedir na base atual, já que a base
triplicou. Se o número mudou, atualizar; se não, citar a data.
**Aceite:** o valor citado na 4.5/5.3 tem data e base declaradas.

---

## Bloco C — Polish

### C1. Sobreposição entre 5.8 e 6.1 — ✅ feito (6.1: 527 → 412 palavras)

A 5.8 tem **1.126 palavras**; a 6.1, **488**. O termo "subajuste" aparece
nas duas. A 6.1 declara a sobreposição (*"A descrição completa está na
Seção 5.8"*), então não é defeito — mas a 6.1 repete a taxa-base e a
grade em ~150 palavras.

**Opção:** reduzir a 6.1 às três ameaças de validade (construto, externa,
interna) e deixar a limitação técnica só na 5.8. Libera ~1 página.
**Aceite:** "subajuste" com uma única ocorrência, na 5.8.
**Escolha sua:** com o corpo em 29 de 25–30, a folga não é urgente. Fazer
só se o orientador pedir encurtar.

### C2. Saída do Quadro 1 não arquivada — ⏳ adiado (10 min)

`docs/verifica_tcc.py` checagem 6 confronta o Quadro 1 com o banco, mas não
salva a saída. O diário já apontava isso como pendência em 2026-10-03: *"não
houve segunda execução independente da query, e a saída não foi arquivada"*.

**Correção:** gravar `reports/stats_regions_2026-10-04.txt` com a query, o
timestamp e o resultado.
**Aceite:** o arquivo existe e `verifica_tcc` o produz.

### C3. `.log` do tuning não versionado

`reports/tune_models_39k.log` cai no `.gitignore` (`*.log`); o `.json`
versionado é o que a checagem 12 lê. Verifiquei num clone limpo: o JSON
sobrevive, o log não. Está correto — o log é derivado e regenerável.

**Decisão:** manter como está. Se preferir o log legível no repo, é
`git add -f` e uma exceção ao `.gitignore`. **Não é defeito.**

---

## Bloco D — Lacunas de pesquisa (não são redação)

> Aqui não é-consertar. É trabalho novo, e a decisão é sobre o escopo do
> TCC, não sobre o texto.

### D1. Calibração e regularização alternativa — ✅ medido em 2026-10-04

É a lacuna real que eu mesmo abri ao medir o grid. A limitação da 5.8 é:
o modelo projeta o empate para perto de 50% quando o dado bruto dá 46-48%.
O argumento é *"a grade de hiperparâmetros não acha ajuste melhor"* — e é
verdade, mas a gradevariou só `n_estimators`, `learning_rate` e `max_depth`.

As duas alavancas naturais contra esse defeito **não foram testadas**:

- **calibração** (`CalibratedClassifierCV` sobre o output) — força a
  projeção de empate para a taxa-base observada;
- **regularização alternativa** — penalização de leaves, `min_child_weight`,
  subsample.

**Por que importa:** se a calibração sozinha fechar a discrepância de 1,7 a
4,7 pontos, a limitação da 5.8 deixa de ser "limitação em aberto" e vira
"corrigida com uma linha", o que é um resultado **mais forte** que o atual —
e caberia na 5.8 em duas frases.

**Custo estimado:** 20–40 min para as duas, mais 20 min para reescrever 5.8
e revalidar a bateria se der resultado.
**Decisão sua:** se o escopo permite, é o item com maior retorno de todo o
plano. Se não permite, registre no diário que a alavanca não foi testada —
porque "não testado" escrito é honesto, e "não testado" omitido é a mesma
falha de sempre.

### D2. Teste de duração remedido

Depende de B3. Se o número mudou, cai no Apêndice D como experimento
adicional; se não, é só citação datada.

---

## Ordem sugerida

```
1. A1 + A2 + A3        # documentação, ~30 min, zero risco
2. B1 + B2             # texto, ~15 min, zero risco
3. B3                  # remedir + datar, ~20 min
4. D1                  # calibração, 20-40 min  <- maior retorno
5. C2                  # arquivar saída, ~10 min
6. C1                  # só se o orientador pedir encurtar
```

**A1 e C1 juntos resolvem o documento e o espaço.** O resto é consistência.

## O que NÃO está no plano, e por quê

- **Apêndices/anexos**: feitos e conferidos (`confere_docx`).
- **Figuras**: 6, citadas no corpo, fonte conferida contra o Anexo A.
- **Referências**: 18, ordem alfabética, sem duplicata, 6 verificadas por DOI.
- **Estrutura**: 10 de 10 aprovados usam "Trabalhos Relacionados" como seção
  de primeiro nível; seguimos.
- **Formato**: herdado do TCC I via `--reference-doc`; 0 títulos em negrito.

---

## Regra para o que vier depois

Qualquer afirmação nova entra no TCC **só depois** de o comando que a mede
existir e o log estar em `reports/`. Foi a violação dessa regra que produziu,
nesta rodada, quatro números errados e um achado refutado — e todos foram
encontrados no fim, não quando entraram.