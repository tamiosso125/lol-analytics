# Análise da escrita: o nosso TCC contra os 10 TCC II aprovados

Feita em 2026-11-02. Objetivo: verificar se a linguagem do texto está no
registro dos trabalhos que a UNISINOS aprovou e apontar o que ajustar.

## Como foi medido

- **Corpus:** os 10 PDFs de `Downloads/TCC II - EXEMPLOS E MATERIAIS/`
  (5 com aprovação com distinção) e o nosso `docs/tcc2_final.docx`.
- **Trecho medido:** o corpo, da "1 INTRODUÇÃO" ao início das
  REFERÊNCIAS. Os textos dos colegas vêm do PDF (inclui tabelas e
  legendas); o nosso vem dos parágrafos do .docx (exclui tabelas). Isso
  **favorece os colegas** em métricas como parênteses e números, então
  quando o nosso fica acima deles a diferença é real.
- **Normalização:** toda contagem é por 1.000 palavras. Os corpos têm de
  5.632 a 8.070 palavras; o nosso tem 6.991.
- **Scripts:** `extrai.py`, `metricas.py` e `metricas2.py`, no scratchpad
  da sessão (não versionados; são leitura, não produzem número do TCC).

Os números abaixo descrevem estilo, não qualidade. Um valor fora da faixa
dos dez aprovados é um sinal para revisar, não um erro por definição.

## Resultado: onde estamos dentro da faixa

| Métrica (por 1.000 palavras) | Aprovados (mín–mediana–máx) | Nosso |
|---|---|---|
| Travessão "—" na prosa | 0,0 – 0,0 – 0,4 | **0,0** |
| Hífen solto " - " como pontuação | 0,0 – 0,3 – 2,3 | **0,0** |
| Meia-risca "–" | 0,0 – 1,1 – 2,8 | 1,6 (só nas legendas "Quadro 1 – …") |
| Primeira pessoa (eu, nós, nosso) | 0,0 – 0,0 – 0,7 | 0,0 |
| "Este/o presente trabalho" | 0,6 – 1,6 – 2,8 | 2,3 |
| Frase média (palavras) | 24,6 – 31,7 – 41,6 | 33,4 |
| Frases com mais de 40 palavras | 11,8% – 21,5% – 31,6% | 24,9% |
| Voz passiva analítica (foi/foram + particípio) | 5,7 – 9,3 – 15,1 | 6,3 |
| Aspas | 1,1 – 5,3 – 12,8 | 0,9 |

**Travessões e hífens:** o corpo **não usa** travessão nem hífen como
pontuação. As únicas meias-riscas são as das legendas, que seguem o modelo
do professor. A preocupação com "uso constante de -" não se confirma no
texto atual; ela valia para versões antigas, e o Abstract perdeu os dois
travessões que ainda tinha em 2026-11-02.

## Resultado: onde estamos fora da faixa

| Métrica (por 1.000 palavras) | Aprovados (mín–mediana–máx) | Nosso | Leitura |
|---|---|---|---|
| Construção ", e não X" | 0,0 – 0,0 – 0,1 | **2,1** (15 vezes) | marca de estilo própria; nenhum colega usa |
| "não" | 1,5 – 3,1 – 10,3 | 7,2 | consequência da anterior |
| Parênteses | 8,7 – 13,1 – 16,0 | **27,2** (187) | o dobro da mediana, acima do máximo |
| Remissões "(Seção X)", "(Apêndice Y)" | 0,0 – 0,0 – 1,4 entre parênteses | **2,6** | texto que remete demais a outras partes |
| Ponto e vírgula | 0,0 – 1,9 – 5,9 | **8,0** | ~25 juntam duas frases inteiras |
| Termos em inglês | 0,0 – 0,7 – 4,3 | **10,7** | parte é do domínio, parte é traduzível |
| Contração "num/numa" | 0,0 – 0,0 – 0,1 | **1,3** (9) | registro oral |
| "só" (no lugar de apenas/somente) | 0,0 – 0,1 – 0,1 | **1,4** (10) | registro oral |
| Conectivos (além disso, portanto, dessa forma, por exemplo, ou seja, pois) | 1,1 – 2,7 – 4,2 | **0,0** | texto telegráfico, sem transições |
| Datas ISO (2026-10-04) | 0 em todos | 4 | formato de diário, não de texto acadêmico |
| Código no corpo (`python -m`, `ITEM_UNDO`, `monsterSubType`) | 0 em todos | 5 | nenhum colega põe comando ou identificador no corpo |
| Percentuais | 0,3 – 1,8 – 12,5 | 6,7 | esperado para um trabalho de dados |
| Números | 24,2 – 32,6 – 92,4 | 57,4 | idem; dentro da faixa |

