# Plano de contexto — Bellestraiko

Roteiro para entender o projeto em camadas, do mais barato ao mais caro. Use
quando estiver "a frio": outra sessão, outra máquina, ou depois de uma pausa.

O objetivo de cada camada é responder uma pergunta. Pule camada quando a
resposta já está na sua cabeça — mas não pule a **Fase 0**.

---

## Fase 0 — Onde as coisas estão (10 min)

Rode primeiro. Custa pouco e evita investigator em arquivos que não
importam.

```bash
git log --oneline -20              # o que aconteceu por último
git status --short                 # trabalho pendente não commitado
```

Leia `AGENTS.md` (raiz) **por inteiro**. Ele tem arquitetura, os 5
invariantes de domínio, comandos, convenções e mapa da documentação. É o
arquivo que evita 90% dos erros.

Depois confira que o ambiente está de pé:

```bash
.venv\Scripts\python.exe tests\smoke_test.py
```

Se o smoke test passa, o pipeline features → modelos funciona. Se falha, o
problema é no código — pare e investigue antes de qualquer outra coisa.

**Pergunta respondida:** o que é este projeto e o que está quebrado agora?

---

## Fase 1 — O mapa (30 min)

Três documentos, nesta ordem. Não pule nenhum.

| # | Arquivo | O que extrair |
|---|---------|---------------|
| 1 | `docs/handoff.md` (193 linhas) | O que existe, por que existe, o que falta. É literalmente escrito para ser o ponto de entrada a frio. |
| 2 | `README.md` | Setup, ordem de execução, decisões metodológicas registradas. |
| 3 | `docs/tcc2_texto.md` — só as seções **4 RESULTADOS** e **5 DISCUSSÃO** | O que a pesquisa realmente encontrou. Ler primeiro o referencial teórico é a forma mais rápida de perder o interesse sem saber o que procurar. |

No `tcc2_texto.md`, pare na seção 4. A 2 (referencial) é a que você vai
consultar quando precisar de citação, não antes.

Ao terminar, você deve conseguir responder sem olhar o código:

- Quais são os dois datasets e por que dois?
- Qual é a tarefa de predição (pré-jogo ou em jogo? por quê?)
- Quais modelos e qual o número de produção?
- Qual o execution accuracy do NLQ?
- Quais são as limitações declaradas?

**Pergunta respondida:** o que este trabalhoikmprovou?

---

## Fase 2 — O porquê das decisões (1–2 h)

Aqui está o contexto que não está em lugar nenhum além do diário. Esta fase é
o que separa quem trabalha no projeto de quem só mexe nele.

`docs/diario_execucao.md` tem 2.857 linhas — **não leia linearmente**. Use
o índice por data e caça com `grep`.

```bash
grep -n '^## ' docs/diario_execucao.md          # índice de entradas
grep -n -i 'vazamento\|leakage\|regressão\|bug real' docs/diario_execucao.md
```

Leia nesta ordem de prioridade:

1. **A entrada do seu tema.** Vai direto pelo índice. Se você vai mexer em
   features, leia a entrada de 2026-07-06 (retreino de 23k) e a de
   2026-07-08 (itens e visão, ambos negativos).
2. **As entradas de decisão**, não as de rotina. Configure `git log` com
   `--grep` para achar quando algo foi decidido:
   ```bash
   git log --oneline --grep='decid\|escolh\|troca' -20
   ```
3. **A seção "Próximos registros pendentes"** no fim do arquivo. É mantida
   atualizada de propósito e é a lista real de pendências.

Duas leituras que valem mais que o resto:

- **Os experimentos negativos.** Oito melhorias de modelo deram ~zero
  (barão/arauto, dispersão de time, tuning por fase, calibração extra, ouro
  em itens, split def/off, item_gold_diff refeito, ward_diff). Isso diz que a
  abordagem está no teto do que features agregadas permitem. Não é fracasso —
  é o material da seção de limitações do TCC. Leia antes de tentar "melhorar
  o modelo".
- **O achado de viés de lado.** As quatro regiões pendem pro vermelho. É o
  achado metodológico mais forte do trabalho, e o `tcc2_texto.md` já registra
  as implicações de composição de amostra que o limitam.

**Pergunta respondida:** por que o código é assim e não de outro jeito?

---

## Fase 3 — O código (2–3 h)

Só agora. E não leia tudo — siga um caminho vertical, da coleta até a tela.

### 3.1 O eixo vertical do pipeline

Três arquivos, na ordem, lendo um a um:

```bash
# 1. features_from_timeline() — o coração do projeto
#    src/features/build_features.py
# 2. o treino
#    src/models/train_baseline.py
# 3. o que a API expõe
#    src/api/main.py
```

`build_features.py` é onde mora o risco real. Cada função tem o aviso sobre
vazamento de dados no topo. Entenda o corte de tempo (`frames[:cutoff+1]`,
cortes 10/15/20/25 min) antes de qualquer coisa.

