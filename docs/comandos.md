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

# AMPLIAR uma região que já foi coletada — USE --skip-collected:
.venv\Scripts\python.exe -m src.collect.collect_matches --platforms kr --players 500 --matches-per-player 20 --skip-collected

#   Sem a flag, a rodada re-percorre o TOPO do ladder (ORDER BY
#   league_points DESC), que já está inteiro, e cada partida é descartada
#   por já estar no banco. Medido em 2026-10-04: 150 jogadores rendem 88
#   partidas novas em 15 minutos. Com a flag, o filtro age ANTES do corte e
#   desce no ladder até achar 500 jogadores que ainda não têm partida — que
#   é o que amplia uma região de verdade.

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
# Garante que nenhum corte usa o quadro final de partida já encerrada (precisa do banco):
.venv\Scripts\python.exe tests	est_corte_sem_quadro_final.py
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
`.venv\Scripts\python.exe -m src.models.train_pro
```

> **Após recoletar**: a ordem é `load_items` → `build_features` →
> `export_model`, e **reiniciar a API** (ela carrega os modelos no
> startup). Depois de mexer em features/modelo, o `/predict` só reflete
> a mudança com a API reiniciada.

### 5b. Medidas que sustentam números do TCC

São os comandos que produzem os números citados no texto. Regra do projeto:
**um número só entra no TCC depois que o comando que o mede existe e o
resultado está em `reports/`.**

```powershell
# Quadros 3 e 4, Apêndice C (4 cortes × 3 modelos) + reports/metricas_corte.json:
# XGBoost com os hiperparâmetros DE PRODUÇÃO, Random Forest e MLP na
# configuração de referência; CV 5-fold com semente 42.
.venv\Scripts\python.exe -m src.models.multi_cutoff_metrics

# GridSearchCV na base final + reports/tune_models_39k.log/.json (~50s só
# com XGBoost). Sustenta a afirmação da 6.1 e do Apêndice F de que a
# limitação de taxa-base NÃO é subajuste. --completo acrescenta RF e MLP
# (~6 min) e mede a melhor combinação como no Quadro 3: são os valores
# ajustados que a 5.4 cita (acuracia_quadro3 / auc_quadro3 no JSON):
.venv\Scripts\python.exe -m src.models.tune_models_full
.venv\Scripts\python.exe -m src.models.tune_models_full --completo

# Robustez do número de dobras: 5 (trabalho) contra 10 (Kohavi), mesmos modelos
# e semente; ~10 min. Grava reports/robustez_dobras.json (Apêndice C):
.venv\Scripts\python.exe -m src.models.robustez_dobras

# Treino no passado, teste no futuro (Kaufman et al., 2012): divisão
# cronológica 80/20, por patch (treina 16.10 a 16.13, testa 16.14 a 16.19) e
# aleatória de mesmo tamanho, nos quatro cortes; ~3 min, precisa do banco
# (data e patch das partidas). Grava reports/holdout_temporal.json (Apêndice C):
.venv\Scripts\python.exe -m src.models.holdout_temporal

# Baseline (regressão logística) e IC 95% da diferença do XGBoost para os
# demais modelos, por bootstrap pareado; ~10 min. Grava
# reports/baseline_e_diferencas.json (Apêndice C):
.venv\Scripts\python.exe -m src.models.baseline_e_diferencas

# Taxa de vitória do azul por corte, no estado de empate
# + reports/taxa_base_por_corte.json:
.venv\Scripts\python.exe docs\taxa_base_por_corte.py

# Teste (iv) de robustez: Wilson + Holm sobre as taxas por corte, com a
# PARTIDA como unidade (bootstrap por partida, 2.000 reamostragens; a mesma
# partida pode estar empatada em mais de um corte). Sustenta a Seção 5.3;
# grava reports/vies_cortes_por_partida.json:
.venv\Scripts\python.exe docs\testa_diferenca_taxas.py

# --- Medidas do parecer do orientador (2026-11-08) ---
# Calibração nas partidas empatadas REAIS, fora da dobra, nos 4 cortes, mais
# sigmoide/isotônica sob o mesmo protocolo e a Figura 12 (~5 min). Substitui a
# comparação com o estado sintético todo-zero (Apêndice F, Quadros 23 e 24):
.venv\Scripts\python.exe docs\calibracao_empate_real.py
# Busca em grade ANINHADA de XGBoost, RF e MLP aos 15 min (~20 min). Coluna
# "seleção aninhada" do Quadro 3 e Quadro 12; grava reports/tune_models_aninhado.json:
.venv\Scripts\python.exe -m src.models.tune_models_aninhado
# Curva de aprendizado com teste FIXO e cortes sobre as MESMAS partidas (~2 min).
# Quadros 16 e 17; grava reports/curva_aprendizado.json:
.venv\Scripts\python.exe -m src.models.curva_aprendizado
# Ganho das variáveis novas dentro do mesmo classificador (logística contra
# logística; ~5 min, precisa do banco). Apêndice K; grava reports/ganho_variaveis_logit.json:
.venv\Scripts\python.exe -m src.models.ganho_variaveis_logit
# Quantos acertos escalares do gabarito dependem da regra "qualquer valor da
# 1ª linha" (sem API; reexecuta as SQLs gravadas). Grava reports/nlq_comparador_ambiguidade.json:
.venv\Scripts\python.exe -m src.nlq.confere_comparador
# Precisão, recall e F1 dos modelos ajustados e da logística (Quadro 3, ~3 min).
# Grava reports/metricas_ajustados.json:
.venv\Scripts\python.exe -m src.models.metricas_ajustados
# Versão do text-to-SQL medida no gabarito de 203: tag git `gabarito-203`
git show gabarito-203:src/nlq/nl_to_sql.py

# Teste (ii) de robustez: taxa do azul por faixa de duração total
# + reports/faixa_duracao.json:
.venv\Scripts\python.exe docs\testa_faixa_duracao.py

# Conversão de vantagem material, nos DOIS contextos e com a mesma
# definição de faixa:
.venv\Scripts\python.exe docs\confere_conversao_advantagem.py
```

