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
>   aparece no corpo do texto, na introdução.
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

A exploração dos dados de esports ainda depende de ferramentas
fragmentadas e de conhecimento técnico. Este trabalho desenvolveu uma
plataforma inteligente para análise de dados de *League of Legends* que
integra coleta, modelagem preditiva com *machine learning*,
explicabilidade, visualização e consulta em linguagem natural. A
pesquisa é aplicada e quantitativa, sobre 41.063 partidas ranqueadas de
elo alto, obtidas pela interface de programação de aplicações (API) da
Riot Games, e 99.259 jogos profissionais (Oracle's Elixir). XGBoost,
*Random Forest* e um perceptron multicamadas (MLP) foram comparados por validação cruzada para predizer o vencedor em cortes de
10 a 25 minutos. Após o ajuste, aos 15 minutos, a área sob a curva ROC
(AUC-ROC) ficou entre 0,8480 e 0,8491, e uma regressão logística chegou
a 0,8495; o XGBoost (0,8487) foi mantido pela proximidade dos resultados
e pela integração com o SHAP. A análise exploratória identificou viés
favorável ao lado vermelho no *solo queue* (56,3% na região com maior
amostra); entre partidas com diferença de ouro inferior a 500, as taxas
foram próximas nos quatro cortes, sem diferença detectada. No cenário
profissional, o viés se inverte (53,2% para o azul), achado sustentado
por testes de robustez. Uma interface *text-to-SQL* com validação
acertou 181 de 203 perguntas (89,2%) de um gabarito gerado por modelos
de pergunta: 166 de 187 respondíveis e 15 de 16 recusas esperadas. A plataforma tem seis páginas de visualização, com predição explicável. Conclui-se que
integrar essas etapas é viável.

**Palavras-chave:** esports; *League of Legends*; análise de dados;
*machine learning*; interface em linguagem natural.

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
usuário final. Jiang et al. (2025), por sua vez, mostram que modelos de linguagem
podem apoiar a exploração de dados estruturados em soluções de *Business
Intelligence*, reduzindo a barreira técnica entre o usuário e a base de
dados.

O tema deste trabalho é a análise de dados aplicada a esports, na área da
Ciência da Computação, envolvendo ciência de dados, inteligência
artificial, aprendizado de máquina e sistemas de informação. O recorte é
*League of Legends*, com duas fontes de dados de papéis distintos. As
partidas ranqueadas solo/duo de jogadores de elo alto (Desafiante a
Mestre), coletadas pela interface de programação de aplicações (API,
*Application Programming Interface*) da Riot Games, sustentam a modelagem
preditiva. Os jogos profissionais do Oracle's Elixir permitem comparar os
padrões entre os dois contextos. A modelagem compara XGBoost, *Random
Forest* e redes neurais em predições restritas ao estado do jogo até o
momento da predição, sem informação posterior ao corte temporal. Outros
jogos e outras abordagens de inteligência artificial ficam fora do
escopo. A questão de pesquisa é: como desenvolver uma plataforma
inteligente para análise de dados de *League of Legends* que integre
coleta, organização, modelagem preditiva, visualização e consulta em
linguagem natural para apoiar a interpretação de informações competitivas?

O trabalho se justifica academicamente por articular áreas centrais da
Ciência da Computação, como análise de dados, inteligência artificial,
aprendizado de máquina, sistemas de informação e interação humano-computador,
sobre um campo de produção de dados em crescimento. Do ponto de vista
prático, reunir coleta, tratamento, modelagem e consulta em linguagem
natural em uma mesma plataforma reduz a dependência de processos
fragmentados e de ferramentas que exigem conhecimento técnico elevado, e
oferece uma contribuição aplicável à interpretação de desempenho, ao
acompanhamento de tendências competitivas e à análise de partidas.

Neste contexto, o presente trabalho tem como objetivo geral desenvolver
uma plataforma inteligente para análise de dados de esports, com foco em
*League of Legends*, integrando coleta, organização e exploração de dados
competitivos, modelagem preditiva com técnicas de aprendizado de máquina e
mecanismos de visualização e consulta em linguagem natural para apoiar a
interpretação das informações. A plataforma, batizada **Bellestraiko**,
foi desenvolvida e implementada ao longo do trabalho. Os objetivos específicos, retomados um a um nas Seções 5 e 6, são: a) mapear os dados e os
recursos disponibilizados pela Riot Games API relevantes para a análise
competitiva em *League of Legends*; b) identificar quais informações
relacionadas a partidas, jogadores e estatísticas podem ser organizadas em
uma base estruturada para apoio à análise de dados; c) estruturar um
processo de coleta, tratamento e organização dos dados obtidos, de modo a
viabilizar sua exploração analítica; d) avaliar o uso de técnicas de
análise de dados para identificação de padrões e apoio à interpretação de
informações competitivas; e) comparar o desempenho de modelos de aprendizado de máquina, com foco em XGBoost, *Random Forest* e redes neurais, no
contexto dos dados analisados; f) propor *dashboards* para visualização
das informações e dos resultados analíticos produzidos pela plataforma; e
g) propor uma interface em linguagem natural para facilitar a consulta aos
dados e a geração de descobertas no contexto competitivo estudado.

Este trabalho está organizado em cinco seções, além desta introdução. A
Seção 2 apresenta a fundamentação teórica; a Seção 3, os trabalhos
relacionados; a Seção 4, a metodologia; a Seção 5, os resultados e sua
análise à luz da literatura; e a Seção 6, as conclusões, as limitações e
os trabalhos futuros.

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
campo relevante para a análise de dados. Em *Dota 2*, Hodge et al. (2021)
mostram que é possível prever o resultado de partidas profissionais enquanto
elas acontecem, com modelos de aprendizado de máquina padrão e engenharia de
atributos. Em *League of Legends*, Birant e Birant (2023) destacam a
modelagem centrada no time, e Bahrololloomi et al. (2022), a relação entre
métricas de jogadores, funções em jogo (*roles*) e resultado da partida.

### 2.2 FAMÍLIAS DE MODELOS PREDITIVOS E SUA APLICAÇÃO EM ESPORTS

Esses estudos delimitam o espaço de escolha da modelagem, mas não decidem
qual família de modelos é adequada a este problema. O trabalho comparou
três por medição. A primeira são os *ensembles* de árvores de decisão, em particular a
*Random Forest* (Breiman, 2001), que combina *bagging*, em que cada árvore
treina sobre uma amostra *bootstrap*, com a seleção aleatória de
variáveis em cada nó. Isso reduz a correlação entre as árvores, que limitaria o ganho do *ensemble*; a redução importa aqui porque as variáveis preditoras (ouro, experiência, abates, torres e dragões) evoluem juntas na partida.

A segunda são os modelos de *gradient boosting*, representados pelo XGBoost (Chen; Guestrin, 2016), que constroem as árvores em sequência, cada uma ajustada
ao resíduo das anteriores, com otimização de segunda ordem e
regularização explícita. Em dados tabulares, como os deste trabalho, os
métodos baseados em árvores seguem competitivos frente a redes neurais em
amostras de porte médio, de cerca de 10 mil exemplos, com indício de que a
diferença diminui em amostras maiores (Grinsztajn; Oyallon; Varoquaux,
2022).

A terceira são as redes neurais *feedforward*, ou perceptrons multicamadas
(MLP). Elas capturam interações sem que precisem ser
especificadas, mas exigem mais dados e mais cuidado com escala e
regularização, restrição relevante em uma amostra de dezenas de milhares de
partidas, longe de milhões.

### 2.3 EXPLICABILIDADE E AVALIAÇÃO DE MODELOS PREDITIVOS

García-Méndez e Arriba-Pérez (2025) mostram que a predição em esports pode
combinar classificação e interpretação, tornando os fatores da previsão
compreensíveis para o usuário final. Explicar um *ensemble*, porém, não é
trivial: a saída é a soma de centenas de árvores, e a contribuição de cada
variável não é diretamente legível. O LIME (Ribeiro; Singh; Guestrin, 2016), de *Local Interpretable Model-agnostic Explanations*, aproxima o classificador por uma regressão linear local na vizinhança de cada
predição, simples de ler, mas pouco fiel se o modelo for muito não linear na vizinhança. O SHAP (*SHapley Additive exPlanations*)
recorre ao valor de Shapley da teoria dos jogos: a importância de uma
variável é sua contribuição média para a previsão, sobre todas as
combinações das demais. Lundberg e Lee (2017) mostram que essa é a única
atribuição aditiva com propriedades desejáveis, como a consistência e a
importância nula para uma variável ausente, e o SHAP foi o método
adotado. No XGBoost, o explicador de árvores decompõe a saída bruta do
modelo, em log-odds: as contribuições somam-se ao valor de referência (a
saída média do modelo), e a probabilidade é a transformação logística
dessa soma. São aditivas na escala logit, não em pontos percentuais. Como
as contribuições somam a previsão, a explicação exibida na plataforma vem de valores
calculados, sem recorrer a conhecimento genérico sobre o jogo.

