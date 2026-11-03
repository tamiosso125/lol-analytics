# TCC II — Texto do trabalho

> **Este arquivo é a fonte do entregável.** O documento formatado é gerado a
> partir dele por `docs/build_tcc_docx.py` + `docs/finalize-fields.ps1`, na
> ordem das seções de primeiro nível (capa → folha de rosto → Resumo/Abstract
> → 1 Introdução → 2 Fundamentação Teórica → 3 Trabalhos Relacionados →
> 4 Metodologia → 5 Resultados e Análise → 6 Conclusão → Referências →
> Apêndices/Anexos).
> **Não edite o `.docx` diretamente** — edite aqui e regere, senão texto e
> entregável divergem.
>
> **Decisões de escopo já tomadas:**
> - **Título acadêmico não cita Bellestraiko.** Decidido em 2026-10-03;
>   mantido igual ao TCC I, por ser o mesmo trabalho. O nome do produto
>   aparece no corpo do texto, na Seção 1.1.
> - **A estrutura do corpo segue os TCC II aprovados da UNISINOS**
>   (decidido em 2026-10-04; **inverte** o registro de 2026-10-03). Evidência
>   medida por `pypdf` nos 10 PDFs de aprovados da pasta "TCC II - EXEMPLOS E
>   MATERIAIS" da UNISINOS: 10 de 10 têm INTRODUÇÃO na posição 1; 10 de 10 têm
>   seção de fundamentação na posição 2 (9 intituladas FUNDAMENTAÇÃO TEÓRICA e
>   1 REFERENCIAL TEÓRICO); **10 de 10 têm TRABALHOS RELACIONADOS como seção
>   de primeiro nível, na posição 3**; 10 de 10 têm METODOLOGIA na posição 4;
>   **10 de 10 fundem a discussão nos resultados** (RESULTADOS E ANÁLISE) na
>   posição 5; e CONCLUSÃO/CONSIDERAÇÕES FINAIS na posição 6. A decisão
>   anterior ("não é seção de primeiro nível") atendia ao modelo institucional
>   genérico de 2026-09-28 — template em branco, sem exemplar de banca. Um
>   template em branco não diz o que a banca efetivamente aprova; prevaileceram
>   os dez aprovados. A Seção 3 existe, a referência conceitual fica na
>   Seção 2 e a confrontação com os resultados obtidos fica na Seção 5.7.
> - ~~Resumo/Abstract~~ — escrito.

---

## RESUMO

O crescimento dos esports amplia a geração de dados sobre partidas,
jogadores e estratégias, mas sua exploração ainda depende de ferramentas
fragmentadas e de conhecimento técnico. Este trabalho desenvolveu uma
plataforma inteligente para análise de dados de *League of Legends* que
integra coleta, modelagem preditiva com *machine learning*,
explicabilidade, visualização e consulta em linguagem natural. Trata-se
de pesquisa aplicada, de abordagem mista, sobre 41.063 partidas
ranqueadas de elo alto em cinco regiões, coletadas via Riot Games API, e
96.716 jogos profissionais de 2014 a 2026 (Oracle's Elixir). Três
modelos (XGBoost, *Random Forest* e uma rede neural MLP) foram comparados
por validação cruzada estratificada para predizer o vencedor em quatro
cortes temporais, de 10 a 25 minutos; os três ficaram próximos, e o
XGBoost, adotado em produção, alcançou acurácia de 0,7621 e AUC-ROC de
0,8473 no corte de 15 minutos. A análise exploratória identificou viés de
lado favorável ao time vermelho no *solo queue* de elo alto (56,3% de
vitórias na região com maior amostra), estável ao longo da partida e
invertido no cenário profissional, em que o azul vence 53,2% dos jogos,
achado sustentado por testes de robustez. Uma interface *text-to-SQL* com
validação estrutural atingiu 88% de acurácia de execução em um benchmark de
26 perguntas, e a plataforma reúne seis páginas de visualização com
predição explicável (SHAP). Os resultados mostram a viabilidade de
integrar essas etapas em uma única solução aplicada a esports.

**Palavras-chave:** esports; *League of Legends*; análise de dados;
*machine learning*; interface em linguagem natural.

**Abstract:** The growth of esports increases the data generated about
matches, players and strategies, but exploring these data still depends
on fragmented tools and technical expertise. This work developed an
intelligent platform for *League of Legends* data analysis that
integrates data collection, predictive modeling with machine learning,
explainability, visualization and natural language querying. It is
applied research with a mixed-methods approach, based on 41,063 high-elo
ranked matches from five regions, collected through the Riot Games API,
and 96,716 professional games from 2014 to 2026 (Oracle's Elixir). Three
models (XGBoost, Random Forest and an MLP neural network) were compared
through stratified cross-validation to predict the winning team at four
time cutoffs, from 10 to 25 minutes; the three performed similarly, and
XGBoost, adopted in production, reached an accuracy of 0.7621 and an
AUC-ROC of 0.8473 at the 15-minute cutoff. The exploratory analysis
identified a side bias favoring the red side in high-elo solo queue
(56.3% win rate in the region with the largest sample), stable
throughout the match and reversed in the professional scenario, where
the blue side wins 53.2% of games, a finding supported by robustness
tests. A text-to-SQL interface with structural validation achieved 88%
execution accuracy on a 26-question benchmark, and the platform comprises
six visualization pages with explainable predictions (SHAP). The results
show the feasibility of integrating these stages into a single solution
applied to esports.

**Key-words:** esports; League of Legends; data analysis; machine
learning; natural language interface.

---

## 1 INTRODUÇÃO

Os esports vêm se consolidando como um campo de crescente relevância
acadêmica e tecnológica, em função do grande volume de dados gerados por
partidas, jogadores, equipes e estratégias competitivas. Em *League of
Legends*, Birant e Birant (2023) destacam que esses dados podem ser
explorados por modelos de aprendizado de máquina (*machine learning*) voltados à análise
competitiva e à predição de resultados. Além do potencial preditivo, a
análise desses dados pode apoiar a interpretação do jogo, a identificação
de padrões e a avaliação de desempenho.

A exploração dessas informações, porém, ainda costuma depender de
processos fragmentados e de ferramentas que exigem conhecimento técnico
específico. García-Méndez e Arriba-Pérez (2025) indicam que não basta
gerar previsões: é preciso apresentá-las de forma interpretável ao
usuário final. E Jiang et al. (2025) mostram que modelos de linguagem
podem apoiar a exploração de dados estruturados em soluções de *Business
Intelligence*, reduzindo a barreira técnica entre o usuário e a base de
dados.

Neste contexto, o presente trabalho teve como objetivo geral desenvolver
uma plataforma inteligente para análise de dados de esports, com foco em
*League of Legends*, que integra coleta, organização e exploração de
dados competitivos, modelagem preditiva com técnicas de *machine learning*
e mecanismos de visualização e consulta em linguagem natural. Além do
escopo previsto no TCC I, a base foi complementada com dados
profissionais (Oracle's Elixir, 96.716 jogos de 2014 a 2026), o que
permitiu comparar os padrões do *solo queue* com os do cenário
competitivo profissional.

Este trabalho está organizado em cinco seções, além desta introdução. A
Seção 2 apresenta a fundamentação teórica; a Seção 3, os trabalhos
relacionados; a Seção 4, a metodologia; a Seção 5, os resultados e sua
análise à luz da literatura; e a Seção 6, as conclusões, as limitações e
os trabalhos futuros.

### 1.1 TEMA

O tema deste trabalho é a análise de dados aplicada a esports, com foco
no desenvolvimento de uma plataforma inteligente para exploração de
informações competitivas em *League of Legends*. A plataforma, batizada
**Bellestraiko**, é o sistema desenvolvido e implementado ao longo do
trabalho, que se insere na área da Ciência da Computação e envolve
ciência de dados, inteligência artificial, aprendizado de máquina e sistemas
de informação.

### 1.2 DELIMITAÇÃO DO TEMA

O trabalho delimitou-se a *League of Legends*, com dados da Riot Games
API complementados por dados profissionais do Oracle's Elixir, sobre
partidas, jogadores e estatísticas de desempenho. No campo analítico, o
recorte é a comparação entre XGBoost, *Random Forest* e redes neurais em
análises preditivas restritas ao estado do jogo até o momento da
predição, sem informação posterior ao corte temporal. A proposta inclui
*dashboards* e uma interface em linguagem natural para consulta e
interpretação dos dados. Não abrange outros jogos nem todas as abordagens
possíveis de inteligência artificial, mas um recorte específico e viável,
alinhado aos objetivos definidos no TCC I.

### 1.3 PROBLEMA

Diante da grande quantidade de dados competitivos disponíveis em
*League of Legends* e da dificuldade de explorá-los de forma
integrada, acessível e analiticamente útil, este trabalho buscou
responder à seguinte questão de pesquisa:

Como desenvolver uma plataforma inteligente para análise de dados de
*League of Legends* que integre coleta, organização, modelagem
preditiva, visualização e consulta em linguagem natural para apoiar a
interpretação de informações competitivas?

### 1.4 OBJETIVOS

#### 1.4.1 Objetivo geral

Desenvolver uma plataforma inteligente para análise de dados de
esports, com foco em *League of Legends*, integrando coleta,
organização e exploração de dados competitivos, modelagem preditiva
com técnicas de *machine learning* e mecanismos de visualização e
consulta em linguagem natural para apoiar a interpretação das
informações.

#### 1.4.2 Objetivos específicos

Para alcançar o objetivo geral proposto, foram definidos os seguintes
objetivos específicos, todos alcançados conforme apresentado na
Seção 5:

a) mapear os dados e os recursos disponibilizados pela Riot Games API
relevantes para a análise competitiva em *League of Legends*;

b) identificar quais informações relacionadas a partidas, jogadores e
estatísticas podem ser organizadas em uma base estruturada para apoio
à análise de dados;

c) estruturar um processo de coleta, tratamento e organização dos
dados obtidos, de modo a viabilizar sua exploração analítica;

d) avaliar o uso de técnicas de análise de dados para identificação de
padrões e apoio à interpretação de informações competitivas;

e) comparar o desempenho de modelos de *machine learning*, com foco em
XGBoost, *Random Forest* e redes neurais, no contexto dos dados
analisados;

f) propor dashboards para visualização das informações e dos
resultados analíticos produzidos pela plataforma;

g) propor uma interface em linguagem natural para facilitar a consulta
aos dados e a geração de descobertas no contexto competitivo estudado.

### 1.5 JUSTIFICATIVA

O trabalho se justifica academicamente por articular áreas centrais da
Ciência da Computação, como análise de dados, inteligência artificial,
aprendizado de máquina, sistemas de informação e interação humano-computador,
sobre um campo de produção de dados em crescimento. Do ponto de vista
prático, reunir coleta, tratamento, modelagem e consulta em linguagem
natural em uma mesma plataforma reduz a dependência de processos
fragmentados e de ferramentas que exigem conhecimento técnico elevado, e
oferece uma contribuição aplicável à interpretação de desempenho, ao
acompanhamento de tendências competitivas e à análise de partidas.

---

## 2 FUNDAMENTAÇÃO TEÓRICA

Esta seção define os conceitos usados no restante do trabalho: análise de
dados em esports, as famílias de modelos preditivos comparadas,
explicabilidade e avaliação de modelos, interfaces em linguagem natural e
visualização analítica. As obras originais dos métodos aplicados são
citadas pela propriedade técnica que justifica o uso. Os estudos do
domínio são descritos autor a autor na Seção 3 e confrontados com os
resultados na Seção 5.7.

### 2.1 ESPORTS E ANÁLISE DE DADOS

Jogos competitivos geram grande volume de dados sobre partidas,
jogadores, equipes e eventos em tempo real, o que faz dos esports um
campo relevante para a análise de dados. Hodge et al. (2021) mostram que
é possível prever o resultado de partidas profissionais de Dota 2
enquanto elas acontecem, com modelos de aprendizado de máquina padrão e
engenharia de atributos. Em *League of Legends*, Birant e Birant (2023)
destacam a modelagem centrada no time, e Bahrololloomi et al. (2022), a
relação entre métricas de jogadores, funções em jogo (*roles*) e
resultado da partida.

### 2.2 FAMÍLIAS DE MODELOS PREDITIVOS E SUA APLICAÇÃO EM ESPORTS

Esses estudos delimitam o espaço de escolha da modelagem, mas não decidem
qual família de modelos é adequada a este problema. O trabalho comparou
três por medição.

A primeira são os *ensembles* de árvores de decisão, em particular a
*Random Forest* (Breiman, 2001), que combina *bagging*, em que cada árvore
treina sobre uma amostra *bootstrap*, com a seleção aleatória de
variáveis em cada nó. Isso faz as árvores divergirem entre si e reduz a
variância do conjunto, o que importa quando as variáveis preditoras são
correlacionadas, como ouro, abates e torres, que evoluem juntos ao longo
da partida.

