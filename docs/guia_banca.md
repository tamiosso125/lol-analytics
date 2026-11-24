# Perguntas possíveis da banca, por seção do TCC (Bellestraiko)

> Versão 2, gerada em 2026-11-23 após a simplificação do TCC (corpo de 28 páginas; 4 apêndices). Quadros e figuras seguem a **nova numeração**. Cada pergunta traz a **Resposta** (fiel ao texto do TCC), **Onde achar no TCC** e **Explicando fácil** (palavras simples e exemplos de jogos).

Observações: onde o TCC não responde, a pergunta diz isso e a sugestão é leitura minha (inferência). Números conferidos contra docs/tcc2_texto.md e reports/. Objetivos a–g: a mapear a Riot API (5.1); b informações para base estruturada (5.2); c coleta, tratamento e organização (5.2); d técnicas de análise para padrões (5.3); e comparar XGBoost, Random Forest e redes neurais (5.4); f dashboards (5.5); g interface em linguagem natural (5.6).

## Índice

1. Resumo (9)
2. 1 Introdução (10)
3. 2 Fundamentação teórica (14)
4. 3 Trabalhos relacionados (11)
5. 4.1 a 4.2 Natureza, abordagem e estratégias (6)
6. 4.3 Coleta de dados (8)
7. 4.4 Organização e tratamento (5)
8. 4.5 Análise exploratória e testes de robustez (7)
9. 4.6 Modelagem preditiva (15)
10. 4.7 e 4.8 Interface, coach e materiais (10)
11. 5.1 e 5.2 Mapeamento e base de dados (6)
12. 5.3 Análise exploratória: resultados (11)
13. 5.4 Modelagem: resultados (13)
14. 5.5, 5.6 e 5.7 Dashboards, linguagem natural e literatura (11)
15. 6 Conclusão, limitações e trabalhos futuros (11)
16. Apêndices e itens cortados (10)
17. Perguntas transversais (cruzam várias seções) (14)

---

## Resumo

### 1. Em uma frase, o que o seu trabalho fez?

**Resposta:** Desenvolveu uma plataforma que integra coleta de dados, modelos de previsão, explicação, visualização e consulta em português para League of Legends.

**Onde achar no TCC:** Resumo; Seção 1 (objetivo geral).

**Explicando fácil:** Pense num ‘painel de treinador’ de LoL num lugar só. Antes, para saber quem estava ganhando, você precisava baixar dados, rodar scripts e escrever consultas técnicas. Aqui, uma única plataforma coleta as partidas, prevê quem vence, mostra por que previu, desenha gráficos e deixa você perguntar em português, como num chat. O trabalho prova que dá para juntar tudo isso, e mede o quanto cada parte funciona.

### 2. Por que essas 41.063 partidas e 99.259 jogos profissionais? Para que cada base serve?

**Resposta:** As 41.063 partidas ranqueadas de elo alto sustentam a modelagem; os 99.259 jogos profissionais servem para comparar os dois contextos.

**Onde achar no TCC:** Resumo; Seção 4.3; Seção 5.2.

**Explicando fácil:** São duas fontes com funções diferentes, como treinar numa fila ranqueada e comparar com um campeonato mundial. As partidas ranqueadas (Desafiante a Mestre, vindas da API da Riot) têm a linha do tempo minuto a minuto, que é o que o modelo precisa para prever. Os jogos profissionais (arquivos do Oracle’s Elixir) não treinam o modelo: servem para perguntar ‘o que muda quando o jogo é profissional?’, por exemplo se o lado azul ganha mais ou menos.

### 3. Por que a AUC-ROC foi apresentada junto com a acurácia?

**Resposta:** A acurácia depende de um limiar e da taxa-base; a AUC-ROC mede a discriminação em todos os limiares. As duas são reportadas juntas.

**Onde achar no TCC:** Seção 2.3; Seção 5.4 (Quadro 2).

**Explicando fácil:** Se o azul perde 53% das partidas, um modelo que sempre diz ‘vermelho vence’ já acerta 53%, sem entender nada. Isso é como acertar um quiz chutando sempre a mesma letra. A AUC-ROC não cai nesse truque: ela pergunta ‘o modelo dá nota maior às partidas que o azul ganhou do que às que ele perdeu?’. 0,5 é chute, 1,0 é perfeito. Aqui, 0,8487 aos 15 minutos.

### 4. Os modelos empataram. Isso não invalida a comparação?

**Resposta:** Não. Após o ajuste, os quatro ficam a 0,0015 de AUC-ROC uns dos outros: os resultados sugerem que, com as cinco variáveis e o protocolo usados, maior complexidade do classificador não trouxe ganho relevante.

**Onde achar no TCC:** Resumo; Seção 5.4.

**Explicando fácil:** É um resultado, e não uma falha. Imagine dar a três chefs diferentes os mesmos 5 ingredientes: se o prato sai igual, é um indício de que o limite está nos ingredientes, e não na técnica. Aqui os ‘ingredientes’ são 5 números (ouro, XP, abates, torres, dragões). Um modelo simples e um complexo extraem praticamente a mesma coisa deles. Por isso o trabalho lê o gargalo como a informação disponível, sem afirmar que outra arquitetura jamais ganharia.

### 5. Por que o XGBoost foi mantido se a regressão logística foi um pouco melhor?

**Resposta:** Pela proximidade dos resultados e porque a integração com o SHAP de árvores já estava pronta na interface. A escolha não se apoia em superioridade de desempenho.

**Onde achar no TCC:** Resumo; Seção 5.4.

**Explicando fácil:** A diferença é 0,0008 de AUC, menos de um milésimo. Como a plataforma já explicava as previsões com SHAP em árvores (exato e rápido), trocar de modelo daria trabalho sem mudar o resultado prático. É como manter o controle do console que você já conhece quando o outro é só 1% melhor. O TCC é aberto nisso: diz que a escolha não é por superioridade.

### 6. O que significa o ‘viés favorável ao vermelho’ no solo queue?

**Resposta:** No agregado, o time vermelho venceu mais que o azul (56,3% na BR1, a região de maior amostra), com intensidade diferente por região.

**Onde achar no TCC:** Resumo; Seção 5.3 (Quadro 1).

**Explicando fácil:** Em LoL, as partidas ranqueadas têm dois lados do mapa. Se os dois fossem iguais, cada lado ganharia cerca de 50%. Mas os dados mostram o vermelho acima: 56,3% na BR1. É como descobrir que, em Mario Kart, quem larga numa certa pista ganha mais. O trabalho mede isso e testa se não é acaso ou mistura de regiões.

### 7. Por que o viés se inverte no profissional (53,2% para o azul)?

**Resposta:** O TCC não sabe: apresenta uma hipótese (prioridade de escolha no pro, counter-pick garantido do vermelho no solo queue) e diz que os dados não registram a ordem de escolha.

**Onde achar no TCC:** Seção 5.3; Seção 6.

**Explicando fácil:** Hipótese em jogo: no solo queue o time vermelho escolhe o campeão por último e pode ‘counterar’ (escolher alguém forte contra o do adversário). No profissional, o azul tem a prioridade de primeira escolha, que pesa mais com times coordenados. O TCC não consegue testar isso porque a API não guarda a ordem em que cada campeão foi escolhido. Então é hipótese, e é assim que deve ser dita.

### 8. 181 de 203 é 89,2%. Isso garante que a interface acerta 89% de qualquer pergunta?

**Resposta:** Não. É o resultado em perguntas geradas por modelos de pergunta; em versões antigas, perguntas livres escritas à mão acertaram 54% e 60%.

**Onde achar no TCC:** Seção 5.6; Seção 6.1; Apêndice B.

**Explicando fácil:** As 203 perguntas foram montadas por moldes (‘Qual a taxa de vitória do campeão X?’), com a resposta certa calculada antes. É como treinar para uma prova usando as questões do próprio professor: você vai bem, mas uma pergunta inesperada pode ser mais difícil. Por isso o TCC avisa que o número pode superestimar o desempenho em perguntas livres.

### 9. O que são as ‘seis páginas de visualização’?

**Resposta:** Início, Dashboard, Campeões, Partidas, Competitivo e Simulador; a consulta em linguagem natural tem página própria.

**Onde achar no TCC:** Resumo; Seção 5.5 (Figuras 3 e 4); as telas completas saíram do TCC (capturas em `reports/anexo_a/`).

**Explicando fácil:** São as telas da plataforma, como as abas de um jogo: Início (busca), Dashboard (números gerais), Campeões (estatísticas por campeão), Partidas (análise minuto a minuto de uma partida), Competitivo (profissional contra solo queue) e Simulador (prever e explicar um estado de jogo). A consulta em português é uma sétima tela, tratada à parte.

---

## 1 Introdução

### 10. Qual é a questão de pesquisa?

**Resposta:** Como desenvolver uma plataforma inteligente para análise de dados de League of Legends que integre coleta, organização, modelagem preditiva, visualização e consulta em linguagem natural para apoiar a interpretação de informações competitivas?

**Onde achar no TCC:** Seção 1, parágrafo do tema.

**Explicando fácil:** A questão de pesquisa é a pergunta que o trabalho tenta responder. Aqui ela é de ‘como fazer’: como montar uma plataforma que junte as etapas. A resposta do TCC é a própria plataforma, mais as medidas de quanto cada etapa funciona. Pense num projeto de montar uma ‘central de análise’ de um jogo e mostrar que dá certo.

### 11. Qual o objetivo geral e quais os objetivos específicos?

**Resposta:** Geral: desenvolver a plataforma. Específicos a a g: mapear a API; identificar informações para uma base estruturada; estruturar coleta e tratamento; avaliar técnicas de análise para padrões; comparar XGBoost, Random Forest e redes neurais; propor dashboards; propor interface em linguagem natural.

**Onde achar no TCC:** Seção 1; Seção 6 (cada objetivo retomado); Seção 6 (itens a a g).

**Explicando fácil:** O objetivo geral é o destino; os específicos são as fases, como as missões de um jogo: (a) descobrir o que a API da Riot oferece, (b) decidir o que guardar, (c) montar a coleta, (d) achar padrões, (e) comparar modelos, (f) fazer gráficos, (g) deixar perguntar em português. A Seção 5 mostra uma evidência para cada letra, e a Seção 6 retoma cada objetivo com a evidência.

### 12. Por que League of Legends e não outro jogo?

**Resposta:** O recorte é League of Legends, com duas fontes de dados; outros jogos ficam fora do escopo. Estender a outro jogo está nos trabalhos futuros.

**Onde achar no TCC:** Seção 1; Seção 6.2.

**Explicando fácil:** O TCC não compara jogos; escolheu um e foi fundo. Um bom motivo prático, e uma leitura minha: a Riot oferece uma API pública com linha do tempo minuto a minuto, o que permite prever em fases. O TCC declara apenas que outros jogos estão fora do escopo e que testar outro jogo é trabalho futuro.

### 13. O que é a plataforma Bellestraiko?

**Resposta:** É o nome do produto desenvolvido: a plataforma integrada de coleta, modelagem, explicação, visualização e consulta em linguagem natural.

**Onde achar no TCC:** Seção 1.

**Explicando fácil:** Bellestraiko é o ‘nome do jogo’ do produto. O título acadêmico do TCC não usa esse nome (decisão registrada), mas o texto chama a plataforma assim. Ela é composta de um coletor, um banco, modelos, uma API, telas em React e uma interface de perguntas em português.

### 14. A pesquisa é aplicada e quantitativa. O que isso significa?

**Resposta:** Aplicada: busca solucionar um problema prático (uma plataforma). Quantitativa: trabalha com dados numéricos (partidas, métricas, testes).

**Onde achar no TCC:** Seção 4.1; Resumo.

**Explicando fácil:** Aplicada é como fazer um mod para o jogo que resolve um problema real, em vez de só estudar teoria. Quantitativa é medir com números (taxas, AUC, intervalos) em vez de entrevistar pessoas. A revisão bibliográfica e a interpretação dão contexto, mas o centro são números.

### 15. Qual a justificativa acadêmica e a prática?

**Resposta:** Acadêmica: articula análise de dados, IA, machine learning, sistemas de informação e IHC sobre um campo em crescimento. Prática: reúne etapas em uma plataforma, reduz a dependência de ferramentas fragmentadas e serve à interpretação de desempenho e tendências.

**Onde achar no TCC:** Seção 1, parágrafo da justificativa.

**Explicando fácil:** Acadêmica é ‘por que isso é ciência da computação’: o trabalho junta várias áreas. Prática é ‘para que serve’: quem analisa partidas deixa de depender de vários programas e de conhecimento técnico alto. Como a ferramenta de edição de vídeo que junta cortar, legendar e exportar num app só.

### 16. O que significa ‘predições restritas ao estado do jogo até o momento da predição’?

**Resposta:** O modelo só pode usar informação que existia até o minuto do corte (10, 15, 20 ou 25), sem nada posterior.

**Onde achar no TCC:** Seção 1; Seção 4.6.

**Explicando fácil:** É a regra do jogo de adivinhação justo: se você vai prever aos 15 minutos, só pode olhar o placar até os 15 minutos. Usar o placar final (por exemplo, o total de abates da partida inteira) seria olhar o resultado. Isso se chama vazamento de dados e invalidaria tudo. O TCC garante que cada modelo vê só o estado do seu corte.

### 17. Por que ‘elo alto’ (Desafiante a Mestre)?

**Resposta:** É um recorte de escopo: uma população fechada, que a API lista por inteiro e que cabe no limite de requisições da chave de desenvolvedor.

**Onde achar no TCC:** Seção 4.3.

**Explicando fácil:** Em vez de tentar coletar milhões de jogadores de todos os elos, o trabalho pega os jogadores de topo, uma lista que a API entrega completa. É como estudar só o servidor competitivo. A consequência é que os resultados valem para esse recorte, e o TCC diz que não dá para estender a outros elos.

### 18. Por que a introdução cita Birant, García-Méndez e Jiang?

**Resposta:** Birant e Birant: modelos de ML para análise e predição em LoL. García-Méndez e Arriba-Pérez: não basta prever, é preciso apresentar de forma interpretável. Jiang et al.: modelos de linguagem reduzem a barreira técnica em BI.

