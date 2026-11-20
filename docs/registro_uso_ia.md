# Registro de uso de IA generativa no projeto (levantamento de 2026-11-11)

**Permissão:** o orientador permitiu o uso de IA (informado pelo autor em
2026-11-11). A permissão não dispensa a divulgação pedida pela CONSUN 35/2025.

**Status: rascunho de trabalho, só leitura. Não entra no TCC, não foi commitado e
não foi enviado a ninguém.** Serve de base para o autor decidir o que declarar
(Resolução CONSUN 35/2025, itens B.I e C.II). Tudo abaixo vem do histórico do
`git` e de metadados de arquivos; nada foi lido das conversas.

## 1. O que o repositório prova

Todos os commits foram feitos na conta `tamiosso125`. O que identifica a IA é a
linha `Co-Authored-By`, que a ferramenta acrescenta à mensagem.

| | Commits |
|---|---:|
| Na branch `main` | 182 |
| Mais 1 commit fora da `main` (o da tag `gabarito-203`) | 1 |
| **Total (sem merges)** | **183** |
| Com `Co-Authored-By: Claude` | **144** (143 na `main` + o da tag) |
| Sem essa linha | 39 |

Por modelo, como a própria linha registra:

| Modelo (conforme o `Co-Authored-By`) | Commits | Primeiro | Último |
|---|---:|---|---|
| Claude Haiku 4.5 | 1 | 2026-07-07 | 2026-07-07 |
| Claude Opus 4.8 | 1 | 2026-07-08 | 2026-07-08 |
| Claude Sonnet 5 | 28 | 2026-07-06 | 2026-11-06 |
| Claude Sonnet 5.5 | 72 | 2026-10-06 | 2026-11-06 |
| Claude Opus 5.5 | 42 | 2026-10-28 | 2026-11-10 |

Por mês (todos os commits, com e sem a linha):

| Mês | Com Claude | Sem |
|---|---:|---:|
| 2026-07 | 24 | 5 |
| 2026-10 | 20 | 34 |
| 2026-11 | 100 | 0 |

(Não há commits em agosto e setembro; o primeiro é de 2026-07-04.)

## 2. O que esses commits tocaram

Arquivos alterados nos commits com a linha de Claude (commits que mexem na área,
linhas acrescentadas e removidas). **As linhas não medem autoria:** `reports/` e
`docs/tcc2_final.docx` são arquivos gerados por scripts, e um commit pode misturar
texto escrito pelo autor com texto escrito ou revisado pela IA.

| Área | Commits | Linhas + | Linhas − |
|---|---:|---:|---:|
| `reports/` (resultados gerados) | 29 | 47.887 | 3.333 |
| `docs/` em geral (diário, scripts, guias, conferentes) | 112 | 27.731 | 1.897 |
| `src/` (coleta, ETL, modelos, API, NLQ, coach) | 38 | 5.969 | 392 |
| `frontend/` | 23 | 5.702 | 1.583 |
| `docs/tcc2_texto.md` (texto do TCC) | 64 | 3.342 | 3.382 |
| `tests/` | 9 | 1.237 | 25 |

Nos 39 commits **sem** a linha: `docs/` 36 commits, `docs/tcc2_texto.md` 27 commits,
`src/` 11, `frontend/` 4, `tests/` 4.

## 3. O que este levantamento NÃO prova

1. **A linha `Co-Authored-By` é um piso, não uma medida.** Falta ela em 39 commits,
   e 34 deles são de 2026-10-03 e 2026-10-04, imediatamente antes de a linha
   aparecer (a primeira de Sonnet 5.5 é de 2026-10-06). Várias mensagens desses dias
   estão escritas em primeira pessoa e narram erros e correções ("eu tinha
   apagado…", "tres numeros que eu ainda tinha errado"). Isso é indício de estilo,
   **não prova** de que a IA os escreveu. **Só o autor sabe quais foram feitos com
   IA.**
2. **O git só mostra commits.** Explicações, revisões e rascunhos que não viraram
   commit não aparecem.
3. **Os *prompts* não estão no repositório.** Ficam no histórico das sessões do
   Claude Code, em `C:\Users\Home\.claude\projects\c--Users-Home-Documents-Faculdade-lol-analytics\`:
   - `98bb348a-…jsonl`: 390 MB, a sessão principal, de 2026-11-05 em diante
     (modificada em 2026-11-11);
   - `12488a2a-…jsonl`: praticamente vazia, de 2026-11-05.
   - **Não há transcrição local de julho a 4 de novembro**, embora haja commits
     com a linha de Claude nesse período. Os *prompts* desse período não podem ser
     reconstruídos a partir daqui.
4. **Outra ferramenta de IA está configurada**, sem prova de uso: `opencode.json`
   aponta para um modelo local (`ollama/qwen2.5-coder:14b`) e há agentes em
   `.opencode/` (orquestrador, revisor, validador, doc-tcc), versionados desde
   2026-10-03. Não há marca desse modelo nas mensagens de commit.

5. **ChatGPT também foi usado, fora do repositório:** três relatórios de
   pesquisa na pasta `Downloads/TCC` ("Pesquisa artigos TCC.pdf",
   "Pesquisa artigos TCC (1).pdf", "Análise de links TCC.pdf") têm "criador:
   ChatGPT" nos metadados e datas de 13 a 15 de abril de 2026 (fase do TCC I:
   levantamento de artigos e da Riot API). Comparação de trechos de 8+ palavras
   com o TCC II: nenhum trecho passou para o texto, só duas expressões curtas
   ("até 85% de acurácia após 5 minutos de jogo", "para análise de dados de
   League of Legends"). Isso também entra na declaração.

## 4. Não confundir com a IA que faz parte do produto

O TCC já declara, na Metodologia (4.7, 4.8) e no Apêndice B, que a interface em
linguagem natural e o módulo de orientação estratégica da plataforma usam o
**Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) via API da Anthropic, com as
temperaturas e os limites de saída de cada etapa. Isso é componente do sistema
estudado, não apoio à elaboração do trabalho. A declaração pedida pela resolução
trata do segundo caso.

## 5. O que o autor precisa responder antes de qualquer texto de declaração

Eu não tenho como afirmar estas respostas:

1. **O que o contrato pedagógico do TCC II e o orientador permitem** em uso de IA?
   (A resolução recai a decisão sobre o professor de cada atividade.)
2. **Em que partes o autor escreveu e em que partes a IA escreveu ou revisou:**
   código, scripts de análise, texto do TCC, quadros, figuras, interface?
3. **O autor leu e validou o que foi integrado?** Como (conferência de números
   contra `reports/`, revisão do texto, testes)?
4. **Quais dos 39 commits sem a linha foram feitos com IA?** E o modelo local do
   `opencode.json` chegou a ser usado?
5. **Há *prompts* anteriores a 5 de novembro** guardados em algum outro lugar
   (histórico do editor, notas)? Se não, a declaração deve dizer que eles não
   estão disponíveis.

## 6. Onde isso encaixa nas diretrizes (CONSUN 35/2025)

| Pedido da resolução | Situação neste levantamento |
|---|---|
| Nome da ferramenta | Claude (Anthropic), via Claude Code; opencode/Ollama configurado, uso não confirmado |
| Versão | Tabela da seção 1 |
| Data de uso | 2026-07-06 a 2026-11-10 (commits com a linha) |
| Seções do texto em que foi empregada | **Depende da resposta 2** |
| *Prompts* utilizados | Disponíveis só de 2026-11-05 em diante; antes disso, indisponíveis |
| Finalidade | **Depende da resposta 2** |
| Como o resultado foi integrado | **Depende das respostas 2 e 3** |