### Os achados em detalhe

**1. A construção ", e não X" (15 ocorrências; zero nos colegas).** É o
traço mais característico do nosso texto, e lê como fórmula repetida.
Exemplos: "comparou três, por medição, e não por preferência"; "o que
torna o erro de conversão mensurável, e não ilustrativo"; "e não por
vencer em todos os cortes"; "e não um único modelo genérico". Algumas são
necessárias (marcam uma delimitação real); a maioria pode virar afirmação
direta.

**2. Parênteses demais (187).** Por conteúdo: 83 com número ou estatística
("(n = 3.294)", "([55,4%, 57,2%])"), 38 com explicação, 26 com termo ou
glosa, 20 com citação e 20 com remissão. Os colegas põem número em quadro e
explicação em frase própria. O nosso empilha as duas coisas dentro da
frase, o que alonga a leitura.

**3. Ponto e vírgula juntando frases.** Das 56 ocorrências, cerca de 13
são de listas (objetivos, conclusão a–g, roteiro da Introdução) e são
normais. As outras ~25 ligam duas orações completas ("o viés existe e tem
magnitude praticamente constante; o que a amostra maior desfez foi…").
Ponto final resolve a maioria.

**4. Registro oral: "num/numa" (9) e "só" (10).** No texto acadêmico
brasileiro, "em um/em uma" e "apenas/somente". Os dez aprovados praticamente
não usam "num" nem "só".

**5. Nenhum conectivo de transição.** Zero ocorrências de "além disso",
"portanto", "dessa forma", "por exemplo", "ou seja", "pois". Os colegas
usam de 1 a 4 por mil palavras. É efeito das rodadas de condensação: cada
frase carrega informação, mas as passagens entre elas ficam secas. Não é
para encher de conectivo; é para pôr um onde a relação de causa ou de
consequência não está explícita.

**6. Termos em inglês (10,7 contra no máximo 4,3).** Os mais frequentes:
*solo queue* (20), *machine learning* (13), *benchmark* (5), *dashboards*
(4+2), *features* (4+1), *text-to-SQL* (3), *draft* (3), *dataset* (3),
*endpoints* (2+2), *folds* (2), *pipeline* (2). *Solo queue*, *draft* e
*text-to-SQL* são do domínio e não têm tradução estabelecida; *dashboards*
está no objetivo f, herdado do TCC I. Os traduzíveis: *features* →
"variáveis preditoras" (o texto já usa as duas), *dataset* → "base" ou
"conjunto de dados", *benchmark* → "conjunto de perguntas de referência",
*pipeline* → "fluxo", *folds* → "dobras", *machine learning* → alternar com
"aprendizado de máquina".

**7. Marcas de diário e de código no corpo.** Quatro datas ISO na 5.2 e
5.3 ("no retreino de 2026-07-06", "de 2026-10-04") e cinco trechos de
código: o comando `python -m src.models.multi_cutoff_metrics` (5.4),
`ITEM_UNDO` (4.4), `monsterSubType` (5.4) e `monotone_constraints` (6.1).
Nenhum dos aprovados faz isso. O lugar do comando é o apêndice; a data
pode ser "em outubro de 2026" ou sair.

## Citações: regra da ABNT 2023, conferida no manual da UNISINOS

O *Manual para elaboração de trabalhos acadêmicos 2026* (p. 171-189)
segue a ABNT NBR 10520:2023: sobrenome em **maiúsculas e minúsculas** tanto
na citação narrativa quanto entre parênteses, e, entre parênteses, autores
separados por **ponto e vírgula** ("(Mattos; Silveira, 1998)"), com "e" só na
forma narrativa ("Mattos e Silveira (1998)").

- **Caixa:** o nosso está certo, "(Kohavi, 1995)". Os colegas usam
  "(SILVA, 2020)", da regra antiga; não é para copiar.
- **Ponto e vírgula entre autores, entre parênteses:** o nosso usa "e" em
  vários lugares. Exemplos: "(Grinsztajn, Oyallon e Varoquaux, 2022)",
  "(Ribeiro, Singh e Guestrin, 2016)", "(Brown, Cai e DasGupta, 2001)",
  "(Niculescu-Mizil e Caruana, 2005)", "(Chen e Guestrin, 2016)" na lista da
  abertura da Seção 3 e "(Hornik, Stinchcombe e White, 1989)". Já estão
  certos "(Creswell; Creswell, 2023)" e "(Prodanov; Freitas, 2013)", o que
  deixa o texto inconsistente.
- **Citação sem ano:** na 3.6, "(García-Méndez e Arriba-Pérez)", "(Jiang et
  al.; Guo et al.)" e "(Wallner, Wang e Dormann)" estão sem o ano, que a
  norma exige.

