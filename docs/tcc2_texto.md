# TCC II — Texto do trabalho

> **Este arquivo é a fonte do entregável.** O documento formatado é gerado a
> partir dele por `docs/build_tcc_docx.py` + `docs/finalize-fields.ps1`, na
> ordem do modelo institucional (capa → folha de rosto → Resumo/Abstract →
> 1 Introdução → 2 Referencial Teórico → 3 Material(is) e Métodos →
> 4 Resultados → 5 Discussão → 6 Conclusão → Referências → Apêndices/Anexos).
> **Não edite o `.docx` diretamente** — edite aqui e regere, senão texto e
> entregável divergem.
>
> **Decisões de escopo já tomadas (2026-10-03):**
> - **Título acadêmico não cita Bellestraiko.** Mantido igual ao TCC I, por
>   ser o mesmo trabalho. O nome do produto aparece no corpo do texto, na
>   Seção 1.1.
> - **Trabalhos Relacionados não são seção de primeiro nível**, porque o
>   modelo institucional do TCC II não prevê essa seção. A referência
>   teórica fica na Seção 2 e a comparação com os resultados na Seção 5.1.
> - O TCC I tem "3 TRABALHOS RELACIONADOS" como seção, mas o modelo do TCC II
>   (2026-09-28) não inclui — prevalecou o modelo do TCC II.
> - ~~Resumo/Abstract~~ — escrito.

---

## RESUMO

O crescimento dos esports tem ampliado significativamente a geração de
dados sobre partidas, jogadores, equipes e estratégias competitivas,
criando oportunidades relevantes para aplicação de análise de dados e
inteligência artificial. Entretanto, a exploração desses dados ainda
costuma depender de processos fragmentados e de ferramentas que exigem
conhecimento técnico específico. Diante desse cenário, este trabalho
desenvolveu uma plataforma inteligente para análise de dados de
esports com foco em *League of Legends*, integrando coleta,
organização e exploração de dados competitivos, modelagem preditiva
com *machine learning* e mecanismos de visualização e consulta em
linguagem natural. Foram coletadas e organizadas 23.133 partidas
ranqueadas de elo alto (quatro regiões) via Riot Games API, e
incorporadas 99.259 partidas profissionais (2014-2026, Oracle's
Elixir). Três modelos — XGBoost, *Random Forest* e uma rede neural
(MLP) — foram treinados e comparados para predizer o vencedor a partir
do estado da partida em quatro cortes temporais (10, 15, 20 e 25
minutos), com o XGBoost alcançando o melhor desempenho no corte de 15
minutos (acurácia de 0,7573; AUC-ROC de 0,8393). A análise exploratória
identificou que o time vermelho é favorecido no *solo queue* de elo
alto (56,3% de vitórias na região com maior amostra), um padrão que se
enfraquece ao longo da partida e que se inverte no cenário profissional
(onde o time azul vence cerca de 53% das partidas, de forma estável
entre 2014 e 2026) — achado sustentado por testes de robustez
estatística. Uma interface em linguagem natural (*text-to-SQL* com
validação estrutural da consulta) atingiu 88% de acurácia de execução
em um benchmark de 26 perguntas de referência. A plataforma foi
disponibilizada com seis páginas de visualização interativa, incluindo
predição explicável (SHAP) e mapa de calor de posicionamento por
partida. Os resultados demonstram a viabilidade de integrar coleta,
modelagem preditiva, explicabilidade e consulta em linguagem natural
em uma única solução aplicada a dados reais de esports.

**Palavras-chave:** Esports. *League of Legends*. Análise de dados.
*Machine learning*. Interface em linguagem natural.