A segunda é o *gradient boosting*, representado pelo XGBoost (Chen; Guestrin, 2016), que constrói as árvores em sequência, cada uma ajustada
ao resíduo das anteriores, com otimização de segunda ordem e
regularização explícita. Em dados tabulares, como os deste trabalho, os
métodos baseados em árvores seguem competitivos frente a redes neurais em
amostras de porte médio, de cerca de 10 mil exemplos, com indício de que a
diferença diminui em amostras maiores (Grinsztajn; Oyallon; Varoquaux,
2022).

A terceira são as redes neurais *feedforward*, ou perceptrons multicamada
(MLP). Com capacidade de aproximação universal (Hornik; Stinchcombe; White, 1989), elas capturam interações sem que precisem ser
especificadas, mas exigem mais dados e mais cuidado com escala e
regularização, restrição relevante em uma amostra de dezenas de milhares de
partidas, longe de milhões.

### 2.3 EXPLICABILIDADE E AVALIAÇÃO DE MODELOS PREDITIVOS

García-Méndez e Arriba-Pérez (2025) mostram que a predição em esports pode
combinar classificação e interpretação, tornando os fatores da previsão
compreensíveis para o usuário final. Explicar um *ensemble*, porém, não é
trivial: a saída é a soma de centenas de árvores, e a contribuição de cada
variável não é diretamente legível. O LIME (Ribeiro; Singh; Guestrin, 2016) aproxima o modelo por um modelo linear local na vizinhança de cada
predição, simples de ler, mas dependente de como essa vizinhança é
definida. O SHAP
recorre ao valor de Shapley da teoria dos jogos: a importância de uma
variável é sua contribuição média para a previsão, sobre todas as
combinações das demais. Lundberg e Lee (2017) mostram que essa é a única
atribuição aditiva com propriedades desejáveis, como a consistência e a
importância nula para uma variável ausente, e o SHAP foi o método
adotado. Como as contribuições somam a previsão, a explicação exibida na
plataforma vem de valores calculados, sem recorrer a conhecimento
genérico sobre o jogo.

A avaliação exige também uma escolha de métrica. A acurácia depende de um
limiar e precisa ser lida contra a taxa-base: na amostra, o azul vence
46,6% das partidas, de modo que um classificador que sempre respondesse
"vitória do vermelho" acertaria 53,4% sem poder preditivo algum. Por isso
a avaliação se apoia também na área sob a curva ROC (AUC-ROC), que mede a
discriminação do modelo em todos os limiares. Hanley e McNeil (1982)
mostram que ela equivale à probabilidade de um caso positivo receber
pontuação maior que um negativo. As duas métricas são reportadas juntas
na Seção 5.

### 2.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

Interfaces em linguagem natural reduzem a barreira técnica entre o
usuário e os dados. Jiang et al. (2025) observam que soluções de
*Business Intelligence* apoiadas por modelos de linguagem, com diálogo em
várias rodadas, favorecem a exploração de dados estruturados, e Guo et al.
(2024), que a decomposição de perguntas e a análise visual tornam essa
exploração mais intuitiva. O problema técnico central é a geração da consulta: o modelo
produz texto, e o banco exige SQL válido e correto sobre um esquema
específico. Uma consulta gramaticalmente correta pode citar uma tabela
inexistente ou responder à pergunta errada. Wang et al. (2020) tratam
este segundo caso e mostram que representar o esquema com os
relacionamentos entre tabelas, além dos nomes das colunas, melhora
a precisão da conversão. Neste trabalho, a correção da consulta não é
delegada ao modelo: ela é validada antes de tocar o banco.

### 2.5 VISUALIZAÇÃO ANALÍTICA E DADOS ESPAÇO-TEMPORAIS EM ESPORTS

A análise de esports também precisa representar informações que evoluem
no espaço e no tempo, como movimentação, posicionamento e interação entre
jogadores. Wallner, Wang e Dormann (2023) mostram que visualizações
espaço-temporais, sobretudo as que integram tempo e localização em uma
única representação, ajudam a interpretar o comportamento em jogo na
revisão pós-partida. Esse referencial motivou o mapa de calor de
posicionamento da análise de partida.

---

## 3 TRABALHOS RELACIONADOS

Esta seção descreve os onze estudos de domínio que sustentam a pesquisa,
com o objeto, a abordagem e a contribuição de cada um para o problema
aqui tratado. As obras de método (Breiman, 2001; Chen; Guestrin, 2016; Hanley; McNeil, 1982; Lundberg; Lee, 2017; Ribeiro; Singh; Guestrin, 2016; Wang et al., 2020) estão na Seção 2, no ponto em que o método que
elas fundamentam é introduzido.

### 3.1 ESPORTS COMO FENÔMENO DE PRODUÇÃO E ANÁLISE DE DADOS

Hodge et al. (2021) tratam da predição de vitória em partidas
profissionais de Dota 2, em tempo real. Com modelos de aprendizado de máquina
padrão, engenharia de atributos e otimização, chegam a até 85% de
acurácia após 5 minutos de jogo, em previsões ao vivo de 28 partidas de um
torneio, o que estabelece a predição de
resultados em esports como problema tratável por modelagem estatística.
Por tratar de outro jogo, o estudo sustenta a abordagem de prever a
partir do estado da partida, mas não o recorte de *League of Legends*.

### 3.2 MACHINE LEARNING APLICADO A LEAGUE OF LEGENDS E ESPORTS

Birant e Birant (2023) apresentam uma abordagem de aprendizado
multi-objetivo e multi-instância (*Multi-Objective Multi-Instance
Learning*) aplicada a esports e destacam a modelagem centrada no time, em vez do jogador isolado. É a abordagem adotada aqui, com as variáveis
preditoras construídas como diferenças agregadas entre os dois times.
Bahrololloomi et al. (2022) percorrem o caminho oposto: predizem a
vitória a partir das funções (*roles*) e das métricas individuais dos
jogadores. Este trabalho usa esse nível de agregação apenas nos perfis de
jogador.

Outros estudos preveem partidas de *League of Legends* com insumos
diferentes. Jadowski e Cunningham (2022) ajustam classificadores
estatísticos a métricas das ligas profissionais de 2020 e acertam 67% dos
306 jogos da etapa seguinte. Do et al. (2021) preveem partidas ranqueadas
antes de elas começarem, a partir da experiência de cada jogador com o
campeão escolhido, e chegam a 75,1% de acurácia com uma rede neural
profunda. Maymin (2021) calibra um modelo de probabilidade de vitória com
dados de milhões de partidas ranqueadas e avalia cada ação individual pelo
efeito que tem nessa probabilidade. Guan e Tung (2026), em um *preprint*
ainda sem revisão por pares, fazem previsão pré-jogo no cenário
profissional e tratam o lado do mapa e a prioridade de escolha como
covariáveis do modelo.

### 3.3 EXPLICABILIDADE E ANÁLISE PREDITIVA

García-Méndez e Arriba-Pérez (2025) combinam classificação por *machine
learning* com mecanismos de interpretação na predição de vitória em
partidas profissionais de *Counter-Strike*, em fluxo contínuo (*streaming*).
Eles apontam a falta de interpretabilidade como uma das principais
limitações dos trabalhos anteriores, o que orienta a camada de
explicabilidade da plataforma.

### 3.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

Jiang et al. (2025) apresentam o SiriusBI, solução de *Business
Intelligence* apoiada por modelos de linguagem para análise de dados em
contextos corporativos, e Guo et al. (2024), o Talk2Data, interface em
linguagem natural para análise visual exploratória baseada em
decomposição de perguntas. Os dois usam modelos de linguagem como camada
de interação sobre dados estruturados e fundamentam o *text-to-SQL* deste
trabalho, que leva a abordagem ao domínio de *League of
Legends*.

### 3.5 VISUALIZAÇÃO ANALÍTICA E DADOS ESPAÇO-TEMPORAIS EM ESPORTS

Wallner, Wang e Dormann (2023) estudam a evolução espaço-temporal do
gameplay em *League of Legends* com a técnica de *storyline
visualization* e mostram o valor de integrar tempo e localização em uma
única representação para a interpretação pós-jogo. O estudo é a
referência do posicionamento minuto a minuto da análise de partida.

### 3.6 SÍNTESE E POSIÇÃO DESTE TRABALHO

Os estudos cobrem frentes isoladas: predição de resultados, interpretabilidade da predição (García-Méndez; Arriba-Pérez, 2025),
interação em linguagem natural (Jiang et al., 2025; Guo et al., 2024) e visualização
espaço-temporal (Wallner; Wang; Dormann, 2023). No entanto, nenhum é entregue como uma
plataforma que reúna coleta, tratamento, modelagem, explicabilidade,
visualização e consulta em linguagem natural sobre a mesma base, e é
essa lacuna de integração que este trabalho ocupa. A distinção também
está em três decisões de projeto.

**Horizonte da predição.** Em vez de um único momento, a predição é feita
em quatro cortes de tempo, com um modelo por corte, o que torna o
desempenho comparável ao longo da partida e mostra como a importância das
variáveis muda de fase para fase.

**Recorte de população.** A maior parte dos estudos de predição atua
sobre o cenário profissional, e os que usam partidas ranqueadas (Do et
al., 2021; Maymin, 2021) não as comparam com ele. Este trabalho mede o
mesmo indicador nos dois contextos e mostra que o viés de lado do *solo
queue* de elo alto se inverte no circuito profissional.

**Consulta mensurável.** A interface em linguagem natural foi avaliada no
próprio domínio, com 26 perguntas fixas e resposta esperada conferida
contra o banco, o que permite medir o erro de conversão, sem se limitar
a exemplos ilustrativos.

---

## 4 METODOLOGIA

Esta seção descreve como a pesquisa e a plataforma foram desenvolvidas: a
natureza do estudo, a coleta e o tratamento dos dados, a modelagem
preditiva e os recursos de visualização e consulta.

### 4.1 NATUREZA E ABORDAGEM DA PESQUISA

Quanto à natureza, trata-se de pesquisa aplicada, que busca conhecimento
voltado à solução de um problema específico e de uso prático (Prodanov; Freitas, 2013): aqui, uma plataforma para coletar, organizar e analisar
dados competitivos de *League of Legends*. Quanto aos objetivos, a
pesquisa é exploratória, na investigação da Riot Games API e das
possibilidades de modelagem, e descritiva, na caracterização dos dados,
dos padrões e dos modelos comparados (Gil, 2002). A abordagem é mista
(Creswell; Creswell, 2023): qualitativa na revisão bibliográfica e na
interpretação dos achados, quantitativa na coleta, na análise
exploratória e na comparação entre os modelos de aprendizado de máquina.

### 4.2 ESTRATÉGIAS DE PESQUISA

O trabalho foi desenvolvido por meio de pesquisa bibliográfica (Gil,
2002), pesquisa documental sobre a documentação oficial da Riot Games API
(Prodanov; Freitas, 2013) e estudo aplicado com recorte de caso no domínio
de *League of Legends* (Yin, 2018).

### 4.3 COLETA DE DADOS

A coleta usou duas fontes. A segunda foi incorporada durante o TCC II,
além do escopo previsto no TCC I.

**a) Riot Games API (*solo queue*).** O endpoint *league-v4* identificou
os jogadores dos elos Desafiante e Grão-Mestre, recorte de escopo: uma
população fechada, que a API lista por inteiro e que cabe no limite de
requisições da chave de desenvolvedor. O *account-v1* resolveu o Riot ID,
e o *match-v5* e o *timeline-v5* trouxeram cada partida e sua linha do
tempo minuto a minuto. A coleta cobriu cinco regiões (BR1, EUW1, KR, NA1 e
EUN1, esta com amostra insuficiente e fora da leitura) na fila 420
(ranqueada solo/duo), em um total de **41.063 partidas**. Como a chave de desenvolvedor
expira a cada 24 horas, o coletor retoma de onde parou e pula as partidas
já salvas.

