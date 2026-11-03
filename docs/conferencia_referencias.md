# Conferência das referências contra os artigos

Feita em 2026-11-02. Objetivo: verificar se cada frase do TCC sobre um
trabalho citado confere com o que o trabalho diz, lendo o texto completo
sempre que possível. É a pergunta que um avaliador que conheça o artigo
faria: "isso está mesmo no artigo?".

## O que foi lido, e como

| Obra | Acesso | Leitura |
|---|---|---|
| Hodge; Birant; Bahrololloomi; García-Méndez; Guo; Wallner; Do; Guan e Tung; Jadowski; Maymin | PDF completo no computador | texto completo, com busca por cada afirmação do TCC |
| Holm (1979) | PDF no computador | conferido o título e o procedimento |
| Chen e Guestrin; Lundberg e Lee; Ribeiro et al.; Wang et al.; Zhong et al.; Niculescu-Mizil e Caruana; Jiang et al. (SiriusBI) | texto completo, acesso aberto | texto completo, com busca |
| Grinsztajn et al. | texto colado por você em 2026-11-02 (o PDF passa do limite da ferramenta de leitura); a colagem foi cortada na Figura 9 do Apêndice A.2.2 | texto completo até A.2.2 |
| Brown, Cai e DasGupta; Kaufman et al. | só o resumo (acesso restrito) | resumo |
| Kohavi (1995) | lido em 2026-10-20 | recomenda validação cruzada estratificada de 10 *folds* |
| Hornik et al.; Breiman; Hanley e McNeil; Pedregosa et al. | **não relidos** | citados por afirmações canônicas (aproximação universal, *Random Forest*, AUC como probabilidade de ordenar certo um par, scikit-learn) |
| Prodanov e Freitas; Gil; Creswell e Creswell; Yin | **sem acesso** (livros) | classificação da pesquisa, como no TCC I |

Os textos extraídos estão no scratchpad da sessão e não são versionados;
são só leitura e não produzem número do TCC.

## Estudos de domínio

| Estudo | Onde o TCC o cita | Resultado |
|---|---|---|
| **Hodge et al. (2021)** | 2.1, 3.1, 5.7 | **Confere.** Dota 2, profissional, ao vivo, "até 85% após 5 min". Ressalva que o TCC não diz: os 85% saem de **28 jogos ao vivo do ESL One Hamburg 2017**, com treino em dados de habilidade mista (~5,7 mil partidas) |
| **Birant e Birant (2023)** | 1, 2.1, 3.2, 5.7 | **Confere** (abordagem centrada no time, MOMIL). Ressalva: os "até 95%" usam **resumos do fim da partida** (abates, assistências, mortes, dano, ouro por jogador); o próprio artigo chama esses atributos de *post-game*. Não comparável com previsão em jogo |
| **Bahrololloomi et al. (2022)** | 2.1, 3.2, 5.7 | **Confere** (funções e métricas individuais; partidas ranqueadas solo coletadas pela Riot API). "Desempenho competitivo", em 2.1, é elástico: são partidas ranqueadas |
| **Jadowski e Cunningham (2022)** | 3.2, 5.3, 5.7 | **Confere**: 67,3% de 306 jogos (Summer Split 2020); azul 54,08% de 882 jogos, χ² p = 0,015; "90%+ improvável pelas zebras" |
| **Do et al. (2021)** | 3.2, 5.7 | **Confere**: 75,1% com rede neural profunda, pré-jogo. Ressalva: o *gradient boosting* teve 75,4%, acima da rede; RF 74,7%, SVC 74,3%, kNN 72,7% |
| **Maymin (2021)** | 3.2, 3.6, 5.7 | **Confere**: modelo de probabilidade em jogo com milhões de partidas, sem o ouro. Contém um **mapa de calor de posição** (Figura 4), que o TCC ainda não usa como precedente |
| **Guan e Tung (2026)** | 3.2, 5.3, 5.7 | **Confere**: pré-jogo, profissional, *first pick* como covariável, 5.135 jogos de 2024 a 2026; o Brier vem da pontuação RPS reduzida a dois resultados. Não reporta taxa por lado (nenhuma taxa de vitória por lado aparece no texto) |
| **García-Méndez e Arriba-Pérez (2025)** | 1, 2.3, 3.3, 3.6, 5.7 | **Dois pontos a corrigir.** 1 e 2.3 conferem. **3.3 e 5.7 exageram**: o artigo diz que a falta de interpretabilidade é "uma das limitações mais significativas" dos trabalhos anteriores; não diz que a previsão "só é útil" com explicação. E o jogo é **CS:GO profissional** (Kaggle/HLTV, 92,5%), o que o texto não diz |
| **Jiang et al. (2025)** | 2.4, 3.4, 5.7 | **Confere**: BI com LLM na Tencent, mais de 93% de acerto em SQL (97%, 93% e 96% por setor), diálogo de várias rodadas, estudo com 40 analistas. A referência bate com o título da versão do PVLDB |
| **Guo et al. (2024)** | 2.4, 3.4, 5.7 | **Um ponto a corrigir.** 3.4 e 5.7 conferem. **2.4 atribui "diálogo" ao Guo**, mas o Talk2Data não tem diálogo (a única menção está nas referências, a outro sistema). O diálogo de várias rodadas é do SiriusBI |
| **Wallner et al. (2023)** | 2.5, 3.5, 5.7 | **Confere** (*storyline* integrando tempo e posição, revisão pós-partida). Ressalva: o artigo **não usa mapa de calor**; dizer que "fundamentou o mapa de calor" é uma inspiração conceitual |

## Obras de método

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Chen e Guestrin (2016) | otimização de segunda ordem e regularização explícita | **Confere** (a aproximação de segunda ordem vem de Friedman, e o artigo diz isso; a regularização é melhoria deles) |
| Lundberg e Lee (2017) | única atribuição aditiva com propriedades desejáveis (consistência e importância nula para variável ausente) | **Confere** literalmente: solução única com precisão local, ausência (*missingness*) e consistência |
| Ribeiro et al. (2016) | modelo linear local na vizinhança; "sensível à escolha dessa vizinhança" | **Descrição confere. "Sensível" não está no artigo**: ele define a vizinhança por um núcleo exponencial de largura σ e só diz ser robusto a ruído de amostragem. A sensibilidade é crítica de trabalhos posteriores |
| Grinsztajn et al. (2022) | árvores competitivas frente a redes em amostras de porte médio (cerca de 10 mil exemplos, com indício de que a diferença diminui em amostras maiores) | **Confere, lido no texto completo (colado em 2026-11-02).** O artigo diz que as árvores "seguem no estado da arte" em dados médios (conjuntos de treino truncados em 10 mil), em 45 bases com mais de 3 mil exemplos, i.i.d. e não determinísticas. No Apêndice A.2.2, com treino de 50 mil, escreve que "na maioria dos casos aumentar o treino reduz a diferença" entre redes e árvores e deixa o estudo rigoroso para trabalho futuro (são só 4 bases de classificação). Os 39 mil do nosso trabalho ficam entre os dois regimes, e o empate do MLP é coerente com isso. O artigo explica a vantagem das árvores por três vieses (redes suavizam demais, sofrem com variáveis não informativas e não são invariantes a rotação); com cinco variáveis agregadas e todas informativas nos cortes tardios, esses efeitos pesam pouco |
| Niculescu-Mizil e Caruana (2005) | calibração, preocupação conhecida em *boosting* | **Confere**: *boosted trees* empurram as probabilidades para longe de 0 e 1 (distorção em S), corrigida por Platt ou isotônica. Nuance: eles tratam *boosting* de margem máxima; o XGBoost usa perda logística, que já otimiza probabilidade, e a nossa curva de calibração confirmou |
| Wang et al. (2020) | representar o esquema com as relações, e não só com os nomes das colunas, melhora a precisão | **Confere**: *relation-aware* com ligação ao esquema; exact match no Spider sobe a 57,2%, +8,7 pontos |
| Zhong, Yu e Klein (2020) | limites da acurácia de execução; vários bancos de teste | **Confere**: a avaliação em um banco só gera falsos positivos; propõem *test suites* destiladas |
| Brown, Cai e DasGupta (2001) | intervalo de Wilson para proporções | **Confere** (resumo; releitura em 2026-11-03, ver abaixo): recomendam Wilson ou Jeffreys para n pequeno e Agresti-Coull para n maior. Nossos n são de milhares, onde os três praticamente coincidem |
| Kaufman et al. (2012) | vazamento de dados | **Confere** (resumo): informação sobre o alvo que não deveria estar disponível |
| Holm (1979) | correção para comparações múltiplas | **Confere** |

