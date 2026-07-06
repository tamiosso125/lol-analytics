# Comandos — Bellestraiko

Referência rápida de todos os comandos do projeto, na ordem em que
costumam ser usados. Windows/PowerShell; o interpretador Python é
sempre `.venv\Scripts\python.exe` (ou ative a venv antes).

Convenção: `py` abaixo = `.venv\Scripts\python.exe`. No PowerShell:
```powershell
cd C:\Users\Home\Documents\Faculdade\lol-analytics
$py = ".venv\Scripts\python.exe"
```

---

## 0. Subir os servidores (o que você mais usa)

Os dois processos NÃO sobrevivem a reboot — precisam ser subidos a cada
sessão. Dois terminais:

```powershell
# Terminal 1 — API (porta 8000)
cd C:\Users\Home\Documents\Faculdade\lol-analytics
.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — Frontend (porta 5173)
cd C:\Users\Home\Documents\Faculdade\lol-analytics\frontend
npm run dev
```

A API precisa estar de pé antes do front (o front consome
`http://localhost:8000`). Abrir: http://localhost:5173

---

## 1. Setup inicial (uma vez)

```powershell
.venv\Scripts\python.exe -m src.db                 # aplica db/schema.sql (idempotente)
cd frontend; npm install; cd ..                    # dependências do front
```

Pré-requisitos: PostgreSQL rodando, banco `lol_analytics` criado, `.env`
preenchido (`RIOT_API_KEY`, `DATABASE_URL`, `ANTHROPIC_API_KEY`).

> **RIOT_API_KEY expira a cada 24h** (chave de desenvolvedor). Renove em
> developer.riotgames.com e cole no `.env` antes de qualquer coleta.
> Para coleta grande/multi-região, peça uma **Personal API Key**
> (developer.riotgames.com → Register Product; sem expiração diária,
> limite maior — aprovação leva alguns dias).

---

## 2. Coleta de solo queue (Riot API)

```powershell
# Semear jogadores dos ladders (padrão: só a plataforma do .env)
.venv\Scripts\python.exe -m src.collect.seed_players

# Multi-região / multi-elo:
.venv\Scripts\python.exe -m src.collect.seed_players --platforms br1 kr euw1 na1 --tiers CHALLENGER GRANDMASTER MASTER

# Coletar partidas (todas as plataformas em players):
.venv\Scripts\python.exe -m src.collect.collect_matches --players 730 --matches-per-player 40

# Coletar só de regiões específicas (N jogadores POR plataforma):
.venv\Scripts\python.exe -m src.collect.collect_matches --platforms kr euw1 na1 --players 100 --matches-per-player 20

# Preencher nomes (game_name/tag_line) de quem tem >= N jogos:
.venv\Scripts\python.exe -m src.collect.backfill_names --min-games 20
```

Plataformas válidas: `br1 la1 la2 na1 oc1 kr jp1 euw1 eun1 tr1 ru`
(+ SEA: `ph2 sg2 th2 tw2 vn2`). O roteamento de região é automático.
A coleta é **retomável** (pula match_ids já no banco) — pode interromper
e rodar de novo. É sequencial entre plataformas para respeitar o rate
limit por região de roteamento.

Dimensionamento (chave de dev, ~100 req/2min): ~1.000 partidas ≈ 40 min;
10.000 ≈ 7h. Rode em background/sessões.

---

## 3. Coleta de competitivo (Oracle's Elixir)

```powershell
# Baixar um ano (o Drive tem quota diária; se bloquear, baixe manual):
.venv\Scripts\python.exe -m src.collect.collect_pro --year 2026

# Carregar TODOS os CSVs em data/pro/ no banco (idempotente por ano):
.venv\Scripts\python.exe -m src.etl.load_pro

# Carregar só um ano:
.venv\Scripts\python.exe -m src.etl.load_pro --year 2026
```

Fallback manual da quota: baixar em oracleselixir.com/tools/downloads e
salvar em `data/pro/{ano}_LoL_esports_match_data_from_OraclesElixir.csv`.