**Onde achar no TCC:** Seção 1, 2º parágrafo.

**Explicando fácil:** Cada um sustenta uma parte do problema: (1) dá para prever com ML; (2) prever sem explicar não ajuda o usuário; (3) dá para conversar com os dados em linguagem natural. Os três juntos justificam uma plataforma que prevê, explica e responde em português.

### 19. O que fica fora do escopo?

**Resposta:** Outros jogos e outras abordagens de inteligência artificial; previsão ao vivo; outras filas, elos e versões não têm base para extensão.

**Onde achar no TCC:** Seção 1; Seção 6.1 e 6.2.

**Explicando fácil:** Fora do escopo é a lista de ‘isso não foi feito’. Previsão ao vivo (durante a partida em tempo real) não está implementada: a barreira é de dados em tempo real, não de modelo. Outros jogos ou outras filas ficam como trabalho futuro. Dizer isso na banca mostra que você conhece os limites do que entregou.

---

## 2 Fundamentação teórica

### 20. Por que comparar três famílias de modelos (Random Forest, XGBoost, MLP)?

**Resposta:** Porque os estudos delimitam o espaço de escolha mas não decidem qual família é adequada: o trabalho comparou por medição.

**Onde achar no TCC:** Seção 2.2; Seção 5.4.

**Explicando fácil:** É como testar três estilos de jogar a mesma fase em vez de escolher um por opinião. Random Forest é uma votação de muitas árvores; XGBoost são árvores em sequência, cada uma corrigindo a anterior; MLP é uma rede de neurônios. Medir os três evita escolher por moda.

### 21. O que é a Random Forest e o que são bagging e bootstrap?

**Resposta:** Combina bagging (cada árvore treina numa amostra bootstrap) com seleção aleatória de variáveis em cada nó, reduzindo a correlação entre as árvores.

**Onde achar no TCC:** Seção 2.2.

**Explicando fácil:** Imagine 200 jogadores avaliando a mesma partida, cada um vendo só um pedaço sorteado das informações. Cada um erra de um jeito, mas a média dos palpites é mais estável. Bootstrap é sortear partidas com reposição (pode repetir); bagging é treinar cada árvore numa dessas amostras; e o sorteio de variáveis a cada divisão impede as árvores de serem cópias.

### 22. O que é gradient boosting e como o XGBoost funciona?

**Resposta:** Constrói árvores em sequência, cada uma ajustada ao resíduo das anteriores, com otimização de segunda ordem e regularização.

**Onde achar no TCC:** Seção 2.2.

**Explicando fácil:** Na floresta as árvores votam sozinhas; no boosting elas se ajudam. A primeira faz um palpite; mede-se o erro; a segunda é treinada para consertar esse erro; a terceira conserta o que sobrou. Como num boss fight em que você corrige a estratégia a cada tentativa. O resultado é a soma das correções. ‘Segunda ordem’ e ‘regularização’ são refinamentos que deixam o treino mais preciso e evitam decorar.

### 23. O que é uma rede MLP e por que ela exige mais dados?

**Resposta:** Rede neural feedforward (perceptron multicamadas) com aproximação universal; captura interações sem especificá-las, mas exige mais dados e cuidado com escala e regularização.

**Onde achar no TCC:** Seção 2.2.

**Explicando fácil:** Uma MLP é uma pilha de camadas de ‘neurônios’ que somam as entradas com pesos e decidem quanto passar adiante. Treinar é ajustar os pesos aos poucos. Ela é flexível, mas como uma build com muitos itens: precisa de muita prática (dados) para saber usar, e sem cuidado ela decora. Com dezenas de milhares de partidas (e não milhões), isso é uma restrição.

### 24. O que dizem Grinsztajn et al. sobre dados tabulares?

**Resposta:** Em dados tabulares, métodos de árvores seguem competitivos frente a redes neurais em amostras de cerca de 10 mil exemplos, com indício de que a diferença diminui em amostras maiores.

**Onde achar no TCC:** Seção 2.2.

**Explicando fácil:** Dados tabulares são como uma planilha: colunas de números por partida. Para esse tipo, árvores costumam ir muito bem mesmo com poucos dados. É um motivo para comparar árvores e redes aqui, e para não se surpreender com o empate.

### 25. O que é o SHAP, de onde vem o valor de Shapley e o que o TCC adotou?

**Resposta:** O SHAP usa o valor de Shapley da teoria dos jogos: a importância de uma variável é sua contribuição média para a previsão sobre todas as combinações das demais. Foi o método adotado.

**Onde achar no TCC:** Seção 2.3.

**Explicando fácil:** Imagine um time que ganhou um prêmio e você quer repartir o mérito entre os jogadores. Valor de Shapley é a contribuição média de cada um, olhando todas as ordens possíveis de entrada. SHAP faz isso com as variáveis do modelo (ouro, XP, abates...), que são os ‘jogadores’, e o ‘prêmio’ é a previsão. Resultado: cada variável recebe uma contribuição, e referência mais contribuições dá a previsão.

### 26. Por que o SHAP e não o LIME?

**Resposta:** O LIME aproxima por um modelo linear local, simples de ler, mas pouco fiel se o modelo for muito não linear ali. O SHAP é aditivo e com propriedades (consistência, importância nula para variável ausente).

**Onde achar no TCC:** Seção 2.3.

**Explicando fácil:** LIME é como explicar um mapa inteiro olhando só a rua à sua frente e desenhando uma reta: ajuda perto, mas pode enganar se o terreno for curvo. SHAP reparte exatamente a previsão entre as variáveis. No XGBoost, o explicador de árvores é exato e já estava na interface; por isso o TCC adotou o SHAP e deixou o LIME como alternativa não adotada.

### 27. O que significa ‘as contribuições SHAP estão em log-odds, não em pontos percentuais’?

**Resposta:** O explicador de árvores atribui a saída bruta do XGBoost (em log-odds); as contribuições somam-se ao valor de referência e a probabilidade é a transformação logística da soma.

**Onde achar no TCC:** Seção 2.3; Seção 5.5 (Figura 4).

**Explicando fácil:** Log-odds é uma escala em que o modelo soma: 0 é 50%, +1 é 73%, +2 é 88%. A escala não é linear em probabilidade: +0,5 vale 12 pontos a partir de 50%, mas só 4 a partir de 88% (como subir de nível: os primeiros níveis rendem mais). Por isso o TCC nunca converte SHAP em pontos percentuais.

### 28. O que é a taxa-base e por que importa para a acurácia?

**Resposta:** Na amostra o azul vence 46,7%; um classificador que sempre dissesse vermelho acertaria 53,3% sem poder preditivo algum.

**Onde achar no TCC:** Seção 2.3.

**Explicando fácil:** Taxa-base é o placar que um chute fixo já faria. Se 53,3% das partidas são do vermelho, ‘sempre vermelho’ é um modelo de 53,3% de acurácia. Então 76% de acurácia só impressiona quando você compara com esse piso. É o ‘chute da moeda’ calibrado.

### 29. O que é AUC-ROC segundo Hanley e McNeil?

**Resposta:** Equivale à probabilidade de um caso positivo receber pontuação maior que um negativo.

**Onde achar no TCC:** Seção 2.3.

**Explicando fácil:** Pegue uma partida que o azul ganhou e uma que perdeu, ao acaso. AUC é a chance de o modelo dar probabilidade maior à que o azul ganhou. 0,5 é sorte, 1,0 é perfeito. Não depende de limiar de 0,5 nem da proporção de vitórias.

### 30. Qual o problema técnico central do text-to-SQL, segundo o TCC?

**Resposta:** O modelo produz texto, e o banco exige SQL válido e correto sobre um esquema específico; uma consulta gramaticalmente correta pode citar tabela inexistente ou responder à pergunta errada.

**Onde achar no TCC:** Seção 2.4.

**Explicando fácil:** Uma consulta pode estar ‘bem escrita’ e ainda assim errada, como obedecer a regra do jogo mas ir para o lugar errado do mapa. Dois riscos: (1) citar tabela que não existe e (2) responder outra coisa. Wang et al. mostram que descrever o esquema com os relacionamentos entre tabelas ajuda. O TCC valida a segurança antes de executar e mede a correção no gabarito.

### 31. Por que a segurança da consulta não é delegada ao modelo?

**Resposta:** Ela é validada antes de tocar o banco (um único SELECT ou WITH, palavras proibidas, lista de tabelas, execução somente leitura com tempo limite); a correção semântica é medida no benchmark e no gabarito.

**Onde achar no TCC:** Seção 2.4; Seção 5.6.

**Explicando fácil:** Confiar no modelo para ser seguro é como confiar que o jogador nunca vai usar cheat. Melhor ter um anti-cheat no servidor. A validação é um programa fixo e testável que barra comandos de escrita (insert, delete, drop) e tabelas fora da lista, não importa o que o modelo escreva.

### 32. O que a Seção 2.5 diz sobre dados espaço-temporais?

**Resposta:** Visualizações que integram tempo e localização numa só representação ajudam a interpretar o comportamento em jogo na revisão pós-partida (Wallner, Wang e Dormann, 2023); isso motivou o mapa de calor.

**Onde achar no TCC:** Seção 2.5; Seção 5.5.

**Explicando fácil:** Espaço é onde (posição no mapa), tempo é quando (minuto da partida). Ver os dois juntos é como ver o replay com o rastro dos jogadores. O mapa de calor da plataforma mostra, num minuto escolhido, onde estavam os 10 jogadores. A timeline pública tem uma amostra por minuto, então é uma aproximação.

### 33. O que é a ‘linha do tempo’ da partida?

**Resposta:** Um retrato por minuto da partida (ouro, experiência, posição) mais os eventos (abates, torres, dragões), com um quadro extra no instante em que o jogo acaba.

**Onde achar no TCC:** Seção 4.3; Seção 4.6.

**Explicando fácil:** É como o replay salvo de minuto em minuto: a cada 60 segundos fica registrado o ouro, a experiência e a posição de cada jogador, além dos eventos. O modelo usa o quadro do minuto do corte. O quadro extra do fim do jogo nunca pode servir de estado, porque já mostra o resultado.

---

## 3 Trabalhos relacionados

### 34. Como foram escolhidos os onze estudos? Foi uma revisão sistemática?

**Resposta:** Não. Os critérios foram recência (até cinco anos), cobrir cada frente da plataforma e, na predição, preferir estudos de League of Legends; lacunas foram fechadas por pesquisa complementar, com os artigos conferidos no texto completo.

**Onde achar no TCC:** Seção 3 (abertura).

**Explicando fácil:** Não é uma revisão sistemática (com protocolo e bases de busca fixas). É uma seleção por critérios: artigos recentes, que cubram predição, explicabilidade, consulta em linguagem natural e visualização. Dizer isso com clareza é melhor que fingir um método que não houve. Conferir contra o texto completo foi necessário porque alguns resumos escondiam detalhes.

### 35. O que Hodge et al. (2021) fizeram e por que citá-los se é Dota 2?

**Resposta:** Preveem a vitória em partidas profissionais de Dota 2 em tempo real, com modelos padrão, engenharia de atributos e otimização, até 85% após 5 minutos (28 partidas de um torneio).

**Onde achar no TCC:** Seção 3.1; Seção 5.7.

**Explicando fácil:** Citam-se porque mostram que prever o resultado a partir do estado da partida é um problema tratável. Mas é outro jogo e outra escala (28 partidas), então o TCC usa o estudo para sustentar a abordagem, e não para comparar números.

### 36. Por que o TCC adota a modelagem centrada no time (Birant e Birant) e não a do jogador?

**Resposta:** As variáveis são diferenças agregadas entre os dois times, seguindo Birant e Birant; Bahrololloomi et al. usam métricas individuais e concluem que o peso de cada função é desprezível.

**Onde achar no TCC:** Seção 3.2; Seção 5.7.

**Explicando fácil:** Numa partida de LoL quem vence é o time, não um jogador isolado. É como prever o resultado de um jogo de futebol pelo placar do time, não pela estatística de um atacante. As métricas individuais entram só nos perfis de jogador da plataforma. Além disso, nos experimentos, variáveis por jogador renderam menos de um centésimo de AUC.

### 37. Por que o TCC não prevê antes da partida, como Do et al. (2021)?

**Resposta:** O TCC prevê durante a partida, a partir do estado em cortes de tempo. Em experimento, campeões e histórico do jogador, sem o estado, deram AUC-ROC de 0,56 aos 15 minutos.

**Onde achar no TCC:** Seção 3.2; Seção 5.7 (o experimento de pré-jogo: só no repositório).

**Explicando fácil:** Prever antes de o jogo começar é como adivinhar o campeão pela seleção de campeões: quase não há informação ainda. O experimento do TCC mostra isso: sem o estado da partida, a AUC fica em 0,56, perto do chute. Do et al. chegam a 75,1% de acurácia com uma rede profunda e a experiência de cada jogador com o campeão, o que é um problema diferente.

### 38. O que Maymin (2021) e Guan e Tung (2026) fazem, e por que ficam fora da comparação numérica?

**Resposta:** Maymin calibra um modelo de probabilidade com milhões de partidas e avalia eventos individuais; Guan e Tung (preprint, pré-jogo profissional) avaliam o erro de probabilidade (Brier), não a acurácia.

**Onde achar no TCC:** Seção 3.2; Seção 5.7.

**Explicando fácil:** Para comparar números você precisa da mesma medida. Se um trabalho mede Brier (erro de probabilidade) e outro mede acurácia, os números não se comparam, como comparar o dano por segundo com a vida total. Guan e Tung também é um preprint, ainda sem revisão por pares.

### 39. Por que citar um preprint sem revisão por pares?

**Resposta:** Guan e Tung (2026) é citado como evidência de que a prioridade de escolha entra como covariável própria; o texto declara que o estudo é um preprint e que a citação não comprova a hipótese.

**Onde achar no TCC:** Seção 3.2; Seção 5.3.

**Explicando fácil:** Preprint é um artigo ainda não revisado por especialistas. O TCC o usa só como indício, não como prova, e avisa isso no texto. É como citar um rumor de patch notes: serve para contextualizar, não para afirmar.