## Leitura integral das obras de método (2026-11-03)

**Lidos linha a linha, do começo ao fim:** Hanley e McNeil (8 págs.),
Kohavi (7 págs.) e Hornik et al. (8 págs., incluindo o apêndice; releitura
completa em 2026-11-03). **Texto obtido, mas lido só nos trechos que o TCC
cita:** (nenhum no momento; Pedregosa foi relido por inteiro, ver abaixo).
Cópias locais em `docs/artigos/` (ignorada pelo Git).

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Hanley e McNeil (1982) | a AUC equivale à probabilidade de um caso positivo receber pontuação maior que um negativo (2.3) | **Confere literalmente** (p. 29, resumo; p. 31–32, relações A e B): a área é a probabilidade de um doente sorteado ser classificado com mais suspeita que um não doente sorteado, e é a mesma quantidade da estatística de Wilcoxon (Mann-Whitney). Nuance: empates contam 1/2. Útil à banca: o artigo avisa (p. 35) que os tamanhos de amostra valem para grupos independentes e que, em dados pareados, a análise pareada é mais potente, o que sustenta o *bootstrap* pareado do Apêndice C |
| Hornik et al. (1989) | MLP tem capacidade de aproximação universal (2.2) | **Confere** (introdução, p. 359): com unidades ocultas em número suficiente, aproxima qualquer função de interesse com a precisão desejada. Limites que o próprio artigo declara: não diz quantas unidades são necessárias, e atribui falhas em aplicações a aprendizado inadequado, número insuficiente de unidades ou **relação estocástica, e não determinística, entre entrada e alvo**. Este último ponto explica por que o MLP não passa do teto das cinco variáveis |
| Kohavi (1995) | validação cruzada estratificada, 5 dobras (4.4 e Apêndice C) | **Confere em parte.** O artigo recomenda **validação cruzada estratificada de 10 dobras** (resumo e seção 6) e mostra que a estratificação reduz viés e variância. Sobre 5 dobras, diz que há viés pessimista "especialmente com duas e cinco dobras" (a estratificação reduz esse pessimismo: em 5 dobras a acurácia estimada sobe 4,7 pontos em soybean e 1,9 em vehicle), em bases de 50 a 900 exemplos de treino. A variância quase não muda com o número de dobras (Corolário 2). **A citação ao lado de "5 dobras" no corpo sugere que o autor recomenda 5; ele recomenda 10.** O Apêndice C já mede a diferença (≤ 0,0008 em acurácia), e o viés pessimista do artigo vem de curvas de aprendizado inclinadas, o que não é o caso de 39 mil partidas (inferência nossa, rotulada como tal) |
| Kohavi (1995), referência | p. 1137-1145 | **Erro nas páginas.** O artigo termina na p. 1143 (7 págs.). Correto: p. 1137-1143 |
| Pedregosa et al. (2011) | `GridSearchCV`, do scikit-learn, otimizando a AUC-ROC (4.4) | **Confere** (seção 3): `GridSearchCV` envolve um estimador, escolhe os parâmetros numa grade por validação cruzada e maximiza um escore. A escolha da AUC-ROC como escore é nossa, não do artigo. Páginas 2825-2830 conferem |

**Aplicado em 2026-11-03 (com aprovação):** na 4.4, "validação foi cruzada e
estratificada (Kohavi, 1995), com 5 dobras", e as páginas da referência
corrigidas para 1137-1143. Total seguiu em 29 páginas; `verifica_tcc.py`
consistente e `confere_docx.py` conforme.

**Brown, Cai e DasGupta** (lido: resumo, introdução e o resumo das
recomendações, págs. 1 a 3 do relatório; as outras 20 páginas, com as
curvas de cobertura por *n* e as expansões de Edgeworth, **não foram lidas
linha a linha**). O PDF é o relatório técnico #99-19 de **agosto de 1999**,
não o artigo de 2001 da *Statistical Science* citado no TCC. **Confere**: o
intervalo usual (Wald) tem cobertura caótica mesmo com *n* grande (com
*n* = 100, cobertura .952 se *p* = .106 e .911 se *p* = .107), e os autores
recomendam Wilson ou Jeffreys para *n* ≤ 40. Nuance para a banca: **para
*n* > 40 dizem que Wilson, Jeffreys e Agresti-Coull são muito parecidos e
recomendam Agresti-Coull pela simplicidade**. Nossos *n* são de milhares, então
Wilson é uma escolha válida, mas o argumento sólido é "em vez do intervalo
usual", e não "Wilson é o melhor para esse tamanho".

## Livros de metodologia (2026-11-03)

Textos completos recebidos: Gil, *Como elaborar projetos de pesquisa* (cap.
4 e 5); Prodanov e Freitas (e-book da Feevale, cap. 3); Creswell e Creswell
(2023, cap. 1 e 10); Yin (2018, cap. 1). Li as definições que o TCC cita,
não os livros inteiros.

| Obra | Afirmação do TCC (4.1 e 4.2) | Resultado |
|---|---|---|
| Prodanov e Freitas (2013) | pesquisa aplicada "busca conhecimento voltado à solução de um problema específico e de uso prático" | **Confere** (seção 3.4.1): "objetiva gerar conhecimentos para aplicação prática dirigidos à solução de problemas específicos" |
| Prodanov e Freitas (2013) | pesquisa documental sobre a documentação da Riot Games API | **Confere** (p. 56): a documental usa materiais que ainda não receberam tratamento analítico ou que podem ser reelaborados conforme os objetivos; a bibliográfica usa contribuições de vários autores |
| Gil (2002) | pesquisa exploratória (Riot API e possibilidades de modelagem) e descritiva (dados, padrões e modelos) | **Confere** (seção 4.1, p. 42–43): a exploratória dá familiaridade com o problema e costuma assumir a forma de pesquisa bibliográfica ou estudo de caso; a descritiva descreve características de um fenômeno ou estabelece relações entre variáveis |
| Gil (2002) | pesquisa bibliográfica | **Confere** (seção 4.3, p. 44): baseada em material já elaborado, principalmente livros e artigos científicos |
| **Creswell e Creswell (2023)** | "abordagem mista: qualitativa na revisão bibliográfica e na interpretação dos achados, quantitativa na coleta, na análise exploratória e na comparação entre os modelos" | **Não confere com a definição do livro.** Cap. 1: pesquisa de métodos mistos é a abordagem que **coleta dados quantitativos e qualitativos**, combina (integra) os dois tipos de dado em um desenho específico e tira meta-inferências. O TCC não coleta dado qualitativo (sem entrevistas, questionários abertos ou documentos analisados como dado); revisão bibliográfica e interpretação dos achados não são coleta qualitativa. Pelo critério do autor, o trabalho é **quantitativo**, com revisão bibliográfica. Ressalva: o rótulo vem do TCC I e pode ter sido aceito pelo orientador |
| **Yin (2018)** | "estudo aplicado com recorte de caso no domínio de *League of Legends*" | **Confere só em parte.** Cap. 1: estudo de caso investiga um fenômeno contemporâneo em profundidade e em seu contexto real, quando a fronteira entre fenômeno e contexto é pouco nítida; a segunda parte da definição exige **muito mais variáveis do que pontos de dados**, proposições teóricas prévias e **múltiplas fontes de evidência que convergem** (triangulação). O trabalho tem o oposto (dezenas de milhares de partidas e cinco variáveis) e não parte de proposições teóricas. As duas fontes (solo queue e profissional) lembram a triangulação, mas são complementares, não convergentes. A formulação "recorte de caso" é cautelosa e se sustenta como "delimitado a um domínio", mas não como estudo de caso no sentido de Yin |

**Aplicado em 2026-11-03 (a pedido do autor): opções 1 e 2 abaixo.** 4.1
passou a "predominantemente quantitativa"; Resumo e *Abstract* trocaram
"mista"/"mixed-methods" por "quantitativa"/"quantitative"; a 4.2 perdeu a
citação de Yin, e a referência foi removida (32 → 31, `confere_docx.py`
atualizado). Corpo seguiu em 29 páginas, `verifica_tcc.py` consistente. Guia
e site atualizados. **Levar ao orientador na quarta**, porque "mista" vinha
do TCC I, que ele aprovou: a opção 3 é a resposta pronta se ele preferir
voltar ao rótulo anterior.

