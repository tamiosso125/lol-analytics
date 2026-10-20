# Plano de contingência — reduzir o corpo do TCC, se precisar abrir espaço

## Por que este documento existe

Em 2026-10-05 (Bloco E da revisão completa) o corpo do TCC II (Seção 1
até o início de REFERÊNCIAS, medido por `docs/finalize-fields.ps1`)
fechou em **30 páginas — o teto exato da faixa institucional 25-30**.
Não há folga: qualquer frase nova dentro das Seções 1-6 empurra o corpo
para fora da faixa permitida, e só se descobre isso rodando o pipeline
completo (`build_tcc_docx.py` → `finalize-fields.ps1`), não lendo o
Markdown.

Se o orientador ou a banca pedir acréscimo de texto no corpo — uma
discussão mais longa, um parágrafo de limitação adicional, resposta a
uma pergunta de defesa incorporada ao texto — este plano é o ponto de
partida: o que cortar primeiro, por quê, e quanto cada corte libera.
Não é para ser executado agora (o TCC está fechado); é para não
precisar redescobrir, sob pressão de prazo, onde o texto tem gordura e
onde é osso.

## Regra de ouro ao aplicar qualquer corte

1. Aplicar um tier por vez, do mais seguro para o mais arriscado —
   parar assim que as páginas necessárias estiverem liberadas.
2. Depois de cada corte: `build_tcc_docx.py` → `finalize-fields.ps1`
   (mede o corpo de novo) → `docs/verifica_tcc.py` → `docs/confere_docx.py`.
   Um corte que tira um número que o `verifica_tcc.py` cruza contra
   artefato quebra a suíte — ajustar a checagem junto, nunca remover a
   checagem pra fazer passar.
3. Nenhum corte deste plano apaga dado medido. Nos Tiers 0 e 1 a
   informação continua no documento (só muda de lugar ou de nível de
   detalhe); no Tier 2, qualquer coisa removida teria que ir para o
   diário de execução antes de sair do `.md`, para não se perder — a
   regra do projeto é "número sempre vem de artefato real", e isso vale
   também para não destruir o rastro depois de ele existir.

> **Executado em 2026-10-20** (ao inserir 14 referências novas, o corpo
> foi a 31 páginas): 0b (lista dos 11 experimentos da 5.4 trocada por
> remissão ao Apêndice D) e metade de 0a (a "Nota de método" do Quadro 1 e
> a origem das taxas de conversão foram para o novo **Apêndice E**; a "Nota
> sobre as bases" ficou na 5.3 porque a checagem 18 do `verifica_tcc.py` a
> exige). Corpo voltou a 30/30. **O teto continua sem folga**: o que ainda
> pode sair sem perda é só a "Nota sobre as bases" e o Tier 1.

## Tier 0 — mover para apêndice (perda de informação: zero)

A Seção 5 (Resultados) tem 445 linhas de Markdown — mais que o dobro de
qualquer outra seção do corpo (Introdução 179, Fundamentação 180,
Trabalhos Relacionados 129, Metodologia 160, Conclusão 110). É aqui que
sobra texto para mover, não nas outras seções.

**0a. As três notas de método em itálico da Seção 5.2/5.3** já são
parentéticas — o texto principal funciona sem elas, só perde a
proveniência detalhada dos números:
- "Nota sobre as bases usadas nesta seção e na modelagem" (após o
  título 5.3, ~14 linhas) — explica a diferença entre 41.063 e 39.426.
- "Nota de método: quadro original..." (depois do Quadro 1, ~19 linhas)
  — histórico das três rodadas de medição do viés de lado.
- Parêntese final de "Conversão de vantagem" (~7 linhas) — aponta o
  script e a base usada.

Juntas, ~40 linhas densas (≈1 página impressa). Mover as três para um
novo "Apêndice E — Notas de proveniência das bases e medições" (ou para
dentro do Apêndice C, que já é sobre métricas por corte) libera essa
página inteira sem tirar uma frase do trabalho — elas continuam
citáveis e citadas (ex.: "ver Apêndice E" no lugar do parêntese).
**Maior ganho por menor risco deste plano — primeiro candidato.**