**b) Oracle's Elixir (cenário profissional).** Foram incorporados
**96.716 jogos profissionais** de 2014 a 2026, das principais ligas (LCK,
LPL, LEC, LTA, CBLOL, entre outras), a partir dos arquivos CSV anuais que
o site publica (Oracle's Elixir, [s.d.]), para comparar o *solo queue* de
elo alto com o cenário profissional.

Os dados são secundários e públicos, sem participação de sujeitos humanos
como fonte em nenhuma etapa.

### 4.4 ORGANIZAÇÃO E TRATAMENTO DE DADOS

Os dados foram organizados em um banco relacional PostgreSQL, descrito no
Quadro 1. O tratamento incluiu a normalização da partida
bruta de cada fonte, a extração das compras e vendas de itens a partir da
linha do tempo, com os desfazimentos de compra aplicados, e a
reconciliação dos nomes de campeão entre a Riot API e o Oracle's Elixir,
que usam convenções diferentes. O catálogo de itens, derivado do Data
Dragon da Riot, permite resolver nome e ícone de item por consulta ao
banco, sem depender da memória de um modelo de linguagem.

### 4.5 ANÁLISE EXPLORATÓRIA DE DADOS

A análise exploratória investigou distribuições e relações entre
variáveis, com atenção à taxa de vitória por lado do mapa em três
recortes: região, fase da partida e contexto (*solo queue* ou
profissional). Nenhum padrão foi aceito como resultado sem passar por
quatro testes de robustez: (i) replicação restrita a uma região, contra
o efeito de mistura regional; (ii) comparação por duração total da
partida, contra a confusão com "jogos longos"; (iii) intervalo de
confiança de Wilson sobre a proporção (Brown; Cai; DasGupta, 2001), para
a significância em amostras menores; e (iv) comparação de pares com
correção de Holm (Holm, 1979), que corrige a multiplicidade quando várias
diferenças são testadas na mesma base. O teste (iv) foi decisivo para o
viés de lado: sem ele, a dispersão entre cortes seria lida como tendência.

### 4.6 MODELAGEM PREDITIVA E COMPARAÇÃO ENTRE MODELOS

Foram comparados três classificadores binários da vitória do time azul:
XGBoost, *Random Forest* e uma rede neural do tipo perceptron multicamadas
(MLP). As variáveis preditoras são as diferenças, azul menos vermelho, de
ouro, experiência, abates, torres e dragões acumuladas até o corte
temporal. Há um modelo independente para cada corte (10, 15, 20 e 25
minutos), e nenhuma informação posterior ao corte entra como variável, o
que evita o vazamento de dados descrito por Kaufman et al. (2012). A
validação foi cruzada e estratificada, com 5 dobras (Kohavi, 1995), e
mediu acurácia, precisão, *recall*, F1 e AUC-ROC. Depois de um modelo de
referência, os hiperparâmetros foram ajustados por *GridSearchCV*, do
scikit-learn (Pedregosa et al., 2011), otimizando a AUC-ROC. O modelo de
produção recebeu curva de calibração e explicações SHAP, globais e por
predição. Onze experimentos de enriquecimento testaram se outros sinais,
dez da linha do tempo e um de um endpoint de progressão do jogador,
melhoravam a previsão.

### 4.7 PROPOSTA DE VISUALIZAÇÃO E INTERFACE EM LINGUAGEM NATURAL

A camada de apresentação é uma aplicação web em React com TypeScript, que
consome uma API própria em FastAPI, com seis páginas: Início (busca),
Dashboard (indicadores agregados), Campeões, Partidas (análise minuto a
minuto, mapa de calor, leitura de *draft* e modo "e se"), Competitivo
(*solo queue* × profissional) e Simulador (composição, estado de jogo e
SHAP). A Seção 5 mostra, recortada, a parte de cada tela que discute. As seis telas completas estão no Apêndice F (Figuras 6 a 11).

A interface em linguagem natural é um fluxo *text-to-SQL*: um modelo
de linguagem (Claude) traduz a pergunta em SQL, a consulta é validada
antes de executar (apenas `SELECT` ou `WITH...SELECT`, sobre uma lista fechada
de tabelas) e a resposta vem sempre do banco, nunca do conhecimento
genérico do modelo. A acurácia foi medida em um *benchmark* de 26 perguntas
de referência com SQL esperado, sobre o *solo queue* e o competitivo. A
métrica é a acurácia de execução, que compara o resultado da consulta
gerada com o da consulta de referência. Zhong, Yu e Klein (2020) discutem
seus limites e propõem avaliar a mesma consulta sobre vários bancos de
teste, o que este *benchmark*, feito sobre uma única base, não faz.

O módulo de orientação estratégica (*coach*) traduz a probabilidade e as
contribuições SHAP de um estado de jogo em recomendações em linguagem
natural, geradas por um modelo de linguagem (Claude). Cada resposta separa
o que vem dos dados (confrontos de rota, sinergias entre campeões e itens
calculados sobre o histórico de partidas) do que é conhecimento geral do
modelo sobre o jogo, marcado como tal, sem verificação pelos dados da
partida. O modelo preditivo não vê itens, posição nem o estado das ondas de *minions*. Qualquer orientação que dependa disso é inferência (Seção
6.1). Além disso, antes da partida, o módulo também lê a composição dos dois times e
aponta a condição de vitória de cada um, sem usar a predição.

### 4.8 MATERIAIS E MÉTODOS UTILIZADOS

Foram utilizados Python (coleta, ETL e modelagem, com *pandas*, *NumPy*,
*scikit-learn*, *XGBoost* e *SHAP*), PostgreSQL, FastAPI e React com
TypeScript e Recharts. A interface em linguagem natural e o módulo de
orientação estratégica (*coach*) usam a API da Anthropic (modelo Claude).
Testes automatizados cobrem o *backend* (testes de fumaça e uma bateria de
validação comportamental do modelo de produção) e o *frontend* (Vitest).
O desenvolvimento e a execução foram feitos localmente, em Windows.

---

## 5 RESULTADOS E ANÁLISE

Esta seção apresenta os resultados obtidos, organizados de acordo com
os objetivos específicos definidos na Seção 1.4.2.

### 5.1 Mapeamento de dados e recursos da Riot Games API (objetivo a)

Foram mapeados e utilizados os endpoints *league-v4*, *account-v1*,
*match-v5* e *timeline-v5* da Riot Games API (Anexo A), além da documentação
técnica necessária para compreender limitações de taxa de requisição e
o ciclo de expiração da chave de desenvolvedor (24 horas). Esse
mapeamento orientou o desenho de um coletor resumível, capaz de operar
dentro dos limites de taxa e de retomar a coleta entre sessões sem
duplicar dados já salvos.

### 5.2 Estruturação da base de dados (objetivos b e c)

A base usada para treinar e comparar os modelos preditivos
reúne **39.188 partidas** de *solo queue* no corte de 15 minutos,
provenientes das **39.426 partidas** que o banco tinha quando o
conjunto de variáveis foi congelado, com JSON
bruto de partida e linha do tempo preservados para reprocessamento, e
**96.716 jogos profissionais**
(2014-2026, Oracle's Elixir). O Quadro 1 resume as tabelas do banco. Os campos e as chaves de cada uma estão no Apêndice A.

Quadro — Tabelas do banco de dados e o que cada uma guarda

| Tabela | Conteúdo |
|---|---|
| `players` | jogadores Desafiante e Grão-Mestre obtidos pela *league-v4* |
| `raw_matches`, `raw_timelines` | JSON bruto da partida e da linha do tempo, para reprocessar sem nova coleta |
| `matches` | uma linha por partida: região, fila, versão do jogo e duração |
| `teams` | resultado e objetivos de cada time na partida |
| `participants` | desempenho de cada jogador na partida |
| `bans` | campeões banidos por time |
| `item_events`, `items` | compras e vendas de itens, já com desfazimentos aplicados, e o catálogo de itens |
| `pro_games`, `pro_players` | jogos e jogadores profissionais (Oracle's Elixir) |

A coleta seguiu de forma incremental e o volume cresceu ao longo do
trabalho: 10.295 partidas na primeira base ampla, 23.133 no retreino de
julho de 2026, 39.426 em 4 de outubro e 41.063 ao fim desse dia, com a região NA1 passando de 1.446
para 7.159 partidas na rodada final. Era a menor das quatro regiões com
amostra relevante, e a que mais limitava a generalização do achado de
viés de lado.

### 5.3 Análise exploratória: padrões identificados (objetivo d)

**Viés de lado no *solo queue* de elo alto.** No agregado das cinco
regiões, o time vermelho venceu mais que o azul, com intensidade variável
por região. O Quadro 2 traz a medição direta em SQL, de 4 de outubro de 2026, sobre
as 41.063 partidas. O histórico das medições está no Apêndice E.

Quadro — Vitória do time vermelho por região

| Região | Partidas | Vitória do vermelho |
|---|---:|---:|
| BR1 | 11.936 | 56,3% |
| EUW1 | 11.744 | 53,4% |
| KR | 10.204 | 50,4% |
| NA1 | 7.159 | 52,2% |
| EUN1 | 20 | 50,0% (amostra insuficiente, não considerada) |

A direção é a mesma nas quatro regiões com amostra relevante, mas a força
da evidência não é uniforme. Em BR1, EUW1 e NA1 o intervalo de confiança
de 95% exclui 50%; na KR, com 50,4% e intervalo [49,5%, 51,4%], o
intervalo inclui 50%, e o viés não é distinguível de zero. A BR1 sustenta
a assimetria com folga ([55,4%, 57,2%]). O padrão se estende ao elo alto em
geral, além do Brasil, mas as quatro regiões não o demonstram com a mesma força.

(Nota sobre as bases usadas nesta seção e na modelagem: a análise
descritiva foi medida sobre as **41.063 partidas** que o banco tem ao fim
da coleta. As variáveis e os modelos foram construídos antes da última
rodada da KR, sobre a base anterior de **39.426 partidas**, das quais
39.309 geraram variáveis preditoras e 39.188 chegam ao corte de 15 minutos. Por isso a Seção 5.4 e o Apêndice C citam 39.426. As 1.637 partidas de diferença,
quase todas da KR, são uma limitação declarada na Seção 6.1.)

**O viés é estável ao longo da partida.** Uma versão anterior deste texto
afirmava que ele atingia um pico no meio do jogo. A base ampliada não
confirma essa forma. Entre as partidas empatadas em cada corte (diferença
de ouro menor que 500), o azul venceu 46,4% aos 10 minutos (n = 7.349),
47,9% aos 15 (n = 3.970), 46,7% aos 20 (n = 2.423) e 47,1% aos 25
(n = 1.430). Nenhuma diferença entre pares sobrevive à correção de Holm
para comparações múltiplas (o menor valor-p corrigido é 0,83), e o
intervalo do corte de 10 minutos, o de maior amostra, [45,3%, 47,6%],
exclui 50% com folga. O viés existe e tem magnitude praticamente constante. O que a amostra maior desfez foi a *evolução* atribuída a ele.
A lição vale para o trabalho todo: em corpus de esports, um ponto
percentual de diferença em subamostras de mil partidas não é diferença.

Os quatro testes de robustez da Seção 4.5 se aplicam aqui. O teste (i),
restrito à BR1, reproduz a assimetria e descarta mistura regional. O
teste (ii) mostra a taxa de vitória do **azul** estável por faixa de
duração total da partida
(medido em 4 de outubro de 2026 sobre as 41.063 partidas: 45,6% a 47,3% entre
as faixas de duração, amplitude de 1,7 ponto percentual, todas abaixo
de 50%), o que
descarta que partidas longas sejam outro tipo de jogo. O teste (iii), o
intervalo de Wilson, está aplicado acima, e o teste (iv), a comparação de
pares com correção de Holm, é o que sustenta a constância.

**Comparação com o cenário profissional.** Nos dados competitivos
(Oracle's Elixir, 96.716 jogos), o time azul venceu 53,2% das partidas,
com série anual estável desde 2016 (entre 52,5% e 55,0%). O viés vai na direção oposta à do *solo queue* de
elo alto: a mesma métrica, em dois contextos institucionalmente
diferentes, produz sinais opostos. Hipótese de explicação: no *solo
queue*, sem coordenação de *draft*, o *counter-pick* garantido do time
vermelho (que escolhe por último) pesa mais; no jogo profissional, a
prioridade de primeira escolha é valorizada a ponto de influenciar a
escolha de lado em *playoffs*. O resultado é coerente com Jadowski e
Cunningham (2022), que observam 54,08% de vitórias do azul em 882 jogos
profissionais de 2020, e a prioridade de escolha entra como covariável
própria em Guan e Tung (2026), mas isso não comprova a hipótese.

**Conversão de vantagem.** Com vantagem de ouro entre +2.000 e +4.000 aos
15 minutos, o azul venceu 81,5% das partidas no profissional (n = 3.294)
contra 73,7% no *solo queue* (n = 5.166); entre +4.000 e +6.000, 91,7%
(n = 72) contra 86,3% (n = 3.343). Ou seja, a mesma vantagem material vale mais
nas mãos de um time coordenado. A diferença na faixa com amostra
suficiente, de 7,8 pontos percentuais, é pequena em termos absolutos, mas
significativa (z = 8,3, p < 0,001). A faixa de +4.000 a +6.000 do
profissional, com 72 jogos, é apenas indicativa. A origem das taxas está no
Apêndice E. A Figura 1 mostra as duas comparações na tela Competitivo,
com o cenário profissional restrito a 2026. Por isso o azul aparece com
53,1%, diferente dos 53,2% do acervo completo.

Figura — Tela Competitivo: viés de lado e conversão de vantagem de ouro, solo queue × profissional de 2026 | reports/figuras_texto/fig_competitivo.png

### 5.4 Modelagem preditiva e comparação entre modelos (objetivo e)

O Quadro 3 compara os três modelos no corte de 15 minutos (validação
cruzada estratificada de 5 dobras, semente 42), no conjunto final de
39.188 partidas, em que o azul vence 46,6%: o XGBoost com os
hiperparâmetros da busca em grade (*GridSearchCV*), os outros dois na
configuração de referência. O comando que reproduz a medição está no
Apêndice C.

Quadro — Comparação entre modelos (corte de 15 minutos)

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---:|---:|---:|
| **XGBoost (produção)** | **0,7621** | 0,7561 | 0,7228 | 0,7391 | **0,8473** |
| MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| *Random Forest* | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |

Os três modelos ficaram próximos. Com a mesma busca em grade, a *Random
Forest* e o MLP chegam a 0,7617 e 0,7619 de acurácia (AUC-ROC de 0,8468 e
0,8477), e o XGBoost mantém a maior acurácia. Ele foi adotado pela
estabilidade na faixa intermediária, já que não vence em todos os cortes:
aos 10 minutos o MLP o supera em acurácia (0,7020 contra 0,7004) e aos 25
chega a 0,002 do seu AUC (0,9072 contra 0,9090). Com um modelo treinado para cada
corte, com os mesmos hiperparâmetros e sobre a base de 39.426 partidas, o
desempenho cresce conforme a partida avança: AUC-ROC de 0,774 aos 10
minutos a 0,909 aos 25 (Quadro 4). As métricas dos três modelos nos
quatro cortes estão no Apêndice C.

Quadro — Desempenho do XGBoost por corte temporal

| Corte | Partidas | Acurácia | AUC-ROC |
|---|---:|---:|---:|
| 10 min | 39.309 | 0,7004 | 0,7742 |
| 15 min | 39.188 | 0,7621 | 0,8473 |
| 20 min | 34.337 | 0,7917 | 0,8762 |
| 25 min | 26.837 | 0,8241 | 0,9090 |

Na importância das variáveis (SHAP, média do valor absoluto), as
diferenças de ouro e de experiência dominam em todos os cortes. A
diferença de torres é quase irrelevante até os 20 minutos (0,0044 aos 10,
0,0060 aos 15 e 0,0031 aos 20) e salta para 0,0928 aos 25, cerca de 15
vezes o valor dos 15 minutos (Figura 2). É coerente com a mecânica do
jogo: as placas de defesa das torres caem por volta dos 14 minutos, e
antes disso destruir uma torre é raro e pouco informativo. É a
justificativa concreta para treinar um modelo *por fase* em vez de um
único modelo genérico. A calibração, preocupação conhecida em modelos de
*boosting* (Niculescu-Mizil; Caruana, 2005), não exigiu correção: a curva
de calibração mostrou o XGBoost já bem calibrado.

Figura — Importância média de cada variável (|SHAP|) nos quatro cortes temporais | reports/figuras_texto/fig_shap_fases.png

**Experimentos negativos.** Onze tentativas de enriquecer o conjunto de
variáveis não produziram ganho distinguível de ruído (Quadro 5). O único
caso de piora mensurável foi o tipo do dragão (AUC-ROC de 0,8319 para
0,8295). As notas sobre três delas estão no Apêndice D. Já
o aumento do *volume* de partidas produziu ganho real: o AUC-ROC do
XGBoost subiu de 0,8214 (10.295 partidas) para 0,8393 (23.133) e para
0,8473 (39.188). Com as variáveis de estado agregado que a API oferece, isso
é consistente com um desempenho limitado mais pelo volume de dados do que
pela engenharia de novas variáveis, embora três pontos não bastem para
afirmá-lo.

Quadro — Experimentos negativos de enriquecimento de *features*

| # | Experimento | Resultado |
|---|---|---|
| 1 | Diferença de abates de Barão/Arauto | Δ AUC ≈ ruído (±0,001-0,003) |
| 2 | Dispersão espacial do time | Δ AUC ≈ ruído |
| 3 | Tuning específico por fase | Δ AUC ≈ ruído |
| 4 | Calibração adicional (além da já obtida) | sem ganho (modelos já calibrados) |
| 5 | Ouro convertido em itens | Δ AUC ≈ ruído |
| 6 | Separação de features defensivas/ofensivas | Δ AUC ≈ ruído |
| 7 | Ouro em itens (`item_gold_diff`), em amostra maior | Δ AUC ≈ ruído |
| 8 | Visão (ward_diff / ward_kill_diff) | Δ AUC ≈ ruído |
| 9 | Dragões por tipo (`monsterSubType`) | **AUC piorou** (0,8319 → 0,8295), sobre a base de 23.133 partidas |
| 10 | Placas de torre (`plate_diff`, `TURRET_PLATE_DESTROYED`) | Δ AUC -0,0002 (cortes 10 e 15 min, base de 39.188-39.309) |
| 11 | Percentis comportamentais (`teamwork_pct_diff`/`expertise_pct_diff`, `lol-challenges-v1`) | Δ AUC -0,0031/+0,0007 (corte 15 min, n=2.987, piloto de n=199 sugeriu sinal que não se sustentou) |

### 5.5 Dashboards (objetivo f)

Foram entregues seis páginas de visualização: Início, Dashboard,
Campeões, Partidas, Competitivo e Simulador. O simulador separa a
estimativa por composição de time, uma heurística de taxa de vitória
histórica sinalizada como tal na interface, da predição feita pelo modelo
de produção a partir do estado de jogo.

A Figura 3 mostra a análise de uma partida individual: o mapa de calor de
posicionamento no minuto escolhido, a diferença de ouro ao longo da
partida e os objetivos de cada time até aquele minuto. A Figura 4 mostra
o simulador no estado de jogo: o usuário define as diferenças aos 15
minutos, o modelo de produção devolve a probabilidade de vitória do time
azul e o SHAP decompõe essa probabilidade por variável, na mesma tela. As
seis telas completas estão no Apêndice F.

Figura — Análise de partida: mapa de calor, diferença de ouro e objetivos até o minuto 14 | reports/figuras_texto/fig_partida.png

Figura — Simulador, aba Estado: probabilidade de vitória e contribuição de cada variável (SHAP) | reports/figuras_texto/fig_simulador_estado.png

### 5.6 Interface em linguagem natural (objetivo g)

O fluxo de consulta em linguagem natural (*text-to-SQL* com
validação estrutural antes da execução) atingiu **88% de acurácia de
execução**: 23 de 26 perguntas de referência, 22 sobre *solo queue* e 4
sobre os dados competitivos. O mesmo resultado saiu em três execuções
em datas diferentes; uma quarta, feita durante a coleta, deu 22 de 26 por
interferência da escrita no banco (Apêndice B). As três falhas pertencem à mesma família: todas
pedem um mínimo de jogos e erram na formatação ou em uma coluna a mais na
resposta, não na interpretação da pergunta. O Quadro 6 agrupa as 26
perguntas pelo tipo de consulta que exigem.

Quadro — Acurácia de execução por tipo de pergunta do benchmark

| Tipo de pergunta | Perguntas | Acertos |
|---|---|---:|
| Agregação simples (contagem ou média) | 1, 3, 4, 6, 7, 8, 11, 13, 14, 15, 18, 20 | 12 de 12 |
| Ranking ou agrupamento | 2, 9, 10, 16, 17, 19 | 6 de 6 |
| Ranking com mínimo de jogos | 5, 12, 22 | 0 de 3 |
| Junção com a tabela de jogadores | 21 | 1 de 1 |
| Dataset competitivo | 23, 24, 25, 26 | 4 de 4 |
| **Total** | **26** | **23 de 26 (88%)** |

A Figura 5 mostra uma consulta na plataforma: a pergunta 9 do benchmark,
a SQL gerada pelo modelo, já validada, e o resultado lido do banco.

Figura — Consulta em linguagem natural: pergunta, SQL gerada e resultado | reports/figuras_texto/fig_nlq.png

### 5.7 Os resultados frente à literatura

Hodge et al. (2021) chegam a 85% de acurácia após 5 minutos em partidas
profissionais de Dota 2, mas tratam apenas da previsão. Este trabalho leva a
predição por fases a *League of Legends* e a integra a explicabilidade,
visualização e consulta em uma mesma solução. Entre os estudos de *League of
Legends*, Jadowski e Cunningham (2022) reportam 67% de acerto em jogos
profissionais e Do et al. (2021), 75,1% antes de a partida começar, a
partir da experiência com o campeão. As acurácias deste trabalho, de 70,0%
a 82,4% conforme o corte, ficam na mesma ordem de grandeza, mas a
comparação é apenas indicativa: mudam o nível dos jogadores, o momento da
previsão e a informação usada. Maymin (2021) trata de eventos individuais
e Guan e Tung (2026) avaliam o erro de probabilidade (Brier) em vez da
acurácia, por isso ficam fora da comparação numérica.

Quanto às escolhas de projeto, as variáveis preditoras, diferenças agregadas entre os dois times, seguem
a modelagem centrada no time de Birant e Birant (2023). A granularidade
por jogador de Bahrololloomi et al. (2022) entrou apenas nos perfis de
jogador, fora da modelagem de vitória. A limitação que García-Méndez e
Arriba-Pérez (2025) apontam nos trabalhos anteriores, a falta de
interpretação das previsões, foi enfrentada com o SHAP na interface e com um
módulo de orientação que cita o dado real de cada recomendação. Jiang et al. (2025)
e Guo et al. (2024) fundamentam a consulta a dados estruturados por
modelos de linguagem. Este trabalho acrescenta a validação da consulta
antes da execução. O mapa de calor aplica, de forma mais simples, a
integração de tempo e posição de Wallner, Wang e Dormann (2023), sem a
técnica de *storyline*, e o mapa de calor de posição de Maymin (2021), que
parte de rastreamento a cada segundo, ao contrário do minuto da *timeline*.

---

## 6 CONCLUSÃO

Este trabalho teve como objetivo geral desenvolver uma plataforma
inteligente para análise de dados de esports com foco em *League of
Legends*, integrando coleta, organização e exploração de dados
competitivos, modelagem preditiva com técnicas de *machine learning* e
mecanismos de visualização e consulta em linguagem natural. Os
resultados apresentados na Seção 5 indicam que o objetivo geral foi
alcançado, com evidência para cada objetivo específico:

a) os dados e recursos da Riot Games API foram mapeados e utilizados de
forma sistemática (endpoints *league-v4*, *account-v1*, *match-v5* e
*timeline-v5*);

b) as informações relevantes de partidas, jogadores e estatísticas
foram identificadas e organizadas em um esquema relacional específico;

c) foi estruturado e executado um processo de coleta, tratamento e
organização capaz de escalar de um piloto de ~100 partidas para uma
base de 41.063 partidas de *solo queue* somadas a 96.716 partidas
profissionais;

d) técnicas de análise de dados identificaram padrões relevantes,
incluindo o viés de lado no *solo queue* de elo alto, sua constância
ao longo da partida e sua inversão em relação ao cenário
profissional, achados sustentados por testes de robustez estatística,
não apenas observação pontual;