A avaliação exige também uma escolha de métrica. A acurácia depende de um
limiar e precisa ser lida contra a taxa-base: na amostra, o azul vence
46,7% das partidas, de modo que um classificador que sempre respondesse
"vitória do vermelho" acertaria 53,3% sem poder preditivo algum. Por isso
a avaliação se apoia também na área sob a curva ROC (*Receiver Operating Characteristic*), a AUC-ROC, que mede a
discriminação do modelo em todos os limiares. Hanley e McNeil (1982)
mostram que ela equivale à probabilidade de um caso positivo receber
pontuação maior que um negativo. As duas métricas são reportadas juntas
na Seção 5.

### 2.4 INTERFACES EM LINGUAGEM NATURAL PARA EXPLORAÇÃO ANALÍTICA

Interfaces em linguagem natural reduzem a barreira técnica entre o
usuário e os dados. Jiang et al. (2025) observam que soluções de
*Business Intelligence* apoiadas por modelos de linguagem, com diálogo em
várias rodadas, favorecem a exploração de dados estruturados, e Guo et al.
(2024) acrescentam que a decomposição de perguntas e a análise visual tornam essa
exploração mais intuitiva. O problema técnico central é a geração da consulta: o modelo
produz texto, e o banco exige SQL (*Structured Query Language*) válido e correto sobre um esquema
específico. Uma consulta gramaticalmente correta pode citar uma tabela
inexistente ou responder à pergunta errada. Wang et al. (2020) tratam
este segundo caso e mostram que representar o esquema com os
relacionamentos entre tabelas, além dos nomes das colunas, melhora
a precisão da conversão. Neste trabalho, a segurança da consulta não é delegada ao modelo: ela é validada antes de tocar o banco, e a correção semântica é medida no gabarito automático (Seção 5.6).

### 2.5 VISUALIZAÇÃO ANALÍTICA E DADOS ESPAÇO-TEMPORAIS EM ESPORTS

A análise de esports também precisa representar informações que evoluem
no espaço e no tempo, como movimentação e posicionamento dos jogadores.
Wallner, Wang e Dormann (2023) mostram que visualizações que integram
tempo e localização em uma única representação ajudam a interpretar o
comportamento em jogo; esse referencial motivou o mapa de calor de
posicionamento da análise de partida.

---

## 3 TRABALHOS RELACIONADOS

Esta seção descreve os onze estudos de domínio que sustentam a pesquisa,
com o objeto, a abordagem e a contribuição de cada um para o problema
aqui tratado. A seleção não seguiu uma revisão sistemática com *strings* de
busca fixas; os critérios foram recência (até cinco anos), cobertura de cada
frente da plataforma (predição, explicabilidade, interface em linguagem
natural e visualização, uma por subseção) e, na predição, preferência por
estudos do próprio *League of Legends*. Os artigos foram conferidos no
texto completo, e não só no resumo. As principais
obras de método (Breiman, 2001; Chen; Guestrin, 2016; Hanley; McNeil, 1982; Lundberg; Lee, 2017; Ribeiro; Singh; Guestrin, 2016; Wang et al., 2020) estão na Seção 2, no ponto em que o método que
elas fundamentam é introduzido.

### 3.1 PREDIÇÃO DE VITÓRIA EM DOTA 2

Hodge et al. (2021) tratam da predição de vitória em partidas
profissionais de *Dota 2*, em tempo real. Com modelos de aprendizado de máquina
padrão, engenharia de atributos e otimização, chegam a 85% de
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
Bahrololloomi et al. (2022) percorrem o caminho oposto: predizem a vitória a partir das métricas individuais dos jogadores e concluem que o peso de cada função é desprezível. Neste trabalho, as métricas individuais aparecem só nos perfis de jogador da plataforma, não no modelo.

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

García-Méndez e Arriba-Pérez (2025) combinam classificação por aprendizado
de máquina com mecanismos de interpretação na predição de vitória em
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
*gameplay* em *League of Legends* com a técnica de *storyline
visualization* e mostram que integrar tempo e localização numa só vista é viável para a interpretação pós-jogo. O estudo é a
referência do posicionamento minuto a minuto da análise de partida.

### 3.6 SÍNTESE E POSIÇÃO DESTE TRABALHO

Os estudos revisados cobrem frentes isoladas: predição de resultados, interpretabilidade da predição (García-Méndez; Arriba-Pérez, 2025),
interação em linguagem natural (Jiang et al., 2025; Guo et al., 2024) e visualização
espaço-temporal (Wallner; Wang; Dormann, 2023). No entanto, nenhum deles é entregue como uma
plataforma que reúna coleta, tratamento, modelagem, explicabilidade,
visualização e consulta em linguagem natural sobre a mesma base, e é
essa lacuna de integração que este trabalho ocupa. A distinção está
em uma decisão de projeto.

**Recorte de população.** A maior parte dos estudos de predição atua
sobre o cenário profissional, e os que usam partidas ranqueadas (Do et
al., 2021; Maymin, 2021) não as comparam com ele. Este trabalho mede o
mesmo indicador nos dois contextos e mostra que o viés de lado do *solo
queue* de elo alto se inverte no circuito profissional.

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

A coleta usou duas fontes, com papéis distintos: as partidas ranqueadas
sustentam a modelagem preditiva, e a base profissional permite comparar
padrões entre os dois contextos.

**a) Riot Games API (*solo queue*).** Os *endpoints* seguem a
documentação oficial (Riot Games, [s.d.]). O *league-v4* identificou
os jogadores de elo alto (Desafiante a Mestre), recorte de escopo: uma
população fechada, que a API lista por inteiro e que cabe no limite de
requisições da chave de desenvolvedor. O *account-v1* resolveu o Riot ID,
e o *match-v5* trouxe cada partida e sua linha do tempo minuto a
minuto. A coleta cobriu cinco regiões (BR1, EUW1, KR, NA1 e
EUN1, com só 20 partidas e por isso fora da análise por região) na fila 420
(ranqueada solo/duo), em um total de **41.063 partidas**. Como a chave de desenvolvedor
expira a cada 24 horas, o coletor retoma de onde parou e pula as partidas
já salvas.

