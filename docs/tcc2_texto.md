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
de pesquisa aplicada, de abordagem quantitativa, sobre 41.063 partidas
ranqueadas de elo alto em cinco regiões, coletadas via Riot Games API, e
99.259 jogos profissionais de 2014 a 2026 (Oracle's Elixir). Três
modelos (XGBoost, *Random Forest* e uma rede neural MLP) foram comparados
por validação cruzada estratificada para predizer o vencedor em quatro
cortes temporais, de 10 a 25 minutos. Os três ficaram próximos, e o
XGBoost, adotado em produção, alcançou acurácia de 0,7621 e AUC-ROC de
0,8473 no corte de 15 minutos. Uma regressão logística simples chegou ao mesmo patamar. A análise exploratória identificou viés de lado favorável ao time vermelho no *solo queue* de elo alto (56,3% de vitórias na região com maior amostra), estável ao longo da partida. No cenário profissional o viés se inverte, e o azul vence 53,2% dos jogos,
achado sustentado por testes de robustez. Uma interface *text-to-SQL* com validação estrutural e roteamento entre as duas bases acertou 181 de 203 perguntas (89,2%) de um gabarito automático conferido por código. A plataforma reúne seis páginas de visualização com
predição explicável (SHAP). Os resultados mostram a viabilidade de
integrar essas etapas em uma única solução.

**Palavras-chave:** esports; *League of Legends*; análise de dados;
*machine learning*; interface em linguagem natural.

**Abstract:** The growth of esports increases the data generated about
matches, players and strategies, but exploring these data still depends
on fragmented tools and technical expertise. This work developed an
intelligent platform for *League of Legends* data analysis that
integrates data collection, predictive modeling with machine learning,
explainability, visualization and natural language querying. It is
applied research with a quantitative approach, based on 41,063 high-elo
ranked matches from five regions, collected through the Riot Games API,
and 99,259 professional games from 2014 to 2026 (Oracle's Elixir). Three
models (XGBoost, Random Forest and an MLP neural network) were compared
through stratified cross-validation to predict the winning team at four
time cutoffs, from 10 to 25 minutes. The three performed similarly, and
XGBoost, adopted in production, reached an accuracy of 0.7621 and an
AUC-ROC of 0.8473 at the 15-minute cutoff. A simple logistic regression reached the same level. The exploratory analysis identified a side bias favoring the red side in high-elo solo queue (56.3% win rate in the region with the largest sample), stable
throughout the match. In the professional scenario the bias reverses, and
the blue side wins 53.2% of games, a finding supported by robustness
tests. A text-to-SQL interface with structural validation and routing between the two databases answered 181 of 203 questions (89.2%) of an automatic gold standard checked by code. The platform comprises
six visualization pages with explainable predictions (SHAP). The results
show the feasibility of integrating these stages into a single solution.

**Key-words:** esports; *League of Legends*; data analysis; *machine learning*; natural language interface.

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
profissionais (Oracle's Elixir, 99.259 jogos de 2014 a 2026), o que
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

f) propor *dashboards* para visualização das informações e dos
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
citadas pela propriedade técnica que justifica o uso (Apêndice G). Os estudos do
domínio são descritos autor a autor na Seção 3 e confrontados com os
resultados na Seção 5.7.

### 2.1 ESPORTS E ANÁLISE DE DADOS

Jogos competitivos geram grande volume de dados sobre partidas,
jogadores, equipes e eventos em tempo real, o que faz dos esports um
campo relevante para a análise de dados. Hodge et al. (2021) mostram que
é possível prever o resultado de partidas profissionais de *Dota 2*
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
variáveis em cada nó. Isso reduz a correlação entre as árvores, que limita o ganho de um *ensemble* e pesa aqui, porque as variáveis preditoras (ouro, abates e torres) evoluem juntas na partida.

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
predição, simples de ler, mas pouco fiel se o modelo for muito não linear na vizinhança. O SHAP
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
a precisão da conversão. Neste trabalho, a segurança da consulta não é delegada ao modelo: ela é validada antes de tocar o banco, e a correção semântica é medida no *benchmark* (Seção 5.6).

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
aqui tratado. As principais obras de método (Breiman, 2001; Chen; Guestrin, 2016; Hanley; McNeil, 1982; Lundberg; Lee, 2017; Ribeiro; Singh; Guestrin, 2016; Wang et al., 2020) estão na Seção 2, no ponto em que o método que
elas fundamentam é introduzido.

### 3.1 PREDIÇÃO DE VITÓRIA EM DOTA 2

Hodge et al. (2021) tratam da predição de vitória em partidas
profissionais de *Dota 2*, em tempo real. Com modelos de aprendizado de máquina
padrão, engenharia de atributos e otimização, chegam a até 85% de
acurácia após 5 minutos de jogo, em previsões ao vivo de 28 partidas de um
torneio, o que estabelece a predição de
resultados em esports como problema tratável por modelagem estatística.
Por tratar de outro jogo, o estudo sustenta a abordagem de prever a
partir do estado da partida, mas não o recorte de *League of Legends*.

### 3.2 ESTUDOS DE PREDIÇÃO EM LEAGUE OF LEGENDS

Birant e Birant (2023) apresentam uma abordagem de aprendizado
multi-objetivo e multi-instância (*Multi-Objective Multi-Instance
Learning*) aplicada a esports e destacam a modelagem centrada no time, em vez do jogador isolado. É a orientação adotada aqui, com as variáveis
preditoras construídas como diferenças agregadas entre os dois times.
Bahrololloomi et al. (2022) percorrem o caminho oposto: predizem a vitória a partir das métricas individuais dos jogadores e concluem que o peso de cada função é desprezível. Aqui, esse nível só aparece nos perfis de jogador.

Outros estudos preveem partidas de *League of Legends* com insumos
diferentes. Jadowski e Cunningham (2022) ajustam classificadores
estatísticos a métricas das ligas profissionais de 2020 e acertam 67% dos
306 jogos da etapa seguinte. Do et al. (2021) preveem partidas ranqueadas
antes de elas começarem, a partir da experiência de cada jogador com o
campeão escolhido, e chegam a 75,1% de acurácia com uma rede neural
profunda. Maymin (2021) calibra um modelo de probabilidade de vitória com
dados de milhões de partidas ranqueadas e avalia abates e mortes pelo efeito que têm nessa probabilidade. Guan e Tung (2026), em um *preprint*
ainda sem revisão por pares, fazem previsão pré-jogo no cenário
profissional e tratam o lado do mapa e a prioridade de escolha como
covariáveis do modelo.

### 3.3 PREDIÇÃO COM INTERPRETAÇÃO EM COUNTER-STRIKE

García-Méndez e Arriba-Pérez (2025) combinam classificação por *machine
learning* com mecanismos de interpretação na predição de vitória em
partidas profissionais de *Counter-Strike*, em fluxo contínuo (*streaming*).
Eles apontam a falta de interpretabilidade como uma das principais
limitações dos trabalhos anteriores, o que orienta a camada de
explicabilidade da plataforma.

### 3.4 SISTEMAS DE CONSULTA EM LINGUAGEM NATURAL SOBRE DADOS

Jiang et al. (2025) apresentam o SiriusBI, solução de *Business
Intelligence* apoiada por modelos de linguagem para análise de dados em
contextos corporativos, e Guo et al. (2024), o Talk2Data, interface em
linguagem natural para análise visual exploratória baseada em
decomposição de perguntas. Os dois usam modelos de linguagem como camada
de interação sobre dados estruturados e motivam o *text-to-SQL* deste
trabalho, que leva a abordagem ao domínio de *League of
Legends*.

### 3.5 VISUALIZAÇÃO ESPAÇO-TEMPORAL DE PARTIDAS

Wallner, Wang e Dormann (2023) estudam a evolução espaço-temporal do
gameplay em *League of Legends* com a técnica de *storyline
visualization* e mostram que integrar tempo e localização numa só vista é viável para a interpretação pós-jogo. O estudo é a
referência do posicionamento minuto a minuto da análise de partida.

### 3.6 SÍNTESE E POSIÇÃO DESTE TRABALHO

Os estudos revisados cobrem frentes isoladas: predição de resultados, interpretabilidade da predição (García-Méndez; Arriba-Pérez, 2025),
interação em linguagem natural (Jiang et al., 2025; Guo et al., 2024) e visualização
espaço-temporal (Wallner; Wang; Dormann, 2023). No entanto, nenhum deles é entregue como uma
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
próprio domínio, com 26 perguntas fixas de referência e um gabarito automático de
203, ambos conferidos contra o banco, o que permite medir o erro de conversão,
sem se limitar a exemplos ilustrativos.

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
dos padrões e dos modelos comparados (Gil, 2002). A abordagem é predominantemente quantitativa (Creswell; Creswell, 2023): a coleta,
a análise exploratória e a comparação entre os modelos de aprendizado de máquina
trabalham com dados numéricos, e a revisão bibliográfica e a interpretação dos
achados dão o contexto.

### 4.2 ESTRATÉGIAS DE PESQUISA

O trabalho foi desenvolvido por meio de pesquisa bibliográfica (Gil, 2002) e de
pesquisa documental sobre a documentação oficial da Riot Games API (Prodanov;
Freitas, 2013), com aplicação delimitada ao domínio de *League of Legends*.

### 4.3 COLETA DE DADOS

A coleta usou duas fontes. A segunda foi incorporada durante o TCC II,
além do escopo previsto no TCC I.

**a) Riot Games API (*solo queue*).** O endpoint *league-v4* identificou
os jogadores de elo alto (Desafiante a Mestre), recorte de escopo: uma
população fechada, que a API lista por inteiro e que cabe no limite de
requisições da chave de desenvolvedor. O *account-v1* resolveu o Riot ID,
e o *match-v5* trouxe cada partida e sua linha do tempo minuto a
minuto. A coleta cobriu cinco regiões (BR1, EUW1, KR, NA1 e
EUN1, esta com amostra insuficiente e fora da leitura) na fila 420
(ranqueada solo/duo), em um total de **41.063 partidas**. Como a chave de desenvolvedor
expira a cada 24 horas, o coletor retoma de onde parou e pula as partidas
já salvas.

**b) Oracle's Elixir (cenário profissional).** Foram incorporados
**99.259 jogos profissionais** de 2014 a 2026, de 122 ligas, da elite às de
desenvolvimento, a partir dos arquivos CSV anuais que o site publica
(Oracle's Elixir, [s.d.]; arquivos de 4 jul. 2026; Apêndice H), para comparar o *solo queue* de
elo alto com o cenário profissional.

Os dados são secundários e públicos, sem participação de sujeitos humanos
como fonte em nenhuma etapa.

### 4.4 ORGANIZAÇÃO E TRATAMENTO DE DADOS

Os dados foram organizados em um banco relacional PostgreSQL, descrito no
Quadro 1. O tratamento incluiu a normalização da partida
bruta de cada fonte, a extração das compras e vendas de itens a partir da
linha do tempo, com os desfazimentos de compra aplicados, e, na consulta, a reconciliação dos nomes de campeão entre a Riot API e o Oracle's Elixir,
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
validação foi cruzada e estratificada (Kohavi, 1995), com 5 dobras, e
mediu acurácia, precisão, *recall*, F1 e AUC-ROC. Depois de um modelo de
referência, os hiperparâmetros foram ajustados por *GridSearchCV*, do
scikit-learn (Pedregosa et al., 2011), otimizando a AUC-ROC. O modelo de
produção recebeu curva de calibração e explicações SHAP, globais e por
predição. Onze experimentos de enriquecimento testaram se outros sinais,
dez da linha do tempo e um de um endpoint de progressão do jogador,
melhoravam a previsão.

### 4.7 PROPOSTA DE VISUALIZAÇÃO E INTERFACE EM LINGUAGEM NATURAL

A camada de apresentação é uma aplicação web em React com TypeScript, que consome uma API própria em FastAPI, com seis páginas de visualização, descritas na Seção 5.5. As seis telas completas estão no Apêndice E (Figuras 6 a 11).

A interface em linguagem natural é um fluxo *text-to-SQL*: um modelo
de linguagem (Claude) traduz a pergunta em SQL, a consulta é validada
antes de executar (apenas `SELECT` ou `WITH...SELECT`, sobre uma lista fechada
de tabelas) e o resultado vem sempre do banco, nunca do conhecimento genérico do modelo; a explicação pode acrescentar, rotulada como "Leitura de jogo", uma nota de conhecimento geral. Antes da SQL, a pergunta é roteada para o *solo queue*, o competitivo ou ambos (regras sobre o esquema e, no resíduo, um modelo pequeno); a consulta não mistura as bases, tem no máximo uma nova tentativa após erro do banco e roda em transação somente leitura. A acurácia foi medida em um *benchmark* de 26 perguntas de referência, com SQL esperada, e em um gabarito automático de 203 perguntas, comparado por código (Apêndice B). A métrica de ambos é a acurácia de execução, que compara o resultado da consulta
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
6.1). Em 36 respostas auditadas, nenhum número estatístico estava fora dos dados fornecidos e todas terminaram com a ressalva de limites; afirmações qualitativas não foram avaliadas (Apêndice B). Antes da partida, o módulo também lê a composição e aponta a condição de vitória de cada time, sem usar a predição.

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
os objetivos específicos definidos na Seção 1.4.2 (Apêndice I).