```powershell
# Teste D1: calibração e regularização alternativa contra a discrepância de
# taxa-base da Seção 6.1 e do Apêndice F. LENTO (~40 min): cada variante roda validação
# cruzada aninhada. HISTÓRICO: o artefato é de 2026-11-06, antes da correção do
# vazamento (40.816 linhas); desde o parecer, a calibração do TCC vem de
# docs/calibracao_empate_real.py. Grava
# reports/experimento_calibracao.json, e o veredito sai de
# reports/experimento_calibracao_veredito.json:
.venv\Scripts\python.exe docs\experimento_calibracao.py

# Reavalia o veredito a partir do JSON, sem reexecutar o experimento (1s):
.venv\Scripts\python.exe docs\reavalia_calibracao.py
```

```powershell
# Experimento 10 (Apêndice K): placas de torre (TURRET_PLATE_DESTROYED)
# como feature plate_diff — ~10 min, varre 41 mil timelines. Grava
# reports/experimento_placas_torre.json:
.venv\Scripts\python.exe -m src.models.experiment_turret_plates
```

```powershell
# Experimento 11 (Apêndice K): percentis comportamentais do jogador
# (teamwork_pct_diff/expertise_pct_diff via lol-challenges-v1), sobre as
# partidas KR mais recentes (minimiza o gap entre a coleta e a consulta —
# lol-challenges-v1 devolve estado VITALÍCIO atual, não da época da
# partida). ~70-90 min (rate limit, ~4 mil jogadores únicos em 3000
# partidas) na primeira vez; reexecuções reusam
# reports/_cache_challenges_kr.json e só consultam jogador novo. Grava
# reports/experimento_challenges_piloto.json:
.venv\Scripts\python.exe -m src.models.experiment_challenges_pilot --n-matches 3000
```

> `reavalia_calibracao.py` é separado porque a primeira versão do
> experimento declarava *"VEREDITO: FECHA"* com um limiar que aceitava o
> próprio estado atual como sucesso: a variante de produção já estava em
> 1,7 pp e o corte era 2,0 pp. Limiar que aceita o estado atual como
> sucesso não é limiar, é noise floor. O critério corrigido exige desvio
> abaixo de 1,0 pp **e** custo de AUC abaixo de 0,001.