**b) Oracle's Elixir (cenário profissional).** Foram incorporados
**99.259 jogos profissionais** de 2014 a 2026, de 122 ligas, da elite às de
desenvolvimento, a partir dos arquivos anuais em valores separados por vírgula (CSV) que o site publica
(Oracle's Elixir, [s.d.]; arquivos de 4 jul. 2026), para comparar o *solo queue* de
elo alto com o cenário profissional.

Os dados são secundários e públicos, sem participação de sujeitos humanos
como fonte em nenhuma etapa.

### 4.4 ORGANIZAÇÃO E TRATAMENTO DE DADOS

Os dados foram organizados em um banco relacional PostgreSQL, descrito no Apêndice A. O tratamento incluiu a normalização da partida
bruta de cada fonte, a extração das compras e vendas de itens a partir da
linha do tempo, com os desfazimentos de compra aplicados, e, na consulta, a reconciliação dos nomes de campeão entre a Riot API e o Oracle's Elixir,
que usam convenções diferentes. O catálogo de itens, derivado do Data
Dragon da Riot, permite resolver nome e ícone de item por consulta ao
banco, sem depender da memória de um modelo de linguagem.

### 4.5 ANÁLISE EXPLORATÓRIA DE DADOS

A análise exploratória investigou a taxa de vitória por lado do mapa em três recortes: região, fase da partida e contexto (*solo queue* ou profissional). Nenhum padrão foi aceito como resultado sem passar por quatro testes de robustez: (i) replicação restrita a uma região, contra o efeito de mistura regional; (ii) comparação por duração total da partida, contra a confusão com "jogos longos"; (iii) intervalo de confiança de Wilson sobre a proporção (Brown; Cai; DasGupta, 2001), para a significância em amostras menores; e (iv) comparação de pares com correção de Holm (Holm, 1979), que corrige a multiplicidade quando várias diferenças são testadas na mesma base, com a partida como unidade quando ela aparece em mais de um grupo. O teste (iv) foi decisivo para o viés de lado: sem ele, a dispersão entre cortes seria lida como tendência.

### 4.6 MODELAGEM PREDITIVA E COMPARAÇÃO ENTRE MODELOS

Foram comparados três classificadores binários da vitória do time azul:
XGBoost, *Random Forest* e um perceptron multicamadas (MLP). As variáveis
preditoras são as diferenças, azul menos vermelho, de ouro, experiência,
abates, torres e dragões acumuladas até o corte temporal. Há um modelo
independente para cada corte (10, 15, 20 e 25 minutos), e nenhuma informação
posterior ao corte entra como variável, o que evita o vazamento de dados
descrito por Kaufman et al. (2012). Em cada corte entram só as partidas ainda
em andamento naquele minuto: a linha do tempo termina com um quadro no
instante em que o jogo acaba, e esse quadro nunca é usado como estado do
corte. A validação foi cruzada e estratificada (Kohavi, 1995), com 5 dobras, e
mediu acurácia, precisão, *recall*, F1 e AUC-ROC.

Depois de um modelo de referência, os hiperparâmetros foram ajustados por
*GridSearchCV*, do scikit-learn (Pedregosa et al., 2011), otimizando a
AUC-ROC. No XGBoost, a busca foi feita na primeira base ampla, de 10.295
partidas, todas contidas nas 40.778 da avaliação final e presentes nas suas
dobras; repetida na base final, a busca escolheu a mesma configuração, e a
AUC-ROC da grade difere em 0,0001 da medida final. Na *Random Forest* e no
MLP, a busca rodou nas 40.778 partidas e foi avaliada nas mesmas dobras. Para
medir o otimismo dessa seleção, as três buscas foram repetidas de forma
aninhada, com a escolha feita só no treino de cada dobra (Apêndice C).

O modelo de produção recebeu curva de calibração, sobre as probabilidades fora
da dobra, e explicações SHAP, globais e por predição. Uma regressão logística
serviu de *baseline* simples, e a estabilidade no tempo foi verificada
treinando nas partidas mais antigas e testando nas mais recentes
(Apêndice C).

### 4.7 PROPOSTA DE VISUALIZAÇÃO E INTERFACE EM LINGUAGEM NATURAL

A camada de apresentação é uma aplicação web em React com TypeScript, que consome uma API própria em FastAPI, com seis páginas de visualização, descritas na Seção 5.5.

A interface em linguagem natural é um fluxo *text-to-SQL*: um modelo
de linguagem (Claude) traduz a pergunta em SQL, a consulta é validada
antes de executar e o resultado vem sempre do banco, nunca do conhecimento genérico do modelo; a explicação pode acrescentar, rotulada como "Leitura de jogo", uma nota de conhecimento geral. Antes da SQL, a pergunta é roteada para o *solo queue*, o competitivo ou ambos, e perguntas sobre o que o banco não registra recebem uma recusa antes de chegar ao modelo. O desempenho foi medido em um gabarito automático de 203 perguntas, comparado por código (Seção 5.6 e Apêndice B), pela acurácia de execução, que compara o resultado da consulta
gerada com o da consulta de referência. Zhong, Yu e Klein (2020) discutem
seus limites e propõem avaliar a mesma consulta sobre vários bancos de
teste, o que esta avaliação, feita sobre uma única base, não faz.

O módulo de orientação estratégica (*coach*) traduz a probabilidade e as
contribuições SHAP de um estado de jogo, informadas em log-odds com o valor
de referência, em recomendações em linguagem natural, geradas por um modelo de linguagem (Claude). Cada resposta separa
o que vem dos dados (confrontos de rota, sinergias entre campeões e itens
calculados sobre o histórico de partidas) do que é conhecimento geral do
modelo sobre o jogo, marcado como tal. O modelo preditivo não vê itens, posição nem o estado das ondas de *minions*. Qualquer orientação que dependa disso é inferência (Seção
6.1). A auditoria desse módulo, feita em 36 respostas e restrita aos números, está no Apêndice B e resumida na Seção 5.7.

### 4.8 MATERIAIS E MÉTODOS UTILIZADOS

Foram utilizados Python (coleta, extração, transformação e carga, ou ETL, e modelagem, com pandas, NumPy,
scikit-learn, XGBoost e SHAP), PostgreSQL, FastAPI e React com
TypeScript e Recharts. A interface em linguagem natural e o módulo de
orientação estratégica (*coach*) usam a API da Anthropic (modelo Claude).
Testes automatizados cobrem o *backend* (testes de fumaça e uma bateria de
validação comportamental do modelo de produção) e o *frontend* (Vitest).
O desenvolvimento e a execução foram feitos localmente, em um computador com Windows 11, processador Intel Core i5-13400F e 32 GB de memória.

---

## 5 RESULTADOS E ANÁLISE

Esta seção apresenta os resultados obtidos, organizados de acordo com
os objetivos específicos definidos na introdução.

### 5.1 Mapeamento de dados e recursos da Riot Games API (objetivo a)

Foram mapeados e utilizados os *endpoints* *league-v4*, *account-v1* e *match-v5* (partida e linha do tempo) da Riot Games API (Riot Games, [s.d.]), com seus limites de taxa e o ciclo de expiração da chave de desenvolvedor (24 horas). Esse mapeamento orientou o desenho de um coletor resumível, que retoma a coleta entre sessões sem duplicar dados já salvos.

### 5.2 Estruturação da base de dados (objetivos b e c)

A base de modelagem reúne **40.778 partidas** de *solo queue* no corte de 15 minutos, das **41.063** que o banco tem; as demais acabaram antes desse minuto ou não têm linha do tempo, e o número varia por corte (Quadro 3). O banco guarda o JSON (*JavaScript Object Notation*) bruto de partida e de linha do tempo, para reprocessamento, e os **99.259 jogos profissionais** (2014-2026, Oracle's Elixir). O banco tem onze tabelas (jogadores, JSON bruto de partida e de linha do tempo, partidas, times, participantes, bans, eventos de item, catálogo de itens e jogos e jogadores profissionais); os campos e as chaves de cada uma estão no Apêndice A.

### 5.3 Análise exploratória: padrões identificados (objetivo d)

**Viés de lado no *solo queue* de elo alto.** No agregado, o time vermelho venceu mais que o azul, com intensidade variável
por região. O Quadro 1 traz a medição direta em SQL, de 4 de outubro de 2026, sobre
as 41.063 partidas.

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

**Taxas próximas nos quatro cortes.** Entre as partidas com diferença absoluta de ouro inferior a 500 em cada corte, o azul venceu 46,5% aos 10 minutos (n = 7.639), 47,8% aos 15 (n = 4.126), 46,9% aos 20 (n = 2.500) e 47,4% aos 25 (n = 1.474). Os grupos não são independentes, porque a mesma partida pode estar na faixa em mais de um corte (2.766 das 12.615 estão em dois ou mais); por isso a comparação usou a partida como unidade, com *bootstrap* de 2.000 reamostragens. Nenhuma das seis diferenças entre pares foi detectada após a correção de Holm (menor valor-p corrigido de 0,65; a maior diferença, de 1,4 ponto entre 10 e 15 minutos, tem intervalo de −3,1 a +0,2), e o intervalo de Wilson do corte de 10 minutos, o de maior amostra, [45,3%, 47,6%], exclui 50%. O resultado se limita a isso: taxas próximas e nenhuma diferença detectada entre os cortes, o que não demonstra que o viés seja igual em toda a partida. Em conjuntos de dados de esports, um ponto percentual em subamostras de mil partidas fica dentro do erro de amostragem (cerca de ±3 pontos com 95% de confiança).

Os quatro testes de robustez da Seção 4.5 se aplicam aqui. Restrita à BR1, a assimetria se reproduz, o que mostra que o padrão não decorre apenas da mistura de regiões. A taxa de vitória do **azul** fica próxima entre as faixas de duração total da partida (medido em 4 de outubro de 2026 sobre as 41.063 partidas: 45,6% a 47,3% entre as faixas de duração, amplitude de 1,7 ponto percentual, todas abaixo de 50%), sem diferença expressiva desse indicador entre partidas curtas e longas. O intervalo de Wilson e a comparação de pares com correção de Holm estão aplicados acima.

**Comparação com o cenário profissional.** Nos dados competitivos
(Oracle's Elixir, 99.259 jogos), o time azul venceu 53,2% das partidas,
com série anual estável desde 2015 (entre 52,5% e 55,0%). O viés vai na direção oposta à do *solo queue* de
elo alto: a mesma métrica, em dois contextos institucionalmente
diferentes, produz sinais opostos. Uma hipótese, não testada aqui, é que
no *solo queue*, sem coordenação de *draft*, pese mais o *counter-pick*
garantido do time vermelho (que escolhe por último), e no jogo
profissional, a prioridade de primeira escolha do azul. Os dados deste
trabalho não registram a ordem de escolha e não permitem atribuir a
diferença a ela. O resultado é coerente com Jadowski e
Cunningham (2022), que observam 54,08% de vitórias do azul em 882 jogos
profissionais de 2020, e a prioridade de escolha entra como covariável
própria em Guan e Tung (2026), mas isso não comprova a hipótese.

**Conversão de vantagem.** Com vantagem de ouro entre +2.000 e +4.000 aos
15 minutos, o azul venceu 83,6% das partidas no profissional (n = 14.617)
contra 74,1% no *solo queue* (n = 5.366); entre +4.000 e +6.000, 94,0%
(n = 5.842) contra 86,3% (n = 3.497). A diferença observada entre os dois
recortes é de 9,5 pontos percentuais na primeira faixa e de 7,7 na segunda,
e é significativa nas duas (teste z de duas proporções, com grupos
independentes; z = 15,2 e z = 12,7, p < 0,001). Atribuí-la à coordenação
das equipes exigiria evidência que este trabalho não tem: os recortes
diferem também no nível dos jogadores, na versão do jogo e na época. A Figura 1 mostra as duas comparações na tela Competitivo,
com o cenário profissional restrito a 2026. Por isso o azul aparece com
53,1%, diferente dos 53,2% do acervo completo.

Figura — Tela Competitivo: viés de lado e conversão de vantagem de ouro, *solo queue* × profissional de 2026 | reports/figuras_texto/fig_competitivo.png

### 5.4 Modelagem preditiva e comparação entre modelos (objetivo e)

O Quadro 2 compara os modelos no corte de 15 minutos (validação
cruzada estratificada de 5 dobras, semente 42), no conjunto final de
40.778 partidas, em que o azul vence 46,7%. As quatro primeiras linhas são
a comparação após o ajuste de hiperparâmetros, com a regressão logística
como *baseline* simples; as duas últimas, a *Random Forest* e o MLP na
configuração de referência, sem busca em grade.

Quadro — Comparação entre modelos após o ajuste (corte de 15 minutos)

| Modelo | Acurácia | Precisão | *Recall* | F1 | AUC-ROC | AUC-ROC com seleção aninhada |
|---|---:|---:|---:|---:|---:|---:|
| Regressão logística (sem hiperparâmetro ajustado) | 0,7648 | 0,7568 | 0,7317 | 0,7440 | 0,8495 | — |
| MLP ajustado | 0,7638 | 0,7562 | 0,7296 | 0,7427 | 0,8491 | 0,8491 |
| XGBoost ajustado (produção) | 0,7641 | 0,7576 | 0,7278 | 0,7424 | 0,8487 | 0,8485 |
| *Random Forest* ajustada | 0,7628 | 0,7513 | 0,7356 | 0,7434 | 0,8480 | 0,8480 |
| MLP (referência) | 0,7619 | 0,7488 | 0,7378 | 0,7433 | 0,8459 | — |
| *Random Forest* (referência) | 0,7439 | 0,7312 | 0,7144 | 0,7227 | 0,8278 | — |

Após o ajuste, os quatro modelos ficam a 0,0015 de AUC-ROC e 0,0020 de
acurácia uns dos outros, e escolher os hiperparâmetros só no treino de cada
dobra (seleção aninhada) muda a AUC-ROC em no máximo 0,0002. A regressão
logística fica à frente do XGBoost por 0,0008 de AUC-ROC aos 15 minutos; isso sugere que, com as cinco variáveis e o protocolo usados, maior
complexidade do classificador não trouxe ganho relevante. O XGBoost foi
mantido pela proximidade dos resultados e porque a integração com o SHAP
de árvores, exato, já estava implementada na interface; a escolha não se
apoia em superioridade de desempenho, e, nos testes feitos, trocá-lo não mudaria o
resultado.

Há um modelo para cada corte, com os mesmos hiperparâmetros, avaliado nas
partidas elegíveis, isto é, ainda em andamento no corte; o conjunto muda de
40.919 partidas aos 10 minutos para 25.098 aos 25 (Quadro 3). Entre as
partidas elegíveis, a AUC-ROC vai de 0,7752 aos 10 minutos a 0,8899 aos 25.
Restringindo a avaliação às mesmas 25.098 partidas, as que chegam aos 25 minutos, o
crescimento se mantém e é ainda maior: 0,6444, 0,7126, 0,7870 e 0,8899 (Apêndice C). Isso sugere
que as partidas curtas, que só entram nos primeiros cortes, são mais fáceis
de prever cedo. As métricas dos três modelos nos quatro cortes estão no
Apêndice C.

Quadro — Desempenho do XGBoost por corte temporal

| Corte | Partidas | Acurácia | AUC-ROC |
|---|---:|---:|---:|
| 10 min | 40.919 | 0,7020 | 0,7752 |
| 15 min | 40.778 | 0,7641 | 0,8487 |
| 20 min | 34.505 | 0,7856 | 0,8690 |
| 25 min | 25.098 | 0,8068 | 0,8899 |

Na importância das variáveis (SHAP, média do valor absoluto), as
diferenças de ouro e de experiência dominam em todos os cortes. A
diferença de torres é quase irrelevante até os 20 minutos (0,0038 aos 10,
0,0076 aos 15 e 0,0023 aos 20) e sobe para 0,0429 aos 25, cerca de 6 vezes o valor dos 15 minutos (Figura 2). É coerente com a mecânica do
jogo: as placas de defesa das torres caem por volta dos 14 minutos, e
antes disso destruir uma torre é raro e pouco informativo. É uma
justificativa para treinar um modelo *por fase* em vez de um
único modelo genérico. A calibração, preocupação conhecida em modelos de
*boosting* (Niculescu-Mizil; Caruana, 2005), foi avaliada nas probabilidades
fora da dobra de cada corte: entre os decis da probabilidade prevista, o
maior desvio para a taxa observada é de 1,19 ponto percentual aos 15
minutos, e nas partidas empatadas a média prevista fica a menos de 0,5
ponto da taxa observada (Apêndice C e Figura 5). O modelo não exigiu
correção.

Figura — Importância média de cada variável (|SHAP|, em log-odds) nos quatro cortes temporais | reports/figuras_texto/fig_shap_fases.png

**Experimentos de enriquecimento.** Além das cinco variáveis originais, foram feitos 19 experimentos de enriquecimento de variáveis e de ajuste, entre eles dispersão espacial dos jogadores, valor em ouro dos itens, atributos de combate, visão, dragões por tipo, placas de torre, trajetória de ouro e experiência, variáveis por função, campeões e histórico do jogador. Os dez primeiros, refeitos na base final, ficaram, no máximo, +0,0006 acima das cinco variáveis originais em AUC-ROC; os conjuntos mais ricos acrescentaram, aos 15 minutos, até +0,0044 no XGBoost e +0,0073 na regressão logística, cada um contra o mesmo classificador com as cinco variáveis originais, pouco frente à AUC-ROC de 0,8487. O experimento 11, um piloto com atributo consultado depois das partidas, não é comparável aos demais e não entra em nenhuma conclusão. Os resultados completos e os scripts estão nos diretórios `reports/` e `src/models/` do repositório do projeto.

### 5.5 Dashboards (objetivo f)

Foram entregues seis páginas de visualização: Início, Dashboard,
Campeões, Partidas (análise de uma partida, aberta a partir das outras páginas), Competitivo e Simulador; a consulta em linguagem natural tem página própria (Seção 5.6). O simulador separa a
estimativa por composição de time, uma heurística de taxa de vitória
histórica sinalizada como tal na interface, da predição feita pelo modelo
de produção a partir do estado de jogo.

A Figura 3 mostra a análise de uma partida individual: o mapa de calor de
posicionamento no minuto escolhido, a diferença de ouro ao longo da
partida e os objetivos de cada time até aquele minuto. A Figura 4 mostra
o simulador no estado de jogo: o usuário define as diferenças aos 15
minutos, o modelo de produção devolve a probabilidade de vitória do time
azul e o SHAP decompõe a previsão por variável, em log-odds, na mesma
tela. No estado da Figura 4, o valor de referência de −0,132 (46,7%)
somado às contribuições, que totalizam +1,038, dá 0,906 em log-odds, que a
transformação logística leva a 71,2%; o gráfico identifica essa unidade e
a referência.

Figura — Análise de partida: mapa de calor, diferença de ouro e objetivos até o minuto 14 | reports/figuras_texto/fig_partida.png

Figura — Simulador, aba Estado: probabilidade de vitória e contribuição de cada variável (SHAP, em log-odds) | reports/figuras_texto/fig_simulador_estado.png

### 5.6 Interface em linguagem natural (objetivo g)

A consulta em linguagem natural (*text-to-SQL* com validação e roteamento entre as bases) foi medida em um gabarito gerado por modelos de pergunta (*templates*): cada pergunta nasce com a SQL de referência, escrita antes de qualquer execução, e um programa compara os resultados (Apêndice B). Das perguntas geradas, 203 foram amostradas ao acaso. O sistema acertou **181 de 203 (89,2%)**, com intervalo de Wilson de 95% de 84,1% a 92,7%: 166 de 187 perguntas respondíveis e 15 de 16 recusas esperadas. O resultado verifica o valor devolvido, não o rótulo da coluna nem a forma da SQL.

As 22 falhas vêm de nomes de entidade escritos de outro modo pelo modelo ("Monkey King" no lugar de MonkeyKing), de abates somados indevidamente às assistências e de roteamento para a base errada. As três correções feitas depois (nome exato das entidades resolvido no banco, consulta refeita quando os abates são somados indevidamente às assistências, e envio direto ao competitivo de pergunta com liga, equipe ou jogador profissional) não foram medidas de ponta a ponta; a versão medida, a base congelada e a configuração do modelo de linguagem estão no Apêndice B. Quando o banco não tem o dado, uma recusa determinística responde antes do modelo.

Antes de executar, a SQL passa por controles: um único comando, iniciado por `SELECT` ou `WITH`; bloqueio de palavras de escrita e administração (`INSERT`, `UPDATE`, `DELETE`, `DROP` e outras); e lista fechada de tabelas permitidas. A execução ocorre em transação somente leitura, com tempo limite de 10 segundos. Esses controles impedem escrita no banco e consulta a tabelas fora da lista, mas não verificam se a consulta responde à pergunta (Seção 6.1).

### 5.7 Os resultados frente à literatura

Hodge et al. (2021) chegam a 85% de acurácia após 5 minutos em partidas
profissionais de *Dota 2*, mas tratam apenas da previsão. Este trabalho leva a
predição por fases a *League of Legends* e a integra a explicabilidade,
visualização e consulta em uma mesma solução. Entre os estudos de *League of
Legends*, Jadowski e Cunningham (2022) reportam 67% de acerto em jogos
profissionais e Do et al. (2021), 75,1% antes de a partida começar, a
partir da experiência com o campeão. As acurácias deste trabalho, de 70,2%
a 80,7% conforme o corte, ficam na mesma ordem de grandeza, mas a
comparação é apenas indicativa: mudam o nível dos jogadores, o momento da
previsão e a informação usada.

Quanto às escolhas de projeto, as variáveis preditoras, diferenças agregadas entre os dois times, seguem
a modelagem centrada no time de Birant e Birant (2023); a granularidade
por jogador de Bahrololloomi et al. (2022) entrou apenas nos perfis de
jogador. A limitação que García-Méndez e
Arriba-Pérez (2025) apontam nos trabalhos anteriores, a falta de
interpretação das previsões, foi enfrentada com o SHAP na interface e com um
módulo de orientação que separa o dado real do conhecimento geral, cuja
auditoria confere apenas os números (Apêndice B).

---

## 6 CONCLUSÃO

Este trabalho teve como objetivo geral desenvolver uma plataforma
inteligente para análise de dados de esports com foco em *League of
Legends*, integrando coleta, organização e exploração de dados
competitivos, modelagem preditiva com técnicas de aprendizado de máquina e
mecanismos de visualização e consulta em linguagem natural. Os
resultados apresentados na Seção 5 indicam que o objetivo geral foi
alcançado, com evidência para cada objetivo específico:

a) os dados e recursos da Riot Games API foram mapeados e utilizados de
forma sistemática (*endpoints* *league-v4*, *account-v1* e *match-v5*, com linha do tempo);

b) as informações relevantes de partidas, jogadores e estatísticas
foram organizadas em um esquema relacional específico;

c) foi estruturado e executado um processo de coleta, tratamento e
organização capaz de escalar de um piloto de cerca de 100 partidas para uma
base de 41.063 partidas de *solo queue* somadas a 99.259 jogos profissionais;

