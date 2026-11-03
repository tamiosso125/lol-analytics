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
| Grinsztajn et al.; Brown, Cai e DasGupta; Kaufman et al. | só o resumo (o PDF de Grinsztajn passa do limite de leitura; os outros dois são de acesso restrito) | resumo |
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
| Grinsztajn et al. (2022) | árvores competitivas frente a redes em amostras de porte médio | **Confere** (o resumo diz que as árvores seguem no estado da arte). "Médio" é cerca de 10 mil amostras; as nossas são 39 mil, uma extrapolação razoável, não literal |
| Niculescu-Mizil e Caruana (2005) | calibração, preocupação conhecida em *boosting* | **Confere**: *boosted trees* empurram as probabilidades para longe de 0 e 1 (distorção em S), corrigida por Platt ou isotônica. Nuance: eles tratam *boosting* de margem máxima; o XGBoost usa perda logística, que já otimiza probabilidade, e a nossa curva de calibração confirmou |
| Wang et al. (2020) | representar o esquema com as relações, e não só com os nomes das colunas, melhora a precisão | **Confere**: *relation-aware* com ligação ao esquema; exact match no Spider sobe a 57,2%, +8,7 pontos |
| Zhong, Yu e Klein (2020) | limites da acurácia de execução; vários bancos de teste | **Confere**: a avaliação em um banco só gera falsos positivos; propõem *test suites* destiladas |
| Brown, Cai e DasGupta (2001) | intervalo de Wilson para proporções | **Confere** (resumo): recomendam Wilson ou Jeffreys para n pequeno e Agresti-Coull para n maior. Nossos n são de milhares, onde os três praticamente coincidem |
| Kaufman et al. (2012) | vazamento de dados | **Confere** (resumo): informação sobre o alvo que não deveria estar disponível |
| Holm (1979) | correção para comparações múltiplas | **Confere** |

## Ajustes propostos no TCC (aguardam aprovação)

Nenhum muda número. Cada um é do mesmo tamanho ou pouco maior; as páginas
são medidas depois.

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