| artefato | quem consome |
|---|---|
| `reports/metricas_corte.json` | Quadros 3 e 4 e Apêndice C; checagem 5 |
| `reports/tune_models_39k.json` | Seção 5.4 (três modelos ajustados), 6.1 e Apêndice F; checagem 12 |
| `reports/taxa_base_por_corte.json` | Seção 5.3, 6.1 e Apêndice F |
| `reports/faixa_duracao.json` | Seção 4.5 e 5.3 (teste ii) |
| `reports/experimento_calibracao_veredito.json` | Apêndices K e F; checagem 14 |
| `reports/experimento_placas_torre.json` | Seção 5.4 e Apêndice K (experimento 10) |
| `reports/experimento_challenges_piloto.json` | Seção 5.4 e Apêndice K (experimento 11) |

> `reports/tune_models_39k.log` cai no `.gitignore` (`*.log`) e não é
> versionado; o `.json` é, e é dele que a checagem 12 lê. O log é a versão
> legível e se regenera com o comando acima.

### 5c. Conferir o texto e o entregável

Antes de fechar o TCC, quatro checagens automáticas. Todas saem com exit 1
quando algo diverge, e todas devem passar.

```powershell
# 23 checagens de consistência do texto contra o banco e os artefatos.
# A lista completa e o docstring de docs/verifica_tcc.py; a checagem 22
# confere que o numero aqui afirmado bate com o que a suite imprime, entao
# este comentario nao pode divergir sem reprovar.
#   1-5   texto e formatacao (CJK, referencias cruzadas, tabelas, ABNT,
#         numeros de modelo)
#   6-8   numero contra artefato (Quadro 1 x banco, dataset profissional x
#         banco, guard de residuo + Abstract english)
#   9-14  figuras, fontes, anglicismos, tuning, citacoes, calibracao
#   15    scripts que produzem medida estao documentados aqui
#   16    regioes: o texto nao uniformiza o que o IC nao sustenta
#   17    teste (ii) de faixa de duracao x artefato E x banco
#   18    as DUAS bases declaradas onde cada numero aparece
#   19    accuracy do NLQ: artefato, ou declaracao de lacuna com a chave
#         comprovadamente ausente
#   20    treino no passado e teste no futuro (holdout) x artefato
#   21    Apendice M (experimentos 12 a 19) e coach x artefatos
#   22    o numero de checagens que os docs afirmam e o real
#   23    nenhuma figura mais velha que o codigo ou artefato que ela mostra
#         (excecao declarada: Figura 5, sem credito de API para recapturar)
.venv\Scripts\python.exe docs\verifica_tcc.py

# Conformidade formal do .docx gerado: títulos em negrito, contagem de
# títulos e de referências, legendas, fontes, tabelas, imagens.
# Rode DEPOIS de build + finalize-fields:
.venv\Scripts\python.exe docs\confere_docx.py

# Paginas do corpo (25-30) e de cada apendice, medidas pelo Word, so leitura.
# O finalize-fields.ps1 ja chama no fim e sai com o codigo dele (~20 s):
powershell -ExecutionPolicy Bypass -File docs\confere_paginas.ps1

# Materiais da defesa (guia, pptx, README, handoff, scripts.md, telas) contra
# os valores substituidos do verifica_tcc; site e deck sao artefatos
# publicados, passe as copias locais (sem argumento, ficam de fora):
.venv\Scripts\python.exe docs\confere_materiais.py
.venv\Scripts\python.exe docs\confere_materiais.py <estudo.html> <pasta-do-deck>
```

### 5d. Regerar as figuras (recortes da Seção 5 e telas do Apêndice E)

```powershell
# A API precisa estar em :8000 e o frontend na porta LIBERADA NO CORS
# (:5173). Servir em outra porta funciona no navegador até a página fazer
# fetch, e aí o Chromium renderiza o banner de erro.
Push-Location frontend; npx vite preview --port 5173; Pop-Location
$env:FRONT_URL = "http://localhost:5173"
.venv\Scripts\python.exe docs\capturar_figuras_texto.py   # 5 recortes do corpo (Figuras 1-5)
.venv\Scripts\python.exe docs\recapturar_anexo_a.py       # 6 telas inteiras (Apêndice E)
```