d) técnicas de análise de dados identificaram o viés de lado no *solo queue* de elo alto,
com taxas próximas nos quatro cortes entre partidas com diferença de ouro inferior a 500 e
nenhuma diferença detectada entre eles, e sua inversão em relação ao
cenário profissional, achados sustentados por testes de robustez estatística;

e) três modelos de aprendizado de máquina (XGBoost, *Random Forest* e MLP) e
uma regressão logística de referência ficaram próximos após o ajuste (AUC-ROC de 0,8480 a 0,8495 no corte de 15 minutos); o
XGBoost foi mantido em produção (acurácia 0,7641, AUC-ROC 0,8487) pela
proximidade dos resultados e pela integração com o SHAP, com modelos
adicionais para os cortes de 10, 20 e 25 minutos;

f) *dashboards* foram entregues em seis páginas de visualização;

g) uma interface em linguagem natural foi implementada e avaliada: acertou 181 de 203 perguntas (89,2%) de um gabarito gerado por modelos de pergunta, 166 de 187 respondíveis e 15 de 16 recusas esperadas.

O achado que merece destaque, por não ter sido o objeto anunciado do trabalho, é o viés de lado: uma assimetria entre os dois lados do mapa, estatisticamente firme em três das quatro regiões com amostra suficiente (BR1, EUW1, NA1; a KR tem intervalo de confiança que inclui 50%) e com sinal invertido no jogo profissional. Ele é um fator de confusão que qualquer modelo preditivo sobre *solo queue* precisa controlar; a origem da inversão fica como hipótese, que este trabalho delimita sem comprovar. Os dados profissionais permitiram ainda medir a diferença na conversão de vantagem material em vitória entre os dois contextos, sem atribuí-la a uma causa.