**0b. A lista de 11 experimentos enumerados por nome na Seção 5.4**
("diferença de abates de Barão/Arauto, dispersão espacial do time,
ajuste de hiperparâmetros..." — linhas ~1006-1021 do
`tcc2_texto.md` atual) **duplica, com menos detalhe, a tabela que já
existe no Apêndice D** (Quadro — Experimentos negativos, com resultado
por linha e notas individuais dos experimentos 4/10/11). Trocar a
enumeração por uma frase curta — "onze tentativas de enriquecimento de
variáveis não produziram ganho estatisticamente distinguível de ruído
(Apêndice D)" — mantendo os números de volume que vêm logo depois
(esses são o achado real da subseção, não a lista). Libera ~12-15
linhas sem apagar nada: o detalhe already existe no Apêndice D.

Estimativa combinada do Tier 0: **~1,5 página**. Como o corpo está
exatamente no teto (30/30), isso por si só devolve folga para 1-2
parágrafos novos sem tocar em conteúdo nenhum.

## Tier 1 — condensar (perda: baixa, pede revisão de quem escreveu)

**1a. Repetição de números do viés de lado por região.** As taxas de
BR1/EUW1/KR/NA1 aparecem por completo pelo menos três vezes: no Quadro
1 (5.3), na nota de método logo depois (já candidata ao Tier 0), e de
novo na bateria de testes de robustez (5.3) e na limitação
"Desequilíbrio de amostra por região" (5.8). Manter os números só no
Quadro 1 e, nas outras três ocorrências, referenciar ("conforme o
Quadro 1") em vez de reafirmar os quatro percentuais — a direção do
argumento não precisa dos números repetidos para se sustentar.

**1b. Os dois primeiros itens da Seção 5.8 (Limitações)** — a
discrepância de taxa-base e a diferença entre a base do modelo e a base
do banco — são, cada um, parágrafos de 15-25 linhas com nível de
detalhe de apêndice (grade search completo, as três alavancas
testadas, o comando exato). O achado (existe discrepância, foi
investigada, não é subajuste) cabe em metade do espaço sem perder a
conclusão; o detalhe do procedimento já está, em grande parte, também
no texto de `docs/experimento_calibracao.py` e no próprio artefato
JSON. Resumir mantendo a conclusão e o ponteiro pro artefato, cortando
a narrativa passo a passo de qual alavanca foi tentada em qual ordem.

Estimativa combinada do Tier 1: **~1 página**, com revisão (não é corte
mecânico — exige reler para garantir que a conclusão continua
sustentada sem a repetição).

## Tier 2 — cortar de verdade (perda real de conteúdo — último recurso)

**2a. Seção 5.7 (Os resultados frente à literatura)** tem cinco
parágrafos, um por referência de Trabalhos Relacionados, 8-10 linhas
cada. É o tipo de seção que a banca costuma valorizar (mostra que o
autor sabe posicionar o próprio trabalho), então cortar aqui tem custo
acadêmico, não só de espaço — fazer por último, e preferir condensar
(2-3 frases por referência) a eliminar alguma comparação inteira.
Estimativa: ~0,5-1 página, só se os Tiers 0 e 1 não bastarem.

**2b. Bullets finais da Seção 5.8** (cobertura por patch, ausência de
micro-posicionamento, monotonicidade isolada) são mais curtos e menos
centrais ao argumento principal do trabalho do que os dois primeiros.
Eliminar um deles inteiro (não condensar — remover) é o corte de maior
risco deste plano: mexe na lista de limitações declaradas, que a banca
pode perguntar sobre diretamente. Só considerar se nada mais for
suficiente, e registrar no diário de execução o que foi removido e por
quê, antes de apagar do `.md`.

## Se o pedido for o oposto — abrir espaço cortando dos pré/pós-textuais

Apêndices e Anexos **não contam** para o limite de 25-30 páginas do
corpo (confirmado em `docs/finalize-fields.ps1` — o corpo é medido de
"1 INTRODUÇÃO" até o início de "REFERÊNCIAS"). Então, se o problema for
"documento geral ficou grande demais" e não especificamente o corpo
regulado, mexer lá (ex.: Apêndice C mais enxuto) não resolve o teto do
corpo — só ajuda a legibilidade geral. Os dois problemas são
independentes; este plano é só sobre o corpo.