Os recortes vão para `reports/figuras_texto/` (registro em `figuras.json`,
inclusive a SQL gerada na figura da consulta NL, que chama a API da
Anthropic). As telas inteiras vão para `reports/anexo_a/` (o nome da pasta
ficou de quando eram Anexo A). Os dois scripts recusam a captura se a página
mostrar "Erro no servidor" ou se o arquivo sair vazio. Vale deixar essa
trava: sem ela o script grava a tela de erro e reporta sucesso.

---

## 6. Interface em linguagem natural (NLQ)

```powershell
# Rodar uma pergunta pelo terminal:
.venv\Scripts\python.exe -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"

# Benchmark de execution accuracy (exigência da banca):
# grava reports/nlq_benchmark.json (accuracy, base e desfecho por pergunta)
.venv\Scripts\python.exe -m src.nlq.evaluate_nlq

# Conjunto de perguntas pelo caminho do PRODUTO (roteador, base, guarda, nova
# tentativa). Grava a cada pergunta, com o hash dos 4 arquivos do sistema; para
# limpo se a API falhar (créditos, rede) e retoma com --retomar. NÃO julga acerto:
# quem julga é uma pessoa lendo a SQL e as linhas (docs/revisao_nlq_*.md).
# O conjunto CEGO (docs/nlq_perguntas_cegas.txt) roda UMA vez, com o sistema
# congelado: não ajuste o sistema depois de ver o resultado.
.venv\Scripts\python.exe -m src.nlq.avaliar_conjunto --perguntas docs/nlq_perguntas_cegas.txt --saida reports/nlq_cego_resultado.json --rotulo cego
.venv\Scripts\python.exe -m src.nlq.avaliar_conjunto --perguntas docs/nlq_perguntas_cegas.txt --saida reports/nlq_cego_resultado.json --rotulo cego --retomar

# Auditoria do coach (Seção 4.7 e Apêndice B): 36 respostas pelo caminho do
# produto, cada número conferido contra os dados do prompt. Grava
# reports/coach_audit.json. A revisão manual dos sinalizados fica em
# reports/coach_audit_revisao.json (checagem 21 confere os dois).
# A saída da IA varia (temperatura 0,4): rode UMA vez e guarde.
.venv\Scripts\python.exe -m src.coach.audit_grounding --n 36
# recalcula só as métricas da saída gravada, sem chamar o modelo:
.venv\Scripts\python.exe -m src.coach.audit_grounding --reanalisar
```

> **Regra da casa**: sempre rode `evaluate_nlq` de novo depois de
> QUALQUER mudança em `src/nlq/schema_context.py` — já regrediu
> silenciosamente 2×. O benchmark de 26 perguntas **não é independente** (as
> regras do esquema foram escritas conhecendo as 3 falhas antigas): hoje dá 26/26.
> A medida independente é o gabarito automático (181/203, 89,2%): `python -m src.nlq.gerar_gabarito` (gera), `python -m src.nlq.avaliar_conjunto --perguntas docs/nlq_perguntas_203.txt --saida reports/x.json` (roda) e `python -m src.nlq.avaliar_gabarito --resultado reports/x.json --saida reports/y.json` (compara). A consulta roda em transação somente leitura
> (`tests/test_run_query_readonly.py`).
>
> O comando exige `ANTHROPIC_API_KEY`. Sem ela o Apêndice B fica sem
> artefato: em 2026-10-04 o número publicado (23/26) vinha da saída de
> console e não de `reports/`.

---

## 7. Testes

```powershell
# Smoke test (sem banco/API, roda em tempdir — não toca dados reais):
.venv\Scripts\python.exe tests\smoke_test.py

# Bateria de validação comportamental do modelo de produção
# (precisa do modelo exportado; ~30s):
.venv\Scripts\python.exe tests\validate_predictions.py
```