**Propostas originais (todas as três eram alternativas):**
1. 4.1: trocar "A abordagem é mista (Creswell; Creswell, 2023): qualitativa na revisão..." por uma formulação que o livro sustente, por exemplo "A abordagem é predominantemente quantitativa (Creswell; Creswell, 2023): a coleta, a análise exploratória e a comparação entre os modelos usam dados numéricos, e a revisão bibliográfica e a interpretação dos achados dão o contexto". Conversar com o orientador antes, porque o rótulo "mista" pode vir do TCC I.
2. 4.2: trocar "estudo aplicado com recorte de caso no domínio de *League of Legends* (Yin, 2018)" por "estudo aplicado, delimitado ao domínio de *League of Legends*", sem a citação de Yin, ou manter Yin e explicar na defesa que "recorte de caso" quer dizer só delimitação de domínio.
3. Se o orientador preferir manter "mista" e "caso", preparar a resposta: "a classificação segue o TCC I, aprovado; reconheço que, no sentido estrito de Creswell e de Yin, o trabalho é quantitativo e não é um estudo de caso".

## Mais leituras (2026-11-03, tarde)

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Breiman (2001), texto obtido (33 págs. na cópia de Berkeley); **lidos só o resumo, a seção 1, a 2.1 a 2.2 e a 4, por busca de termos, não o artigo inteiro** | *Random Forest* combina *bagging* com seleção aleatória de variáveis em cada nó; reduz a variância do conjunto (2.2) | **Confere, com nuance de enquadramento.** Definição 1.1: coleção de árvores `h(x, Θk)` com vetores aleatórios i.i.d.; o *bagging* é um dos exemplos de `Θ`. A seção 4 descreve a seleção aleatória de variáveis por nó (Forest-RI), com árvores crescidas sem poda. O artigo não fala em "reduzir a variância": diz que o erro de generalização depende da **força das árvores e da correlação entre elas** (Teorema 2.3: PE* ≤ ρ(1−s²)/s²), e que a seleção aleatória reduz a correlação. "Faz as árvores divergirem" (nosso texto) equivale a menor correlação. Também diz (Teor. 1.2) que a floresta **não sobreajusta ao acrescentar árvores**, e que o erro converge |
| Grinsztajn et al. (2022), seção 3.1, conferida no texto completo | árvores competitivas em amostras de porte médio | **Confere**, e traz um critério novo para a defesa: bases em que a regressão logística fica a menos de 5% do ResNet e do HistGradientBoosting são removidas por serem "fáceis demais", e séries temporais e alvos determinísticos também. Nossa logística (AUC 0,8483 contra 0,8473) cairia nesse critério. Isso **não invalida a citação** (ela diz só "porte médio" e "indício"), mas a banca pode perguntar por que o empate acontece: a base não discrimina famílias de modelo |
| Brown, Cai e DasGupta, págs. 8 e 12 do relatório | intervalo de Wilson | **Confere.** Pág. 8: as regras de bolso dos manuais (np ≥ 5 ou 10) são insuficientes; com n = 40 e p = 0,5 a cobertura real do intervalo usual é 0,919 para um nível nominal de 0,95. Pág. 12: o intervalo de Agresti-Coull (Wilson ajustado) é descrito. Págs. 4 a 7, 10, 11 e 13 a 23 (curvas de cobertura, Edgeworth, tabelas) **não foram lidas** |

## Leitura linear dos estudos de domínio (2026-11-03)

Cada artigo abaixo foi lido **do início ao fim** (texto extraído do PDF, sem
busca por termos) e comparado com a frase da Seção 3 que o cita.

### Bloco A: Do, Jadowski e Cunningham, Bahrololloomi

| Obra | Afirmação do TCC (3.2) | Resultado |
|---|---|---|
| Do et al. (2021) | preveem partidas ranqueadas antes de elas começarem, a partir da experiência de cada jogador com o campeão, e chegam a 75,1% com uma rede neural profunda | **Confere inteiro.** Detalhes úteis à defesa: 5.000 partidas ranqueadas da NA em 2020, **de Ferro a Diamante**; o artigo diz que não reflete o 1% do topo, e a nossa base é Challenger/Grandmaster, então as populações não se sobrepõem. O predito vale **depois da escolha de campeões** (pré-jogo, não pré-draft). Validação cruzada de 10 dobras. O *gradient boosting* teve 75,4%, acima da rede (75,1%), mas desvio-padrão muito maior (5,25% contra 1,9%), e foi por isso que escolheram a rede. Também citam como referência de preditores em jogo: Lee et al. 73% aos 15 min (Random Forest) e Silva et al. 83,54% aos 25 min (rede recorrente), comparáveis aos nossos 76% (acurácia) aos 15 e 82% aos 25 |
| Jadowski e Cunningham (2022) | ajustam classificadores estatísticos a métricas das ligas profissionais de 2020 e acertam 67% dos 306 jogos da etapa seguinte | **Confere.** Treino: 882 jogos do *Spring Split* 2020; teste: 306 do *Summer Split*; 7 ligas (a chinesa fica de fora por falta de dados). Os "classificadores" são regressão logística e a fórmula Log5, sobre médias por jogo de equipes e jogadores; o melhor (avaliação por jogador) acerta 67,3% (AUC 0,666). **Dado extra:** os dados vêm do Oracle's Elixir, como os nossos, e o lado azul vence 54,08% dos 882 jogos (qui-quadrado, p = 0,015), compatível com os nossos 53,2% do profissional |
| Bahrololloomi et al. (2022) | predizem a vitória a partir das funções (*roles*) e das métricas individuais dos jogadores | **Confere em parte.** Predizem a partir da pontuação individual (percentil de XP por minuto dentro de cada função e posição), somada por time, mas **concluem que o peso de cada função é desprezível** (pesos entre 0,1995 e 0,2006, diferença de 0,1%) e que a função "pode ser omitida". Dizer que predizem "a partir das funções" inverte o achado. Os 86% vêm de contar em quantas partidas o time vencedor tinha a maior soma de pontuação, sobre as mesmas 2.901 partidas em que os pesos foram calculados, **sem conjunto de teste separado**, e a descrição de que pontuações vêm dos "últimos jogos" de cada jogador é ambígua. Os 92,7% são 100 − MAPE em regressão de XP por minuto, não classificação |

**Proposta, aguardando aprovação (3.2):** trocar "predizem a vitória a partir
das funções (*roles*) e das métricas individuais dos jogadores" por "predizem
a vitória a partir das métricas individuais dos jogadores e concluem que o
peso de cada função (*role*) é desprezível". Mesmo tamanho; não muda o total
de páginas.

### Bloco B: Maymin, Guan e Tung, Hodge et al.

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Maymin (2021) | calibra um modelo de probabilidade de vitória com dados de milhões de partidas ranqueadas e avalia cada ação individual pelo efeito que tem nessa probabilidade (3.2) | **Confere em parte.** O modelo de vitória em jogo é uma regressão logística sobre minuto, abates, torres e monstros grandes de cada lado, treinada com **um minuto sorteado por partida** em milhões de partidas. Só **abates e mortes** são classificados pelo efeito na probabilidade ("abates inteligentes" e "mortes inúteis"); as dezenas de outras métricas não são. "Cada ação individual" exagera. **Contraste útil:** Maymin **exclui o ouro** do modelo ("fundamentalmente falho", pág. 16) e diz que acrescentar variáveis não melhorou o modelo; o nosso modelo usa a diferença de ouro como variável principal. A análise individual usa ~150 mil partidas do último *patch*, metade de Bronze e menos de 1% de Mestre/Desafiante |
| Guan e Tung (2026) | previsão pré-jogo no cenário profissional, com o lado do mapa e a prioridade de escolha como covariáveis; *preprint* sem revisão por pares (3.2) | **Confere.** *Preprint* do arXiv (stat.AP, set. 2026). 5.135 jogos de seis ligas e três eventos internacionais, 2024–2026. Modelo: regressão logística com forma recente por lado (azul/vermelho), força estável do time e covariável de primeira escolha. **Achado útil à defesa:** o modelo simples **empata estatisticamente** com um modelo misto de dois estágios, construído como o rival mais forte possível, e acrescentar variáveis ao modelo piora o resultado de forma monótona (RPS 0,2230 → 0,2242 → 0,2258). Conclusão deles: a escolha se faz por parcimônia, não por acurácia, o mesmo padrão do nosso baseline logístico. Também declaram uso de LLM (Claude) na escrita do código e do texto. Eles afirmam que a validação cruzada aleatória é inválida **para os modelos deles**, porque as variáveis dependem de jogos anteriores do time; as nossas dependem só da própria partida no corte, então o argumento não se transfere |
| Hodge et al. (2021) | Dota 2 profissional, em tempo real; até 85% após 5 min, em 28 partidas de um torneio; modelos padrão, engenharia de atributos e otimização (3.1) | **Confere inteiro** (resumo e seção VI-A: ESL One Hamburg 2017, N = 28, "a acurácia varia entre 70% e 90%" por causa da amostra pequena). **Número mais robusto para citar na defesa:** na avaliação *offline* com 186 partidas profissionais (The International 2017) no minuto 20, a acurácia fica entre **70,81% e 74,59%**. Em partidas mistas, regressão logística, Random Forest e LightGBM ficam entre 77,24% e 77,51%, o mesmo "empate" que medimos. O artigo diz que as redes neurais "não foram convincentes" com esse tamanho de base. Usam divisão cronológica; nós usamos validação cruzada estratificada, porque cada partida é independente. A base mistura 24% de partidas profissionais com partidas de elo muito alto (> 5.000 MMR, top 4%) |