### 3.2 Os caminhos de LLM

Três arquivos com regras diferentes de "não invente":

| Arquivo | Regra |
|---------|-------|
| `src/features/build_features.py` | Nada de estatística final como feature |
| `src/nlq/nl_to_sql.py` | 4 camadas de segurança na SQL |
| `src/coach/advice.py` | Separar dado medido de conhecimento geral |

### 3.3 O schema

```bash
# src/db.py aplica db/schema.sql de forma idempotente
```

Só o suficiente para saber qual tabela existe e o que cada uma guarda.
`bans`, `item_events` e `items` exigem backfill explícito — se uma página
voltar vazia, rode o ETL antes de suspeitar do código.

### 3.4 O frontend (opcional, só se for mexer)

`frontend/src/App.tsx` (rotas), depois `pages/` (o que existe) e
`lib/api.ts` (o contrato com o backend). Nunca leia o `node_modules` do
`recharts`.

**Pergunta respondida:** como o dado vira número na tela?

---

## Fase 4 — Verificar de ponta a ponta (30 min)

Não confie na leitura. Rode:

```bash
# 1. Pipeline sem banco nem API
.venv\Scripts\python.exe tests\smoke_test.py

# 2. Frontend: lint, testes, typecheck (o build roda tsc)
cd frontend; npm run lint; npm run test; npm run build; cd ..
```

Se for mexer em modelo:

```bash
.venv\Scripts\python.exe tests\validate_predictions.py   # precisa do modelo exportado
```

E ponta a ponta de verdade, com os dois servidores:

```powershell
# Terminal 1
.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
# Terminal 2
cd frontend; npm run dev    # http://localhost:5173
```

Clique em pelo menos: Predict, Explain, Nlq, ChampionDetail. É o caminho que
achou os bugs mais reais do projeto (build vazio, KDA não seguindo o minuto,
itens faltando).

**Pergunta respondida:** está tudo funcionando de verdade agora?

---

## Fase 5 — Onde o projeto está (15 min)

Leia a seção "Próximos passos" do `docs/handoff.md` e a "Próximos registros
pendentes" do `diario_execucao.md`.

Estado real em 2026-10-03, resumido:

- **Sprints 0–6 do `planejamento_v2.md`: entregues.** O documento é registro
  histórico de decisão, não lista de tarefas.
- **`tcc2_texto.md`: escrito.** Das 5 pendências de formatação restam 2
  itens mecânicos — decisão do orientador sobre "Trabalhos Relacionados" e a
  conversão para LaTeX/docx (numeração de "Quadro", legenda de figura no
  topo, fonte abaixo).
- **Maior pendência real:** converter o texto LaTeX e fechar os detalhes de
  diagramação. Limite de 25–30 páginas no corpo.
- **Única feature da visão original não iniciada:** champion select
  competitivo no Team Builder.
- **Opcional:** ampliar amostra de KR/EUW1/NA1 para reforçar o viés de lado
  (NA1 segue baixo, 1.446 partidas).

**Pergunta respondida:** para onde vai o trabalho agora?

---

## Armadilhas conhecidas

Coisas que custam tempo se você não souber de antemão:

- **`RIOT_API_KEY` expira a cada 24h.** Erro 401/403 da Riot é isso, não é
  bug. Para coleta grande, peça Personal API Key no portal.
- **Os servidores não sobrevivem a reboot.** API e frontend precisam ser
  subidos a cada sessão, API antes do frontend.
- **Erro de encoding no PowerShell.** As saídas podem aparecer com
  caracteres quebrados (`predição` virando `predi??ão`). É o console, não o
  arquivo. Use `-Encoding UTF8` ao ler.
- **Nome do produto ≠ nome do diretório.** O produto é **Bellestraiko**; o
  diretório segue `lol-analytics`. Não renomeie. (O TCC ainda menciona
  "Hextech Lab" em um ponto — nome antigo, ver pendência no
  `tcc2_texto.md`.)
- **`docs/planejamento_v2.md` e `project_scope_decisions.md` não são lista
  de tarefas.** São registro de decisão. A lista viva é a do fim do diário.

---

## Resumo em uma tela

| Fase | Tempo | Pergunta |
|------|-------|----------|
| 0 — AGENTS.md + smoke test | 10 min | O que é isto e está quebrado? |
| 1 — handoff + README + seção 4 do TCC | 30 min | O que isto provou? |
| 2 — diário por índice | 1–2 h | Por que é assim? |
| 3 — código em caminho vertical | 2–3 h | Como o dado vira número? |
| 4 — verificação ponta a ponta | 30 min | Está funcionando? |
| 5 — próximos passos | 15 min | Para onde vai? |

Custo total: cerca de um turno. Para uma tarefa específica, não precisa das
cinco fases — Fase 0 sempre, Fase 3 e 4 sempre, e as demais conforme o que a
tarefa exige.