### 6.1 LIMITAÇÕES E AMEAÇAS À VALIDADE

Registrar o que o trabalho não sustenta é parte da conclusão. Nenhuma das
limitações a seguir invalida os achados. Elas delimitam até onde eles
valem.

**Validade de construto.** A linha do tempo do *match-v5* não registra o estado das ondas
de *minions* nem a ordem de escolha de campeões (*draft*), e nenhuma API
pública da Riot expõe micro-posicionamento. Os experimentos de enriquecimento de variáveis (Seção 5.4), inclusive a posição dos jogadores, que existe na *timeline* e foi testada, acrescentaram, aos 15 minutos, até +0,0044 de AUC-ROC no XGBoost e +0,0073 na regressão logística, cada um contra o mesmo classificador com as cinco variáveis originais. Um ganho maior pode depender de informação que a fonte não tem. Que parte do erro
do modelo venha dessa informação ausente é hipótese, não resultado medido.
Por isso nenhuma orientação que dependa do estado das ondas, ou de itens e posição além do que o
módulo de orientação recebe dos dados, vem do modelo preditivo, e a interface a marca como inferência geral.

**Validade externa.** Os resultados de *solo queue* vêm da fila ranqueada, nas faixas Desafiante a Mestre, em cinco regiões, quatro delas com amostra suficiente e desiguais entre si: a KR tem intervalo que inclui 50%, e o *patch* 16.13 concentra 40,4% da coleta. Não há base para estender as taxas por lado nem a acurácia a outras filas, elos, versões ou jogos, ainda que a arquitetura seja reaproveitável.

**Validade interna.** As partidas foram coletadas em janelas de tempo, sem amostragem ao longo de todo o histórico, e um padrão sazonal pode estar confundido com o que os dados descrevem. A validação cruzada sorteia partidas ao acaso, e jogadores que se repetem tornam as dobras menos independentes do que a técnica supõe. Treinar no passado e testar no futuro, porém, só reduziu a AUC-ROC em um caso (0,0026, dentro do intervalo de confiança; Apêndice C). Recortes finos, como um jogador em um campeão ou um confronto de rota, seguem frágeis mesmo com 41.063 partidas, apesar do encolhimento estatístico (*shrinkage*).

**Limitações do modelo.** O XGBoost não garante monotonicidade isolada por variável, por não usar restrição formal. A calibração foi verificada nas previsões fora da dobra: nas partidas empatadas, a média prevista fica a menos de 0,5 ponto percentual da taxa observada em todos os cortes (Apêndice C).

**Validade da consulta em linguagem natural.** A medida principal (203 perguntas de template, escritas pelo autor a partir de famílias de erro já conhecidas) pode superestimar o resultado em perguntas livres: em versões anteriores do sistema, dois conjuntos de 50 perguntas escritas à mão acertaram 27 e 30 (54% e 60%). As correções posteriores não foram medidas.

### 6.2 TRABALHOS FUTUROS