**Proposta, aguardando aprovação (3.2):** trocar "e avalia cada ação
individual pelo efeito que tem nessa probabilidade" por "e avalia abates e
mortes pelo efeito que têm nessa probabilidade". Tamanho parecido; não muda o
total de páginas.

### Bloco C: Birant e Birant, García-Méndez e Arriba-Pérez

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Birant e Birant (2023) | abordagem multi-objetivo e multi-instância; modelagem centrada no time em vez do jogador isolado; "é a abordagem adotada aqui, com as variáveis preditoras construídas como diferenças agregadas entre os dois times" (3.2) | **Confere na descrição; "é a abordagem adotada aqui" é forte demais.** O artigo agrupa os cinco vetores de jogadores de cada time em um "saco" (*bag*) e usa algoritmos de múltiplas instâncias; nós usamos uma diferença agregada entre os times e modelos comuns. O que compartilhamos é a **orientação centrada no time**, não a técnica. **Contexto dos "até 95%":** usam estatísticas de **fim de partida** (abates, ouro, dano, recompensas de cada jogador), em base do Kaggle (NA e EUW, temporadas 3 a 7) com validação cruzada de 10 dobras; o próprio artigo diz "consideramos variáveis pós-jogo". Não é previsão em jogo. A Tabela 3 compara o F-measure deles com estudos de **recomendação de itens**, e a acurácia com uma dissertação de KNN (58%), que não são o mesmo problema. O TCC não cita o 95% (correto) |
| García-Méndez e Arriba-Pérez (2025) | classificação com mecanismos de interpretação em partidas profissionais de *Counter-Strike*, em *streaming*; apontam a falta de interpretabilidade como uma das principais limitações dos trabalhos anteriores (3.3) | **Confere.** Base do Kaggle (HLTV), 45.079 jogos profissionais de CS:GO; random forest adaptativo é o melhor, com 92,51% de acurácia (88,87% na validação aninhada por segmentos). **Qualificador omitido:** o artigo diz que a falta de interpretabilidade limita os trabalhos "de predição **pré-partida**, que não conseguem usar fluxos de dados ao vivo". **Contexto dos 92,51%:** o cenário B soma o histórico de cada jogador (240 variáveis pré-jogo) e o placar da primeira metade da partida; só com variáveis do time e do placar (cenário A) a acurácia é de ~75%. A explicabilidade deles é a frequência de variáveis no caminho das árvores mais descrição em linguagem natural (não SHAP). Excluem redes neurais por não serem interpretáveis nem atualizáveis em fluxo |

**Propostas, aguardando aprovação:**
1. 3.2: "É a abordagem adotada aqui" por "É a orientação adotada aqui" (a técnica
   de múltiplas instâncias não foi usada). Mesmo tamanho.
2. 3.3 (opcional): sem mudança. O qualificador "pré-partida" é de contexto dos autores e a frase do TCC resume o argumento sem distorcê-lo.

### Bloco D (parcial): Guo et al.

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Guo et al. (2024), Talk2Data | interface em linguagem natural para análise visual exploratória baseada em decomposição de perguntas; "os dois usam modelos de linguagem como camada de interação sobre dados estruturados e fundamentam o *text-to-SQL* deste trabalho" (3.4) | **Confere na descrição; "fundamentam o *text-to-SQL*" é forte.** Lido inteiro, exceto a lista de referências. O Talk2Data **não gera SQL**: decompõe a pergunta em duas subperguntas com um modelo *seq2seq* (codificador e decodificador GRU, com atenção e mecanismo de cópia, mais um classificador BERT do tipo de pergunta) e busca "fatos de dados" por busca em feixe, apresentados em gráficos anotados. Não é um LLM generativo. Treino: 7.096 perguntas complexas sobre 26 tabelas (a maioria de marketing). Avaliação: BLEU 26,22 e METEOR 27,55 da decomposição; estudo com 20 estudantes de design e letras, com 87,6% de acerto em perguntas complexas contra 67,5% do *baseline* (NL4DV). **Limitação declarada que contrasta com o nosso trabalho:** o protótipo "ainda não lida com tabelas de dezenas de milhares de registros", e o nosso consulta dezenas de milhares de partidas via SQL. O PDF é o *preprint* do arXiv (v3, 2023), com cabeçalho de periódico provisório; o ano 2024 do TCC não pôde ser conferido neste arquivo |

**Proposta, aguardando aprovação (3.4):** trocar "fundamentam o *text-to-SQL*
deste trabalho" por "motivam o *text-to-SQL* deste trabalho", pelo mesmo critério
da 2.5 ("fundamentou" virou "motivou"): são inspiração de interface, não base
do método de conversão. Mesmo tamanho.

### Bloco D (cont.): Wallner et al.

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Wallner, Wang e Dormann (2023) | estudam a evolução espaço-temporal do *gameplay* em *League of Legends* com *storyline visualization* e "mostram o valor de integrar tempo e localização em uma única representação para a interpretação pós-jogo"; é "a referência do posicionamento minuto a minuto" (3.5) | **Confere, com ressalva de intensidade.** Lido do início à conclusão (as referências, só o começo). Adaptam a técnica *storyline* (framework iStoryline) a partidas de LoL com dados da API da Riot e a avaliam com **39 jogadores** em estudo *online* por tarefas. Conclusão do artigo: o método "é promissor" e "pode ser adequado", e os participantes reagiram bem. Mas as perguntas sobre **tempo foram as mais difíceis e menos eficientes**, e legibilidade e estética tiveram as notas mais baixas (linhas sobrepostas). "Mostram o valor" é um pouco mais forte que "mostram que é adequado e bem recebido". A API só registra posições **a cada 1 minuto**, o que o artigo declara como limitação: é a mesma restrição do nosso mapa de calor. Amostra: 76 respostas completas, 8 excluídas por rapidez e 28 por suspeita de duplicidade, ficando 39 (35 homens); coleta por Reddit e Discord. Não há mapa de calor no artigo (a revisão cita VisuaLeague e MOBA Coach, que usam mapas) |

**Proposta, opcional (3.5):** trocar "mostram o valor de integrar tempo e
localização em uma única representação" por "mostram que integrar tempo e
localização em uma única representação é viável e bem recebido pelos
jogadores". Tamanho parecido; não muda o total de páginas.

### Bloco D (fim): Jiang et al. (SiriusBI)

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Jiang et al. (2025), SiriusBI | solução de *Business Intelligence* apoiada por modelos de linguagem para análise de dados em contextos corporativos (3.4); soluções com diálogo em várias rodadas favorecem a exploração de dados estruturados (2.4) | **Confere.** Lido da página de rosto até a seção 4.5 (a conclusão e as referências não foram lidas). PVLDB 18(12), 2025, equipe da Tencent e Universidade de Pequim. Quatro módulos: gestão de conhecimento, diálogo em várias rodadas com perguntas de esclarecimento, geração de SQL (em um passo, com ajuste fino, ou em dois, com representação intermediária semântica) e *insights* de dados. **Números do guia conferidos:** em produção 97% (finanças), 93% (publicidade) e 96% (nuvem, média de 14 clientes); na base industrial própria de 182 consultas, 79,19% (dois passos) e 83,24% (um passo); no BIRD, 65,32% e 68,97%; no diálogo em várias rodadas (MRD-Industry), 55,00% e 62,50%. **Ressalvas para comparar com o nosso 88%:** a métrica deles é a UEX (*Useful Execution Accuracy*), que aceita a consulta se a intenção coincide com a de referência, mais branda que a nossa comparação do resultado; os próprios autores atribuem os números de produção a perguntas mais simples e uniformes, base de conhecimento completa e ciclos de correção; os autores avaliam o sistema da própria empresa. Estudo de uso: 40 analistas (20 com o sistema, 20 sem), 30,2% menos tempo por tarefa e nota SUS de 84,2 |