### 40. O que García-Méndez e Arriba-Pérez fazem em Counter-Strike?

**Resposta:** Combinam classificação por machine learning com interpretação na predição de vitória, em fluxo contínuo (streaming); apontam a falta de interpretabilidade como limitação dos trabalhos anteriores.

**Onde achar no TCC:** Seção 3.3; Seção 5.7.

**Explicando fácil:** Em CS, o modelo prevê o vencedor enquanto o jogo acontece e explica o motivo. O TCC aproveita a ideia de explicar (SHAP na interface), mas não a de streaming. É o que sustenta o princípio ‘previsão sem explicação não basta’.

### 41. O que são SiriusBI e Talk2Data, e o que o TCC aproveita deles?

**Resposta:** SiriusBI (Jiang et al.): BI apoiado por modelos de linguagem em contextos corporativos. Talk2Data (Guo et al.): interface em linguagem natural para análise visual com decomposição de perguntas. Os dois motivam o text-to-SQL do TCC.

**Onde achar no TCC:** Seção 3.4; Seção 5.7.

**Explicando fácil:** São exemplos de ‘conversar com os dados’: você pergunta em linguagem natural e o sistema consulta. O TCC aplica a ideia de perguntar a dados estruturados e acrescenta a validação da consulta antes de executar. Não aplica a decomposição de perguntas nem a geração automática de gráficos.

### 42. O que é storyline visualization (Wallner, Wang e Dormann) e o TCC a usa?

**Resposta:** É uma técnica de visualização espaço-temporal do gameplay. O TCC não a usa: aplica, de forma mais simples, a integração de tempo e posição com um mapa de calor minuto a minuto.

**Onde achar no TCC:** Seção 3.5; Seção 5.7.

**Explicando fácil:** A storyline é como um gráfico de linhas que mostra as ‘trajetórias’ dos jogadores ao longo da partida. O TCC escolheu algo mais simples: um mapa de calor no minuto selecionado. E a timeline pública tem uma amostra por minuto, bem menos detalhada que um rastreamento a cada segundo.

### 43. Qual a lacuna que o TCC ocupa?

**Resposta:** Nenhum estudo é entregue como plataforma que reúna coleta, tratamento, modelagem, explicabilidade, visualização e consulta em linguagem natural sobre a mesma base.

**Onde achar no TCC:** Seção 3.6.

**Explicando fácil:** Os estudos cobrem uma peça cada: prever, explicar, perguntar ou visualizar. O TCC junta todas numa única plataforma. É a diferença entre ter ótimos jogadores avulsos e montar o time completo. A contribuição, portanto, é de integração, e não de bater o recorde de um deles.

### 44. Quais são as três decisões de projeto que distinguem o TCC?

**Resposta:** Horizonte da predição (quatro cortes, um modelo por corte), recorte de população (mesmo indicador nos dois contextos, solo queue e profissional) e consulta mensurável (gabarito automático de 203 perguntas).

**Onde achar no TCC:** Recorte de população: Seção 3.6. Horizonte: Seções 4.6 e 5.4. Consulta mensurável: Seção 5.6. (Na versão enxuta, a 3.6 manteve só o recorte.)

**Explicando fácil:** (1) Em vez de prever uma vez, prevê aos 10, 15, 20 e 25 minutos, para ver como o jogo fica mais previsível. (2) Mede a mesma coisa nos dois contextos e mostra que o viés de lado se inverte. (3) A interface de perguntas é testada com um gabarito de 203 perguntas, e não só exemplos bonitos.

---

## 4.1 a 4.2 Natureza, abordagem e estratégias

### 45. Que tipo de pesquisa é esta?

**Resposta:** Aplicada quanto à natureza; exploratória e descritiva quanto aos objetivos; predominantemente quantitativa quanto à abordagem; com estratégias bibliográfica e documental.

**Onde achar no TCC:** Seção 4.1 e 4.2.

**Explicando fácil:** São quatro rótulos que respondem a perguntas diferentes: natureza (para quê? aplicada, resolver um problema real), objetivos (o que faz? explorar e descrever), abordagem (como mede? números) e estratégia (de onde vêm as fontes? livros e artigos mais a documentação da API).

### 46. Exploratória e descritiva não é contradição?

**Resposta:** Não: exploratória na investigação da API e das possibilidades de modelagem; descritiva na caracterização dos dados, padrões e modelos comparados (Gil, 2002).

**Onde achar no TCC:** Seção 4.1.

**Explicando fácil:** Explorar é ‘ver o que existe e o que dá para fazer’, como abrir o mapa pela primeira vez. Descrever é ‘medir e relatar como é’, como listar as estatísticas do mapa. O trabalho faz as duas coisas em momentos diferentes, então os dois rótulos convivem.

### 47. Qual a diferença entre pesquisa bibliográfica e documental?

**Resposta:** Bibliográfica usa artigos e livros já analisados por outros autores; documental usa documentos ainda não analisados academicamente, como a documentação da Riot Games API.

**Onde achar no TCC:** Seção 4.2.

**Explicando fácil:** Bibliográfica é ler o que outros pesquisadores já escreveram (artigos). Documental é ler uma fonte ‘crua’ que ninguém tratou como estudo, como o manual da API. O TCC usa as duas: artigos para a teoria, a documentação oficial para saber o que a Riot entrega.

### 48. Por que ‘aplicação delimitada ao domínio de League of Legends’?

**Resposta:** Porque a pesquisa e a plataforma ficam restritas a esse jogo; outros jogos e abordagens ficam fora.

**Onde achar no TCC:** Seção 4.2; Seção 1.

**Explicando fácil:** Delimitar é dizer ‘até onde vai o trabalho’. Evita prometer que funciona em qualquer jogo. Isso protege contra a pergunta ‘funciona em Valorant?’: a resposta honesta é que não foi testado.

### 49. Por que predominantemente quantitativa e não mista?

**Resposta:** A coleta, a análise exploratória e a comparação de modelos trabalham com dados numéricos; a revisão bibliográfica e a interpretação dão o contexto (Creswell e Creswell, 2023).

**Onde achar no TCC:** Seção 4.1.

**Explicando fácil:** O núcleo é número: taxas de vitória, AUC, intervalos, testes. Não houve entrevista nem questionário. A parte textual (revisão, interpretação) serve para dar sentido aos números, e por isso se diz ‘predominantemente’ quantitativa.

### 50. Houve participação de pessoas, e isso exige comitê de ética?

**Resposta:** Os dados são secundários e públicos, sem participação de sujeitos humanos como fonte em nenhuma etapa.

**Onde achar no TCC:** Seção 4.3 (último parágrafo).

**Explicando fácil:** Ninguém foi entrevistado nem observado. Os dados vêm da API pública da Riot e de arquivos públicos do Oracle’s Elixir. Por isso o TCC declara que não há sujeitos humanos como fonte. Os identificadores de jogadores vêm da própria API pública.

---

## 4.3 Coleta de dados

### 51. Como a coleta foi feita, passo a passo?

**Resposta:** Pela Riot API: league-v4 lista os jogadores de elo alto, account-v1 resolve o Riot ID e match-v5 traz cada partida e a linha do tempo, em cinco regiões na fila 420.

**Onde achar no TCC:** Seção 4.3; Seção 5.1.

**Explicando fácil:** Primeiro lista-se quem são os jogadores de topo (league-v4); depois, para cada jogador, pega-se os ids das últimas partidas e baixa-se a partida e a linha do tempo (match-v5). Tudo é salvo em JSON bruto no banco. É como montar um álbum de figurinhas, pulando as que você já tem.

### 52. O que é a fila 420 e por que ela?

**Resposta:** É a fila ranqueada solo/duo.

**Onde achar no TCC:** Seção 4.3.

**Explicando fácil:** Fila 420 é a partida ranqueada em que o jogador entra sozinho ou em dupla. É o modo em que jogadores de elo alto se enfrentam por pontos de liga, então os dados são comparáveis entre si. Outras filas (normal, flex) têm outras regras e ficam fora.

### 53. Por que a EUN1 ficou fora da análise por região?

**Resposta:** Teve só 20 partidas, amostra insuficiente.

**Onde achar no TCC:** Seção 4.3; Seção 5.3 (Quadro 1).

**Explicando fácil:** Com 20 partidas a taxa de vitória oscila muito: pode virar 70% ou 30% só por sorte. Por isso a EUN1 aparece nos dados mas não entra na análise por região. É a mesma lógica de não julgar uma build por 3 partidas.

### 54. O que são limite de taxa e o erro 429?

**Resposta:** A API limita os pedidos por janela de tempo; o cliente do projeto se limita a 95 pedidos a cada 2 minutos (margem sob o limite de 100 que o próprio código atribui à chave de desenvolvimento). Se exceder, a API devolve 429 e o cliente espera o tempo do cabeçalho Retry-After.

**Onde achar no TCC:** Seção 5.1 (menciona os limites de taxa e a validade de 24 horas, sem os números); número exato: `src/riot/client.py`. O quadro com os tipos de chave saiu do TCC (`git show f2ecb39:docs/tcc2_texto.md`) e deve ser conferido no portal developer.riotgames.com, porque o limite varia conforme o tipo de chave.

**Explicando fácil:** Limite de taxa é a fila de senhas do banco: só atendem tantos por minuto. O cliente do TCC conta os pedidos e espera quando chega perto de 95. Se mesmo assim receber 429 (‘muitos pedidos’), dorme o tempo que a Riot manda. Assim a coleta roda por horas sem ser bloqueada.

### 55. Por que a chave expira a cada 24 horas e como isso afeta o trabalho?

**Resposta:** A chave de desenvolvedor expira em 24 horas; o coletor é resumível e retoma de onde parou, pulando as partidas já salvas.

**Onde achar no TCC:** Seção 4.3; Seção 5.1.

**Explicando fácil:** Chave de desenvolvedor é uma senha temporária. Se a coleta cair por expiração, basta gerar outra chave e rodar de novo: o coletor lê o que já está no banco e continua. Funciona como salvar o jogo: voltar não repete o que já foi feito (idempotência).

### 56. De onde vêm os 99.259 jogos profissionais?

**Resposta:** Do Oracle’s Elixir: arquivos anuais CSV de 2014 a 2026, de 122 ligas (arquivos de 4 de julho de 2026).

**Onde achar no TCC:** Seção 4.3 (composição por liga: só no repositório, consulta a `pro_games`).

**Explicando fácil:** É um site que publica, em planilhas CSV, os resultados de jogos profissionais de LoL. O TCC baixou os arquivos anuais e carregou em tabelas. Atenção: são 122 ligas, da elite às de desenvolvimento; 40% dos jogos estão em 22 ligas principais. A taxa de vitória do azul é parecida nos dois grupos (53,4% e 53,0%).

### 57. O que é um dado secundário e por que isso importa?

**Resposta:** Dado que já foi coletado por outra instituição (a Riot e o Oracle’s Elixir), e não por entrevistas ou experimentos do autor.

**Onde achar no TCC:** Seção 4.3.

**Explicando fácil:** Dados primários são os que você mesmo produz (uma pesquisa). Secundários já existem. A vantagem é ter volume (41 mil partidas); o cuidado é que você não controla como foram coletados, e por isso o TCC cita as ressalvas (viés de seleção, recortes).

### 58. Os dados são representativos de todos os jogadores?

**Resposta:** Não. São partidas ranqueadas de Desafiante a Mestre em cinco regiões; não há base para estender a outras filas, elos, versões ou jogos.

**Onde achar no TCC:** Seção 6.1 (validade externa).

**Explicando fácil:** Representar todos exigiria sortear de todos os elos. Aqui é só elo alto, o que é o recorte do estudo. A conclusão deve ser lida como ‘vale para elo alto’. E dentro disso há desequilíbrio: BR1 e EUW1 têm mais partidas, e o patch 16.13 concentra 40,4% da coleta.

---

## 4.4 Organização e tratamento

### 59. Por que um banco relacional (PostgreSQL)?

**Resposta:** Foi escolhido por atender o projeto, mas o TCC não compara alternativas.

**Onde achar no TCC:** Seção 4.4; Apêndice A.

**Explicando fácil:** O TCC não justifica com comparação. O que atende ao projeto, como leitura minha: dados estruturados com chaves, SQL como base da interface em português, tipo JSONB para guardar o JSON bruto, gratuito e rodando local. Na banca, não afirme que foi comparado com outros bancos.

### 60. O que é ETL e que tratamentos foram feitos?

**Resposta:** Extrair, transformar e carregar: normalização da partida bruta de cada fonte, extração das compras e vendas de itens da linha do tempo com os desfazimentos aplicados, e reconciliação dos nomes de campeão entre a Riot e o Oracle’s Elixir.

**Onde achar no TCC:** Seção 4.4.

**Explicando fácil:** ETL é a linha de montagem: tira o dado cru (JSON, CSV), arruma e coloca nas tabelas. Exemplo de arrumação: se o jogador compra um item e desfaz a compra, a compra não pode contar. E ‘Wukong’ na Riot é MonkeyKing no banco, com outros nomes nos arquivos profissionais; é preciso reconciliar.

### 61. Por que guardar o JSON bruto e também as tabelas?

**Resposta:** Para reprocessar sem nova coleta quando a regra de extração mudar.

**Onde achar no TCC:** Seção 5.2; Apêndice A.

**Explicando fácil:** A API tem limite de pedidos: coletar tudo de novo levaria horas. Guardando o bruto, se você descobrir um bug (como o das torres no time errado), refaz as tabelas a partir do arquivo salvo. É como guardar o replay original além do resumo da partida.

### 62. O que o catálogo de itens resolve?

**Resposta:** Permite resolver nome e ícone de item por consulta ao banco, sem depender da memória de um modelo de linguagem.

**Onde achar no TCC:** Seção 4.4.

**Explicando fácil:** Se a interface perguntasse a um modelo ‘quanto custa o item 3153?’, ele poderia inventar. A tabela items (do Data Dragon da Riot) responde com o dado real. É o princípio do trabalho: fato do jogo sai de tabela, não da memória da IA.

### 63. O que significa ‘desfazimentos de compra aplicados’?