O smoke test e a bateria saem com código 1 em caso de falha e podem ser
usados como portão em CI ou script. A bateria imprime um veredito de
três estados — `APROVADO`, `APROVADO COM RESSALVAS` ou `REPROVADO`:
ressalvas são casos em que o modelo exibe a limitação que o TCC 5.2
declara, ou em que um fator tem peso despresível naquele corte (SHAP
abaixo de 0,05), e por isso a direção não é exigível. Detalhes em
`docs/scripts.md`.

---

## 7b. Gerar o documento do TCC (.docx)

Sempre que alterar `docs/tcc2_texto.md`, regere o entregável:

```powershell
# TCC 1 é usado só como REFERÊNCIA DE ESTILO (fonte, margens, espaçamento);
# o conteúdo dele não é lido. Ajuste o caminho para o seu arquivo.
$env:TCC1_REFERENCE_DOCX = 'C:\Users\Home\Downloads\TCC\TCC_Final.docx'

# 1. markdown -> .docx (pandoc gera o corpo; python-docx monta capa,
#    folha de rosto, numeração de Quadros e Figuras, insere as 5 figuras
#    do corpo e as 6 telas do Apêndice E)
.\.venv\Scripts\python.exe docs\build_tcc_docx.py

# 2. o Word preenche a numeração dos campos SEQ e PAGE (não há sumário nem
#    listas: nenhum dos 10 TCC II aprovados usa)
powershell -ExecutionPolicy Bypass -File docs\finalize-fields.ps1
```

O passo 2 não é opcional: campos `SEQ` nascem vazios e sem ele o
documento sai com Quadros e Figuras sem número. O script também repagina e
reporta a contagem final de páginas — útil para conferir o limite de 30,
contadas do Resumo ao fim das Referências.

Precisa de `pandoc` no PATH (`winget install JohnMacFarlane.Pandoc`) e
`python-docx` no venv. Detalhes em `docs/scripts.md`.

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
5.  python -m src.etl.load_items             # itens (compras/vendas por partida)
6.  python -m src.etl.load_item_catalog      # catálogo de itens (nome/custo) — 1x, só se data/items.json mudar
7.  python -m src.features.build_features     # features por fase
8.  python -m src.models.train_baseline       # baseline
9.  python -m src.models.tune_models          # tuning + calibração
10. python -m src.models.export_model         # modelos de produção
11. python -m src.collect.collect_pro         # + competitivo (opcional)
12. python -m src.etl.load_pro
13. uvicorn src.api.main:app --port 8000     # API
14. cd frontend && npm run dev                # front
```

## Antes de entregar o TCC

Não faz parte do pipeline de dados, mas é o que garante que os números do
texto existam de verdade. Ver **5b**, **5c** e **5d**.

```
15. python -m src.models.multi_cutoff_metrics  # Apêndice C + metricas_corte.json
16. python -m src.models.tune_models_full --completo  # lastro da 5.4, 6.1 e Apêndice F
17. python docs/verifica_tcc.py               # 23 checagens, exit 0
18. python docs/build_tcc_docx.py             # gera o .docx
19. powershell -File docs/finalize-fields.ps1  # campos + confere_paginas (corpo 25-30), exit 0
20. python docs/confere_docx.py               # conformidade formal, exit 0
21. python docs/confere_materiais.py          # guia, pptx, README sem numero velho, exit 0
```

## Experimentos de precisão (2026-11-03, exploratório, não altera o modelo de produção)

```powershell
# variáveis ricas (base única de 41.063 partidas); grava data/features_v2.csv.gz
.venv\Scripts\python.exe -m src.features.build_features_v2
.venv\Scripts\python.exe tests\test_features_v2_sem_vazamento.py        # 0 vazamentos em 703 pares
# experimentos 12 a 18 -> reports/experimentos_precisao.json (Apêndice K)
.venv\Scripts\python.exe -m src.models.experiment_precisao --cutoffs 15 25
# treino no passado, teste no futuro com as variáveis novas -> reports/holdout_precisao.json
.venv\Scripts\python.exe -m src.models.holdout_precisao --cutoffs 15 25
# experimento 19, histórico do jogador por estrato -> reports/experimento_historico.json
.venv\Scripts\python.exe -m src.models.experiment_historico --cutoffs 15 25
```
