# Achados da leitura sequencial (plano_revisao_final.md, passo 8)

Nada é editado durante a leitura. Cada bloco espera aprovação.

## Bloco 1 — Resumo e Abstract (linhas 34-87)

Conferido: números do Resumo e do Abstract batem entre si e com
`verifica_tcc.py` (41.063; 99.259; 0,7621; 0,8473; 56,3%; 53,2%; 88%; 26
perguntas). "Seis páginas" bate com as rotas de `frontend/src/App.tsx`
(Início, Dashboard, Campeões, Competitivo, Consulta, Simulador).

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 1.1 | 86 | Palavras-chave em inglês sem itálico em *League of Legends* e *machine learning*, enquanto o português (linha 60) usa itálico | `*League of Legends*; ... *machine learning*` | 0 |

Nenhum erro de português, intensidade ou número neste bloco.

## Bloco 2 — 1 Introdução (linhas 91-213)

Conferido: os objetivos a-g da 1.4.2 correspondem um a um aos itens a-g da
Conclusão; "cinco seções, além desta introdução" confere (2 a 6).

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 2.1 | 196 | "dashboards" sem itálico (linha 145 e a Conclusão usam *dashboards*) | `*dashboards*` | +2 |
| 2.2 | 111-115 | O objetivo geral aparece quase igual três vezes (1 Introdução, 1.4.1, Conclusão). É padrão de TCC, só sinalizo; **não mexer** | nenhuma | 0 |

## Bloco 7 — 6 Conclusão (linhas 832-943)

Conferido: itens a-g batem com os objetivos; viés "firme em três das quatro
regiões, KR inclui 50%" bate com a checagem 16 do verificador; "quatro
caminhos" de trabalhos futuros são de fato quatro.

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 7.1 | 843 | Minha edição de hoje ficou truncada: "*account-v1*, *match-v5* com linha do tempo" | "*account-v1* e *match-v5*, com linha do tempo" | +3 |
| 7.2 | 850-851 | "99.259 partidas profissionais": o resto do texto diz "jogos profissionais" | "99.259 jogos profissionais" | 0 |
| 7.3 | 898 | "Onze experimentos" precisa bater com o Quadro 5 (conferir no bloco 6) | pendente do bloco 6 | ? |

## Bloco 3 — 2 Fundamentação teórica (linhas 216-314)

Conferido: referência cruzada "Seção 5.7" existe (Os resultados frente à
literatura); 46,6%/53,4% da taxa-base batem com a Seção 5.4 (linha 676).

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 3.1 | 247 | Frase quebrada, resultado da correção do Breiman: "reduz a correlação entre as árvores, o que limita o ganho de um *ensemble*, e as variáveis preditoras ... evoluem juntas". Falta ligar as duas ideias (a correlação importa **porque** as variáveis são correlacionadas) | "Isso reduz a correlação entre as árvores, que limita o ganho de um *ensemble* e pesa aqui, porque as variáveis preditoras (ouro, abates e torres) evoluem juntas na partida." | ~0 |
| 3.2 | 303-304 | **Intensidade.** "a correção da consulta não é delegada ao modelo: ela é validada antes de tocar o banco". A validação (4 camadas) garante segurança e forma (só `SELECT`, tabelas permitidas, tempo limite), **não** que a consulta responda à pergunta certa; o próprio benchmark (88%, 23/26) mostra erros semânticos. O parágrafo acabou de dizer que consulta correta pode responder à pergunta errada | "a segurança da consulta não é delegada ao modelo: ela é validada antes de tocar o banco. A correção semântica é medida no benchmark (Seção 5.6)." | +~45 |
| 3.3 | 231 | *Dota 2* sem itálico (o resto usa itálico para títulos de jogos) | `*Dota 2*` | +2 |

Nota para 3.2: é o único achado do bloco que muda o que o texto afirma; vale
levar à defesa como "validação estrutural, não semântica" (o Resumo já diz
"validação estrutural"). Tamanho ~+45 caracteres: exige compensar em outro
ponto do corpo para manter 29 páginas.

## Bloco 4 — 3 Trabalhos relacionados (linhas 318-407)