**Resposta:** Se o jogador desfaz a compra de um item, o evento de desfazer cancela a compra; a tabela de itens já vem com isso resolvido.

**Onde achar no TCC:** Seção 4.4; Apêndice A (Quadro 4).

**Explicando fácil:** Na loja do LoL dá para desfazer uma compra e receber o ouro de volta. Se você só contasse as compras, contaria itens que o jogador nunca teve. O ETL aplica os desfazimentos para a tabela refletir o que o jogador realmente possuía.

---

## 4.5 Análise exploratória e testes de robustez

### 64. O que foi investigado na análise exploratória?

**Resposta:** Distribuições e relações entre variáveis, com atenção à taxa de vitória por lado do mapa em três recortes: região, fase da partida e contexto (solo queue ou profissional).

**Onde achar no TCC:** Seção 4.5.

**Explicando fácil:** É perguntar ‘o azul ganha mais que o vermelho?’ de três ângulos: por região (BR, EUW, KR, NA), por fase do jogo (10, 15, 20, 25 minutos) e por contexto (ranqueada ou campeonato). A análise foi descritiva: mede o que acontece, sem afirmar a causa.

### 65. Quais são os quatro testes de robustez e por que existem?

**Resposta:** (i) replicação numa só região; (ii) comparação por duração total; (iii) intervalo de confiança de Wilson; (iv) comparação de pares com correção de Holm. Nenhum padrão foi aceito sem passar por eles.

**Onde achar no TCC:** Seção 4.5; Seção 5.3.

**Explicando fácil:** São quatro perguntas de ‘isso é real ou ilusão?’: (i) o padrão some se eu olhar uma região só? (ii) é porque partidas longas são diferentes? (iii) o intervalo de confiança exclui 50%? (iv) quando faço várias comparações, ainda sobra diferença depois de corrigir o acaso? É como checar se uma estratégia funciona em outro mapa, em outra duração e com margem de erro.

### 66. O que é o intervalo de Wilson?

**Resposta:** Um intervalo de confiança de 95% para uma proporção que funciona melhor que o usual em amostras menores (Brown, Cai e DasGupta, 2001).

**Onde achar no TCC:** Seção 4.5.

**Explicando fácil:** Se o azul venceu 47% em 1.000 partidas, a taxa verdadeira provavelmente está numa faixa em volta de 47%, por exemplo entre 44% e 50%. Essa faixa é o intervalo. Com mais partidas, a faixa estreita. O de Wilson é uma versão mais confiável quando a amostra não é enorme. Se a faixa não contém 50%, o desvio é provavelmente real.

### 67. O que é a correção de Holm e por que ela foi decisiva?

**Resposta:** Corrige a multiplicidade quando várias diferenças são testadas na mesma base; sem ela, a dispersão entre cortes seria lida como tendência.

**Onde achar no TCC:** Seção 4.5; Seção 5.3.

**Explicando fácil:** Se você joga 20 partidas de moeda e procura qualquer sequência esquisita, vai achar uma só por acaso. Com 6 comparações entre cortes, a chance de achar uma ‘diferença’ falsa sobe. Holm ajusta os valores-p para isso. Resultado do TCC: depois do ajuste nenhuma das seis diferenças foi detectada (menor valor-p corrigido 0,65).

### 68. Por que a partida foi usada como unidade no bootstrap?

**Resposta:** Porque a mesma partida pode aparecer em mais de um corte; reamostrar partidas inteiras preserva essa dependência.

**Onde achar no TCC:** Seção 5.3.

**Explicando fácil:** Uma partida empatada em ouro aos 10 e aos 15 minutos entra nos dois grupos, então os grupos não são independentes. Se você tratasse cada linha como independente, o erro seria subestimado. Reamostrando a partida inteira (bootstrap), o computador reproduz essa sobreposição e a margem de erro fica honesta.

### 69. O que é o teste de duração e o que ele mostra?

**Resposta:** Compara a taxa de vitória do azul entre faixas de duração total da partida: 45,6% a 47,3%, amplitude de 1,7 ponto, todas abaixo de 50%; não houve diferença expressiva desse indicador entre partidas curtas e longas.

**Onde achar no TCC:** Seção 5.3 (frase do teste de duração); faixas por duração: só no repositório (`reports/faixa_duracao.json`).

**Explicando fácil:** Alguém poderia dizer: ‘o viés só aparece em jogos longos’. O teste divide as partidas por duração e vê se o padrão se mantém em todas. Ele se mantém (azul sempre abaixo de 50%), então a duração, sozinha, não parece explicar o viés; isso não prova que partidas curtas e longas sejam iguais em tudo.

### 70. Por que a análise exploratória é descritiva e não causal?

**Resposta:** Mede o que ocorre e a robustez estatística, sem atribuir causa; as hipóteses (prioridade de escolha, counter-pick) são declaradas sem comprovar.

**Onde achar no TCC:** Seção 5.3; Seção 6.

**Explicando fácil:** Descrever é dizer ‘o vermelho vence 56,3% na BR1’. Causal seria dizer ‘por causa do counter-pick’. Para isso seria preciso testar com dados de ordem de escolha, que a API não dá. O TCC é cuidadoso: diz o que viu e a hipótese, sem confundir os dois.

---

## 4.6 Modelagem preditiva

### 71. Quais são as variáveis do modelo?

**Resposta:** Cinco diferenças, azul menos vermelho: ouro, experiência, abates, torres e dragões acumulados até o corte.

**Onde achar no TCC:** Seção 4.6; Seção 5.4.

**Explicando fácil:** O modelo vê só cinco números por partida, todos no nível do time: quanto o azul está à frente em ouro, experiência, abates, torres e dragões. Exemplo: +1.500 de ouro, +800 de XP, +3 abates, 1 torre a mais, 0 dragões. É o placar resumido de um instante.

### 72. Por que um modelo para cada corte (10, 15, 20, 25)?

**Resposta:** Porque a importância das variáveis muda de fase: por exemplo, torres quase não pesam até os 20 minutos e sobem aos 25. Um modelo por fase é mais adequado que um genérico.

**Onde achar no TCC:** Seção 4.6; Seção 5.4 (Figura 2).

**Explicando fácil:** Aos 10 minutos quase ninguém derrubou torre; aos 25 já é comum. Um modelo único teria que servir a todas as fases e misturaria as regras. Treinar um por fase é como ter um guia diferente para o early game e outro para o late game.

### 73. O que é vazamento de dados e como o TCC o evita?

**Resposta:** É usar informação que não existiria na hora da previsão (Kaufman et al., 2012). No TCC, nenhuma informação posterior ao corte entra, e o quadro final da linha do tempo nunca é usado como estado do corte.

**Onde achar no TCC:** Seção 4.6; Seção 5.4.

**Explicando fácil:** É estudar com a prova respondida. Exemplo no LoL: prever o vencedor aos 15 minutos usando o total de abates da partida inteira. O modelo ‘acerta’ porque olha o futuro. O TCC tem um caso real: numa partida de 24min16s o ‘estado aos 25 minutos’ era o quadro final, com o vencedor decidido; foi corrigido em 8/11.

### 74. Qual foi o erro do quadro final e quantas partidas afetou?

**Resposta:** O estado do corte era o quadro final do jogo em partidas que acabaram antes; afetou 22, 37, 1.120 e 2.642 partidas aos 10, 15, 20 e 25 minutos; a AUC-ROC nessas linhas era 1,0.

**Onde achar no TCC:** Seção 4.6 (descreve a regra, sem as contagens). As contagens 22, 37, 1.120 e 2.642 estão só no diário de execução (8/11/2026) e no código, `src/features/build_features.py` (corte_disponivel).

**Explicando fácil:** A linha do tempo tem um quadro por minuto mais um quadro extra no instante em que o jogo acaba. O código antigo só checava ‘tem quadros suficientes?’ e em partida curta o quadro ‘25’ era o do fim. A regra nova exige um quadro DEPOIS do quadro do corte, então o estado é sempre de um minuto com o jogo em andamento. Tudo foi refeito depois da correção.

### 75. O que é validação cruzada estratificada com 5 dobras?

**Resposta:** Divide as partidas em 5 grupos, treina em 4 e testa no quinto, 5 vezes; estratificada preserva a proporção de vitórias do azul e do vermelho em cada grupo (Kohavi, 1995).

**Onde achar no TCC:** Seção 4.6.

**Explicando fácil:** É como cinco rodadas de teste em que cada quinto das partidas é a ‘prova’ uma vez. A nota é a média. Estratificada garante que cada grupo tenha ~46,7% de vitórias do azul, como o total. Kohavi recomenda 10 dobras; a diferença para 5 é de no máximo 0,0004 de AUC no TCC.

### 76. Por que 5 dobras e não 10, como Kohavi recomenda?

**Resposta:** A diferença para 10 dobras é de no máximo 0,0021 em acurácia e 0,0004 em AUC-ROC (Random Forest aos 15 min; no XGBoost, 0,0006 e 0,0001) e não altera nenhuma conclusão.

**Onde achar no TCC:** Seção 4.6 (5 dobras); comparação 5 x 10 dobras: só no repositório (`src/models/robustez_dobras.py`).

**Explicando fácil:** O TCC comparou: rodou com 5 e com 10 dobras e viu que o resultado praticamente não muda. Cinco dobras gastam menos tempo de máquina. Se perguntarem, a resposta é essa medida, e não uma opinião.

### 77. O que é o GridSearchCV e o que ele otimizou?

**Resposta:** Busca em grade (scikit-learn) que testa combinações de hiperparâmetros otimizando a AUC-ROC; no XGBoost testou 27 combinações e escolheu 500 árvores, taxa de aprendizado 0,01 e profundidade 3.

**Onde achar no TCC:** Seção 4.6; Apêndice C (Quadro 7).

**Explicando fácil:** Hiperparâmetros são os botões do modelo (número de árvores, profundidade, velocidade de aprendizado). A busca em grade é testar todas as combinações de uma lista, como regular resolução, sombras e DLSS num jogo para achar o melhor equilíbrio. Cada combinação é medida em cinco dobras, e vence a de maior AUC.

### 78. A busca de hiperparâmetros foi feita nas mesmas partidas em que se mediu? Isso não é otimista?

**Resposta:** Pode ser; por isso as três buscas foram repetidas de forma aninhada, com a escolha feita só no treino de cada dobra. A AUC-ROC muda no máximo 0,0002.

**Onde achar no TCC:** Seção 4.6; Seção 5.4; Apêndice C.

**Explicando fácil:** Se você escolhe a configuração olhando a prova, a nota fica otimista (a escolha ‘viu’ o teste). O desenho aninhado separa: dentro de cada dobra de treino, a grade roda numa validação interna de 3 dobras; só depois a combinação escolhida é testada na dobra externa, que a busca nunca viu. Resultado: o otimismo é desprezível.

### 79. Por que a busca do XGBoost foi na primeira base de 10.295 partidas?

**Resposta:** Foi feita na primeira base ampla, cujas partidas estão contidas nas 40.778 da avaliação final; repetida na base final, a busca escolheu a mesma configuração.

**Onde achar no TCC:** Seção 4.6; Apêndice C.

**Explicando fácil:** A busca em grade foi feita quando a base era menor; depois repetiu-se na base final e a escolha foi a mesma (500, 0,01, 3). Um ponto que a banca pode apontar: as 10.295 partidas aparecem nas dobras de avaliação. Por isso a seleção aninhada foi feita, que testa a escolha sem esse viés.

### 80. O que é o MLP de referência e o ajustado?

**Resposta:** Referência: camadas (64, 32) e 500 iterações. Ajustado pela grade: uma camada de 32 neurônios, regularização alpha 0,001.

**Onde achar no TCC:** Seção 4.6; Apêndice C (Quadro 7).

**Explicando fácil:** Referência é a configuração de partida, sem busca. A grade testou 9 combinações de tamanho de camadas e regularização, e a vencedora foi a mais simples (32 neurônios). Em dados com 5 variáveis, uma rede pequena basta.

### 81. Por que a regressão logística entrou como baseline?

**Resposta:** Serve de baseline simples; ela chegou a AUC-ROC 0,8495, à frente do XGBoost por 0,0008.

**Onde achar no TCC:** Seção 4.6; Seção 5.4 (Quadro 2).

**Explicando fácil:** Baseline é o ‘modelo ponto de partida’ que qualquer método complexo tem que bater. A logística é a mais simples: pesa cada variável e soma. Ela empatou com os complexos, o que é um achado: com 5 variáveis, simples basta.

### 82. Como o modelo de produção foi calibrado e explicado?

**Resposta:** Recebeu curva de calibração sobre as probabilidades fora da dobra e explicações SHAP, globais e por predição.

**Onde achar no TCC:** Seção 4.6; Seção 5.4; Apêndice C (calibração, Quadro 10 e Figura 5).

**Explicando fácil:** Calibrar é checar se ‘70%’ significa mesmo 70% de vitórias. SHAP é explicar quanto cada variável empurrou a previsão. As probabilidades ‘fora da dobra’ vêm de modelos que não viram aquela partida no treino.

### 83. O que são os dez experimentos de enriquecimento e o décimo primeiro?

**Resposta:** Dez tentativas de acrescentar sinais da linha do tempo (barão/arauto, posição, tuning por fase, calibração, itens, atributos, visão, dragões por tipo, placas); o décimo primeiro usou um endpoint de progressão do jogador e fica à parte.

**Onde achar no TCC:** Seção 4.6; Seção 5.4 (parágrafo de experimentos); detalhe e quadros: só no repositório (`reports/experimentos_antigos.json`, `reports/experimentos_precisao.json`).

**Explicando fácil:** Foi a pergunta ‘mais informação melhora a previsão?’. Para cada ideia, mediu-se o ganho de AUC contra o mesmo modelo de 5 variáveis. O máximo foi +0,0006. O décimo primeiro consultou um atributo depois das partidas e, por isso, não é comparável e não entra em nenhuma conclusão.

### 84. Por que o experimento 11 fica à parte?

**Resposta:** O endpoint lol-challenges devolve o estado do jogador na data da consulta, de 0 a 16 dias depois das partidas; o valor pode refletir partidas posteriores. O resultado (−0,0031 e +0,0007) não entra em nenhuma conclusão.

