# Guia de estudo para a banca — Bellestraiko (TCC II)

> Para que serve: entender o projeto inteiro, do porquê de cada decisão até
> de onde veio cada número, para conseguir responder qualquer pergunta da
> banca com segurança. Linguagem simples, exemplos reais do próprio projeto.
>
> Regra de ouro deste guia: **todo número aqui vem do texto final do TCC
> (`docs/tcc2_texto.md`) ou de um artefato real em `reports/`.** Se a banca
> perguntar "de onde saiu isso?", sempre existe um arquivo que prova.
>
> Como estudar: leia a Parte 1 primeiro (o projeto em 5 minutos). Depois vá
> nas partes que você sente mais fraco. A Parte 15 (perguntas prováveis da
> banca) é para treinar em voz alta.

---

## Sumário

1. O projeto em 5 minutos
2. League of Legends para quem nunca jogou (você vai precisar explicar)
3. O problema, a pergunta de pesquisa e os objetivos
4. Metodologia de pesquisa e pesquisa bibliográfica
5. Os trabalhos relacionados (os 11 estudos), como foram escolhidos, e as obras de método
6. Os dados: de onde vieram e como foram coletados
7. O banco de dados e o tratamento (ETL)
8. As *features*: o que o modelo enxerga
9. Os três modelos: Random Forest, XGBoost e MLP
10. Como os modelos foram avaliados (métricas)
11. Explicabilidade: SHAP
12. Os 11 experimentos que não funcionaram (e por que isso é bom)
13. A análise exploratória: o viés de lado
14. A interface em linguagem natural (text-to-SQL)
15. Perguntas prováveis da banca, com respostas
16. A plataforma (o sistema que foi entregue)
17. Testes e verificações de qualidade
18. Limitações e trabalhos futuros
19. Histórias reais de erros encontrados e corrigidos
20. Sobre o uso de IA no trabalho
21. Folha de cola: os números para decorar

---

## 1. O projeto em 5 minutos

**O Resumo do TCC (versão de 2026-11-02) segue a ordem contexto,
objetivo, metodologia, resultados e conclusão.** Use a mesma ordem no
pitch: (1) esports geram muitos dados, mas explorar exige ferramentas
fragmentadas e conhecimento técnico; (2) desenvolvi uma plataforma que
junta coleta, predição, explicação, visualização e consulta em português;
(3) pesquisa aplicada, mista, sobre 41.063 partidas e 99.259 jogos
profissionais, com três modelos comparados por validação cruzada
estratificada; (4) empate técnico entre os três, XGBoost adotado com 76% e
AUC de 0,85 aos 15 minutos, viés do vermelho que se inverte no
profissional, 89,2% de acerto (181 de 203) no gabarito automático da consulta em português (60% e 54% nos conjuntos anteriores, julgados à mão); (5) dá para integrar tudo numa
solução só.

**Em uma frase:** foi construída uma plataforma (chamada **Bellestraiko**)
que coleta dados reais de partidas de *League of Legends*, organiza tudo
num banco de dados, usa *machine learning* para estimar quem vai vencer uma
partida olhando o estado do jogo num minuto específico, explica o porquê da
previsão, e deixa o usuário fazer perguntas em português sobre os dados.

**O problema:** existem muitos dados de partidas de esports, mas explorar
esses dados normalmente exige saber programar, saber SQL, juntar
ferramentas separadas. Quem não é técnico fica de fora.

**A solução:** uma plataforma só que junta seis coisas:
coleta → organização → modelagem preditiva → explicabilidade →
visualização (*dashboards*) → consulta em linguagem natural.

**Os resultados principais (decore estes):**

| O quê | Número |
|---|---|
| Partidas ranqueadas coletadas (solo queue) | **41.063** (5 regiões) |
| Partidas profissionais incorporadas | **99.259** (2014-2026) |
| Modelo adotado (os três empataram) | **XGBoost** |
| Acurácia aos 15 minutos | **0,7621** (≈ 76 de cada 100 partidas certas) |
| AUC-ROC aos 15 minutos | **0,8473** |
| Viés de lado no solo queue | vermelho vence mais (56,3% na BR1) |
| Viés de lado no profissional | **inverte**: azul vence 53,2% |
| Interface em linguagem natural | **89,2%** (181 de 203) no gabarito automático, comparado por código; 60% e 54% em dois conjuntos de 50 julgados à mão; 26 de 26 no *benchmark* de referência, que não é independente |
| Páginas de visualização | 6 |

**O achado mais interessante** (e que não era o objetivo inicial): no
*solo queue* de elo altíssimo, o time **vermelho** vence mais vezes que o
azul. No cenário profissional acontece o **contrário**: o azul vence mais.
A mesma métrica, em dois contextos, dá sinais opostos.

---

## 2. League of Legends para quem nunca jogou

A banca pode não conhecer o jogo. Você precisa explicar o básico em
poucas frases, sem jargão.

**O jogo:** duas equipes de 5 jogadores (time **azul** e time
**vermelho**) num mapa. Cada lado tem uma base. Ganha quem destruir a
base do outro. Uma partida dura em média uns 26 minutos.

**Termos que aparecem no TCC:**

| Termo | O que é, em palavras simples |
|---|---|
| **Campeão** | O personagem que cada jogador controla. Há mais de 160. |
| **Ouro (*gold*)** | Dinheiro do jogo. Ganha matando inimigos e "minions". Compra itens que deixam o campeão mais forte. |
| **Experiência (XP)** | Sobe o nível do campeão, deixando-o mais forte. |
| **Abate (*kill*)** | Matar um campeão inimigo. Dá ouro. |
| **Torre** | Estruturas de defesa no caminho até a base. Destruir torres abre o mapa. |
| **Placa de torre** | "Pedaços" da torre que dão ouro extra. Caem (somem) aos 14 minutos. |
| **Dragão / Barão / Arauto** | Monstros neutros que dão bônus a quem matar. |
| **Minion / onda (*wave*)** | Soldadinhos que andam sozinhos pelas rotas. A posição das ondas importa muito para jogadores experientes, mas a Riot **não grava** isso. |
| ***Solo queue*** | A fila ranqueada: jogadores entram sozinhos (ou em dupla) e o jogo monta times com desconhecidos. Fila 420 na API. |
| **Elo** | O nível/ranking do jogador. Do mais baixo ao mais alto: Ferro... até Mestre, **Grão-Mestre** e **Desafiante** (os topos). |
| **Elo alto** | Neste TCC: Desafiante e Grão-Mestre, o topo do topo de cada região. Escolhido **por escopo** (confirmado por você em 2026-11-02): ver Parte 6.1. |
| ***Draft* / seleção de campeões** | A fase antes do jogo em que cada time escolhe e bane campeões, alternadamente. |
| ***Counter-pick*** | Escolher um campeão que é forte contra o que o inimigo já escolheu. Quem escolhe por último tem essa vantagem. |
| ***Patch*** | Atualização do jogo que muda o balanceamento (ex.: 16.13). |
| **Região** | Servidor: BR1 (Brasil), EUW1 (Europa Oeste), KR (Coreia), NA1 (América do Norte), EUN1 (Europa Nórdica e Leste). |

**Exemplo para explicar a predição:** "Imagine que você está assistindo
um jogo de futebol aos 60 minutos e o placar está 2 a 0. Você não sabe
quem vai ganhar, mas consegue chutar com boa chance. O nosso modelo faz
isso com *League of Legends*: olha o 'placar' aos 15 minutos (ouro,
experiência, abates, torres, dragões) e estima a chance de cada time
vencer."

---

## 3. O problema, a pergunta de pesquisa e os objetivos

### A pergunta de pesquisa (Seção 1.3)

> Como desenvolver uma plataforma inteligente para análise de dados de
> *League of Legends* que integre coleta, organização, modelagem
> preditiva, visualização e consulta em linguagem natural para apoiar a
> interpretação de informações competitivas?

### Objetivo geral

Desenvolver essa plataforma.

### Objetivos específicos (a até g) e onde cada um foi cumprido

Decore esta tabela. A banca adora perguntar "o objetivo X foi
cumprido? onde?".

| Objetivo | O que pede | Onde está o resultado | Resposta curta |
|---|---|---|---|
| **a** | Mapear dados e recursos da Riot API | Seção 5.1 | Usados 4 endpoints: league-v4, account-v1, match-v5 (partida e linha do tempo) |
| **b** | Identificar quais informações organizar | Seção 5.2 | Quadro 1 (tabelas do banco) e esquema completo no Apêndice A |
| **c** | Estruturar coleta e tratamento | Seção 5.2 | Coletor resumível, 41.063 partidas |
| **d** | Avaliar análise de dados para achar padrões | Seção 5.3 | Viés de lado, conversão de vantagem |
| **e** | Comparar XGBoost, Random Forest e redes neurais | Seção 5.4 | Empate técnico; XGBoost adotado: 0,7621 / 0,8473 |
| **f** | Propor *dashboards* | Seção 5.5 | 6 páginas de visualização |
| **g** | Propor interface em linguagem natural | Seção 5.6 | 181 de 203 (89,2%) no gabarito automático; 60% e 54% nos conjuntos de 50 anteriores; 26/26 no *benchmark* ajustado |