**Proposta, aguardando aprovação (3.4):** a mesma da Guo, "fundamentam" por
"motivam" o *text-to-SQL*. O SiriusBI gera SQL com LLM e é, de fato, a obra
mais próxima do nosso método; ainda assim, o nosso gera uma única consulta
com validação em quatro camadas, sem diálogo em várias rodadas nem ajuste fino.

### Resumo da leitura linear dos estudos de domínio

Todos os 11 foram lidos do início ao fim, com estas exceções declaradas:
as listas de referências de Guo e Wallner, o fim do SiriusBI (conclusão) e o
fim do Apêndice B do Guan e Tung. **Nenhum erro de fato foi encontrado.**
Cinco imprecisões de intensidade ou enquadramento, todas com proposta curta
(3.2: Bahrololloomi, Maymin e Birant; 3.4: Guo e SiriusBI; 3.5: Wallner,
opcional). Nenhuma muda o total de páginas.

## Leitura linear das obras de método (2026-11-03, noite)

Lidos **do início ao fim**: Lundberg e Lee, Niculescu-Mizil e Caruana, Holm,
Wang et al. (RAT-SQL) e Zhong et al.

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Lundberg e Lee (2017) | o SHAP recorre ao valor de Shapley; "única atribuição aditiva com propriedades desejáveis, como a consistência e a importância nula para uma variável ausente"; "as contribuições somam a previsão" (2.3) | **Confere literalmente.** Teorema 1: só uma explicação aditiva satisfaz as propriedades 1 a 3 (precisão local, ausência/*missingness* e consistência). "As contribuições somam a previsão" é a precisão local. **Duas observações.** (1) Este artigo **não traz o algoritmo para árvores**: descreve Kernel SHAP, Deep SHAP, Linear SHAP, Max SHAP e a amostragem de Shapley. O código usa `shap.TreeExplainer` (`explain_shap.py`, `main.py`, `export_model.py`), que vem de Lundberg et al. (2020, *Nature Machine Intelligence*), **não citado no TCC**. (2) O artigo avisa que as aproximações simples assumem **independência entre variáveis** (equação 11); as nossas (ouro, abates, torres) são correlacionadas. O *TreeExplainer* trata isso pela estrutura das árvores, mas a defesa deve saber dizer isso |
| Lundberg e Lee (2017), sobre o LIME | o LIME é "dependente de como essa vizinhança é definida" (2.3), já marcado como não literal em Ribeiro et al. | **O Lundberg sustenta uma crítica melhor e literal:** o LIME escolhe de forma **heurística** a perda, o núcleo de ponderação e a regularização, e "com essas escolhas a equação 2 não recupera os valores de Shapley", o que **viola a precisão local e/ou a consistência** (seção 4.1) |
| Niculescu-Mizil e Caruana (2005) | a calibração é uma preocupação conhecida em modelos de *boosting*; o XGBoost já saiu bem calibrado (5.4) | **Confere.** Árvores com *boosting* empurram as probabilidades para longe de 0 e 1 (distorção em S); Platt e isotônica corrigem. Dados novos: **regressão logística e redes neurais já saem bem calibradas**, e *random forests* nem sempre. Sem calibração independente (o conjunto de calibração precisa ser separado do treino) há viés. Nuance de sempre: o "boosting" do artigo é de margem máxima, e o XGBoost usa perda logística |
| Holm (1979) | correção de Holm "corrige a multiplicidade quando várias diferenças são testadas na mesma base" (4.5 e 5.3) | **Confere.** Procedimento sequencial: ordena os valores-p e compara com α/n, α/(n−1), ... até não rejeitar mais; garante o nível de significância múltiplo para qualquer combinação de hipóteses verdadeiras (por Boole) e é mais potente que a Bonferroni clássica. O "valor-p corrigido" que o TCC cita é a forma equivalente usual, que o artigo não apresenta |
| Wang et al. (2020), RAT-SQL | "representar o esquema com os relacionamentos entre tabelas, além dos nomes das colunas, melhora a precisão da conversão" (2.4) | **Confere.** Atenção sensível a relações codifica chaves estrangeiras, primárias e ligação entre a pergunta e as colunas. Acurácia de correspondência exata no Spider: 57,2% (+8,7), e 65,6% com BERT; sem as relações do esquema, 35,59% contra 55,13% (ablação, p < 0,001). **Nuances:** a métrica é correspondência **exata** (18% dos "erros" são consultas equivalentes, que a acurácia de execução aceitaria); e a ligação ambígua de colunas continua sendo a causa principal dos erros (39% no SELECT) |
| Zhong, Yu e Klein (2020) | discutem os limites da acurácia de execução e propõem avaliar a consulta sobre vários bancos de teste; o nosso *benchmark*, sobre uma base, não faz (4.7) | **Confere.** Avaliar sobre **um** banco ("denotação única") gera falsos positivos: 6,5% em média nas 21 submissões do Spider (até 9,0%, Tabela 2); a correspondência exata gera falsos negativos de 2,6% em média. Propõem *test suites* destilados de bancos aleatórios. **Consequência para a defesa:** os nossos 88% (23/26) são um **teto** da acurácia semântica, não uma medida exata. Observação: o texto do artigo diz "8%" no pior caso e a Tabela 2 diz 9,0% |

**Propostas, aguardando aprovação:**
1. 2.3, sobre o LIME: trocar "mas dependente de como essa vizinhança é
   definida" por "mas escolhe de forma heurística a perda e o núcleo de
   ponderação, o que pode violar a precisão local e a consistência (Lundberg;
   Lee, 2017)". Corrige a ressalva antiga do Ribeiro com apoio literal. Soma
   uma citação já existente na lista; mesmo tamanho aproximado.
2. 4.4 (opcional, custa uma referência e ~3 linhas, e o corpo tem ~1 linha de
   folga, então só com corte equivalente): citar Lundberg et al. (2020) para
   o *TreeExplainer*. Alternativa sem custo: deixar a resposta pronta no guia.

### Leitura linear (cont.): Chen e Guestrin, Ribeiro et al.

| Obra | Afirmação do TCC | Resultado |
|---|---|---|
| Chen e Guestrin (2016) | XGBoost "constrói as árvores em sequência, cada uma ajustada ao resíduo das anteriores, com otimização de segunda ordem e regularização explícita" (2.2) | **Confere.** Lido inteiro, exceto a prova do esboço de quantis ponderados (apêndice). Treino aditivo: cada árvore nova minimiza o objetivo regularizado com **aproximação de segunda ordem** (gradiente e hessiana da perda); a regularização é Ω = γT + ½λ‖w‖². Nuances de intensidade: o artigo diz que a segunda ordem **vem de Friedman et al. (2000)** e que a regularização é uma "melhoria menor"; as contribuições principais são de **sistema** (algoritmo ciente de esparsidade, esboço de quantis ponderados, bloco em colunas com acesso ciente de cache, execução fora da memória). Também descreve *shrinkage* (nosso `learning_rate` 0,01) e subamostragem de colunas. As árvores são ajustadas à estatística de gradiente `g/h` ponderada por `h`, que equivale ao resíduo no caso da perda quadrática. Configuração deles: profundidade 8 e *shrinkage* 0,1; a nossa de produção é profundidade 3 e 0,01 |
| Ribeiro, Singh e Guestrin (2016) | o LIME "aproxima o modelo por um modelo linear local na vizinhança de cada predição, simples de ler, mas dependente de como essa vizinhança é definida" (2.3) | **Descrição confere; a ressalva literal é outra.** Lido inteiro, exceto as referências. Modelo linear esparso ponderado por um núcleo exponencial de proximidade; o artigo diz que o método é "razoavelmente robusto ao ruído de amostragem". **A limitação que o próprio artigo declara (seção 3.4):** se o modelo for "altamente não linear mesmo na vizinhança da predição, pode não haver uma explicação fiel" por um modelo linear. **Dado útil à defesa:** o artigo usa o conceito de vazamento de dados de Kaufman et al. e mostra que explicações ajudam a **detectar** vazamento (exemplo do identificador do paciente), o que sustenta ler o SHAP também como verificação de que nenhuma variável suspeita domina o modelo |

**Proposta 1 (2.3, LIME) revisada:** trocar "mas dependente de como essa
vizinhança é definida" por "mas pode ser pouco fiel quando o modelo é muito
não linear na vizinhança da predição, e escolhe de forma heurística o núcleo
de ponderação (Ribeiro; Singh; Guestrin, 2016; Lundberg; Lee, 2017)". As duas
partes têm apoio literal nos dois artigos; o tamanho cresce meia linha.

### Pedregosa et al. (2011), leitura integral

**Confere** o que o TCC diz (4.4: `GridSearchCV`, do scikit-learn). O artigo
tem 6 páginas (2825-2830, conferem) e o escopo declarado é "problemas
supervisionados e não supervisionados de **escala média**". Descreve a
interface de estimadores, os iteradores de validação cruzada (K-fold,
*leave-one-out*, estratificada) e o `GridSearchCV`, que "seleciona os
parâmetros numa grade especificada, maximizando um escore". **Não menciona
Random Forest nem MLP.** O guia dizia que o artigo era a "origem do MLP/Random
Forest"; **corrigido em 2026-11-03** (RF vem de Breiman e MLP de Hornik et al.).
O TCC não tinha esse erro.

## Ajustes aplicados em 2026-11-03 (noite), com aprovação

Seis correções de intensidade, todas no corpo, **textos finais**:

| Onde | Texto final |
|---|---|
| 2.3, LIME | "...simples de ler, mas pouco fiel se o modelo for muito não linear na vizinhança." (limitação declarada por Ribeiro et al., seção 3.4) |
| 3.2, Birant | "É a orientação adotada aqui" |
| 3.2, Bahrololloomi | "predizem a vitória a partir das métricas individuais dos jogadores e concluem que o peso de cada função é desprezível. Aqui, esse nível só aparece nos perfis de jogador." |
| 3.2, Maymin | "avalia abates e mortes pelo efeito que têm nessa probabilidade" |
| 3.4, Guo e SiriusBI | "...e motivam o *text-to-SQL* deste trabalho" |
| 3.5, Wallner | "mostram que integrar tempo e localização numa só vista é viável para a interpretação pós-jogo" |

**Lição de layout:** a primeira versão, com o texto mais longo (+~110 caracteres
no total), subiu o corpo de 29 para **30 páginas** (última página 45% cheia),
porque um quadro ou figura mudou de página e abriu um vão. Cada edição foi
reduzida até o tamanho líquido ficar perto de zero, e o corpo voltou a 29. Em
edições futuras no corpo, **conferir a contagem de páginas a cada mudança**.
Não foram aplicadas as duas propostas opcionais: citar Lundberg et al. (2020)
(*TreeExplainer*) e a versão da LIME com "Lundberg; Lee, 2017", que custava
linhas.

### Breiman (2001), leitura linear completa

Lido do resumo à seção 13 (excluídos: referências e provas dos apêndices).

| Afirmação do TCC (2.2) | Resultado |
|---|---|
| "*Random Forest* (Breiman, 2001), que combina *bagging*, em que cada árvore treina sobre uma amostra *bootstrap*, com a seleção aleatória de variáveis em cada nó" | **Confere** (seção 3.1: "o *bagging* é usado em conjunto com a seleção aleatória de variáveis; cada árvore cresce sobre amostra com reposição, sem poda") |
| "Isso faz as árvores divergirem entre si e **reduz a variância do conjunto**, o que importa quando as variáveis preditoras são correlacionadas, como ouro, abates e torres" | **Não está no artigo como escrito.** Breiman explica por outro caminho: o erro de generalização é limitado por ρ(1−s²)/s² (Teorema 2.3), onde ρ é a **correlação entre as árvores** e s a **força** de cada uma; a seleção aleatória **reduz ρ sem perder s**. Ele não fala em "variância do conjunto" e conclui na seção 13 que as florestas "parecem **reduzir o viés**" e que "o mecanismo não é óbvio". Quanto às variáveis correlacionadas, a seção 10 mostra o contrário do que a frase sugere: se duas variáveis são idênticas, cada uma recebe a mesma importância, e a segunda não reduz o erro depois que a primeira entra (importância se divide). O trecho "o que importa quando as variáveis são correlacionadas" é **inferência do autor do TCC**, sem apoio em Breiman |
| (guia) "não sobreajusta ao acrescentar árvores" | **Confere** (Teorema 1.2, pela Lei dos Grandes Números; o erro converge a um limite) |

Contexto útil: Breiman compara com o Adaboost (*boosting*) e acha as florestas
**competitivas**, mais robustas a ruído nos rótulos (aumento de erro com 5% de
ruído: 1,8% a 11% contra 15% a 49% do Adaboost em vários conjuntos), e usa 100
árvores; os conjuntos têm até 15.000 exemplos. O empate Random Forest e
XGBoost que medimos é coerente com isso.

**Proposta, aguardando aprovação (2.2), de tamanho líquido ~zero:** trocar "Isso
faz as árvores divergirem entre si e reduz a variância do conjunto, o que
importa quando as variáveis preditoras são correlacionadas, como ouro, abates
e torres, que evoluem juntos ao longo da partida." por "Isso reduz a
correlação entre as árvores, o que limita o ganho de um *ensemble*, e as
variáveis preditoras, como ouro, abates e torres, evoluem juntas ao longo da
partida." Mantém o fato e tira a causalidade que o artigo não afirma.

### Brown, Cai e DasGupta, leitura quase completa (relatório técnico #99-19, 1999)

Lidas como imagem as págs. 1 a 20 do relatório (resumo, introdução, seção 2,
seção 3 inteira, seção 4, conclusões e começo das referências). **Não vistas:**
uma página de transição da seção 2 e as duas últimas (Tabela 5 dos limites de
Jeffreys e o fim das referências). O PDF é a versão de **1999**; o TCC cita a
de 2001 (*Statistical Science*), e a conferência de fato do artigo publicado
exigiria o PDF de 2001.

| Afirmação do TCC (4.5) | Resultado |
|---|---|
| intervalo de Wilson sobre a proporção, "para a significância em amostras menores" | **Confere.** O Wilson (seção 3.2) inverte o teste normal usando o erro-padrão sob a hipótese nula, em vez do estimado; tem "apelo teórico". Cobertura média "muito próxima do nível nominal" (Figura 7); para 1/n ≤ p ≤ 1−1/n a cobertura limite fica entre 0,92 e 0,98 (seção 3.10). As falhas ficam em *p* muito perto de 0 ou 1, que não é o nosso caso (taxas perto de 50%) |
| (guia) "o intervalo usual é instável" | **Confere**, com exemplos concretos do artigo: para *p* = 0,5, a cobertura do intervalo de 95% é 0,951 com *n* = 17 e 0,904 com *n* = 18, e 0,919 com *n* = 40; para *p* = 0,005 cai a 0,792 com *n* = 592 |
| (nuance já registrada) | **Recomendação do artigo (seção 4):** Wilson ou Jeffreys para *n* ≤ 40; para *n* ≥ 40, **Agresti-Coull**, "o mais simples de apresentar", porque os três são comparáveis. O artigo diz que o intervalo usual "não deveria ser usado de forma alguma". O Wilson tem comprimento médio quase mínimo entre os intervalos com cobertura aproximadamente 1−α |

**Conclusão:** nenhuma correção necessária no TCC. A resposta de defesa segue
a do guia: "o Wilson substitui o intervalo usual, que o artigo condena; nos
nossos *n* (milhares), os três recomendados praticamente coincidem".

### Grinsztajn, Oyallon e Varoquaux (2022), leitura linear do texto disponível

Lido do resumo ao Apêndice A.2.2 (até a Figura 9), incluindo a lista de
bases. **Não lido:** o resto do apêndice (resultados por base, A.3 em diante),
que o texto colado não trouxe. **Versão:** é o *preprint* **v1 do arXiv** (18
jul. 2022, "em revisão"), cujo título é "...outperform deep learning on
tabular data?". A referência do TCC usa o título publicado no NeurIPS 2022
("...on **typical** tabular data?"). As afirmações abaixo foram conferidas na
v1; a versão publicada pode ter ajustes.

| Afirmação do TCC (2.2) | Resultado |
|---|---|
| "em dados tabulares, os métodos baseados em árvores seguem competitivos frente a redes neurais em amostras de porte médio, de cerca de 10 mil exemplos, com indício de que a diferença diminui em amostras maiores" | **Confere**, e o artigo é mais forte que "competitivos": diz que as árvores "seguem **no estado da arte**" em dados médios (treino truncado em 10 mil), em 45 bases, mesmo sem contar a velocidade, e que a vantagem se mantém para qualquer orçamento de busca de hiperparâmetros. A diminuição da diferença com mais dados vem do Apêndice A.2.2 (treino de 50 mil, só bases com mais de 50 mil exemplos): "parece que, na maioria dos casos, aumentar o treino reduz a diferença", deixando "um estudo rigoroso para trabalho futuro". É **indício**, como o TCC diz |
| (implícita) as bases deles são comparáveis à nossa | **Parcialmente.** Critérios de seleção: colunas heterogêneas, dados i.i.d. (sem séries temporais), **não determinísticos** (excluem xadrez e pôquer), mais de 3.000 exemplos e mais de 4 variáveis, e **"fáceis demais" removidas** (logística a menos de 5% do ResNet e do *boosting*). Eles também **balanceiam as classes** e removem dados ausentes. A nossa base tem 39 mil partidas, 5 variáveis e é i.i.d. por partida, mas não seria incluída por causa da logística |
| (o TCC não cita, o guia sim) por que as árvores ganham | Três vieses (seções 5.2 a 5.4): redes tendem a soluções **suaves demais**, são menos robustas a **variáveis não informativas** e são **invariantes a rotação**, o que mistura variáveis que têm significado próprio. Com cinco variáveis todas informativas, o segundo e o terceiro efeitos devem pesar pouco, o que é coerente com o empate do MLP (**inferência nossa**, não do artigo) |

**Conclusão:** nenhuma correção no TCC. Pendência opcional: conferir o artigo
publicado, se alguém na banca citar a v2 ou a versão do NeurIPS.

### Kaufman et al., leitura integral da versão de conferência (KDD 2011, 8 págs.)

Cópia aberta (UMass Boston) da versão de **conferência** (KDD'11, p. 556-563,
sem Stitelman). O TCC cita a versão de **periódico** (TKDD v. 6, n. 4, art. 15,
2012, com Stitelman), que é a expansão desta; a versão de 2012 foi lida inteira depois (ver a próxima seção). A definição e a metodologia são as mesmas nas duas.

| Afirmação do TCC (4.4) | Resultado |
|---|---|
| "nenhuma informação posterior ao corte entra como variável, o que evita o vazamento de dados descrito por Kaufman et al. (2012)" | **Confere e é uma aplicação direta.** Definição (resumo e seção 1): vazamento é "a introdução de informação sobre o alvo que não deveria estar legitimamente disponível". A condição central é o *no-time-machine requirement* (seção 3.2, eq. 3): só são legítimas as variáveis com informação de um momento **anterior ou igual** ao do alvo. A nossa regra (`frames[: corte + 1]`) é exatamente isso. A metodologia de prevenção (seção 4) é a **separação aprendizado-previsão** com marcas de legitimidade (aqui, o tempo do quadro) |
| (defesa) como detectar vazamento | Seção 5: análise exploratória, **desempenho surpreendente** comparado com a literatura ("uma divergência substancial do esperado merece teste"), e exame do modelo ajustado. Os nossos AUC (0,77 a 0,91) e a acurácia de 76% aos 15 min ficam na faixa da literatura (Lee et al.: 73% aos 15 min) |

**Duas ressalvas honestas que a banca pode explorar (seções 3.3 e 3.4):**
1. **Vazamento em exemplos de treino.** Quando há não estacionariedade
   (*concept drift*) e os exemplos não são independentes, treinar com dados de
   um período para prever outro pode vazar. Nossas partidas cobrem vários
   *patches* e os mesmos jogadores aparecem várias vezes, e a validação
   cruzada é aleatória, não temporal. O teste de **treino no passado e teste
   no futuro** (pendência opcional já registrada) responderia isso.
2. **Vazamento por decisão de projeto.** O artigo cita a escolha de
   hiperparâmetros e de modelo em dados de avaliação. A nossa busca em grade
   usa as mesmas dobras de avaliação, sem validação aninhada (já documentado:
   a configuração de produção ficou a 0,0001 da melhor).

**Conclusão:** nenhuma correção no TCC. Resposta pronta para a defesa no guia.

### Kaufman et al. (2012), artigo de periódico, leitura integral (15:1 a 15:21)

PDF recebido em 2026-11-03: *ACM TKDD*, v. 6, n. 4, art. 15, dez. 2012, com os
quatro autores (Kaufman, Rosset, Perlich e Stitelman). **É a obra que o TCC
cita; a referência (v. 6, n. 4, art. 15, 2012, DOI 10.1145/2382577.2382579)
bate com o PDF.** Lidas as 21 páginas, inclusive as referências.

| Afirmação do TCC (4.4) | Resultado |
|---|---|
| "nenhuma informação posterior ao corte entra como variável, o que evita o vazamento de dados descrito por Kaufman et al. (2012)" | **Confere.** Definição (resumo e seção 1): vazamento é "a introdução de informação sobre o alvo que não deveria estar legitimamente disponível". A condição *no-time-machine* (seção 3.2, eq. 3) exige que cada variável seja observável **antes** do alvo, e a seção diz "mais cedo (ou, às vezes, não mais tarde)". O nosso `frames[: corte + 1]` é o caso "não mais tarde": a previsão é feita no minuto do corte e as variáveis são observáveis até ele. **Nuance do periódico, ausente na conferência:** o operador de tempo é diferente para variáveis (instante em que ficam *observáveis*) e para o alvo (instante da *previsão*); aqui as duas coisas são o minuto do corte. A metodologia de prevenção é a separação aprendizado-previsão com marcas de legitimidade, que o artigo diz ser, no caso temporal, um corte no tempo |

**O que o periódico traz a mais que a conferência:**
1. **Seção 7, vazamento e causalidade.** Um segundo mecanismo de vazamento, o
   viés de **estratificar num colisor**: a amostragem do conjunto de dados (S)
   pode ser causada ao mesmo tempo pelo alvo e por uma variável (o exemplo é o
   identificador de paciente da KDD Cup 2008), criando uma relação artificial.
   O artigo diz que "a amostragem acidental num colisor é provavelmente uma das
   questões mais comuns na preparação de bases".
2. Exemplos novos (Kaggle/HIV 2010 e KDD Cup 2011) e a discussão de por que
   competições e projetos reais vazam por motivos diferentes.
3. A abordagem semiautomática do Kaggle: um modelo de *random forest* lista as
   *n* variáveis mais importantes para um especialista avaliar a legitimidade.
   Isso valida o uso do **SHAP/importância de variáveis como verificação de
   vazamento** (o nosso SHAP mostra ouro, experiência, abates, torres e
   dragões, todas legítimas no corte).

**Ponto para a defesa (não é achado, é pergunta que a seção 7 permite):** a
nossa coleta parte de jogadores que **estão** nas ligas Desafiante e
Grão-Mestre no momento da coleta, e o jogador chegou lá, em parte, por ter
vencido partidas recentes. Em tese a seleção das partidas depende um pouco dos
resultados passados dos participantes (um colisor possível). O efeito sobre a
taxa de vitória por lado não foi medido, e os cinco números do modelo são
calculados dentro de cada partida, sem usar o histórico dos jogadores. Resposta
honesta: "é uma limitação de amostragem, que declaro; o modelo não usa
nenhuma variável que dependa da seleção".

**Conclusão:** nenhuma correção no TCC; a referência de 2012 é a certa e fica.
**Pendência fechada.**

## Ajustes no TCC (aplicados em 2026-11-02)

Os seis ajustes abaixo, mais um sétimo na 2.1 ("desempenho competitivo" de
Bahrololloomi et al. virou "resultado da partida": o artigo estuda partidas
ranqueadas e o peso das funções no resultado), foram aplicados. Nenhum muda
número, e o documento seguiu em 29 páginas (`verifica_tcc.py` consistente,
`confere_docx.py` conforme). No ajuste 4 a 2.5 também trocou "fundamentou"
por "motivou". O texto de cada ajuste está na coluna "Proposta".

**Leitura completa de quatro artigos (anexados em 2026-11-02):**
Bahrololloomi, García-Méndez, Guo (Talk2Data) e Jiang (SiriusBI, versão do
PVLDB). Confirmaram os achados: Guo não tem diálogo; García-Méndez usa
CS:GO profissional (Kaggle/HLTV) e 92,51%; SiriusBI traz 97%, 93% e 96%
por setor e estudo com 40 analistas. Novidade da leitura de Bahrololloomi:
os "92,7%" são *100 − MAPE* numa regressão de XP por minuto, e os "86%" de
previsão de vitória comparam a soma das notas dos dois times **na própria
partida** (medida de fim de partida, não previsão em jogo).

| # | Seção | Hoje | Proposta |
|---|---|---|---|
| 1 | 2.4 | "...e Guo et al. (2024), que diálogo, decomposição de perguntas e análise visual tornam essa exploração mais intuitiva." | "Jiang et al. (2025) observam que soluções de *Business Intelligence* apoiadas por modelos de linguagem, com diálogo em várias rodadas, favorecem a exploração de dados estruturados, e Guo et al. (2024), que a decomposição de perguntas e a análise visual tornam essa exploração mais intuitiva." |
| 2 | 3.3 | "...na predição de vitória em esports, inclusive em transmissões (*streaming*). Deles vem o pressuposto de que um sistema preditivo só é útil ao usuário final quando acompanha a previsão de uma explicação dos fatores que a sustentam, que orienta..." | "...na predição de vitória em partidas profissionais de *Counter-Strike*, em fluxo contínuo (*streaming*). Eles apontam a falta de interpretabilidade como uma das principais limitações dos trabalhos anteriores, o que orienta..." |
| 3 | 5.7 | "A recomendação de García-Méndez e Arriba-Pérez (2025), de que a predição em esports precisa de interpretação para ser útil, foi atendida com o SHAP..." | "A limitação que García-Méndez e Arriba-Pérez (2025) apontam nos trabalhos anteriores, a falta de interpretação das previsões, foi enfrentada com o SHAP..." |
| 4 | 3.1 | "...chegam a até 85% de acurácia após 5 minutos de jogo, o que estabelece..." | "...chegam a até 85% de acurácia após 5 minutos de jogo, em previsões ao vivo de 28 partidas de um torneio, o que estabelece..." |
| 5 | 2.3 | "...simples de ler, mas sensível à escolha dessa vizinhança." | "...simples de ler, mas dependente de como essa vizinhança é definida." |
| 6 | 5.7 | "O mapa de calor aplica, de forma mais simples, a visualização espaço-temporal de Wallner, Wang e Dormann (2023), sem a técnica de *storyline* dos autores." | "O mapa de calor aplica, de forma mais simples, a integração de tempo e posição de Wallner, Wang e Dormann (2023), sem a técnica de *storyline*, e o mapa de calor de posição de Maymin (2021), que parte de rastreamento a cada segundo, e não do minuto da *timeline*." |

O ajuste 6 acrescenta a ressalva certa a uma pergunta que a banca pode
fazer: Maymin escreve que mapa de calor "não é possível com os dados da
API", e o nosso sai da API. A resposta é a resolução: o dele vem de
rastreamento óptico a cada segundo; o nosso agrega as posições por minuto
da *timeline-v5*, bem mais grosseiro, e o texto já admite que é mais
simples.

## Conferência das fontes de dados: Riot Games API e Oracle's Elixir (2026-11-03)

Conferido contra o código do coletor (`src/riot/client.py`, `src/collect/`),
o banco, os 13 CSVs em `data/pro/` (datados de 04/07/2026) e o portal
oficial (`developer.riotgames.com/docs/portal`, `/apis`). Medições com
`pandas` e SQL, reproduzíveis.

**Confere**
| Afirmação do TCC | Evidência |
|---|---|
| a chave de desenvolvedor expira a cada 24 horas (4.3, 5.1) | portal oficial: as chaves "se desativam a cada 24 horas" |
| o coletor opera dentro do limite de taxa e retoma sem duplicar (5.1, 4.3) | `RiotClient`: janela deslizante de 95 req/2 min e espera do `Retry-After` em 429 (portal: chave pessoal 20/s e 100/2 min); `known_match_ids` e `ON CONFLICT DO NOTHING` pulam partidas salvas |
| endpoints *league-v4*, *account-v1*, *match-v5* | URLs do cliente (`/lol/league/v4/...`, `/riot/account/v1/...`, `/lol/match/v5/...`) |
| fila 420, 41.063 partidas, cinco regiões | banco: todas as 41.063 são da fila 420; BR1 11.936, EUW1 11.744, KR 10.204, NA1 7.159, EUN1 20 |
| linha do tempo "minuto a minuto" | `frameInterval` = 60.000 ms; cada quadro traz a posição (x, y) de cada jogador; há o evento `TURRET_PLATE_DESTROYED` (experimento 10) |
| nomes de campeão com convenções diferentes (4.4) | Oracle's Elixir: *Wukong*, *Nunu & Willump*, *Renata Glasc*; Riot: *MonkeyKing*, *Nunu*, *Renata*. O mapeamento está em `CHAMPION_NORM_SQL` (`src/api/main.py`), **na consulta e não no ETL** |
| arquivos CSV anuais de 2014 a 2026 | 13 arquivos; esquema de `pro_games` (22 colunas, chave jogo+lado) idêntico ao do Apêndice A |

**Não confere ou está impreciso**
1. **96.716 jogos (Resumo, Abstract, 1, 4.3, 5.2, 5.3, Apêndice E).** Os CSVs
   têm **99.259 jogos únicos**; o banco tem 96.716. **Causa: erro em
   `src/etl/load_pro.py`.** Cada arquivo apaga `WHERE year = ano do arquivo`,
   mas insere cada linha com o `year` que ela traz. Os 2.543 jogos cujo `year`
   é maior que o do arquivo (por exemplo, jogos de 2015 dentro do arquivo de
   2014) são apagados quando o arquivo do ano seguinte é carregado. A medição
   fecha exatamente: os 2.543 ausentes são todos desse tipo, e nenhum jogo
   com `year` ≤ ano do arquivo se perdeu. **O verificador proíbe "99.259" como
   "contagem nunca conferida"**, e esse era o valor correto.
   **Efeito nos resultados:** a taxa do azul no total continua **53,2%**
   (53,21% no banco, 53,2% nos CSVs). Por ano muda pouco: 2015 de 55,3% para
   55,0%, 2016 de 53,6% para 53,5%, 2018 de 53,7% para 53,6%, 2025 de 53,3%
   para 53,2%; os demais iguais. Os ausentes sozinhos dão 52,9% (2.543 jogos).
   Nenhuma conclusão muda. Afeta 21 menções em 5 arquivos mais o verificador.
2. **Elos (4.3a, Quadro 1, 6.2).** O TCC diz que os jogadores são Desafiante
   e Grão-Mestre. A tabela `players` tem **60.680 jogadores, 93% de Mestre**
   (a semeadura incluiu a Mestre). Das 41.063 partidas, **97,2%** têm ao menos
   um Desafiante ou Grão-Mestre (média de 5,4 por partida), e **1.163 (2,8%)
   só têm Mestre**, das quais 769 na KR (7,5% das partidas da KR; a última
   rodada da KR desceu o ladder). Entre os participantes cujo *tier* é
   conhecido, 25% são Desafiante, 31% Grão-Mestre e 44% Mestre.
3. **"das principais ligas (LCK, LPL, LEC, LTA, CBLOL, entre outras)" (4.3b).**
   Os 99.259 jogos vêm de **122 ligas**; só 40,0% estão numa lista de 22 ligas
   principais e 60% nas outras 100 (desenvolvimento, acadêmicas e regionais,
   como LDL com 7.020 e LCKC com 2.511). A taxa do azul é a mesma nos dois
   grupos (53,4% e 53,0%), então a conclusão não depende da mistura. A LTA tem
   só 476 jogos.
4. **"*timeline-v5*" como endpoint (4.3a, 5.1, 6, Anexo A).** O índice
   oficial lista "match-v5" e **nenhuma "timeline-v5"**; no nosso cliente a
   linha do tempo é `GET /lol/match/v5/matches/{id}/timeline`, método do
   *match-v5*.
5. **Data de acesso do Oracle's Elixir.** A referência diz "Acesso em: 20 out.
   2026", mas os CSVs em disco são de **04/07/2026** (o último jogo do banco
   também). Convém declarar a data de coleta dos arquivos.

**Propostas (aguardam decisão).** (a) Corrigir `load_pro.py` (apagar por
`game_id` em vez de por ano), recarregar e atualizar 99.259 no texto, no guia,
no `handoff.md`, no `README.md` e no verificador (tirar "99.259" da lista de
valores proibidos e atualizar a constante); a tabela por ano muda em quatro
linhas. (b) Ajustar 4.3a, Quadro 1 e 6.2 para os elos reais. (c) Trocar
"principais ligas" por "122 ligas, da elite às de desenvolvimento". (d) Escrever
"*match-v5* (partida e linha do tempo)". (e) Declarar 04/07/2026 como data dos
arquivos.

## Erro de autoria encontrado em 2026-11-03 (Wang et al., 2020)

A referência do RAT-SQL trazia os coautores errados (WANG, Chuhan; SHIN, Yitao; LIU, Bing; POLOZOV, Alexander; RICHARDSON, Sarah) e o título sem "Parsers". Conferido no ACL Anthology (2020.acl-main.677) e no arXiv 1911.04942: **WANG, Bailin; SHIN, Richard; LIU, Xiaodong; POLOZOV, Oleksandr; RICHARDSON, Matthew**, título "RAT-SQL: relation-aware schema encoding and linking for text-to-SQL parsers", p. 7567-7578. Corrigido no TCC. As leituras anteriores conferiam as afirmações atribuídas a cada obra, não os prenomes dos autores. Também conferidos nesta data, e corretos: Wallner, Wang e Dormann (2023) e Guo et al. (2024).