**Onde achar no TCC:** Experimento 11: só no repositório (`src/models/experiment_challenges_pilot.py`, `reports/`); o TCC cita só que ele fica à parte.

**Explicando fácil:** É como prever quem ganha a partida de ontem olhando o perfil do jogador de hoje, que já inclui o jogo de ontem. Isso é vazamento potencial. Um piloto de 199 partidas deu +0,0090, mas com 2.987 deu −0,0031 (regressão à média em amostra pequena).

### 85. Por que a regressão logística aproveitou melhor as variáveis novas?

**Resposta:** Aos 15 minutos o ganho foi +0,0073 na logística e +0,0044 no XGBoost, cada um contra si mesmo; o TCC lê isso como indício de que o limite está na informação, não no algoritmo.

**Onde achar no TCC:** Seção 5.4 (ganhos máximos); Seção 6.1; detalhe por experimento: só no repositório (`reports/experimentos_precisao.json`).

**Explicando fácil:** Se um modelo simples (logística) usa melhor as variáveis novas do que o complexo, o algoritmo não é o gargalo. É um indício que o TCC apresenta como interpretação, sem provar.

---

## 4.7 e 4.8 Interface, coach e materiais

### 86. Como é a arquitetura da plataforma?

**Resposta:** Aplicação web em React com TypeScript que consome uma API própria em FastAPI; seis páginas de visualização; banco PostgreSQL.

**Onde achar no TCC:** Seção 4.7; Seção 4.8.

**Explicando fácil:** Três camadas: o banco guarda os dados; a API (FastAPI) responde a pedidos; a interface (React) desenha as telas e chama a API. É como o servidor, o cliente e o banco de um jogo online: a tela nunca fala direto com o banco.

### 87. Como a pergunta em português vira resposta?

**Resposta:** Roteamento (solo, competitivo ou ambos), o modelo escreve a SQL, a validação confere, a execução é somente leitura com tempo limite de 10 s e o resultado vem do banco, nunca do conhecimento do modelo.

**Onde achar no TCC:** Seção 4.7; Seção 5.6.

**Explicando fácil:** Primeiro decide em qual base perguntar; depois o Claude traduz para SQL; um programa confere que é só leitura e só nas tabelas permitidas; o banco executa e a tela mostra o resultado. Uma nota ‘Leitura de jogo’ pode acrescentar conhecimento geral, rotulada como tal.

### 88. O que é a acurácia de execução?

**Resposta:** Compara o resultado da consulta gerada com o da consulta de referência; Zhong, Yu e Klein discutem seus limites e propõem vários bancos de teste, o que o TCC não faz.

**Onde achar no TCC:** Seção 4.7.

**Explicando fácil:** Em vez de comparar o texto da SQL (duas SQLs diferentes podem dar a mesma resposta), compara-se o resultado que cada uma devolve. Se bate, acertou. O limite: uma consulta errada pode coincidir por acaso num banco só; por isso Zhong et al. propõem testar em vários bancos, e o TCC reconhece que não faz.

### 89. O que é o coach e o que ele pode e não pode dizer?

**Resposta:** É o módulo que traduz a probabilidade e as contribuições SHAP em recomendações em linguagem natural; separa o que vem dos dados do que é conhecimento geral do modelo, marcado como tal.

**Onde achar no TCC:** Seção 4.7; Seção 6.1; Apêndice B.

**Explicando fácil:** O coach é um treinador virtual. Ele recebe o estado da partida, a probabilidade e o SHAP, e escreve orientações. A regra de honestidade: o que vem dos dados (confrontos, sinergias, itens do histórico) é rotulado; o que a IA sabe do jogo em geral (itens que recomenda, ondas de minions) é marcado como conhecimento geral. Nunca deve inventar estatística.

### 90. O coach inventa números?

**Resposta:** Em 36 respostas auditadas, 453 números; nenhuma estatística foi inventada após revisão (13 não achados: 8 derivados dos dados, 2 de formato, 3 limiares de conhecimento geral).

**Onde achar no TCC:** Seção 4.7; Apêndice B (Quadro 5).

**Explicando fácil:** A auditoria conferiu cada número do texto do coach contra os dados enviados à IA. Os 13 que o detector não achou foram revisados à mão. A ressalva importante: a auditoria confere números, não afirmações qualitativas. No caso 5, a resposta atribui atraso a dois campeões quando os dados só tinham o time inteiro.

### 91. Por que o modelo preditivo não vê itens, posição nem ondas de minions?

**Resposta:** Porque a linha do tempo do match-v5 não registra o estado das ondas nem a ordem de escolha, e o modelo usa só as cinco diferenças; orientação que dependa disso, além do que o coach recebe dos dados, é inferência.

**Onde achar no TCC:** Seção 4.7; Seção 6.1.

**Explicando fácil:** O modelo foi treinado só com 5 números. Itens e posição não são variáveis dele, e o estado das ondas de minions nem existe na API. O coach é outro módulo: pode receber dados reais (itens do catálogo, confrontos de rota, histórico) e acrescenta conhecimento geral da IA, que a interface rotula como inferência. O que o coach diz além do que recebeu dos dados é inferência, não saída do modelo.

### 92. Que ferramentas foram usadas e por quê?

**Resposta:** Python (pandas, NumPy, scikit-learn, XGBoost, SHAP), PostgreSQL, FastAPI, React com TypeScript e Recharts, e a API da Anthropic (Claude); testes de fumaça, validação comportamental e Vitest.

**Onde achar no TCC:** Seção 4.8.

**Explicando fácil:** Cada ferramenta tem um papel: Python para dados e modelos, PostgreSQL para guardar, FastAPI para a API, React para as telas, Recharts para gráficos, Claude para linguagem natural e coach. São ferramentas consolidadas; a API da Anthropic é cobrada por uso. O TCC não compara com alternativas.

### 93. Onde foi desenvolvido e executado?

**Resposta:** Localmente, em um computador com Windows 11, Intel Core i5-13400F e 32 GB de memória.

**Onde achar no TCC:** Seção 4.8.

**Explicando fácil:** Tudo roda numa máquina comum, sem servidor em nuvem. Isso ajuda a reprodutibilidade: o código, o banco congelado e os artefatos de `reports/` permitem refazer os números. Uma nova coleta, porém, pode gerar outra amostra, e as chamadas à Riot e à Anthropic exigem chaves próprias.

### 94. Que testes automatizados existem?

**Resposta:** Testes de fumaça e uma bateria de validação comportamental do modelo de produção no backend, e Vitest no frontend.

**Onde achar no TCC:** Seção 4.8.

**Explicando fácil:** Teste de fumaça é o ‘liga e vê se pega fogo’: verifica o essencial sem banco nem API. A validação comportamental checa, por exemplo, que o modelo dá mais chance ao time à frente em ouro. O Vitest testa os componentes das telas. São verificações de que nada quebrou, e não provas de acerto.

### 95. Como a plataforma garante a reprodutibilidade?

**Resposta:** Semente 42 nas validações, base congelada em 4/10/2026, versão do gabarito marcada no repositório e scripts que conferem o texto contra os artefatos.

**Onde achar no TCC:** Seção 4.6; Apêndice B (versões e congelamento); scripts do projeto.

**Explicando fácil:** Fixar a semente faz o sorteio das dobras ser sempre o mesmo. Congelar a base é como salvar o estado do jogo: os números não mudam porque entrou partida nova. E os scripts de verificação comparam o texto do TCC com os arquivos de resultado, para nenhum número ficar solto.

---

## 5.1 e 5.2 Mapeamento e base de dados

### 96. O que foi mapeado na Riot API (objetivo a)?

**Resposta:** Os endpoints league-v4, account-v1 e match-v5 (partida e linha do tempo), além dos limites de taxa e do ciclo de expiração da chave de 24 horas.

**Onde achar no TCC:** Seção 5.1.

**Explicando fácil:** Mapear é descobrir o que a API oferece e o que dá para usar. Resultado: três famílias de endpoints (listar jogadores, resolver nomes, baixar partidas e linhas do tempo) e as regras do jogo da API (limite de pedidos, chave que expira). Isso orientou o coletor resumível.

### 97. Quantas partidas há e por que 40.778 e não 41.063?

**Resposta:** O banco tem 41.063 partidas; aos 15 minutos a base de modelagem tem 40.778, porque as demais acabaram antes desse minuto ou não têm linha do tempo; o número varia por corte.

**Onde achar no TCC:** Seção 5.2; Apêndice A (Quadro 4).

**Explicando fácil:** 41.063 é o total salvo. Para prever aos 15 minutos, a partida precisa ter chegado aos 15 minutos e ter linha do tempo; 285 não têm. Por isso cada corte tem um número diferente: 40.919, 40.778, 34.505 e 25.098.

### 98. Como o volume cresceu e por que isso importa para a NA1?

**Resposta:** 10.295 na primeira base ampla, 23.133 no retreino de julho e 41.063 ao fim da coleta de 4/10; a NA1 passou de 1.446 para 7.159 partidas.

**Onde achar no TCC:** Seção 5.2 (41.063 partidas, 40.778 no corte de 15 min). O histórico de crescimento por região saiu do TCC: só no repositório (`diario_execucao.md`, `reports/stats_regions.txt`).

**Explicando fácil:** A NA1 era a menor região com amostra relevante e a que mais limitava a generalização do achado de viés de lado. Com 7.159 partidas, deixou de ser limitação: a taxa do vermelho foi de 51,9% para 52,2% sem mudar a direção.

### 99. O que guarda cada tabela do banco?

**Resposta:** players, raw_matches e raw_timelines, matches, teams, participants, bans, item_events e items, pro_games e pro_players (descritas na Seção 5.2; campos e chaves no Quadro 4, Apêndice A).

**Onde achar no TCC:** Seção 5.2; Apêndice A (Quadro 4).

**Explicando fácil:** Pense em fichas ligadas por um número de partida (match_id): matches é a ficha da partida; teams, uma por time; participants, uma por jogador; bans, os campeões banidos; item_events, compras e vendas; items, o catálogo; pro_games e pro_players, o profissional. Os brutos (raw_) guardam o JSON original.

### 100. O que é chave primária e chave estrangeira?

**Resposta:** Primária identifica uma linha (ex.: match_id em matches); estrangeira aponta para a chave de outra tabela (ex.: teams.match_id → matches.match_id).

**Onde achar no TCC:** Apêndice A.

**Explicando fácil:** A primária é o ‘CPF’ da linha: não repete. A estrangeira é o ‘endereço’ que liga uma linha a outra tabela. Por exemplo, o time 100 (azul) de uma partida aponta para essa partida pelo match_id. Chave composta (match_id + team_id) identifica o time dentro da partida.

### 101. Como o TCC evita linhas duplicadas na carga?

**Resposta:** O coletor retoma de onde parou, pula partidas já salvas, e os INSERTs usam ON CONFLICT DO NOTHING.

**Onde achar no TCC:** Seção 4.3; Seção 5.1.

**Explicando fácil:** É a mesma ideia de salvar o jogo: rodar de novo não repete o que já existe. Se a carga rodar duas vezes, a chave primária impede a segunda linha igual. Isso se chama idempotência.

---

## 5.3 Análise exploratória: resultados

### 102. Qual o resultado do viés de lado no solo queue?

**Resposta:** O vermelho venceu mais que o azul: BR1 56,3%, EUW1 53,4%, NA1 52,2%, KR 50,4%. Em BR1, EUW1 e NA1 o intervalo de 95% exclui 50%; na KR o intervalo [49,5%, 51,4%] inclui 50%.

**Onde achar no TCC:** Seção 5.3 (Quadro 1).

**Explicando fácil:** Em todas as regiões o vermelho fica de 50% para cima, mas com força diferente. Na BR1 a diferença é grande e firme. Na KR não dá para distinguir de 50%. Portanto o padrão não se limita ao Brasil, mas as quatro regiões não o demonstram com a mesma força.

### 103. Por que a KR tem 50,4% e a BR1 56,3%? O que explica?

**Resposta:** O TCC não sabe: os dados não permitem dizer.

**Onde achar no TCC:** Seção 5.3; Seção 6.

**Explicando fácil:** O TCC mede a diferença, mas não explica. Qualquer explicação (metagame, composição dos jogadores, versão) seria hipótese. Na banca, responda ‘não sei, e os dados não permitem dizer’; é uma resposta honesta e forte.

### 104. O que são ‘taxas próximas nos quatro cortes’ e por que ‘nenhuma diferença detectada’ não é ‘iguais’?

**Resposta:** Entre partidas com diferença absoluta de ouro menor que 500, o azul venceu 46,5% (10 min), 47,8% (15), 46,9% (20) e 47,4% (25). Nenhuma das seis diferenças entre pares foi detectada após Holm; isso não demonstra que o viés seja igual em toda a partida.

**Onde achar no TCC:** Seção 5.3; Apêndice C (Quadro 10).

**Explicando fácil:** ‘Não detectei diferença’ não é ‘provei que é igual’. Com 1.000 partidas, ±3 pontos já é erro de amostragem. O TCC só afirma que as taxas ficam próximas e que, depois da correção por múltiplas comparações, nada se distingue do acaso.

### 105. Por que a faixa ‘diferença de ouro menor que 500’?

**Resposta:** Para comparar partidas em estado equilibrado, em que o azul e o vermelho estão perto em ouro.

**Onde achar no TCC:** Seção 5.3; Apêndice C (Quadro 10, calibração nas partidas empatadas).

**Explicando fácil:** Se um time está +3.000 de ouro, a vitória dele é provável e esconde o efeito do lado. Escolhendo partidas empatadas em ouro, sobra o efeito do lado do mapa. É como comparar largar na pista A ou na B só entre pilotos de mesmo nível.

### 106. O que mostra o teste (i), a replicação na BR1?

**Resposta:** Reproduz a assimetria, o que mostra que o padrão não decorre apenas da mistura de regiões.

**Onde achar no TCC:** Seção 5.3.

**Explicando fácil:** Alguém pode dizer: ‘o viés aparece porque você misturou regiões diferentes’. Olhando só a BR1, ele continua. Logo não é só efeito de mistura, embora a composição de cada região ainda possa influenciar os outros resultados.