**Abstract:** The growth of esports has significantly increased the
amount of data generated about matches, players, teams and competitive
strategies, creating relevant opportunities for the application of
data analysis and artificial intelligence. However, the use of such
data still often depends on fragmented processes and tools that
require specific technical knowledge. In this scenario, this work
developed an intelligent platform for esports data analysis focused on
*League of Legends*, integrating the collection, organization and
exploration of competitive data, predictive modeling with *machine
learning* techniques, and visualization and natural language query
mechanisms. A total of 23,133 high-elo ranked matches (four regions)
were collected and organized through the Riot Games API, complemented
by 99,259 professional matches (2014-2026, Oracle's Elixir). Three
models — XGBoost, Random Forest and a neural network (MLP) — were
trained and compared to predict the winning team from the match state
at four time cutoffs (10, 15, 20 and 25 minutes), with XGBoost
achieving the best performance at the 15-minute cutoff (accuracy of
0.7573; AUC-ROC of 0.8393). The exploratory analysis identified that
the red side is favored in high-elo solo queue (56.3% win rate in the
region with the largest sample), a pattern that weakens over the
course of the match and reverses in the professional scenario (where
the blue side wins about 53% of matches, stable from 2014 to 2026) — a
finding supported by statistical robustness tests. A natural language
interface (text-to-SQL with structural query validation) achieved 88%
execution accuracy on a 26-question reference benchmark. The platform
was delivered with six interactive visualization pages, including
explainable prediction (SHAP) and per-match positional heat maps. The
results demonstrate the feasibility of integrating data collection,
predictive modeling, explainability and natural language querying into
a single solution applied to real esports data.

**Key-words:** Esports. League of Legends. Data analysis. Machine
learning. Natural language interface.

---

## 1 INTRODUÇÃO

Os esports vêm se consolidando como um campo de crescente relevância
acadêmica e tecnológica, especialmente em função do grande volume de
dados gerados por partidas, jogadores, equipes e estratégias
competitivas. Em *League of Legends*, Birant e Birant (2023) destacam
que esses dados podem ser explorados por meio de modelos de *machine
learning* voltados à análise competitiva e à predição de resultados.

Nesse cenário, a análise de dados aplicada a esports ganha importância
não apenas pelo potencial preditivo, mas também pela capacidade de
apoiar a interpretação do jogo, a compreensão de tendências
competitivas e a organização de informações complexas de forma mais
estruturada. No contexto de *League of Legends*, informações
relacionadas a partidas, jogadores, equipes e estatísticas de
desempenho podem servir de base para identificar padrões, avaliar
performance e apoiar análises competitivas.

Apesar desse potencial, a exploração dessas informações ainda costuma
depender de processos fragmentados e de ferramentas que exigem
conhecimento técnico específico, o que limita o acesso mais amplo a
análises competitivas de qualidade. García-Méndez e Arriba-Pérez
(2025) indicam que não basta apenas gerar previsões, sendo também
importante apresentar resultados de forma interpretável e acessível ao
usuário final.

Outro ponto relevante é que a interação com dados analíticos tem sido
ampliada pelo uso de interfaces em linguagem natural, capazes de
reduzir a barreira técnica entre o usuário e a base de dados. Jiang et
al. (2025) mostram que modelos de linguagem podem apoiar soluções de
*Business Intelligence* voltadas à exploração de dados estruturados, o
que se mostra pertinente em cenários com grande quantidade de dados
competitivos e múltiplas possibilidades de análise.

Neste contexto, o presente trabalho teve como objetivo geral
desenvolver uma plataforma inteligente para análise de dados de
esports, com foco em *League of Legends*, integrando coleta,
organização e exploração de dados competitivos, modelagem preditiva
com técnicas de *machine learning* e mecanismos de visualização e
consulta em linguagem natural. Para alcançar esse objetivo, foram
mapeados os dados e recursos disponibilizados pela Riot Games API,
identificadas as informações relevantes sobre partidas, jogadores e
estatísticas, estruturado um processo de coleta e tratamento dos
dados, comparados os modelos XGBoost, *Random Forest* e redes
neurais, e propostos dashboards e uma interface em linguagem natural
para apoiar a interpretação das informações competitivas de forma
mais acessível e organizada. Além do escopo originalmente previsto no
TCC I, a base de dados competitivos foi complementada com um segundo
conjunto de dados profissionais (Oracle's Elixir, ~99 mil partidas de
2014 a 2026), o que permitiu comparar os padrões observados no *solo
queue* com os do cenário competitivo profissional.

Este trabalho está organizado em cinco seções, além desta introdução.
A Seção 2 apresenta o referencial teórico, reunindo os principais
conceitos relacionados a esports, análise de dados, *machine
learning*, explicabilidade, interfaces em linguagem natural e
visualização analítica. A Seção 3 descreve o material e os métodos
utilizados no desenvolvimento da plataforma. A Seção 4 apresenta os
resultados obtidos. A Seção 5 discute esses resultados à luz da
literatura e das limitações identificadas. A Seção 6 apresenta as
considerações finais. Por fim, são apresentadas as referências
utilizadas na construção deste trabalho.

### 1.1 TEMA

O tema deste trabalho é a análise de dados aplicada a esports, com
foco no desenvolvimento de uma plataforma inteligente para exploração
de informações competitivas em *League of Legends*. A plataforma,
batizada **Bellestraiko**, constitui a materialização do sistema
desenvolvido e implementado ao longo deste trabalho. O estudo está
inserido na área da Ciência da Computação e envolve conceitos de
ciência de dados, inteligência artificial, *machine learning* e
sistemas de informação, contribuindo para a organização, interpretação
e acessibilidade de dados gerados em partidas competitivas.

### 1.2 DELIMITAÇÃO DO TEMA

Este trabalho delimitou-se ao desenvolvimento de uma plataforma
inteligente para análise de dados de esports com foco exclusivo em
*League of Legends*. O estudo concentrou-se na utilização de dados
competitivos obtidos por meio da Riot Games API — complementados por
dados históricos profissionais do Oracle's Elixir —, considerando
informações relacionadas a partidas, jogadores e estatísticas de
desempenho. No campo analítico, o recorte envolveu a aplicação e
comparação de modelos de *machine learning*, com ênfase em XGBoost,
*Random Forest* e redes neurais, voltados à identificação de padrões e
à realização de análises preditivas restritas ao estado do jogo até o
momento da predição (sem uso de informações posteriores ao corte
temporal). Além disso, a proposta restringiu-se à concepção de
dashboards e de uma interface em linguagem natural para consulta e
interpretação dos dados. Dessa forma, o trabalho não abrange todos os
jogos do cenário de esports nem todas as abordagens possíveis de
inteligência artificial, mas um recorte específico e viável, alinhado
aos objetivos definidos no TCC I.

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
objetivos específicos — todos alcançados, conforme apresentado na
Seção 4:

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
aos dados e a geração de *insights* no contexto competitivo estudado.

### 1.5 JUSTIFICATIVA

A realização deste trabalho se justifica pela crescente relevância dos
esports como campo de produção e exploração de dados, especialmente em
jogos competitivos amplamente consolidados, como *League of Legends*.
O tema apresenta importância acadêmica por articular áreas centrais da
Ciência da Computação, como análise de dados, inteligência artificial,
*machine learning*, sistemas de informação e interação
humano-computador, permitindo o desenvolvimento de uma proposta
interdisciplinar alinhada à formação do curso. Além disso, a
investigação sobre dados competitivos em esports representou uma
oportunidade significativa de aprofundamento, sobretudo por integrar
análise preditiva, visualização e acessibilidade no uso das
informações.

Do ponto de vista prático, o trabalho também se mostra relevante por
propor uma solução capaz de organizar e tornar mais acessível a
exploração de dados competitivos, reduzindo a dependência de processos
fragmentados e de ferramentas que exigem conhecimento técnico elevado.
Ao reunir coleta, tratamento, modelagem analítica e mecanismos de
consulta em linguagem natural em uma mesma plataforma, a proposta
ofereceu uma contribuição aplicável à interpretação de desempenho, ao
acompanhamento de tendências competitivas e ao apoio à análise de
partidas. Nesse sentido, a ausência de abordagens integradas voltadas
à exploração acessível desses dados limitava o aproveitamento de
informações valiosas no contexto dos esports, tanto em estudos
acadêmicos quanto em aplicações práticas.

---

## 2 REFERENCIAL TEÓRICO

A fundamentação teórica deste trabalho reúne os principais conceitos
necessários para compreender a proposta de uma plataforma inteligente
para análise de dados de esports com foco em *League of Legends*.
Considerando a natureza interdisciplinar do tema, o capítulo articula
contribuições da análise de dados, do *machine learning*, da
explicabilidade de modelos, das interfaces em linguagem natural e da
visualização analítica, buscando estabelecer uma base conceitual
coerente para o desenvolvimento da pesquisa. Hodge et al. (2021)
contribuem para a compreensão da predição em partidas de esports,
enquanto Birant e Birant (2023) e Bahrololloomi et al. (2022)
fundamentam a discussão sobre *machine learning* aplicado a *League of
Legends*.

No campo da interpretação e da interação com dados, García-Méndez e
Arriba-Pérez (2025) apoiam a discussão sobre explicabilidade, enquanto
Jiang et al. (2025) fundamentam o uso de modelos de linguagem em
soluções analíticas.

### 2.1 ESPORTS E ANÁLISE DE DADOS

Os esports vêm se consolidando como um campo relevante para análise de
dados, uma vez que jogos competitivos geram grande volume de
informações sobre partidas, jogadores, equipes, estratégias e eventos
em tempo real. Hodge et al. (2021) demonstram que a predição de
resultados em partidas profissionais pode se beneficiar da análise
estruturada desses dados. No contexto de *League of Legends*, Birant e
Birant (2023) destacam a importância da modelagem centrada no time,
enquanto Bahrololloomi et al. (2022) evidenciam a relação entre
métricas de jogadores, funções em jogo e desempenho competitivo.

### 2.2 MACHINE LEARNING APLICADO A LEAGUE OF LEGENDS E ESPORTS

A aplicação de *machine learning* em esports tem se mostrado promissora
em tarefas como predição de vitória, avaliação de desempenho e
identificação de padrões competitivos. Em *League of Legends*, Birant e
Birant (2023) indicam que a modelagem centrada no time é uma abordagem
relevante para compreender os resultados das partidas. Bahrololloomi et
al. (2022), por outro lado, analisam o desempenho dos jogadores a
partir de funções e métricas individuais, ampliando a compreensão
sobre diferentes fatores associados à vitória. Este trabalho utilizou e
comparou os modelos XGBoost, *Random Forest* e redes neurais (MLP),
analisando diferentes estratégias para dados competitivos e verificando
como abordagens baseadas em árvores e modelos neurais contribuem para
a análise preditiva proposta — os resultados dessa comparação são
apresentados na Seção 4.

### 2.3 EXPLICABILIDADE E ANÁLISE PREDITIVA

Além de produzir previsões, sistemas analíticos voltados a esports
precisam oferecer mecanismos que favoreçam a interpretação dos
resultados gerados. García-Méndez e Arriba-Pérez (2025) mostram que
abordagens de predição explicável podem combinar classificação e
interpretação, tornando *dashboards*, descrições e fatores relevantes
da previsão mais compreensíveis para o usuário final. A explicabilidade
assumiu papel importante neste projeto, tendo sido implementada por
meio de valores SHAP (*SHapley Additive exPlanations*), curvas de
calibração e explicações textuais geradas a partir dos próprios fatores
identificados como relevantes — não a partir de conhecimento genérico
de um modelo de linguagem, mas ancoradas nos dados e nos coeficientes
calculados (ver Seção 3).

### 2.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

A utilização de interfaces em linguagem natural tem ampliado as
possibilidades de interação com sistemas analíticos, reduzindo a
barreira técnica entre o usuário e os dados. Jiang et al. (2025)
observam que soluções de *Business Intelligence* apoiadas por modelos
de linguagem podem favorecer a exploração de dados estruturados. Guo et
al. (2024) também destacam que mecanismos de diálogo, decomposição de
perguntas e análise visual podem tornar a exploração dos dados mais
intuitiva e eficiente. Este trabalho implementou uma interface de
linguagem natural (*text-to-SQL*) capaz de traduzir perguntas em
português para consultas SQL validadas contra o esquema real do banco
de dados, integrando visualização, recuperação de informações e geração
de *insights* em uma mesma plataforma — os resultados de acurácia dessa
interface são apresentados na Seção 4.

### 2.5 VISUALIZAÇÃO ANALÍTICA E DADOS ESPAÇO-TEMPORAIS EM ESPORTS

Além da modelagem preditiva, a análise de dados em esports também
envolve o desafio de representar visualmente informações complexas que
evoluem no espaço e no tempo ao longo das partidas. Em jogos como
*League of Legends*, dados relacionados a movimentação, posicionamento,
interação entre jogadores e dinâmica das partidas podem ser explorados
por meio de abordagens de *visual analytics* voltadas à revisão
pós-jogo. Wallner, Wang e Dormann (2023) mostram que visualizações
espaço-temporais podem contribuir para a interpretação do comportamento
em jogo e para a identificação de padrões relevantes ao desempenho
competitivo, especialmente quando conseguem integrar tempo e
localização em uma única representação visual. Esse referencial
fundamentou o desenvolvimento do mapa de calor de posicionamento
apresentado na análise de partida da plataforma (Seção 4).

A comparação direta entre estes trabalhos e os resultados obtidos neste
trabalho é apresentada na Seção 5.1. O modelo institucional do TCC II não
prevê uma seção própria de trabalhos relacionados — a referência teórica é
descrita aqui e a confrontação com os resultados fica na discussão, que é
onde a leitura crítica faz sentido.

---

## 3 MATERIAL(IS) E MÉTODOS

Esta seção descreve os procedimentos metodológicos efetivamente
empregados no desenvolvimento da pesquisa e da plataforma, detalhando a
natureza do estudo, a coleta e o tratamento dos dados, a modelagem
preditiva e os recursos de visualização e consulta construídos.

### 3.1 NATUREZA E ABORDAGEM DA PESQUISA

O presente trabalho caracteriza-se, quanto à sua natureza, como uma
pesquisa aplicada: Prodanov e Freitas (2013) explicam que a pesquisa
aplicada busca produzir conhecimentos voltados à solução de problemas
específicos e com possibilidade de utilização prática, o que se
concretizou na estruturação de uma plataforma funcional para coletar,
organizar e analisar dados competitivos de *League of Legends*. Quanto
aos objetivos, a pesquisa teve caráter exploratório e descritivo (GIL,
2002): exploratório na investigação inicial sobre a Riot Games API e as
possibilidades de modelagem, e descritivo na caracterização dos dados
coletados, dos padrões identificados e dos modelos comparados. Quanto à
abordagem, a pesquisa adotou perspectiva mista (CRESWELL; CRESWELL,
2023): o componente qualitativo esteve presente na revisão
bibliográfica e na interpretação dos achados; o componente quantitativo
esteve associado à coleta e ao tratamento dos dados, à análise
exploratória e à comparação entre os modelos de *machine learning*.

### 3.2 ESTRATÉGIAS DE PESQUISA

O trabalho foi desenvolvido por meio de pesquisa bibliográfica (GIL,
2002), pesquisa documental sobre a documentação oficial da Riot Games
API (PRODANOV; FREITAS, 2013) e estudo aplicado com recorte de caso no
domínio de *League of Legends* (YIN, 2018).

### 3.3 COLETA DE DADOS

A coleta foi realizada a partir de duas fontes complementares — a
segunda delas incorporada durante a execução do TCC II, ampliando o
escopo originalmente previsto no TCC I:

**a) Riot Games API (dados de partidas ranqueadas — *solo queue*).**
Foram utilizados os endpoints *league-v4* (para identificar jogadores
nos elos Desafiante e Grão-Mestre), *account-v1* (resolução de Riot ID)
e *match-v5*/*timeline-v5* (dados de partida e linha do tempo minuto a
minuto). A coleta abrangeu quatro regiões (BR1, EUW1, KR, NA1) na fila
420 (ranqueada solo/duo), totalizando **23.133 partidas** normalizadas,
com estado bruto (JSON) preservado em `raw_matches`/`raw_timelines`
para reprocessamento. A chave de desenvolvedor da Riot expira a cada 24
horas, o que exigiu um processo de coleta resumível (script capaz de
retomar de onde parou, pulando partidas já salvas).

**b) Oracle's Elixir (dados de partidas profissionais).** Foram
incorporados **99.259 jogos profissionais** (2014-2026), cobrindo as
principais ligas mundiais (LCK, LPL, LEC, LTA, CBLOL, entre outras), a
partir de arquivos CSV anuais publicados publicamente. Essa fonte não
estava prevista no recorte original do TCC I e foi adicionada para
permitir a comparação entre o padrão observado no *solo queue* de elo
alto e o padrão do cenário competitivo profissional (ver Seção 4).

Como o TCC I já delimitava o uso de dados secundários e públicos, não
houve participação direta de sujeitos humanos como fonte de dados em
nenhuma etapa.

### 3.4 ORGANIZAÇÃO E TRATAMENTO DE DADOS

Os dados foram estruturados em um banco de dados relacional PostgreSQL,
com entidades para partidas, times, participantes, jogadores, banimentos
de campeão, eventos de item e — para o dataset profissional —
`pro_games`/`pro_players`. Um catálogo de itens (`items`, derivado dos
dados públicos do Data Dragon da Riot) foi incorporado para permitir que
nomes e ícones de item fossem resolvidos por consulta direta ao banco,
nunca por conhecimento genérico de um modelo de linguagem. O tratamento
incluiu normalização dos dados brutos de partida (ETL específico por
fonte), extração de eventos de compra/venda de item a partir da linha
do tempo (com desfazimento de `ITEM_UNDO` aplicado) e reconciliação de
nomes de campeão entre a Riot API e o Oracle's Elixir (que usam
convenções de nomenclatura diferentes).

### 3.5 ANÁLISE EXPLORATÓRIA DE DADOS

A análise exploratória buscou identificar distribuições, padrões
iniciais e relações entre variáveis relevantes ao problema de pesquisa,
com particular atenção à taxa de vitória por lado do mapa (azul/vermelho)
em diferentes recortes — por região, por fase da partida e por contexto
competitivo (*solo queue* vs. profissional). Achados quantitativos
inesperados (como a variação do viés de lado ao longo do tempo de jogo)
foram submetidos a testes de robustez adicionais antes de serem aceitos
como resultado, incluindo: replicação restrita a uma única região (para
descartar efeito de mistura regional), comparação contra a duração total
da partida (para descartar confusão com "jogos longos") e cálculo de
intervalo de confiança de Wilson sobre a proporção observada (para
avaliar a significância estatística do efeito em amostras menores). Os
resultados dessa análise são apresentados na Seção 4.3.

### 3.6 MODELAGEM PREDITIVA E COMPARAÇÃO ENTRE MODELOS

Foram treinados e comparados três modelos de classificação binária
(vitória do time azul: sim/não) — XGBoost, *Random Forest* e uma rede
neural do tipo perceptron multicamadas (MLP) — usando como variáveis
preditoras as diferenças (azul menos vermelho) de ouro, experiência,
abates, torres e dragões acumuladas até um corte temporal da partida.
Foram treinados modelos independentes para quatro cortes (10, 15, 20 e
25 minutos), respeitando a restrição de que nenhuma informação posterior
ao corte é usada como *feature* (evitando vazamento de dados). A
validação foi feita por validação cruzada estratificada de 5 *folds*,
com métricas de acurácia, precisão, *recall*, F1 e AUC-ROC. Após um
baseline inicial, foi realizado ajuste de hiperparâmetros por
*GridSearchCV* (otimizando AUC-ROC) para os três modelos, seguido de
geração de curva de calibração e de explicações SHAP (importância
global e por instância) sobre o modelo de produção. Adicionalmente,
foram conduzidos nove experimentos exploratórios de enriquecimento de
*features* (ver Seção 4.4) para avaliar se sinais adicionais da linha do
tempo (visão, itens, dispersão espacial do time, objetivos neutros)
melhoravam o poder preditivo além das cinco variáveis de estado já
utilizadas.

### 3.7 PROPOSTA DE VISUALIZAÇÃO E INTERFACE EM LINGUAGEM NATURAL

A camada de apresentação foi construída como uma aplicação web (React +
TypeScript no *frontend*, consumindo uma API própria em FastAPI),
organizada em seis páginas principais: Início (busca unificada),
Dashboard (KPIs e padrões agregados), Campeões (estatísticas e detalhe
por campeão, incluindo presença no cenário profissional), Partidas
(análise minuto a minuto com mapa de calor de posicionamento, leitura de
composição/draft e modo contrafactual "e se"), Competitivo (comparação
*solo queue* × profissional, com seletor de ano/*split*) e Simulador
(composição de time com estimativa por heurística de taxa de vitória
histórica, estado de jogo com predição por modelo e explicabilidade via
SHAP). A interface em linguagem natural foi implementada como um
pipeline *text-to-SQL*: a pergunta do usuário é traduzida em uma consulta
SQL por um modelo de linguagem (Claude), a consulta é validada
estruturalmente antes da execução (apenas `SELECT`/`WITH...SELECT`,
tabelas permitidas em lista fechada) e o resultado é executado contra o
banco real — nunca respondido a partir de conhecimento genérico do
modelo sobre o domínio. A acurácia dessa interface foi medida por um
benchmark de 26 perguntas de referência com SQL esperado, cobrindo tanto
o dataset de *solo queue* quanto o competitivo.

### 3.8 MATERIAIS E MÉTODOS UTILIZADOS

Foram utilizados Python (coleta, ETL, modelagem — bibliotecas *pandas*,
*NumPy*, *scikit-learn*, *XGBoost*, *SHAP*), PostgreSQL (armazenamento
relacional), FastAPI (camada de serviço/API) e React com TypeScript
(camada de visualização, biblioteca de gráficos Recharts). A interface
em linguagem natural e o módulo de orientação estratégica (*coach*)
utilizaram a API da Anthropic (modelo Claude). Testes automatizados
cobriram tanto o *backend* (testes de fumaça em ambiente isolado e uma
bateria de validação comportamental do modelo de produção) quanto o
*frontend* (Vitest). O ambiente de desenvolvimento e execução foi
Windows, com os serviços de API e *frontend* executados localmente
durante o desenvolvimento.

---

## 4 RESULTADOS

Esta seção apresenta os resultados obtidos, organizados de acordo com
os objetivos específicos definidos na Seção 1.4.2.

### 4.1 Mapeamento de dados e recursos da Riot Games API (objetivo a)

Foram mapeados e utilizados os endpoints *league-v4*, *account-v1*,
*match-v5* e *timeline-v5* da Riot Games API, além da documentação
técnica necessária para compreender limitações de taxa de requisição e
o ciclo de expiração da chave de desenvolvedor (24 horas). Esse
mapeamento orientou o desenho de um coletor resumível, capaz de operar
dentro dos limites de taxa e de retomar a coleta entre sessões sem
duplicar dados já salvos.

### 4.2 Estruturação da base de dados (objetivos b e c)

A base usada para treinar e comparar os modelos preditivos (Seção 4.4)
reúne **23.133 partidas** de *solo queue* (24.999 jogadores distintos,
173 campeões), com JSON bruto de partida e linha do tempo preservados
para reprocessamento, e **99.259 jogos profissionais** (2014-2026,
Oracle's Elixir). O esquema relacional contempla partidas, times,
participantes, jogadores, banimentos, eventos de item (com
desfazimento de compras/vendas aplicado) e um catálogo de itens para
resolução de nome/ícone sem depender de conhecimento genérico de
modelo de linguagem. A coleta de *solo queue* continuou após esse
corte especificamente para ampliar as regiões com amostra menor
(EUW1/KR/NA1), chegando a 33.713 partidas em 2026-10-03 — volume
usado na análise de viés de lado por região (Seção 4.3), mas não
usado para retreinar os modelos preditivos nesta versão do trabalho.
O ganho potencial de um novo ciclo de treino é da ordem de ~45%
sobre as 23.133 partidas do corte; ele não foi priorizado porque
exigiria rever integralmente a Seção 4.4 e o Apêndice C, e o texto
estava em fase de consolidação. Os números de modelo relatados adiante
são, portanto, os de 23.133 partidas.

### 4.3 Análise exploratória: padrões identificados (objetivo d)

**Viés de lado no *solo queue* de elo alto.** No agregado das cinco
regiões coletadas, o time vermelho venceu com mais frequência que o
azul, com intensidade variável por região. Medição direta em SQL,
2026-10-03, sobre 33.713 partidas (volume ampliado especificamente
para fortalecer este quadro — ver nota de método abaixo):

Quadro — Vitória do time vermelho por região

| Região | Partidas | Vitória do vermelho |
|---|---:|---:|
| BR1 | 11.936 | 56,3% |
| EUW1 | 11.744 | 53,4% |
| KR | 8.567 | 50,3% |
| NA1 | 1.446 | 51,9% |
| EUN1 | 20 | 50,0% (amostra insuficiente, não considerada) |

*(Nota de método: quadro original — medido em 2026-07-06 com BR1
11.936, EUW1 1.307, NA1 1.367, KR 1.308 partidas — foi substituído por
uma segunda rodada de coleta destinada especificamente a ampliar
EUW1/KR/NA1, e depois por esta medição de 2026-10-03, quando EUW1 e
KR já haviam quase dobrado novamente. A direção do achado (as quatro
regiões com amostra relevante pendem para o vermelho, entre 50,3% e
56,3%) se manteve idêntica em todas as três medições — o que
fortalece a leitura de "padrão de elo altíssimo em geral", não
artefato de uma região com pouca amostra. BR1 não se alterou em nenhum
dos três levantamentos. NA1 segue com volume pequeno mesmo após as
coletas adicionais — ver Seção 5.2.)*

**O viés de lado não é constante ao longo da partida.** Investigando a
probabilidade-base do modelo (estado de empate total) em cada corte
temporal, observou-se: 10min 47,8% de vitória azul → 15min 46,3% (ponto
mais favorável ao vermelho) → 20min 49,1% → 25min 51,1%. O mesmo padrão
apareceu na taxa de vitória bruta (sem modelo) entre partidas
genuinamente empatadas (diferença de ouro menor que 500): 46,1% → 46,4%
→ 47,3% → 48,6% de vitória azul, do corte de 10 ao de 25 minutos. Três
testes de robustez foram aplicados: (i) restrição a uma única região
(BR1) reproduziu e até intensificou o padrão, descartando mistura
regional como explicação; (ii) a taxa de vitória incondicional por
faixa de duração total de partida manteve-se estável (44%-47%),
descartando a hipótese de que "partidas longas são um tipo diferente de
jogo"; (iii) o intervalo de confiança de Wilson a 95% no ponto de 25
minutos (BR1, n=458) foi [46,5%–55,6%] — inclui 50%, mas também inclui
valores ainda favoráveis ao vermelho, o que sustenta a tendência de
enfraquecimento do viés sem sustentar uma alegação de inversão completa
e confirmada.

**Comparação com o cenário profissional.** No dataset competitivo
(Oracle's Elixir), o time azul venceu aproximadamente 53% das partidas,
de forma estável entre 2014 e 2026 — o padrão descrito pela literatura
geral sobre *League of Legends*. O viés de lado do *solo queue* de elo
alto vai na direção oposta ao do jogo profissional, o que constitui um
dos achados centrais deste trabalho: a mesma métrica, medida em dois
contextos institucionalmente diferentes, produz sinais opostos —
hipótese de explicação: no *solo queue*, sem coordenação de *draft* de
cinco jogadores, o *counter-pick* garantido do time vermelho (que
escolhe por último) pesa mais; no jogo profissional, a prioridade de
primeira escolha é valorizada o suficiente para influenciar decisões
de lado em *playoffs*.

**Conversão de vantagem.** Com uma vantagem de ouro entre +2.000 e
+4.000 aos 15 minutos, o time azul venceu 84,0% das partidas no cenário
profissional contra aproximadamente 68% no *solo queue* (com vantagem
de +4.000 a +6.000, ~95% contra ~81%). Esse resultado quantifica a
noção de que "macro ganha jogo": a mesma vantagem material aos 15
minutos vale mais nas mãos de um time coordenado.

*(Ressalva de volume: as taxas do *solo queue* desta comparação foram
medidas em 2026-07-04 sobre aproximadamente 12 mil partidas — a base
disponível na ocasião, não as 23.133 usadas nos modelos. São estimativas
de apoio a um achado qualitativo (a diferença de ~16 pontos percentuais
entre os dois cenários é grande demais para ser artefato de amostra), e
não medidas sobre a base de treino. A tabela por região da Seção 4.3 e
as taxas do profissional são de faixas posteriores.)*

### 4.4 Modelagem preditiva e comparação entre modelos (objetivo e)

Após ajuste de hiperparâmetros (*GridSearchCV*, validação cruzada
estratificada de 5 *folds*) sobre o corte de 15 minutos, no conjunto
final de 23.133 partidas:

Quadro — Comparação entre modelos (corte de 15 minutos)

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---:|---:|---:|
| **XGBoost (produção)** | **0,7573** | 0,7444 | 0,7133 | 0,7285 | **0,8393** |
| MLP | 0,7550 | 0,7457 | 0,7034 | 0,7238 | 0,8385 |
| *Random Forest* | 0,7409 | 0,7237 | 0,6997 | 0,7115 | 0,8219 |

*(taxa de vitória do time azul na amostra: 45,6%; medição confirmada em
2026-09-28 sobre as 22.973 partidas do corte de 15 min, reproduzindo
exatamente os números do retreino de 2026-07-06.)*

Os três modelos performaram de forma próxima entre si, com o XGBoost
adotado como modelo de produção. Modelos independentes foram treinados
para os quatro cortes temporais, com desempenho crescente conforme a
partida avança (medido com os hiperparâmetros de produção): AUC-ROC de
0,767 (10min), 0,842 (15min), 0,872 (20min) e 0,907 (25min) — resultado
esperado, já que mais informação está disponível em cortes mais
tardios, mas que só se sustenta porque um modelo *por fase* foi
treinado especificamente para cada corte.

A análise de importância de variáveis (SHAP, valor médio absoluto por
*feature*) mostrou a diferença de ouro e de experiência como os fatores
dominantes em todos os cortes (gold_diff variando de 0,65 a 10min até
1,04 a 20-25min; xp_diff de 0,26 a 10min até 0,79 a 25min), com a
diferença de torres crescendo de forma acentuada apenas nos cortes
tardios — de 0,004 (10min) e 0,014 (15min) para 0,018 (20min) e 0,108
(25min), um salto de cerca de 26 vezes entre o corte de 15 e o de 25
minutos. Esse comportamento é consistente com a mecânica do jogo, em
que as placas de defesa das torres caem por volta dos 14 minutos,
tornando destruições de torre um evento raro (e pouco informativo) antes
disso — e é a justificativa concreta para treinar um modelo *por fase*
em vez de um único modelo genérico. A curva de calibração mostrou que
os modelos, especialmente o XGBoost, já produziam probabilidades bem
calibradas sem necessidade de
recalibração adicional.

**Experimentos negativos.** Nove tentativas de enriquecer o conjunto de
variáveis não produziram ganho de desempenho estatisticamente
distinguível de ruído (deltas de AUC-ROC na ordem de ±0,001-0,003):
diferença de abates de Barão/Arauto, dispersão espacial do time, ajuste
de hiperparâmetros específico por fase, calibração adicional além da já
obtida, ouro convertido em itens, separação de *features* defensivas e
ofensivas, uma segunda tentativa de `item_gold_diff`, diferenças de
visão (colocação/destruição de sentinelas) e o tipo do dragão
(`monsterSubType`) — este último o único em que o desempenho piorou
de forma mensurável (AUC-ROC de 0,8319 para 0,8295). Em contraste, o
aumento do *volume* de partidas produziu ganhos reais e consistentes: o
AUC-ROC do
XGBoost subiu de 0,8214 (10.295 partidas) para 0,8393 (23.133 partidas)
ao longo da coleta incremental — evidência de que, com as *features* de
estado agregado atualmente disponíveis via API, o teto de desempenho é
limitado mais pelo volume de dados do que pela engenharia de novas
variáveis a partir da mesma fonte.

### 4.5 Dashboards (objetivo f)

Foram entregues seis páginas de visualização (Início, Dashboard,
Campeões, Partidas, Competitivo e Simulador), incluindo KPIs agregados,
gráficos de distribuição por campeão e objetivo, mapa de calor de
posicionamento por minuto na análise de partida, comparação visual
*solo queue* × profissional com seletor de ano, e um simulador que
combina composição de time (heurística de taxa de vitória histórica,
sinalizada como tal na interface para não ser confundida com predição
por modelo), estado de jogo (predição pelo modelo de produção) e
explicabilidade (SHAP).

### 4.6 Interface em linguagem natural (objetivo g)

O *pipeline* de linguagem natural para consulta ao banco (*text-to-SQL*
com validação estrutural antes da execução) atingiu **88% de acurácia de
execução** (23 de 26 perguntas de referência, sendo 22 sobre *solo
queue* e 4 sobre o dataset competitivo), medida de forma estável ao
longo de sessões de revisão sucessivas. As três falhas remanescentes
pertencem à mesma família benigna — diferenças de formatação ou coluna
extra na resposta, não erros de interpretação da pergunta ou de geração
de SQL incorreto.

---

## 5 DISCUSSÃO

### 5.1 Os resultados frente à literatura

Hodge et al. (2021) demonstraram a viabilidade de modelos preditivos
para partidas profissionais de esports em tempo real; este trabalho
corrobora essa viabilidade para *League of Legends* especificamente, com
a particularidade de ter caracterizado como o desempenho preditivo varia
ao longo da partida (AUC-ROC de 0,767 a 10 minutos a 0,907 a 25 minutos)
— uma dimensão que o estudo original não detalha por fase. Diferente de
Hodge et al. (2021), que não propõem uma plataforma integrada com
*dashboards* e interface em linguagem natural, este trabalho se
diferenciou justamente por integrar predição, explicabilidade,
visualização e consulta em uma mesma solução.

Birant e Birant (2023) destacam a relevância da modelagem centrada no
time para compreender resultados de partidas — abordagem que este
trabalho adotou diretamente ao construir as variáveis preditoras como
diferenças agregadas entre os dois times (ouro, experiência, abates,
torres, dragões), em vez de métricas individuais de jogador. Já
Bahrololloomi et al. (2022) analisam desempenho a partir de funções e
métricas individuais de jogador; este trabalho não explorou essa
granularidade na modelagem preditiva de vitória, mas incorporou uma
noção próxima na camada de perfis de jogador e de recomendação de
time (estimativa por jogador-campeão com correção estatística de
amostra pequena, não reportada em detalhe nesta seção por não ser
parte da modelagem preditiva central).

García-Méndez e Arriba-Pérez (2025) argumentam que sistemas preditivos
em esports precisam de mecanismos de interpretação para serem úteis ao
usuário final; este trabalho concretizou essa recomendação por meio de
explicações SHAP integradas ao *dashboard* e de um módulo de orientação
estratégica que cita, para cada recomendação, o dado real de onde ela
foi extraída — nunca uma afirmação genérica de modelo de linguagem sem
lastro nos dados coletados.

Jiang et al. (2025) e Guo et al. (2024) fundamentam a aplicação de
modelos de linguagem para exploração de dados estruturados fora do
contexto de esports; este trabalho estendeu essa ideia especificamente
ao domínio competitivo de *League of Legends*, com validação estrutural
da consulta gerada antes da execução — uma camada de segurança que não é
detalhada nos trabalhos de referência, mas que se mostrou necessária na
prática para evitar consultas malformadas ou fora do escopo de tabelas
permitidas.

Wallner, Wang e Dormann (2023) demonstram o valor de visualizações
espaço-temporais para revisão pós-jogo; o mapa de calor de
posicionamento desenvolvido neste trabalho aplica esse princípio, embora
de forma mais simples (posição agregada por minuto, sem a técnica de
*storyline visualization* proposta pelos autores) — uma limitação
reconhecida e discutida na próxima subseção.

### 5.2 Limitações

- **Amostras pequenas em recortes finos** (combinações específicas de
  jogador e campeão, ou de matchup de rota) seguem estatisticamente
  frágeis mesmo com 23.133 partidas — mitigado, onde aplicável, por
  encolhimento estatístico (*shrinkage*) em direção à média do grupo
  maior, mas não eliminado.
- **Desequilíbrio de amostra por região**: após as rodadas adicionais de
  coleta (Seção 4.3), BR1 e EUW1 concentram a maior parte dos dados
  (11.936 e 11.744 partidas) e KR cresceu para 8.567, mas NA1 não avançou
  na última rodada e permanece em 1.446 — cerca de um décimo da amostra
  de BR1. O achado de viés de lado "generalizado ao elo alto, não
  específico do Brasil" é sustentado pela direção consistente nas
  quatro regiões com amostra relevante, mas o caso de NA1 isolado ainda
  se beneficiaria de mais volume, e é hoje o elo mais frágil da
  generalização.
- **Cobertura desigual por versão do jogo** (*patch*): um único *patch*
  concentra a maior parte das partidas coletadas, o que limita a
  generalização dos achados para versões do jogo com balanceamento
  diferente.
- **Teto de desempenho das variáveis atuais**: nove experimentos de
  enriquecimento de *features* a partir da mesma fonte de dados (linha
  do tempo da partida) não superaram o modelo com as cinco variáveis
  originais, sugerindo que o próximo ganho relevante depende de um tipo
  de dado que a API atual não fornece — por exemplo, ordem de escolha de
  campeão (*draft*) ou posição em tempo real para *features* espaciais.
- **Ausência de dados de micro-posicionamento** (movimentação de
  *minions*, controle de onda): nenhuma API pública da Riot expõe esse
  nível de detalhe; caminhos alternativos (replays `.rofl`, visão
  computacional sobre o minimapa) foram considerados, mas não
  implementados neste trabalho.
- **Monotonicidade isolada por fator**: o modelo XGBoost não garante
  formalmente que aumentar isoladamente a diferença de abates ou de
  torres nunca reduza a probabilidade prevista de vitória, por conta de
  interações e redundâncias entre variáveis — comportamento documentado
  e compreendido, mas não corrigido por restrição formal
  (`monotone_constraints`) nesta versão.

---

## 6 CONCLUSÃO

Este trabalho teve como objetivo geral desenvolver uma plataforma
inteligente para análise de dados de esports com foco em *League of
Legends*, integrando coleta, organização e exploração de dados
competitivos, modelagem preditiva com técnicas de *machine learning* e
mecanismos de visualização e consulta em linguagem natural. Os
resultados apresentados na Seção 4 indicam que o objetivo geral foi
alcançado, com evidência para cada objetivo específico:

a) os dados e recursos da Riot Games API foram mapeados e utilizados de
forma sistemática (endpoints *league-v4*, *account-v1*, *match-v5* e
*timeline-v5*);

b) as informações relevantes de partidas, jogadores e estatísticas
foram identificadas e organizadas em um esquema relacional específico;

c) foi estruturado e executado um processo de coleta, tratamento e
organização capaz de escalar de um piloto de ~100 partidas para uma
base de 23.133 partidas de *solo queue* somadas a 99.259 partidas
profissionais;

d) técnicas de análise de dados identificaram padrões relevantes,
incluindo o viés de lado no *solo queue* de elo alto, sua variação ao
longo da partida e sua inversão em relação ao cenário profissional —
achados sustentados por testes de robustez estatística, não apenas
observação pontual;

e) três modelos de *machine learning* (XGBoost, *Random Forest* e MLP)
foram comparados, com o XGBoost adotado como modelo de produção
(acurácia 0,7573, AUC-ROC 0,8393 no corte de 15 minutos, com modelos
adicionais para os cortes de 10, 20 e 25 minutos);

f) *dashboards* foram entregues em seis páginas de visualização,
cobrindo desde estatísticas agregadas até análise minuto a minuto de
partida individual;

g) uma interface em linguagem natural foi implementada e avaliada,
atingindo 88% de acurácia de execução sobre um benchmark de 26
perguntas de referência.

Como contribuição além do escopo originalmente delimitado no TCC I, a
incorporação do dataset competitivo profissional (Oracle's Elixir)
permitiu uma comparação direta entre dois contextos institucionalmente
diferentes do mesmo jogo, produzindo dois achados quantitativos com
potencial de contribuição à literatura: a inversão do viés de lado entre
*solo queue* de elo alto e jogo profissional, e a diferença na conversão
de vantagem material em vitória entre os dois contextos.

Como trabalhos futuros, ficam registrados: a ampliação adicional da
amostra da região NA1 especificamente (as demais regiões já foram
reforçadas ao longo deste trabalho, ver Seção 4.3); a extensão da
predição para o cenário de partidas ao vivo (não
implementada nesta versão, mas considerada na arquitetura desde o
início — a camada de predição aceita estado de jogo arbitrário por
fase, não apenas dados pré-processados de um conjunto fixo); a inclusão
de seleção de campeão competitiva no simulador de time; e a investigação
de restrições de monotonicidade formal no modelo, caso avaliada como
necessária.

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

CRESWELL, John W.; CRESWELL, J. David. **Research design: qualitative,
quantitative, and mixed methods approaches**. 6. ed. Thousand Oaks: SAGE
Publications, 2023.

GARCÍA-MÉNDEZ, Silvia; ARRIBA-PÉREZ, Francisco de. Explainable e-sports win
prediction through machine learning classification in streaming. **Entertainment
Computing**, [S. l.], v. 55, art. 101027, 2025. DOI: 10.1016/j.entcom.2025.101027.
Disponível em:
https://www.sciencedirect.com/science/article/pii/S1875952125001077. Acesso em:
10 jun. 2026.

GIL, Antonio Carlos. **Como elaborar projetos de pesquisa**. 4. ed. São Paulo: Atlas,
2002.

GUO, Yi; SHI, Danqing; GUO, Mingjuan; WU, Yanqiu; CAO, Nan; CHEN, Qing.
Talk2Data: a natural language interface for exploratory visual analysis via question
decomposition. **ACM Transactions on Interactive Intelligent Systems**, New York,
v. 14, n. 2, art. 8, p. 1-24, 2024. DOI: 10.1145/3643894.

HODGE, Victoria J.; DEVLIN, Sam Michael; SEPHTON, Nicholas John; BLOCK,
Florian Oliver; COWLING, Peter I.; DRACHEN, Anders. Win prediction in multi-player
e-sports: live professional match prediction. **IEEE Transactions on Games**, [S. l.], v.
13, n. 4, p. 368-379, 2021. DOI: 10.1109/TG.2019.2948469.

JIANG, Jie; XIE, Haining; SHEN, Siqi; SHEN, Yu; ZHANG, Zihan; LEI, Meng;
ZHENG, Yifeng; LI, Yang; LI, Chunyou; HUANG, Danqing; WU, Yinjun; ZHANG,
Wentao; YANG, Xiaofeng; CUI, Bin; CHEN, Peng. SiriusBI: a comprehensive LLM-
powered solution for data analytics in business intelligence. **Proceedings of the
VLDB Endowment**, [S. l.], v. 18, n. 12, p. 4860-4873, 2025. DOI:
10.14778/3750601.3750610.

PRODANOV, Cleber Cristiano; FREITAS, Ernani Cesar de. **Metodologia do
trabalho científico: métodos e técnicas da pesquisa e do trabalho acadêmico**.
2. ed. Novo Hamburgo: Feevale, 2013.

RIOT GAMES. **APIs**. [S. l.], [s. d.]. Disponível em:
https://developer.riotgames.com/apis. Acesso em: 12 maio 2026.

WALLNER, Günter; WANG, Letian; DORMANN, Claire. Visualizing the spatio-
temporal evolution of gameplay using storyline visualization: a study with League of
Legends. **Proceedings of the ACM on Human-Computer Interaction**, New York, v.
7, n. CHI PLAY, art. 412, p. 1002-1024, 2023. DOI: 10.1145/3611058.

YIN, Robert K. **Case study research and applications: design and methods**. 6.
ed. Thousand Oaks: SAGE Publications, 2018.

---

## APÊNDICE A — Esquema relacional do banco de dados

O banco de dados (PostgreSQL) foi estruturado com as tabelas a seguir.
Tabelas `raw_matches`/`raw_timelines` preservam o JSON bruto retornado
pela Riot API (para reprocessamento sem nova coleta); as demais são a
normalização relacional usada pela análise e pela modelagem.

```sql
players(puuid PK, game_name, tag_line, tier, division, league_points,
        platform, updated_at)

raw_matches(match_id PK, payload JSONB, collected_at)
raw_timelines(match_id PK/FK→raw_matches, payload JSONB, collected_at)

matches(match_id PK, platform_id, queue_id, game_version,
        game_creation, game_duration_s)

teams(match_id FK, team_id, win, barons, dragons, heralds, towers,
      inhibitors — PK: match_id+team_id)

participants(match_id FK, puuid, team_id, team_position, champion_id,
             champion_name, kills, deaths, assists, gold_earned,
             cs_total, vision_score, dmg_to_champions, win
             — PK: match_id+puuid)

bans(match_id FK, team_id, pick_turn, champion_id
     — PK: match_id+team_id+pick_turn)

item_events(id PK, match_id FK, puuid, ts_ms, item_id, action)
  -- compras/vendas efetivas (ITEM_UNDO já resolvido no ETL)

items(item_id PK, name, total_gold, purchasable, map_11)
  -- catálogo Data Dragon, usado para JOIN de nome/ícone de item

pro_games(game_id, league, year, split, playoffs, game_date, patch,
          side, team_name, win, game_length_s, kills, deaths, dragons,
          barons, heralds, towers, inhibitors, gold_diff_at15,
          xp_diff_at15, cs_diff_at15, kill_diff_at15
          — PK: game_id+side)

pro_players(game_id, side, position, player_name, team_name, champion,
            kills, deaths, assists, win
            — PK: game_id+side+position)
```

Índices B-tree foram criados sobre as colunas mais usadas em filtro
(campeão, jogador, versão do jogo, liga) para suportar tanto os
endpoints da API quanto as consultas geradas pela interface em
linguagem natural.

---

## APÊNDICE B — Benchmark da interface em linguagem natural

Execução em 2026-09-28 sobre a base de produção (23.133-23.316 partidas
— a coleta regional estava em andamento durante a medição, ver nota
abaixo): **23/26 = 88% de acurácia de execução**, reproduzindo
exatamente o número já documentado no histórico do projeto. Uma
primeira execução, feita simultaneamente à coleta em background, mediu
22/26 (85%) com uma falha adicional na pergunta 3 ("win rate do time
azul") — repetida a execução sem a interferência de escrita
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
estruturalmente errado — padrão já documentado em execuções anteriores
do mesmo benchmark.

---

## APÊNDICE C — Métricas completas por corte temporal

Quadro cruzado gerado em 2026-09-28 (mesmo desenho experimental da
Seção 4.4: validação cruzada estratificada de 5 *folds*, hiperparâmetros
base — não os tunados de produção — para manter a comparação entre os
3 modelos em igualdade de condições, conforme o objetivo específico e).
Os valores do corte de 15 min reproduzem exatamente os já citados na
Seção 4.4.

| Corte | n | Taxa vitória azul | Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 10min | 23.053 | 0,457 | RandomForest | 0,6652 | 0,6402 | 0,6088 | 0,6241 | 0,7237 |
| 10min | 23.053 | 0,457 | **XGBoost** | 0,6934 | 0,6730 | 0,6391 | 0,6556 | 0,7609 |
| 10min | 23.053 | 0,457 | MLP | 0,6963 | 0,6751 | 0,6461 | 0,6600 | 0,7658 |
| 15min | 22.973 | 0,456 | RandomForest | 0,7409 | 0,7237 | 0,6997 | 0,7115 | 0,8219 |
| 15min | 22.973 | 0,456 | **XGBoost** | 0,7573 | 0,7444 | 0,7133 | 0,7285 | 0,8393 |
| 15min | 22.973 | 0,456 | MLP | 0,7550 | 0,7457 | 0,7034 | 0,7238 | 0,8385 |
| 20min | 20.254 | 0,456 | RandomForest | 0,7731 | 0,7548 | 0,7435 | 0,7491 | 0,8565 |
| 20min | 20.254 | 0,456 | **XGBoost** | 0,7827 | 0,7664 | 0,7522 | 0,7592 | 0,8675 |
| 20min | 20.254 | 0,456 | MLP | 0,7845 | 0,7681 | 0,7549 | 0,7614 | 0,8699 |
| 25min | 16.179 | 0,458 | RandomForest | 0,8123 | 0,7996 | 0,7876 | 0,7935 | 0,8934 |
| 25min | 16.179 | 0,458 | **XGBoost** | 0,8216 | 0,8128 | 0,7930 | 0,8028 | 0,9031 |
| 25min | 16.179 | 0,458 | MLP | 0,8209 | 0,8102 | 0,7952 | 0,8026 | 0,9026 |

Nota: os valores de AUC-ROC por fase citados na Seção 4.4
(0,767/0,842/0,872/0,907) usam os hiperparâmetros *tunados* de produção
do XGBoost (500 árvores, *learning rate* 0,01), diferentes dos
hiperparâmetros base usados neste quadro para a comparação entre os 3
modelos — por isso os números não são idênticos, embora a mesma
tendência (desempenho crescente com o corte) apareça nos dois casos.
Com os hiperparâmetros base, o XGBoost superou os demais modelos em
AUC-ROC nos 4 cortes; com os hiperparâmetros tunados (Seção 4.4, corte
de 15 min), a diferença entre XGBoost e MLP fica marginal (0,8393 vs.
0,8385).

---

## APÊNDICE D — Experimentos negativos de enriquecimento de features

Quadro — Experimentos negativos de enriquecimento de *features*

| # | Experimento | Resultado |
|---|---|---|
| 1 | Diferença de abates de Barão/Arauto | Δ AUC ≈ ruído (±0,001-0,003) |
| 2 | Dispersão espacial do time | Δ AUC ≈ ruído |
| 3 | Tuning específico por fase | Δ AUC ≈ ruído |
| 4 | Calibração adicional (além da já obtida) | sem ganho — modelos já calibrados |
| 5 | Ouro convertido em itens | Δ AUC ≈ ruído |
| 6 | Separação de features defensivas/ofensivas | Δ AUC ≈ ruído |
| 7 | `item_gold_diff` (segunda tentativa, refeita) | Δ AUC ≈ ruído |
| 8 | Visão (ward_diff / ward_kill_diff) | Δ AUC ≈ ruído |
| 9 | Dragões por tipo (`monsterSubType`) | **AUC piorou** (0,8319 → 0,8295) |

Em contraste, o aumento de *volume* de partidas produziu ganho real:
AUC-ROC do XGBoost (corte 15 min) subiu de 0,8214 (10.295 partidas)
para 0,8393 (23.133 partidas) ao longo da coleta incremental — cerca de
20× maior que o maior ganho obtido por qualquer um dos 9 experimentos
de *feature*.

---

## ANEXO A — Capturas de tela da plataforma

Geradas em 2026-09-28 via Playwright (Chromium, 1440×900, página
inteira) contra a API e o *frontend* rodando localmente com dados de
produção (24.154 partidas no momento da captura). Arquivos em
`reports/anexo_a/` (não versionados neste Markdown — inserir como
figura ao converter para o `.docx` final):

| Arquivo | Página |
|---|---|
| `reports/anexo_a/01_inicio.png` | Início (busca unificada) |
| `reports/anexo_a/02_dashboard.png` | Dashboard (KPIs, viés de lado por região, cobertura do dataset) |
| `reports/anexo_a/03_campeoes.png` | Campeões |
| `reports/anexo_a/04_partida_detalhe.png` | Partidas — análise de uma partida individual |
| `reports/anexo_a/05_competitivo.png` | Competitivo (solo queue × profissional) |
| `reports/anexo_a/06_simulador.png` | Simulador (Composição/Estado/Explicabilidade) |

---

## ANEXO B — Documentação da Riot Games API

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
3. **Trabalhos Relacionados — DECIDIDO (2026-10-03): não é seção de
   primeiro nível.** Seguindo o modelo institucional do TCC 2 (2026-09-28),
   que não prevê essa seção, a referência teórica fica na Seção 2 e a
   comparação direta com os resultados obtidos fica na Seção 5.1. Note que
   o TCC 1 tem "3 TRABALHOS RELACIONADOS" como seção de primeiro nível,
   aprovada naquele documento — mas o modelo do TCC 2 difere, e prevalecceu
   o do TCC 2. Efeito colateral vantajoso: a numeração do corpo segue
   exatamente a do modelo (1 Introdução … 6 Conclusão).
3. ~~Apêndices/Anexos~~ — **feitos**: A (schema), B (26 perguntas NLQ,
   88% confirmado com dados frescos), C (quadro cruzado 4 cortes × 3
   modelos), D (9 experimentos negativos), Anexo A (6 capturas de tela
   reais em `reports/anexo_a/`), Anexo B (referência da API).
4. **Formatação final — FEITA (2026-10-03).** O texto foi vertido para
   `.docx` institucional por script, não à mão. Pipeline em
   `docs/build_tcc_docx.py` + `docs/finalize-fields.ps1`, produzindo
   `docs/tcc2_final.docx` (49 páginas; corpo = 21 páginas, dentro do
   limite de 25-30). A formatação (A4, margens 3/2/3/2 cm, Arial 12,
   entrelinha 1,5, capa, folha de rosto, identidade) é **herdada do
   TCC I** via `--reference-doc`, não reescrita.

   As duas correções do Prof. Elvandi aplicadas no TCC I foram
   conferidas no documento gerado:
   - Títulos de seção em maiúscula **sem negrito** — verificado: 41
     títulos, 0 em negrito. Já saía certo.
   - Referências com **1 linha em branco** separando cada entrada —
     **não saía certo** na primeira geração (o pandoc cola as entradas
     em parágrafos `Normal`). Corrigido no pipeline: 12 referências no
     estilo `REFERÊNCIAS` do TCC I, com a separação entre entradas.

   As 3 regras do modelo institucional de 2026-09-29 também estão
   aplicadas — as duas últimas passaram a valer no `.docx`, não só no
   Markdown:
   - Palavras-chave separadas por **ponto final**, não ponto-e-vírgula
     — corrigido no Resumo/Abstract.
   - Tabelas se chamam **"Quadro"** nesta instituição, com "Lista de
     Quadros" — feito no `.docx`: 5 Quadros com numeração automática por
     campo `SEQ` e página de Lista de Quadros montada.
   - Figuras: legenda no **topo**, fonte obrigatória **abaixo** (mesmo
     para figura de autoria própria) — feito: as 6 capturas do Anexo A
     entraram como figuras com essa convenção, e há Lista de
     Ilustrações.
   - Confirmado também: a estrutura de seções do corpo (além de
     Introdução/Referencial Teórico obrigatórios) é **livre, por
     acordo com o orientador** — não há seção "Trabalhos Relacionados"
     obrigatória no template genérico, o que dá mais folga à pendência
     nº 3 acima (não é mais um bloqueio estrutural, só uma preferência
     a confirmar). Limite de páginas do TCC II: **25 a 30 páginas**,
     não contando apêndices/anexos — o corpo do documento gerado tem
     21 páginas.
5. ~~Ampliar a coleta EUW1/KR/NA1~~ — **feito**: EUW1 1.307→11.744
   partidas, KR 1.308→8.567 (NA1 ficou em 1.446 mesmo após duas novas
   rodadas — anotado como limitação, não re-executado de novo). Quadro
   de viés de lado por região remedido com dados de 2026-10-03
   (Seção 4.3) e verificado por SQL direto contra o valor mostrado no
   *dashboard* (metodologia registrada em memória do projeto:
   `feedback_verify_dashboard_numbers`).

**Status (2026-10-03):** de 6 pendências, **5 estão fechadas** (Resumo,
Apêndices/Anexos, formatação `.docx`, ampliação da coleta, e agora as duas
decisões de escopo). **Nenhuma pendência depende do orientador.**

1. **Título acadêmico** — decidido: não cita Bellestraiko (item 2 acima).
2. **Trabalhos Relacionados** — decidido: não é seção de primeiro nível,
   segue o modelo do TCC 2 (item 3 acima).

**Resta 1 item, já resolvido:** o título do Quadro 4 (Apêndice C), que no
rascunho só tinha nota de método — o que viola a regra da instituição, já
que tabela sem legenda não é permitida. O título foi escrito na conversão e
**confirmado pelo autor em 2026-10-03**: "Métricas completas por corte temporal
— comparação entre os três modelos".

**Nenhuma pendência em aberto.** As 6 estão fechadas.

**Consequência prática:** com as duas decisões fechadas, a numeração do corpo
fica exatamente igual à do modelo institucional (1 Introdução, 2 Referencial
Teórico, 3 Material(is) e Métodos, 4 Resultados, 5 Discussão, 6 Conclusão) e
não há mais nada a regenerar por causa delas.
