# AGENTS.md — Bellestraiko (TCC II)

Instruções para agentes de IA trabalhando neste repositório. Leia antes de
tocar em qualquer arquivo.

## O que é o projeto

TCC II (CS, Unisinos): plataforma de análise de esports de League of Legends.
Nome do produto **Bellestraiko**; o diretório do repositório continua
`lol-analytics` (não renomear — quebraria caminhos e histórico).

Dois datasets complementares:

1. **Solo queue** (Riot API) — partidas ranqueadas Challenger/GM
   multi-região (BR1/EUW1/KR/NA1, fila 420). JSON bruto + timelines
   guardados para reprocessamento.
2. **Competitivo** (Oracle's Elixir) — jogos profissionais 2014-2026
   (LCK/LPL/LEC/LTA/CBLOL etc.) em `data/pro/`.

Fluxo:

```
Riot API ─> coletor (rate-limited) ─> raw_matches/raw_timelines (JSONB)
                                            │ ETL
                                            ▼
              matches / teams / participants / players / bans
                        item_events / items
Oracle's Elixir CSV ─> pro_games / pro_players
                                            │
        ┌───────────────────────────────────┼──────────────────┐
        ▼                                   ▼                  ▼
  features por fase              modelos ML por fase      API FastAPI
   10/15/20/25 min                (train_baseline,        (src/api/main.py)
  (build_features.py)             tune_models,                   │
                                   explain_shap,                  ▼
                                   export_model)      frontend/ React (principal)
                                                      + Streamlit (alternativa)
```

## Triagem de prompt — para onde cada pedido vai

**Toda sessão começa no agente `orquestrador`** (`default_agent` no
`opencode.json`). Ele é read-only e existe só para classificar e despachar.
Nenhum trabalho sai dele — ele não edita nem roda comando de escrita.

Antes de despachar, classifique o pedido em complexityidade:

| Nível | Sinal | Quem executa |
|---|---|---|
| **N0** | 1 arquivo, factual, sem alteração | **Você mesmo.** Não despache. |
| **N1** | 1–2 arquivos, mudança pequena e óbvia | **Você mesmo.** Chame `revisor` no fim se tocou lógica de domínio. |
| **N2** | Atravessa camadas, toca um invariante, ou >3 arquivos | **Você** executa + `revisor` antes de dar por pronto. |
| **N3** | Auditoria, consistência, capítulo do TCC, sweeping no codebase | **Despache como dono.** O especialista entrega. |

Por intenção:

| O pedido é sobre… | Agente |
|---|---|
| Revisar código/diff, "isso está correto?", "achei um bug" | `revisor` |
| "Está funcionando?", rodar testes, o que quebrou | `validador` |
| TCC, `docs/`, README, métrica, número, LaTeX, texto | `doc-tcc` |
| Implementar, corrigir, criar feature | `build` (o agente programador) |

**Regras de despacho:**

- **N0 e N1 vão direto.** É o caso comum. Delegar por hábito é o erro mais
  caro: cada subagente é uma sessão nova e paga o custo de reconstruir
  contexto.
- **N2 e N3 vão para o especialista**, que vira o dono da tarefa.
- **Diga em uma linha** o nível e o agente escolhido antes de despachar.
- **Fixe as coordenadas no prompt do subagente**: arquivos/glob, o que mudou
  (`git diff`), e a pergunta concreta. Contexto novo não sabe nada deste
  projeto; sem isso ele explora o repo inteiro e devolve genericidade.
- **`revisor` e `validador` não editam nada.** Se o pedido é consertar, eles
  não são o dono — são portão. Devolvem diagnóstico, o agente programador
  aplica.
- **Dois read-only independentes podem rodar em paralelo** (`revisor` +
  `validador` no mesmo diff). Nunca dois read-only no mesmo escopo.
- **Escalone** se um N0 revelar um N2: promova o nível e traga o `revisor`
  antes de mexer em mais coisa.

## INVARIANTES DO DOMÍNIO — não violar

Estas regras são a razão de o projeto ser academicamente defensável. Quebrar
qualquer uma é um bug crítico, mesmo que o código "funcione".

### 1. Vazamento de dados (data leakage) — `src/features/build_features.py`

A tarefa de predição é **em jogo**: estado da partida em um corte de tempo.
Features só podem vir de `frames[: cutoff + 1]` da timeline.

- **Proibido** usar estatística final da partida (kills totais, ouro total,
  itens finalizados, `winner`) como feature. Isso prevê vitória trivialmente e
  invalida todos os resultados.
- Ao adicionar feature nova, derive do estado **no corte**, nunca do fim.
- Os cortes são 10/15/20/25 min (`CUTOFFS`). `CUTOFF_MIN = 15` é o padrão
  compatível com `train_baseline`/`tune_models`/`gold15`.
- `features_from_timeline` retorna `None` se a partida acabou antes do corte —
  trate esse caso.

### 2. Honestidade da LLM — `src/coach/`, `src/nlq/`

O projeto separa explicitamente **dado medido** de **conhecimento geral do
jogo**, e essa separação aparece na interface:

- O NLQ tem a seção "Leitura de jogo:" separada do resultado da query.
- O coach (`advice.py`) rotula o que veio dos dados reais (matchup, sinergia,
  item histórico) e o que é conhecimento geral da LLM (itens que ela
  recomenda, posição, wave/minion).
- **Nunca** inventar estatística. Se o número não foi calculado a partir do
  histórico, ele não aparece como número.
- O modelo de ML não vê itens, posição nem estado de wave/minion (a Riot API
  não grava). Orientação que dependa disso é inferência, rotulada como tal.

### 3. Segurança do text-to-SQL — `src/nlq/nl_to_sql.py`

Quatro camadas, todas obrigatórias:

1. Apenas um statement, começando com `SELECT` (sem `;` encadeado).
2. `FORBIDDEN` bloqueia `insert|update|delete|drop|alter|create|truncate|grant|revoke|copy`.
3. Somente tabelas de `ALLOWED_TABLES` são permitidas.
4. `statement_timeout` no PostgreSQL.

- Nunca interpolar input do usuário na SQL fora dessa validação.
- `temperature=0` é requisito do benchmark de execution accuracy — não mexer.
- `max_tokens=1200` foi calibrado; reduzir corta queries no meio e gera
  erro de sintaxe em vez de rodar (ver comentário no código).
- `SqlExecutionError` carrega a SQL **e** a causa original para o usuário
  poder depurar. Não engula a exceção.

### 4. Retomabilidade e idempotência

Coletores e ETLs são re-executáveis de propósito:

- `collect_matches` pula partida já salva.
- `load_matches` e `load_items` são backfill idempotente a partir do bruto.
- `src.db` aplica `db/schema.sql` de forma idempotente.
- Rodar duas vezes não pode duplicar linha nem corromper estado.

### 5. Tabelas que exigem backfill explícito

Depois de qualquer coleta nova, e se o banco foi populado antes da tabela
existir:

| Tabela | Como popular |
|---|---|
| `bans` | `python -m src.etl.load_matches` |
| `item_events` | `python -m src.etl.load_items` |
| `items` | `python -m src.etl.load_item_catalog` (só quando o Data Dragon muda) |

Se uma query ou página retornar vazio e o schema tiver a tabela, verifique
se o backfill rodou antes de suspeitar do código.

## Comandos

Windows/PowerShell. O interpretador é **sempre** `.venv\Scripts\python.exe`.
Referência completa em `docs/comandos.md`.

```powershell
# Verificação sem banco nem API (primeiro de tudo)
.venv\Scripts\python.exe tests\smoke_test.py
.venv\Scripts\python.exe tests\validate_predictions.py   # precisa do modelo exportado

# Texto do TCC e entregáveis (exit 0 = ok)
.venv\Scripts\python.exe docs\verifica_tcc.py        # texto x artefatos
.venv\Scripts\python.exe docs\confere_docx.py        # estrutura do .docx
powershell -File docs\confere_paginas.ps1             # corpo 25-30 páginas
.venv\Scripts\python.exe docs\confere_materiais.py   # guia/pptx/README sem número velho

# Frontend
cd frontend; npm run lint; npm run test; npm run build; cd ..

# Servidores (não sobrevivem a reboot)
.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000   # API
cd frontend; npm run dev                                                     # :5173
```

A API precisa estar de pé **antes** do frontend.

## Ambiente

- `.env` (copiar de `.env.example`): `RIOT_API_KEY`, `RIOT_PLATFORM`,
  `RIOT_REGION`, `DATABASE_URL`, `ANTHROPIC_API_KEY`.
- **`RIOT_API_KEY` de dev expira a cada 24h.** Se a coleta falhar com 401/403,
  é isso — não é bug.
- Banco: PostgreSQL, database `lol_analytics`.
- `src/config.py` faz `load_dotenv()` e usa `os.environ[...]` — importa o
  módulo só com o `.env` presente.
- **Nunca** commitar `.env`, `data/`, `*.csv` ou `__pycache__` (já no
  `.gitignore`).

## Convenções de código

- Comentários explicam **por quê**, não o quê. O projeto documenta decisões
  dentro do código com a data e o motivo:
  ```python
  # killerTeamId no evento é o time que PERDEU a torre (2026-07-08: bug
  # invertido por 2 semanas de leitura de dashboard)
  ```
  Preserve esse estilo ao mexer em código com histórico.
- Docstrings em PT-BR, detalhadas quando a função tem armadilha conhecida.
- Frontend: Vite + React 19 + TypeScript + Tailwind v4 + TanStack Query +
  Recharts. Componentes em `src/components/`, páginas em `src/pages/`,
  client HTTP em `src/lib/api.ts`. Tokens de gráfico em
  `src/lib/chart-tokens.ts`.
- Rotas antigas redirecionam (ex.: `/montar`, `/predicao`,
  `/explicabilidade` → `/simulador`). Não reintroduza rotas mortas.
- `ErrorBoundary.tsx` existe — rotas novas precisam funcionar dentro dele.

## Documentação

| Arquivo | Papel |
|---|---|
| `docs/diario_execucao.md` | **Fonte primária** dos números do TCC |
| `docs/handoff.md` | Mapa do projeto para retomar a frio |
| `docs/scripts.md` | Referência por script |
| `docs/comandos.md` | Comandos na ordem de uso |
| `docs/planejamento_v2.md` | Plano de sprints (histórico — sprints entregues) |
| `docs/tcc2_texto.md` | Texto do TCC II |
| `docs/tcc2_latex/` | Fonte LaTeX (classe UNISINOS, `Makefile`) |

Regras:

- Documentação e comentários em **PT-BR**.
- **Número no TCC sempre vem de artefato real** (métrica em
  `diario_execucao.md`, saída de script, `reports/`). Nunca estimar,
  arredondar para "bom" ou inventar.
- Ao mudar comportamento, comando ou arquitetura, atualizar `README.md`,
  `docs/comandos.md` e `docs/handoff.md` junto. Documentação divergente do
  código é bug.
- Antes de escrever o TCC, ler `docs/diario_execucao.md` — ele explica o
  porquê de cada decisão.

## Git

- Branch principal com commits em português no formato convencional:
  `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `revisão:`.
- Não commitar `.env`, `data/`, `*.csv`, `.venv/`, `node_modules/`.
- Logs e `.pid` no diretório raiz são artefatos de sessão local, não vão
  para o repo.