Conferido: "onze estudos de domínio" confere (Hodge, Birant, Bahrololloomi,
Jadowski, Do, Maymin, Guan, García-Méndez, Jiang, Guo, Wallner); cada estudo
aparece uma vez com o seu papel; as correções da leitura integral estão
aplicadas.

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 4.1 | 328 | *Dota 2* sem itálico (mesmo caso do 3.3) | `*Dota 2*` | +2 |
| 4.2 | 385 | **Escopo da generalização.** "Os estudos cobrem frentes isoladas" e "nenhum é entregue como uma plataforma" valem para os estudos lidos, não para toda a literatura | "Os estudos revisados cobrem..." e "nenhum deles é entregue..." | +~20 |
| 4.3 | 322 | "As obras de método (...)" lista 6 obras, mas a Seção 2 também usa Hornik, Grinsztajn e Hanley; a lista não é completa. Baixa prioridade | "As principais obras de método" | +11 |

## Bloco 5 — 4 Metodologia (linhas 411-542)

Conferido: quatro testes de robustez (i-iv) batem com a lista; cinco
variáveis (ouro, experiência, abates, torres, dragões); Kaufman, Kohavi (5
dobras) e Pedregosa como corrigidos na leitura integral; "Seção 6.1" existe
(Limitações); fila 420 e 41.063 conferem com o banco.

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 5.1 | 465-466 | "O tratamento incluiu ... a reconciliação dos nomes de campeão": no código ela é feita **na consulta** (`CHAMPION_NORM_SQL`, `src/api/main.py`), não no ETL. "Tratamento" insinua que a base já está reconciliada | "e, na consulta, a reconciliação dos nomes de campeão" | +10 |
| 5.2 | 507-511 | A lista de seis páginas traz "Partidas" e não traz "Consulta"; o menu do `Layout.tsx` tem Início, Dashboard, Campeões, Competitivo, Consulta NL e Simulador, e Partidas é página de detalhe (`/partidas/:id`). A Consulta aparece no parágrafo seguinte, então não é erro, mas a banca pode contar sete telas | "seis páginas de visualização" na 4.7 (a Consulta é descrita à parte) e deixar a resposta pronta no guia | +~15 |
| 5.3 | 513-517 | "a resposta vem sempre do banco, nunca do conhecimento genérico" convive com a seção "Leitura de jogo" do NLQ (conhecimento geral, rotulado, AGENTS.md invariante 2). Conferir no bloco 6 se a 5.6 explica | pendente do bloco 6 | ? |

## Bloco 6 — 5 Resultados e análise (linhas 546-828)