---

## 4. ETL e features (após qualquer coleta nova)

```powershell
# Re-normalizar tudo de raw_matches (só se o schema relacional mudou):
.venv\Scripts\python.exe -m src.etl.load_matches

# Extrair compras/vendas de itens (reconstrói item_events):
.venv\Scripts\python.exe -m src.etl.load_items

# Gerar features por fase (10/15/20/25 min):
.venv\Scripts\python.exe -m src.features.build_features
```

---

## 5. Modelos

```powershell
# Baseline RF/XGBoost/MLP (métricas do TCC):
.venv\Scripts\python.exe -m src.models.train_baseline

# Tuning (GridSearchCV) + curva de calibração:
.venv\Scripts\python.exe -m src.models.tune_models

# Exportar modelos de produção por fase (a API carrega no startup):
.venv\Scripts\python.exe -m src.models.export_model

# Explicabilidade (gráficos SHAP para o TCC):
.venv\Scripts\python.exe -m src.models.explain_shap

# Comparação formal solo queue × pro + salva model_pro.joblib:
.venv\Scripts\python.exe -m src.models.train_pro
```

> **Após recoletar**: a ordem é `load_items` → `build_features` →
> `export_model`, e **reiniciar a API** (ela carrega os modelos no
> startup). Depois de mexer em features/modelo, o `/predict` só reflete
> a mudança com a API reiniciada.

---

## 6. Interface em linguagem natural (NLQ)

```powershell
# Rodar uma pergunta pelo terminal:
.venv\Scripts\python.exe -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"

# Benchmark de execution accuracy (exigência da banca):
.venv\Scripts\python.exe -m src.nlq.evaluate_nlq
```

> **Regra da casa**: sempre rode `evaluate_nlq` de novo depois de
> QUALQUER mudança em `src/nlq/schema_context.py` — já regrediu
> silenciosamente 2×.

---

## 7. Testes

```powershell
# Smoke test (sem banco/API, roda em tempdir — não toca dados reais):
.venv\Scripts\python.exe tests\smoke_test.py

# Bateria de validação comportamental do modelo de produção:
.venv\Scripts\python.exe tests\validate_predictions.py
```

---

## 8. Dashboard Streamlit (alternativa ao React)

```powershell
.venv\Scripts\python.exe -m streamlit run src\dashboard\app.py
```

---

## Reiniciar a API sem terminal dedicado (background)

Quando a API precisa ser reiniciada (ex.: mudou endpoint/modelo) mas você
não quer prender um terminal:

```powershell
$pid_ = Get-Content .api.pid -ErrorAction SilentlyContinue
if ($pid_) { Stop-Process -Id $pid_ -Force -Confirm:$false -ErrorAction SilentlyContinue }
$p = Start-Process -FilePath ".venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","src.api.main:app","--port","8000" `
  -WorkingDirectory "C:\Users\Home\Documents\Faculdade\lol-analytics" `
  -RedirectStandardOutput ".api_stdout.log" -RedirectStandardError ".api_stderr.log" `
  -PassThru -WindowStyle Hidden
$p.Id | Out-File .api.pid -Encoding utf8
```

---

## Pipeline completo do zero (referência)

Ordem canônica quando se popula um banco vazio (também no README):

```
1.  python -m src.db                         # schema
2.  python -m src.collect.seed_players       # jogadores
3.  python -m src.collect.collect_matches    # partidas + timelines
4.  python -m src.collect.backfill_names     # nomes
5.  python -m src.etl.load_items             # itens
6.  python -m src.features.build_features     # features por fase
7.  python -m src.models.train_baseline       # baseline
8.  python -m src.models.tune_models          # tuning + calibração
9.  python -m src.models.export_model         # modelos de produção
10. python -m src.collect.collect_pro         # + competitivo (opcional)
11. python -m src.etl.load_pro
12. uvicorn src.api.main:app --port 8000     # API
13. cd frontend && npm run dev                # front
```