## Resultado da correção (2026-11-03)

Os oito passos foram aplicados ao corpo, cada um verificado
(`verifica_tcc.py`, `confere_docx.py`) e medido; o documento seguiu em 29
páginas. Medição repetida com os mesmos scripts, por 1.000 palavras:

| Métrica | Aprovados (mediana) | Antes | Depois |
|---|---|---|---|
| ", e não X" | 0,0 | 2,1 | **0,0** (os 4 que restam estão nos Apêndices C, F e G) |
| "num/numa" | 0,0 | 1,3 | **0,0** |
| "só" | 0,1 | 1,4 | **0,0** |
| Datas ISO | 0,0 | 0,6 | **0,0** |
| Código no corpo | 0,0 | 0,1 | **0,0** |
| Termos em inglês | 0,7 | 10,7 | **8,4** (o resto é do domínio: *solo queue*, *draft*, *text-to-SQL*, *benchmark*) |
| Conectivos | 2,7 | 0,0 | **0,6** |
| Ponto e vírgula | 1,9 | 8,0 | **7,5** (sobram as listas a) a g), os testes (i) a (iv) e as citações) |
| Parênteses | 13,1 | 27,2 | **25,2** |
| Remissões | 2,3 | 9,4 | **7,5** |
| Frase média (palavras) | 31,7 | 33,4 | **30,7** |

O que **não** chegou à faixa dos aprovados, e por quê:

- **Parênteses e remissões** continuam acima. Boa parte é número
  (estatísticas e tamanhos de amostra) e citação, que um trabalho de dados
  tem de ter; tirar mais exigiria passar números para quadros, o que
  custaria páginas.
- **Termos em inglês** ainda passam do máximo (4,3). Os que sobram não têm
  tradução estabelecida no meio, ou vêm dos objetivos do TCC I.
- **Conectivos** subiram de 0 para 0,6; a mediana é 2,7. Acrescentei só onde
  a relação entre as frases estava implícita, para não encher o texto.

Também mudaram duas coisas fora da lista: a 2.2 ganhou a precisão sobre o
Grinsztajn et al. (porte médio é cerca de 10 mil exemplos) e
`verifica_tcc.py` passou a aceitar a data por extenso na frase-síntese do
teste (ii).

## Plano de correção (um passo por vez, cada um medido e salvo)

O documento está em 29 páginas, com uma linha de folga. Cada passo é
reescrita de mesmo tamanho ou menor.

| Passo | O quê | Ocorrências | Efeito esperado em páginas |
|---|---|---|---|
| 1 | Citações: ponto e vírgula entre autores dentro de parênteses e ano nas três da 3.6 | ~10 | neutro |
| 2 | Registro: "num/numa" → "em um/em uma"; "só" → "apenas/somente" | 19 | neutro |
| 3 | Datas ISO e código no corpo: datas viram mês e ano ou saem; o comando vai para o Apêndice C; identificadores viram descrição | 9 | reduz |
| 4 | ", e não X": manter as que marcam delimitação real, reescrever o resto como afirmação direta | 15 | neutro ou reduz |
| 5 | Ponto e vírgula entre orações completas → ponto final | ~25 | neutro |
| 6 | Parênteses: tirar remissões redundantes e números que já estão no quadro ao lado | ~30 dos 187 | reduz |
| 7 | Inglês traduzível (*features*, *dataset*, *benchmark*, *pipeline*, *folds*) e alternância de *machine learning* | ~15 | neutro |
| 8 | Conectivos: pôr um onde a relação de causa ou consequência não está explícita | poucos | aumenta pouco; compensado pelos passos 3 e 6 |

Depois de cada passo: `verifica_tcc.py`, regerar o .docx, medir páginas,
`confere_docx.py`, registrar no diário e salvar.