### 107. Qual o resultado no profissional e como ele se compara?

**Resposta:** O azul venceu 53,2% em 99.259 jogos, com série anual estável desde 2015 (entre 52,5% e 55,0%): sinal oposto ao do solo queue de elo alto.

**Onde achar no TCC:** Seção 5.3; série anual: só no repositório (consulta em `pro_games`).

**Explicando fácil:** A mesma pergunta (‘qual lado ganha mais?’) tem resposta oposta nos dois contextos. É um achado descritivo: no ranqueado o vermelho, no campeonato o azul. O TCC oferece uma hipótese (prioridade de escolha e counter-pick), não testada.

### 108. Por que 53,1% na Figura 1 e 53,2% no texto?

**Resposta:** A Figura 1 restringe o profissional a 2026 (53,1%); o texto usa o acervo completo (53,2%).

**Onde achar no TCC:** Seção 5.3 (final do parágrafo da conversão de vantagem).

**Explicando fácil:** São dois recortes diferentes. 53,2% é de todos os 99.259 jogos de 2014 a 2026; 53,1% é só de 2026 na tela. Não é erro, mas convém saber para não se atrapalhar se alguém notar.

### 109. O que é a conversão de vantagem e quais os resultados?

**Resposta:** Com vantagem de ouro de +2.000 a +4.000 aos 15 minutos o azul venceu 83,6% no profissional (n = 14.617) e 74,1% no solo queue (n = 5.366); de +4.000 a +6.000, 94,0% contra 86,3%.

**Onde achar no TCC:** Seção 5.3 (conversão de vantagem); origem das taxas: só no repositório (`docs/confere_conversao_advantagem.py`).

**Explicando fácil:** Conversão de vantagem é quanto de uma vantagem de ouro vira vitória. No profissional, estar +2.000 à frente aos 15 minutos vira vitória em 83,6% das vezes, e no ranqueado, em 74,1%. É como ter 2 níveis a mais: no campeonato quase sempre se converte, na ranqueada nem tanto.

### 110. A diferença de 9,5 pontos é significativa? O que isso quer dizer?

**Resposta:** Sim: teste z de duas proporções com grupos independentes, z = 15,2 e z = 12,7, p < 0,001. Mas é diferença observada, sem causa atribuída.

**Onde achar no TCC:** Seção 5.3.

**Explicando fácil:** z grande e p menor que 0,001 significam que a diferença é grande demais para ser sorte. Mas o TCC não afirma o porquê: os dois recortes diferem também em nível dos jogadores, versão do jogo e época. Atribuir à coordenação das equipes exigiria uma evidência que o trabalho não tem.

### 111. Houve algum erro de cálculo na conversão de vantagem?

**Resposta:** Sim, corrigido: o script lia a linha do jogador do topo em vez da linha do time; os valores corretos são os do texto atual (83,6%, n = 14.617).

**Onde achar no TCC:** Seção 5.3; diário de execução (17/11/2026).

**Explicando fácil:** O arquivo do Oracle’s Elixir tem 12 linhas por jogo (10 de jogador e 2 de time). O script antigo pegava a primeira linha do azul, que é a do jogador do topo, e não a do time. Foi achado ao comparar com uma consulta direta no banco e corrigido no script, no texto, nos slides e nos documentos. Se alguém citar os valores antigos (81,5% e 91,7%), eles estão superados.

### 112. Quais os testes de robustez (ii), (iii) e (iv) mostraram?

**Resposta:** (ii) taxa do azul próxima entre as faixas de duração (45,6% a 47,3%); (iii) Wilson do corte de 10 min [45,3%, 47,6%] exclui 50%; (iv) Holm: nenhuma diferença entre cortes detectada.

**Onde achar no TCC:** Seção 5.3.

**Explicando fácil:** (ii) não mostra diferença expressiva entre partidas curtas e longas. (iii) mostra que mesmo na maior amostra o azul fica abaixo de 50%. (iv) impede ler a variação entre os cortes como uma tendência. Juntos, sustentam que o viés é um padrão estável, mas não que seja igual em toda a partida.

---

## 5.4 Modelagem: resultados

### 113. O que mostra o Quadro 2?

**Resposta:** A comparação dos modelos aos 15 minutos: a regressão logística (AUC 0,8495), o MLP ajustado (0,8491), o XGBoost ajustado (0,8487) e a Random Forest ajustada (0,8480); as referências sem ajuste dão 0,8459 e 0,8278.

**Onde achar no TCC:** Seção 5.4 (Quadro 2).

**Explicando fácil:** É o ‘placar’ final. Depois do ajuste, os quatro modelos ficam a 0,0015 de AUC e 0,0020 de acurácia uns dos outros. O ajuste de hiperparâmetros importou principalmente para a Random Forest (0,8278 para 0,8480). O XGBoost de produção tem acurácia 0,7641.

### 114. Por que a Random Forest de referência foi tão pior (0,8278)?

**Resposta:** Era a configuração de referência (500 árvores, demais parâmetros padrão do scikit-learn), sem busca em grade; ajustada, subiu para 0,8480.

**Onde achar no TCC:** Seção 5.4 (Quadro 2); Apêndice C (Quadro 7).

**Explicando fácil:** Árvores sem limite de profundidade tendem a decorar os dados de treino. A busca em grade escolheu profundidade 6 e folha mínima de 5 partidas, que freiam a memorização. O TCC mostra os dois para ser transparente.

### 115. Como interpretar a AUC-ROC de 0,8487? Significa 84,87% de acerto?

**Resposta:** Não. É a probabilidade de uma partida que o azul ganhou receber pontuação maior que uma que ele perdeu; a acurácia é outra medida (0,7641).

**Onde achar no TCC:** Seção 2.3; Seção 5.4.

**Explicando fácil:** AUC e acurácia são medidas diferentes. A acurácia (76,41%) é a fração de acertos com limiar de 50%. A AUC (0,8487) é a capacidade de ordenar partidas. Confundir as duas é um erro comum na banca; vale deixar claro.

### 116. Como o desempenho varia com o corte?

**Resposta:** XGBoost: AUC 0,7752 (10 min), 0,8487 (15), 0,8690 (20), 0,8899 (25); acurácia 0,7020, 0,7641, 0,7856, 0,8068.

**Onde achar no TCC:** Seção 5.4 (Quadro 3).

**Explicando fácil:** Mais tempo, mais informação: aos 25 minutos o placar já diz muito. Mas cuidado: cada corte avalia partidas diferentes, e as curtas só entram nos primeiros cortes. Nas mesmas 25.098 partidas, a AUC vai de 0,644 a 0,890: o efeito do tempo é claro e maior.

### 117. Por que não comparar 0,775 com 0,890 como ‘melhora com o tempo’?

**Resposta:** Porque a população muda: as partidas curtas, mais fáceis de prever cedo, só entram nos primeiros cortes; nas mesmas 25.098 partidas os valores são 0,644, 0,713, 0,787 e 0,890.

**Onde achar no TCC:** Seção 5.4; Apêndice C (Quadro 9).

**Explicando fácil:** Aos 10 minutos entram muitas partidas que acabam cedo (massacres, fáceis de prever); aos 25 só ficam as que duraram. Comparar os dois números é comparar conjuntos de partidas diferentes. O jeito certo é olhar as mesmas partidas em todos os cortes.

### 118. O que mostra o SHAP por corte?

**Resposta:** Ouro e experiência dominam em todos os cortes; torres quase não pesam até os 20 minutos (0,0038, 0,0076, 0,0023) e sobem aos 25 (0,0429), cerca de 6 vezes o valor dos 15.

**Onde achar no TCC:** Seção 5.4 (Figura 2); valores por corte: só no repositório (`reports/shap_importance_phases.json`).

**Explicando fácil:** Em LoL, derrubar uma torre antes dos 14 minutos é raro (as placas de defesa caem por volta daí), então uma torre a mais não diz muito cedo. Aos 25 já pesa. É a justificativa concreta para treinar um modelo por fase. Lembre: é média do valor absoluto, em log-odds; mostra o tamanho do peso, não a direção.

### 119. A calibração do modelo é boa?

**Resposta:** Sim: o maior desvio entre decis é 1,19 ponto percentual aos 15 minutos; nas partidas empatadas a média prevista fica a menos de 0,5 ponto da observada. O modelo não exigiu correção.

**Onde achar no TCC:** Seção 5.4; Apêndice C (Quadro 10 e Figura 5).

**Explicando fácil:** Calibrado é quando ‘70%’ significa 70% de vitórias. Dividindo as previsões em 10 faixas, o pior desvio foi 1,19 ponto. Como a plataforma mostra a probabilidade ao usuário, ela precisa ser confiável. A sigmoide piorou a calibração e a isotônica não melhorou a AUC nem o Brier.

### 120. Por que não aplicar calibração isotônica, que reduziu o desvio médio?

**Resposta:** Reduziu o desvio médio (0,36 pp) sem melhorar o escore de Brier nem a AUC-ROC; a calibração adicional não traz ganho, e a produção segue sem ela.

**Onde achar no TCC:** Calibração adicional (isotônica e sigmoide): só no repositório (`docs/experimento_calibracao.py`); a calibração do modelo de produção está no Apêndice C (Quadro 10, Figura 5).

**Explicando fácil:** Mexer num modelo que já está bem calibrado só complica. A isotônica baixou um pouco o desvio médio, mas não melhorou as duas medidas principais. Custo sem benefício, então ficou fora.

### 121. O que a curva de aprendizado mostra?

**Resposta:** Com teste fixo de 8.156 partidas, a AUC-ROC passa de 0,8494 (2.500 partidas) para 0,8519 (10.000) e 0,8527 (32.622): acima de 10 mil, mais volume quase não muda o resultado.

**Onde achar no TCC:** Curva de aprendizado: só no repositório (`src/models/curva_aprendizado.py`, `reports/curva_aprendizado.json`); a frase-resumo está na Seção 5.4 (acima de 10 mil partidas, mais volume quase não muda o resultado).

**Explicando fácil:** Treinando com cada vez mais partidas e testando sempre no mesmo conjunto, a nota quase para de subir depois de 10 mil. Isso sugere que o limite está nas cinco variáveis, e não na quantidade de partidas. Coletar mais não valeria o esforço.

### 122. Por que a sequência 0,8214, 0,8393 e 0,8487 não prova o efeito do volume?

**Resposta:** Porque registra as rodadas de coleta, com conjuntos de teste diferentes (e composição regional e de versões diferentes); não isola o efeito do volume.

**Onde achar no TCC:** Seção 5.4.

**Explicando fácil:** Entre as rodadas mudaram juntos o tamanho do treino, as partidas avaliadas e a composição por região. Para atribuir o ganho só ao volume, o teste tem que ser fixo. Foi o que a curva de aprendizado fez.

### 123. O que mostra o treino no passado e teste no futuro?

**Resposta:** Divisões cronológica 80/20 e por patch (16.10 a 16.13 treinam e 16.14 a 16.19 testam) ficam iguais ou acima da aleatória, exceto 0,0026 abaixo aos 10 minutos (dentro do intervalo).

**Onde achar no TCC:** Seção 6.1; Apêndice C (Quadro 8).

**Explicando fácil:** É o teste do ‘viajante do tempo’: treinar com partidas antigas e testar nas novas, como o jogo muda de patch. Se o modelo só funcionasse no passado, a nota cairia; não caiu. Ressalva: a região se mistura ao tempo (o teste cronológico tem 44,3% de NA1 e nenhuma BR1).

### 124. O que são os experimentos 12 a 19 e que ganho tiveram?

**Resposta:** Oito conjuntos novos de variáveis (trajetória, por função, objetivos, campeões, jogadores, histórico); aos 15 minutos o ganho foi de até +0,0044 no XGBoost e +0,0073 na regressão logística.

**Onde achar no TCC:** Seção 5.4; Seção 6.1; quadros dos experimentos: só no repositório (`reports/experimentos_precisao.json`).

**Explicando fácil:** Foi a pergunta ‘e se eu der muito mais informação?’. O ganho foi menor que um centésimo de AUC. Cada conjunto foi medido contra o mesmo classificador com as cinco variáveis originais, para isolar o efeito das variáveis.

### 125. Por que o ganho de +0,0081 (da regressão logística com todas as variáveis contra o XGBoost) não é só das variáveis?

**Resposta:** Compara a regressão logística com 64 variáveis ao XGBoost com 5: muda variáveis e classificador ao mesmo tempo. O ganho só das variáveis é +0,0073 (logística) e +0,0044 (XGBoost).

**Onde achar no TCC:** Seção 5.4 e Seção 6.1 (os dois ganhos); o quadro com as três comparações: só no repositório (`reports/ganho_variaveis_logit.json`).

**Explicando fácil:** Se você troca o motor e o combustível ao mesmo tempo, não sabe qual melhorou o carro. O +0,0081 mistura as duas mudanças; os números limpos são +0,0073 e +0,0044.

---

## 5.5, 5.6 e 5.7 Dashboards, linguagem natural e literatura

### 126. O que a Figura 4 (simulador) mostra, passo a passo?

**Resposta:** O usuário define as diferenças aos 15 minutos; o modelo devolve 71,2% para o azul e o SHAP decompõe: referência −0,132 (46,7%) + contribuições +1,038 = 0,906 log-odds, que a função logística leva a 71,2%.

**Onde achar no TCC:** Seção 5.5 (Figura 4).

**Explicando fácil:** A referência −0,132 é a previsão média do modelo (46,7%, perto da taxa de vitória do azul). Cada variável empurra para cima ou para baixo (ouro, XP...); a soma dá +0,906. Para virar probabilidade: 1 / (1 + e^−0,906) ≈ 71,2%. É a ‘conta’ da previsão, escrita barra a barra.

### 127. A estimativa por composição de time é do modelo?

**Resposta:** Não. O simulador separa a estimativa por composição (uma heurística de taxa de vitória histórica, sinalizada como tal na interface) da predição do modelo de produção a partir do estado de jogo.

**Onde achar no TCC:** Seção 5.5.