Ficam registrados três caminhos. O primeiro é a extensão da predição para partidas ao vivo, prevista na arquitetura mas não implementada: a barreira é de dados em tempo real, não de modelo. O segundo é a ampliação do recorte (validade externa), com outras filas e, eventualmente, outro jogo, para testar se o viés de lado descreve o jogo ou o modo de jogar de uma população específica. O terceiro é a melhoria da consulta em linguagem natural: verificação do resultado depois da execução, um gabarito maior com perguntas escritas à mão, avaliação sobre vários bancos de teste (Zhong; Yu; Klein, 2020) e um modelo aberto local para comparar com a API.

---

## REFERÊNCIAS

BAHROLOLLOOMI, Farnod; SAUER, Sebastian; KLONOWSKI, Fabio; HORST,
Robin; DÖRNER, Ralf. A machine learning based analysis of e-sports player
performances in League of Legends for winning prediction based on player roles and
performances. In: INTERNATIONAL JOINT CONFERENCE ON COMPUTER
VISION, IMAGING AND COMPUTER GRAPHICS THEORY AND APPLICATIONS,
17., 2022, on-line. **Proceedings of the 17th International Joint Conference on
Computer Vision, Imaging and Computer Graphics Theory and Applications
(VISIGRAPP 2022): Volume 2: HUCAPP**. [S. l.]: SciTePress, 2022. p. 68-76. DOI:
10.5220/0010895900003124.

BIRANT, Kokten Ulas; BIRANT, Derya. Multi-Objective Multi-Instance Learning: a
new approach to machine learning for eSports. **Entropy**, [S. l.], v. 25, n. 1, art. 28,
2023. DOI: 10.3390/e25010028. Disponível em: https://www.mdpi.com/1099-4300/25/1/28. Acesso em: 10 jun. 2026.

BREIMAN, Leo. Random Forests. **Machine Learning**, [S. l.], v. 45, n. 1, p. 5-32,
2001. DOI: 10.1023/A:1010933404324.

BROWN, Lawrence D.; CAI, T. Tony; DASGUPTA, Anirban. Interval estimation for a
binomial proportion. **Statistical Science**, [S. l.], v. 16, n. 2, p. 101-133,
2001. DOI: 10.1214/ss/1009213286.

CHEN, Tianqi; GUESTRIN, Carlos. XGBoost: a scalable tree boosting system. In: ACM SIGKDD INTERNATIONAL CONFERENCE ON KNOWLEDGE DISCOVERY AND DATA MINING, 22., 2016, San Francisco. **Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining**. New York: ACM, 2016. p. 785-794. DOI: 10.1145/2939672.2939785.

CRESWELL, John W.; CRESWELL, J. David. **Research design**: qualitative,
quantitative, and mixed methods approaches. 6. ed. Thousand Oaks: SAGE
Publications, 2023.

DO, Tiffany D.; WANG, Seong Ioi; YU, Dylan S.; MCMILLIAN, Matthew G.; MCMAHAN,
Ryan P. Using machine learning to predict game outcomes based on
player-champion experience in League of Legends. In: INTERNATIONAL CONFERENCE
ON THE FOUNDATIONS OF DIGITAL GAMES, 16., 2021, on-line. **Proceedings of the 16th
International Conference on the Foundations of Digital Games**. New York: ACM,
2021. DOI: 10.1145/3472538.3472579.

GARCÍA-MÉNDEZ, Silvia; ARRIBA-PÉREZ, Francisco de. Explainable e-sports win
prediction through machine learning classification in streaming. **Entertainment
Computing**, [S. l.], v. 55, art. 101027, 2025. DOI: 10.1016/j.entcom.2025.101027.
Disponível em:
https://www.sciencedirect.com/science/article/pii/S1875952125001077. Acesso em:
10 jun. 2026.

GIL, Antonio Carlos. **Como elaborar projetos de pesquisa**. 4. ed. São Paulo: Atlas,
2002.

GRINSZTAJN, Léo; OYALLON, Edouard; VAROQUAUX, Gaël. Why do tree-based models still outperform deep learning on typical tabular data? In: CONFERENCE ON NEURAL INFORMATION PROCESSING SYSTEMS, 36., 2022, New Orleans. **Advances in Neural Information Processing Systems 35**. Red Hook: Curran Associates, 2022. Disponível em: https://arxiv.org/abs/2207.08815. Acesso em: 20 out. 2026.

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

JADOWSKI, Robbie; CUNNINGHAM, Stuart. Statistical models for predicting results
in professional League of Legends. In: WÖLFEL, Matthias; BERNHARDT, Johannes;
THIEL, Sonja (ed.). **ArtsIT, Interactivity and Game Creation**. Cham: Springer
International Publishing, 2022. p. 138-152. DOI: 10.1007/978-3-030-95531-1_10.

JIANG, Jie; XIE, Haining; SHEN, Siqi; SHEN, Yu; ZHANG, Zihan; LEI, Meng;
ZHENG, Yifeng; LI, Yang; LI, Chunyou; HUANG, Danqing; WU, Yinjun; ZHANG,
Wentao; YANG, Xiaofeng; CUI, Bin; CHEN, Peng. SiriusBI: a comprehensive
LLM-powered solution for data analytics in business intelligence. **Proceedings of the
VLDB Endowment**, [S. l.], v. 18, n. 12, p. 4860-4873, 2025. DOI:
10.14778/3750601.3750610.

KAUFMAN, Shachar; ROSSET, Saharon; PERLICH, Claudia; STITELMAN, Ori. Leakage in
data mining: formulation, detection, and avoidance. **ACM Transactions on
Knowledge Discovery from Data**, [S. l.], v. 6, n. 4, art. 15, 2012. DOI:
10.1145/2382577.2382579.

KOHAVI, Ron. A study of cross-validation and bootstrap for accuracy estimation
and model selection. In: INTERNATIONAL JOINT CONFERENCE ON ARTIFICIAL
INTELLIGENCE, 14., 1995, Montreal. **Proceedings of the 14th International Joint
Conference on Artificial Intelligence (IJCAI-95)**. San Mateo: Morgan Kaufmann,
1995. p. 1137-1143.

LUNDBERG, Scott M.; LEE, Su-In. A unified approach to interpreting model predictions. In: CONFERENCE ON NEURAL INFORMATION PROCESSING SYSTEMS, 31., 2017, Long Beach. **Advances in Neural Information Processing Systems 30**. Red Hook: Curran Associates, 2017. p. 4765-4774. Disponível em: https://arxiv.org/abs/1705.07874. Acesso em: 4 out. 2026.

MAYMIN, Philip Z. Smart kills and worthless deaths: eSports analytics for
League of Legends. **Journal of Quantitative Analysis in Sports**, [S. l.], v.
17, n. 1, p. 11-27, 2021. DOI: 10.1515/jqas-2019-0096.

NICULESCU-MIZIL, Alexandru; CARUANA, Rich. Predicting good probabilities with
supervised learning. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 22.,
2005, Bonn. **Proceedings of the 22nd International Conference on Machine Learning
(ICML 2005)**. New York: ACM, 2005. p. 625-632. DOI: 10.1145/1102351.1102430.

ORACLE'S ELIXIR. **Downloads**: dados de partidas profissionais de League of
Legends. [S. l.], [s. d.]. Disponível em:
https://oracleselixir.com/tools/downloads. Acesso em: 4 jul. 2026.

PEDREGOSA, Fabian et al. Scikit-learn: machine learning in Python. **Journal of
Machine Learning Research**, [S. l.], v. 12, p. 2825-2830, 2011.

PRODANOV, Cleber Cristiano; FREITAS, Ernani Cesar de. **Metodologia do
trabalho científico**: métodos e técnicas da pesquisa e do trabalho acadêmico.
2. ed. Novo Hamburgo: Feevale, 2013.

RIBEIRO, Marco Tulio; SINGH, Sameer; GUESTRIN, Carlos. "Why should I trust you?": explaining the predictions of any classifier. In: ACM SIGKDD INTERNATIONAL CONFERENCE ON KNOWLEDGE DISCOVERY AND DATA MINING, 22., 2016, San Francisco. **Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining**. New York: ACM, 2016. p. 1135-1144. DOI: 10.1145/2939672.2939778.

RIOT GAMES. **APIs**. [S. l.], [s. d.]. Disponível em:
https://developer.riotgames.com/apis. Acesso em: 3 nov. 2026.

WALLNER, Günter; WANG, Letian; DORMANN, Claire. Visualizing the
spatio-temporal evolution of gameplay using storyline visualization: a study with League of
Legends. **Proceedings of the ACM on Human-Computer Interaction**, New York, v.
7, n. CHI PLAY, art. 412, p. 1002-1024, 2023. DOI: 10.1145/3611058.