Conferido: sequência de figuras 1 a 5 no corpo e 6 a 11 no Apêndice F;
Quadro 5 tem onze linhas e bate com "onze" da 4.6, da 5.4, da 6.1 e do
Apêndice D (**fecha o 7.3**); Quadro 6 soma 26 perguntas e 23 acertos;
acurácias de 70,0% a 82,4% batem com o Quadro 4; 53,1% (2026) versus 53,2%
(acervo) confere com o banco recarregado; série anual "52,5% a 55,0%" confere.

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 6.1 | 553-554 | Lista sem conjunção: "*league-v4*, *account-v1*, *match-v5* (partida e linha do tempo)" (resíduo da minha edição) | "*league-v4*, *account-v1* e *match-v5* (partida e linha do tempo)" | +2 |
| 6.2 | 563-569 | **Precisão.** "A base usada para treinar e comparar os modelos reúne 39.188 partidas ... e 99.259 jogos profissionais" sugere que os jogos profissionais entram no treino. Os modelos usam só o *solo queue* | "A base de modelagem reúne 39.188 partidas de *solo queue* ...; o banco guarda também 99.259 jogos profissionais" | ~+20 |
| 6.3 | 612-613 | "O padrão se estende ao elo alto em geral" extrapola; a 6.1 diz que não há base para estender a outros elos | "O padrão não se limita ao Brasil" | ~-25 |
| 6.4 | 622-623 | "Uma versão anterior deste texto afirmava..." é história de rascunho num trabalho final | "Com amostras menores parecia haver um pico no meio do jogo. A base ampliada não confirma essa forma." | ~0 |
| 6.5 | 696-697 | Ambíguo: "aos 25 chega a 0,002 do seu AUC (0,9072 contra 0,9090)" não diz quem é "seu" | "aos 25 o MLP chega a 0,002 do AUC do XGBoost (0,9072 contra 0,9090)" | +10 |
| 6.6 | 727-729 | **Contradição interna.** "O único caso de piora mensurável foi o tipo do dragão (0,8319 para 0,8295, −0,0024)", mas o Quadro 5 traz o experimento 11 com −0,0031 (cooperação), maior em módulo | "Nenhum melhorou o AUC de forma distinguível de ruído. As maiores quedas numéricas foram a cooperação do jogador (−0,0031, 2.987 partidas) e o tipo do dragão (0,8319 para 0,8295)." | ~+30 |
| 6.7 | 822 | "módulo de orientação que cita o dado real de cada recomendação": nem toda recomendação tem dado (a parte de conhecimento geral é rotulada) | "módulo de orientação que separa o dado real do conhecimento geral" | ~0 |
| 6.8 | 823 | "Jiang et al. e Guo et al. **fundamentam** a consulta": a 3.4 já foi suavizada para "motivam" na leitura integral; aqui ficou a versão forte | "motivam" | 0 |
| 6.9 | 513-517 (bloco 5) | **Overclaim confirmado.** `src/nlq/nl_to_sql.py:159-164` manda a explicação acrescentar "Leitura de jogo:" (conhecimento geral rotulado). A 4.7 diz que a resposta "vem sempre do banco, nunca do conhecimento genérico", e o texto nunca menciona essa seção, que é o invariante 2 do projeto | "o resultado vem sempre do banco; a explicação pode acrescentar, rotulada como \"Leitura de jogo\", uma nota de conhecimento geral" | ~+80 |

Nota: os achados 3.2, 6.6 e 6.9 mudam o que o texto afirma; os demais são
forma. Soma de tamanho dos achados que aumentam texto: ~+190 caracteres.
Isso passa a folga de ~1 linha do corpo; é preciso compensar cortando em
outro ponto (candidatos: parêntese da 5.3 sobre as bases, linhas 615-620,
repetido na 5.4 e no Apêndice C).

## Blocos 8 e 9 — Referências e Apêndices (linhas 946-1465)

**Lido:** Apêndices A, D, E (quadros), F, G e Anexo A. **Não relido aqui:**
Apêndices B e C (quadros longos, cobertos pelas checagens 19 e 20 do
verificador) e a lista de Referências (coberta pelo `confere_docx.py`, 31
entradas, e pela leitura integral das obras).

Conferido: Apêndice A bate com `db/schema.sql` (chaves primárias e índices
citados); no Apêndice G, 1.754 = 1.647 (KR) + 107 e 117 da base congelada
fecham com 41.063 − 39.309 e 39.426 − 39.309; "onze experimentos" e
"experimento 2" batem com o Quadro 5.

| # | Linha | Problema | Proposta | Tamanho |
|---|---|---|---|---|
| 9.1 | 1436-1437 | "o pico de meio de jogo que uma versão anterior do texto atribuía aos dados": história de rascunho (mesmo caso do 6.4) | "o pico de meio de jogo que amostras menores sugeriam" | ~0 |

Higiene da fonte (não afeta o `.docx`, que corta a seção): a seção "Pendências
finais antes da entrega" (linha 1466 em diante) é um log interno com números
velhos (30 páginas, 18 referências, 6 quadros). Convém não citá-la como fonte.

## Resumo do estado

- 28 achados em 9 blocos. Três mudam o que o texto afirma (3.2, 6.6, 6.9) e
  um é contradição interna (6.6). Os demais são forma, itálico, conjunção ou
  intensidade.
- **Aplicados todos os 28 em 2026-11-03** (aprovação do usuário). Rebuild: corpo em 29 páginas, `verifica_tcc.py` consistente (21 checagens), `confere_docx.py` conforme.