**Explicando fácil:** São duas coisas diferentes: (1) a heurística ‘esses campeões costumam ganhar’ (histórico) e (2) o modelo de ML, que usa o estado da partida. A interface avisa qual é qual, para ninguém tomar a heurística por previsão do modelo.

### 128. O que é o mapa de calor e que limite ele tem?

**Resposta:** Mostra o posicionamento dos jogadores no minuto escolhido; a timeline tem uma amostra por minuto, então é aproximação.

**Onde achar no TCC:** Seção 5.5 (Figura 3); Seção 5.7.

**Explicando fácil:** Cada jogador deixa uma ‘mancha’ de cor (azul ou vermelho) onde estava no minuto escolhido; as manchas se acumulam numa janela de poucos minutos. Mas só há uma foto por minuto, bem menos que um rastreamento segundo a segundo. Não é uma variável do modelo; é um recurso de exploração.

### 129. O que é o benchmark de 26 perguntas e por que ele ‘não é independente’?

**Resposta:** Eram 23 de 26 antes dos ajustes e 26 de 26 depois; os ajustes foram orientados pelas três falhas conhecidas, então o 26 de 26 não é medida independente.

**Onde achar no TCC:** Seção 5.6 (não cita o 26: só o gabarito de 203); Apêndice B (o benchmark de 26 perguntas saiu do TCC: só no repositório, `src/nlq/evaluate_nlq.py`).

**Explicando fácil:** É estudar para a prova depois de ver a prova: você acerta tudo, mas isso não prova que sabe a matéria. As três falhas eram conhecidas, e as regras do esquema foram escritas depois de conhecê-las. Por isso a medida principal é outra: o gabarito de 203.

### 130. O que é o gabarito automático de 203 perguntas?

**Resposta:** Perguntas geradas por moldes (templates) sobre entidades reais do banco, cada uma com a SQL de referência escrita antes de qualquer execução; um programa compara os resultados.

**Onde achar no TCC:** Seção 5.6; Apêndice B.

**Explicando fácil:** Um gerador monta perguntas (‘Qual a taxa de vitória do campeão X?’) já com a resposta calculada. Depois o sistema responde pelo caminho do produto e um comparador automático vê se bate. 203 foram sorteadas. Vantagem: não depende de avaliador humano. Limite: são perguntas de molde, e não livres.

### 131. Qual o resultado e o intervalo de confiança?

**Resposta:** 181 de 203 (89,2%), Wilson de 95% de 84,1% a 92,7%: 166 de 187 respondíveis e 15 de 16 recusas esperadas.

**Onde achar no TCC:** Seção 5.6; Apêndice B (as famílias do gabarito saíram do TCC: só no repositório, `reports/nlq_gabarito_resultado_203.json`).

**Explicando fácil:** Das 203, 187 tinham resposta no banco (166 acertos) e 16 deviam ser recusadas porque o banco não tem o dado (15 recusadas certo). O intervalo 84,1% a 92,7% mostra a incerteza. Entre as famílias mais fracas estão liga (66,7%), KDA (66,7%) e média por campeão (72,2%).

### 132. Quais foram as 22 falhas e o que elas dizem?

**Resposta:** Nomes de entidade escritos de outro modo pelo modelo (‘Monkey King’ no lugar de MonkeyKing), abates somados indevidamente às assistências e roteamento para a base errada.

**Onde achar no TCC:** Seção 5.6; Apêndice B.

**Explicando fácil:** As falhas não são de segurança, e sim de significado: o modelo ‘corrigia’ nomes pela memória, somava assistências onde a pergunta pedia só abates e às vezes perguntava na base errada. Foram identificadas por família de pergunta (o quadro por família saiu do TCC; está em `reports/nlq_gabarito_resultado_203.json`).

### 133. As três correções feitas depois melhoraram o resultado?

**Resposta:** Não foram medidas de ponta a ponta. O TCC não afirma melhoria; a versão medida é a marcada gabarito-203.

**Onde achar no TCC:** Seção 5.6; Apêndice B.

**Explicando fácil:** Corrigiu-se (1) nome exato resolvido no banco, (2) refazer a consulta quando abates são somados indevidamente às assistências, (3) enviar ao competitivo perguntas com liga, equipe ou jogador profissional. Mas o gabarito não foi rodado de novo com elas; então o 89,2% é da versão anterior. Dizer isso com clareza protege você.

### 134. O que é a recusa determinística?

**Resposta:** Uma regra em código, antes do modelo, que responde ‘não é possível responder’ para perguntas sobre o que o banco não registra (primeiro sangue, série, estado em minutos que não 15, dano a estruturas).

**Onde achar no TCC:** Seção 4.7; Seção 5.6.

**Explicando fácil:** O banco não tem certas informações. Dizer isso no prompt para o modelo é probabilístico: ele pode ignorar e inventar um substituto. Uma lista de padrões em código responde antes e sempre igual. No gabarito, 15 das 16 recusas esperadas saíram certas.

### 135. Quais os controles de segurança da SQL?

**Resposta:** Um único comando iniciado por SELECT ou WITH; bloqueio de palavras de escrita e administração; lista fechada de tabelas; execução em transação somente leitura com tempo limite de 10 segundos.

**Onde achar no TCC:** Seção 5.6; Apêndice B.

**Explicando fácil:** É um anti-cheat em camadas: (1) só uma instrução de leitura; (2) palavras como INSERT, DELETE, DROP bloqueadas; (3) só as tabelas permitidas; (4) transação somente leitura e tempo limite. Mas esses controles não verificam se a consulta responde à pergunta: segurança não é correção.

### 136. Como os resultados se comparam com a literatura (Seção 5.7)?

**Resposta:** As acurácias de 70,2% a 80,7% ficam na mesma ordem de grandeza de Jadowski e Cunningham (67%) e Do et al. (75,1%), mas a comparação é apenas indicativa: mudam o nível, o momento e a informação.

**Onde achar no TCC:** Seção 5.7.

**Explicando fácil:** É como comparar tempos de speedrun de jogos e categorias diferentes: serve de referência, não de ranking. O TCC não afirma superar nem ficar abaixo de ninguém; usa a literatura para situar a ordem de grandeza.

---

## 6 Conclusão, limitações e trabalhos futuros

### 137. O objetivo geral foi alcançado? Em que se baseia?

**Resposta:** Sim, segundo o TCC, com evidência para cada objetivo específico (a a g) na Seção 5.

**Onde achar no TCC:** Seção 6; Seção 6 (itens a a g).

**Explicando fácil:** Cada letra de a a g tem seu resultado: a (endpoints mapeados), b (esquema relacional), c (coleta de 41.063 partidas e 99.259 jogos), d (viés de lado), e (comparação de modelos), f (seis telas) e g (181 de 203). A Seção 6 lista cada objetivo com a evidência.

### 138. Qual o achado de destaque e por que?

**Resposta:** O viés de lado, por não ter sido o objeto anunciado: assimetria estrutural, firme em três das quatro regiões, com sinal invertido no profissional.

**Onde achar no TCC:** Seção 6.

**Explicando fácil:** O trabalho não foi montado para estudar o lado do mapa, mas isso apareceu ao explorar os dados. Ele é um fator de confusão que qualquer modelo sobre solo queue precisa controlar, e a inversão no profissional sugere que a origem é diferente. O TCC delimita a hipótese sem comprová-la.

### 139. Quais as limitações do trabalho (validade de construto, externa, interna)?

**Resposta:** Construto: a API não registra ondas de minions nem draft. Externa: só elo alto, cinco regiões e patch 16.13 com 40,4% da coleta. Interna: coleta em janelas de tempo e dobras menos independentes por jogadores repetidos.

**Onde achar no TCC:** Seção 6.1; Seção 6.1.

**Explicando fácil:** Construto é ‘estou medindo o que acho que meço?’ (faltam dados importantes). Externa é ‘vale para outros casos?’ (só para este recorte). Interna é ‘o desenho do estudo sustenta o resultado?’ (coleta em janelas, jogadores repetidos). O TCC diz que nenhuma delas invalida os achados, mas delimita até onde valem.

### 140. Por que ‘que parte do erro do modelo venha da informação ausente é hipótese’?

**Resposta:** Porque o TCC mediu que variáveis novas dão ganho pequeno, mas não mediu o efeito do draft e das ondas de minions, que a fonte não tem.

**Onde achar no TCC:** Seção 6.1.

**Explicando fácil:** O TCC suspeita que o erro restante vem do que a API não dá (ordem do draft, ondas), mas não pode provar sem esses dados. Por isso diz ‘hipótese, não resultado medido’.

### 141. O XGBoost não garante monotonicidade. O que isso significa?

**Resposta:** Aumentar apenas a diferença de abates ou de torres pode, por interações e redundâncias entre variáveis, não aumentar sempre a probabilidade prevista; não há restrição formal (monotone_constraints).

**Onde achar no TCC:** Seção 6.1; Seção 6.1.

**Explicando fácil:** Esperamos que mais abates sempre aumente a chance do azul. O modelo não garante isso em cada ponto, porque as variáveis andam juntas (quem tem mais abates costuma ter mais ouro). É um comportamento documentado e compreendido, sem regra imposta.

### 142. As dobras da validação cruzada são independentes?

**Resposta:** Menos do que a técnica supõe, porque jogadores se repetem entre partidas; treinar no passado e testar no futuro só reduziu a AUC em um caso (−0,0026, dentro do intervalo).

**Onde achar no TCC:** Seção 6.1; Apêndice C.

**Explicando fácil:** A validação cruzada sorteia partidas ao acaso; se o mesmo jogador aparece em treino e teste, as partidas deixam de ser totalmente independentes entre treino e teste (dependência amostral), o que não é o mesmo que vazamento de dados. O TCC mediu a consequência com o treino no passado e o teste no futuro, e a queda foi mínima.

### 143. Recortes finos (um jogador num campeão) são confiáveis?

**Resposta:** Não: seguem frágeis mesmo com 41.063 partidas, apesar do encolhimento estatístico (shrinkage) em direção à média.

**Onde achar no TCC:** Seção 6.1.

**Explicando fácil:** Um jogador com 3 partidas de um campeão não tem taxa de 100% de verdade: com poucos casos o acaso pesa muito. Shrinkage puxa a taxa dele para a média conforme o número de partidas. Mesmo assim, recortes muito finos continuam frágeis.

### 144. Qual a validade da consulta em linguagem natural?

**Resposta:** A medida principal pode superestimar o resultado em perguntas livres: em versões anteriores, dois conjuntos de 50 perguntas escritas à mão acertaram 27 e 30 (54% e 60%); as correções posteriores não foram medidas e o benchmark de 26 não é independente.

**Onde achar no TCC:** Seção 6.1.

**Explicando fácil:** É o ponto mais sensível da banca. Os 89,2% são de perguntas de molde; perguntas livres, em versões antigas, acertaram bem menos. O TCC declara isso, e seu trabalho futuro propõe um gabarito maior com perguntas escritas à mão.

### 145. Quais são os trabalhos futuros?

**Resposta:** (1) Previsão ao vivo, prevista na arquitetura mas não implementada (a barreira é de dados em tempo real); (2) validade externa (outras filas e outro jogo); (3) melhoria da consulta em linguagem natural (verificação pós-execução, gabarito maior, vários bancos de teste, modelo aberto local).

**Onde achar no TCC:** Seção 6.2.

**Explicando fácil:** Três caminhos: prever durante a partida, estender a outras filas e jogos, e melhorar o text-to-SQL. A previsão ao vivo exigiria um feed de dados em tempo real que a API pública não oferece com a mesma riqueza. Dizer que a barreira é de dados, e não de modelo, é uma frase importante do TCC.

### 146. Se você pudesse refazer algo, o que seria?

**Resposta:** O TCC não responde diretamente; os trabalhos futuros e as limitações apontam o gabarito escrito à mão, a previsão ao vivo e outras filas.

**Onde achar no TCC:** Seção 6.1 e 6.2.

**Explicando fácil:** Pergunta de opinião: monte sua resposta com o que já está no TCC. Por exemplo: ‘eu faria um gabarito maior com perguntas escritas à mão, porque é o ponto em que o resultado pode estar superestimado’. Escolher uma limitação real e propor o próximo passo mostra maturidade.

### 147. Qual a contribuição do trabalho em três minutos?

**Resposta:** Integração completa numa plataforma, medição com número e limite, achado do viés de lado (solo queue × profissional) e interface em linguagem natural mensurável.

**Onde achar no TCC:** Seções 3.6, 5 e 6.

**Explicando fácil:** Roteiro: (1) problema: ferramentas fragmentadas; (2) solução: plataforma que coleta, prevê, explica, visualiza e responde em português; (3) resultado: AUC por volta de 0,85 aos 15 minutos, modelos empatados, limite nas variáveis, e 89,2% na consulta em perguntas de molde; (4) achado: viés de lado se inverte; (5) limites: dado ausente, perguntas livres, recorte de elo alto.

---

## Apêndices e itens cortados

> Em 23/11/2026 o TCC foi simplificado: de 11 apêndices (cerca de 32 páginas) para 4 (cerca de 9 páginas). Estas perguntas cobrem o que ficou e o que saiu. O texto da versão anterior continua no repositório (histórico do git, commit `f2ecb39`) e em `bellestraiko_v2/03_tcc_texto_v2.md` está o texto novo.

### 148. O que o Apêndice A traz?

**Resposta:** O esquema relacional do banco (Quadro 4): tabelas, campos e chaves.

**Onde achar no TCC:** Apêndice A.

**Explicando fácil:** É o ‘mapa do banco’: lista cada tabela, seus campos e as chaves primárias e estrangeiras. Serve para explicar como os dados se ligam. As tabelas raw_ guardam o JSON original; as demais são a versão relacional usada nas análises. O arquivo que cria essas tabelas é `db/schema.sql`.

### 149. O que o Apêndice B traz?

**Resposta:** A medida principal da consulta em linguagem natural (gabarito de 203 perguntas: 181 certas, 166 de 187 respondíveis e 15 de 16 recusas), as versões do modelo de linguagem e o congelamento dos dados, e a auditoria do coach (36 respostas, Quadro 5).

**Onde achar no TCC:** Apêndice B (Quadro 5).