WANG, Bailin; SHIN, Richard; LIU, Xiaodong; POLOZOV, Oleksandr; RICHARDSON, Matthew. RAT-SQL: relation-aware schema encoding and linking for text-to-SQL parsers. In: ANNUAL MEETING OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 58., 2020, on-line. **Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics**. [S. l.]: Association for Computational Linguistics, 2020. p. 7567-7578. DOI: 10.18653/v1/2020.acl-main.677.

ZHONG, Ruiqi; YU, Tao; KLEIN, Dan. Semantic evaluation for text-to-SQL with
distilled test suites. In: CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE
PROCESSING, 2020, on-line. **Proceedings of the 2020 Conference on Empirical Methods in
Natural Language Processing (EMNLP)**. [S. l.]: Association for Computational
Linguistics, 2020. p. 396-411. DOI: 10.18653/v1/2020.emnlp-main.29.

---

## APÊNDICE A - Esquema relacional do banco de dados

O banco de dados (PostgreSQL) segue o esquema do Quadro 4. As
tabelas `raw_matches` e `raw_timelines` guardam o JSON bruto da Riot API,
para reprocessar sem nova coleta; as demais são a normalização relacional
usada pela análise e pela modelagem. Na coluna de chaves, PK indica a
chave primária (*primary key*) e FK, a chave estrangeira (*foreign key*);
JSONB é o tipo do PostgreSQL que guarda JSON em formato binário.

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
resolvidos; `items` é o catálogo do Data Dragon. Índices cobrem as colunas
mais filtradas (campeão, jogador, versão do jogo e liga).

---

## APÊNDICE B - Avaliação da interface em linguagem natural e auditoria do coach

A medida principal da consulta em linguagem natural é o gabarito automático descrito a seguir. O apêndice traz também as versões e o congelamento dos dados da medição e a auditoria do módulo de orientação estratégica (*coach*).

**Gabarito automático (medida principal, 5 de novembro de 2026).** Um gerador monta perguntas por templates sobre entidades reais do banco (campeões, equipes, ligas, *patches*, jogadores e itens) e escreve, junto de cada uma, a SQL de referência, que é executada na hora; pergunta com gabarito vazio, com empate no limite de um ranking ou repetida é descartada. Parte das perguntas não tem resposta no banco (primeiro sangue, série, ouro aos 10 minutos, dano a estruturas) e espera uma recusa. O sistema roda as perguntas pelo caminho do produto e um comparador automático compara: em pergunta de valor único (escalar), passa se qualquer valor numérico da primeira linha do sistema coincidir com o último valor da primeira linha do gabarito (tolerância de 0,1%, aceitando fração ou percentual), sem conferir o nome da coluna; essa regra poderia aceitar a coluna errada, mas nenhum dos 146 acertos escalares tinha mais de uma coluna numérica na primeira linha; em ranking, a chave de cada linha do gabarito aparece na mesma posição; recusa esperada só passa se toda base consultada recusou; resposta na base errada falha. A comparação não depende de avaliador, e as regras do comparador têm testes automatizados. O conjunto avaliado tem 203 perguntas, amostradas ao acaso: **181 de 203 certas (89,2%)**, intervalo de 95% de 84,1% a 92,7%, com 166 de 187 respondíveis e 15 de 16 recusas esperadas. Falhas: 16 valores diferentes do gabarito, 2 recusas indevidas, 3 roteamentos para a base errada e 1 resposta onde o banco não tem o dado. As 22 foram lidas uma a uma: todas são do sistema, nenhuma do gabarito ou do comparador. A maior família foi nome de entidade (o modelo escrevia 'Monkey King' para MonkeyKing, tratava ligas como equipe, trocava LPLOL por LPL), seguida de abates somados indevidamente às assistências. Três correções (a resolução do nome exato das entidades no banco, o envio ao competitivo de pergunta com liga, equipe ou jogador profissional e uma checagem que refaz a consulta) vieram depois da medida e não foram medidas de ponta a ponta. Limites: o texto é de template, o autor conhecia as famílias de erro e algumas famílias de pergunta têm poucos exemplos.