e) três modelos de *machine learning* (XGBoost, *Random Forest* e MLP)
foram comparados, com o XGBoost adotado como modelo de produção
(acurácia 0,7621, AUC-ROC 0,8473 no corte de 15 minutos, com modelos
adicionais para os cortes de 10, 20 e 25 minutos);

f) *dashboards* foram entregues em seis páginas de visualização,
cobrindo desde estatísticas agregadas até análise minuto a minuto de
partida individual;

g) uma interface em linguagem natural foi implementada e avaliada,
atingindo 88% de acurácia de execução sobre um benchmark de 26
perguntas de referência.

O achado que merece destaque, por não ter sido o objeto anunciado do
trabalho, é o viés de lado: uma assimetria estrutural entre os dois lados
do mapa, estatisticamente firme em três das quatro regiões coletadas
(BR1, EUW1, NA1; a KR tem intervalo de confiança que inclui 50%) e com
sinal invertido no jogo profissional. O valor é duplo: é um fator de
confusão que qualquer modelo preditivo sobre *solo queue* precisa
controlar, já que o lado carrega informação sobre o resultado sem refletir
o estado da partida; e a
inversão no circuito profissional sugere origem distinta no *solo
queue*, hipótese que este trabalho delimita sem comprovar.

Como contribuição além do escopo originalmente delimitado no TCC I, a
incorporação dos dados competitivos profissionais (Oracle's Elixir)
permitiu uma comparação direta entre dois contextos institucionalmente
diferentes do mesmo jogo, produzindo dois achados quantitativos: a inversão do viés de lado entre
*solo queue* de elo alto e jogo profissional, e a diferença na conversão
de vantagem material em vitória entre os dois contextos.

### 6.1 LIMITAÇÕES E AMEAÇAS À VALIDADE

Registrar o que o trabalho não sustenta é parte da conclusão. Nenhuma das
limitações a seguir invalida os achados. Elas delimitam até onde eles
valem. O detalhe e os experimentos de cada uma estão no Apêndice G.

**Validade de construto.** A *timeline-v5* não registra o estado das ondas
de *minions* nem a ordem de escolha de campeões (*draft*), e nenhuma API
pública da Riot expõe micro-posicionamento. Onze experimentos de
enriquecimento não superaram as cinco variáveis originais (Quadro 5),
inclusive a posição dos jogadores, que existe na *timeline* e foi testada.
O próximo ganho provável depende do que a fonte não tem. Que parte do erro
do modelo venha dessa informação ausente é hipótese, não resultado medido.
Por isso nenhuma orientação da plataforma que dependa de itemização ou de
ondas vem do modelo, e a interface a marca como inferência geral.

**Validade externa.** Os resultados de *solo queue* vêm da fila ranqueada,
nas faixas Desafiante e Grão-Mestre, em cinco regiões, quatro delas com
amostra suficiente e desiguais entre si: BR1 e EUW1 concentram a maior
parte das partidas, e a KR tem intervalo que inclui 50%. Um único *patch*
concentra a maior parte da coleta. Não há base para estender as taxas por
lado nem a acurácia a outras filas, elos, versões ou jogos, ainda que a
arquitetura seja reaproveitável.

**Validade interna.** As partidas foram coletadas em janelas de tempo, sem amostragem ao longo de todo o histórico. Um padrão sazonal pode estar
confundido com o que os dados descrevem. Além disso, a validação cruzada sorteia
partidas ao acaso, e jogadores que se repetem entre partidas tornam as
dobras menos independentes do que a técnica supõe. Recortes finos, como um
jogador em um campeão ou um confronto de rota, seguem frágeis mesmo com
41.063 partidas, apesar do encolhimento estatístico (*shrinkage*) em
direção à média.

**Limitações do modelo.** Três ficam em aberto. A taxa-base do XGBoost no
estado de empate total, de 49,0% a 51,4% conforme o corte, subestima o
viés de lado medido nos dados (46,4% a 47,9%). A discrepância não é
subajuste: a busca em grade completa ficou 0,0001 de AUC acima da
produção (de 0,8473 para 0,8475, em 2º lugar entre 27 combinações), e apenas a
troca para *Random Forest* a fecha (0,6 pp), ao custo de 0,0005 de AUC.
O modelo foi treinado sobre 39.426 das 41.063 partidas do banco e não foi
retreinado, para não invalidar as validações já feitas. E
o XGBoost não garante monotonicidade isolada por variável, por não usar
restrição formal de monotonicidade.

### 6.2 TRABALHOS FUTUROS

Ficam registrados quatro caminhos. O primeiro é a extensão da predição
para o cenário de partidas ao vivo, não implementada nesta versão mas
considerada na arquitetura desde o início: a camada de predição aceita
estado de jogo arbitrário por fase, não apenas dados pré-processados de
um conjunto fixo, de modo que a barreira é de dados em tempo real, não
de modelo. O segundo é a inclusão de seleção de campeão competitiva no
simulador de time. O terceiro é a investigação de restrições de
monotonicidade formal no modelo, caso seja avaliada como necessária. O quarto
é a extensão do recorte de validade externa, que passaria por coletar
outras filas e, eventualmente, outro jogo, de modo a testar se o viés
de lado descreve o jogo ou o modo de jogar de uma população específica.
---

## REFERÊNCIAS

BAHROLOLLOOMI, Farnod; SAUER, Sebastian; KLONOWSKI, Fabio; HORST,
Robin; DÖRNER, Ralf. A machine learning based analysis of e-sports player
performances in League of Legends for winning prediction based on player roles and
performances. In: INTERNATIONAL JOINT CONFERENCE ON COMPUTER
VISION, IMAGING AND COMPUTER GRAPHICS THEORY AND APPLICATIONS,
17., 2022, Roma. **Proceedings of the 17th International Joint Conference on
Computer Vision, Imaging and Computer Graphics Theory and Applications
(VISIGRAPP 2022): Volume 2: HUCAPP**. [S. l.]: SciTePress, 2022. p. 68-76. DOI:
10.5220/0010895900003124.

BIRANT, Kokten Ulas; BIRANT, Derya. Multi-Objective Multi-Instance Learning: a
new approach to machine learning for eSports. **Entropy**, [S. l.], v. 25, n. 1, art. 28,
2023. DOI: 10.3390/e25010028. Disponível em: https://www.mdpi.com/1099-
4300/25/1/28. Acesso em: 10 jun. 2026.

BREIMAN, Leo. Random Forests. **Machine Learning**, [S. l.], v. 45, n. 1, p. 5-32,
2001. DOI: 10.1023/A:1010933404324.

BROWN, Lawrence D.; CAI, T. Tony; DASGUPTA, Anirban. Interval estimation for a
binomial proportion. **Statistical Science**, [S. l.], v. 16, n. 2, p. 101-133,
2001. DOI: 10.1214/ss/1009213286.

CHEN, Tianqi; GUESTRIN, Carlos. XGBoost: a scalable tree boosting system. In:
Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge
Discovery and Data Mining. New York: ACM, 2016. p. 785-794. DOI:
10.1145/2939672.2939785.

CRESWELL, John W.; CRESWELL, J. David. **Research design: qualitative,
quantitative, and mixed methods approaches**. 6. ed. Thousand Oaks: SAGE
Publications, 2023.

DO, Tiffany D.; WANG, Seong Ioi; YU, Dylan S.; MCMILLIAN, Matthew G.; MCMAHAN,
Ryan P. Using machine learning to predict game outcomes based on
player-champion experience in League of Legends. In: INTERNATIONAL CONFERENCE
ON THE FOUNDATIONS OF DIGITAL GAMES, 16., 2021. **Proceedings of the 16th
International Conference on the Foundations of Digital Games**. Montreal: ACM,
2021. DOI: 10.1145/3472538.3472579.

GARCÍA-MÉNDEZ, Silvia; ARRIBA-PÉREZ, Francisco de. Explainable e-sports win
prediction through machine learning classification in streaming. **Entertainment
Computing**, [S. l.], v. 55, art. 101027, 2025. DOI: 10.1016/j.entcom.2025.101027.
Disponível em:
https://www.sciencedirect.com/science/article/pii/S1875952125001077. Acesso em:
10 jun. 2026.

GIL, Antonio Carlos. **Como elaborar projetos de pesquisa**. 4. ed. São Paulo: Atlas,
2002.

GRINSZTAJN, Léo; OYALLON, Edouard; VAROQUAUX, Gaël. Why do tree-based models
still outperform deep learning on typical tabular data? In: **Advances in
Neural Information Processing Systems 35 (NeurIPS 2022)**. 2022. Disponível em:
https://arxiv.org/abs/2207.08815. Acesso em: 20 out. 2026.

GUAN, Min-Ren; TUNG, Shen-Ning. Pre-game paired-comparison modeling of
professional League of Legends map outcomes. **arXiv**, 2609.08060, 2026.
*Preprint*. Disponível em: https://arxiv.org/abs/2609.08060. Acesso em: 20 out.
2026.

GUO, Yi; SHI, Danqing; GUO, Mingjuan; WU, Yanqiu; CAO, Nan; CHEN, Qing.
Talk2Data: a natural language interface for exploratory visual analysis via question
decomposition. **ACM Transactions on Interactive Intelligent Systems**, New York,
v. 14, n. 2, art. 8, p. 1-24, 2024. DOI: 10.1145/3643894.

HANLEY, James A.; MCNEIL, Bernard J. The meaning and use of the area under a
receiver operating characteristic (ROC) curve. **Radiology**, [S. l.], v. 143,
n. 1, p. 29-36, 1982. DOI: 10.1148/radiology.143.1.7063747.

HODGE, Victoria J.; DEVLIN, Sam Michael; SEPHTON, Nicholas John; BLOCK,
Florian Oliver; COWLING, Peter I.; DRACHEN, Anders. Win prediction in multi-player
e-sports: live professional match prediction. **IEEE Transactions on Games**, [S. l.], v.
13, n. 4, p. 368-379, 2021. DOI: 10.1109/TG.2019.2948469.

HOLM, Sture. A simple sequentially rejective multiple test procedure.
**Scandinavian Journal of Statistics**, [S. l.], v. 6, n. 2, p. 65-70, 1979.

HORNIK, Kurt; STINCHCOMBE, Maxwell; WHITE, Halbert. Multilayer feedforward
networks are universal approximators. **Neural Networks**, [S. l.], v. 2, n. 5,
p. 359-366, 1989. DOI: 10.1016/0893-6080(89)90020-8.

JADOWSKI, Robbie; CUNNINGHAM, Stuart. Statistical models for predicting results
in professional League of Legends. In: WÖLFEL, Matthias; BERNHARDT, Johannes;
THIEL, Sonja (ed.). **ArtsIT, Interactivity and Game Creation**. Cham: Springer
International Publishing, 2022. p. 138-152. DOI: 10.1007/978-3-030-95531-1_10.

JIANG, Jie; XIE, Haining; SHEN, Siqi; SHEN, Yu; ZHANG, Zihan; LEI, Meng;
ZHENG, Yifeng; LI, Yang; LI, Chunyou; HUANG, Danqing; WU, Yinjun; ZHANG,
Wentao; YANG, Xiaofeng; CUI, Bin; CHEN, Peng. SiriusBI: a comprehensive LLM-
powered solution for data analytics in business intelligence. **Proceedings of the
VLDB Endowment**, [S. l.], v. 18, n. 12, p. 4860-4873, 2025. DOI:
10.14778/3750601.3750610.

KAUFMAN, Shachar; ROSSET, Saharon; PERLICH, Claudia; STITELMAN, Ori. Leakage in
data mining: formulation, detection, and avoidance. **ACM Transactions on
Knowledge Discovery from Data**, [S. l.], v. 6, n. 4, art. 15, 2012. DOI:
10.1145/2382577.2382579.

KOHAVI, Ron. A study of cross-validation and bootstrap for accuracy estimation
and model selection. In: INTERNATIONAL JOINT CONFERENCE ON ARTIFICIAL
INTELLIGENCE, 14., 1995. **Proceedings of the 14th International Joint
Conference on Artificial Intelligence (IJCAI-95)**. San Mateo: Morgan Kaufmann,
1995. p. 1137-1145.

LUNDBERG, Scott M.; LEE, Su-In. A unified approach to interpreting model
predictions. In: Advances in Neural Information Processing Systems 30 (NIPS 2017). 2017. p. 4765-4774. Disponível em: https://arxiv.org/abs/1705.07874.
Acesso em: 4 out. 2026.

MAYMIN, Philip Z. Smart kills and worthless deaths: eSports analytics for
League of Legends. **Journal of Quantitative Analysis in Sports**, [S. l.], v.
17, n. 1, p. 11-27, 2021. DOI: 10.1515/jqas-2019-0096.

NICULESCU-MIZIL, Alexandru; CARUANA, Rich. Predicting good probabilities with
supervised learning. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 22.,
2005. **Proceedings of the 22nd International Conference on Machine Learning
(ICML 2005)**. New York: ACM, 2005. p. 625-632. DOI: 10.1145/1102351.1102430.

ORACLE'S ELIXIR. **Downloads**: dados de partidas profissionais de League of
Legends. [S. l.], [s. d.]. Disponível em:
https://oracleselixir.com/tools/downloads. Acesso em: 20 out. 2026.

PEDREGOSA, Fabian et al. Scikit-learn: machine learning in Python. **Journal of
Machine Learning Research**, [S. l.], v. 12, p. 2825-2830, 2011.

PRODANOV, Cleber Cristiano; FREITAS, Ernani Cesar de. **Metodologia do
trabalho científico: métodos e técnicas da pesquisa e do trabalho acadêmico**.
2. ed. Novo Hamburgo: Feevale, 2013.

RIBEIRO, Marco Tulio; SINGH, Scott; GUESTRIN, Carlos. "Why should I trust you?":
explaining the predictions of any classifier. In: Proceedings of the 22nd ACM
SIGKDD International Conference on Knowledge Discovery and Data Mining. New
York: ACM, 2016. p. 1135-1144. DOI: 10.1145/2939672.2939778.

RIOT GAMES. **APIs**. [S. l.], [s. d.]. Disponível em:
https://developer.riotgames.com/apis. Acesso em: 12 maio 2026.

WALLNER, Günter; WANG, Letian; DORMANN, Claire. Visualizing the spatio-
temporal evolution of gameplay using storyline visualization: a study with League of
Legends. **Proceedings of the ACM on Human-Computer Interaction**, New York, v.
7, n. CHI PLAY, art. 412, p. 1002-1024, 2023. DOI: 10.1145/3611058.

WANG, Chuhan; SHIN, Yitao; LIU, Bing; POLOZOV, Alexander; RICHARDSON, Sarah.
RAT-SQL: relation-aware schema encoding and linking for text-to-SQL. In:
Proceedings of the 58th Annual Meeting of the Association for Computational
Linguistics. Association for Computational Linguistics, 2020. p. 7567-7578.
DOI: 10.18653/v1/2020.acl-main.677.

YIN, Robert K. **Case study research and applications: design and methods**. 6.
ed. Thousand Oaks: SAGE Publications, 2018.

ZHONG, Ruiqi; YU, Tao; KLEIN, Dan. Semantic evaluation for text-to-SQL with
distilled test suites. In: CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE
PROCESSING, 2020. **Proceedings of the 2020 Conference on Empirical Methods in
Natural Language Processing (EMNLP)**. [S. l.]: Association for Computational
Linguistics, 2020. p. 396-411. DOI: 10.18653/v1/2020.emnlp-main.29.

---

## APÊNDICE A – Esquema relacional do banco de dados

O banco de dados (PostgreSQL) foi estruturado com as tabelas listadas
no Quadro a seguir. `raw_matches`/`raw_timelines` preservam o JSON
bruto retornado pela Riot API (para reprocessamento sem nova coleta);
as demais são a normalização relacional usada pela análise e pela
modelagem.

Quadro — Esquema relacional do banco de dados

| Tabela | Campos | Chave |
|---|---|---|
| `players` | puuid, game_name, tag_line, tier, division, league_points, platform, updated_at | PK: puuid |
| `raw_matches` | match_id, payload (JSONB), collected_at | PK: match_id |
| `raw_timelines` | match_id, payload (JSONB), collected_at | PK/FK: match_id → raw_matches |
| `matches` | match_id, platform_id, queue_id, game_version, game_creation, game_duration_s | PK: match_id |
| `teams` | match_id, team_id, win, barons, dragons, heralds, towers, inhibitors | PK: match_id+team_id; FK: match_id → matches |
| `participants` | match_id, puuid, team_id, team_position, champion_id, champion_name, kills, deaths, assists, gold_earned, cs_total, vision_score, dmg_to_champions, win | PK: match_id+puuid; FK: match_id → matches |
| `bans` | match_id, team_id, pick_turn, champion_id | PK: match_id+team_id+pick_turn; FK: match_id → matches |
| `item_events` | id, match_id, puuid, ts_ms, item_id, action | PK: id; FK: match_id → matches |
| `items` | item_id, name, total_gold, purchasable, map_11 | PK: item_id |
| `pro_games` | game_id, league, year, split, playoffs, game_date, patch, side, team_name, win, game_length_s, kills, deaths, dragons, barons, heralds, towers, inhibitors, gold_diff_at15, xp_diff_at15, cs_diff_at15, kill_diff_at15 | PK: game_id+side |
| `pro_players` | game_id, side, position, player_name, team_name, champion, kills, deaths, assists, win | PK: game_id+side+position |

`item_events` guarda compras/vendas efetivas (`ITEM_UNDO` já resolvido
no ETL); `items` é o catálogo Data Dragon, usado para JOIN de nome/ícone
de item. Índices B-tree foram criados sobre as colunas mais usadas em
filtro (campeão, jogador, versão do jogo, liga) para suportar tanto os
endpoints da API quanto as consultas geradas pela interface em
linguagem natural.

---

## APÊNDICE B – Benchmark da interface em linguagem natural

Execução em 2026-10-04 sobre a base de produção de **41.063 partidas**:
**23/26 = 88% de acurácia de execução**, com o comando
`python -m src.nlq.evaluate_nlq`, que grava
`reports/nlq_benchmark.json` com o accuracy, a base, o modelo e o desfecho de
cada pergunta. É o mesmo número que a execução anterior mediu sobre as 39.426
partidas da base intermediária, 4% de diferença no volume que não moveu o
resultado. O mesmo número já havia saído antes, na execução de 2026-09-28
(24.154 partidas) e em uma de 2026-07-13. Uma
primeira execução, feita simultaneamente à coleta em background, mediu
22/26 (85%) com uma falha adicional na pergunta 3 ("win rate do time
azul"). Repetida a execução sem a interferência de escrita
concorrente no banco, a pergunta 3 voltou a passar, confirmando que a
falha extra foi um artefato de leitura durante escrita concorrente
(contagem mudando entre a consulta gerada e a consulta de referência),
não um erro real de interpretação. As 26 perguntas de referência:

Quadro — Benchmark de 26 perguntas de referência (NLQ)

| # | Pergunta | SQL de referência | Resultado |
|---|---|---|---|
| 1 | Quantas partidas existem no banco? | `SELECT COUNT(*) FROM matches` | OK |
| 2 | Quais os 5 campeões mais jogados? | `SELECT champion_name, COUNT(*) AS n FROM participants GROUP BY champion_name ORDER BY n DESC LIMIT 5` | OK |
| 3 | Qual o win rate do time azul? | `SELECT AVG(win::int) FROM teams WHERE team_id = 100` | OK |
| 4 | Qual a duração média das partidas em minutos? | `SELECT AVG(game_duration_s) / 60.0 FROM matches` | OK |
| 5 | Quais os 5 campeões com maior win rate com pelo menos 50 jogos? | `SELECT champion_name, AVG(win::int) AS wr FROM participants GROUP BY champion_name HAVING COUNT(*) >= 50 ORDER BY wr DESC LIMIT 5` | **FALHA** (formatação — limiar de jogos) |
| 6 | Quantos jogadores estão cadastrados na tabela de jogadores? | `SELECT COUNT(*) FROM players` | OK |
| 7 | Quantas partidas o time vermelho venceu? | `SELECT COUNT(*) FROM teams WHERE team_id = 200 AND win = true` | OK |
| 8 | Qual a média de ouro dos jogadores na posição JUNGLE? | `SELECT AVG(gold_earned) FROM participants WHERE team_position = 'JUNGLE'` | OK |
| 9 | Quais os 5 campeões mais jogados na posição MIDDLE? | `SELECT champion_name, COUNT(*) AS n FROM participants WHERE team_position = 'MIDDLE' GROUP BY champion_name ORDER BY n DESC LIMIT 5` | OK |
| 10 | Qual o win rate por posição? | `SELECT team_position, AVG(win::int) AS wr FROM participants GROUP BY team_position ORDER BY wr DESC` | OK |
| 11 | Qual a média de barões derrubados pelo time vencedor por partida? | `SELECT AVG(barons) FROM teams WHERE win = true` | OK |
| 12 | Qual o campeão com maior win rate em UTILITY, com pelo menos 20 partidas? | `SELECT champion_name, AVG(win::int) AS wr FROM participants WHERE team_position = 'UTILITY' GROUP BY champion_name HAVING COUNT(*) >= 20 ORDER BY wr DESC LIMIT 1` | **FALHA** (formatação — limiar de jogos) |
| 13 | Quantas partidas duraram mais de 30 minutos? | `SELECT COUNT(*) FROM matches WHERE game_duration_s > 1800` | OK |
| 14 | Qual a média de dano a campeões dos jogadores do time azul? | `SELECT AVG(dmg_to_champions) FROM participants WHERE team_id = 100` | OK |
| 15 | Quantos jogadores estão no tier Challenger? | `SELECT COUNT(*) FROM players WHERE tier = 'CHALLENGER'` | OK |
| 16 | Qual time, azul ou vermelho, derruba mais torres em média? | `SELECT team_id, AVG(towers) AS avg_towers FROM teams GROUP BY team_id ORDER BY avg_towers DESC LIMIT 1` | OK |
| 17 | Quantas partidas existem por versão do jogo, da mais para a menos frequente? | `SELECT game_version, COUNT(*) AS n FROM matches GROUP BY game_version ORDER BY n DESC` | OK |
| 18 | Qual o CS médio dos jogadores na posição TOP? | `SELECT AVG(cs_total) FROM participants WHERE team_position = 'TOP'` | OK |
| 19 | Quais os 5 campeões com maior média de assistências? | `SELECT champion_name, AVG(assists) AS avg_assists FROM participants GROUP BY champion_name ORDER BY avg_assists DESC LIMIT 5` | OK |
| 20 | Em quantas partidas o time com pelo menos 1 arauto também venceu? | `SELECT COUNT(*) FROM teams WHERE heralds > 0 AND win = true` | OK |
| 21 | Quantas partidas têm participantes que também estão na tabela de jogadores? | `SELECT COUNT(DISTINCT pt.match_id) FROM participants pt JOIN players p ON p.puuid = pt.puuid` | OK |
| 22 | Campeão com maior win rate entre jogadores Grandmaster, com pelo menos 10 partidas? | `SELECT pt.champion_name, AVG(pt.win::int) AS wr FROM participants pt JOIN players p ON p.puuid = pt.puuid WHERE p.tier = 'GRANDMASTER' GROUP BY pt.champion_name HAVING COUNT(*) >= 10 ORDER BY wr DESC LIMIT 1` | **FALHA** (formatação — limiar de jogos) |
| 23 | Quantos jogos profissionais de 2026 existem no banco? | `SELECT COUNT(DISTINCT game_id) FROM pro_games WHERE year = 2026` | OK |
| 24 | Qual o win rate do lado azul no competitivo em 2026? | `SELECT AVG(win::int) FROM pro_games WHERE side = 'Blue' AND year = 2026` | OK |
| 25 | Quais os 5 campeões mais jogados no competitivo em 2026? | `SELECT pp.champion, COUNT(*) AS jogos FROM pro_players pp JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side WHERE pg.year = 2026 GROUP BY pp.champion ORDER BY jogos DESC LIMIT 5` | OK |
| 26 | Qual liga teve mais jogos profissionais em 2026? | `SELECT league, COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE year = 2026 GROUP BY league ORDER BY jogos DESC LIMIT 1` | OK |

As três falhas (perguntas 5, 12, 22) pertencem à mesma família: todas
envolvem um limiar mínimo de jogos ("com pelo menos N partidas"),
questão de formatação da resposta (coluna extra ou apresentação),
não de interpretação incorreta da pergunta ou geração de SQL
estruturalmente errado, padrão já documentado em execuções anteriores
do mesmo benchmark.

---

## APÊNDICE C – Métricas completas por corte temporal

Quadro reproduzido por `python -m src.models.multi_cutoff_metrics`, que
avalia os três modelos nos quatro cortes com validação cruzada estratificada
de 5 dobras (semente 42) usando, no XGBoost, os **mesmos hiperparâmetros
de produção** (500 árvores, taxa de aprendizado 0,01, profundidade 3); a
*Random Forest* (500 árvores) e o MLP (camadas de 64 e 32 neurônios) estão
na configuração de referência, sem busca em grade. É o mesmo desenho
do quadro anterior, agora regenerável por comando. Executado em 2026-10-04
sobre a base de 39.426 partidas. Os valores do corte de 15 min reproduzem os
já citados na Seção 5.4.

Quadro — Métricas completas por corte temporal, comparação entre os três modelos

| Corte | n | Taxa vitória azul | Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 10min | 39.309 | 0,466 | RandomForest | 0,6704 | 0,6515 | 0,6301 | 0,6406 | 0,7341 |
| 10min | 39.309 | 0,466 | **XGBoost** | 0,7004 | 0,6912 | 0,6461 | 0,6679 | 0,7742 |
| 10min | 39.309 | 0,466 | MLP | 0,7020 | 0,6861 | 0,6651 | 0,6755 | 0,7735 |
| 15min | 39.188 | 0,466 | RandomForest | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |
| 15min | 39.188 | 0,466 | **XGBoost** | 0,7621 | 0,7561 | 0,7228 | 0,7391 | 0,8473 |
| 15min | 39.188 | 0,466 | MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| 20min | 34.337 | 0,466 | RandomForest | 0,7785 | 0,7659 | 0,7551 | 0,7604 | 0,8623 |
| 20min | 34.337 | 0,466 | **XGBoost** | 0,7917 | 0,7817 | 0,7666 | 0,7741 | 0,8762 |
| 20min | 34.337 | 0,466 | MLP | 0,7866 | 0,7712 | 0,7701 | 0,7707 | 0,8729 |
| 25min | 26.837 | 0,467 | RandomForest | 0,8147 | 0,8047 | 0,7969 | 0,8008 | 0,8975 |
| 25min | 26.837 | 0,467 | **XGBoost** | 0,8241 | 0,8172 | 0,8034 | 0,8103 | 0,9090 |
| 25min | 26.837 | 0,467 | MLP | 0,8240 | 0,8171 | 0,8033 | 0,8101 | 0,9072 |

Nota: este quadro e a série de AUC-ROC por fase citada na Seção 5.4
(0,774 / 0,847 / 0,876 / 0,909) usam os **mesmos** hiperparâmetros de
produção do XGBoost (500 árvores, *learning rate* 0,01, profundidade 3). A
versão anterior desta nota afirmava que eram diferentes, e não são:
`src/models/multi_cutoff_metrics.py` e `src/models/export_model.py` leem a
mesma configuração. A diferença entre os valores atuais e a série
histórica de 2026-07-08 (0,767 / 0,842 / 0,872 / 0,907) vem da base de
treino, que era de 23.133 partidas e passou a 39.426, e não do ajuste. O
comando que regenera este quadro é
`python -m src.models.multi_cutoff_metrics`.

---

## APÊNDICE D – Notas sobre os experimentos negativos

Os onze experimentos estão no Quadro 5 da Seção 5.4. Três deles pedem
detalhe que não cabe no quadro.

*Nota sobre o experimento 4.* A ausência de ganho de AUC da calibração foi
reexaminada em 2026-10-04, quando a limitação de taxa-base (Apêndice G)
passou a ser testada contra as alavancas que este apêndice não cobre. O
resultado é mais forte que "sem ganho": a calibração **piora** também a
discrepância de taxa-base, de 1,7 para 2,3 pontos percentuais, porque o
estado de empate total fica fora da distribuição observada e o calibrador o
extrapola para perto de 50%. A *Random Forest* com 500 árvores e
profundidade 6 fecha a discrepância (0,6 pp) ao custo de 0,0005 de AUC,
mas não foi adotada; a justificativa está no Apêndice G. Esse teste não
figura na tabela porque não é enriquecimento de variáveis, e sim
caracterização de uma limitação de modelo; o comando é
`python docs/experimento_calibracao.py`.

*Nota sobre o experimento 10.* Achado em 2026-10-05 ao inspecionar o
payload bruto real da timeline em busca de evento ainda não testado (não
pela documentação oficial, que exige login para detalhar *schema*).
`TURRET_PLATE_DESTROYED` cobre exatamente a janela onde `tower_diff` é
pouco informativo (torres raramente morrem antes dos 15 min, mas placas
são batidas o jogo inteiro nessa janela), hipótese concreta, mas o sinal
de pressão de rota que capta já deve estar redundante com
`gold_diff`/`xp_diff`. Comando e artefato: `python -m
src.models.experiment_turret_plates` e
`reports/experimento_placas_torre.json`.

*Nota sobre o experimento 11.* Único entre os onze que não vem da
*timeline*: `lol-challenges-v1` devolve o estado comportamental VITALÍCIO
e ATUAL do jogador, não o estado dele na época de uma partida passada; um
teste ingênuo sobre o histórico vazaria dado do futuro. Contornado medindo
sobre as partidas mais recentes da KR (gap de horas/dias entre a coleta e
a consulta, registrado, não suposto). Um piloto inicial (199 partidas)
sugeriu `teamwork_pct_diff` com delta +0,0090, maior que qualquer outro
experimento, mas a escala para 2.987 partidas (gap 0-16 dias, média 7,8)
devolveu -0,0031, dentro do ruído dos demais. O piloto pequeno era
regressão à média, não sinal: o próprio *baseline* já oscilava 1,8 pp do
AUC de produção apenas pelo tamanho da amostra. Comando e artefato: `python -m
src.models.experiment_challenges_pilot --n-matches 3000` e
`reports/experimento_challenges_piloto.json`.

Em contraste, o aumento de *volume* de partidas produziu ganho real:
AUC-ROC do XGBoost (corte 15 min) subiu de 0,8214 (10.295 partidas)
para 0,8393 (23.133 partidas) e para 0,8473 (39.188 partidas) ao longo
da coleta incremental, um ganho acumulado de 0,0259, cerca de 6× maior
que o maior ganho de qualquer um dos 11 experimentos de variáveis (0,003),
e cerca de 130× o menor deles (0,0002).

---

## APÊNDICE E – Proveniência das medições da Seção 5.3

**Histórico do Quadro 2.** O quadro original, medido em 2026-07-06 com BR1
11.936, EUW1 1.307, NA1 1.367 e KR 1.308 partidas, foi substituído por uma
segunda rodada de coleta destinada especificamente a ampliar EUW1, KR e NA1, e
depois pela medição de 2026-10-04, quando EUW1 e KR já haviam quase dobrado
novamente e a NA1 também foi ampliada. A direção do achado (todas as quatro
regiões com amostra relevante do lado do vermelho) se manteve idêntica em todas
as quatro medições. A BR1 não se alterou em nenhum dos quatro levantamentos. A
NA1, que era o elo mais frágil da generalização, foi ampliada de 1.446 para
7.159 partidas na rodada final, e a taxa do vermelho passou de 51,9% para
52,2%. A direção do achado não mudou, e a NA1 deixou de ser limitação.

**Origem das taxas de conversão de vantagem.** Todas as taxas de conversão da
Seção 5.3 foram remedidas sobre a base de variáveis congelada (39.309 partidas
distintas, 39.188 no corte de 15 minutos) pelo script
`docs/confere_conversao_advantagem.py`, que lê `data/features_phases.csv`.

**Teste (ii), faixas de duração.** Foi remedido em 2026-10-04 sobre a base atual, porque a
medição que o texto usava era de 2026-07-08 e de uma base quase metade
desta: as taxas por faixa de duração total são 46,5% (0 a 25 min, 15.944
partidas), 47,3% (25 a 30, 13.314), 46,4% (30 a 35, 8.364), 45,6% (35 a 40,
2.684) e 47,0% (acima de 40, 757). A amplitude é de 1,7 ponto percentual e
todas as faixas ficam abaixo de 50%: o teste se sustenta, agora com data,
base e amplitude explícitas.

**Série anual do cenário profissional.** Vitória do azul por ano nos dados competitivos: 53,6% (2016), 55,0% (2017), 53,7% (2018), 53,2% (2019), 52,7% (2020), 52,6% (2021), 52,5% (2022), 53,3% (2023), 53,1% (2024), 53,3% (2025) e 53,1% (2026). Os dois primeiros anos divergem (58,2% em 2014 e 55,3% em 2015), mas se apoiam em amostras muito menores (814 e 1.702 jogos, contra 96.716 no total), e a diferença é atribuída a essa assimetria de volume, não a uma mudança no padrão.


---

## APÊNDICE F – Telas completas da plataforma

As seis telas, inteiras, das quais a Seção 5 mostra recortes. Geradas em
2026-10-28 via Playwright (Chromium, 1440 px de largura, altura ajustada à
página, sem `full_page`, **tema escuro**) contra a API e o *frontend*
rodando localmente, com **41.063 partidas** na fila ranqueada, a mesma base
do Quadro 2 da Seção 5.3. O instante e a base estão em
`reports/anexo_a/captura.json`, gravado pelo comando que produz as telas
(`python docs/recapturar_anexo_a.py`); os recortes da Seção 5 têm o próprio
registro, `reports/figuras_texto/figuras.json`, gravado por
`python docs/capturar_figuras_texto.py`. O tema escuro é o da própria
interface, aplicado antes de a página montar, e não um filtro de imagem.

| Arquivo | Página |
|---|---|
| `reports/anexo_a/01_inicio.png` | Início (busca unificada) |
| `reports/anexo_a/02_dashboard.png` | Dashboard (KPIs, viés de lado por região, cobertura do dataset) |
| `reports/anexo_a/03_campeoes.png` | Campeões |
| `reports/anexo_a/04_partida_detalhe.png` | Partidas: análise de uma partida individual |
| `reports/anexo_a/05_competitivo.png` | Competitivo (solo queue × profissional) |
| `reports/anexo_a/06_simulador.png` | Simulador, aba Estado |

---

## APÊNDICE G – Limitações em detalhe

Detalhe das limitações resumidas na Seção 6.1, com os números e os
experimentos de cada uma.

**A taxa-base do modelo em estado de empate subestima o viés de lado.**
Com o retreino de 39.188 partidas, a probabilidade prevista para o estado
"tudo empatado" ficou em 49,2% (10 min), 49,6% (15 min), 51,4% (20 min) e
49,0% (25 min), enquanto a medição direta sobre os dados brutos, entre
partidas genuinamente empatadas, dá 46,4% a 47,9% (Seção 5.3): uma
diferença de **1,7 a 4,7 pontos percentuais conforme o corte**. A série
do modelo é plana, sem o pico de meio de jogo da primeira versão do
texto, mas as duas séries não concordam em magnitude, nem sempre em
direção: aos 20 minutos o modelo projeta 51,4% de vitória azul,
favorecendo o azul, enquanto o dado bruto dá 46,7%, favorecendo o
vermelho. A discrepância não decorre de subajuste: uma busca em grade
completa (27 combinações, 5 dobras) escolheu a **mesma profundidade** de
produção (3) e terminou 0,0001 de AUC acima dela, de 0,8473 para 0,8475,
em 2º lugar entre as 27. Testadas as três alavancas que a grade não cobre,
a conclusão é contraintuitiva: a **calibração piora** a discrepância (de
1,7 para 2,3 pp na sigmoidal), porque o estado de empate total fica fora
da distribuição observada e o calibrador o extrapola para perto de 50%; a
regularização alternativa move o desvio dentro do ruído; e apenas a **troca
de família** o fecha: uma *Random Forest* com 500 árvores e profundidade 6
leva o desvio a **0,6 pp** ao custo de 0,0005 de AUC. A discrepância é,
portanto, uma propriedade da função que o XGBoost aprende neste recorte, e
não um déficit de ajuste. A troca não foi adotada porque o critério de
escolha do modelo foi a acurácia no corte de 15 min, e nela a *Random
Forest* fica em 0,7617 contra 0,7621. É decisão consciente e reversível,
sem retreino. Comando e artefato: `docs/experimento_calibracao.py` e
`reports/experimento_calibracao_veredito.json`.

**O modelo não viu a última rodada de coleta.** As variáveis e a
modelagem foram construídas sobre 39.426 partidas, e a base do banco tem
41.063, 1.637 partidas a mais, quase todas da KR (das 1.754 partidas do
banco que não geraram variáveis, 1.647 são da KR e 107 são de BR1, EUW1 e
NA1). O conjunto que de fato alimentou o modelo são 39.309 partidas
distintas, das quais 39.188 chegam ao corte de 15 minutos; as outras 117
da base congelada não produziram linha em `features_phases.csv`. A
discussão de volume da Seção 5.4 mediu que o ganho de AUC por volume é da
ordem de 0,001 por acréscimo relevante, o que situa o efeito desta
diferença abaixo do que aquela discussão mediu como ganho real, mas não
nulo. Retreinar foi deixado de fora porque o desempenho do modelo atual já
está medido e validado contra o Apêndice C e a bateria comportamental, e
refazê-lo invalidaria as duas coisas sem ganho apurado. Quem quiser o
modelo treinado sobre a base completa reexecuta `train_baseline` e
`export_model`.

**Teto de desempenho das variáveis atuais.** Onze experimentos de
enriquecimento de variáveis não superaram o modelo com as cinco
variáveis originais (Quadro 5), dez a partir da mesma fonte de dados
(linha do tempo da partida) e um a partir de uma fonte diferente
(percentis comportamentais do jogador via `lol-challenges-v1`, Apêndice
D), o que descarta a hipótese de que o teto fosse apenas da *timeline*
esgotada. O próximo ganho relevante depende de dado que a API não fornece:
a ordem de escolha de campeão (*draft*), que a API pública não expõe, e o
estado das ondas de *minions*. A posição em tempo real **existe** no
payload da *timeline* (`participantFrames`) e já foi testada sem ganho
mensurável (experimento 2, dispersão espacial do time), de modo que ela
não é o que falta.

**Ausência de dados de micro-posicionamento** (movimentação de *minions*,
controle de onda). Nenhuma API pública da Riot expõe esse nível de
detalhe; caminhos alternativos (replays `.rofl`, visão computacional sobre
o minimapa) foram considerados, mas não implementados neste trabalho.

**Desequilíbrio de amostra por região.** Após as rodadas adicionais de
coleta, BR1 e EUW1 concentram a maior parte dos dados (11.936 e 11.744
partidas) e a KR cresceu para 10.204; a NA1, que permanecia em 1.446, foi
ampliada para 7.159 na rodada final, o que reduz a assimetria entre
regiões sem eliminá-la. O achado de viés de lado "generalizado ao elo
alto, não específico do Brasil" se apoia nas três regiões com evidência
estatística firme; três das quatro têm taxa cujo intervalo de 95% exclui
50%, e a KR fica em 50,4%, com intervalo que inclui 50%.

**Cobertura desigual por versão do jogo** (*patch*). Um único *patch*
concentra a maior parte das partidas coletadas, o que limita a
generalização dos achados para versões do jogo com balanceamento
diferente.

**Monotonicidade isolada por fator.** O XGBoost não garante formalmente
que aumentar isoladamente a diferença de abates ou de torres nunca reduza
a probabilidade prevista de vitória, por conta de interações e
redundâncias entre variáveis. O comportamento é documentado e
compreendido, mas não corrigido por restrição formal
(`monotone_constraints`) nesta versão.

---

## ANEXO A – Documentação da Riot Games API

Referência: RIOT GAMES. **APIs**. Disponível em:
https://developer.riotgames.com/apis. Endpoints utilizados: *league-v4*
(elos Desafiante/Grão-Mestre), *account-v1* (resolução de Riot ID),
*match-v5* e *timeline-v5* (dados de partida e linha do tempo).

---

## Pendências finais antes da entrega

1. ~~Resumo/Abstract~~ — **feito**.
2. **Título acadêmico — DECIDIDO (2026-10-03): não citar Bellestraiko.**
   O título do TCC 2 é o mesmo do TCC 1 ("Plataforma Inteligente para
   Análise de Dados de Esports: uma proposta para League of Legends com
   uso de machine learning e interface em linguagem natural"). Decisão do
   autor: por ser o mesmo trabalho, o título acompanha o do TCC 1. O nome
   do produto foi registrado no corpo, na Seção 1.1: "A plataforma,
   batizada Bellestraiko, constitui a materialização do sistema
   desenvolvido e implementado ao longo deste trabalho". A interface já
   usa esse nome em produção (ver capturas do Anexo A).
3. **Trabalhos Relacionados — DECIDIDO (2026-10-04): É seção de primeiro
   nível.** A decisão anterior (2026-10-03, "não é seção") seguia o modelo
   institucional de 2026-09-28, que não prevê a seção. Ao medir os **10 TCC II
   aprovados** da UNISINOS (cinco com "Aprov. Destição", três "Pos Banca"),
   em 2026-10-04, verificou-se que **10 de 10** a têm como seção de primeiro
   nível — é o padrão que a banca efetivamente aprovou. A decisão foi
   invertida: o trabalho segue o padrão dos aprovados, não o do modelo.
   A referência conceitual dos estudos fica na Seção 2 e a comparação
   direta com os resultados obtidos, na Seção 5.7.
4. ~~Apêndices/Anexos~~ — **feitos**: A (schema), B (26 perguntas NLQ,
   88% confirmado com dados frescos), C (quadro cruzado 4 cortes × 3
   modelos), D (11 experimentos negativos), Anexo A (6 capturas de tela
   reais em `reports/anexo_a/`), Anexo B (referência da API).
5. **Formatação final — FEITA (2026-10-03).** O texto foi vertido para
   `.docx` institucional por script, não à mão. Pipeline em
   `docs/build_tcc_docx.py` + `docs/finalize-fields.ps1`, produzindo
   `docs/tcc2_final.docx` (58 páginas; corpo = **30 páginas**, medido por
   `docs/finalize-fields.ps1`, que localiza a Seção 1 e o fim das
   Referências e reporta a diferença — a faixa institucional é 25 a 30).
   A formatação (A4, margens 3/2/3/2 cm, Arial 12, entrelinha 1,5, capa,
   folha de rosto, identidade) é **herdada do TCC I** via
   `--reference-doc`, não reescrita.

   As duas correções do Prof. Elvandi aplicadas no TCC I foram
   conferidas no documento gerado:
   - Títulos de seção em maiúscula **sem negrito** — verificado no `.docx`
     gerado: **49 títulos, 0 em negrito**. Já saía certo.
   - Referências com **1 linha em branco** separando cada entrada —
     **não saía certo** na primeira geração (o pandoc cola as entradas
     em parágrafos `Normal`). Corrigido no pipeline: **18 referências** no
     estilo `REFERÊNCIAS` do TCC I, com a separação entre entradas.

   Todas as contagens acima são medidas por `python docs/confere_docx.py`,
   que confere também legendas (6 Figuras, 6 Quadros), fontes de ilustração
   (11), tabelas (6) e imagens (6). Ele falha com exit 1 se qualquer uma
   divergir — os números do checklist não são mais escritos à mão, que era
   como "41 títulos" e "12 referências" ficaram velhos sem ninguém perceber.

   As 3 regras do modelo institucional de 2026-09-29 também estão
   aplicadas — as duas últimas passaram a valer no `.docx`, não só no
   Markdown:
   - Palavras-chave separadas por **ponto final**, não ponto-e-vírgula
     — corrigido no Resumo/Abstract.
   - Tabelas se chamam **"Quadro"** nesta instituição — feito no `.docx`:
     6 Quadros com numeração automática por campo `SEQ` (o Apêndice A
     virou Quadro em 2026-10-05, ver pendência abaixo). **Sem** página de
     Lista de Quadros — ver correção de 2026-10-05 logo abaixo.
   - Figuras: legenda no **topo**, fonte obrigatória **abaixo** (mesmo
     para figura de autoria própria) — feito: as 6 capturas do Anexo A
     entraram como figuras com essa convenção.
   - **Correção 2026-10-05 (Bloco B da revisão, "modelos e exemplos do
     TCC II"):** Sumário, Lista de Ilustrações e Lista de Quadros foram
     REMOVIDOS do pré-textual. Os três vinham do modelo institucional
     genérico (nunca cruzado contra os aprovados de verdade nesse item
     específico). Ao extrair a estrutura dos 10 TCC II aprovados
     (`Downloads/TCC II - EXEMPLOS E MATERIAIS/`), confirmou-se em
     **10 de 10** que a Introdução começa na página 3 ou 4 — direto
     após capa+folha de rosto+resumo/abstract, sem nenhum dos três
     elementos no meio. Documento caiu de 59 para 55 páginas totais
     (o corpo, Introdução→Referências, não muda — é medida relativa,
     segue em 30). `listas_de_ilustracoes()` removida de
     `build_tcc_docx.py` (função morta, sem mais uso).
   - Confirmado também: a estrutura de seções do corpo (além de
     Introdução/Referencial Teórico obrigatórios) é **livre, por
     acordo com o orientador**. Em 2026-10-04, a medição dos **10 TCC II
     aprovados** mostrou que 10 de 10 usam "Trabalhos Relacionados" como
     seção de primeiro nível e "Metodologia" (não "Material(is) e
     Métodos"), o que reverte a pendência nº 3 (item 3 acima).
     Limite de páginas do TCC II: **25 a 30 páginas**, não contando
     apêndices/anexos.
6. ~~Ampliar a coleta EUW1/KR/NA1~~ — **feito**: EUW1 1.307→11.744
   partidas, KR 1.308→10.204 e **NA1 1.446→7.159** (a NA1 foi ampliada na
   rodada final de 2026-10-04; a limitação que ela representava saiu das
   limitações, então na 5.8). Quadro de viés de lado por região remedido com dados de
   2026-10-04 (Seção 5.3) e verificado por SQL direto contra o valor
   mostrado no *dashboard*: BR1 56,3%, EUW1 53,4%, KR 50,4%, NA1 52,2% de
   vitória do time vermelho, sobre 41.063 partidas.

**Status (2026-10-04):** de 6 pendências, **6 estão fechadas**. **Nenhuma
depende do orientador.** As duas decisões de escopo (título acadêmico e
Trabalhos Relacionados como seção de primeiro nível) estão nos itens 2 e 3
acima e não se repetem aqui.

Antes de entregar, a suíte completa passa:
`tests/smoke_test.py` (exit 0), `tests/validate_predictions.py`
(APROVADO COM RESSALVAS), `docs/verifica_tcc.py` (20 checagens de
consistência do texto contra o banco e os artefatos, exit 0),
`docs/confere_docx.py` (conformidade formal do `.docx`, exit 0), e
`cd frontend; npm run lint; npm run test` (31/31).

**Resta 1 item, já resolvido:** o título do Quadro 4 (Apêndice C), que no
rascunho só tinha nota de método — o que viola a regra da instituição, já
que tabela sem legenda não é permitida. O título foi escrito na conversão e
**confirmado pelo autor em 2026-10-03**: "Métricas completas por corte temporal
— comparação entre os três modelos".

**Nenhuma pendência em aberto.** A última era a reexecução do benchmark de
linguagem natural do Apêndice B, fechada no mesmo dia: o accuracy de 88% foi
medido sobre a base final de 41.063 partidas e passou a ter artefato em
`reports/nlq_benchmark.json`.

**Estrutura final do corpo (2026-10-04), seguindo os 10 TCC II aprovados:**
1 Introdução · 2 Fundamentação Teórica · 3 Trabalhos Relacionados ·
4 Metodologia · 5 Resultados e Análise · 6 Conclusão. Note que difere do
modelo institucional de 2026-09-28 (Referencial Teórico em vez de
Fundamentação, sem Trabalhos Relacionados, Material(is) e Métodos em vez de
Metodologia, Resultados e Discussão separados): prevalece o padrão que a banca
aprovou.

**Formatação — DECIDIDO (2026-10-05): segue o `.doc` oficial do
Prof. Elvandi, não mais os 10 aprovados.** O usuário pediu que a
formatação batesse com
`TCC II - Modelo de artigo científico da UNISINOS - Exemplo Prof. Elvandi.doc`
como requisito obrigatório. Convertido via automação do Word
(`docs/modelo_elvandi.docx`) e medido direto do XML dos estilos — não por
inferência de PDF:
- **Recuo de parágrafo = 1,25 cm** (`w:firstLine="709"` twips no estilo
  `Normal`) — reverte a medição de 2026-10-04 sobre os 10 aprovados (que
  tinha achado ≈0 e descartado a regra do `Ajustes LATEX.txt`); aquela
  medição vinha de texto extraído por `pypdf`, que o próprio plano já
  avisava não bastar para aferir layout. O XML do estilo é a fonte que
  prevalece.
- **Títulos em negrito + caixa alta** (`<w:b/><w:caps/>` no estilo
  `heading 1`) — reverte a decisão de "sem negrito" (que vinha de um
  comentário manual pontual do orientador numa revisão do TCC I).
  Decisão do usuário: entre os dois sinais do mesmo orientador, prevalece
  o modelo oficial de artigo, mais explícito e mais recente.
- Margens (3/2/3/2 cm), fonte (Arial 12), entrelinha (1,5) e
  justificado já batiam — confirmados no XML, não só herdados do TCC I.

Aplicado em `ajustar_tipografia()`/`aplicar_negrito_titulos()` (novo) em
`docs/build_tcc_docx.py`; `docs/confere_docx.py` invertido para exigir
negrito (era "regra: zero", virou "regra: zero título SEM negrito").

**Efeito colateral e correção (2026-10-05):** o recuo de 1,25 cm sozinho
empurrou o corpo de 30 para 31 páginas — acima do teto institucional.
Cortado texto expositivo redundante (não achado) até voltar a 30: a
sobreposição real entre 5.8/6.1 (~115 palavras), a comparação com a
literatura na síntese da Seção 3.6 (~160 palavras) e a exposição técnica
de RF/XGBoost/MLP e LIME/SHAP na Seção 2 (~400 palavras, sem perder
nenhuma citação). No processo, 3 bugs de texto reais foram encontrados e
corrigidos: um trecho da Conclusão com caracteres árabes corrompidos
misturados no meio da frase, "gerposta" (não é palavra, na Seção 2.4) e
"incorporate" (inglês, não português, mesma seção). Resultado: 30
páginas de corpo, no teto da faixa 25-30, sem folga — qualquer edição
futura do corpo precisa remedir com `docs/finalize-fields.ps1`.

**Apêndice A reformatado (2026-10-05):** o esquema relacional saiu de um
bloco de código SQL (ilegível no `.docx` — sem quebra de linha
inteligente, texto cru) para um Quadro de verdade (Tabela × Campos ×
Chave, 11 linhas), consistente com a convenção "Quadro" já usada no
resto do documento. Isso subiu a contagem de 5 para **6 Quadros** — todas
as referências a "5 Quadros"/"tabelas (5)" acima foram atualizadas, e
`docs/confere_docx.py` também.