**Explicando fácil:** É o ‘boletim’ da parte de IA. Saíram do TCC o benchmark de 26 perguntas, a tabela de execuções e o acerto por família de pergunta, porque o benchmark de 26 não é independente (chegou a 26 de 26 depois de ajustes feitos conhecendo as três falhas). O resultado que vale é o do gabarito de 203.

### 150. O que o Apêndice C traz?

**Resposta:** Métricas completas dos três modelos nos quatro cortes (Quadro 6), configuração dos modelos (Quadro 7), treino no passado e teste no futuro (Quadro 8), AUC-ROC por corte nas mesmas partidas (Quadro 9) e a calibração do modelo de produção (Quadro 10 e Figura 5).

**Onde achar no TCC:** Apêndice C (Quadros 6 a 10; Figura 5).

**Explicando fácil:** É a ‘casa de máquinas’ da modelagem. Se a banca duvidar de um número da Seção 5.4, a evidência principal está aqui. Saíram a tabela da regressão logística contra o XGBoost, a de 5 contra 10 dobras e a curva de aprendizado; os números principais delas continuam em frases da Seção 5.4 e os arquivos estão no repositório.

### 151. O que o Apêndice D traz?

**Resposta:** A origem das imagens (Data Dragon e Community Dragon) e o aviso exigido pela política da Riot Games: o Bellestraiko não é endossado pela Riot.

**Onde achar no TCC:** Apêndice D.

**Explicando fácil:** É o crédito legal das imagens do jogo que aparecem na Figura 3. Os ícones, o mapa e as ilustrações são propriedade da Riot.

### 152. Por que os experimentos de precisão não estão detalhados no TCC?

**Resposta:** O TCC cita que foram feitos 19 experimentos, lista os tipos de variável testados e dá o maior ganho (+0,0044 de AUC-ROC no XGBoost e +0,0073 na regressão logística aos 15 minutos); os quadros completos saíram para não alongar o trabalho. Os resultados estão em `reports/experimentos_precisao.json` e `reports/experimentos_antigos.json`.

**Onde achar no TCC:** Seção 5.4 (parágrafo ‘Experimentos de enriquecimento’); Seção 6.1.

**Explicando fácil:** Foi uma decisão de enxugar: nenhum experimento mudou o modelo de produção, então o TCC dá o resultado em uma frase. Se a banca perguntar por um experimento específico, a resposta honesta é o número do repositório. Não diga que ‘não ajudaram’: ajudaram pouco (+0,0044 contra uma AUC de 0,8487), e isso é o que o TCC afirma.

### 153. Por que o benchmark de 26 perguntas saiu do TCC?

**Resposta:** Porque não é independente: foi ajustado depois de conhecer as três falhas (23 de 26 antes, 26 de 26 depois). A medida principal é o gabarito de 203, escrito com a SQL de referência antes de executar.

**Onde achar no TCC:** Seção 5.6; Seção 6.1 (validade da consulta em linguagem natural); Apêndice B.

**Explicando fácil:** É como mostrar a nota de uma prova que você refez depois de ver o gabarito. Ela não prova nada. Por isso o TCC só usa a prova nova, de 203 questões.

### 154. Por que não há mais um apêndice com as telas completas?

**Resposta:** As Figuras 1, 3 e 4 do corpo já mostram a plataforma (Competitivo, análise de partida e simulador). As seis capturas de página inteira estão em `reports/anexo_a/` e podem ser mostradas na defesa.

**Onde achar no TCC:** Seção 5.5 (Figuras 3 e 4); Seção 5.3 (Figura 1).

**Explicando fácil:** Seis páginas de captura de tela pesavam mais que todo o resto do apêndice e não acrescentavam resultado. A demonstração ao vivo (ou as capturas) cobre isso.

### 155. Onde estão agora os números e quadros que saíram do TCC?

**Resposta:** Todos continuam em `reports/*.json` (artefatos que geraram cada número), nos scripts de `src/models/` e `docs/`, e no texto anterior do TCC (histórico do git).

**Onde achar no TCC:** Não estão no TCC; ver `bellestraiko_v2/02_o_que_foi_cortado_e_onde_esta.md`.

**Explicando fácil:** Nada foi apagado do projeto; só deixou de ocupar página. O TCC diz onde está o código no repositório.

### 156. Por que o TCC tem só 4 apêndices e a comparação com os colegas?

**Resposta:** Nos TCCs aprovados lidos (medido nos PDFs de exemplo, não é norma) o total é de 32 a 41 páginas; quatro não têm apêndice e o máximo é 5 páginas de apêndice. O corpo do TCC tem 28 páginas (faixa de 25 a 30) e os 4 apêndices somam cerca de 9; o documento todo tem 39.

**Onde achar no TCC:** Estrutura do documento; diário de execução (outubro de 2026).

**Explicando fácil:** O foco ficou no que responde à questão de pesquisa. O modelo da UNISINOS não obriga apêndices, e os do TCC servem à rastreabilidade das medidas principais.

### 157. Se a banca perguntar por algo que saiu (benchmark de 26, experimento específico, série anual, composição das ligas), como responder?

**Resposta:** Reconhecer que saiu do texto para enxugar, dar o número principal (está neste guia e nos artefatos) e dizer onde está no repositório.

**Onde achar no TCC:** Ver `02_o_que_foi_cortado_e_onde_esta.md`, que lista cada item cortado com o arquivo de origem.

**Explicando fácil:** Exemplo de resposta: ‘essa medição foi feita (resultado: X); ela saiu do texto por não alterar a conclusão, e o arquivo está em reports/. Posso abrir agora.’ Evita dizer que não foi feito.

---

## Perguntas transversais (cruzam várias seções)

### 158. Os resultados são generalizáveis?

**Resposta:** Não além do recorte: solo queue ranqueado de Desafiante a Mestre, cinco regiões (quatro com amostra suficiente) e patches 16.10 a 16.19; o profissional serve só para comparar.

**Onde achar no TCC:** Seção 6.1 (validade externa).

**Explicando fácil:** Generalizar é ‘vale para outros casos?’. Aqui vale para o recorte estudado. Não há base para estender as taxas por lado nem a acurácia a outras filas, elos, versões ou outros jogos, ainda que a arquitetura seja reaproveitável.

### 159. Por que não usar deep learning ou modelos mais modernos?

**Resposta:** O TCC compara uma rede MLP e mostra que, com 5 variáveis tabulares, os modelos empatam; isso sugere que o limite está na informação das variáveis, e não que nenhuma outra arquitetura possa ganhar.

**Onde achar no TCC:** Seção 2.2; Seção 5.4.

**Explicando fácil:** Com poucas variáveis e dezenas de milhares de partidas, árvores e redes pequenas já extraem quase tudo (Grinsztajn et al.). Modelos maiores não criam informação que não está nos dados. Leitura minha: o TCC não testou redes profundas; testou uma MLP simples.

### 160. Por que o limiar de 50% para a acurácia?

**Resposta:** A acurácia usa o limiar padrão de 0,5 sobre a probabilidade; por depender dele, ela é reportada junto da AUC-ROC, que cobre todos os limiares.

**Onde achar no TCC:** Seção 2.3.

**Explicando fácil:** Decidir ‘azul vence’ quando a probabilidade passa de 50% é uma escolha; outro limiar mudaria a acurácia. A AUC-ROC não depende disso, e por isso as duas medidas andam juntas.

### 161. O que é overfitting e como o trabalho se protege dele?

**Resposta:** É ir bem no treino e mal em dados novos; o TCC usa validação cruzada, seleção aninhada, treino no passado e teste no futuro e profundidade baixa no XGBoost de produção.

**Onde achar no TCC:** Seção 4.6; Apêndice C (Quadro 8).

**Explicando fácil:** Overfitting é decorar o gabarito. As proteções: (1) sempre medir em partidas que o modelo não viu no treino, (2) escolher os parâmetros só dentro do treino (aninhada), (3) testar em partidas mais novas, (4) usar árvores curtas (profundidade 3).

### 162. O que acontece se a Riot mudar a API ou o jogo mudar de patch?

**Resposta:** O TCC não testa mudança de API. Sobre patches: treinar nos patches 16.10 a 16.13 e testar nos 16.14 a 16.19 não reduz a AUC-ROC; a generalização para versões com balanceamento muito diferente segue sem medida.

**Onde achar no TCC:** Seção 6.1; Apêndice C (Quadro 8, treino no passado e teste no futuro).

**Explicando fácil:** Se a API mudar, o coletor e o ETL precisam de ajuste (não foi medido). Se o jogo mudar de patch, o modelo pode envelhecer; nos patches testados, não houve queda. Para um balanceamento muito diferente, o TCC não afirma nada.

### 163. Há dados pessoais ou questões de privacidade?

**Resposta:** Os dados são secundários e públicos, sem sujeitos humanos como fonte; a tabela players guarda identificadores da própria API pública.

**Onde achar no TCC:** Seção 4.3.

**Explicando fácil:** O TCC trata de dados públicos obtidos da API oficial. Os identificadores (puuid, nome e tag) vêm da API. O TCC declara apenas que são públicos e secundários. Em caso de pergunta sobre LGPD, a resposta segura é essa; evite afirmar algo além disso.

### 164. Como o trabalho lida com a Riot (direitos, termos de uso)?

**Resposta:** As imagens de itens vêm do Data Dragon (da Riot); ícones e arte dos campeões e o mapa vêm do Community Dragon; as imagens são propriedade da Riot Games, e o TCC credita a origem.

**Onde achar no TCC:** Apêndice D (origem das imagens e aviso da Riot).

**Explicando fácil:** O TCC declara que as telas mostram ícones e ilustrações do jogo, que são propriedade da Riot, e informa de onde vêm. Os dados vêm da API oficial, dentro do limite da chave de desenvolvedor.

### 165. Onde entra a inteligência artificial no seu trabalho, e é diferente do uso de IA para escrever o TCC?

**Resposta:** Na plataforma, o Claude (Anthropic) faz a tradução da pergunta em SQL, o roteamento no resíduo, a explicação do resultado e o coach. O uso de IA como apoio ao desenvolvimento é um assunto à parte.

**Onde achar no TCC:** Seção 4.7; Seção 4.8; Apêndice B.

**Explicando fácil:** Duas coisas diferentes: (1) a IA que é parte do produto e está descrita e medida no TCC (Claude Haiku 4.5, com temperatura e limite de tokens por etapa); (2) a IA usada como ferramenta de apoio na elaboração. A segunda tem registro próprio e você precisa respondê-la com suas palavras: o que escreveu, o que a IA escreveu e como validou.

### 166. Por que as respostas do coach não são determinísticas e isso é um problema?

**Resposta:** O coach usa temperatura 0,4 (0,2 na releitura dos itens); a saída varia entre execuções, e a auditoria de 36 respostas confere só números, e não afirmações qualitativas.

**Onde achar no TCC:** Seção 4.7; Apêndice B.

**Explicando fácil:** Temperatura é o grau de ‘criatividade’ do modelo de linguagem: 0 é sempre igual, valores maiores variam. O coach precisa escrever texto natural, então tem alguma variação. O controle de qualidade é a auditoria de números e a separação entre dado real e conhecimento geral. A correção qualitativa não foi avaliada, e o TCC diz isso.

### 167. O que mais contribui para a previsão, e isso é causal?

**Resposta:** Ouro e experiência dominam em todos os cortes; o SHAP explica o modelo e não o jogo.

**Onde achar no TCC:** Seção 5.4 (Figura 2); valores por corte: só no repositório (`reports/shap_importance_phases.json`).

**Explicando fácil:** Ouro e XP pesam muito porque, num momento dado, quem está à frente nelas costuma ganhar. Mas o SHAP diz o que pesou na conta do modelo, e não que ouro ‘cause’ vitória. Pode ser que um time melhor ganhe mais ouro e também mais partidas.

### 168. Por que o limite do TCC é 25 a 30 páginas e o seu tem apêndices extensos?

**Resposta:** O limite de 25 a 30 páginas vale para o corpo, sem contar apêndices e anexos, por acordo com o orientador (os modelos da UNISINOS lidos não trazem esse número).

**Onde achar no TCC:** Diário de execução (outubro de 2026).

**Explicando fácil:** Os apêndices guardam a prova detalhada sem pesar no corpo. O corpo tem 28 páginas e os apêndices, cerca de 9. Se a banca perguntar, a resposta é que o limite se aplica ao corpo, e os apêndices cumprem o papel de rastreabilidade dos números.

### 169. Qual foi a maior dificuldade do trabalho?

**Resposta:** O TCC não responde diretamente; os registros mostram, por exemplo, o vazamento do quadro final (achado e corrigido em 8/11) e a conferência dos próprios números (a conversão de vantagem do profissional, corrigida em 17/11).

**Onde achar no TCC:** Seção 4.6 (vazamento); diário de execução.

**Explicando fácil:** Esta é pergunta pessoal: conte a que você viveu. Duas opções sustentadas pelo repositório: (a) impedir que o modelo visse o futuro da partida; (b) conferir cada número contra o banco e achar um erro de definição. Diga o que tentou, o que errou e o que aprendeu.

### 170. Se o modelo erra, em que tipos de partida ele erra mais?

**Resposta:** O TCC não mede isso por tipo de partida; mede por corte e mostra que aos 10 minutos a AUC é 0,775 e aos 25 é 0,890.

**Onde achar no TCC:** Seção 5.4.

**Explicando fácil:** Esta pergunta vai além do que foi medido. O que se sabe: mais cedo, menos informação, menos acerto. Quanto a tipos de partida (por exemplo, viradas tardias), o TCC não tem análise. Responda isso com franqueza e cite como possível extensão.

### 171. O que você faria com mais tempo?

**Resposta:** Os trabalhos futuros: previsão ao vivo, outras filas e outro jogo, e melhoria da consulta em linguagem natural (gabarito escrito à mão, verificação pós-execução, vários bancos de teste, modelo aberto local).

**Onde achar no TCC:** Seção 6.2.

**Explicando fácil:** A resposta está pronta no TCC. Escolha a que mais lhe interessa e explique por quê. Por exemplo: ‘um gabarito escrito à mão, porque é onde meu resultado pode estar superestimado’.