**Versões e congelamento dos dados.** As etapas com modelo de linguagem usam o Claude Haiku 4.5 (`claude-haiku-4-5-20251001`), pela API da Anthropic: a geração de SQL com temperatura 0 e até 1.200 *tokens* de saída; o roteamento, no resíduo das regras, com temperatura 0 e até 16 *tokens*; a explicação do resultado ("Leitura de jogo") com temperatura 0 e até 500 *tokens*; e o *coach* com temperatura 0,4 (0,2 na releitura que extrai os itens sugeridos). O gabarito rodou em 5 de novembro de 2026, às 19h16, sobre a versão marcada no repositório do projeto (https://github.com/tamiosso125/lol-analytics) com a etiqueta `gabarito-203`, que reproduz os *hashes* dos arquivos de roteamento, validação, esquema e geração de SQL gravados no resultado; a versão final acrescenta as três correções citadas. A base estava congelada: a última partida de *solo queue* entrou no banco em 4 de outubro de 2026, e os arquivos profissionais são de 4 de julho de 2026, sem linha nova depois disso. A SQL de referência e a do sistema rodaram na mesma execução, sobre o mesmo estado do banco.

Auditoria do coach, de 4 de novembro de 2026: 36 respostas do módulo de orientação estratégica, geradas pelo mesmo caminho do produto sobre partidas reais (12 de cada modo: partida completa, composição e só estado; cortes de 15, 20 e 25 minutos). Cada número da resposta foi conferido contra os dados fornecidos ao modelo de linguagem (o *prompt* sem as instruções), e os 13 que o detector não encontrou nos dados foram revisados à mão. A saída do modelo de linguagem varia entre execuções (temperatura 0,4), e o Quadro 5 é de uma execução. A auditoria é anterior à mudança de 8 de novembro de 2026, em que o *prompt* passou a informar a unidade (log-odds) e o valor de referência do SHAP.

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

## APÊNDICE C - Métricas completas por corte temporal e calibração

O Quadro 6 reúne os três modelos nos quatro cortes, na configuração
de referência para *Random Forest* e MLP, com validação cruzada
estratificada de 5 dobras (semente 42) sobre as partidas elegíveis de cada
corte (41.063 no banco; o número usado em cada corte varia, Quadro 3). O
Quadro 7 descreve as configurações, o Quadro 8 treina no passado e testa no
futuro, o Quadro 9 separa o efeito do corte e o Quadro 10 traz a calibração do
modelo de produção, com a Figura 5.

Quadro — Métricas completas por corte temporal, comparação entre os três modelos

| Corte | n | Taxa de vitória do azul | Modelo | Acurácia | Precisão | *Recall* | F1 | AUC-ROC |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| 10 min | 40.919 | 0,467 | *Random Forest* | 0,6721 | 0,6538 | 0,6331 | 0,6433 | 0,7362 |
| 10 min | 40.919 | 0,467 | **XGBoost** | 0,7020 | 0,6932 | 0,6492 | 0,6704 | 0,7752 |
| 10 min | 40.919 | 0,467 | MLP | 0,7003 | 0,6928 | 0,6436 | 0,6673 | 0,7741 |
| 15 min | 40.778 | 0,467 | *Random Forest* | 0,7439 | 0,7312 | 0,7144 | 0,7227 | 0,8278 |
| 15 min | 40.778 | 0,467 | **XGBoost** | 0,7641 | 0,7576 | 0,7278 | 0,7424 | 0,8487 |
| 15 min | 40.778 | 0,467 | MLP | 0,7619 | 0,7488 | 0,7378 | 0,7433 | 0,8459 |
| 20 min | 34.505 | 0,467 | *Random Forest* | 0,7699 | 0,7575 | 0,7466 | 0,7520 | 0,8533 |
| 20 min | 34.505 | 0,467 | **XGBoost** | 0,7856 | 0,7770 | 0,7590 | 0,7679 | 0,8690 |
| 20 min | 34.505 | 0,467 | MLP | 0,7832 | 0,7706 | 0,7635 | 0,7670 | 0,8666 |
| 25 min | 25.098 | 0,468 | *Random Forest* | 0,7937 | 0,7825 | 0,7749 | 0,7786 | 0,8761 |
| 25 min | 25.098 | 0,468 | **XGBoost** | 0,8068 | 0,7991 | 0,7848 | 0,7919 | 0,8899 |
| 25 min | 25.098 | 0,468 | MLP | 0,8029 | 0,7945 | 0,7811 | 0,7877 | 0,8846 |

Quadro — Configuração dos três modelos comparados

| Modelo | Configuração | Origem |
|---|---|---|
| XGBoost | 500 árvores, taxa de aprendizado 0,01, profundidade 3 | busca em grade (27 combinações) sobre a base de 10.295 partidas, contidas nas 40.778 da avaliação; repetida nas 40.778, a busca escolheu a mesma configuração (1º lugar entre 27) |
| XGBoost aninhado | grade de 27 combinações escolhida só no treino de cada dobra (3 dobras internas) | a produção foi escolhida em 3 das 5 dobras; acurácia 0,7637, AUC-ROC 0,8485 |
| *Random Forest* (referência) | 500 árvores, demais parâmetros do scikit-learn | sem busca em grade |
| *Random Forest* ajustada | 200 árvores, profundidade 6, mínimo de 5 amostras por folha | busca em grade (27 combinações) nas 40.778, avaliada nas mesmas dobras: 0,7628 e 0,8480; aninhada: 0,7625 e 0,8480 |
| MLP (referência) | camadas de 64 e 32 neurônios, variáveis padronizadas, até 500 iterações | sem busca em grade |
| MLP ajustado | camada de 32 neurônios, regularização 0,001, até 1.000 iterações | busca em grade (9 combinações) nas 40.778, avaliada nas mesmas dobras: 0,7638 e 0,8491; aninhada: 0,7635 e 0,8491 |

Quadro — Treino no passado e teste no futuro, XGBoost

| Corte | Divisão | Treino | Teste | Acurácia | AUC-ROC | Intervalo de 95% da AUC-ROC |
|---|---|---:|---:|---:|---:|---|
| 10 min | Cronológica 80/20 | 32.735 | 8.184 | 0,7034 | 0,7792 | 0,7694 a 0,7890 |
| 10 min | Por *patch* | 23.625 | 17.294 | 0,7082 | 0,7841 | 0,7773 a 0,7905 |
| 10 min | Aleatória 80/20 | 32.735 | 8.184 | 0,7087 | 0,7818 | 0,7713 a 0,7912 |
| 15 min | Cronológica 80/20 | 32.622 | 8.156 | 0,7739 | 0,8570 | 0,8491 a 0,8641 |
| 15 min | Por *patch* | 23.532 | 17.246 | 0,7691 | 0,8567 | 0,8514 a 0,8621 |
| 15 min | Aleatória 80/20 | 32.622 | 8.156 | 0,7553 | 0,8415 | 0,8333 a 0,8501 |
| 20 min | Cronológica 80/20 | 27.604 | 6.901 | 0,7948 | 0,8762 | 0,8683 a 0,8839 |
| 20 min | Por *patch* | 20.138 | 14.367 | 0,7919 | 0,8743 | 0,8686 a 0,8800 |
| 20 min | Aleatória 80/20 | 27.604 | 6.901 | 0,7858 | 0,8699 | 0,8616 a 0,8780 |
| 25 min | Cronológica 80/20 | 20.078 | 5.020 | 0,8122 | 0,8937 | 0,8849 a 0,9020 |
| 25 min | Por *patch* | 15.055 | 10.043 | 0,8082 | 0,8920 | 0,8859 a 0,8984 |
| 25 min | Aleatória 80/20 | 20.078 | 5.020 | 0,8098 | 0,8891 | 0,8799 a 0,8980 |

Na divisão cronológica, as 80% mais antigas treinam e as 20% mais recentes testam; na divisão por *patch*, os *patches* 16.10 a 16.13 treinam e
os 16.14 a 16.19 testam; na aleatória, o teste tem o mesmo tamanho do
cronológico. A divisão temporal só fica abaixo da aleatória uma vez, na cronológica aos 10 minutos (−0,0026, com intervalos sobrepostos); nos demais casos fica igual ou acima, de modo que não houve sinal de ganho artificial por misturar épocas na validação cruzada, ressalvada a
diferença regional descrita adiante. Esta é a resposta ao aviso de Kaufman et al. (2012) sobre dados que
mudam com o tempo. A regressão logística dá o mesmo padrão, com diferença de
até 0,0013 de AUC-ROC para o XGBoost em todas as divisões. A ressalva é que a
região se mistura ao tempo: aos 15 minutos, o teste cronológico tem
44,3% de NA1 e nenhuma partida de BR1, que é 36,2% do treino. O resultado vale
também para uma composição regional diferente da do treino, mas não separa o
efeito do tempo do efeito da região.

Quadro — AUC-ROC do XGBoost por corte, nas partidas elegíveis e nas mesmas partidas

| Corte | Partidas elegíveis | AUC-ROC | Mesmas partidas | AUC-ROC |
|---|---:|---:|---:|---:|
| 10 min | 40.919 | 0,7752 | 25.098 | 0,6444 |
| 15 min | 40.778 | 0,8487 | 25.098 | 0,7126 |
| 20 min | 34.505 | 0,8690 | 25.098 | 0,7870 |
| 25 min | 25.098 | 0,8899 | 25.098 | 0,8899 |

As mesmas partidas são as 25.098 que chegam aos 25 minutos, avaliadas nos
quatro cortes com o mesmo protocolo (5 dobras, semente 42). O desempenho
cresce com o corte nos dois casos.

Quadro — Calibração do XGBoost nas partidas empatadas, com probabilidades fora da dobra

| Corte | Partidas empatadas | Taxa observada do azul (intervalo de 95%) | Média prevista | Diferença | Maior desvio entre decis |
|---|---:|---:|---:|---:|---:|
| 10 min | 7.639 | 46,5% (45,3% a 47,6%) | 46,5% | −0,01 pp | 1,21 pp |
| 15 min | 4.126 | 47,8% (46,3% a 49,4%) | 47,6% | −0,19 pp | 1,19 pp |
| 20 min | 2.500 | 46,9% (44,9% a 48,8%) | 47,0% | +0,08 pp | 0,73 pp |
| 25 min | 1.474 | 47,4% (44,9% a 50,0%) | 47,8% | +0,38 pp | 1,78 pp |

As probabilidades vêm da validação cruzada estratificada de 5 dobras
(semente 42) sobre as partidas elegíveis de cada corte (de 40.919 aos 10
minutos a 25.098 aos 25): cada partida é prevista por um modelo que não a
viu no treino. As partidas empatadas são as de diferença absoluta de ouro
inferior a 500 no corte, as mesmas da Seção 5.3, e nelas a média prevista
fica dentro do intervalo de 95% da taxa observada em todos os cortes. A
previsão para um estado sintético com as cinco diferenças iguais a zero
(de 48,5% a 51,5%, conforme o corte) não serve a essa comparação: nenhuma
das partidas empatadas tem as cinco diferenças nulas, e a experiência, os
abates, as torres e os dragões também informam o modelo. A última coluna
compara, em cada decil da probabilidade prevista, a média prevista com a
taxa observada; a Figura 5 mostra esses decis nos quatro cortes.

Figura — Curva de calibração do XGBoost nos quatro cortes, por decis da probabilidade prevista fora da dobra | reports/figuras_texto/fig_calibracao.png

---

## APÊNDICE D - Origem das imagens e aviso da Riot Games

A imagem da tela de análise de partida (Figura 3) mostra ícones, mapa e ilustrações do jogo, que são propriedade da Riot Games. Os ícones de itens vêm do Data Dragon, da própria Riot; os ícones e a arte dos campeões e o mapa vêm do Community Dragon, projeto da comunidade que extrai os arquivos do cliente do jogo e declara ter sido criado sob a política "Legal Jibber Jabber" da Riot (https://github.com/communitydragon/docs). A política da Riot para quem usa a sua API (https://developer.riotgames.com/policies/general, acesso em 11 nov. 2026) pede este aviso: “o Bellestraiko não é endossado pela Riot Games e não reflete as visões ou opiniões da Riot Games nem de ninguém oficialmente envolvido na produção ou na gestão das propriedades da Riot Games; Riot Games e todas as propriedades associadas são marcas ou marcas registradas da Riot Games, Inc.” (tradução nossa). {{NOTA_ORIGINAL_RIOT}}

---

## Pendências finais antes da entrega

1. ~~Resumo/Abstract~~ — **feito**.
2. **Título acadêmico — DECIDIDO (2026-10-03): não citar Bellestraiko.**
   O título do TCC 2 é o mesmo do TCC 1 ("Plataforma Inteligente para
   Análise de Dados de Esports: uma proposta para League of Legends com
   uso de machine learning e interface em linguagem natural"). Decisão do
   autor: por ser o mesmo trabalho, o título acompanha o do TCC 1. O nome
   do produto foi registrado no corpo, na introdução: "A plataforma,
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
(APROVADO COM RESSALVAS), `docs/verifica_tcc.py` (23 checagens de
consistência do texto contra o banco e os artefatos, exit 0),
`docs/confere_docx.py` (conformidade formal do `.docx`, exit 0), e
`cd frontend; npm run lint; npm run test` (38/38).

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