**De onde vieram esses objetivos:** foram definidos no **TCC I**. O TCC II
executou o que o TCC I prometeu, e foi além (adicionou os dados
profissionais do Oracle's Elixir, que não estavam no plano original).

### Delimitação (o que o trabalho NÃO faz)

- Só *League of Legends* (não outros jogos).
- Predição só com informação **até o minuto do corte** (nada do futuro).
- Não cobre todas as técnicas de IA possíveis, só as três comparadas.

---

## 4. Metodologia de pesquisa e pesquisa bibliográfica

Esta parte é a que alunos de computação costumam saber menos. A banca
pode perguntar "que tipo de pesquisa é a sua?". Aqui está tudo.

### 4.1 Classificações da pesquisa (Seção 4.1)

Toda pesquisa acadêmica é classificada em algumas "caixinhas". O TCC
classificou assim:

**Quanto à natureza: pesquisa aplicada** (Prodanov e Freitas, 2013)
- **O que é:** pesquisa que busca resolver um problema prático e
  específico, gerando algo que pode ser usado. O oposto é a "pesquisa
  básica", que busca conhecimento puro sem aplicação imediata.
- **Por que é a sua:** você construiu uma plataforma funcionando, que
  resolve o problema de explorar dados de esports.
- **Exemplo simples:** estudar "como neurônios aprendem" é básica;
  construir um app que prevê vitória é aplicada.

**Quanto aos objetivos: exploratória e descritiva** (Gil, 2002)
- **Exploratória:** quando você investiga algo pouco conhecido para se
  familiarizar. No seu caso: investigar o que a Riot API oferece e quais
  modelos faziam sentido.
- **Descritiva:** quando você descreve características de algo. No seu
  caso: descrever os dados coletados, os padrões encontrados (viés de
  lado) e o desempenho dos modelos.

**Quanto à abordagem: quantitativa** (Creswell e Creswell, 2023)
- **Quantitativa:** trabalha com números e estatística. Aqui: coleta,
  análise exploratória, métricas e comparação dos modelos.
- **Mista** (o que o TCC dizia até 2026-11-03): o livro define como coletar
  E integrar dados quantitativos e qualitativos, em um desenho específico.
  O TCC não coleta dado qualitativo (sem entrevistas, questionários ou
  documentos analisados como dado); a revisão bibliográfica e a
  interpretação dos achados dão contexto, mas não são coleta. Por isso o
  texto passou a dizer "predominantemente quantitativa".
- **Se a banca perguntar "por que não mista, como no TCC I?":** "o rótulo
  foi revisto contra a definição de Creswell e Creswell (2023), cap. 1; sem
  coleta qualitativa, o trabalho é quantitativo."

### 4.2 Estratégias de pesquisa (Seção 4.2)

São os "procedimentos" usados:

| Estratégia | O que é | Como apareceu no TCC | Referência |
|---|---|---|---|
| **Pesquisa bibliográfica** | Estudar o que já foi publicado (artigos, livros) | Os 11 estudos de domínio e as 15 obras de método | Gil (2002) |
| **Pesquisa documental** | Estudar documentos que não são artigos científicos (manuais, documentação técnica) | A documentação oficial da Riot Games API (Anexo A) | Prodanov e Freitas (2013) |
| **Aplicação delimitada a um domínio** | Não é estratégia nomeada por Yin: o estudo se restringe ao domínio de *League of Legends* | A plataforma e os modelos valem para esse jogo | (sem citação) |

**Diferença entre bibliográfica e documental (pergunta clássica):**
bibliográfica usa material que já passou por análise de outros autores
(artigos, livros). Documental usa material "bruto", que ainda não foi
analisado academicamente (a documentação da API da Riot é um documento
técnico, não um artigo).

**Por que Yin (2018) saiu:** a definição dele de estudo de caso exige
muito mais variáveis do que pontos de dados, proposições teóricas prévias
e fontes de evidência que convergem. O TCC tem dezenas de milhares de
partidas e cinco variáveis, e as duas fontes são complementares, não
convergentes. A referência foi removida (agora 31).

### 4.3 Como a pesquisa bibliográfica foi feita (de verdade)

**Isto você precisa saber contar com suas palavras.**

No TCC I, foi feito um levantamento de artigos em quatro áreas
(está registrado em `Downloads/TCC/Pesquisa artigos TCC.pdf`):

1. Esports / *Game Analytics*
2. *Machine Learning* aplicado
3. Interfaces em linguagem natural e LLMs
4. Sistemas e plataformas de dados

Os artigos (publicados principalmente entre 2018 e 2025) foram
**triados pelo título e pelo resumo**, avaliando a afinidade com o
projeto. Desse levantamento, **5 dos 7 estudos de domínio originais do
TCC vieram de lá** (os outros 4 estudos de LoL e as 14 referências novas
foram acrescentados em 2026-10-20, por pesquisa na web; ver Parte 5.1):

| Estudo no TCC | Estava no levantamento inicial? |
|---|---|
| García-Méndez e Arriba-Pérez (2025) | Sim |
| Hodge et al. (2021) | Sim |
| Bahrololloomi et al. (2022) | Sim |
| Guo et al. (2024) — Talk2Data | Sim |
| Jiang et al. (2025) — SiriusBI | Sim |
| Birant e Birant (2023) | Não aparece nesse PDF |
| Wallner, Wang e Dormann (2023) | Não aparece nesse PDF |

Alguns artigos do levantamento **ficaram de fora** do TCC final
(rastreamento óptico de 2018, tese de Aalto sobre *win probability*,
Honor of Kings, player2vec, Chat2Data). Motivo razoável para dizer à
banca: ou eram de outro jogo, ou tratavam de técnicas que o projeto não
usou (deep learning temporal, RAG), ou eram de 2018 e fugiam da regra de
recência.

**Atenção, seja honesto:** esse PDF de levantamento foi gerado com
ajuda do ChatGPT (aparece no cabeçalho do arquivo). Ver a Parte 20.
Confira também nas suas anotações de onde vieram Birant e Birant e
Wallner et al., para responder com segurança se perguntarem.

### 4.4 A regra dos "5 anos"

O modelo do professor pede **referências até 5 anos antes do TCC**
(ou seja, de 2021 em diante). Os 11 estudos de domínio são todos de
2021 a 2026. ✔

**Mas há referências antigas** (Breiman 2001, Hanley e McNeil 1982,
Chen e Guestrin 2016...). **Por quê?** Porque são as **obras originais
das técnicas**. Se você usa Random Forest, a regra acadêmica é citar
quem inventou o Random Forest, que é Breiman em 2001. Não existe
"versão de 2024" do artigo original. A regra dos 5 anos vale para o
estado da arte do **tema** (esports, LoL), não para a origem de um
método clássico.

**Resposta pronta:** "As referências antigas são as obras originais
dos métodos utilizados, citadas pela propriedade técnica. Os estudos de
domínio, que representam o estado da arte do tema, são todos de 2021 a
2026."

---

## 5. Os trabalhos relacionados (os 11 estudos), como foram escolhidos, e as obras de método

O TCC separa duas coisas (Seção 3, início):

- **Estudos de domínio** (11): artigos sobre esports/LoL/interfaces.
  Ficam na Seção 3 (Trabalhos Relacionados).
- **Obras de método** (15): artigos que criaram as técnicas usadas.
  Ficam nas Seções 2 e 4.

### 5.1 Os 11 estudos de domínio

Para cada um: o que fizeram, e o que você pegou deles.

**1. Hodge et al. (2021) — "Win prediction in multi-player e-sports: live
professional match prediction"** (IEEE Transactions on Games)
- **O que fizeram:** previram vencedores de partidas **profissionais de
  Dota 2**, **ao vivo**, com *machine learning* padrão, engenharia de
  atributos e otimização.
- **O que você usou:** a ideia de prever vitória a partir do **estado da
  partida** (a "opção B" escrita no topo do `build_features.py`). Mostra
  que o problema é tratável por modelagem estatística.
- **Como você se diferencia:** eles são profissionais e ao vivo; você
  usa *solo queue* de elo alto e um **corte de tempo fixo** (10/15/20/25
  min), o que deixa a pergunta mensurável e comparável entre cortes.
- **Número verificado no resumo do artigo (2026-10-20):** chegam a "até 85%
  de acurácia após 5 minutos de jogo", em **Dota 2**, não em LoL. O TCC
  agora diz isso explicitamente (Seções 3.1 e 5.7). Se a banca perguntar
  "por que o seu é 76% e o dele 85%?": outro jogo, outro nível (profissional)
  e outro momento (5 minutos de uma partida de Dota 2); não são comparáveis
  diretamente.

**2. Birant e Birant (2023) — "Multi-Objective Multi-Instance Learning:
a new approach to machine learning for eSports"** (Entropy)
- **O que fizeram:** propuseram uma técnica de aprendizado e destacaram
  a **modelagem centrada no time** (e não no jogador isolado).
- **O que você usou:** foi **exatamente** a escolha das suas *features*:
  todas são **diferenças entre os dois times** (ouro do azul menos ouro
  do vermelho etc.), não estatísticas de um jogador.

**3. Bahrololloomi et al. (2022) — análise de desempenho de jogadores de
LoL por função (*role*)** (VISIGRAPP 2022)
- **O que fizeram:** caminho oposto: previram vitória a partir das
  **funções e métricas individuais dos jogadores**.
- **O que você usou:** delimita o "outro lado" da escolha. Você usou o
  nível de **time** na predição, e uma noção de nível de **jogador** só na
  camada de perfis de jogador (Seção 5.7).

**4. García-Méndez e Arriba-Pérez (2025) — "Explainable e-sports win
prediction through machine learning classification in streaming"**
(Entertainment Computing)
- **O que fizeram:** predição de vitória **com explicabilidade**, em
  cenário de transmissão.
- **O que você usou:** o argumento de que **uma previsão só é útil se vier
  com explicação**. Isso justificou a camada de SHAP na plataforma.

**5. Jiang et al. (2025) — SiriusBI** (Proceedings of the VLDB Endowment)
- **O que fizeram:** solução de *Business Intelligence* com modelos de
  linguagem (LLM) para analisar dados de empresas.
- **O que você usou:** fundamento para usar LLM como camada de conversa
  sobre dados estruturados (o seu *text-to-SQL*).

**6. Guo et al. (2024) — Talk2Data** (ACM Transactions on Interactive
Intelligent Systems)
- **O que fizeram:** interface em linguagem natural para análise visual,
  que **decompõe perguntas complexas** em perguntas simples.
- **O que você usou:** mesmo fundamento do SiriusBI, para a interface de
  perguntas em português.

**7. Wallner, Wang e Dormann (2023) — visualização espaço-temporal com
*storyline visualization*, estudo com LoL** (ACM PACM HCI / CHI PLAY)
- **O que fizeram:** visualizações que juntam **tempo e posição** no
  mapa para analisar partidas depois que acabam.
- **O que você usou:** referência para o **mapa de calor de
  posicionamento** minuto a minuto da análise de partida.
- **Limitação admitida:** o seu mapa é mais simples (posição agregada por
  minuto), sem a técnica de *storyline* deles.

**Os 4 estudos acrescentados em 2026-10-20 (todos de LoL, Seção 3.2):**

**8. Jadowski e Cunningham (2022)** (ArtsIT, Springer): ajustaram
classificadores estatísticos a métricas das ligas profissionais de 2020 e
acertaram **67% dos 306 jogos da etapa seguinte** (é o que a Seção 3.2 diz).
DOI 10.1007/978-3-030-95531-1_10.

*Lido por inteiro em 2026-10-20.* Treinam com a etapa de primavera de 2020
(882 jogos) e testam na de verão (306), então é previsão **pré-jogo com
divisão no tempo**, em ligas regionais (LEC, LCS, LCK, CBLOL, PCS, TCL), com
regressão logística sobre notas de jogadores: 67,3%. Dados do Oracle's Elixir,
a mesma fonte do TCC. **Três usos para a banca:** (1) mediram vitória do azul de
**54,08% em 882 jogos profissionais** (qui-quadrado p = 0,015), o que apoia o
nosso 53,2%, e citam que em 2017 o azul chegou a 64%; (2) escrevem que
abordagens assim "dificilmente chegam a 90% de acurácia, pela inevitabilidade
de zebras, e que mesmo no fim de uma partida o resultado pode ser muito volátil",
exatamente a resposta à pergunta "por que não 90%?"; (3) usam o Hodge como
exemplo de 85% em **outro MOBA profissional**, o mesmo que o TCC diz.

**9. Do et al. (2021)** (FDG 2021): preveem o resultado da partida
ranqueada **antes de ela começar**, pela experiência de cada jogador com o
campeão, com **75,1%** de acurácia (rede neural profunda). Autores: Do, Wang,
Yu, McMillian e McMahan.

**10. Maymin (2021)** (*Journal of Quantitative Analysis in Sports*):
calibra um modelo de probabilidade de vitória com dados de partidas
ranqueadas e avalia cada ação individual pelo efeito que tem nessa
probabilidade (é o que a Seção 3.2 diz, a partir do resumo, que fala em
milhões de partidas).

*Lido por inteiro em 2026-10-20.* O modelo de probabilidade de vitória dele é
uma regressão logística com minuto, abates, torres e monstros grandes, e
**exclui o ouro de propósito** (diz que a diferença de ouro engana conforme o
jogo avança); o nosso usa ouro e experiência, e o SHAP mostra o ouro como fator
dominante. **Conferido no texto completo em 2026-11-02** (o artigo é de
acesso aberto, CC BY 4.0): o modelo de probabilidade em jogo usa **milhões
de partidas**, com um minuto sorteado de cada partida ("milhões de linhas
independentes"), então o TCC está certo. Os **~150 mil** são outra coisa:
as partidas do último *patch* usadas na análise de desempenho individual
(percentis e a regressão sobre os "pacotes" de estatísticas), das quais
metade é Bronze e menos de 1% é Mestre ou Desafiante, bem diferente do nosso
elo alto. A nota anterior deste guia misturava os dois números.

**Três pontos do Maymin que ajudam na banca:**
1. Ele cita o Hodge e diz que o Hodge treina **um modelo por minuto**,
   enquanto ele preferiu **um modelo único** para todos os minutos. O seu
   trabalho fica no meio: um modelo por **fase** (quatro cortes), e o SHAP
   das torres mostra por que separar fases faz diferença.
2. Ele escreve que, em trabalho exploratório, **acrescentar variáveis não
   melhorou** o modelo de probabilidade. É o mesmo que os seus 11
   experimentos negativos mostraram.
3. Ele sorteia **um minuto por partida** porque linhas seguidas da mesma
   partida são muito correlacionadas. No seu desenho, cada modelo tem uma
   linha por partida (o estado naquele corte), então o problema não aparece
   dentro de um mesmo modelo.

Os
80% de acerto do artigo vêm de uma árvore que prevê o resultado do time pelo
desempenho individual no fim da partida; não é previsão em tempo de jogo e não
é comparável à nossa acurácia.

**11. Guan e Tung (2026)** (*preprint* arXiv:2609.08060, **sem revisão por
pares**, publicado em setembro de 2026): previsão **pré-jogo** no
profissional, que trata o lado do mapa e a prioridade de escolha (*first
pick*) como covariáveis do modelo. Eles não reportam taxa de vitória por
lado (por isso o TCC cita esse artigo só como apoio à hipótese, não como
fonte do 53,2%). Curiosidade útil para a banca: o próprio artigo declara
uso do Claude no código e na revisão do texto.

**Como usar isso numa resposta:** "Comparado com outros trabalhos de LoL
(67% em Jadowski e Cunningham, 75,1% em Do et al.), meus 70% a 82% ficam
na mesma ordem de grandeza. A comparação é indicativa, porque muda o
nível dos jogadores, o momento da previsão e a informação usada."

### 5.2 A lacuna que o TCC ocupa (Seção 3.6)

Cada estudo cobre **uma frente isolada**:
- predição (Hodge, Birant, Bahrololloomi)
- explicabilidade (García-Méndez)
- linguagem natural (Jiang, Guo)
- visualização (Wallner)

**Nenhum** entrega tudo junto numa plataforma só, sobre a mesma base de
dados. **Essa é a lacuna.** O texto final (Seção 3.6) aponta também **três
decisões de projeto** (decore os nomes):

1. **Horizonte da predição:** em vez de um único momento, quatro cortes
   (10, 15, 20, 25 min), com um modelo por corte. Isso torna o desempenho
   comparável ao longo da partida e mostra a importância das variáveis
   mudando de fase para fase.
2. **Recorte de população:** a maior parte dos estudos de predição atua
   sobre o profissional, e os que usam ranqueadas (Do et al.; Maymin) não
   comparam com ele. Você mede o mesmo indicador nos dois contextos e
   mostra a inversão do viés de lado.
3. **Consulta mensurável:** a interface em linguagem natural foi avaliada
   no próprio domínio, com 26 perguntas de referência e um conjunto cego de
   50, ambos conferidos contra o banco, o que torna o erro mensurável, e não
   ilustrativo.

**Atenção:** versões antigas falavam em "quatro eixos", com "fonte de
dados" (eles usam bases de terceiros) e "nenhum mede contra *benchmark*".
Isso saiu do texto porque não estava conferido nos artigos, e porque Do et
al. e Maymin também usam ranqueadas. Não use esses argumentos na banca.

### 5.2.1 Como os trabalhos relacionados foram escolhidos (justificativa)

A banca pode perguntar "por que esses trabalhos e não outros?". A
resposta tem três partes: **de onde vieram**, **com que critério** e **o
papel de cada um**.

**De onde vieram (dois momentos):**

1. **TCC I:** levantamento nas quatro frentes do projeto (esports/*game
   analytics*, *machine learning* aplicado, interfaces em linguagem natural
   e LLMs, sistemas e plataformas de dados), com triagem por título e
   resumo. Daí vieram 5 dos 7 estudos originais (Parte 4.3).
2. **TCC II (2026-10-20):** numa revisão de afirmações sem fonte, as
   lacunas foram fechadas por pesquisa na web (18 → 32 referências). Entre
   elas, quatro estudos **de LoL** (Jadowski e Cunningham, Do et al.,
   Maymin, Guan e Tung), conferidos contra o texto dos artigos. Até ali o
   único estudo de predição com número era o Hodge, de Dota 2; com os
   quatro, a Seção 5.7 passou a comparar a acurácia com trabalhos do mesmo
   jogo (diário de 2026-10-20).

**Critérios de inclusão (diga assim):**

- **Cobrir as frentes da plataforma:** cada estudo sustenta uma camada:
  predição, explicabilidade, linguagem natural ou visualização. É por isso
  que a Seção 3 tem as subseções 3.1 a 3.5, uma por frente.
- **Recência:** o modelo do professor pede referências de até cinco anos;
  os onze são de 2021 a 2026.
- **Afinidade com o problema:** preferência por *League of Legends*; quando
  o estudo é de outro jogo (Hodge, Dota 2) ou de outro domínio (SiriusBI e
  Talk2Data, *Business Intelligence*), ele entra pelo **método**, e o texto
  diz isso.
- **Fonte com revisão por pares,** com uma exceção declarada: Guan e Tung
  (2026) é *preprint*, e por isso é citado só como apoio à hipótese, nunca
  como fonte de número.

**O que ficou de fora:** do levantamento do TCC I não entraram, por
exemplo, Honor of Kings (outro jogo, sem método aproveitado), player2vec e
Chat2Data (técnicas que o projeto não usou: *deep learning* temporal, RAG)
e o rastreamento óptico de 2018 (fora da janela de recência). Esses
motivos são a leitura mais coerente com os critérios acima; não há
registro escrito da exclusão de cada um, então fale em critérios, não em
uma lista de rejeições.

**O papel de cada estudo (uma frase cada):**

| Estudo | Frente | Por que está no TCC |
|---|---|---|
| Hodge et al. (2021) | Predição | Mostra que prever pelo estado da partida é tratável; base da "opção B" |
| Birant e Birant (2023) | Predição | Modelagem centrada no time; origem das *features* como diferenças |
| Bahrololloomi et al. (2022) | Predição | O caminho oposto (por jogador); delimita a escolha e entra nos perfis |
| Jadowski e Cunningham (2022) | Predição (LoL) | Comparação de acurácia (67%) e apoio ao 53,2% do azul (54,08%) |
| Do et al. (2021) | Predição (LoL) | Comparação de acurácia pré-jogo (75,1%) em ranqueadas |
| Maymin (2021) | Predição (LoL) | Modelo de probabilidade em ranqueadas; mostra que ninguém compara com o profissional |
| Guan e Tung (2026) | Predição (LoL) | Lado e prioridade de escolha como covariáveis; apoio à hipótese do *draft* |
| García-Méndez e Arriba-Pérez (2025) | Explicabilidade | "Previsão só é útil com explicação"; justifica o SHAP na tela |
| Jiang et al. (2025) | Linguagem natural | LLM sobre dados estruturados (SiriusBI) |
| Guo et al. (2024) | Linguagem natural | Interface NL com decomposição de perguntas (Talk2Data) |
| Wallner, Wang e Dormann (2023) | Visualização | Tempo e posição juntos; referência do mapa de calor |

### 5.2.2 O que cada estudo diz, conferido no próprio artigo (2026-11-02)

Lidos o resumo e a conclusão dos PDFs em `Downloads/TCC/` e
`docs/artigos/`, o texto completo do Maymin (acesso aberto) e o resumo do
SiriusBI no arXiv. O Jadowski e Cunningham foi lido por inteiro em
2026-10-20 (Parte 5.1). Para cada um: o que o artigo diz com as palavras
dele, e por que isso justifica a escolha.

| Estudo | O que o artigo diz (conferido) | Por que justifica a escolha |
|---|---|---|
| **Hodge et al. (2021)** | Pesquisa anterior ficava na previsão **pré-jogo** e em dados **amadores**; eles fazem "o primeiro estudo de caso abrangente" de previsão **ao vivo** no profissional, em Dota 2, e chegam a **85% após 5 minutos**, medido nas previsões ao vivo de **28 jogos** do torneio ESL One Hamburg 2017 (treino com cerca de 5,7 mil partidas de habilidade mista). Na revisão, citam um trabalho que divide a partida em fases de 15 minutos. | É a referência de que prever pelo **estado da partida** funciona. O seu trabalho leva essa ideia a LoL, com cortes fixos |
| **Birant e Birant (2023)** | "Pesquisas anteriores enfatizaram a previsão **centrada no jogador**", mas "é necessária uma classificação **centrada no time**, porque a cooperação é essencial". Base pública do Kaggle (ranqueadas de NA e EU) com abates, assistências, mortes, dano e ouro por jogador, que são **resumos do fim da partida**. Chegam a **até 95%**, que **não é comparável** com previsão em jogo. | Justifica as variáveis como **diferenças entre os times**. Você usa o princípio, não a técnica deles (MOMIL) |
| **Bahrololloomi et al. (2022)** | Duas métricas de desempenho individual a partir de 2.901 partidas (29.010 linhas de jogador); um modelo de *gradient boosting* chega a 92,7%, mas isso é *100 − MAPE* numa regressão do XP por minuto, e **não** acurácia de classificação; o peso de cada função (*role*) é estimado por otimização linear e resulta quase igual entre as cinco (0,1% de diferença). Os 86% de "previsão de vitória" comparam a soma das notas dos dois times **na própria partida**: é medida de fim de partida, não previsão em jogo. | Mostra o caminho **oposto** (por jogador e por função), que delimita a sua escolha e aparece só nos perfis de jogador |
| **Jadowski e Cunningham (2022)** | Treinam na primavera de 2020 (882 jogos profissionais) e testam nos 306 do verão: 67%. Medem 54,08% de vitória do azul. Escrevem que 90% é improvável pelas zebras. | Comparação de acurácia e apoio externo ao 53,2% do azul |
| **Do et al. (2021)** | Rede neural profunda prevê ranqueadas **antes do jogo** pela experiência com o campeão: 75,1%. **os outros quatro algoritmos testados ficaram entre 72,7% e 75,4%** (*gradient boosting* 75,4%, acima da rede; *Random Forest* 74,7%; SVM 74,3%; kNN 72,7%), e eles leem isso como sinal de que a experiência com o campeão é um bom indicador independentemente do modelo. | Comparação em ranqueadas e um **paralelo direto** do seu empate entre modelos |
| **Maymin (2021)** | Modelo de probabilidade em jogo, regressão logística com minuto, abates, torres e monstros grandes, calibrada em milhões de partidas; exclui o ouro de propósito; diz que acrescentar variáveis não melhorou; prefere um modelo único a um por minuto. | Ranqueadas sem comparação com o profissional (argumento da 3.6) e três pontos a seu favor (Parte 5.1) |
| **Guan e Tung (2026)** | *Preprint*. Previsão pré-jogo no profissional com regressão logística, 5.135 jogos de 2024 a 2026, e o *first pick* como covariável. **As duas arquiteturas que comparam são estatisticamente indistinguíveis.** | Apoio à hipótese do *draft* e outro paralelo do empate entre modelos; não sustenta número |
| **García-Méndez e Arriba-Pérez (2025)** | O esforço em previsão profissional ficou na classificação em lote, "deixando de lado a visualização"; a falta de interpretabilidade é "uma das limitações mais significativas" dos trabalhos anteriores. O sistema deles tem um **módulo de explicabilidade** e chega a 92,5% de acurácia em *streaming*, **em partidas profissionais de CS:GO** (base do Kaggle com dados da HLTV), e não em LoL. O sistema deles tem também descrições em linguagem natural e um painel visual, como a nossa plataforma. | Justifica o SHAP na tela: previsão sem explicação é a lacuna que eles apontam |
| **Jiang et al. (2025), SiriusBI** | BI com LLM em produção na Tencent (finanças, publicidade, nuvem), diálogo de várias rodadas e mais de 93% de acerto na geração de SQL (97%, 93% e 96% nos três setores), com um estudo de 40 analistas, 20 com o sistema e 20 sem. | Mostra que LLM gerando SQL sobre dados estruturados funciona em escala; você leva a ideia ao domínio de LoL e mede no próprio domínio |
| **Guo et al. (2024), Talk2Data** | Interface em linguagem natural que **decompõe** perguntas complexas em simples, com um modelo de *deep learning*; avaliada com estudo de ablação e estudo com 20 usuários. | Fundamento da consulta em linguagem natural. Cuidado: você não implementa decomposição |
| **Wallner, Wang e Dormann (2023)** | *Storyline visualization* integra tempo e posição numa só vista para resumir partidas de LoL; estudo com 39 participantes respondeu bem a perguntas de local e evento, pior a perguntas de tempo. | Referência do mapa de calor de posicionamento por minuto |

**Dois achados úteis para a banca:**

1. **O empate entre modelos também aparece na literatura.** Do et al.
   (2021) obtêm 73% a 75% com *Random Forest*, SVM e rede neural, e Guan e
   Tung (2026) acham as duas arquiteturas indistinguíveis. Se a banca
   perguntar "não é estranho os três modelos empatarem?": "Não. Do et al. e
   Guan e Tung também acharam modelos diferentes empatados. Quando as
   variáveis são poucas e agregadas, o limite está nos dados."
2. **Fases de jogo têm precedente.** O Hodge et al. citam um trabalho que
   divide a partida em fases de 15 minutos, e o Maymin cita o Hodge
   treinando um modelo por minuto. O seu desenho, um modelo por fase, fica
   entre os dois.

### 5.2.3 Por que cada obra de método está no TCC

As obras de método não são "trabalhos relacionados": cada uma justifica
uma técnica no ponto em que ela é usada. A regra é citar a obra original
ou a mais aceita da técnica, mesmo que antiga.

| Obra | Por que esta, e não outra |
|---|---|
| Breiman (2001) | Artigo original da *Random Forest* |
| Chen e Guestrin (2016) | Artigo original do XGBoost |
| Hornik, Stinchcombe e White (1989) | Prova da aproximação universal, que justifica testar uma rede neural |
| Grinsztajn, Oyallon e Varoquaux (2022) | Comparação ampla e recente de árvores contra redes em dados tabulares (45 bases, treino truncado em 10 mil). Conferido no texto: com treino de 50 mil, a diferença tende a diminuir (indício, sem estudo rigoroso). As nossas 39 mil ficam entre os dois regimes, e o empate do MLP é coerente com isso. **Critério de seleção que importa à defesa (seção 3.1 do artigo):** eles removem bases "fáceis demais", isto é, aquelas em que a regressão logística fica a menos de 5% (relativo) de **ambos** o ResNet e o HistGradientBoosting. Nossa regressão logística (AUC 0,8483 contra 0,8473 do XGBoost) cairia nesse critério: a base não discrimina famílias de modelo, o que explica o empate e fica fora do regime em que o resultado deles é informativo. Também removem séries temporais e alvos determinísticos |
| Lundberg e Lee (2017) | Artigo original do SHAP, com a prova das propriedades que o justificam |
| Ribeiro, Singh e Guestrin (2016) | Artigo original do LIME, a alternativa considerada |
| Hanley e McNeil (1982) | Interpretação clássica da AUC como probabilidade de ordenar certo um par |
| Niculescu-Mizil e Caruana (2005) | Estudo clássico de calibração, que mostra que *boosting* pode distorcer probabilidades |
| Kohavi (1995) | Estudo de referência sobre validação cruzada estratificada |
| Kaufman et al. (2012) | Definição formal de vazamento de dados e de como evitá-lo |
| Pedregosa et al. (2011) | Citação oficial do scikit-learn (*GridSearchCV*, MLP, *Random Forest*) |
| Brown, Cai e DasGupta (2001) | Comparação de intervalos para proporções que recomenda o de Wilson |
| Holm (1979) | Artigo original da correção de Holm para comparações múltiplas |
| Wang et al. (2020), RAT-SQL | Mostra que representar as relações do esquema melhora o *text-to-SQL* |
| Zhong, Yu e Klein (2020) | Discute os limites da acurácia de execução, a métrica do *benchmark* |
| Prodanov e Freitas (2013); Gil (2002); Creswell e Creswell (2023) | Manuais de metodologia usados na classificação da pesquisa, como no TCC I |

**Resposta pronta:** "Os trabalhos foram escolhidos para cobrir cada
camada da plataforma (predição, explicabilidade, linguagem natural e
visualização), dentro da janela de cinco anos. O núcleo veio do
levantamento do TCC I, triado por título e resumo; no TCC II acrescentei
quatro estudos de *League of Legends* para ter com quem comparar a
acurácia. Quando o estudo é de outro jogo ou outro domínio, ele entra pelo
método, e o texto diz isso."

### 5.3 As 15 obras de método (Seções 2 e 4)

| Obra | O que criou/mostrou | Por que está no TCC |
|---|---|---|
| Brown, Cai e DasGupta (2001) | Compara intervalos de confiança para proporções; recomenda Wilson ou Jeffreys para n ≤ 40 e, acima disso, diz que Wilson, Jeffreys e Agresti-Coull são muito parecidos (prefere Agresti-Coull pela simplicidade) | Justifica o intervalo de Wilson em vez do usual (Wald), que tem cobertura instável (Seção 4.5). Nossos n são de milhares |
| Holm (1979) | Correção de Holm para comparações múltiplas | O teste que refutou o "pico" do viés (Seção 4.5) |
| Kohavi (1995) | Estudo de validação cruzada e *bootstrap*; **recomenda validação cruzada estratificada de 10 dobras**, e diz que 5 dobras tem viés pessimista em bases pequenas | Justifica a validação cruzada estratificada (Seção 4.4). As 5 dobras são escolha de custo, e o Apêndice C mostra que 10 muda no máximo 0,0008 de acurácia |
| Pedregosa et al. (2011) | A biblioteca scikit-learn: interface única de estimadores, validação cruzada e `GridSearchCV` (seção 4 do artigo). **Não descreve** Random Forest nem MLP (o `MLPClassifier` entrou na versão 0.18, de 2016) | Origem do `GridSearchCV` e da biblioteca usada (Seção 4.4). Os modelos RF e MLP vêm de Breiman (2001) e de Hornik et al. (1989) |
| Kaufman et al. (2012) | Vazamento de dados: formulação e como evitar | Base da regra "nada do futuro entra" (Seção 4.6) |
| Hornik, Stinchcombe e White (1989) | Redes com camada escondida aproximam qualquer função | Aproximação universal do MLP (Seção 2.2) |
| Grinsztajn, Oyallon e Varoquaux (2022) | Em dados tabulares de porte médio, métodos de árvores seguem competitivos com redes neurais | Por que árvores fazem sentido aqui (Seção 2.2) |
| Niculescu-Mizil e Caruana (2005) | Calibração de probabilidades; *boosting* pode distorcê-las | Contexto da curva de calibração (Seção 5.4) |
| Zhong, Yu e Klein (2020) | Limites da acurácia de execução em *text-to-SQL*; propõe vários bancos de teste | Limitação do *benchmark* de 26 perguntas (Seção 4.7) |
| Breiman (2001) | Random Forest | Um dos 3 modelos comparados |
| Chen e Guestrin (2016) | XGBoost | O modelo adotado em produção |
| Hanley e McNeil (1982) | O significado da AUC-ROC | Justifica a métrica principal |
| Lundberg e Lee (2017) | SHAP | A técnica de explicação usada |
| Ribeiro, Singh e Guestrin (2016) | LIME | A alternativa ao SHAP (comparada, não usada) |
| Wang et al. (2020) | RAT-SQL (text-to-SQL ciente do esquema) | Fundamenta a conversão de pergunta em SQL |

### 5.4 As outras 5 referências

- **Prodanov e Freitas (2013), Gil (2002), Creswell e Creswell (2023):**
  livros de metodologia científica (Parte 4). Yin (2018) foi removido em
  2026-11-03 (ver 4.2).
- **Riot Games (APIs):** a documentação oficial da API (Anexo A).
- **Oracle's Elixir (Downloads):** fonte dos dados profissionais
  (oracleselixir.com/tools/downloads, acesso em 4 jul. 2026; os arquivos
  são baixados do Google Drive que o site aponta).

**Total: 31 referências** = 11 de domínio + 15 de método + 3 de
metodologia + 1 de documentação da API + 1 de fonte de dados.

---

## 6. Os dados: de onde vieram e como foram coletados

### 6.1 Fonte 1: Riot Games API (partidas ranqueadas)

**O que é uma API:** um "balcão de atendimento" de um sistema. Você faz
um pedido no formato combinado e recebe uma resposta com dados. A Riot
(dona do LoL) oferece uma API pública com dados das partidas.

**Os 4 endpoints usados** (cada endpoint é um "tipo de pedido"):

| Endpoint | Para que serviu | Exemplo |
|---|---|---|
| **league-v4** | Listar os jogadores Desafiante e Grão-Mestre de cada região | "me dá a lista dos melhores da Coreia" |
| **account-v1** | Descobrir o nome (Riot ID) de um jogador a partir do seu código | "quem é o jogador abc-123?" |
| **match-v5** | Baixar o resumo de uma partida (quem ganhou, campeões, totais) | "me dá a partida BR1_123" |
| **match-v5 /timeline** | Baixar a **linha do tempo** da partida, minuto a minuto | "como estava a partida no minuto 15?" |

**A *timeline* é o coração do projeto.** Ela tem uma "foto" (chamada
*frame*) a cada minuto: quanto ouro e XP cada jogador tinha, onde ele
estava no mapa, e todos os eventos (abates, torres, dragões) com o
momento exato. É dela que saem as *features* e o mapa de calor.

**Por que só Desafiante e Grão-Mestre? (confirmado por você em
2026-11-02: questão de escopo).** O recorte delimita uma população finita e
bem definida: a *league-v4* devolve a lista inteira desses elos por região,
e o número de jogadores é pequeno o bastante para coletar com a chave de
desenvolvedor (100 pedidos a cada 2 minutos). Cobrir todos os elos
exigiria amostragem por faixa e muito mais tempo de coleta. O custo do
recorte está declarado: os resultados não valem para outros elos (Seção
6.1, validade externa). Desde 2026-11-02 o motivo está escrito no TCC, na
Seção 4.3 a): "recorte de escopo: uma população fechada, que a API lista por
inteiro e que cabe no limite de requisições da chave de desenvolvedor".

**Resposta pronta:** "Foi uma decisão de escopo. O topo do ranking é uma
população fechada, que a API entrega inteira e que dava para coletar com a
chave de desenvolvedor. O preço é a validade externa: os números não se
estendem a outros elos, e isso está nas limitações."

**Fluxo da coleta (em 2 passos):**
1. `seed_players` busca, pela league-v4, os jogadores de elo alto de
   cada região e guarda na tabela `players`.
2. `collect_matches` pega cada jogador, lista as últimas partidas dele na
   **fila 420** (ranqueada solo/duo), e baixa a partida + a *timeline* das
   que ainda **não** estão no banco.

**Três dificuldades reais da coleta e como foram resolvidas:**

**a) Limite de pedidos (*rate limit*).** A chave de desenvolvedor só
permite **20 pedidos por segundo e 100 a cada 2 minutos**. Se passar,
a Riot responde com erro 429 ("calma aí"). Solução: o cliente
(`src/riot/client.py`) controla uma "janela deslizante" e se segura em
**95 pedidos a cada 2 minutos** (margem de segurança). Se mesmo assim
tomar 429, ele espera o tempo que a Riot mandar (cabeçalho
`Retry-After`).
- **Exemplo:** é como uma fila de banco com senha: no máximo 100 senhas
  a cada 2 minutos. O coletor conta as senhas e espera quando chega no
  limite.

**b) A chave expira a cada 24 horas.** A chave de desenvolvedor da Riot
vence todo dia. Solução: o coletor é **resumível**: ele pula partidas
já salvas. Se a chave vence no meio, você gera outra e roda de novo, e
ele continua de onde parou, sem duplicar nada.

**c) Regiões diferentes têm endereços diferentes.** A lista de
jogadores é por **plataforma** (br1, kr, euw1...), mas as partidas são
por **região de roteamento** (americas, asia, europe). O cliente
converte automaticamente (ex.: br1 e na1 → americas).

**Quantas partidas, por região (base final, Quadro 2):**

| Região | Partidas |
|---|---|
| BR1 (Brasil) | 11.936 |
| EUW1 (Europa Oeste) | 11.744 |
| KR (Coreia) | 10.204 |
| NA1 (América do Norte) | 7.159 |
| EUN1 | 20 (insuficiente, fora da análise) |
| **Total** | **41.063** |

**A coleta foi crescendo aos poucos** (isso é importante para a Parte
12): 10.295 → 23.133 → 24.154 → 33.713 → 39.426 → **41.063**.

**Por que EUN1 tem só 20?** Nunca foi uma região-alvo. O escopo sempre
foi BR1, EUW1, KR e NA1. As 20 partidas apareceram "de carona" e nunca
cresceram. O texto declara que ela foi excluída da leitura por amostra
insuficiente.

### 6.2 Fonte 2: Oracle's Elixir (partidas profissionais)

- **O que é:** um site que publica, de graça, planilhas (CSV) com
  estatísticas de jogos profissionais de LoL, ano a ano.
- **O que entrou:** **99.259 jogos** de 2014 a 2026, de 122 ligas, da elite às de desenvolvimento
  (LCK da Coreia, LPL da China, LEC da Europa, LTA, CBLOL do Brasil e
  outras).
- **Por que foi adicionada:** **não estava no TCC I**. Entrou no TCC II
  para comparar o padrão do *solo queue* com o do profissional. Foi essa
  comparação que revelou a inversão do viés de lado.

### 6.3 Ética e dados de pessoas

Os dados são **públicos e secundários** (já existiam, você não coletou de
pessoas diretamente). Não houve participação de sujeitos humanos. Isso
está escrito no fim da Seção 4.3.

---

## 7. O banco de dados e o tratamento (ETL)

### 7.1 PostgreSQL e o esquema (Apêndice A)

**Banco relacional** = dados guardados em tabelas que se ligam entre si
(como planilhas conectadas). Usado: **PostgreSQL**.

As **11 tabelas**:

| Tabela | Guarda o quê |
|---|---|
| `players` | Jogadores semeados (código, nome, elo, região) |
| `raw_matches` | O JSON **bruto** de cada partida, como veio da Riot |
| `raw_timelines` | O JSON **bruto** de cada *timeline* |
| `matches` | Dados normalizados da partida (região, versão, duração) |
| `teams` | Uma linha por time por partida (venceu? torres, dragões...) |
| `participants` | Uma linha por jogador por partida (campeão, KDA, ouro...) |
| `bans` | Campeões banidos |
| `item_events` | Compras e vendas de itens ao longo da partida |
| `items` | Catálogo oficial de itens (nome, preço) |
| `pro_games` | Jogos profissionais, uma linha por time |
| `pro_players` | Jogadores profissionais, uma linha por jogador |

### 7.2 Por que guardar o JSON bruto?

**Exemplo:** é como guardar a **nota fiscal original** além da planilha
de gastos. Se você descobrir um erro na planilha, refaz a partir das
notas, sem ter que pedir tudo de novo à Riot (o que levaria dias, por
causa do limite de pedidos). Isso salvou o projeto mais de uma vez
(ver Parte 19, o bug das torres).

### 7.3 ETL

**ETL** = *Extract, Transform, Load* (extrair, transformar, carregar).
É o processo de pegar o dado bruto e transformar em tabelas limpas.

Tratamentos importantes:
- **Normalização** do JSON da partida em `matches`, `teams`,
  `participants`.
- **Eventos de item** com o "desfazer" (`ITEM_UNDO`) aplicado: se o
  jogador comprou e desfez a compra, a compra não conta.
- **Reconciliação de nomes de campeão** entre Riot e Oracle's Elixir
  (cada fonte escreve alguns nomes de um jeito).
- **Catálogo de itens** vindo do Data Dragon (arquivo oficial da Riot),
  para o sistema mostrar nome e ícone do item **consultando o banco**, e
  nunca confiando na memória de um modelo de linguagem.

### 7.4 Idempotência (palavra difícil, ideia simples)

**Idempotente** = rodar duas vezes dá o mesmo resultado que rodar uma
vez. **Exemplo:** apertar o botão do elevador duas vezes não chama dois
elevadores. O coletor e os ETLs foram feitos assim de propósito: rodar
de novo **não duplica** linhas nem corrompe nada. Isso é o que permite
retomar a coleta todo dia depois que a chave vence.

---

## 8. As *features*: o que o modelo enxerga

### 8.1 O que é uma *feature*

*Feature* (ou variável preditora) é uma **informação de entrada** que o
modelo usa para fazer a previsão. **Exemplo:** para prever se vai
chover, as *features* seriam umidade, temperatura, nuvens.

### 8.2 As 5 *features* do projeto

Todas são **diferenças: time azul menos time vermelho**, no minuto do
corte:

| *Feature* | Significado | Exemplo |
|---|---|---|
| `gold_diff` | Diferença de ouro | +2.000 = azul tem 2 mil de ouro a mais |
| `xp_diff` | Diferença de experiência | +500 = azul tem mais XP |
| `kill_diff` | Diferença de abates | -3 = vermelho matou 3 a mais |
| `tower_diff` | Diferença de torres destruídas | +1 = azul derrubou 1 torre a mais |
| `dragon_diff` | Diferença de dragões | 0 = empate |

**E o "alvo"** (o que se quer prever): `blue_win` = 1 se o azul venceu,
0 se perdeu. É uma **classificação binária** (duas respostas possíveis).

**Por que diferenças e não valores absolutos?** Porque o que importa é
quem está **na frente**, não quanto cada um tem. Um time com 30 mil de
ouro pode estar perdendo se o outro tem 33 mil. Isso segue a ideia de
**modelagem centrada no time** de Birant e Birant (2023).

### 8.3 Os cortes de tempo: 10, 15, 20 e 25 minutos

O modelo não olha a partida inteira. Ele olha uma **foto** num minuto
específico. Foram escolhidos 4 cortes, cada um representando uma fase
(está escrito no topo do `build_features.py`):

| Corte | Fase do jogo |
|---|---|
| 10 min | Fase de rotas (cada um no seu caminho) |
| **15 min** | **Fim das rotas** (as placas de torre caem aos 14) — **corte padrão** |
| 20 min | Meio de jogo |
| 25 min | Transição para o fim de jogo |

**Por que 15 minutos é o padrão?** Porque é o fim da fase de rotas: o
jogo já mostrou quem está melhor, mas ainda não está decidido. Uma
previsão aos 15 é útil (dá tempo de reagir) e informativa.

**Por que um modelo para cada corte?** Porque a importância das coisas
muda com o tempo. **Exemplo real:** torres quase não importam até os 20
minutos e de repente importam muito aos 25 (Parte 11). Um modelo único
misturaria essas fases e ficaria pior.

**Se a partida acabou antes do corte** (ex.: alguém se rendeu aos 14
minutos), ela simplesmente não entra naquele corte. Por isso o número
de partidas cai nos cortes tardios: 39.309 aos 10, 39.188 aos 15,
34.337 aos 20, 26.837 aos 25.

### 8.4 Vazamento de dados (*data leakage*) — A REGRA MAIS IMPORTANTE

**É muito provável a banca perguntar isso.**

**O que é:** quando o modelo, sem querer, recebe uma informação que ele
**não teria no momento real da previsão**, normalmente informação do
futuro. Aí ele parece ótimo nos testes e é inútil na prática.

**Exemplo simples:** prever quem ganha um jogo de futebol olhando o
**placar final**. Você vai acertar 100%, mas isso não é previsão, é
"colar com o gabarito".

**No LoL:** se você usasse o **total de abates da partida inteira** ou o
**ouro total no fim**, o modelo acertaria quase sempre, porque quem
ganhou normalmente termina com mais. Seria trapaça.

**Como o projeto evita:** as *features* são calculadas **só com os
frames até o minuto do corte** (`frames[: corte + 1]` no código). Nada
depois do minuto 15 entra no modelo do minuto 15. Isso é um "invariante"
do projeto: uma regra que nunca pode ser quebrada.

**Onde cuidar mais:** o experimento 11 (percentis comportamentais) quase
caiu nessa armadilha: a Riot devolve o comportamento **atual** do
jogador, não o de quando a partida aconteceu. Usar isso em partidas
antigas seria usar dado do futuro. A solução foi testar só em partidas
**recentes** da Coreia, registrando o intervalo de dias (Parte 12).

---

## 9. Os três modelos: Random Forest, XGBoost e MLP

### 9.1 Por que comparar três modelos?

1. **O TCC I prometeu:** o objetivo específico **e** é "comparar o
   desempenho de modelos de *machine learning*, com foco em XGBoost,
   Random Forest e redes neurais". O TCC II cumpriu.
2. **São três "famílias" diferentes** de modelo, cada uma com uma lógica.
   Comparar mostra qual combina melhor com esse tipo de dado, por
   **medição**, não por preferência. (A Seção 2.2 diz: "comparou três, por
   medição, e não por preferência".)
3. **Conversa com o orientador (confirmado por você em 2026-11-02):** além
   do XGBoost, entraram *Random Forest* e redes neurais porque, numa
   conversa com o orientador, ficou combinado que seria interessante ver
   as diferenças de resultado entre as abordagens. O registro de
   acompanhamento não detalha esse assunto (só "estrutura" e
   "fundamentação"), então, se perguntarem onde está escrito, a
   justificativa formal é a do TCC I, Seção 4.6: "analisar abordagens
   distintas para dados competitivos, incluindo métodos amplamente
   utilizados em dados tabulares e modelos neurais capazes de capturar
   relações mais complexas entre variáveis".

**Resposta pronta:** "O XGBoost era o candidato natural para dados em
tabela. Conversando com o orientador, decidimos comparar com *Random
Forest* e uma rede neural para ver as diferenças de resultado entre
famílias de modelos: dois *ensembles* de árvores, um por *bagging* e outro
por *boosting*, e uma rede neural. A comparação foi por medição, e os três
ficaram próximos."

### 9.2 Primeiro: o que é uma árvore de decisão

Os dois primeiros modelos usam árvores de decisão. Uma árvore é uma
sequência de perguntas de sim ou não. **Exemplo:**

```
O azul tem mais de 2.000 de ouro a mais?
├── Sim → Tem pelo menos 1 torre a mais?
│         ├── Sim → "azul provavelmente vence"
│         └── Não → ...
└── Não → ...
```

Uma árvore sozinha erra muito. Os dois modelos juntam **centenas** de
árvores, de jeitos diferentes.

### 9.3 Random Forest (Breiman, 2001)

**Ideia:** um **comitê** de muitas árvores que votam. Cada árvore é
treinada com uma **amostra sorteada** das partidas (isso se chama
*bagging*) e, em cada pergunta, só pode escolher entre um **sorteio de
*features***. Isso força as árvores a serem diferentes umas das outras.
No fim, a maioria dos votos decide.

**Exemplo:** 500 pessoas tentando adivinhar o vencedor, cada uma viu
partes diferentes dos jogos e prestou atenção em coisas diferentes. A
média das opiniões costuma ser melhor que a opinião de qualquer uma.

**Por que faz sentido aqui:** as *features* do LoL andam juntas (quem
tem mais ouro costuma ter mais abates e mais torres). O sorteio de
*features* "descorrelaciona" as árvores, o que ajuda nesse tipo de dado.

**No projeto:** 500 árvores na comparação final.

### 9.4 XGBoost (Chen e Guestrin, 2016), o modelo adotado

**O nome:** *eXtreme Gradient Boosting*.

**Ideia (*boosting*):** em vez de árvores independentes votando, as
árvores são construídas **em sequência**, e **cada nova árvore tenta
corrigir os erros das anteriores**.

**Exemplo:** uma turma fazendo uma prova em fila. O primeiro aluno
responde. O segundo olha **só onde o primeiro errou** e tenta corrigir.
O terceiro olha o que ainda está errado... depois de 500 alunos, o
resultado somado é muito bom.

**O "gradiente":** é a forma matemática de medir "para que lado e quanto
o erro precisa ser corrigido". O XGBoost usa também a "curvatura" do
erro (otimização de segunda ordem), o que deixa a correção mais precisa.

**A "regularização":** é um freio para o modelo não "decorar" os dados
de treino (*overfitting*). **Exemplo:** um aluno que decora as respostas
da prova antiga e vai mal numa prova nova. O freio impede isso.

**Configuração de produção (hiperparâmetros):**

| Hiperparâmetro | Valor | Em palavras simples |
|---|---|---|
| `n_estimators` | **500** | 500 árvores em sequência |
| `learning_rate` | **0,01** | Cada árvore corrige só **1%** do erro. Passos pequenos = aprende devagar, mas com cuidado |
| `max_depth` | **3** | Cada árvore faz no máximo **3 perguntas** seguidas. Árvores rasas = modelo simples, difícil de decorar |

**Por que "hiperparâmetro" e não "parâmetro":** parâmetros o modelo
aprende sozinho dos dados. Hiperparâmetros são configurações que
**você** escolhe antes de treinar.

**Por que o XGBoost foi escolhido como modelo de produção (Seção 5.4):**
- Teve a **maior acurácia no corte de 15 minutos** (0,7621), o corte
  padrão, também contra a *Random Forest* e o MLP ajustados (0,7617 e
  0,7619). Na AUC, o MLP ajustado fica 0,0004 acima (0,8477 contra
  0,8473). Ou seja: **empate técnico** (Seção 5.4, texto corrigido em
  2026-11-02).
- **Mas atenção, a escolha não foi porque ele ganhou em tudo.** Aos 10
  minutos o MLP teve acurácia um pouco maior (0,7020 contra 0,7004) e aos
  25 minutos o MLP quase empatou na AUC (0,9072 contra 0,9090). O texto
  (Seção 5.4) não usa mais o argumento da "estabilidade na faixa
  intermediária": diz que o XGBoost foi **mantido por ser a escolha
  anterior ao baseline e já sustentar a interface**, e remete os números
  dos quatro cortes ao Apêndice C (mudado em 2026-11-04).
- **Resposta pronta se perguntarem "mas o MLP ganhou aos 10 minutos!":**
  "Ganhou por 0,0016 de acurácia, uma diferença irrelevante. O XGBoost
  vinha do TCC I e já sustentava a interface; ele se integra direto com o
  SHAP de árvore (TreeExplainer), que dá explicações exatas e rápidas, e
  os dois ficaram no mesmo patamar."
  (Essa última parte é verdade técnica: o `export_model.py` usa
  `shap.TreeExplainer`, que é específico para árvores.)

**De onde veio o conhecimento para usar o XGBoost:**
1. **O artigo original** (Chen e Guestrin, 2016), citado na Seção 2.2,
   que explica o método e por que ele costuma ser forte em **dados
   tabulares** (dados em forma de tabela, como as suas *features*).
2. **A exigência do TCC I** (objetivo e).
3. **A documentação da biblioteca** `xgboost` em Python.
4. **A medição:** a busca em grade (abaixo) confirmou a configuração.

**Como os hiperparâmetros foram escolhidos (GridSearchCV):**
- *Grid search* = **testar todas as combinações** de uma lista de
  valores e ficar com a melhor. **Exemplo:** testar todas as combinações
  de runas e itens para ver qual dá mais dano.
- A grade do XGBoost tinha 3 valores para cada um dos 3 hiperparâmetros:
  árvores (200, 300, 500), taxa (0,01; 0,05; 0,1) e profundidade (3, 4,
  6) = **27 combinações**.
- Sobre as 39 mil partidas, a melhor combinação foi 200 árvores, taxa
  0,05, profundidade 3, com AUC **0,8475**. A de produção (500/0,01/3)
  teve **0,8473**: **2º lugar entre 27**, diferença de **0,0001**.
- **Conclusão importante:** o modelo de produção **não está mal
  ajustado** (não é "subajuste"). Escolheu a **mesma profundidade** (3).

### 9.5 MLP — rede neural (perceptron multicamadas)

**Ideia:** imitação simplificada de neurônios. Os dados entram, passam
por **camadas** de "neurônios artificiais" que fazem contas e combinam
as informações, e sai uma probabilidade.

**No projeto:** duas camadas escondidas, com **64 e 32 neurônios**.
Antes de entrar, os dados passam por um `StandardScaler`, que coloca
todas as *features* na mesma escala (ouro está na casa dos milhares,
torres na casa das unidades; sem isso a rede daria importância demais
ao ouro só porque o número é maior).

**Ponto forte:** consegue aprender combinações complexas sozinha.
**Ponto fraco:** precisa de **muitos** dados e cuidado. O texto diz:
"restrição relevante numa amostra de dezenas de milhares de partidas, e
não de milhões".

**Como foi implementada (conferido no código, 2026-11-02):**

```python
make_pipeline(StandardScaler(),
              MLPClassifier(hidden_layer_sizes=(64, 32),
                            max_iter=500, random_state=42))
```

- **Arquitetura:** 5 entradas → 64 → 32 → 1 saída. São **2.497 pesos**
  aprendidos (5×64+64 = 384; 64×32+32 = 2.080; 32×1+1 = 33), pouco para 39
  mil partidas.
- **Padrões do scikit-learn 1.9 usados:** ativação **ReLU** nas camadas
  escondidas; saída **logística** (probabilidade); perda logarítmica;
  otimizador **Adam** com taxa 0,001; regularização `alpha` 0,0001; lotes de
  200 partidas; para em 500 épocas ou após 10 épocas sem melhora.
- **Treino, em uma frase:** pesos aleatórios (semente 42) → previsão → erro
  pela perda logarítmica → retropropagação calcula a culpa de cada peso →
  Adam corrige → repete lote a lote.
- **Normalização dentro do pipeline:** sem vazamento (Parte 9.6).
- **Convergência:** no piloto de 98 partidas não convergiu (aviso
  registrado no diário de 2026-07-01); com milhares, convergiu.

**Histórico de desempenho (AUC aos 15 min, MLP × XGBoost):** 7.353
partidas sem ajuste 0,8050 × 0,8144; ajustada (32 neurônios, alpha 0,01)
0,8278 × 0,8260; 10.295 partidas ajustada 0,8325 × 0,8319; base final
(Quadro 3, configuração de referência 64/32) 0,8455 × 0,8473.

**Por que não foi a de produção:** empate técnico em desempenho (XGBoost
igual ou melhor em AUC nos quatro cortes e em acurácia em três), e a
explicação: para árvores o SHAP usa o `TreeExplainer`, exato e rápido; para
uma rede do scikit-learn usaria o `KernelExplainer`, aproximado e muito
mais lento, ruim para a tela interativa.

**A comparação do Quadro 3 (achado e corrigido no texto em 2026-11-02).**
A 5.4 dizia que o Quadro 3 comparava os três "após ajuste de
hiperparâmetros", mas na base final só o XGBoost passou pela busca em
grade; a *Random Forest* (500 árvores, sem limite de profundidade) e o MLP
(64, 32) estão na configuração de referência. Agora a 5.4 diz isso e cita a
busca feita também para os outros dois, sobre as mesmas 39.188 partidas
(`tune_models_full --completo`, gravado em `reports/tune_models_39k.json`),
medida do mesmo jeito do Quadro 3:

| 15 min | Acurácia | AUC |
|---|---|---|
| XGBoost (produção) | **0,7621** | 0,8473 |
| MLP ajustada: (32), alpha 0,001 | 0,7619 | **0,8477** |
| *Random Forest* ajustada: 200 árvores, profundidade 6, folha 5 | 0,7617 | 0,8468 |

Empate técnico. O XGBoost segue com a maior acurácia, o critério do
Apêndice F, e a conclusão não muda. Se a banca comparar o Quadro 3
(*Random Forest* com 0,8277) com o Apêndice F (*Random Forest* de
profundidade 6 a 0,0005 do XGBoost), a resposta está na própria 5.4: o
quadro traz a configuração de referência, e a frase seguinte, a ajustada.
**Resposta pronta:** "Na base final, ajustei por busca em
grade o XGBoost. Rodando a mesma busca para a *Random Forest* e a rede, os
três ficam a menos de 0,001 em AUC e em acurácia. É empate técnico, e o
XGBoost segue com a maior acurácia, o critério que defini."

### 9.6 Validação cruzada estratificada de 5 *folds* (semente 42)

**O problema:** se você testar o modelo nas mesmas partidas em que ele
treinou, ele parece ótimo (já viu as respostas). Precisa testar em
partidas que ele **nunca viu**.

**Validação cruzada de 5 *folds*:** divide as partidas em **5 pilhas**.
Treina com 4 e testa na 5ª. Repete 5 vezes, cada vez testando numa pilha
diferente. Faz a média. Assim **toda partida é testada uma vez** sem que
o modelo a tenha visto no treino.

**"Estratificada":** cada pilha mantém a **mesma proporção** de vitórias
do azul do conjunto inteiro (46,6%). Evita uma pilha "azarada" só com
vitórias do vermelho.

**"Semente 42":** o sorteio das pilhas é aleatório. Fixar a semente
(*seed*) faz o sorteio sair **igual toda vez**, então qualquer pessoa que
rodar o script obtém exatamente os mesmos números. Isso é
**reprodutibilidade**. (O número 42 é só uma convenção, poderia ser
qualquer um.)

**Por que validação cruzada e não só "80% treino, 20% teste"?** Porque
com uma divisão só, o resultado depende da sorte daquela divisão. Com 5,
a média é mais confiável.

**Por que 5 e não 10 dobras? (pergunta provável, confirmado por você em
2026-11-02).** O Kohavi (1995), que o TCC cita, recomenda validação cruzada
estratificada com **10** dobras. O projeto usou 5 por custo: a busca em
grade treina cada combinação uma vez por dobra (27 combinações no XGBoost,
mais as grades da *Random Forest* e do MLP em `tune_models_full.py`), e 10
dobras dobrariam o número de treinos. Com ~39 mil partidas, cada dobra de
teste ainda tem perto de **7.800 partidas** (39.188 ÷ 5), amostra grande o
bastante para a média ser estável. Do Kohavi, o projeto segue a parte
central: validação cruzada **estratificada**. Um bônus: a mesma divisão
(`StratifiedKFold(n_splits=5, random_state=42)`) é usada em todos os
scripts (modelo de referência, busca em grade, os 11 experimentos), então
toda comparação do trabalho é feita sobre as mesmas dobras.

**Resposta pronta:** "O Kohavi recomenda 10 dobras. Usei 5 por custo
computacional, porque a busca em grade treina cada combinação uma vez por
dobra, nos três modelos. Com quase 40 mil partidas, cada dobra de teste tem
cerca de 7.800, o que deixa a estimativa estável. A parte da recomendação
que mais importa, a estratificação, foi seguida, e a mesma divisão vale
para todos os experimentos."

**Medido em 2026-11-03:** rodando de novo com 10 dobras (`src/models/robustez_dobras.py`, Apêndice C), a diferença é de no máximo 0,0008 em acurácia e 0,0006 em AUC, nos quatro cortes e nos três modelos. A resposta agora é "medi, e não muda".

**Não exagere o custo.** A grade do XGBoost sobre as 39.188 partidas levou
**51,7 segundos** (`reports/tune_models_39k.json`). Se a banca disser "então
10 dobras custariam dois minutos", concorde: o custo pesava mais nas grades
da *Random Forest* (500 árvores) e do MLP e na repetição dos 11
experimentos, e o argumento principal é outro: com 7.800 partidas por dobra
de teste, a diferença entre 5 e 10 dobras na estimativa é pequena, e manter
a mesma divisão em todo o trabalho deixa os resultados comparáveis entre si.

**Pergunta relacionada: "a busca em grade e a avaliação usaram as mesmas
dobras? Isso não é otimista?"** Sim, as mesmas dobras, sem validação
cruzada aninhada nem conjunto de teste separado. Em tese isso dá uma
estimativa levemente otimista para a melhor combinação. Na prática, o
efeito aqui é desprezível: a configuração de produção (500/0,01/3) foi
escolhida pela busca em grade na base **antiga, de 10.295 partidas**
(`reports/tune_models_10k.log`), e mantida; na base de 39.188 a grade
completa a pôs em 2º de 27, a 0,0001 da melhor. Resposta: "Não usei
validação aninhada. Mas a configuração de produção veio da busca numa base
anterior, de 10 mil partidas, e na base final ficou a 0,0001 da melhor
combinação, então o viés de seleção não muda a conclusão."

**E o `StandardScaler` do MLP, vaza?** Não: ele está dentro de um
`make_pipeline` (`multi_cutoff_metrics.py`), então é ajustado só nas dobras
de treino de cada rodada. Esse é um ponto que bancas de ML costumam
perguntar (pré-processamento ajustado antes de dividir os dados).

**Outra pergunta possível: "as dobras são independentes?"** Não
totalmente, e o texto admite (Seção 6.1, validade interna): o mesmo
jogador aparece em várias partidas, e o sorteio por partida pode pôr
partidas dele no treino e no teste. Uma divisão por grupo (por jogador)
seria mais rigorosa; fica como limitação declarada.

### 9.7 Os resultados completos (Quadros 3 e 4, Apêndice C)

**Corte de 15 minutos (Quadro 3):**

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| **XGBoost** | **0,7621** | 0,7561 | 0,7228 | 0,7391 | **0,8473** |
| MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| Random Forest | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |

**XGBoost em todos os cortes (Quadro 4):**

| Corte | Acurácia | AUC-ROC |
|---|---|---|
| 10 min | 0,7004 | 0,774 |
| 15 min | 0,7621 | 0,847 |
| 20 min | 0,7917 | 0,876 |
| 25 min | 0,8241 | 0,909 |

**Leitura:** quanto mais tarde, mais o modelo acerta. **Faz sentido:**
aos 25 minutos já aconteceu muito mais coisa, a partida está mais
"definida". Mas a previsão aos 25 também é **menos útil**, porque sobra
menos tempo para mudar o rumo.

**Tudo isso é reproduzível** com `python -m src.models.multi_cutoff_metrics`,
que grava `reports/metricas_corte.json`.

---

## 10. Como os modelos foram avaliados (métricas)

**De onde vieram as 5 métricas:** da **ficha de avaliação do TCC I**
(está escrito no topo do `train_baseline.py`).

Para explicar, imagine **1.000 partidas** no corte de 15 minutos. Em
~466 o azul venceu (46,6%), em ~534 o vermelho venceu.

### 10.1 Acurácia — 0,7621

**De todas as previsões, quantas acertaram?** ≈ 762 de 1.000.

**A armadilha:** como as classes não são 50/50, um "modelo burro" que
**sempre** diz "vermelho vence" acerta 53,4% **sem entender nada**. Então
76% não deve ser comparado com 50%, e sim com esse "chute" de ~53%.
O ganho real é de uns 23 pontos percentuais acima do chute.

### 10.2 Precisão — 0,7561

**Quando o modelo diz "azul vence", quantas vezes ele está certo?**
De cada 100 vezes que ele aposta no azul, ~76 o azul vence mesmo.

### 10.3 *Recall* (revocação) — 0,7228

**De todas as partidas que o azul realmente venceu, quantas o modelo
pegou?** ~72 de cada 100.

**Precisão x recall, exemplo de detector de incêndio:** precisão alta =
quando apita, é incêndio mesmo. Recall alto = não deixa nenhum incêndio
passar sem apitar. Normalmente melhorar um piora o outro.

### 10.4 F1 — 0,7391

A **média harmônica** entre precisão e recall: um número só que só é
alto se **os dois** forem altos.

### 10.5 AUC-ROC — 0,8473 (a métrica principal)

**A pergunta que ela responde:** pegue **uma partida que o azul venceu**
e **uma que o azul perdeu**, ao acaso. O modelo dá uma probabilidade de
vitória do azul para cada uma. Em quantos desses pares ele dá a
probabilidade **maior** para a partida que o azul de fato venceu?
Resposta: **84,73%** das vezes.

Isso é exatamente o que Hanley e McNeil (1982) mostraram que a AUC
significa: a probabilidade de um caso positivo receber nota maior que
um negativo.

- **AUC = 0,5:** igual a jogar moeda.
- **AUC = 1,0:** perfeito.
- **0,8473:** bom poder de separação.

**Por que ela é a principal:** não depende do "corte de 50%" e não é
enganada pela proporção desigual de vitórias. O texto reporta acurácia
**e** AUC juntas justamente para mostrar essa diferença (Seção 2.3).

### 10.6 Calibração

**Pergunta:** quando o modelo diz "70% de chance de o azul vencer", o
azul vence mesmo em ~70% dessas partidas?

**Exemplo:** a previsão do tempo. Se em 100 dias a previsão disse "70%
de chuva" e choveu em 70 deles, ela é **bem calibrada**.

**Resultado:** a curva de calibração (`reports/calibration_curve.png`)
mostrou que os modelos, especialmente o XGBoost, **já eram bem
calibrados**, sem precisar de ajuste extra.

### 10.7 Taxa-base e a limitação do empate (Seção 6.1 e Apêndice F)

**Pergunta crítica:** se as duas equipes estão **totalmente empatadas**,
o que o modelo prevê?

- O modelo prevê ~49-51% para o azul (49,2% aos 10, 49,6% aos 15, 51,4%
  aos 20, 49,0% aos 25).
- Mas os **dados reais** de partidas empatadas mostram o azul vencendo
  só **46,4% a 47,9%** (o viés de lado, Parte 13).
- Diferença: **1,7 a 4,7 pontos percentuais**.

**Foi investigado a fundo:**
- **Não é subajuste:** a busca em grade não melhorou (Parte 9.4).
- **Calibrar piora:** de 1,7 para 2,3 pp, porque o "empate total" é um
  estado raro e o calibrador puxa para 50%.
- **Trocar para Random Forest (500 árvores, profundidade 6) resolve**
  (desvio cai para 0,6 pp), mas custa 0,0005 de AUC e a acurácia fica
  0,7617 contra 0,7621.
- **Decisão:** manter o XGBoost, porque o critério de escolha foi a
  acurácia aos 15 minutos. Decisão consciente, registrada como limitação.

---

## 11. Explicabilidade: SHAP

### 11.1 Por que explicar?

Por causa de García-Méndez e Arriba-Pérez (2025): **uma previsão sem
explicação não ajuda o usuário**. Dizer "o azul tem 72% de chance" é
menos útil que dizer "o azul tem 72% de chance **principalmente porque
tem 2 mil de ouro a mais**".

O problema: o XGBoost soma 500 árvores. Ninguém consegue ler isso.

### 11.2 As duas opções: LIME e SHAP

**LIME** (Ribeiro, Singh e Guestrin, 2016): "mexe um pouquinho" na
entrada e vê como a saída muda, criando um modelo simples só na
vizinhança daquela partida.
- Vantagem: simples.
- Problema: o resultado depende de como você define essa "vizinhança".

**SHAP** (Lundberg e Lee, 2017) — **o escolhido**: vem da **teoria dos
jogos**, do **valor de Shapley**.
- **Exemplo do valor de Shapley:** três amigos fazem um trabalho em grupo
  e ganham 9 pontos. Quanto cada um merece? O valor de Shapley calcula a
  contribuição média de cada um, testando todas as combinações possíveis
  de quem participou. É a divisão **justa** do mérito.
- No modelo: a "nota" é a probabilidade prevista, e os "amigos" são as 5
  *features*. O SHAP diz quanto cada *feature* empurrou a previsão.
- **Por que escolher o SHAP:** Lundberg e Lee mostraram que é a única
  solução com propriedades desejáveis (**consistência** e não dar
  importância a uma variável ausente). E as contribuições **somam**
  exatamente a previsão, o que permite montar a explicação em texto a
  partir de números **realmente calculados**.

### 11.3 O que o SHAP mostrou (Seção 5.4)

- **Ouro e experiência dominam** em todos os cortes. `gold_diff` vai de
  0,66 (10 min) a 1,07 (20 min). `xp_diff` vai de 0,27 (10 min) a 0,81
  (25 min).
- **Torres têm um comportamento curioso:** quase zero nos três primeiros
  cortes (0,0044 aos 10; 0,0060 aos 15; 0,0031 aos 20) e **saltam para
  0,0928 aos 25** — cerca de **15 vezes** entre 15 e 25 minutos.
- **Não é crescimento contínuo:** aos 20 minutos é menor que aos 10 e 15.
  É uma **concentração tardia**.
- **Por quê, no jogo:** as placas de torre caem aos 14 minutos, e antes
  disso destruir uma torre inteira é raro. Depois, torres viram sinal de
  quem domina o mapa.
- **Importância para a tese:** essa é a **justificativa concreta** para
  ter um modelo por fase. Um modelo único não capturaria essa mudança.

---

## 12. Os 11 experimentos que não funcionaram (e por que isso é bom)

### 12.1 O que foi tentado (Quadro 5, Seção 5.4; detalhe no Apêndice K)

Para tentar melhorar o modelo, foram testadas 11 ideias. **Nenhuma**
melhorou de forma distinguível de ruído (mudanças de ±0,001 a 0,003 na
AUC):

| # | Ideia | Resultado |
|---|---|---|
| 1 | Diferença de Barão/Arauto | ruído |
| 2 | Dispersão espacial do time (quão espalhado no mapa) | ruído |
| 3 | Ajuste de hiperparâmetros por fase | ruído |
| 4 | Calibração extra | sem ganho (já era calibrado) |
| 5 | Ouro convertido em itens | ruído |
| 6 | Separar *features* de defesa e ataque | ruído |
| 7 | `item_gold_diff` (segunda tentativa) | ruído |
| 8 | Visão (sentinelas colocadas/destruídas) | ruído |
| 9 | Tipo de dragão | **piorou** (0,8319 → 0,8295) |
| 10 | Placas de torre | -0,0002 |
| 11 | Percentis comportamentais do jogador (`lol-challenges-v1`) | -0,0031 / +0,0007 |

### 12.2 A história do experimento 11 (ótima para contar)

- Um **piloto pequeno** (199 partidas) mostrou um ganho de **+0,009**,
  maior que qualquer outro experimento. Parecia uma descoberta.
- Antes de acreditar, a amostra foi ampliada para **2.987 partidas**.
- Resultado: **-0,0031**. O "ganho" sumiu.
- **Explicação:** **regressão à média**. Com amostra pequena, o acaso
  pode criar um efeito que parece real. O próprio modelo base já oscilava
  1,8 ponto só pelo tamanho da amostra.
- **Exemplo:** jogar moeda 10 vezes e dar 8 caras não prova que a moeda é
  viciada. Jogue 1.000 vezes e vai dar perto de 500.

### 12.3 E o que realmente funcionou: mais dados

A AUC do XGBoost subiu só por aumentar o número de partidas:

| Partidas | AUC (15 min) |
|---|---|
| 10.295 | 0,8214 |
| 23.133 | 0,8393 |
| 39.188 | 0,8473 |

Ganho total de **0,0259**: cerca de **9 vezes** o maior ganho de um
experimento de variáveis (0,003) e cerca de 130 vezes o menor (0,0002).
(Versões anteriores diziam "6 vezes"; 0,0259 ÷ 0,003 dá 8,6. Corrigido em
2026-11-03 ao reescrever o Apêndice K.)

### 12.4 Por que resultados negativos são bons para a tese

1. **Honestidade científica:** mostra que você tentou melhorar e reporta
   o que não deu certo, em vez de esconder.
2. **É uma descoberta em si:** indica que, com essas *features* de estado,
   o modelo está **perto do teto**. O próximo ganho exigiria dados que a
   API pública **não oferece**: a **ordem do *draft*** e o **estado das
   ondas de minion**.
3. **Responde a pergunta "por que não chegaram em 90%?"** (Parte 15).

---

## 13. A análise exploratória: o viés de lado

**Este é o achado que mais chama atenção. Estude bem.**

### 13.1 O achado

No *solo queue* de elo alto, o **time vermelho vence mais** que o azul
(Quadro 2, 41.063 partidas):

| Região | Partidas | Vitória do vermelho | Intervalo de confiança 95% | Conclusão |
|---|---|---|---|---|
| BR1 | 11.936 | **56,3%** | [55,4%; 57,2%] | Firme |
| EUW1 | 11.744 | 53,4% | [52,5%; 54,3%] | Firme |
| NA1 | 7.159 | 52,2% | [51,1%; 53,4%] | Firme |
| KR | 10.204 | 50,4% | [49,5%; 51,4%] | **Inclui 50%: não dá para afirmar** |

**Leitura correta (decore a frase):** "A direção é a mesma nas quatro
regiões, mas a força não é igual: em **três das quatro** o intervalo
exclui 50%. Na Coreia o viés não é estatisticamente distinguível de
zero." Isso mostra que o padrão **não é só do Brasil**, é de elo
altíssimo em geral, mas sem afirmar mais do que os dados sustentam.

### 13.2 O que é um intervalo de confiança (de Wilson)

**Exemplo:** pesquisa eleitoral. "O candidato tem 40%, com margem de
erro de 2 pontos." Significa que o valor real provavelmente está entre
38% e 42%.

Aqui: na BR1, o vermelho venceu 56,3%, e o valor real provavelmente está
entre 55,4% e 57,2%. Como **50% está fora** desse intervalo, o viés é
real. Na KR, 50% está **dentro**, então pode ser só acaso.

**Wilson** é um jeito específico e mais confiável de calcular essa margem
para proporções (porcentagens).

### 13.3 O viés é constante ao longo da partida

**Uma versão antiga do texto dizia que o viés tinha um "pico" no meio do
jogo e enfraquecia no fim. Com mais dados, isso foi REFUTADO.**

Entre partidas **genuinamente empatadas** (diferença de ouro menor que
500), o azul venceu:

| Corte | Vitória do azul | Partidas |
|---|---|---|
| 10 min | 46,4% | 7.349 |
| 15 min | 47,9% | 3.970 |
| 20 min | 46,7% | 2.423 |
| 25 min | 47,1% | 1.430 |

Variação de só 1,4 ponto. **Nenhuma diferença entre os cortes sobrevive
à correção de Holm** (menor valor-p corrigido: 0,83). Ou seja: o viés
**existe e é constante**; o que sumiu foi a **"evolução"** que tinham
visto antes.

### 13.4 O que é a correção de Holm

**Exemplo:** se você joga 20 moedas, uma delas pode dar 8 caras em 10
só por sorte. Quanto **mais comparações** você faz, maior a chance de
achar uma diferença "falsa". A correção de Holm **aperta a régua** quando
você compara várias coisas ao mesmo tempo, para não ser enganado pelo
acaso. Foi ela que mostrou que o "pico" era ruído.

### 13.5 Os 4 testes de robustez (Seção 4.5)

Todo padrão encontrado passou por 4 testes **antes** de ser aceito:

1. **Replicação regional:** testar só na BR1. Se o viés aparece numa
   região sozinha, não é efeito de misturar regiões. ✔
2. **Faixa de duração:** ver se o viés muda em partidas curtas e longas.
   O azul ficou entre 45,6% e 47,3% em todas as faixas (amplitude de 1,7
   ponto, todas abaixo de 50%). Então não é "partidas longas são outro
   tipo de jogo". ✔
3. **Intervalo de Wilson:** nenhum dos 4 cortes inclui 50%. ✔
4. **Pares com correção de Holm:** sustenta a constância. ✔

### 13.6 A inversão no cenário profissional

No Oracle's Elixir (99.259 jogos), é o **azul** que vence: **53,2%**.
Estável de 2016 a 2026 (entre 52,5% e 55,0%). 2014 (58,2%) e 2015 (55,3%)
destoam, mas com poucos jogos (814 e 1.702).

**Hipótese de explicação (é hipótese, não prova):**
- No *draft*, o time **vermelho escolhe por último** e garante o
  ***counter-pick***.
- No *solo queue*, sem coordenação entre 5 desconhecidos, esse
  *counter-pick* garantido pesa mais.
- No profissional, as equipes valorizam muito a **primeira escolha**
  (que é do azul), e coordenam o *draft* inteiro.

**Resposta pronta:** "O trabalho mede a inversão com firmeza estatística
e propõe uma hipótese, mas delimita sem comprovar. Testar a hipótese
exigiria a ordem do *draft*, que a API pública não expõe."

### 13.7 Conversão de vantagem ("macro ganha jogo")

Com **+2.000 a +4.000 de ouro aos 15 minutos**, o azul venceu:
- **81,5%** no profissional (3.294 jogos)
- **73,7%** no *solo queue* (5.166 partidas)

Diferença de **7,8 pontos**, estatisticamente muito significativa (z =
8,3; p < 0,001).

**Leitura:** a **mesma vantagem** vale mais nas mãos de um time
coordenado. Os profissionais "convertem" melhor a vantagem em vitória.

**Detalhe honesto:** a faixa de +4.000 a +6.000 no profissional tem só 72
jogos, então é indicativa. E uma versão antiga do texto falava em 16
pontos de diferença; com mais dados caiu para 7,8.

### 13.8 Por que isso importa para o modelo

O viés de lado é um **fator de confusão** que qualquer modelo de *solo
queue* precisa controlar: o lado carrega informação sobre o resultado sem
refletir o estado da partida (Seção 6, conclusão). É também o que a
limitação da taxa-base mostra: no empate total, o modelo dá 49-51% ao azul,
mas os dados dizem 46-48% (Parte 10.7).

**Cuidado:** uma versão antiga falava em "atalho" e dizia que o lado
distingue os times "sem nenhuma propriedade do jogo". O texto final não
usa essa formulação; use a frase acima.

---

## 14. A interface em linguagem natural (*text-to-SQL*)

### 14.1 O que é

O usuário escreve uma pergunta em português, por exemplo: **"Quais os 5
campeões mais jogados?"**. O sistema:
1. **Roteia:** decide se a pergunta é sobre o *solo queue*, o competitivo
   ou as duas bases (regras sobre o esquema; um modelo pequeno só no que
   sobra). Se for ambígua, responde nas duas e mostra lado a lado.
2. Manda a pergunta + a descrição do banco para um **modelo de
   linguagem** (LLM: Claude Haiku, da Anthropic).
3. O LLM devolve uma consulta **SQL** (a linguagem dos bancos de dados).
4. O sistema **valida** essa SQL (4 camadas de segurança) e confere que
   ela **não mistura** as duas bases.
5. Executa no banco **real**, em transação **somente leitura**. Se o banco
   recusar a SQL, refaz **uma** vez passando o erro ao modelo.
6. Mostra o resultado e uma explicação em português.

**Exemplo real do *benchmark* (pergunta 2):**
- Pergunta: "Quais os 5 campeões mais jogados?"
- SQL: `SELECT champion_name, COUNT(*) AS n FROM participants GROUP BY
  champion_name ORDER BY n DESC LIMIT 5`

### 14.2 As 4 camadas de segurança (decore)

Deixar uma IA escrever SQL num banco é perigoso: ela poderia apagar
dados. Por isso, **4 "seguranças na porta"**:

1. **Só um comando, e só de leitura:** tem que começar com `SELECT` (ou
   `WITH ... SELECT`), e não pode ter `;` encadeando outro comando.
2. **Palavras proibidas bloqueadas:** `insert`, `update`, `delete`,
   `drop`, `alter`, `create`, `truncate`, `grant`, `revoke`, `copy`.
3. **Lista fechada de tabelas:** só pode consultar as 9 tabelas
   permitidas (não pode, por exemplo, ler as tabelas brutas).
4. **Tempo máximo:** o banco cancela qualquer consulta que passe de **10
   segundos** (`statement_timeout`).

Desde 2026-11-05 há uma **5ª proteção, no próprio banco**: a consulta roda
em transação **somente leitura**. Se o validador falhasse, o banco ainda
recusaria escrever (`tests/test_run_query_readonly.py`).

**Por que isso também protege contra *SQL injection*:** a entrada do
usuário nunca é colada direto na SQL; o que roda é só o que passou pelas
4 camadas.

### 14.3 Escolhas técnicas com motivo

- **`temperature = 0`:** faz o LLM dar **sempre a mesma resposta** para a
  mesma pergunta. Necessário para o *benchmark* ser reproduzível.
- **`max_tokens = 1200`:** com 500, perguntas complexas tinham a SQL
  **cortada no meio**, gerando erro. Calibrado com casos reais. E o
  código **detecta** quando a resposta foi cortada e avisa o usuário, em
  vez de executar SQL quebrada.
- **Erro com a SQL junto:** se a consulta falha no banco, o erro mostra a
  SQL e a causa, para dar para entender o que aconteceu.

### 14.4 Duas medidas, e por que não se somam (Apêndice B)

**1. *Benchmark* de referência (26 perguntas, 22 *solo queue* e 4 profissional).**
- "Acurácia de execução" = o resultado da SQL gerada bate com o da SQL de
  referência.
- **23 de 26 (88%)** em todas as execuções até 3/11. As 3 falhas (5, 12 e
  22) eram da mesma família: "com pelo menos N partidas", coluna a mais.
- **Hoje dá 26 de 26, mas isso NÃO é uma medida independente**: as regras
  novas do esquema (amostra mínima) foram escritas **conhecendo** essas 3
  falhas. É a medida de regressão, não a nota.
- Curiosidade: uma execução deu 22/26 porque rodou ao mesmo tempo que a
  coleta escrevia no banco.

**2. Conjunto cego (50 perguntas, 51 a 100) = a nota que vale.**
- Elaboradas pelo autor **fora do ciclo de ajuste**, rodadas **uma única vez**
  com o sistema congelado (o *hash* dos arquivos ficou gravado) e conferidas
  uma a uma contra o banco, com uma consulta independente por pergunta.
- **30 de 50 (60%)**, intervalo de 95% de 46% a 72%: 24 certas, 6 recusas
  certas (o banco não tem o dado), 11 parciais, 8 erradas, 1 recusa indevida.
- Três repetições com o sistema parado: **nenhum veredito mudou**.
- Versões anteriores nas mesmas 50 perguntas: 22 e 24 de 50. Ganho real, mas
  modesto; o que mais mudou foi o tipo de erro (erros sem resposta: 8 → 1).
- **MEDIDA PRINCIPAL: gabarito automático, 181 de 203 (89,2%), IC 95% 84,1%–92,7%.** Cada pergunta tem SQL de referência escrita antes da execução e um programa compara (sem avaliador humano): 166 de 187 respondíveis e 15 de 16 recusas esperadas. Das 22 falhas, todas do sistema: nomes de entidade (MonkeyKing escrito 'Monkey King', liga tratada como equipe), eliminações lidas como kills+assists, roteamento. Duas correções (`entidades.py` e checagem de eliminações) vieram depois e **não foram medidas de ponta a ponta** . Limites: perguntas de template e famílias que o autor conhecia.
- **Segundo conjunto de 50 escrito à mão (101 a 150, perguntas inéditas):** **27 de 50 (54%)**, IC 95% 40%–67%: 18 certas, 9 recusas certas, 9 parciais, 13 erradas, 1 recusa indevida. Os intervalos se sobrepõem: as correções feitas depois do primeiro conjunto **não elevaram** o acerto em perguntas novas. Falha dominante: sem o dado (primeira torre, primeiro sangue, série), 9 ou 10 de ~19 perguntas receberam um substituto sem rótulo em vez de recusa.
- **O ponto central (1º conjunto):** 7 das 50 respostas estavam **erradas e pareciam certas**
  (ex.: "sequência de vitórias" que era o total de vitórias; 86.699 partidas
  "sem barão" quando eram 6.633). Só 2 falharam de forma visível. O
  validador garante a **segurança**, não o **sentido** da consulta.
- Limites declarados (6.1): 50 perguntas, **um só avaliador**, sem segunda
  leitura; o autor viu o texto das perguntas antes de congelar o sistema.

### 14.5 Honestidade da IA: dado medido x conhecimento geral

**Regra do projeto:** a plataforma **separa** o que vem dos **dados** do
que vem do **conhecimento geral** da IA.
- Na consulta em linguagem natural, se a IA quiser comentar algo que os
  números não mostram, ela precisa começar com **"Leitura de jogo:"**,
  deixando claro que não veio dos dados.
- Na orientação estratégica (*coach*), o que vem do histórico real
  (*matchups*, sinergias, itens) é rotulado como dado; o resto é rotulado
  como conhecimento geral.
- **A IA nunca inventa estatística.** Se um número não foi calculado do
  banco, ele não aparece como número. **Medido em 2026-11-04** (Apêndice B,
  `src/coach/audit_grounding.py`): em 36 respostas do coach, 453 números, 0
  estatísticas inventadas depois de revisar à mão os 13 que o detector não
  achou nos dados (8 somas, complementos ou arredondamentos dos dados, 2 de
  formato, 3 limiares de conhecimento geral); 167 de 167 porcentagens e 52 de
  52 contagens de jogos batem com os dados; 87 de 87 itens sugeridos vêm da
  lista real; todas terminam com a ressalva de limites. **Limite que vocês
  devem dizer:** isso mede número, não afirmação qualitativa. No caso 5 a IA
  disse que dois campeões estavam "muito atrasados em ouro e experiência",
  mas nesse modo só há a diferença do time.
- O modelo de ML **não vê** itens, posição nem ondas de minion; qualquer
  orientação sobre isso é marcada como inferência.

---

## 15. Perguntas prováveis da banca, com respostas

### 15.0 Como uma banca de TCC costuma funcionar

Pesquisa na web em 2026-11-02. **Nenhum documento público da UNISINOS
descreve o rito da banca de Ciência da Computação**; o próprio site manda
consultar o Guia do Aluno de Graduação (portal Minha Unisinos) e a
coordenação. O que segue é o padrão de regulamentos de outros cursos de
computação no Brasil, para você saber o que esperar, **não a regra da
UNISINOS**. Confirme com o orientador.

- **Formato comum:** apresentação oral de 15 a 30 minutos (20 é o mais
  frequente), depois arguição de cada membro (até ~15 min cada), depois
  deliberação a portas fechadas e resultado na hora.
- **Composição comum:** o orientador preside e mais um ou dois
  professores avaliam. Em geral o orientador não faz a arguição dura; quem
  pergunta são os outros membros.
- **Critérios comuns nas fichas:** clareza da apresentação, domínio do
  tema, metodologia, relevância e coerência dos resultados com os
  objetivos, qualidade do texto e da formatação, e **respeito ao tempo**.
- **Regra prática de slides:** cerca de 1 minuto por slide (20 minutos →
  até ~20 slides, o roteiro do site tem 14).
- **O que as bancas perguntam (padrão):** justificativa das escolhas
  metodológicas, limitações, implicações dos resultados, relação entre
  teoria e dados e continuidade. A banca pergunta mais onde acha que
  há ponto fraco, não onde você está seguro.
- **Em trabalhos de ML, os temas típicos:** escolha do modelo frente a
  alternativas mais simples, *baseline* (classe majoritária), métricas,
  divisão treino/teste e número de dobras, vazamento de dados (inclusive
  no pré-processamento), *overfitting* e generalização.

**Como responder (pesquisa de 2026-11-02, fontes de preparação para
defesa; são conselhos práticos, não norma):**

- Ouça a pergunta inteira antes de começar. Se não entendeu, peça para
  reformular; isso não é sinal de despreparo.
- "Deixa eu pensar um instante" é uma resposta válida. A banca prefere
  uma pausa a uma resposta apressada.
- Se não souber, **não blefe**: muitas vezes o avaliador sabe a resposta e
  está testando a honestidade. Diga "não medi isso neste trabalho", ofereça
  o que o trabalho mostra de mais próximo e, se couber, diga que é um
  desdobramento para trabalhos futuros.
- Pergunta que aponta uma fraqueza: concorde com o que for verdade, diga
  onde está declarado no texto e por que não invalida o achado. Não
  responda na defensiva.
- Treine **em voz alta**; pensar a resposta em silêncio não basta.

**Slides e demo:**

- 1 slide por minuto, no máximo; para 20 minutos, entre 12 e 20 slides. Uma
  ideia por slide, fonte de 24 pt ou mais. O erro mais comum é tentar mostrar
  tudo.
- Ensaie com cronômetro pelo menos três vezes. Estourar o tempo costuma
  contar contra.
- Demo ao vivo convence mais que captura de tela, mas só com 3 a 5 coisas.
  Deixe o ambiente pronto (API e *frontend* rodando) antes de a banca
  entrar.
- **Grave um vídeo da demo** funcionando, para o caso de algo falhar, e
  leve os slides em PDF num pendrive. Abra a apresentação no equipamento
  da sala antes, se puder: outro computador pode desmontar transições e
  fontes.

**O que confirmar com o orientador:** tempo de apresentação e de
arguição, quem são os membros (e a área de cada um, para prever o tipo de
pergunta), se haverá projetor e se a demo ao vivo é bem-vinda, e a política
da UNISINOS sobre uso de IA (não há documento público achado).

Treine em voz alta. As respostas são curtas de propósito; se pedirem
mais, use as partes do guia.

**1. "Explique o trabalho em poucas palavras."**
"Construí uma plataforma que coleta partidas reais de *League of
Legends*, prevê o vencedor a partir do estado do jogo num minuto
específico, explica a previsão e deixa o usuário perguntar sobre os dados
em português. Os três modelos comparados empataram, e o adotado, o
XGBoost, acerta 76% aos 15 minutos, com AUC de 0,85."

**2. "Por que 76% é um bom resultado?"**
"Porque o chute mais simples, que é sempre apostar no vermelho, acerta
53%. O modelo fica 23 pontos acima disso usando só 5 informações do
minuto 15, com 15 minutos de jogo ainda pela frente. E a AUC de 0,85
mostra que ele separa bem vitórias e derrotas."

**3. "Daria para chegar a 90%?"**
"Não com os dados atuais. Testei 11 formas de enriquecer as *features* e
nenhuma melhorou. O que melhorou foi volume de dados. O próximo ganho
exigiria a ordem do *draft* e o estado das ondas, que a API pública não
fornece. Aos 25 minutos a AUC já chega a 0,909, mas aí a previsão é
menos útil, porque o jogo está quase decidido."

**4. "O que é vazamento de dados e como vocês evitaram?"**
"É o modelo usar informação que ele não teria no momento da previsão,
normalmente do futuro. Evitei usando só os frames da *timeline* até o
minuto do corte. Usar o total de abates da partida, por exemplo, seria
colar com o gabarito."

**5. "Por que XGBoost e não uma rede neural profunda?"**
"Comparei três famílias por medição. Para dados em tabela, com dezenas de
milhares de linhas, métodos de árvores seguem competitivos com redes
neurais (Grinsztajn et al., 2022), e foi o que aconteceu: a rede (MLP)
empatou com o XGBoost, sem superar as árvores de forma distinguível. Uma
rede profunda pediria muito mais dados e não teria o que explorar em cinco
números por partida. O XGBoost também se integra com o SHAP de árvore,
que dá explicações exatas."

**6. "O MLP ganhou aos 10 minutos. Por que não usaram ele?"**
"A diferença foi de 0,0016 de acurácia, irrelevante. O XGBoost vinha do
TCC I e já sustentava a interface, com o SHAP de árvore; o MLP ficou no
mesmo patamar e o quadro dos quatro cortes está no Apêndice C."

**7. "Os hiperparâmetros estão bem ajustados?"**
"Sim. Uma busca em grade com 27 combinações e validação cruzada achou a
melhor com AUC 0,8475; a de produção tem 0,8473, segundo lugar, com a
mesma profundidade. Diferença de 0,0001."

**8. "O que é a validação cruzada que vocês usaram?"**
"Cinco *folds* estratificados com semente fixa 42. Divido as partidas em
cinco pilhas com a mesma proporção de vitórias, treino com quatro e testo
na quinta, cinco vezes. Toda partida é testada sem ter sido vista no
treino, e qualquer um reproduz os números." Se perguntarem por que não 10
(o Kohavi recomenda 10): custo da busca em grade, e cada dobra de teste
ainda tem cerca de 7.800 partidas (Parte 9.6).

**9. "Por que o vermelho vence mais no *solo queue*?"**
"O trabalho mede isso com firmeza, mas a causa é hipótese: o vermelho
escolhe por último no *draft* e garante o *counter-pick*, e no *solo
queue*, sem coordenação, isso pesa mais. No profissional, a primeira
escolha é mais valorizada e o padrão inverte. Testar a causa exigiria a
ordem do *draft*, que a API não expõe."

**10. "Como vocês sabem que o viés não é sorte?"**
"Mais de 41 mil partidas, intervalos de confiança de Wilson que excluem
50% em três das quatro regiões, e quatro testes de robustez. Na Coreia o
intervalo inclui 50%, e o texto diz isso explicitamente."

**11. "O texto dizia que o viés tinha um pico. Mudou?"**
"Sim, e isso está registrado no texto. Com a amostra ampliada e a
correção de Holm para comparações múltiplas, as quatro taxas ficaram
indistinguíveis. O viés existe e é constante; o pico era efeito de
amostra pequena. Preferi reportar o resultado negativo a manter a versão
antiga."

**12. "Por que o modelo não foi retreinado com as 41.063 partidas?"**
"As *features* foram congeladas com 39.426. As 1.637 a mais, quase todas
da Coreia, mudariam o treino em cerca de 4%, e o ganho medido por volume
é pequeno nessa escala. Retreinar invalidaria as métricas e a bateria de
validação já feitas. Está declarado como limitação na Seção 6.1 (detalhe no Apêndice F), com o
comando para quem quiser retreinar."

**13. "O que é SHAP e por que não LIME?"**
"SHAP vem do valor de Shapley, da teoria dos jogos: divide de forma justa
quanto cada variável empurrou a previsão. Lundberg e Lee mostraram que é
a única solução com consistência. O LIME depende de como se define a
vizinhança, então dá explicações menos estáveis."

**14. "Como garantem que a IA não inventa dados?"**
"Duas regras: tudo que é número vem de consulta ao banco, e o que é
conhecimento geral da IA é rotulado como 'Leitura de jogo'. Nomes de
itens são buscados num catálogo oficial no banco, nunca da memória da
IA."

**15. "A interface de linguagem natural é segura?"**
"Tem quatro camadas de validação (só um SELECT, palavras de escrita
bloqueadas, lista fechada de tabelas, tempo máximo de 10 segundos) e,
desde 5 de novembro, o banco roda a consulta em transação somente
leitura. A entrada do usuário nunca é colada direto na SQL. Segurança é
diferente de acerto: a consulta pode ser segura e responder outra coisa."

**16. "Por que 60% e não 88%?"**
"São duas medidas diferentes. O benchmark de 26 perguntas deu 88% e hoje
dá 26 de 26, mas as regras do esquema foram escritas conhecendo as
falhas dele, então não é independente. Montei um conjunto cego de 50
perguntas, rodado uma vez, com o sistema congelado, e conferi cada
resposta contra o banco: 30 de 50, 60%, com intervalo de 46% a 72%.
Depois corrigi falhas gerais e rodei um segundo conjunto, de perguntas
inéditas: 27 de 50, 54%. Como o julgamento era meu, criei um gabarito automático,
com SQL de referência escrita antes e comparação por código: 181 de 203, 89,2%.
Esse é o número principal; os de 60% e 54% mostram as falhas que ele corrigiu."

**16b. "O conjunto cego é mesmo cego?"**
"Foi elaborado por mim, fora do ciclo de ajuste, e o sistema foi
congelado antes de rodar, com o hash dos arquivos gravado. Mas eu vi o
texto das perguntas antes de congelar, e uma regra de recusa que
acrescentei toca em um tema que o conjunto também sonda. Está declarado
no Apêndice B. Por isso o chamo de conjunto cego com ressalvas."

**16c. "O que o sistema erra, e é grave?"**
"Em 7 de 50 respostas devolveu um número ou lista plausível e errado,
como uma sequência de vitórias que era o total de vitórias. É o risco
principal: o erro não aparece. Só duas falharam de forma visível. Está nas
limitações (6.1) e é o primeiro dos trabalhos futuros de linguagem
natural: verificar o resultado depois da execução."

**16d. "Quem julgou as respostas?"**
"Um só avaliador, com uma consulta independente por pergunta, e o motivo
de cada veredito está no Apêndice B. Não houve segunda leitura; está
declarado como limitação. Um veredito foi revisto: a pergunta 89 passou
de recusa certa para parcial, porque o solo queue respondia."

**16e. "O roteamento ajudou?"**
"Sim, mas pouco: 22 de 50 na versão mais antiga, 24 sem o roteamento e 30
na atual. O que mais mudou foi o tipo de erro: respostas sem resultado
caíram de 8 para 1, e perguntas de equipe deixaram de ser respondidas na
base errada."

**17. "Qual a contribuição científica?"**
"Três: a integração completa numa plataforma, que nenhum trabalho
relacionado entrega; a medição do viés de lado no *solo queue* de elo
alto e sua inversão no profissional; e a quantificação de que a mesma
vantagem de ouro vale mais no profissional."

**18. "Os resultados valem para outros elos ou outros jogos?"**
"Não. É validade externa limitada: só Desafiante e Grão-Mestre, fila
ranqueada, quatro regiões. O recorte foi uma decisão de escopo. A
arquitetura é reaproveitável, mas os números não se estendem."

**19. "Por que só 5 *features*?"**
"Porque são o estado agregado de cada time no minuto do corte, que é o
que a *timeline* oferece com confiabilidade. Testei 11 acréscimos e
nenhum ajudou; adicionar variáveis que não ajudam só deixa o modelo mais
complicado."

**20. "Por que referências tão antigas, como 1982 e 2001?"**
"São as obras originais dos métodos, como Random Forest e AUC. Os
estudos de domínio são todos de 2021 a 2026."

**21. "Qual a diferença entre pesquisa bibliográfica e documental?"**
"Bibliográfica usa artigos e livros já analisados por outros autores.
Documental usa documentos técnicos ainda não analisados academicamente,
como a documentação da API da Riot."

**22. "Por que a predição não é em tempo real?"**
"A arquitetura foi pensada para isso, porque o modelo aceita qualquer
estado de jogo. A barreira é o acesso a dados ao vivo, não o modelo.
Está em trabalhos futuros."

**23. "O que acontece com uma partida que acabou antes do corte?"**
"Ela não entra naquele corte. Por isso aos 25 minutos há 26.837
partidas, contra 39.188 aos 15."

**24. "Por que o EUN1 tem só 20 partidas?"**
"Nunca foi região-alvo; o escopo sempre foi BR1, EUW1, KR e NA1. As 20
apareceram de carona e o texto as exclui por amostra insuficiente."

**25. "Quantas páginas tem a plataforma?"**
"Seis páginas de visualização: Início, Dashboard, Campeões, Partidas,
Competitivo e Simulador. A Consulta NL, a interface em linguagem natural,
é o objetivo g e fica à parte." (Atenção: no menu lateral das capturas
aparece "Consulta NL" e não aparece "Partidas", porque a análise de
partida abre ao clicar numa partida. Se a banca contar o menu, explique
isso.)

**26. "Você usou IA para fazer o trabalho?"** Ver a Parte 20.

**27. "Por que esses trabalhos relacionados e não outros?"**
"Escolhi para cobrir cada camada da plataforma (predição,
explicabilidade, linguagem natural e visualização), dentro da janela de
cinco anos. O núcleo veio do levantamento do TCC I; no TCC II acrescentei
quatro estudos de *League of Legends* para comparar a acurácia com
trabalhos do mesmo jogo." (Parte 5.2.1)

**28. "Por que três modelos?"**
"Conversando com o orientador, decidimos comparar o XGBoost com *Random
Forest* e uma rede neural para ver as diferenças de resultado entre
famílias: *bagging*, *boosting* e rede neural. Os três ficaram próximos, e
o XGBoost foi o mais estável." (Parte 9.1)

**29. "Por que só Desafiante e Grão-Mestre?"**
"Escopo. É uma população fechada, que a API entrega inteira e que cabia
na coleta com a chave de desenvolvedor. O custo é a validade externa,
declarado na 6.1." (Parte 6.1)

**30. "Por que 5 dobras, se o Kohavi recomenda 10?"** Parte 9.6.

**31. "Qual é o seu *baseline*?"**
"A classe majoritária: sempre apostar no vermelho acerta 53,4% aos 15
minutos. O XGBoost fica 23 pontos acima. Antes da busca em grade houve
também um modelo de referência com parâmetros padrão
(`train_baseline.py`)."

**32. "Usaram conjunto de teste separado? Validação aninhada?"** Não;
Parte 9.6 (a configuração veio da base de 10 mil e ficou a 0,0001 da
melhor na base final).

**33. "As partidas do mesmo jogador não vazam entre treino e teste?"**
"Podem: o sorteio é por partida, e o mesmo jogador aparece em várias. O
texto declara isso como ameaça à validade interna (6.1). As *features* são
do estado da partida, não do jogador, o que reduz o efeito, mas uma divisão
por jogador seria mais rigorosa."

**34. "Qual a diferença de uma Random Forest para o XGBoost?"**
"A Random Forest treina árvores independentes em amostras sorteadas e
faz a média (*bagging*, reduz variância). O XGBoost treina em sequência,
cada árvore corrigindo o erro das anteriores (*boosting*, reduz viés), com
regularização."

**35. "O que é a AUC, em uma frase?"**
"A probabilidade de o modelo dar nota maior a uma partida que o azul
venceu do que a uma que ele perdeu, sorteadas ao acaso."

**36. "Por que o viés não entra como *feature*?"**
"Entra implicitamente: todas as *features* são azul menos vermelho, então
o modelo aprende a vantagem do lado pelo valor de base (a taxa média de
vitória do azul, que ele recebe quando todas as diferenças são zero). O
problema é que ele
a subestima no empate (49-51% contra 46-48% nos dados); está na 6.1 e no
Apêndice F."

**37. "Se fosse começar de novo, o que faria diferente?"**
"Congelaria a coleta antes de treinar, para não ter duas bases (41.063 e
39.426), e dividiria as dobras por jogador. E tentaria desde o início uma
fonte com a ordem do *draft*, que é o dado que falta para testar a
hipótese do viés."

**38. "Qual foi a maior dificuldade?"**
Escolha uma história da Parte 19 e conte em 30 segundos: problema,
como percebeu, como corrigiu, o que mudou no processo. A melhor é a das
torres (o bug invertido e o reprocessamento a partir do JSON bruto) ou a
do "pico" do viés refutado com mais dados.

**39. "A plataforma tem usuários? Foi avaliada com pessoas?"**
"Não houve avaliação com usuários; os dados são secundários e não houve
participação de pessoas. O que foi medido é a acurácia do modelo e da
interface em linguagem natural. Avaliação de usabilidade seria um trabalho
futuro natural."

**40. "Por que tanto texto nos apêndices?"** Comparação feita em
2026-11-02 com os 10 TCC II aprovados da pasta de exemplos: 7 têm
apêndice, e todos usam o apêndice para **material** (link do GitHub,
figuras de teste, questionários, entrevistas, termos, fotos, circuitos).
Nenhum tem notas em prosa como os nossos D, E e G. O modelo do professor
permite ("texto ou documento elaborado pelo próprio autor, com a finalidade
de complementar seu trabalho"), então não é erro, mas foge do costume.
Resposta: "O corpo tem tudo o que sustenta as conclusões, dentro das 30
páginas. Os apêndices guardam o detalhe para quem quiser conferir: a origem
de cada número, os comandos que reproduzem cada resultado e as limitações
com os números. Nada que a conclusão use está só no apêndice."

**41. "Quanto custa rodar a interface em linguagem natural?"** Não há
medição de custo no TCC; não invente número. Diga que usa um modelo
pequeno da Anthropic (Haiku), com `max_tokens` 1.200 por consulta, e que o
custo por pergunta não foi objeto do trabalho.

**42. "Birant e Birant chegam a 95%. Por que o seu é 76%?"** (conferido no
artigo, 2026-11-02)
"Os atributos deles são resumos do fim da partida, como abates, assistências
e ouro por jogador, que o próprio artigo chama de *post-game*. O meu modelo
só vê o estado até o minuto do corte. Usar o resumo final seria o vazamento
de dados que Kaufman et al. descrevem: o modelo veria o resultado antes de
prever."

**43. "García-Méndez e Arriba-Pérez passam de 90%. Por que o seu não?"**
"O trabalho deles é de CS:GO profissional, com outra base e outras
variáveis, e chega a 92,5%. Não é o mesmo jogo, nem o mesmo problema. O que
eu tomo deles é a necessidade de explicar a previsão, e o meu SHAP faz
isso."

**44. "Hodge chega a 85% com 5 minutos. O seu fica em 76% aos 15."**
"O 85% é de Dota 2 profissional, medido em 28 jogos ao vivo de um torneio, e
é um teto ('até'). O meu é a média de validação cruzada em 39 mil partidas de
elo alto de LoL, outro jogo e outra base. Não são comparáveis diretamente."

**45. "O Maymin escreve que o mapa de calor não é possível com os dados da
API. O seu sai da API?"** "Sai, mas é mais grosseiro: o dele vem de
rastreamento óptico a cada segundo; o meu agrega as posições por minuto da
*match-v5* (linha do tempo). O texto já admite que o meu é mais simples."

**47. "O SiriusBI tem mais de 93% em SQL. Por que o seu é 88%?"** (conferido
no artigo, 2026-11-02)
"Os 93% a 97% do SiriusBI são de produção, em consultas reais e mais
simples de três setores da Tencent, com um modelo ajustado nos dados do
cliente. Nos conjuntos de teste dele, o resultado é menor: 79% a 83% em 182
consultas industriais e 65% a 69% no BIRD. O meu benchmark tem 26 perguntas
sobre o meu esquema, sem ajuste do modelo: é a mesma ordem de grandeza, mas
não é o mesmo teste. O próprio artigo explica que a produção dá mais por
causa de conhecimento mais completo e consultas mais uniformes."

**48. "Uma regressão logística não faz o mesmo? Por que XGBoost?"** (medido em
2026-11-03, `src/models/baseline_e_diferencas.py`, Apêndice C)
"Porque o limite está nas cinco variáveis, não no modelo: uma regressão logística, medida como baseline em 2026-11-03, chega a 0,7631 de acurácia e 0,8483 de AUC aos 15 minutos. O XGBoost ficou 0,0010 abaixo em AUC, com intervalo que exclui zero aos 10, 15 e 20 minutos, mas é uma diferença de milésimos, e o texto diz que a logística fica à frente. A comparação com árvores e rede neural era o objetivo e do TCC I, e o XGBoost foi escolhido antes desse baseline ser medido. Não digam que ele captura interações caso as variáveis cresçam: com as 59 variáveis novas a logística ganhou mais que ele (+0,0080 contra +0,0044, Apêndice K). O que o XGBoost oferece hoje é o SHAP exato de árvore e a integração já validada; trocar de modelo não mudaria o resultado prático."

**46. "O que a literatura diz sobre os três modelos empatarem?"** "Do et al.
(2021) testaram cinco algoritmos e ficaram entre 72,7% e 75,4%, com o
*gradient boosting* acima da rede neural; Guan e Tung (2026) acharam as duas
arquiteturas deles estatisticamente indistinguíveis. Com poucas variáveis
agregadas, o limite está nos dados."

---

## 16. A plataforma (o sistema que foi entregue)

### 16.1 Arquitetura

```
Riot API → coletor (com limite de pedidos) → JSON bruto no banco
                                               │ ETL
                                               ▼
                      tabelas organizadas (PostgreSQL)
Oracle's Elixir (CSV) → tabelas do profissional
                                               │
             ┌─────────────────────────────────┼───────────────┐
             ▼                                 ▼               ▼
   features por corte            modelos XGBoost por corte   API (FastAPI)
                                                                │
                                                                ▼
                                                     site (React)
```

### 16.2 Tecnologias (Seção 4.8)

| Camada | Tecnologia | Para quê |
|---|---|---|
| Coleta, ETL, modelos | **Python** (pandas, NumPy, scikit-learn, XGBoost, SHAP) | Todo o processamento |
| Banco | **PostgreSQL** | Guardar os dados |
| Servidor | **FastAPI** | A "API própria" que o site consulta |
| Site | **React + TypeScript** (Vite, Tailwind, TanStack Query, **Recharts** para gráficos) | O que o usuário vê |
| IA (texto) | **API da Anthropic (Claude)** | Linguagem natural e orientação |

**Regra (Seção 4.8, regra do modelo do professor):** na metodologia do
TCC II, ferramentas e materiais são **descritos**, não referenciados com
citação. Por isso a 4.8 não tem citações.

### 16.3 As 6 páginas (recortes na Seção 5, telas inteiras no Apêndice E)

**No corpo (Seção 5), cinco figuras recortadas:** Figura 1 Competitivo
(viés de lado e conversão, 5.3); Figura 2 SHAP nos quatro cortes (5.4);
Figura 3 análise de partida com mapa de calor (5.5); Figura 4 Simulador,
aba Estado (5.5); Figura 5 consulta em linguagem natural (5.6).

**No Apêndice E, as seis telas inteiras (Figuras 6 a 11):**

| Figura | Página | O que mostra |
|---|---|---|
| 6 | **Início** | Busca unificada e rankings |
| 7 | **Dashboard** | Indicadores gerais e o **viés de lado por região** |
| 8 | **Campeões** | Estatísticas por campeão, itens finalizados, presença no profissional |
| 9 | **Partidas** | Análise de uma partida: probabilidade minuto a minuto, **mapa de calor**, modo "e se", leitura de *draft* |
| 10 | **Competitivo** | Comparação *solo queue* × profissional, por ano |
| 11 | **Simulador** | Aba Estado (modelo de ML e SHAP); as abas Composição (heurística) e Explicabilidade ficam na mesma página |

**Destaques para explicar:**
- **Mapa de calor:** mostra onde os jogadores estavam em cada minuto, a
  partir das posições da *timeline*. Inspirado em Wallner et al. (2023).
- **Modo "e se":** o usuário muda o estado (ex.: "e se o azul tivesse 3
  mil de ouro a mais aos 14 minutos?") e vê como a probabilidade muda.
  Responde perguntas de **estado**, não de **ação** (ele não sabe dizer
  "e se o jogador tivesse ido para o dragão").
- **Composição no Simulador é heurística, não ML:** usa a taxa de vitória
  histórica dos campeões, e a tela **avisa** isso, para não confundir
  com a predição do modelo.
- **Correção de amostra pequena (*shrinkage*):** um campeão com 3
  vitórias em 3 jogos não tem "100% de vitória de verdade". O sistema
  "puxa" esse número para a média até ter amostra suficiente.

---

## 17. Testes e verificações de qualidade

| Verificação | O que faz | Resultado |
|---|---|---|
| `tests/smoke_test.py` | Roda o pipeline inteiro com dados sintéticos, sem tocar nos dados reais | funcional |
| `tests/validate_predictions.py` | Bateria de comportamento do modelo: vantagem real aumenta a chance? casos extremos dão probabilidade alta? o viés é constante? torres crescem aos 25? | **Aprovado com ressalvas** |
| `docs/verifica_tcc.py` | **20 checagens** que comparam os números do texto do TCC com os artefatos reais | **20/20, consistente** |
| `docs/confere_docx.py` | Confere a formatação do `.docx` (títulos, referências, legendas) | conforme |
| Frontend | 31 testes automáticos + verificação de código | ok |

**A checagem retrospectiva** (dentro da bateria): rodando o modelo
minuto a minuto em 150 partidas reais, a previsão dos últimos minutos
apontou o vencedor certo em **140 de 150 (93%)**. Isso **não é** a
acurácia oficial do modelo (é no fim da partida, quando já está quase
decidido); é um teste de sanidade do pipeline completo.

**"Aprovado com ressalvas" quer dizer:** nenhuma checagem falhou; as
ressalvas são casos em que uma *feature* tem peso quase nulo naquele
corte (ex.: torres aos 10 minutos), então não dá para exigir direção
dela.

**Por que o `verifica_tcc.py` existe:** número velho no texto é o erro
mais comum de TCC. Esse script compara o texto com os arquivos de
resultado e **reprova** se algo divergir.

---

## 18. Limitações e trabalhos futuros

### 18.1 Limitações (Seção 6.1 e Apêndice F)

Saber as limitações **é ponto a favor**. A banca respeita quem conhece
os limites do próprio trabalho.

1. **Amostras pequenas em recortes finos** (combinações específicas de
   campeões): amenizado com *shrinkage*, não eliminado.
2. **O modelo subestima o viés de lado no empate** (Parte 10.7).
3. **O modelo não viu a última rodada de coleta** (39.426 x 41.063).
4. **Desequilíbrio por região** (NA1 menor) e força desigual da
   evidência (KR inclui 50%).
5. **Um *patch* concentra a maioria das partidas** (16.13), o que limita
   generalizar para outras versões do jogo.
6. **Teto de desempenho das *features*** (11 experimentos negativos).
7. **Sem dados de micro-posicionamento** (ondas de minion): nenhuma API
   pública da Riot oferece. Alternativas (replays `.rofl`, visão
   computacional no minimapa) foram consideradas, não implementadas.
8. **Monotonicidade:** o XGBoost não garante que aumentar só os abates
   nunca diminua a chance, por causa de interações entre variáveis.

### 18.2 Os três tipos de validade (Seção 6.1) — vocabulário de banca

- **Validade de construto:** "estou medindo o que acho que estou
  medindo?". Limite: o modelo não tem o estado das ondas, que um
  analista consideraria importante.
- **Validade externa:** "vale para outros contextos?". Limite: só elo
  altíssimo, fila ranqueada, 4 regiões.
- **Validade interna:** "a conclusão pode ter outra causa?". Limite: as
  partidas foram coletadas em janelas de tempo, então algo sazonal
  (*patch*, eventos) pode se misturar com o que os dados mostram.

### 18.3 Trabalhos futuros (Seção 6.2)

1. **Predição ao vivo** (a arquitetura já aceita qualquer estado).
2. **Seleção de campeão competitiva** no simulador.
3. **Restrições de monotonicidade** no modelo, se necessário.
4. **Ampliar a validade externa:** outras filas, outros elos, outro jogo.

---

## 19. Histórias reais de erros encontrados e corrigidos

Contar uma história dessas mostra maturidade. Todas estão documentadas
no código ou no diário.

**1. As torres estavam no time errado.** No evento de torre destruída
da Riot, o campo `teamId` é o time que **perdeu** a torre, não o que
destruiu. O código somava no time errado. O erro ficou **duas semanas**
num *dashboard* até ser percebido. A correção (`300 - lost` no
`build_features.py`) inverte explicitamente. Como o JSON bruto estava
guardado, bastou reprocessar.

**2. A AUC estava sendo calculada errado.** A primeira versão do script
do Apêndice C calculava a AUC com a **classe prevista** (0 ou 1) em vez
da **probabilidade**. Isso dava 0,7596 aos 15 minutos, quando o correto
é **0,8473**. A AUC precisa da probabilidade, porque mede a qualidade da
ordenação.

**3. A IA inventava itens.** A orientação estratégica e a consulta em
linguagem natural chegaram a citar nomes e estatísticas de itens "de
memória", com erros. A solução foi criar a tabela `items` (catálogo
oficial) e fazer o sistema buscar ali.

**4. Respostas cortadas silenciosamente.** Com limite de 500 *tokens*, a
SQL saía cortada no meio e dava erro de sintaxe. O limite foi para 1.200
e o código passou a **detectar** o corte e avisar.

**5. O "pico" do viés de lado.** Achado reportado com amostra menor e
refutado com amostra maior + correção de Holm. Corrigido no texto, com
registro.

**6. O piloto enganoso do experimento 11.** +0,009 com 199 partidas,
-0,0031 com 2.987. Não foi publicado como descoberta.

---

## 20. Sobre o uso de IA no trabalho

É bem possível a banca perguntar. A melhor resposta é **honesta e
específica**. Antes da banca, **confirme com o orientador a política da
UNISINOS** sobre uso e declaração de IA em TCC.

Fatos para você ter claros:

1. **A IA é parte do sistema** (isso é público e está no texto): a
   consulta em linguagem natural e a orientação estratégica usam o Claude
   (Anthropic). E o projeto tem regras explícitas para a IA não inventar
   dados (Parte 14.5).
2. **O levantamento bibliográfico inicial teve ajuda de IA:** o PDF
   `Pesquisa artigos TCC.pdf` foi gerado com o ChatGPT. Os artigos foram
   triados por título e resumo e os que entraram estão nas referências.
   Se a banca perguntar algo específico de um artigo, você precisa ter
   lido o artigo (vale revisar os 11 estudos de domínio).
3. **O desenvolvimento e a redação tiveram apoio de um assistente de
   programação com IA** (Claude Code), como mostra o histórico do projeto.

Uma forma honesta de responder, se perguntarem: dizer que usou IA como
ferramenta (como componente do sistema, para apoiar a busca de
literatura e para apoiar desenvolvimento e escrita), e que as decisões,
a validação dos resultados e a responsabilidade pelo conteúdo são suas.
O que vai sustentar essa resposta é você **entender** cada decisão, que é
para isso que este guia existe.

---

## 21. Folha de cola: os números para decorar

**Dados**
- 41.063 partidas *solo queue* (BR1 11.936; EUW1 11.744; KR 10.204; NA1
  7.159; EUN1 20)
- 39.426 na base congelada dos modelos; 39.309 viraram *features*;
  39.188 no corte de 15 min
- 99.259 jogos profissionais (2014-2026)
- Fila 420; elos Desafiante e Grão-Mestre
- Limite da API: 20 pedidos/s e 100 a cada 2 min; chave expira em 24 h

**Modelo (XGBoost, 15 min)**
- Acurácia 0,7621 | Precisão 0,7561 | Recall 0,7228 | F1 0,7391 |
  AUC 0,8473
- Hiperparâmetros: 500 árvores, taxa 0,01, profundidade 3
- Validação: 5 *folds* estratificados, semente 42
- AUC por corte: 0,774 / 0,847 / 0,876 / 0,909
- Taxa de vitória do azul na amostra: 46,6%
- Busca em grade: 27 combinações, produção em 2º lugar (0,8473 x 0,8475)
- Com os três ajustados (15 min): XGBoost 0,7621 / 0,8473; MLP 0,7619 /
  0,8477; *Random Forest* 0,7617 / 0,8468 (empate técnico)

**Explicabilidade**
- Ouro e XP dominam; torres saltam de ~0,006 para 0,0928 aos 25 min
  (~15x)

**Experimentos**
- 11 tentativas, nenhuma melhorou
- Volume: 0,8214 → 0,8393 → 0,8473 (ganho de 0,0259, ~9x o melhor
  experimento)

**Viés de lado**
- Vermelho vence: BR1 56,3%; EUW1 53,4%; NA1 52,2%; KR 50,4% (KR inclui
  50%)
- Empatadas: azul 46,4% / 47,9% / 46,7% / 47,1%; Holm p mín. 0,83
- Profissional: azul 53,2%
- Conversão (+2k a +4k aos 15): pro 81,5% x *solo queue* 73,7%; 7,8 pp;
  z = 8,3

**Linguagem natural**
- 23/26 = 88%; 22 *solo queue* + 4 profissional; falhas: perguntas 5,
  12 e 22
- *temperature* 0; *max_tokens* 1.200; tempo máximo 10 s

**Documento**
- 29 páginas do Resumo ao fim das Referências (limite 30, uma linha de folga)
- 31 referências; 11 Figuras (5 no corpo, 6 telas inteiras no Apêndice E);
  30 Quadros (6 no corpo, 24 nos apêndices); Apêndices A-K (G fundamentos dos métodos, H procedência dos dados e chaves da Riot, I objetivos e evidências, J SHAP por corte, K experimentos de precisão, 1 a 19); Anexo A (documentação da Riot)
- limitações: Seção 6.1, com o detalhe no Apêndice F
- `verifica_tcc.py`: 20/20

---

*Fontes deste guia: `docs/tcc2_texto.md` (texto final),
`docs/handoff.md`, `docs/diario_execucao.md`, código em `src/`,
artefatos em `reports/`, e `Downloads/TCC/Pesquisa artigos TCC.pdf`
(levantamento bibliográfico do TCC I).*

---

## Achados da leitura integral dos artigos (2026-11-03), para a defesa

Detalhes e páginas em `docs/conferencia_referencias.md`.

- **"Por que os três modelos empataram?"** Hodge et al. também mediram
  regressão logística, Random Forest e LightGBM e acharam 77,24% a 77,51%.
  Guan e Tung acharam que um modelo simples empata com um modelo misto
  construído como o rival mais forte, e que acrescentar variáveis piora. E
  Grinsztajn remove bases "fáceis demais", em que a logística fica a menos de
  5% do ResNet e do *boosting*: a nossa cairia nesse critério.
- **"Quanto se acerta em partidas profissionais?"** Hodge: 85% é de 28 jogos
  ao vivo; o número mais robusto é 70,81% a 74,59% em 186 jogos aos 20 min.
  Jadowski: 67,3% em 306 jogos, antes da partida.
- **"Por que validação cruzada de 5 dobras?"** Kohavi recomenda 10, e o
  Apêndice C mostra que a diferença é de até 0,0008. Hodge dividiu por tempo
  porque as variáveis deles dependem do histórico; as nossas só dependem da
  própria partida no corte.
- **"E o ouro?"** Maymin tira o ouro do modelo de vitória por considerá-lo
  enganoso, e diz que mais variáveis não melhoram. O nosso modelo usa a
  diferença de ouro como variável principal, e os experimentos com mais
  variáveis foram negativos, o que é coerente.
- **"Os 95% do Birant?"** Usam estatísticas de fim de partida; não é previsão
  em jogo. **"Os 86% do Bahrololloomi?"** Mesma base de cálculo dos pesos, sem
  teste separado. **"Os 92,51% do García-Méndez?"** Incluem o histórico de cada
  jogador; só com o time e o placar são ~75%.
- **"Redes neurais?"** Hornik prova que existe aproximação, mas atribui falhas
  a aprendizado inadequado, poucas unidades ou relação estocástica entre
  entrada e alvo. Hodge diz que as redes "não foram convincentes" nessa escala.
- **"Quem usa elo alto?"** Do et al. cobrem Ferro a Diamante e dizem que não
  representam o 1% do topo; a nossa base é Challenger/Grandmaster.
- **"SiriusBI faz o mesmo que o NLQ?"** Não: a métrica deles (UEX) é mais
  branda, eles têm diálogo em várias rodadas e ajuste fino, e nós temos
  validação em quatro camadas e um *benchmark* de resultado exato.
- **"A validação aleatória não infla o resultado, já que os dados mudam com o
  tempo?"** Kaufman et al. (2012, seções 3.3 e 3.4) avisam exatamente isso.
  Medido em `holdout_temporal.py` (Apêndice C): treinar nas 80% partidas mais
  antigas e testar nas 20% mais recentes, ou treinar nos *patches* 16.10 a
  16.13 e testar nos 16.14 a 16.19, **não reduz a AUC-ROC**. Aos 15 min:
  0,8545 (cronológica) e 0,8542 (por *patch*) contra 0,8432 da divisão
  aleatória de mesmo tamanho; a pior diferença é −0,0004 (20 min, por
  *patch*). **Ressalva:** o tempo se mistura com a região (o teste cronológico
  aos 15 min tem 49,7% de NA1 e nenhuma BR1), então o teste não separa os dois
  efeitos; ele só mostra que o modelo generaliza para uma época e uma mistura
  regional diferentes das do treino.
- **"O Kaufman: o que a sua regra de corte garante?"** O *no-time-machine
  requirement* (eq. 3): só vale variável com informação de momento anterior ou
  igual ao da previsão. O `frames[: corte + 1]` é exatamente isso. O que ele
  **não** cobre sozinho é a escolha de hiperparâmetros nas mesmas dobras de
  avaliação (seção 3.4), já documentada.
- **"E o viés de seleção da coleta? (Kaufman 2012, seção 7)"** O artigo descreve
  o viés de estratificar num colisor. A nossa coleta parte de jogadores que
  estão hoje em Desafiante e Grão-Mestre, e eles chegaram lá em parte por
  vitórias recentes, então a seleção das partidas depende um pouco de
  resultados passados. O efeito não foi medido. O modelo, porém, só usa cinco
  números calculados dentro de cada partida, e o SHAP mostra que nenhuma
  variável suspeita domina (o artigo recomenda exatamente esse tipo de
  verificação, com uma lista de variáveis mais importantes para um
  especialista avaliar).

## Correção de 2026-11-03: fontes de dados

- Jogos profissionais: **99.259** (o `load_pro.py` perdia 2.543; agora apaga por `game_id`). Taxa do azul 53,2% inalterada.
- Elos: jogadores vão de Desafiante a Mestre (93% da tabela `players` é Mestre); 97,2% das partidas têm ao menos um Desafiante/Grão-Mestre, 2,8% só Mestre (769 na KR). Pergunta de defesa provável.
- "timeline-v5" não é endpoint: é método do *match-v5*.
- Arquivos do Oracle's Elixir datados de 4 jul. 2026.

## Perguntas novas depois dos experimentos de precisão (2026-11-03)

**"Vocês tentaram variáveis mais ricas para subir a acurácia?"**
Sim (Apêndice K). Além dos onze experimentos do Quadro 5, testamos mais oito conjuntos: trajetória, diferença por função, objetivos, campeões de cada time e histórico do jogador. O maior ganho, com 64 variáveis e regressão logística, foi +0,0080 de AUC-ROC aos 15 minutos (0,8483 para 0,8555) e +0,0074 aos 25, e se manteve treinando no passado e testando no futuro (+0,0069 a +0,0089). Está abaixo de +0,01. O que mais ajudou foi a diferença por função (+0,0027).

**"Por que não adotaram o modelo novo, se melhorou?"**
Por duas razões, uma de produto e uma de custo. **Produto:** o Simulador, o modo "e se", a composição 5×5 e o coach recebem só as cinco diferenças (ouro, experiência, abates, torres e dragões), que qualquer pessoa pode digitar. As 59 variáveis novas (ouro, nível e dano por função, atributos do time, trajetória dos minutos anteriores) não existem nessas telas; só a análise de partida, que lê a linha do tempo real, teria todas. Adotar o modelo rico no produto inteiro quebraria o Simulador, e usá-lo só na análise de partida deixaria dois modelos para explicar. **Custo:** o ganho é real mas pequeno (0,7 ponto de acurácia aos 15 minutos, de 0,7630 para 0,7699, cerca de 270 partidas em 39.188; AUC-ROC de 0,8476 para 0,8555), e trocar exigiria retreinar os quatro cortes, reexportar, trocar o SHAP de árvore pelo da logística e revalidar tudo. O que o resultado mostra é que o limite está na informação disponível, não no algoritmo: a regressão logística aproveita as variáveis novas mais que o XGBoost (+0,0080 contra +0,0044). Fica como trabalho futuro. **Evitem dizer "cerca de 1 ponto":** são 0,7.

**"O histórico dos jogadores não ajudaria?"**
Testamos (experimento 19), só com partidas anteriores. Mesmo em partidas com 5 ou mais jogadores com 3 ou mais partidas prévias (92% da base), o ganho sobre o estado de jogo foi de +0,0004 aos 15 minutos. A habilidade já aparece no ouro e na experiência. Atenção: numa versão anterior desta análise eu citei cobertura de 31%; era medida errada (diferença de contagem entre os times).

**"Uma chave de produção da Riot traria dados novos?"**
Não pela documentação: a chave de produção aumenta o limite de requisições (a partir de 500 por 10 segundos e 30.000 por 10 minutos) e libera a API de torneios; as APIs padrão são as mesmas. O que a API pública não expõe (ondas de *minions*, ordem de escolha de campeões) continua fora. A aprovação depende da Riot, que avalia se o produto ajuda jogadores de forma mensurável.

**"Por que 0,90 de acurácia aos 15 minutos não é viável?"**
A literatura que consultei reporta 73% a 82% em partida em andamento, e resultados muito acima disso sem discussão de vazamento são suspeitos. Aos 25 minutos já temos AUC-ROC de 0,909.

**"E os 2.543 jogos profissionais que faltavam?"**
Erro do carregador (apagava por ano do arquivo, não por jogo), corrigido. O total passou de 96.716 para 99.259; a taxa do azul no total continua 53,2% (Apêndice H).
