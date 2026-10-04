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
linguagem natural. Foram coletadas e organizadas 41.063 partidas
ranqueadas de elo alto (cinco regiões) via Riot Games API, e
incorporadas 96.716 partidas profissionais (2014-2026, Oracle's
Elixir). A análise descritiva usa a base completa; os modelos foram
treinados sobre as 39.426 partidas disponíveis quando o conjunto de
*features* foi congelado, diferença registrada como limitação na Seção 5.8.
Três modelos — XGBoost, *Random Forest* e uma rede neural
(MLP) — foram treinados e comparados para predizer o vencedor a partir
do estado da partida em quatro cortes temporais (10, 15, 20 e 25
minutos), com o XGBoost alcançando o melhor desempenho no corte de 15
minutos (acurácia de 0,7621; AUC-ROC de 0,8473). A análise exploratória
identificou que o time vermelho é favorecido no *solo queue* de elo
alto (56,3% de vitórias na região com maior amostra), um padrão de
magnitude estável ao longo da partida e que se inverte no cenário
profissional (onde o time azul vence 53,2% das partidas, padrão estável
desde 2016) — achado sustentado por testes de robustez
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
mechanisms. A total of 41,063 high-elo ranked matches (five regions)
were collected and organized through the Riot Games API, complemented
by 96,716 professional matches (2014-2026, Oracle's Elixir). The
exploratory analysis uses all 41,063; the predictive models were built
on the 39,426 matches available when the feature set was frozen, a
difference registered as a limitation in Section 5.8. Three
models — XGBoost, Random Forest and a neural network (MLP) — were
trained and compared to predict the winning team from the match state
at four time cutoffs (10, 15, 20 and 25 minutes), with XGBoost
achieving the best performance at the 15-minute cutoff (accuracy of
0.7621; AUC-ROC of 0.8473). The exploratory analysis identified that
the red side is favored in high-elo solo queue (56.3% win rate in the
region with the largest sample), a pattern of nearly constant magnitude
along the match that reverses in the professional scenario (where
the blue side wins 53.2% of matches, stable from 2016 on) — a
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
A Seção 2 apresenta a fundamentação teórica, reunindo os principais
conceitos relacionados a esports, análise de dados, *machine
learning*, explicabilidade, interfaces em linguagem natural e
visualização analítica. A Seção 3 descreve os trabalhos relacionados
que sustentam a pesquisa, identificando o objeto, a abordagem e o que
cada um deixa em aberto. A Seção 4 descreve a metodologia
utilizada no desenvolvimento da plataforma. A Seção 5 apresenta os
resultados obtidos e os analisa à luz da literatura e das limitações
identificadas. A Seção 6 apresenta as considerações finais. Por fim,
são apresentadas as referências utilizadas na construção deste
trabalho.

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

## 2 FUNDAMENTAÇÃO TEÓRICA

A fundamentação teórica deste trabalho reúne os principais conceitos
necessários para compreender a proposta de uma plataforma inteligente
para análise de dados de esports com foco em *League of Legends*.
Considerando a natureza interdisciplinar do tema, a seção articula
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

Esta seção é conceitual: define os conceitos e os termos usados no
restante do trabalho. Duas famílias de referência são usadas aqui, com
papéis distintos. As obras originais dos métodos que este trabalho aplica
— Random Forest, XGBoost, AUC-ROC, SHAP, LIME e conversão de linguagem
natural em SQL — são citadas no ponto em que o método é introduzido, nas
subseções 2.2 a 2.4, porque o que importa ali é a propriedade técnica que
justifica o uso. Os estudos de contexto do domínio, estes sim com objeto,
abordagem e resultados, são descritos autor a autor na Seção 3.

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

### 2.2 FAMÍLIAS DE MODELOS PREDITIVOS E SUA APLICAÇÃO EM ESPORTS

A aplicação de *machine learning* em esports tem se mostrado promissora
em tarefas como predição de vitória, avaliação de desempenho e
identificação de padrões competitivos. Em *League of Legends*, Birant e
Birant (2023) indicam que a modelagem centrada no time — e não no
jogador isolado — é uma abordagem relevante para compreender os
resultados das partidas. Bahrololloomi et al. (2022) percorrem caminho
distinto, analisando o desempenho dos jogadores a partir de funções
(*roles*) em jogo e de métricas individuais de desempenho.

As duas leituras delimitam o espaço de escolha da modelagem preditiva,
mas não decidem qual família de modelos é adequada a este problema. Este
trabalho comparou três famílias, e o critério dessa escolha é de
natureza técnica, não de preferência.

A primeira são os ensembles de árvores de decisão, e em particular a
*Random Forest* (Breiman, 2001). A construção combina *bagging* — cada
árvore é treinada sobre uma amostra *bootstrapeada* do conjunto — com a
seleção de um subconjunto aleatório de variáveis em cada nó de partição.
A segunda restrição é a que dá origem ao nome: ela força as árvores a
divergirem entre si, o que reduz a correlação dos erros individuais e,
com isso, a variância do conjunto final. Para um problema como o deste
trabalho, em que as variáveis preditoras são agregados de desempenho
fortemente correlacionados entre si — ouro, abates e torres evoluem
juntos ao longo da partida —, essa decorrelação é diretamente relevante.

A segunda família é o *gradient boosting*, representado aqui pelo
XGBoost (Chen e Guestrin, 2016). Em vez de construir árvores de forma
independente e combinar suas respostas, o método constrói árvores
sequencialmente, cada uma ajustada ao resíduo acumulado das anteriores. O
XGBoost formaliza esse procedimento como otimização de segunda ordem —
cada passo usa tanto o gradiente quanto a curvatura da função de perda — e
introduz controles explícitos de regularização, que são o que torna o
método utilizável com árvores profundas sem sobreajustar. Para dados
tabulares, que é o formato que as *features* deste trabalho produzem,
essa família costuma apresentar desempenho superior ao de ensembles por
agregação.

A terceira são as redes neurais *feedforward*, ou perceptrons multicamada
(MLP). Compostas por camadas de transformações não lineares, têm
capacidade de aproximação universal e capturam interações complexas
entre variáveis sem que essas interações precisem ser especificadas. Em
troca, exigem mais dados e mais cuidado com escala e regularização para
não sobrarjetar — restrição que se mostra determinante quando a amostra
disponível é da ordem de dezenas de milhares de observações e não de
milhões.

As três famílias foram comparadas sob o mesmo desenho experimental: os
mesmos dados, o mesmo particionamento e os mesmos cortes temporais. O
resultado da comparação é reportado na Seção 5, e o que se pode afirmar
nesta seção é apenas o critério adotado — a escolha entre elas não foi
feita por preferência, e sim mediante medição.

### 2.3 EXPLICABILIDADE E AVALIAÇÃO DE MODELOS PREDITIVOS

Além de produzir previsões, sistemas analíticos voltados a esports
precisam oferecer mecanismos que favoreçam a interpretação dos
resultados gerados. García-Méndez e Arriba-Pérez (2025) mostram que
abordagens de predição explicável podem combinar classificação e
interpretação, tornando *dashboards*, descrições e fatores relevantes
da previsão mais compreensíveis para o usuário final.

Explicar a decisão de um ensemble, porém, não é uma tarefa trivial: a
saída final resulta da soma de centenas de árvores, e a contribuição
individual de cada variável não é diretamente legível. Duas famílias de
métodos endereçam essa questão, e é útil nomeá-las porque elas respondem
a perguntas diferentes.

A primeira aproxima o comportamento do modelo por perturbações locais da
entrada. LIME (Ribeiro, Singh e Guestrin, 2016) é o exemplo de
referência: constrói um modelo linear local, e portanto simples de
interpretar, que aproxima o classificador complexo na vizinhança de cada
instância. A vantagem é a simplicidade do resultado; o custo é que a
explicação descreve um comportamento local, e a escolha da vizinhança
influencia o que se vê.

A segunda recorre à teoria dos jogos e ao valor de Shapley, e define a
importância de cada variável como sua contribuição média para a
previsão, calculada sobre todas as combinações possíveis das demais
variáveis. Lundberg e Lee (2017) unificam essa família de medidas e
mostram que existe uma solução única dentro dela com um conjunto de
propriedades desejáveis — entre elas a consistência e a imposibilidade
de atribuir importância a uma variável ausente da entrada. SHAP
(*SHapley Additive exPlanations*) é a implementação dessa unificação, e
foi o mecanismo adotado neste trabalho. A escolha se justifica por uma
razão prática: como a atribuição é sempre somada à previsão e o
resultado é explicável em linguagem aditiva, os valores de SHAP
permitem montar a explicação textual da plataforma a partir dos
contribuições efetivamente calculados — e não a partir de conhecimento
genérico sobre o jogo. A honestidade dessa separação é tratada na
Seção 4.

A avaliação dos modelos apresentados na seção anterior exige ainda
uma escolha metodológica sobre a métrica. Com classes praticamente
balanceadas (46,6% de vitória azul contra 53,4%), a acurácia isolada é
enganosa: um classificador que sempre responde "vitória do time azul"
alcança 46,6% — a própria taxa-base da amostra — sem qualquer poder
preditivo. Por esse motivo a avaliação deste trabalho se apoia na área
sob a curva da característica operacional do receptor (AUC-ROC), que
mede a capacidade de discriminação do modelo em todos os limiares de
decisão e, consequentemente, independe da escolha de um limiar
específico. Hanley e McNeil (1982) demonstram que essa medida é
equivalente à probabilidade de que um caso positivo receba uma
pontuação maior que a de um caso negativo, o que a torna interpretável
diretamente como proporção de pares corretamente ordenados. AUC-ROC e
acurácia são reportados conjuntamente na Seção 5 justamente para tornar
essa distinção visível nos números.

### 2.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

A utilização de interfaces em linguagem natural tem ampliado as
possibilidades de interação com sistemas analíticos, reduzindo a
barreira técnica entre o usuário e os dados. Jiang et al. (2025)
observam que soluções de *Business Intelligence* apoiadas por modelos
de linguagem podem favorecer a exploração de dados estruturados. Guo et
al. (2024) também destacam que mecanismos de diálogo, decomposição de
perguntas e análise visual podem tornar a exploração dos dados mais
intuitiva e eficiente.

O problema técnico central dessa interface é a geração de consultas.
Um modelo de linguagem produz texto, e o banco exige SQL sintaticamente
válido e semanticamente correto sobre um esquema específico — dois
requisitos que falham de maneiras diferentes. O modelo pode escrever uma
consulta gramaticalmente correta que referencia uma tabela inexistente, e
também pode produzir uma estrutura válida que responde à pergunta
errada. Wang et al. (2020) tratam esse segundo caso, que é o mais
difícil, mostrando que representações do esquema que incorporate os
relacionamentos entre tabelas — e não apenas os nomes das colunas —
melhoram de forma consistente a precisão da conversão, inclusive quando
o esquema é amplo ou as perguntas ambíguas.

Este trabalho implementou uma interface de linguagem natural capaz de
traduzir perguntas em português para consultas SQL validadas contra o
esquema real do banco de dados, integrando visualização, recuperação de
informações e geração de descobertas em uma mesma plataforma. A
validação não é delegada ao modelo: a consulta gerposta é submetida a
uma checagem em quatro camadas antes de tocar o banco, descrita na
Seção 4. Os resultados de acurácia dessa interface são apresentados na
Seção 5.

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
apresentado na análise de partida da plataforma (Seção 5.5).

Os estudos citados nesta seção são apresentados, autor a autor, na
Seção 3. A confrontação direta entre eles e os resultados obtidos
neste trabalho é feita na Seção 5.7 — é lá que a leitura crítica faz
sentido, porque só há o que confrontar depois que os resultados estão
apresentados.

---

## 3 TRABALHOS RELACIONADOS

A seção anterior define os conceitos mobilizados por esta pesquisa;
esta seção descreve os estudos que os sustentam. Para cada um, são
apresentados o objeto, a abordagem adotada e a contribuição
relevante para o problema aqui tratado. São sete estudos de domínio, todos
citados ao longo do trabalho — nenhum foi incluído apenas para preencher
esta seção. As obras de método (Breiman, 2001; Chen e Guestrin, 2016;
Hanley e McNeil, 1982; Lundberg e Lee, 2017; Ribeiro, Singh e Guestrin,
2016; Wang et al., 2020) não aparecem aqui: são textos de técnica, não de
domínio, e estão citados na Seção 2, no ponto em que o método que eles
fundamentam é introduzido.

### 3.1 ESPORTS COMO FENÔMENO DE PRODUÇÃO E ANÁLISE DE DADOS

Hodge et al. (2021) tratam da predição de vitória em esports com
múltiplos jogadores (*multi-player*), em partidas profissionais e em
tempo real, e relatam que o desempenho preditivo é favorecido pelo uso
de análise estruturada dos dados de partida. O trabalho estabelece,
portanto, a viabilidade da predição de resultados em esports como
problema tratável por modelagem estatística, e é a referência que
sustenta, no domínio de *League of Legends*, o tratamento dos dados
de partida como objeto de análise neste trabalho.

### 3.2 MACHINE LEARNING APLICADO A LEAGUE OF LEGENDS E ESPORTS

Birant e Birant (2023) apresentam uma abordagem de aprendizado
multi-objetivo e multi-instância (*Multi-Objective Multi-Instance
Learning*) aplicada a esports, e destacam a modelagem centrada no time —
e não no jogador isolado — como caminho para compreender resultados de
partidas. É a abordagem que este trabalho adotou diretamente ao
construir as variáveis preditoras como diferenças agregadas entre os
dois times (ouro, experiência, abates, torres, dragões), em vez de
métricas individuais de jogador.

Bahrololloomi et al. (2022) percorrem caminho distinto: analisam o
desempenho de jogadores de *League of Legends* com técnicas de
*machine learning*, tomando como entrada as funções (*roles*) em
jogo e as métricas individuais de desempenho, com foco na predição
de vitória.

Os dois estudos são complementares e delimitam o espaço de escolha da
modelagem preditiva em *League of Legends*: um nível de agregação
por time e um nível de agregação por jogador. Este trabalho
adota o primeiro como eixo da modelagem preditiva, e usa o segundo
apenas na camada de perfis de jogador, conforme descrito na Seção 5.7.

### 3.3 EXPLICABILIDADE E ANÁLISE PREDITIVA

García-Méndez e Arriba-Pérez (2025) abordam a predição de vitória em
esports sob a perspectiva da explicabilidade, combinando
classificação por *machine learning* com mecanismos de interpretação,
inclusive em cenário de transmissão (*streaming*). A contribuição
relevante para este trabalho é o argumento de que um sistema
preditivo só é útil ao usuário final quando acompanha a previsão de
uma explicação dos fatores que a sustentam — pressuposto que orienta
a camada de explicabilidade da plataforma descrita na Seção 5.5.

### 3.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

Jiang et al. (2025) apresentam o SiriusBI, solução de *Business
Intelligence* apoiada por modelos de linguagem para análise de dados
em contextos corporativos. Guo et al. (2024) apresentam o Talk2Data,
interface em linguagem natural para análise visual exploratória,
baseada em decomposição de perguntas. Ambos exploram o uso de modelos
de linguagem como camada de interação sobre dados estruturados, e
ambos são citados aqui como fundamento para o *text-to-SQL*
implementado neste trabalho (Seção 4.7), que estende a abordagem ao
domínio competitivo de *League of Legends*.

### 3.5 VISUALIZAÇÃO ANALÍTICA E DADOS ESPAÇO-TEMPORAIS EM ESPORTS

Wallner, Wang e Dormann (2023) estudam a evolução espaço-temporal do
gameplay em *League of Legends* por meio da técnica de *storyline
visualization*, e mostram o valor de representações que integram
tempo e localização em uma única visualização para a interpretação
pós-jogo. O estudo é a referência para a representação de
posicionamento minuto a minuto adotada na análise de partida da
plataforma (Seção 5.5).

### 3.6 SÍNTESE E POSIÇÃO DESTE TRABALHO

Lidas em conjunto, as referências acima cobrem quatro frentes
isoladas: predição de resultados (Hodge et al.; Birant e Birant;
Bahrololloomi et al.), interpretabilidade da predição (García-Méndez e
Arriba-Pérez), interação em linguagem natural (Jiang et al.; Guo et
al.) e visualização espaço-temporal (Wallner, Wang e Dormann). Nenhuma
delas, isoladamente, é entregue como uma plataforma integrada que reúna
coleta, tratamento, modelagem, explicabilidade, visualização e consulta
em linguagem natural sobre a mesma base de dados. É essa lacuna de
integração que este trabalho propõe ocupar.

A distinção em relação a cada trabalho, porém, não se resume a esse
degrau de integração. Convém explicitar em que eixos o presente trabalho
difere, porque a diferença não está apenas no escopo e sim em decisões
de projeto que alteram o que é possível concluir.

O primeiro eixo é o horizonte da predição. Hodge et al. (2021) operam
sobre partidas profissionais em andamento, e García-Méndez e
Arriba-Pérez (2025) sobre o cenário de transmissão; ambos tratam a
predição como um problema que se resolve enquanto a partida acontece. Este
trabalho também constrói o estado em jogo, mas de forma explícita: a
tarefa é estimar o vencedor a partir de um corte temporal artificial, o
que torna a pergunta mensurável e comparável entre cortes. A diferença
prática é que o modelo deixa de depender de um relógio e passa a depender
de um parâmetro controlável pelo experimento.

O segundo eixo é a natureza da fonte de dados. Os estudos de
*League of Legends* citados partem de bases já estruturadas por
terceiros. Este trabalho coletou a base diretamente da *timeline-v5* da
Riot Games, que é a única fonte que expõe a posição dos eventos e a
evolução minuto a minuto dos recursos em cada partida. Essa granularidade
é o que torna possível a análise espaço-temporal da Seção 5.5. O viés de
lado em si é medido sobre o agregado de vitória por time e região — e, no
recorte de empate, sobre a diferença de ouro —, sem usar coordenada
alguma; o que a *timeline* acrescenta aqui é a análise de uma partida
individual, não a medição do viés.

O terceiro eixo é o recorte de população. Os trabalhos de predição
analisados atuam sobre o cenário profissional. Parte da contribuição
deste trabalho é justamente contrapor a ele o *solo queue* de elo alto, e
mostrar que o padrão de viés de lado observado entre jogadores de rank
não se reproduz no circuito profissional. Sem essa comparação, o achado
seria descrito como uma peculiaridade sem base comparativa.

O quarto eixo é a transparência da camada preditiva. Nenhum dos trabalhos
citados avalia a interface de consulta em linguagem natural contra um
benchmark de perguntas de referência. A implementação aqui descrita é
avaliada com um conjunto fixo de 26 perguntas cuja resposta esperada foi
conferida diretamente contra o banco, o que torna o erro de conversão
mensurável em vez de ilustrativo.

A confrontação entre os resultados aqui obtidos e os resultados relatados
na literatura é apresentada na Seção 5.7.
---

## 4 METODOLOGIA

Esta seção descreve os procedimentos metodológicos efetivamente
empregados no desenvolvimento da pesquisa e da plataforma, detalhando a
natureza do estudo, a coleta e o tratamento dos dados, a modelagem
preditiva e os recursos de visualização e consulta construídos.

### 4.1 NATUREZA E ABORDAGEM DA PESQUISA

O presente trabalho caracteriza-se, quanto à sua natureza, como uma
pesquisa aplicada: Prodanov e Freitas (2013) explicam que a pesquisa
aplicada busca produzir conhecimentos voltados à solução de problemas
específicos e com possibilidade de utilização prática, o que se
concretizou na estruturação de uma plataforma funcional para coletar,
organizar e analisar dados competitivos de *League of Legends*. Quanto
aos objetivos, a pesquisa teve caráter exploratório e descritivo (Gil, 2002): exploratório na investigação inicial sobre a Riot Games API e as
possibilidades de modelagem, e descritivo na caracterização dos dados
coletados, dos padrões identificados e dos modelos comparados. Quanto à
abordagem, a pesquisa adotou perspectiva mista (Creswell; Creswell, 2023): o componente qualitativo esteve presente na revisão
bibliográfica e na interpretação dos achados; o componente quantitativo
esteve associado à coleta e ao tratamento dos dados, à análise
exploratória e à comparação entre os modelos de *machine learning*.

### 4.2 ESTRATÉGIAS DE PESQUISA

O trabalho foi desenvolvido por meio de pesquisa bibliográfica (Gil, 2002), pesquisa documental sobre a documentação oficial da Riot Games
API (Prodanov; Freitas, 2013) e estudo aplicado com recorte de caso no
domínio de *League of Legends* (Yin, 2018).

### 4.3 COLETA DE DADOS

A coleta foi realizada a partir de duas fontes complementares — a
segunda delas incorporada durante a execução do TCC II, ampliando o
escopo originalmente previsto no TCC I:

**a) Riot Games API (dados de partidas ranqueadas — *solo queue*).**
Foram utilizados os endpoints *league-v4* (para identificar jogadores
nos elos Desafiante e Grão-Mestre), *account-v1* (resolução de Riot ID)
e *match-v5*/*timeline-v5* (dados de partida e linha do tempo minuto a
minuto). A coleta abrangeu cinco regiões (BR1, EUW1, KR, NA1 e EUN1, esta
última com amostra insuficiente e excluída da leitura) na fila
420 (ranqueada solo/duo), totalizando **41.063 partidas** normalizadas,
com estado bruto (JSON) preservado em `raw_matches`/`raw_timelines`
para reprocessamento. A chave de desenvolvedor da Riot expira a cada 24
horas, o que exigiu um processo de coleta resumível (script capaz de
retomar de onde parou, pulando partidas já salvas).

**b) Oracle's Elixir (dados de partidas profissionais).** Foram
incorporados **96.716 jogos profissionais** (2014-2026), cobrindo as
principais ligas mundiais (LCK, LPL, LEC, LTA, CBLOL, entre outras), a
partir de arquivos CSV anuais publicados publicamente. Essa fonte não
estava prevista no recorte original do TCC I e foi adicionada para
permitir a comparação entre o padrão observado no *solo queue* de elo
alto e o padrão do cenário competitivo profissional (ver Seção 5.3).

Como o TCC I já delimitava o uso de dados secundários e públicos, não
houve participação direta de sujeitos humanos como fonte de dados em
nenhuma etapa.

### 4.4 ORGANIZAÇÃO E TRATAMENTO DE DADOS

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

### 4.5 ANÁLISE EXPLORATÓRIA DE DADOS

A análise exploratória buscou identificar distribuições, padrões
iniciais e relações entre variáveis relevantes ao problema de pesquisa,
com particular atenção à taxa de vitória por lado do mapa (azul/vermelho)
em diferentes recortes — por região, por fase da partida e por contexto
competitivo (*solo queue* vs. profissional). Todo padrão quantitativo
encontrado nessa etapa foi submetido a testes de robustez antes de ser
aceito como resultado, e o conjunto desses testes é o mesmo para todos os
achados: (i) replicação restrita a uma única região, para descartar efeito
de mistura regional; (ii) comparação contra a duração total da partida,
para descartar confusão com "jogos longos"; (iii) intervalo de confiança
de Wilson sobre a proporção observada, para avaliar a significância
estatística do efeito em amostras menores; e (iv) comparação de pares com
correção de Holm, que corrige a multiplicidade quando várias diferenças
são testadas sobre a mesma base. Este último foi o teste decisivo para o
achado de viés de lado: sem ele, a dispersão entre cortes seria lida como
tendência (ver Seção 5.3). Os resultados dessa análise são apresentados na
Seção 5.3.

### 4.6 MODELAGEM PREDITIVA E COMPARAÇÃO ENTRE MODELOS

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
*features* (ver Seção 5.4) para avaliar se sinais adicionais da linha do
tempo (visão, itens, dispersão espacial do time, objetivos neutros)
melhoravam o poder preditivo além das cinco variáveis de estado já
utilizadas.

### 4.7 PROPOSTA DE VISUALIZAÇÃO E INTERFACE EM LINGUAGEM NATURAL

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
SHAP). As seis telas estão reproduzidas no Anexo A: a Figura 1 mostra a
página inicial, a Figura 2 o painel de indicadores agregados, a Figura 3 o
detalhe de um campeão, a Figura 4 a análise de uma partida, a Figura 5 a
comparação com o cenário profissional e a Figura 6 o simulador com o estado
de jogo e a explicação por SHAP. A interface em linguagem natural foi
implementada como um
pipeline *text-to-SQL*: a pergunta do usuário é traduzida em uma consulta
SQL por um modelo de linguagem (Claude), a consulta é validada
estruturalmente antes da execução (apenas `SELECT`/`WITH...SELECT`,
tabelas permitidas em lista fechada) e o resultado é executado contra o
banco real — nunca respondido a partir de conhecimento genérico do
modelo sobre o domínio. A acurácia dessa interface foi medida por um
benchmark de 26 perguntas de referência com SQL esperado, cobrindo tanto
o dataset de *solo queue* quanto o competitivo.

### 4.8 MATERIAIS E MÉTODOS UTILIZADOS

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

## 5 RESULTADOS E ANÁLISE

Esta seção apresenta os resultados obtidos, organizados de acordo com
os objetivos específicos definidos na Seção 1.4.2.

### 5.1 Mapeamento de dados e recursos da Riot Games API (objetivo a)

Foram mapeados e utilizados os endpoints *league-v4*, *account-v1*,
*match-v5* e *timeline-v5* da Riot Games API, além da documentação
técnica necessária para compreender limitações de taxa de requisição e
o ciclo de expiração da chave de desenvolvedor (24 horas). Esse
mapeamento orientou o desenho de um coletor resumível, capaz de operar
dentro dos limites de taxa e de retomar a coleta entre sessões sem
duplicar dados já salvos.

### 5.2 Estruturação da base de dados (objetivos b e c)

A base usada para treinar e comparar os modelos preditivos (Seção 5.4)
reúne **39.188 partidas** de *solo queue* no corte de 15 minutos,
provenientes das **39.426 partidas** que o banco tinha quando o
conjunto de *features* foi congelado (BR1/EUW1/KR/NA1/EUN1), com JSON
bruto de partida e linha do tempo preservados para reprocessamento, e
**96.716 jogos profissionais**
(2014-2026, Oracle's Elixir). O esquema relacional contempla partidas,
times, participantes, jogadores, banimentos, eventos de item (com
desfazimento de compras/vendas aplicado) e um catálogo de itens para
resolução de nome/ícone sem depender de conhecimento genérico de modelo
de linguagem.

A coleta seguiu de forma incremental e o volume cresceu ao longo do
trabalho: 10.295 partidas na primeira base ampla, 23.133 no retreino de
2026-07-06, 39.426 em 2026-10-04 e 41.063 ao fim do dia, com a região NA1 passando de 1.446
para 7.159 partidas na rodada final — a menor das quatro regiões com
amostra relevante, e a que mais limitava a generalização do achado de
viés de lado (Seção 5.3).

### 5.3 Análise exploratória: padrões identificados (objetivo d)

*(Nota sobre as bases usadas nesta seção e na modelagem: a análise
descritiva — este quadro, o viés de lado e o teste de faixa de duração —
foi medida sobre as **41.063 partidas** que o banco tem ao fim da coleta.
As *features* e os modelos foram construídos antes da última rodada da
KR e usam a base anterior de **39.426 partidas**, das quais 39.309 geraram
*features* e 39.188 chegam ao corte de 15 minutos. Por isso a Seção 5.4,
os Apêndices B e C e o Anexo A citam 39.426. A diferença são 1.637
partidas, quase todas da KR: das 1.754 partidas do banco que ainda não
geraram *features*, 1.647 são da KR e 107 são de três outras regiões.
Os modelos não foram retreinados sobre a base nova — as 1.637 partidas a
mais alterariam a amostra de treino em cerca de 4%, dentro do que a
própria discussão de volume mediu como ganho real, e não justificam
descartar um modelo cujo desempenho já foi medido e validado. É uma
limitação declarada, registrada na Seção 5.8.)*


**Viés de lado no *solo queue* de elo alto.** No agregado das cinco
regiões coletadas, o time vermelho venceu com mais frequência que o
azul, com intensidade variável por região. Medição direta em SQL,
2026-10-04, sobre as 41.063 partidas da base final (o volume foi ampliado
especificamente para fortalecer este quadro — ver nota de método abaixo):

Quadro — Vitória do time vermelho por região

| Região | Partidas | Vitória do vermelho |
|---|---:|---:|
| BR1 | 11.936 | 56,3% |
| EUW1 | 11.744 | 53,4% |
| KR | 10.204 | 50,4% |
| NA1 | 7.159 | 52,2% |
| EUN1 | 20 | 50,0% (amostra insuficiente, não considerada) |

*(Nota de método: quadro original — medido em 2026-07-06 com BR1
11.936, EUW1 1.307, NA1 1.367, KR 1.308 partidas — foi substituído por
uma segunda rodada de coleta destinada especificamente a ampliar
EUW1/KR/NA1, e depois por esta medição de 2026-10-04, quando EUW1 e
KR já haviam quase dobrado novamente e a NA1 também foi ampliada. A
direção do achado (todas as quatro regiões com amostra relevante ficam
do lado do vermelho, entre 50,4% e 56,3%) se manteve idêntica em todas as
quatro medições. A força da evidência, porém, não é uniforme: **três das
quatro** (BR1, EUW1 e NA1) têm taxa de vitória do vermelho cujo intervalo
de 95% exclui 50%, e a KR fica em 50,4% com intervalo [49,5%, 51,4%],
que o inclui — lá o viés não é estatisticamente distinguível de zero. É a
BR1, que sozinha sustenta a assimetria com folga ([55,4%, 57,2%]), que
carrega o argumento de que o padrão não é especificamente brasileiro. Isso
fortalece a leitura de "padrão de elo altíssimo em geral" sem permitir
afirmar que as quatro regiões o demonstram com a mesma força. BR1 não se
alterou em nenhum dos quatro levantamentos. A NA1, que era o elo mais frágil da
generalização, foi ampliada de 1.446 para 7.159 partidas na rodada final
e a taxa do vermelho passou de 51,9% para 52,2% — a direção do achado não
mudou, e a limitação saiu da Seção 5.8.)*

**O viés de lado é estável ao longo da partida — e essa constância é o
resultado.** Uma primeira versão deste texto afirmava que o viés atingia um
pico no meio do jogo e se enfraqueceria até o fim. A medição sobre a base
ampliada de 41.063 partidas **não confirma essa forma**, e o resultado
negativo é relatado aqui em vez de omitido.

Entre as partidas genuinamente empatadas em cada corte (diferença de ouro
menor que 500), a taxa de vitória do time azul foi de 46,4% aos 10
minutos (n = 7.349), 47,9% aos 15 (n = 3.970), 46,7% aos 20 (n = 2.423)
e 47,1% aos 25 (n = 1.430). A dispersão entre os quatro cortes é de 1,4
ponto percentual, e **nenhuma diferença entre pares sobrevive ao ajuste
para múltiplas comparações**: o menor valor-p corrigido é 0,83, para o par
de 10 contra 15 minutos. Os intervalos de confiança de 95% se sobrepõem em
todos os casos. Em outras palavras, as quatro taxas são estatisticamente
indistinguíveis, e o corte mais favorável ao vermelho é o de 10 minutos,
não o de 15.

A mesma conclusão aparece na taxa-base dos modelos, medida no estado de
empate total: 49,2% de probabilidade de vitória azul aos 10 minutos,
49,6% aos 15, 51,4% aos 20 e 49,0% aos 25. A série é plana e não
apresenta o pico vermelho do meio de jogo.

O que sobrevive é o achado principal, e ele é forte: o viés de lado
existe e favorece o time vermelho em magnitude praticamente constante. O
intervalo de confiança do corte de 10 minutos, o de maior amostra, é
[45,3%, 47,6%] e exclui 50% com folga — o viés não é casual em nenhum dos
quatro cortes. O que a base ampliada desfez foi a *evolução* atribuída ao
viés, não o viés.

Os quatro testes de robustez definidos na Seção 4.5 se aplicam todos aqui,
com o desfecho de cada um. O teste (i), de replicação regional, restringe a
análise à BR1 isoladamente e reproduz a assimetria, descartando mistura
O teste (ii), de faixa de duração, confirma que a taxa de vitória
incondicional do **azul** por faixa de duração total de partida
permaneceu estável (medido em 2026-10-04 sobre as 41.063 partidas: 45,6%
a 47,3% entre as faixas de duração, amplitude de 1,7 ponto percentual,
todas abaixo de 50%), o que descarta a hipótese de que "partidas
longas são um tipo diferente de jogo". O teste (iii), o intervalo de Wilson,
está aplicado acima: mostra que nenhum dos quatro cortes admite 50%. E o
teste (iv), a comparação de pares com correção de Holm, é o que sustenta a
afirmação de constância e está detalhado no parágrafo anterior. É ele que
substituiu o teste que antes sustentava a alegação de enfraquecimento,
deixando de ser aplicável quando a forma deixou de existir.

O teste (ii) foi **remedido** em 2026-10-04 sobre a base atual, porque a
medição que o texto usava era de 2026-07-08 e de uma base quase metade
desta: as taxas por faixa de duração total são 46,5% (0 a 25 min, 15.944
partidas), 47,3% (25 a 30, 13.314), 46,4% (30 a 35, 8.364), 45,6% (35 a 40,
2.684) e 47,0% (acima de 40, 757). A amplitude é de 1,7 ponto percentual e
todas as faixas ficam abaixo de 50% — o teste se sustenta, agora com data,
base e amplitude explícitas.

Este resultado negativo tem valor próprio. Um padrão que se dissolve ao
aumentar a amostra era, em verdade, um artefato de tamanho de amostra: as
quatro taxas sempre ficaram próximas umas das outras, mas a amostra menor
permitia que o ruído se desenhasse como tendência. Registrar isso é mais
honesto do que manter a versão anterior, e reforça a principal ressalva
metodológica do trabalho: em corpus de esports, diferença de um ponto
percentual em subamostras de mil partidas não é diferença.

**Comparação com o cenário profissional.** No dataset competitivo
(Oracle's Elixir, 96.716 jogos), o time azul venceu 53,2% das partidas — o
padrão descrito pela literatura geral sobre *League of Legends*. A série
anual é estável a partir de 2016: 53,6% (2016), 55,0% (2017), 53,7%
(2018), 53,2% (2019), 52,7% (2020), 52,6% (2021), 52,5% (2022), 53,3%
(2023), 53,1% (2024), 53,3% (2025) e 53,1% (2026). Os dois primeiros anos
divergem (58,2% em 2014 e 55,3% em 2015), mas apoiadas em amostras muito
menores (814 e 1.702 jogos, contra 96.716 no total), e a diferença é
atribuída a essa assimetria de volume, não a uma mudança no padrão. O viés de lado do
*solo queue* de elo alto vai na direção oposta ao do jogo profissional, o
que constitui um dos achados centrais deste trabalho: a mesma métrica,
medida em dois contextos institucionalmente diferentes, produz sinais
opostos — hipótese de explicação: no *solo queue*, sem coordenação de
*draft* de cinco jogadores, o *counter-pick* garantido do time vermelho (que
escolhe por último) pesa mais; no jogo profissional, a prioridade de
primeira escolha é valorizada o suficiente para influenciar decisões
de lado em *playoffs*.

**Conversão de vantagem.** Com uma vantagem de ouro entre +2.000 e
+4.000 aos 15 minutos, o time azul venceu 81,5% das partidas no cenário
profissional (n = 3.294) contra 73,7% no *solo queue* (n = 5.166). Na faixa
de +4.000 a +6.000, as taxas são de 91,7% no profissional (n = 72) e 86,3%
no *solo queue* (n = 3.343). Esse resultado quantifica a noção de que
"macro ganha jogo": a mesma vantagem material aos 15 minutos vale mais nas
mãos de um time coordenado. A diferença na faixa com amostra suficiente é
de 7,8 pontos percentuais, e é pequena em termos absolutos — bem menor do
que a estimativa de 16 pontos que a primeira versão deste texto apresentava
— mas permanece altamente significativa (z = 8,3, p < 0,001 para a
comparação das duas proporções), de modo que a direção do efeito não
depende da amostra.

*(Todas as taxas acima foram remedidas sobre a base de *features*
congelada — 39.309 partidas distintas, 39.188 no corte de 15 minutos —
pelo script `docs/confere_conversao_advantagem.py`, que lê
`data/features_phases.csv`
+6.000 no cenário profissional apoia-se em apenas 72 jogos e deve ser lida
como indicativa; a conclusão sobre conversão de vantagem se apoia na faixa
de +2.000 a +4.000.)*

### 5.4 Modelagem preditiva e comparação entre modelos (objetivo e)

Após ajuste de hiperparâmetros (*GridSearchCV*, validação cruzada
estratificada de 5 *folds*) sobre o corte de 15 minutos, no conjunto
final de 39.188 partidas:

Quadro — Comparação entre modelos (corte de 15 minutos)

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---:|---:|---:|---:|---:|
| **XGBoost (produção)** | **0,7621** | 0,7561 | 0,7228 | 0,7391 | **0,8473** |
| MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| *Random Forest* | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |

*(taxa de vitória do time azul na amostra: 46,6%; medição do retreino de
2026-10-04, sobre as 39.188 partidas do corte de 15 min, com validação
cruzada estratificada de 5 *folds* e semente 42. Reproduzível por
`python -m src.models.multi_cutoff_metrics`.)*

Os três modelos performaram de forma próxima entre si, com o XGBoost
adotado como modelo de produção pela estabilidade da faixa intermediária
— a 10 minutos o MLP o supera em acurácia (0,7020 contra 0,7004) e aos
25 minutos o MLP iguala seu AUC (0,9072 contra 0,9090), de modo que a
escolha não decorre de vantagem em todos os cortes, e sim de comportamento
consistente na faixa em que a previsão é usada. Modelos independentes
foram treinados para os quatro cortes temporais, com desempenho crescente
conforme a partida avança (medido com os hiperparâmetros de produção, sobre
a base de 39.426 partidas, congelada antes da rodada final): AUC-ROC de
  0,774 (10min), 0,847 (15min), 0,876
(20min) e 0,909 (25min) — resultado
esperado, já que mais informação está disponível em cortes mais
tardios, mas que só se sustenta porque um modelo *por fase* foi
treinado especificamente para cada corte.

A análise de importância de variáveis (SHAP, valor médio absoluto por
*feature*) mostrou a diferença de ouro e de experiência como os fatores
dominantes em todos os cortes (gold_diff variando de 0,66 aos 10 min até
1,07 aos 20 min; xp_diff de 0,27 aos 10 min até 0,81 aos 25 min). A
diferença de torres tem comportamento distinto: quase irrelevante nos três
primeiros cortes — 0,0044 aos 10 min, 0,0060 aos 15 min e 0,0031 aos 20
min — e salta para 0,0928 aos 25 min, um salto de cerca de 15 vezes entre
o corte de 15 e o de 25 minutos. Vale notar que a série das torres não é
monótona: o corte de 20 min registra valor menor que os de 10 e de 15, de
modo que o que se observa é uma concentração tardia, e não um crescimento
contínuo. Esse comportamento é consistente com a mecânica do jogo, em
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
XGBoost subiu de 0,8214 (10.295 partidas) para 0,8393 (23.133 partidas) e
para 0,8473 (39.188 partidas)
ao longo da coleta incremental — evidência de que, com as *features* de
estado agregado atualmente disponíveis via API, o teto de desempenho é
limitado mais pelo volume de dados do que pela engenharia de novas
variáveis a partir da mesma fonte.

### 5.5 Dashboards (objetivo f)

Foram entregues seis páginas de visualização (Início, Dashboard,
Campeões, Partidas, Competitivo e Simulador), incluindo KPIs agregados,
gráficos de distribuição por campeão e objetivo, mapa de calor de
posicionamento por minuto na análise de partida, comparação visual
*solo queue* × profissional com seletor de ano, e um simulador que
combina composição de time (heurística de taxa de vitória histórica,
sinalizada como tal na interface para não ser confundida com predição
por modelo), estado de jogo (predição pelo modelo de produção) e
explicabilidade (SHAP).

A Figura 2 exibe o painel de indicadores agregados, incluindo a leitura de
viés de lado por região que fundamenta a Seção 5.3; a Figura 4 mostra a
análise de uma partida individual, com o mapa de calor de posicionamento e
a evolução das variáveis ao longo da partida; a Figura 3 traz o detalhe de
um campeão, com os itens finalizados extraídos das *timelines*; e a Figura
6 apresenta o simulador com o estado de jogo e a explicação por SHAP, na
mesma tela em que a previsão é exibida. A Figura 5 traz a comparação com o
cenário profissional discutida adiante, e a Figura 1 a tela inicial da
plataforma.

### 5.6 Interface em linguagem natural (objetivo g)

O *pipeline* de linguagem natural para consulta ao banco (*text-to-SQL*
com validação estrutural antes da execução) atingiu **88% de acurácia de
execução** (23 de 26 perguntas de referência, sendo 22 sobre *solo
queue* e 4 sobre o dataset competitivo), medida de forma estável ao
longo de sessões de revisão sucessivas. As três falhas remanescentes
pertencem à mesma família benigna — diferenças de formatação ou coluna
extra na resposta, não erros de interpretação da pergunta ou de geração
de SQL incorreto.

---


### 5.7 Os resultados frente à literatura

Hodge et al. (2021) demonstraram a viabilidade de modelos preditivos
para partidas profissionais de esports em tempo real; este trabalho
corrobora essa viabilidade para *League of Legends* especificamente, com
a particularidade de ter caracterizado como o desempenho preditivo varia
ao longo da partida (AUC-ROC de 0,774 a 10 minutos a 0,909 a 25 minutos)
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

### 5.8 Limitações

- **Amostras pequenas em recortes finos** (combinações específicas de
  jogador e campeão, ou de matchup de rota) seguem estatisticamente
  frágeis mesmo com 41.063 partidas — mitigado, onde aplicável, por
  encolhimento estatístico (*shrinkage*) em direção à média do grupo
  maior, mas não eliminado.
- **A taxa-base do modelo em estado de empate subestima o viês de lado.**
  Com o retreino de 39.188 partidas, a probabilidade prevista para o
  estado "tudo empatado" ficou em 49,2% (10 min), 49,6% (15 min), 51,4%
  (20 min) e 49,0% (25 min), enquanto a medição direta sobre os dados
  brutos, entre partidas genuinamente empatadas, dá 46,4% a 47,9%
  (Seção 5.3): uma diferença de **1,7 a 4,7 pontos percentuais
  conforme o corte**. As duas séries não concordam apenas em magnitude —
  aos 20 minutos o modelo projeta 51,4% de vitória azul, favorecendo o
  azul, enquanto o dado bruto dá 46,7%, favorecendo o vermelho. A
  discrepância não decorre de subajuste: uma busca em grade completa
  (27 combinações, 5 *folds*) escolheu a **mesma profundidade** de
  produção (3) e terminou 0,0001 de AUC acima dela, de 0,8473 para
  0,8475, em 2º lugar entre as 27. Testadas as três alavancas que a grade
  não cobre, a conclusão é contraintuitiva: a **calibração piora** a
  discrepância (de 1,7 para 2,3 pp na sigmoidal), porque o estado de empate
  total fica fora da distribuição observada e o calibrador o extrapola
  para perto de 50%; a regularização alternativa move o desvio dentro do
  ruído; e só a **troca de família** o fecha — uma *Random Forest* com
  500 árvores e profundidade 6 leva o desvio a **0,6 pp** ao custo de
  0,0005 de AUC. A discrepância é, portanto, uma propriedade da função que
  o XGBoost aprende neste recorte, e não um défict de ajuste. A troca
  não foi adotada porque o critério de escolha do modelo foi a
  acurácia no corte de 15 min, e nela a *Random Forest* fica em 0,7617
  contra 0,7621 — decisão consciente e reversível, sem retreino.
  Comando e artefato: `docs/experimento_calibracao.py` e
  `reports/experimento_calibracao_veredito.json`.
- **O modelo não viu a última rodada de coleta.** As *features* e a
  modelagem foram construídas sobre 39.426 partidas, e a base do banco
  tem 41.063 — 1.637 partidas a mais, quase todas da KR (das 1.754
  partidas do banco que não geraram *features*, 1.647 são da KR e 107
  são de BR1, EUW1 e NA1). O conjunto que de fato alimentou o modelo
  são 39.309 partidas distintas, das quais 39.188 chegam ao corte de 15
  minutos; as outras 117 da base congelada não produziram linha em
  `features_phases.csv`. A discussão de
  volume da Seção 5.4 mediu que o ganho de AUC por volume é da ordem de
  0,001 por acréscimo relevante, o que situa o efeito desta diferença
  abaixo do que aquela discussão mediu como ganho real, mas não nulo.
  Retreinar foi deixado de fora porque o desempenho do modelo atual já
  está medido e validado contra o Apêndice C e a bateria comportamental, e
  refazê-lo invalidaria as duas coisas sem ganho apurado. Fica registrado
  como limitação, e não escondido: quem quiser o modelo treinado sobre a
  base completa reexecuta `train_baseline` e `export_model`.
- **Desequilíbrio de amostra por região**: após as rodadas adicionais de
  coleta (Seção 5.3), BR1 e EUW1 concentram a maior parte dos dados
  (11.936 e 11.744 partidas) e KR cresceu para 10.204; NA1, que permanecia
  em 1.446, foi ampliada para 7.159 na rodada final, o que reduz a assimetria
  entre regiões sem eliminá-la. O achado de viés de lado "generalizado ao
  elo alto, não específico do Brasil" é sustentado pela direção
  consistente nas três regiões com evidência estatística firme, e a NA1 deixa de
  ser o elo mais frágil da generalização. A ressalva é que a força da evidência não é uniforme: três
  das quatro regiões têm taxa cujo intervalo de 95% exclui 50% e a KR fica
  em 50,4%, com intervalo que a inclui.
- **Cobertura desigual por versão do jogo** (*patch*): um único *patch*
  concentra a maior parte das partidas coletadas, o que limita a
  generalização dos achados para versões do jogo com balanceamento
  diferente.
- **Teto de desempenho das variáveis atuais**: nove experimentos de
  enriquecimento de *features* a partir da mesma fonte de dados (linha
  do tempo da partida) não superaram o modelo com as cinco variáveis
  originais, sugerindo que o próximo ganho relevante depende de um tipo
  de dado que a API atual não fornece — notadamente a ordem de escolha de
  campeão (*draft*), que a API pública não expõe, e o estado das ondas de
  *minions*. A posição em tempo real **existe** no payload da *timeline*
  (`participantFrames`) e já foi testada sem ganho mensurável (experimento 2
  do Apêndice D, dispersão espacial do time), de modo que ela não é o que
  falta; o que falta são as duas variáveis acima.
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
profissional — achados sustentados por testes de robustez estatística,
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
trabalho, é o viés de lado. A hipótese inicial era que a modelagem
preditiva operaria sobre um sinal qualquer de desempenho; o que a análise
descritiva revelou é uma assimetria estrutural entre os dois lados do
mapa, presente nas quatro regiões coletadas e com sinal inverso no
jogo profissional — com a ressalva de que é estatisticamente firme
em três delas (BR1, EUW1 e NA1) e apenas consistente em direção na KR,
cuja taxa de 50,4% tem intervalo de confiança que inclui 50%. O valor
disso para a comunidade é duplo. Por um
lado, é um fator de confusão que qualquer modelo preditivo sobre *solo
queue* precisa controlar, porque uma variável que distingue time azul
de time vermelho sem nenhuma propriedade حقوقa do jogo é,
necessariamente, um atalho. Por outro lado, a inversão observada no
circuito profissional sugere que o mesmo fenômeno tem outra origem no
*solo queue* — uma hipótese que este trabalho não comprova, mas que
delimita o problema de forma útil.

Como contribuição além do escopo originalmente delimitado no TCC I, a
incorporação do dataset competitivo profissional (Oracle's Elixir)
permitiu uma comparação direta entre dois contextos institucionalmente
diferentes do mesmo jogo, produzindo dois achados quantitativos com
potencial de contribuição à literatura: a inversão do viés de lado entre
*solo queue* de elo alto e jogo profissional, e a diferença na conversão
de vantagem material em vitória entre os dois contextos.

### 6.1 LIMITAÇÕES E AMEAÇAS À VALIDADE

Registrar o que o trabalho não sustenta é parte da conclusão, e não uma
fórmula de cortesia. As três limitações a seguir delimitam o alcance em
que os achados podem ser generalizados; nenhuma delas os invalida.

**Validade de construto.** A *timeline-v5* não registra o estado das ondas
de *minions*, de modo que o modelo de predição trabalha sem uma variável
que um analista humano consideraria informativa sobre o momento da
partida. É razoável supor que parte do que o modelo erra é informação que
ele jamais recebeu — mas essa é uma hipótese, e não um resultado medido:
nenhum experimento deste trabalho isola o efeito de acrescentar essa
variável, porque ela não existe na fonte. A consequência prática é
observável: nenhuma orientação exibida pela plataforma cuja fundamentação
dependa de itemização ou de estado de ondas foi produzida pelo modelo, e a
interface marca essa orientação como inferência geral em vez de resultado
calculado.

**Validade externa.** Todos os resultados de *solo queue* vêm da fila
ranqueada, nas faixas Challenger e Grandmaster, em cinco regiões
coletadas, quatro delas com amostra suficiente para a leitura. Não há base
para estender as taxas de vitória por lado nem a acurácia do modelo a
outras filas, a outros níveis de elo ou a outros jogos, ainda que a
arquitetura seja reaproveitável.

**Validade interna.** As partidas foram coletadas em janelas de tempo
delimitadas, e não amostradas aleatoriamente ao longo de todo o histórico
disponível. Um padrão sazonal — mudanças de *patch*, eventos do cenário
competitivo — pode portanto estar parcialmente confundido com o que os
dados descrevem.

Há ainda uma limitação técnica em aberto, que não foi resolvida e não
deveria ser omitida: o modelo de produção subestima o viés de lado nos
cortes em que o jogo estava empatado, projetando taxas próximas de 50%
onde o dado bruto dá entre 46% e 48%. A investigação descartou subajuste e
apontou a troca de família de modelo como a única correção, ao custo de
0,0005 de AUC. Por ser uma questão de modelo e não de dado, ela está
detalhada na Seção 5.8, onde também estão os números e o experimento.

Uma fragilidade declarada na primeira versão deste texto foi resolvida e
não permanece como limitação: a amostra da região NA1, então reduzida a
1.446 partidas, foi ampliada para 7.159, e a taxa de vitória do time
vermelho passou de 51,9% para 52,2%, sem mudança de direção do achado.

### 6.2 TRABALHOS FUTUROS

Ficam registrados quatro caminhos. O primeiro é a extensão da predição
para o cenário de partidas ao vivo, não implementada nesta versão mas
considerada na arquitetura desde o início — a camada de predição aceita
estado de jogo arbitrário por fase, não apenas dados pré-processados de
um conjunto fixo, de modo que a barreira é de dados em tempo real, não
de modelo. O segundo é a inclusão de seleção de campeão competitiva no
simulador de time. O terceiro é a investigação de restrições de
monotonicidade formal no modelo, caso seja avaliada como necessária. O quarto
é a extensão do recorte de validade externa, que passaria por coletar
outras filas e, eventualmente, outro jogo, de modo a testar se o viés
de lado descreva o jogo ou o modo de jogar de uma população específica.
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

CHEN, Tianqi; GUESTRIN, Carlos. XGBoost: a scalable tree boosting system. In:
Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge
Discovery and Data Mining. New York: ACM, 2016. p. 785-794. DOI:
10.1145/2939672.2939785.

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

HANLEY, James A.; MCNEIL, Bernard J. The meaning and use of the area under a
receiver operating characteristic (ROC) curve. **Radiology**, [S. l.], v. 143,
n. 1, p. 29-36, 1982. DOI: 10.1148/radiology.143.1.7063747.

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

LUNDBERG, Scott M.; LEE, Su-In. A unified approach to interpreting model
predictions. In: Advances in Neural Information Processing Systems 30 (NIPS 2017). 2017. p. 4765-4774. Disponível em: https://arxiv.org/abs/1705.07874.
Acesso em: 4 out. 2026.

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

Execução em 2026-10-04 sobre a base de produção de 39.426 partidas:
**23/26 = 88% de acurácia de execução**, com o comando
`python -m src.nlq.evaluate_nlq`. O mesmo número havia sido obtido em
execuções anteriores — a de 2026-09-28, sobre a base de então (24.154
partidas), e uma de 2026-07-13 —, o que dá alguma estabilidade ao
resultado. Uma
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

Quadro reproduzido por `python -m src.models.multi_cutoff_metrics`, que
avalia os três modelos nos quatro cortes com validação cruzada estratificada
de 5 *folds* (semente 42) usando os **mesmos hiperparâmetros de produção**
(500 árvores, taxa de aprendizado 0,01, profundidade 3) — o mesmo desenho
do quadro anterior, agora regenerável por comando. Executado em 2026-10-04
sobre a base de 39.426 partidas. Os valores do corte de 15 min reproduzem os
já citados na Seção 5.4.

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
produção do XGBoost (500 árvores, *learning rate* 0,01, profundidade 3) — a
versão anterior desta nota afirmava que eram diferentes, e não são:
`src/models/multi_cutoff_metrics.py` e `src/models/export_model.py` leem a
mesma configuração. A diferença entre os valores atuais e a série
histórica de 2026-07-08 (0,767 / 0,842 / 0,872 / 0,907) vem da base de
treino, que era de 23.133 partidas e passou a 39.426, e não do ajuste. O
comando que regenera este quadro é
`python -m src.models.multi_cutoff_metrics`.

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
| 9 | Dragões por tipo (`monsterSubType`) | **AUC piorou** (0,8319 → 0,8295), sobre a base de 23.133 partidas |

*Nota sobre o experimento 4.* A ausência de ganho de AUC da calibração foi
reexaminada em 2026-10-04, quando a limitação de taxa-base da Seção 5.8
passou a ser testada contra as alavancas que este apêndice não cobre. O
resultado é mais forte que "sem ganho": a calibração **piora** também a
discrepância de taxa-base, de 1,7 para 2,3 pontos percentuais, porque o
estado de empate total fica fora da distribuição observada e o calibrador o
extrapola para perto de 50%. A *Random Forest* com 500 árvores e
profundidade 6 fecha a discrepância (0,6 pp) ao custo de 0,0005 de AUC,
mas não foi adotada — a justificativa está na Seção 5.8. Esse teste não
figura na tabela porque não é enriquecimento de *features*, e sim
caracterização de uma limitação de modelo; o comando é
`python docs/experimento_calibracao.py`.

Em contraste, o aumento de *volume* de partidas produziu ganho real:
AUC-ROC do XGBoost (corte 15 min) subiu de 0,8214 (10.295 partidas)
para 0,8393 (23.133 partidas) e para 0,8473 (39.188 partidas) ao longo
da coleta incremental — um ganho acumulado de 0,0259, cerca de 6× maior
que o maior ganho de qualquer um dos 9 experimentos de *feature* (0,003),
e cerca de 26× o menor deles (0,001).

---

## ANEXO A — Capturas de tela da plataforma

Geradas em 2026-10-04 via Playwright (Chromium, 1440 px de largura, altura
ajustada à página, sem `full_page`) contra a API e o *frontend* rodando
localmente com dados de produção — 39.426 partidas no momento da captura,
as mesmas da Seção 5.3. As capturas anteriores, de 2026-09-28, foram feitas
com 24.154 partidas e foram substituídas: o Dashboard anterior exibia a
tabela regional com NA1 = 1.446, em contradição com os 7.159 que o texto
afirma. Arquivos em `reports/anexo_a/` (não versionados neste Markdown —
inserir como figura ao converter para o `.docx` final). O comando que as
regera é `python docs/recapturar_anexo_a.py`.

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
   modelos), D (9 experimentos negativos), Anexo A (6 capturas de tela
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
   que confere também legendas (6 Figuras, 5 Quadros), fontes de ilustração
   (11), tabelas (5) e imagens (6). Ele falha com exit 1 se qualquer uma
   divergir — os números do checklist não são mais escritos à mão, que era
   como "41 títulos" e "12 referências" ficaram velhos sem ninguém perceber.

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
     acordo com o orientador**. Em 2026-10-04, a medição dos **10 TCC II
     aprovados** mostrou que 10 de 10 usam "Trabalhos Relacionados" como
     seção de primeiro nível e "Metodologia" (não "Material(is) e
     Métodos"), o que reverte a pendência nº 3 (item 3 acima).
     Limite de páginas do TCC II: **25 a 30 páginas**, não contando
     apêndices/anexos.
6. ~~Ampliar a coleta EUW1/KR/NA1~~ — **feito**: EUW1 1.307→11.744
   partidas, KR 1.308→10.204 e **NA1 1.446→7.159** (a NA1 foi ampliada na
   rodada final de 2026-10-04; a limitação que ela representava saiu da
   Seção 5.8). Quadro de viés de lado por região remedido com dados de
   2026-10-04 (Seção 5.3) e verificado por SQL direto contra o valor
   mostrado no *dashboard*: BR1 56,3%, EUW1 53,4%, KR 50,4%, NA1 52,2% de
   vitória do time vermelho, sobre 41.063 partidas.

**Status (2026-10-04):** de 6 pendências, **6 estão fechadas**. **Nenhuma
depende do orientador.** As duas decisões de escopo (título acadêmico e
Trabalhos Relacionados como seção de primeiro nível) estão nos itens 2 e 3
acima e não se repetem aqui.

Antes de entregar, a suíte completa passa:
`tests/smoke_test.py` (exit 0), `tests/validate_predictions.py`
(APROVADO COM RESSALVAS), `docs/verifica_tcc.py` (18 checagens de
consistência do texto contra o banco e os artefatos, exit 0),
`docs/confere_docx.py` (conformidade formal do `.docx`, exit 0), e
`cd frontend; npm run lint; npm run test` (31/31).

**Resta 1 item, já resolvido:** o título do Quadro 4 (Apêndice C), que no
rascunho só tinha nota de método — o que viola a regra da instituição, já
que tabela sem legenda não é permitida. O título foi escrito na conversão e
**confirmado pelo autor em 2026-10-03**: "Métricas completas por corte temporal
— comparação entre os três modelos".

**Nenhuma pendência em aberto.**

**Estrutura final do corpo (2026-10-04), seguindo os 10 TCC II aprovados:**
1 Introdução · 2 Fundamentação Teórica · 3 Trabalhos Relacionados ·
4 Metodologia · 5 Resultados e Análise · 6 Conclusão. Note que difere do
modelo institucional de 2026-09-28 (Referencial Teórico em vez de
Fundamentação, sem Trabalhos Relacionados, Material(is) e Métodos em vez de
Metodologia, Resultados e Discussão separados): prevalece o padrão que a banca
aprovou.