### 5.1 Mapeamento de dados e recursos da Riot Games API (objetivo a)

Foram mapeados e utilizados os endpoints *league-v4*, *account-v1* e *match-v5* (partida e linha do tempo) da Riot Games API (Anexo A), além da documentação
técnica necessária para compreender limitações de taxa de requisição e
o ciclo de expiração da chave de desenvolvedor (24 horas). Esse
mapeamento orientou o desenho de um coletor resumível, capaz de operar
dentro dos limites de taxa e de retomar a coleta entre sessões sem
duplicar dados já salvos.

### 5.2 Estruturação da base de dados (objetivos b e c)

A base de modelagem reúne **39.188 partidas** de *solo queue* no corte de 15 minutos, provenientes das **39.426 partidas** que o banco tinha quando o conjunto de variáveis foi congelado. O banco guarda o JSON bruto de partida e linha do tempo para reprocessamento e **99.259 jogos profissionais** (2014-2026, Oracle's Elixir). O Quadro 1 resume as tabelas do banco. Os campos e as chaves de cada uma estão no Apêndice A.

Quadro — Tabelas do banco de dados e o que cada uma guarda

| Tabela | Conteúdo |
|---|---|
| `players` | jogadores de elo alto (Desafiante a Mestre), da *league-v4* |
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
as 41.063 partidas. O histórico das medições está no Apêndice D.

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
a assimetria com folga ([55,4%, 57,2%]). O padrão não se limita ao Brasil, mas as quatro regiões não o demonstram com a mesma força.

(Nota sobre as bases usadas nesta seção e na modelagem: a análise
descritiva foi medida sobre as **41.063 partidas** que o banco tem ao fim
da coleta. As variáveis e os modelos foram construídos antes da última
rodada da KR, sobre a base anterior de **39.426 partidas**, das quais
39.309 geraram variáveis preditoras e 39.188 chegam ao corte de 15 minutos. Por isso a Seção 5.4 e o Apêndice C citam 39.426. As 1.637 partidas de diferença,
quase todas da KR, são uma limitação declarada na Seção 6.1.)

**O viés é estável ao longo da partida.** Com amostras menores, parecia haver um pico no meio do jogo. A base ampliada não confirma essa forma. Entre as partidas empatadas em cada corte (diferença
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
(Oracle's Elixir, 99.259 jogos), o time azul venceu 53,2% das partidas,
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
Apêndice D. A Figura 1 mostra as duas comparações na tela Competitivo,
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
0,8477), e o XGBoost mantém a maior acurácia entre os três. Uma regressão
logística, usada como *baseline* simples, chega a 0,7631 de acurácia e 0,8483
de AUC-ROC (Apêndice C) e fica à frente do XGBoost por milésimos (0,0010 de AUC-ROC aos 15 minutos; o intervalo exclui zero aos 10, 15 e 20): o limite está na informação das variáveis, não na complexidade do modelo. O XGBoost foi mantido por ser a escolha anterior ao baseline e já sustentar a interface; trocá-lo não mudaria o resultado prático. Com um modelo treinado para cada
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
0,0060 aos 15 e 0,0031 aos 20) e salta para 0,0928 aos 25, cerca de 15 vezes o valor dos 15 minutos (Figura 2 e Apêndice J). É coerente com a mecânica do
jogo: as placas de defesa das torres caem por volta dos 14 minutos, e
antes disso destruir uma torre é raro e pouco informativo. É a
justificativa concreta para treinar um modelo *por fase* em vez de um
único modelo genérico. A calibração, preocupação conhecida em modelos de
*boosting* (Niculescu-Mizil; Caruana, 2005), não exigiu correção: o XGBoost já estava bem calibrado.

Figura — Importância média de cada variável (|SHAP|) nos quatro cortes temporais | reports/figuras_texto/fig_shap_fases.png

**Experimentos de enriquecimento.** Onze tentativas de enriquecer o conjunto de
variáveis não produziram ganho relevante (Quadro 5): refeitas na base congelada, dez deram no máximo +0,0007 de AUC-ROC; a 11, que não dá para refazer, deu −0,0031. Oito conjuntos novos (12 a 19) somaram no máximo +0,0080, com regressão logística, mantido treinando no passado e testando no futuro (Apêndice K). Já o volume de partidas deu ganho real: o AUC-ROC do
XGBoost subiu de 0,8214 (10.295 partidas) para 0,8393 (23.133) e para
0,8473 (39.188). Isso é consistente com um desempenho limitado mais pelo volume de dados do que
pela engenharia de novas variáveis, embora três pontos não bastem para
afirmá-lo.

Quadro — Experimentos negativos de enriquecimento de *features*

| # | Experimento | Δ AUC-ROC aos 15 e aos 25 min |
|---|---|---|
| 1 | Diferença de abates de Barão/Arauto | +0,0000 e −0,0000 |
| 2 | Dispersão espacial do time | −0,0000 e +0,0003 |
| 3 | Tuning específico por fase | +0,0001 e +0,0002 |
| 4 | Calibração adicional (sigmoide) | +0,0001 e +0,0001 |
| 5 | Ouro convertido em itens | +0,0001 e −0,0000 |
| 6 | Variáveis defensivas/ofensivas (ofensivas) | +0,0007 e +0,0000 |
| 7 | Ouro em itens (`item_gold_diff`) | +0,0001 e −0,0000 |
| 8 | Visão (ward_diff / ward_kill_diff) | −0,0000 e +0,0000 |
| 9 | Dragões por tipo (`monsterSubType`) | −0,0000 e +0,0000 |
| 10 | Placas de torre (`plate_diff`, `TURRET_PLATE_DESTROYED`) | +0,0000 e +0,0000 |
| 11 | Percentis comportamentais (`teamwork_pct_diff`/`expertise_pct_diff`, `lol-challenges-v1`) | −0,0031 e +0,0007 aos 15 min (n = 2.987); não refeito |

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
seis telas completas estão no Apêndice E.

Figura — Análise de partida: mapa de calor, diferença de ouro e objetivos até o minuto 14 | reports/figuras_texto/fig_partida.png

Figura — Simulador, aba Estado: probabilidade de vitória e contribuição de cada variável (SHAP) | reports/figuras_texto/fig_simulador_estado.png

### 5.6 Interface em linguagem natural (objetivo g)

A consulta em linguagem natural (*text-to-SQL* com validação e roteamento entre as bases) foi medida de duas formas (Apêndice B). No *benchmark* de 26 perguntas de referência, acertou 23 antes dos ajustes e 26 depois; como as regras do esquema foram escritas conhecendo as três falhas, o resultado não é independente.

Para sair do julgamento de uma só pessoa, a medida principal passou a ser um gabarito automático: cada pergunta nasce com a SQL de referência, escrita antes de qualquer execução, e um programa compara o resultado. O gerador produz as perguntas por template, e a medida usa 203, amostradas ao acaso. O sistema acertou **181 de 203 (89,2%)**, com intervalo de 95% de 84,1% a 92,7%: 166 de 187 perguntas respondíveis e 15 de 16 recusas esperadas.

As 22 falhas vêm de nomes de entidade escritos de outro modo pelo modelo ("Monkey King" no lugar de MonkeyKing), de eliminações lidas como kills mais assistências e de roteamento para a base errada; as duas correções feitas depois não foram medidas de ponta a ponta. Quando o banco não tem o dado, uma recusa determinística responde antes do modelo (15 de 16 recusas esperadas certas). O validador garante a segurança da consulta, não o seu sentido (Seção 6.1).

A Figura 5 mostra uma consulta na plataforma: a pergunta 9 do benchmark,
a SQL gerada pelo modelo, já validada, e o resultado lido do banco.

Figura — Consulta em linguagem natural: pergunta, SQL gerada e resultado | reports/figuras_texto/fig_nlq.png

### 5.7 Os resultados frente à literatura

Hodge et al. (2021) chegam a 85% de acurácia após 5 minutos em partidas
profissionais de *Dota 2*, mas tratam apenas da previsão. Este trabalho leva a
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
módulo de orientação que separa o dado real do conhecimento geral. Jiang et al. (2025) e Guo et al. (2024) motivam a consulta a dados estruturados por
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
forma sistemática (endpoints *league-v4*, *account-v1* e *match-v5*, com linha do tempo);

b) as informações relevantes de partidas, jogadores e estatísticas
foram identificadas e organizadas em um esquema relacional específico;

c) foi estruturado e executado um processo de coleta, tratamento e
organização capaz de escalar de um piloto de ~100 partidas para uma
base de 41.063 partidas de *solo queue* somadas a 99.259 jogos profissionais;

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

g) uma interface em linguagem natural foi implementada e avaliada: acertou 181 de 203 perguntas (89,2%) de um gabarito automático.

O achado que merece destaque, por não ter sido o objeto anunciado do
trabalho, é o viés de lado: uma assimetria estrutural entre os dois lados
do mapa, estatisticamente firme em três das quatro regiões coletadas
(BR1, EUW1, NA1; a KR tem intervalo de confiança que inclui 50%) e com
sinal invertido no jogo profissional. Ele é um fator de confusão que
qualquer modelo preditivo sobre *solo queue* precisa controlar, e a
inversão no circuito profissional sugere origem distinta no *solo queue*,
hipótese que este trabalho delimita sem comprovar. A incorporação dos
dados profissionais (Oracle's Elixir), além do escopo do TCC I, permitiu
ainda medir a diferença na conversão de vantagem material em vitória
entre os dois contextos.

### 6.1 LIMITAÇÕES E AMEAÇAS À VALIDADE

Registrar o que o trabalho não sustenta é parte da conclusão. Nenhuma das
limitações a seguir invalida os achados. Elas delimitam até onde eles
valem. O detalhe e os experimentos de cada uma estão no Apêndice F.

**Validade de construto.** A linha do tempo do *match-v5* não registra o estado das ondas
de *minions* nem a ordem de escolha de campeões (*draft*), e nenhuma API
pública da Riot expõe micro-posicionamento. Onze experimentos de
enriquecimento superaram as cinco variáveis originais em até +0,0007 de AUC (Quadro 5),
inclusive a posição dos jogadores, que existe na *timeline* e foi testada.
Variáveis mais ricas somam até +0,008 de AUC-ROC (Apêndice K); um ganho maior provavelmente depende do que a fonte não tem. Que parte do erro
do modelo venha dessa informação ausente é hipótese, não resultado medido.
Por isso nenhuma orientação da plataforma que dependa de itemização ou de
ondas vem do modelo, e a interface a marca como inferência geral.

**Validade externa.** Os resultados de *solo queue* vêm da fila ranqueada,
nas faixas Desafiante a Mestre, em cinco regiões, quatro delas com
amostra suficiente e desiguais entre si: BR1 e EUW1 concentram a maior
parte das partidas, e a KR tem intervalo que inclui 50%. O *patch* 16.13 concentra 40,4% da coleta. Não há base para estender as taxas por
lado nem a acurácia a outras filas, elos, versões ou jogos, ainda que a
arquitetura seja reaproveitável.

**Validade interna.** As partidas foram coletadas em janelas de tempo, sem amostragem ao longo de todo o histórico. Um padrão sazonal pode estar
confundido com o que os dados descrevem. Além disso, a validação cruzada sorteia
partidas ao acaso, e jogadores que se repetem entre partidas tornam as dobras menos independentes do que a técnica supõe. Treinar no passado e testar no futuro, porém, não reduziu a AUC-ROC (Apêndice C). Recortes finos, como um
jogador em um campeão ou um confronto de rota, seguem frágeis mesmo com
41.063 partidas, apesar do encolhimento estatístico (*shrinkage*) em
direção à média.

**Limitações do modelo.** A taxa-base do XGBoost no estado de empate total (49,0% a 51,4% conforme o corte) subestima o viés de lado medido nos dados (46,4% a 47,9%). A discrepância não é subajuste: a busca em grade completa ficou 0,0001 de AUC acima da produção, e apenas a troca para *Random Forest* a fecha (0,6 pp), ao custo de 0,0005 de AUC. O modelo usa 39.426 das 41.063 partidas e não foi retreinado, para não invalidar as validações. E o XGBoost não garante monotonicidade isolada por variável, por não usar restrição formal.

**Validade da consulta em linguagem natural.** A medida principal (203 perguntas de template, escritas por mim a partir de famílias de erro que já conhecia) pode superestimar o resultado em perguntas livres: em versões anteriores do sistema, perguntas escritas à mão acertaram entre 54% e 60%. As correções posteriores não foram medidas, e o *benchmark* de 26 não é independente.

### 6.2 TRABALHOS FUTUROS

Ficam registrados três caminhos. O primeiro é a extensão da predição para partidas ao vivo, prevista na arquitetura mas não implementada: a barreira é de dados em tempo real, não de modelo. O segundo é a extensão do recorte de validade externa, com outras filas e, eventualmente, outro jogo, para testar se o viés de lado descreve o jogo ou o modo de jogar de uma população específica. O terceiro é a melhoria da consulta em linguagem natural: verificação do resultado depois da execução, um gabarito maior com perguntas escritas à mão e um modelo aberto local para comparar com a API (Zhong; Yu; Klein, 2020).

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
1995. p. 1137-1143.

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
https://oracleselixir.com/tools/downloads. Acesso em: 4 jul. 2026.

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

WANG, Bailin; SHIN, Richard; LIU, Xiaodong; POLOZOV, Oleksandr; RICHARDSON, Matthew. RAT-SQL: relation-aware schema encoding and linking for text-to-SQL parsers. In:
Proceedings of the 58th Annual Meeting of the Association for Computational
Linguistics. Association for Computational Linguistics, 2020. p. 7567-7578.
DOI: 10.18653/v1/2020.acl-main.677.

ZHONG, Ruiqi; YU, Tao; KLEIN, Dan. Semantic evaluation for text-to-SQL with
distilled test suites. In: CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE
PROCESSING, 2020. **Proceedings of the 2020 Conference on Empirical Methods in
Natural Language Processing (EMNLP)**. [S. l.]: Association for Computational
Linguistics, 2020. p. 396-411. DOI: 10.18653/v1/2020.emnlp-main.29.

---

## APÊNDICE A – Esquema relacional do banco de dados

O banco de dados (PostgreSQL) segue o esquema do quadro a seguir. As
tabelas `raw_matches` e `raw_timelines` guardam o JSON bruto da Riot API,
para reprocessar sem nova coleta; as demais são a normalização relacional
usada pela análise e pela modelagem.

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

Em `item_events`, as compras e vendas já vêm com os desfazimentos
resolvidos, e `items` é o catálogo do Data Dragon, usado para resolver nome
e ícone de item. Índices B-tree cobrem as colunas mais usadas em filtro
(campeão, jogador, versão do jogo e liga), tanto para a API quanto para as
consultas geradas pela interface em linguagem natural.

---

## APÊNDICE B – Benchmark da interface em linguagem natural e auditoria do coach

Medição de 5 de novembro de 2026 sobre a base de produção de **41.063
partidas**: **26/26 = 100% de acurácia de execução**, pelo comando
`python -m src.nlq.evaluate_nlq`, que grava `reports/nlq_benchmark.json` com
a acurácia, a base, o modelo e o desfecho de cada pergunta. Esse resultado **não é independente**: as regras do esquema que corrigiram as três falhas foram escritas depois de conhecê-las. Até 3 de novembro, antes dos ajustes, o resultado era 23 de 26 (88%) em todas as execuções. A medida independente é o gabarito automático, descrito mais adiante.

Quadro — Execuções do benchmark de linguagem natural

| Execução | Base (partidas) | Resultado | Observação |
|---|---:|---:|---|
| 13 de julho de 2026 | não registrada | 23/26 | mesmas três falhas |
| 28 de setembro de 2026 | 24.154 | 23/26 | mesmas três falhas |
| 4 de outubro de 2026 | 41.063 | 23/26 | medida de referência; a execução anterior, sobre 39.426 partidas, deu o mesmo resultado |
| 3 de novembro de 2026 | 41.063 | 23/26 | mesmas três falhas, depois da correção da carga dos jogos profissionais (perguntas 23 a 26 seguem corretas) |
| 5 de novembro de 2026 | 41.063 | 26/26 | depois das regras novas do esquema e do roteador, escritas conhecendo as três falhas: **não é independente** |
| Durante a coleta | não registrada | 22/26 | falha extra na pergunta 3 (taxa de vitória do time azul): a contagem mudou entre a consulta gerada e a de referência, por escrita concorrente; sem a coleta, a pergunta voltou a passar |

As 26 perguntas de referência, com a SQL esperada e o resultado da medição
de referência:

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

As três falhas (perguntas 5, 12 e 22) pertencem à mesma família: todas
envolvem um limiar mínimo de jogos ("com pelo menos N partidas") e erram na
formatação da resposta, por coluna extra ou apresentação, sem erro de
interpretação da pergunta nem de estrutura da SQL.

**Gabarito automático (medida principal, 5 de novembro de 2026).** Um gerador (`src/nlq/gerar_gabarito.py`) monta perguntas por templates sobre entidades reais do banco (campeões, equipes, ligas, patches, jogadores e itens) e escreve, junto de cada uma, a SQL de referência, que é executada na hora; pergunta com gabarito vazio, com empate no limite de um ranking ou repetida é descartada. Parte das perguntas não tem resposta no banco (primeiro sangue, série, ouro aos 10 minutos, dano a estruturas) e espera uma recusa. O sistema roda as perguntas pelo caminho do produto e `src/nlq/avaliar_gabarito.py` compara: em escalar, algum valor da primeira linha bate com o do gabarito (tolerância de 0,1%, fração ou percentual); em ranking, a chave de cada linha do gabarito aparece na mesma posição; recusa esperada só passa se toda base consultada recusou; resposta na base errada falha. A comparação não depende de avaliador, e as regras estão no cabeçalho do módulo e em `tests/test_avaliar_gabarito.py`. O conjunto avaliado tem 203 perguntas, amostradas ao acaso: **181 de 203 certas (89,2%)**, intervalo de 95% de 84,1% a 92,7%. Falhas: 16 valores diferentes do gabarito, 2 recusas indevidas, 3 roteamentos para a base errada e 1 resposta onde o banco não tem o dado. Li as 22 uma a uma: todas são do sistema, nenhuma do gabarito ou do comparador. A maior família foi nome de entidade (o modelo escrevia 'Monkey King' para MonkeyKing, tratava ligas como equipe, trocava LPLOL por LPL), seguida de eliminações lidas como kills mais assistências. Duas correções (`src/nlq/entidades.py` e uma checagem que refaz a consulta) vieram depois da medida e não foram medidas de ponta a ponta. Limites: o texto é de template, o autor conhecia as famílias de erro e as famílias pequenas têm poucas perguntas. Artefatos: `docs/nlq_gabarito_203.json`, `reports/nlq_gabarito_bruto_parte1.json` a `3.json`, `reports/nlq_gabarito_resultado_203.json`.

Quadro — Acerto do gabarito automático por família de pergunta

| Família | Base | Certas | Total | % |
|---|---|---:|---:|---:|
| C1-winrate-equipe | competitivo | 14 | 16 | 87,5 |
| C10-contagem | competitivo | 4 | 4 | 100,0 |
| C11-lado | competitivo | 1 | 1 | 100,0 |
| C12-posicao | competitivo | 2 | 2 | 100,0 |
| C2-jogos-equipe | competitivo | 5 | 5 | 100,0 |
| C3-media-equipe | competitivo | 13 | 14 | 92,9 |
| C4-liga | competitivo | 8 | 12 | 66,7 |
| C5-jogador | competitivo | 14 | 16 | 87,5 |
| C6-campeao-pro | competitivo | 13 | 13 | 100,0 |
| C7-patch | competitivo | 2 | 2 | 100,0 |
| C8-ranking | competitivo | 3 | 3 | 100,0 |
| C9-ano | competitivo | 8 | 8 | 100,0 |
| S1-winrate-campeao | solo | 11 | 14 | 78,6 |
| S10-plataforma | solo | 3 | 3 | 100,0 |
| S12-itens | solo | 6 | 6 | 100,0 |
| S14-kda | solo | 2 | 3 | 66,7 |
| S15-posicao-campeao | solo | 6 | 6 | 100,0 |
| S16-visao | solo | 2 | 2 | 100,0 |
| S2-partidas-campeao | solo | 12 | 12 | 100,0 |
| S3-media-campeao | solo | 13 | 18 | 72,2 |
| S4-top-campeoes-posicao | solo | 8 | 10 | 80,0 |
| S5-mais-jogado-posicao | solo | 3 | 3 | 100,0 |
| S6-lado | solo | 2 | 2 | 100,0 |
| S7-duracao | solo | 1 | 1 | 100,0 |
| S8-bans | solo | 8 | 9 | 88,9 |
| S9-campeoes-wr | solo | 2 | 2 | 100,0 |
| U1-primeiro | competitivo | 6 | 6 | 100,0 |
| U2-serie | competitivo | 2 | 2 | 100,0 |
| U3-minuto | competitivo | 1 | 1 | 100,0 |
| U4-dano-visao | competitivo | 2 | 2 | 100,0 |
| U5-ban-pro | competitivo | 1 | 2 | 50,0 |
| U6-draft | competitivo | 1 | 1 | 100,0 |
| U7-itens-pro | competitivo | 1 | 1 | 100,0 |
| U8-multikill | solo | 1 | 1 | 100,0 |

Auditoria do coach, de 4 de novembro de 2026: 36 respostas do módulo de orientação estratégica, geradas pelo mesmo caminho do produto sobre partidas reais (12 de cada modo: partida completa, composição e só estado; cortes de 15, 20 e 25 minutos). Cada número da resposta foi conferido contra os dados fornecidos à IA (o prompt sem as instruções), e os 13 que o detector não encontrou nos dados foram revisados à mão. A saída da IA varia entre execuções (temperatura 0,4), e o quadro é de uma execução. Comando: `python -m src.coach.audit_grounding --n 36`; artefatos: `reports/coach_audit.json` e `reports/coach_audit_revisao.json`.

Quadro — Auditoria de fundamentação do coach (36 respostas)

| Medida | Resultado |
|---|---|
| Respostas auditadas | 36 (12 por modo) |
| Números nas respostas | 453, dos quais 87 de tempo de jogo ou formato |
| Não encontrados nos dados | 13, em 9 respostas |
| Estatística inventada, após a revisão | 0 (8 derivados dos dados, 2 de formato, 3 limiares de conhecimento geral) |
| Porcentagens com correspondente nos dados | 167 de 167 |
| Contagens de jogos ou partidas com correspondente | 52 de 52 |
| Ressalva final de limites | 36 de 36 (35 pelo detector, 1 por leitura) |
| Itens sugeridos que vêm da lista real fornecida | 87 de 87 |

A auditoria mede número, não afirmação qualitativa nem a correção do conhecimento geral. No caso 5, por exemplo, a resposta diz que dois campeões estão "muito atrasados em ouro e experiência", mas nesse modo os dados trazem só a diferença do time. Dos três limiares de conhecimento geral, o de "4-5k de ouro" num cenário hipotético é o mais limítrofe.

---

## APÊNDICE C – Métricas completas por corte temporal

O quadro reúne os três modelos nos quatro cortes, com validação cruzada
estratificada de 5 dobras (semente 42) sobre a base de 39.426 partidas. Os
valores do corte de 15 minutos são os do Quadro 3.

Quadro — Métricas completas por corte temporal, comparação entre os três modelos

| Corte | n | Taxa vitória azul | Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 10 min | 39.309 | 0,466 | *Random Forest* | 0,6704 | 0,6515 | 0,6301 | 0,6406 | 0,7341 |
| 10 min | 39.309 | 0,466 | **XGBoost** | 0,7004 | 0,6912 | 0,6461 | 0,6679 | 0,7742 |
| 10 min | 39.309 | 0,466 | MLP | 0,7020 | 0,6861 | 0,6651 | 0,6755 | 0,7735 |
| 15 min | 39.188 | 0,466 | *Random Forest* | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |
| 15 min | 39.188 | 0,466 | **XGBoost** | 0,7621 | 0,7561 | 0,7228 | 0,7391 | 0,8473 |
| 15 min | 39.188 | 0,466 | MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| 20 min | 34.337 | 0,466 | *Random Forest* | 0,7785 | 0,7659 | 0,7551 | 0,7604 | 0,8623 |
| 20 min | 34.337 | 0,466 | **XGBoost** | 0,7917 | 0,7817 | 0,7666 | 0,7741 | 0,8762 |
| 20 min | 34.337 | 0,466 | MLP | 0,7866 | 0,7712 | 0,7701 | 0,7707 | 0,8729 |
| 25 min | 26.837 | 0,467 | *Random Forest* | 0,8147 | 0,8047 | 0,7969 | 0,8008 | 0,8975 |
| 25 min | 26.837 | 0,467 | **XGBoost** | 0,8241 | 0,8172 | 0,8034 | 0,8103 | 0,9090 |
| 25 min | 26.837 | 0,467 | MLP | 0,8240 | 0,8171 | 0,8033 | 0,8101 | 0,9072 |

Quadro — Configuração dos três modelos comparados

| Modelo | Configuração | Origem |
|---|---|---|
| XGBoost | 500 árvores, taxa de aprendizado 0,01, profundidade 3 | busca em grade sobre a base de 10.295 partidas, mantida na base final (2º lugar entre 27 combinações) |
| *Random Forest* | 500 árvores, demais parâmetros do scikit-learn | configuração de referência, sem busca em grade |
| MLP | camadas de 64 e 32 neurônios, variáveis padronizadas, até 500 iterações | configuração de referência, sem busca em grade |

O comando que regenera o quadro de métricas é
`python -m src.models.multi_cutoff_metrics`, que grava
`reports/metricas_corte.json`.

Quadro — Regressão logística como baseline e diferença do XGBoost para os demais modelos

| Corte | Modelo | Acurácia | AUC-ROC | AUC-ROC do XGBoost menos a do modelo (IC de 95%) |
|---|---|---:|---:|---|
| 10 min | Regressão logística | 0,7016 | 0,7748 | −0,0006 (−0,0011 a −0,0002) |
| 15 min | Regressão logística | 0,7631 | 0,8483 | −0,0010 (−0,0014 a −0,0006) |
| 15 min | MLP | 0,7610 | 0,8455 | +0,0019 (+0,0011 a +0,0026) |
| 15 min | *Random Forest* (referência) | 0,7457 | 0,8277 | +0,0197 (+0,0180 a +0,0215) |
| 20 min | Regressão logística | 0,7933 | 0,8771 | −0,0009 (−0,0012 a −0,0006) |
| 25 min | Regressão logística | 0,8248 | 0,9091 | −0,0002 (−0,0006 a +0,0003) |

O baseline é uma regressão logística com as variáveis padronizadas. Os
intervalos vêm de *bootstrap* pareado (1.000 reamostragens das mesmas
partidas para os dois modelos), sobre as previsões fora da amostra da
validação cruzada de 5 dobras. Na acurácia, a diferença do XGBoost para a
regressão logística fica entre −0,0007 e −0,0016, com intervalo que inclui
zero aos 10, 15 e 25 minutos. Todas as diferenças são de milésimos, exceto a
da *Random Forest* de referência, que a busca em grade elimina (Seção 5.4).
O comando é `python -m src.models.baseline_e_diferencas`, que grava
`reports/baseline_e_diferencas.json`.

Quadro — Validação cruzada com 5 e com 10 dobras

| Corte | Modelo | Acurácia (5 dobras) | Acurácia (10 dobras) | AUC-ROC (5 dobras) | AUC-ROC (10 dobras) |
|---|---|---:|---:|---:|---:|
| 10 min | XGBoost | 0,7004 | 0,7010 | 0,7742 | 0,7741 |
| 15 min | XGBoost | 0,7621 | 0,7619 | 0,8473 | 0,8474 |
| 15 min | *Random Forest* | 0,7457 | 0,7459 | 0,8277 | 0,8273 |
| 15 min | MLP | 0,7610 | 0,7612 | 0,8455 | 0,8449 |
| 20 min | XGBoost | 0,7917 | 0,7913 | 0,8762 | 0,8763 |
| 25 min | XGBoost | 0,8241 | 0,8249 | 0,9090 | 0,9090 |

O número de dobras recomendado por Kohavi (1995) é 10. A diferença para as 5
usadas no trabalho é de no máximo 0,0008 em acurácia e 0,0006 em AUC-ROC, e
não altera nenhuma conclusão. O comando é
`python -m src.models.robustez_dobras`, que grava
`reports/robustez_dobras.json`.

Quadro — Treino no passado e teste no futuro, XGBoost

| Corte | Divisão | Treino | Teste | Acurácia | AUC-ROC | IC 95% da AUC-ROC |
|---|---|---:|---:|---:|---:|---|
| 10 min | Cronológica 80/20 | 31.447 | 7.862 | 0,7038 | 0,7789 | 0,7691 a 0,7888 |
| 10 min | Por *patch* | 23.457 | 15.852 | 0,7080 | 0,7832 | 0,7763 a 0,7905 |
| 10 min | Aleatória 80/20 | 31.447 | 7.862 | 0,7008 | 0,7723 | 0,7631 a 0,7834 |
| 15 min | Cronológica 80/20 | 31.350 | 7.838 | 0,7710 | 0,8545 | 0,8458 a 0,8629 |
| 15 min | Por *patch* | 23.376 | 15.812 | 0,7679 | 0,8542 | 0,8483 a 0,8598 |
| 15 min | Aleatória 80/20 | 31.350 | 7.838 | 0,7573 | 0,8432 | 0,8330 a 0,8517 |
| 20 min | Cronológica 80/20 | 27.469 | 6.868 | 0,7989 | 0,8829 | 0,8750 a 0,8897 |
| 20 min | Por *patch* | 20.609 | 13.728 | 0,7981 | 0,8810 | 0,8749 a 0,8864 |
| 20 min | Aleatória 80/20 | 27.469 | 6.868 | 0,7964 | 0,8814 | 0,8731 a 0,8890 |
| 25 min | Cronológica 80/20 | 21.469 | 5.368 | 0,8333 | 0,9142 | 0,9072 a 0,9213 |
| 25 min | Por *patch* | 16.442 | 10.395 | 0,8277 | 0,9120 | 0,9065 a 0,9172 |
| 25 min | Aleatória 80/20 | 21.469 | 5.368 | 0,8295 | 0,9111 | 0,9034 a 0,9182 |

Na divisão cronológica, as 80% mais antigas treinam e as 20% mais recentes testam; na divisão por *patch*, os *patches* 16.10 a 16.13 treinam e
os 16.14 a 16.19 testam; na aleatória, o teste tem o mesmo tamanho do
cronológico. A pior diferença de AUC-ROC de uma divisão temporal para a
aleatória é de −0,0004 (20 minutos, por *patch*), dentro do intervalo de
confiança, de modo que misturar épocas na validação cruzada não infla o
resultado. Esta é a resposta ao aviso de Kaufman et al. (2012) sobre dados que
mudam com o tempo. A regressão logística dá o mesmo padrão, com diferença de
até 0,0012 de AUC-ROC para o XGBoost em todas as divisões. A ressalva é que a
região se mistura ao tempo: aos 15 minutos, o teste cronológico tem
49,7% de NA1 e nenhuma partida de BR1, que é 37,7% do treino. O resultado vale
também para uma composição regional diferente da do treino, mas não separa o
efeito do tempo do efeito da região. O comando é
`python -m src.models.holdout_temporal`, que grava
`reports/holdout_temporal.json`.

---

## APÊNDICE D – Proveniência das medições da Seção 5.3

Quadro — Partidas por região na primeira e na última medição do viés de lado

| Região | Primeira medição (6 de julho de 2026) | Última medição (4 de outubro de 2026) | Observação |
|---|---:|---:|---|
| BR1 | 11.936 | 11.936 | não mudou em nenhum dos quatro levantamentos |
| EUW1 | 1.307 | 11.744 | |
| NA1 | 1.367 | 7.159 | 1.446 antes da rodada final; a taxa do vermelho passou de 51,9% para 52,2% |
| KR | 1.308 | 10.204 | |

A direção do achado, com o vermelho acima de 50% nas quatro regiões, se
manteve nas quatro medições. A NA1, que era a região mais frágil para a
generalização, deixou de ser limitação.

Quadro — Origem dos números da Seção 5.3

| Número e base | Script (em `docs/`) | Artefato (em `reports/`) |
|---|---|---|
| Vitória do vermelho por região (Quadro 2), sobre 41.063 partidas | consulta SQL agregada por partida, na checagem 6 de `verifica_tcc.py` | `stats_regions.txt` |
| Vitória do azul em partidas empatadas, por corte, sobre as variáveis congeladas (39.309 partidas) | `taxa_base_por_corte.py` | `taxa_base_por_corte.json` |
| Comparação de pares com correção de Holm, sobre as variáveis congeladas | `testa_diferenca_taxas.py` | saída no terminal |
| Vitória do azul por faixa de duração, sobre 41.063 partidas | `testa_faixa_duracao.py` | `faixa_duracao.json` |
| Conversão de vantagem de ouro, sobre as variáveis congeladas (39.188 aos 15 minutos) | `confere_conversao_advantagem.py` | lê `features_phases.csv`, em `data/` |
| Série anual do cenário profissional, sobre 99.259 jogos | consulta SQL em `pro_games` | |

Quadro — Vitória do azul por faixa de duração total da partida

| Duração total | Partidas | Vitória do azul |
|---|---:|---:|
| 0 a 25 min | 15.944 | 46,5% |
| 25 a 30 min | 13.314 | 47,3% |
| 30 a 35 min | 8.364 | 46,4% |
| 35 a 40 min | 2.684 | 45,6% |
| acima de 40 min | 757 | 47,0% |

A amplitude é de 1,7 ponto percentual, e todas as faixas ficam abaixo de
50%. A medição é de 4 de outubro de 2026, sobre as 41.063 partidas.

Quadro — Vitória do azul por ano no cenário profissional

| Ano | Azul | Ano | Azul |
|---|---:|---|---:|
| 2014 | 58,2% | 2021 | 52,6% |
| 2015 | 55,0% | 2022 | 52,5% |
| 2016 | 53,5% | 2023 | 53,3% |
| 2017 | 55,0% | 2024 | 53,1% |
| 2018 | 53,6% | 2025 | 53,2% |
| 2019 | 53,2% | 2026 | 53,1% |
| 2020 | 52,7% | Todos os anos | 53,2% |

Os anos de 2014 e 2015 divergem, mas se apoiam em 814 e 1.806 jogos, contra
99.259 no total, e a diferença é atribuída a esse volume menor, não a uma
mudança no padrão.

---

## APÊNDICE E – Telas completas da plataforma

As seis telas da plataforma, inteiras, das quais a Seção 5 mostra recortes.
Foram capturadas com a API e a interface rodando localmente sobre as 41.063
partidas do Quadro 2, em tema escuro, com 1440 px de largura e altura
ajustada à página. Os comandos que geram as capturas estão em
`docs/comandos.md`.

| Arquivo | Página |
|---|---|
| `reports/anexo_a/01_inicio.png` | Início (busca unificada) |
| `reports/anexo_a/02_dashboard.png` | Dashboard (KPIs, viés de lado por região, cobertura do dataset) |
| `reports/anexo_a/03_campeoes.png` | Campeões |
| `reports/anexo_a/04_partida_detalhe.png` | Partidas: análise de uma partida individual |
| `reports/anexo_a/05_competitivo.png` | Competitivo (solo queue × profissional) |
| `reports/anexo_a/06_simulador.png` | Simulador, aba Estado |

---

## APÊNDICE F – Limitações em detalhe

O quadro a seguir reúne a evidência medida para cada limitação resumida na
Seção 6.1; os dois seguintes detalham a discrepância de taxa-base do
modelo.

Quadro — Limitações do trabalho e a evidência de cada uma

| Limitação | Evidência medida | Tratamento |
|---|---|---|
| Taxa-base do modelo no estado de empate | O modelo prevê 49,0% a 51,4% para o azul, e os dados dão 46,4% a 47,9% | Discrepância de 1,7 a 4,7 pontos percentuais; não é subajuste (quadros seguintes). Mantido o XGBoost |
| Última rodada de coleta fora do treino | Treino com 39.426 das 41.063 partidas do banco. Das 1.754 partidas do banco sem variáveis, 1.647 são da KR e 107 de BR1, EUW1 e NA1; 117 da base congelada também não geraram linha | Não retreinado: o desempenho do modelo atual está medido e validado (Apêndice C e bateria comportamental), e retreinar invalidaria as duas. Quem quiser o modelo sobre a base completa reexecuta `train_baseline` e `export_model` |
| Teto de desempenho das variáveis atuais | Onze experimentos sem ganho, dez sobre a linha do tempo e um sobre o endpoint de progressão do jogador. A posição dos jogadores existe na linha do tempo e foi testada (experimento 2). Os experimentos 12 a 19, com 59 variáveis novas, somam até +0,0080 de AUC-ROC aos 15 minutos (Apêndice K) | O ganho maior provavelmente depende de dado que a API pública não fornece: a ordem de escolha de campeões (*draft*) e o estado das ondas de *minions*. O histórico do jogador não acrescenta ao estado de jogo |
| Ausência de micro-posicionamento | Nenhuma API pública da Riot expõe movimentação de *minions* nem controle de onda | Replays (`.rofl`) e visão computacional sobre o minimapa foram considerados, mas não implementados |
| Desequilíbrio de amostra por região | BR1 11.936, EUW1 11.744, KR 10.204 e NA1 7.159 partidas (a NA1 tinha 1.446 antes da rodada final). Em três das quatro regiões o intervalo de 95% exclui 50%; a KR tem 50,4%, com intervalo que inclui 50% | O achado de viés de elo alto, além do Brasil, se apoia nas três regiões com evidência firme |
| Cobertura desigual por versão do jogo | O *patch* 16.13 concentra 40,4% das partidas (16.572 de 41.063), em dez *patches* de 16.10 a 16.19 | Treinar nos *patches* 16.10 a 16.13 e testar nos 16.14 a 16.19 não reduz a AUC-ROC (Apêndice C). A generalização para versões com balanceamento muito diferente segue sem medida |
| Monotonicidade isolada por variável | O XGBoost não garante que aumentar apenas a diferença de abates ou de torres nunca reduza a probabilidade prevista, por interações e redundâncias entre variáveis | Comportamento documentado e compreendido, sem restrição formal de monotonicidade (`monotone_constraints`) nesta versão |
| Consulta em linguagem natural | 181 de 203 (89,2%, intervalo de 95% de 84,1% a 92,7%) em gabarito automático de template; *benchmark* de 26 ajustado pelo autor, sem independência | Falhas declaradas e sem ajuste depois da medida; consulta em transação somente leitura. Verificação do resultado depois da execução fica como trabalho futuro |

Quadro — Taxa de vitória do azul no estado de empate, modelo e dados

| Corte | Modelo (empate total) | Dados (partidas empatadas) | Diferença |
|---|---:|---:|---:|
| 10 min | 49,2% | 46,4% | 2,8 pp |
| 15 min | 49,6% | 47,9% | 1,7 pp |
| 20 min | 51,4% | 46,7% | 4,7 pp |
| 25 min | 49,0% | 47,1% | 1,9 pp |

A série do modelo é plana, sem o pico de meio de jogo que amostras menores sugeriam. As duas séries não concordam em
magnitude, nem sempre em direção: aos 20 minutos o modelo favorece o azul
(51,4%), enquanto os dados favorecem o vermelho (46,7% de vitória do azul).

Quadro — Alavancas testadas contra a discrepância de taxa-base

| Alavanca | Resultado | Leitura |
|---|---|---|
| Busca em grade completa (27 combinações, 5 dobras) | Escolhe a mesma profundidade da produção (3); AUC de 0,8475 contra 0,8473, com a produção em 2º lugar | Ajuste equivalente: a discrepância não é subajuste |
| Calibração sigmoidal | Piora o desvio, de 1,7 para 2,3 pp | O estado de empate total fica fora da distribuição observada, e o calibrador o extrapola para perto de 50% |
| Regularização alternativa | Move o desvio dentro do ruído | Sem efeito |
| *Random Forest* de 500 árvores e profundidade 6 | Leva o desvio a 0,6 pp | Custa 0,0005 de AUC, e a acurácia fica em 0,7617 contra 0,7621. Não adotada, porque o critério de escolha foi a acurácia aos 15 minutos; a decisão é reversível e dispensa retreino |

A discrepância é, portanto, uma propriedade da função que o XGBoost aprende
neste recorte; não é um déficit de ajuste. Comando e artefato:
`docs/experimento_calibracao.py` e
`reports/experimento_calibracao_veredito.json`.

---

## APÊNDICE G – Fundamentos dos métodos usados

O quadro resume, para cada método, o papel que ele tem neste trabalho, a propriedade que justifica o uso e o limite que o próprio autor da obra ou a medição deste trabalho aponta. As referências completas estão na lista de Referências.

Quadro — Fundamentos dos métodos usados e o limite de cada um

| Método | Papel neste trabalho | Propriedade que o justifica | Limite |
|---|---|---|---|
| *Random Forest* (Breiman, 2001) | Classificador comparado | *Bagging* com seleção aleatória de variáveis em cada nó, o que reduz a correlação entre as árvores | As variáveis preditoras evoluem juntas na partida, o que limita o ganho do conjunto |
| XGBoost (Chen; Guestrin, 2016) | Modelo de produção | Árvores em sequência, cada uma ajustada ao resíduo das anteriores, com otimização de segunda ordem e regularização | Não garante monotonicidade isolada por variável |
| Rede neural MLP (Hornik; Stinchcombe; White, 1989) | Classificador comparado | Aproximação universal: captura interações sem especificá-las | Exige mais dados e cuidado com escala e regularização |
| Dados tabulares (Grinsztajn; Oyallon; Varoquaux, 2022) | Motivo de comparar árvores e redes | Árvores seguem competitivas em amostras de cerca de 10 mil exemplos | A diferença diminui em amostras maiores |
| LIME (Ribeiro; Singh; Guestrin, 2016) | Alternativa não adotada | Modelo linear local, simples de ler | Pouco fiel se o modelo for muito não linear na vizinhança |
| SHAP (Lundberg; Lee, 2017) | Explicação por variável, global e por previsão | Valor de Shapley: atribuição aditiva com consistência e importância nula para variável ausente | Explica o modelo, não o jogo |
| AUC-ROC (Hanley; McNeil, 1982) | Métrica ao lado da acurácia | Equivale à probabilidade de um caso positivo receber pontuação maior que um negativo | Mede discriminação, não calibração |
| Calibração (Niculescu-Mizil; Caruana, 2005) | Curva de calibração do modelo de produção | Calibração é preocupação conhecida em modelos de *boosting* | Não exigiu correção neste trabalho |
| Validação cruzada estratificada (Kohavi, 1995) | Cinco dobras, semente 42 | Estima o desempenho com a proporção de classes preservada | O autor recomenda 10 dobras; a diferença para 5 é de até 0,0008 (Apêndice C) |
| Vazamento de dados (Kaufman et al., 2012) | Variáveis só do estado até o corte | Prever com informação que não existiria no momento da previsão invalida o resultado | A coleta pode ter viés de seleção, não medido |
| Intervalo de Wilson (Brown; Cai; DasGupta, 2001) | Intervalo de confiança das proporções | Funciona melhor que o intervalo usual em amostras menores | Supõe observações independentes |
| Correção de Holm (Holm, 1979) | Comparação de pares de cortes | Controla a multiplicidade quando várias diferenças são testadas | Controla o erro do conjunto de testes, com menos perda de poder que a correção de Bonferroni |
| Esquema no *text-to-SQL* (Wang et al., 2020) | Contexto da consulta gerada | Representar o esquema com os relacionamentos entre tabelas melhora a precisão da conversão | Consulta correta na forma pode responder à pergunta errada |
| Acurácia de execução (Zhong; Yu; Klein, 2020) | Métrica do *benchmark* de linguagem natural | Compara o resultado da consulta gerada com o da consulta de referência | Propõem avaliar sobre vários bancos de teste, o que o *benchmark* feito sobre uma base não faz |

---

## APÊNDICE H – Procedência dos dados e chaves da Riot Games API

O primeiro quadro reúne medições sobre a composição das duas bases, feitas em 3 de novembro de 2026, sobre as 41.063 partidas e os 99.259 jogos descritos na Seção 4.3. As consultas estão registradas em `docs/conferencia_referencias.md`. O segundo quadro resume os tipos de chave da Riot Games API, conforme o portal de desenvolvedores consultado na mesma data.

Quadro — Composição das bases de dados

| Aspecto | Medida | Observação |
|---|---|---|
| Jogos profissionais nos arquivos | 99.259 jogos únicos, de 122 ligas | Arquivos do Oracle’s Elixir de 4 de julho de 2026 |
| Concentração por liga | 40,0% em 22 ligas principais e 60,0% nas outras 100 | As outras são de desenvolvimento, acadêmicas e regionais |
| Vitória do azul por grupo de ligas | 53,4% nas principais e 53,0% nas demais | A conclusão não depende da mistura |
| Carga no banco | 2.543 jogos perdidos por erro do carregador, corrigido | O carregador apagava por ano do arquivo; agora apaga por jogo |
| Jogadores da tabela `players` | 60.680, dos quais 93% de Mestre | A semeadura incluiu a faixa Mestre |
| Partidas com ao menos um Desafiante ou Grão-Mestre | 97,2% das 41.063 | Média de 5,4 jogadores desses elos por partida |
| Partidas só com jogadores de Mestre | 2,8% (1.163), das quais 769 na KR | Na KR, a última rodada de coleta desceu no ladder |
| Elo dos participantes com elo conhecido | 25% Desafiante, 31% Grão-Mestre e 44% Mestre | Elo da tabela `players`, não o da data da partida |

Quadro — Tipos de chave da Riot Games API

| Tipo | Como obter | Limite de requisições | APIs | Validade |
|---|---|---|---|---|
| Desenvolvimento | Concedida ao entrar no portal | Não informado | Não informado | Desativa a cada 24 horas |
| Pessoal | Registro do produto, sem verificação | 20 por segundo e 100 por 2 minutos | APIs padrão | Não informada |
| Produção | Registro do projeto, em geral com protótipo, e aprovação | A partir de 500 por 10 segundos e 30.000 por 10 minutos, ampliável | APIs padrão e API de torneios | Não informada |

---

## APÊNDICE I – Objetivos, evidências e onde estão

Quadro — Objetivos específicos, onde são tratados e a evidência de cada um

| Objetivo | Seção | Evidência |
|---|---|---|
| a | 5.1 e Anexo A | Endpoints *league-v4*, *account-v1* e *match-v5*; coletor resumível e dentro dos limites de taxa |
| b | 5.2 e Apêndice A | Quadro 1: onze tabelas relacionais para partidas, jogadores, estatísticas, itens e jogos profissionais |
| c | 4.3 e 5.2 | 41.063 partidas de *solo queue* e 99.259 jogos profissionais; coleta e carga re-executáveis |
| d | 5.3 e Apêndice D | Quadro 2 e viés de lado com quatro testes de robustez; inversão no profissional; conversão de vantagem |
| e | 5.4 e Apêndice C | Quadros 3 e 4: três modelos comparados em quatro cortes; XGBoost em produção |
| f | 5.5 e Apêndice E | Seis páginas de visualização; Figuras 3 e 4 no texto |
| g | 5.6 e Apêndice B | 181 de 203 perguntas certas (89,2%) no gabarito automático |

---

## APÊNDICE J – Importância das variáveis por corte

Valor médio absoluto do SHAP de cada variável, no modelo XGBoost de cada corte. Artefato: `reports/shap_importance_phases.json`.

Quadro — Importância média das variáveis (valor absoluto do SHAP) por corte

| Variável | 10 min | 15 min | 20 min | 25 min |
|---|---:|---:|---:|---:|
| Diferença de ouro | 0,6643 | 0,8989 | 1,0693 | 1,0642 |
| Diferença de experiência | 0,2741 | 0,4073 | 0,4855 | 0,8104 |
| Diferença de abates | 0,0209 | 0,0680 | 0,0166 | 0,0028 |
| Diferença de torres | 0,0044 | 0,0060 | 0,0031 | 0,0928 |
| Diferença de dragões | 0,1879 | 0,2267 | 0,2650 | 0,2567 |

---

## APÊNDICE K – Experimentos de precisão

Experimentos 1 a 19, todos sobre a mesma base congelada de 39.426 partidas, com o mesmo protocolo (validação cruzada estratificada de 5 dobras, semente 42). Os experimentos 1 a 10, do Quadro 5, foram refeitos em 4 de novembro de 2026: tinham sido medidos antes, com bases de tamanhos diferentes e sem intervalo de confiança. O 11 não pôde ser refeito (adiante). Todas as variáveis vêm de `frames[: corte + 1]` da linha do tempo; as de campeão e de jogador usam só informação anterior à partida (teste `tests/test_features_v2_sem_vazamento.py`, 703 pares de partida e corte sem vazamento). O ganho é a diferença de AUC-ROC contra o XGBoost de produção com as cinco variáveis originais (0,8476 aos 15 minutos e 0,9089 aos 25 nesta base), com intervalo de 95% por *bootstrap* pareado.

Quadro — Experimentos 1 a 10: ganho de AUC-ROC contra as cinco variáveis originais

| Exp. | Variáveis acrescentadas | 15 minutos | 25 minutos |
|---|---|---|---|
| 1 | Diferença de abates de Barão e Arauto (2 variáveis, as mesmas do conjunto 14) | +0,0000 (+0,0000 a +0,0000) | −0,0000 (−0,0000 a +0,0000) |
| 2 | Dispersão espacial: distância média dos jogadores ao centro do time (1) | −0,0000 (−0,0000 a +0,0000) | +0,0003 (+0,0001 a +0,0004) |
| 3 | Tuning por fase: grade de 18 combinações escolhida só no treino (nenhuma variável nova) | +0,0001 (−0,0001 a +0,0003) | +0,0002 (−0,0000 a +0,0004) |
| 4 | Calibração sigmoide sobre o XGBoost de produção | +0,0001 (−0,0000 a +0,0002) | +0,0001 (−0,0000 a +0,0003) |
| 4 | Calibração isotônica sobre o XGBoost de produção | −0,0002 (−0,0003 a +0,0000) | −0,0001 (−0,0003 a +0,0001) |
| 5 e 7 | Valor em ouro dos itens finalizados que cada time possui (1) | +0,0001 (+0,0000 a +0,0002) | −0,0000 (−0,0001 a +0,0000) |
| 6 | Atributos ofensivos: dano de ataque, poder de habilidade, velocidade de ataque (3) | +0,0007 (+0,0004 a +0,0009) | +0,0000 (−0,0000 a +0,0001) |
| 6 | Atributos defensivos: armadura, resistência mágica, vida (3) | +0,0001 (−0,0001 a +0,0003) | +0,0001 (−0,0000 a +0,0003) |
| 8 | Visão: sentinelas colocadas e destruídas (2) | −0,0000 (−0,0001 a −0,0000) | +0,0000 (−0,0000 a +0,0000) |
| 9 | Dragões por tipo (7) | −0,0000 (−0,0001 a +0,0000) | +0,0000 (−0,0000 a +0,0001) |
| 10 | Placas de torre destruídas (1) | +0,0000 (−0,0000 a +0,0000) | +0,0000 (+0,0000 a +0,0001) |
| 11 | Percentis de comportamento: cooperação e experiência (2) | −0,0031 e +0,0007, n = 2.987; não refeito | — |

Só o experimento 6, nos atributos ofensivos, tem intervalo que exclui zero aos 15 minutos (XGBoost), e o ganho é pequeno; com cerca de 20 comparações, um intervalo isolado pode ser acaso. Os experimentos 1 e 10 usam colunas que já existem no conjunto 14, medidas isoladamente. No experimento 4, o desvio no estado de empate total (probabilidade prevista menos a taxa observada entre partidas com diferença de ouro menor que 500) foi de +1,1 pp na produção, +1,9 na sigmoide e +1,9 na isotônica aos 15 minutos, e de +2,1, +3,2 e +0,9 aos 25: a calibração adicional não fecha o desvio (Apêndice F). Comandos: `python -m src.features.build_features_antigos` e `python -m src.models.experiment_antigos --cutoffs 15 25`; artefato: `reports/experimentos_antigos.json`; teste de vazamento: `tests/test_features_antigos_sem_vazamento.py`.

O experimento 11 (percentis do `lol-challenges-v1`) não foi refeito: o endpoint devolve o estado atual do jogador, então o teste usou as partidas mais recentes da KR, com 0 a 16 dias entre a coleta e a consulta (média de 7,8), para não usar dado do futuro. Um piloto de 199 partidas deu +0,0090 de AUC-ROC, mas era regressão à média: com 199 partidas, o modelo de referência já oscilava 1,8 pp de AUC em relação ao de produção. Com 2.987 partidas, o resultado foi −0,0031 (cooperação) e +0,0007 (experiência). Comando: `python -m src.models.experiment_challenges_pilot --n-matches 3000`; artefato: `reports/experimento_challenges_piloto.json`.

Quadro — Experimentos 12 a 19: ganho de AUC-ROC contra as cinco variáveis originais

| Exp. | Variáveis acrescentadas | 15 minutos | 25 minutos |
|---|---|---|---|
| 12 | Trajetória: ouro, experiência e abates dos 3 e 5 minutos anteriores (8 variáveis) | +0,0003 (−0,0001 a +0,0006) | +0,0014 (+0,0009 a +0,0019) |
| 13 | Por função, nível, farm, dano e atributos (37 variáveis) | +0,0027 (+0,0021 a +0,0032) | +0,0018 (+0,0013 a +0,0022) |
| 14 | Objetivos: arauto, barão, vastilarvas, inibidor, placas, primeiros abate e torre (7 variáveis) | +0,0002 (+0,0001 a +0,0003) | +0,0001 (+0,0000 a +0,0002) |
| 15 | Estado rico: 12 a 14 juntos (52 variáveis) | +0,0028 (+0,0022 a +0,0034) | +0,0025 (+0,0020 a +0,0031) |
| 16 | Campeões de cada time, taxa de vitória calculada fora da dobra (2 variáveis) | +0,0013 (+0,0008 a +0,0018) | +0,0020 (+0,0016 a +0,0024) |
| 17 | Histórico prévio do jogador, só com partidas anteriores (5 variáveis) | +0,0011 (+0,0008 a +0,0015) | +0,0004 (+0,0002 a +0,0006) |
| 18 | Tudo junto (59 variáveis), XGBoost | +0,0044 (+0,0037 a +0,0051) | +0,0040 (+0,0034 a +0,0047) |
| 18 | Tudo junto (59 variáveis), regressão logística | +0,0080 (+0,0068 a +0,0093) | +0,0074 (+0,0062 a +0,0087) |
| 19 | Histórico do jogador sobre o estado rico, partidas com 5 ou mais jogadores com histórico, regressão logística | +0,0004 (+0,0001 a +0,0006) | +0,0001 (−0,0001 a +0,0003) |

O maior ganho, com todas as variáveis e regressão logística, é de +0,0080 de AUC-ROC aos 15 minutos e de +0,0074 aos 25. A regressão logística aproveita as variáveis novas mais que o XGBoost, o que indica que o limite está na informação disponível e não no algoritmo. Campeões e histórico do jogador, sozinhos, dão AUC-ROC de 0,56 aos 15 minutos. O histórico do jogador não acrescenta ao estado de jogo mesmo nas partidas bem cobertas (experimento 19). Comando: `python -m src.models.experiment_precisao`; artefatos: `reports/experimentos_precisao.json` e `reports/experimento_historico.json`.

Quadro — Variáveis novas em treino no passado e teste no futuro

| Corte | Divisão | XGBoost, 5 variáveis | Regressão logística, 64 variáveis | Ganho de AUC-ROC |
|---|---|---:|---:|---|
| 15 min | Cronológica 80/20 | 0,8545 | 0,8633 | +0,0089 (+0,0059 a +0,0113) |
| 15 min | Por *patch* | 0,8542 | 0,8623 | +0,0080 (+0,0061 a +0,0097) |
| 15 min | Aleatória 80/20 | 0,8432 | 0,8510 | +0,0077 (+0,0053 a +0,0103) |
| 25 min | Cronológica 80/20 | 0,9142 | 0,9211 | +0,0069 (+0,0044 a +0,0095) |
| 25 min | Por *patch* | 0,9120 | 0,9202 | +0,0083 (+0,0066 a +0,0100) |
| 25 min | Aleatória 80/20 | 0,9111 | 0,9188 | +0,0077 (+0,0049 a +0,0105) |

O ganho se mantém quando se treina no passado e se testa no futuro, e a referência reproduz o Apêndice C. Comando: `python -m src.models.holdout_precisao`; artefato: `reports/holdout_precisao.json`.

---

## ANEXO A – Documentação da Riot Games API

Referência: RIOT GAMES. **APIs**. Disponível em:
https://developer.riotgames.com/apis. Endpoints utilizados: *league-v4*
(elos Desafiante a Mestre), *account-v1* (resolução de Riot ID),
*match-v5* (dados de partida e linha do tempo).

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
(APROVADO COM RESSALVAS), `docs/verifica_tcc.py` (22 checagens de
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
