# Perguntas para a reunião com o orientador (quarta, 2026-11-04)

Entrega em 16/11 (antes 13/11). Em cada pergunta: por que perguntar e o que fazer conforme a
resposta. As de **prioridade A** mudam algo que ainda dá para ajustar; as de B
são confirmações; as de C só se sobrar tempo.

## 1. Entrega e banca (A)

1. **Qual é o formato e o canal da entrega no dia 13?** (arquivo Word, PDF, sistema
   da universidade, número de vias.) *Por quê:* o documento gerado é `.docx`; o PDF
   sai do mesmo arquivo.
2. **Data, horário e local da banca. Quem são os membros e a área de cada um?** *Por
   quê:* o tipo de arguição depende disso (dados, IA, engenharia de software).
3. **Quanto tempo tenho para apresentar e quanto para a arguição?** *Por quê:* o
   deck tem 18 slides para 20 minutos; se forem 15, corto.
4. **Posso fazer a demonstração ao vivo, com projetor e internet?** Ou prefere vídeo
   gravado? *Por quê:* a demonstração depende da API local e do banco; tenho plano
   B com capturas.
5. **Posso levar a apresentação em PowerPoint com animações, ou prefere PDF?** *Por
   quê:* o `.pptx` tem animações de entrada que podem não rodar em outro computador.
6. **Há prazo para enviar o texto aos membros antes da banca?** Quantos dias antes?

## 2. Uso de IA (A)

7. **Qual é a política da UNISINOS sobre uso e declaração de IA em TCC?** Não achei
   documento público. *Por quê:* a IA é parte do sistema (consulta em linguagem
   natural e orientação estratégica usam o Claude), o levantamento bibliográfico
   inicial teve ajuda do ChatGPT, e a escrita, a conferência e o desenvolvimento
   tiveram assistente de código.
8. **Onde e como devo declarar isso?** Nota na Metodologia, nos agradecimentos, em
   apêndice ou só na defesa? *Por quê:* hoje o texto declara a IA como componente do
   sistema, mas não como ferramenta de apoio à escrita e ao código.

## 3. Metodologia e estrutura do texto (A)

9. ~~**"Mista" ou "predominantemente quantitativa"?**~~ **Decidido (2026-11-04):
   manter "predominantemente quantitativa"** (4.1, Resumo e Abstract). No TCC I era
   "mista", e ele aprovou; mudei porque Creswell e Creswell (2023) exigem coleta
   qualitativa para chamar de mista, e aqui só há revisão bibliográfica. Removi Yin.
   Se ele perguntar na banca: Carolina e Eduardo (aprovados) dizem "quantitativa";
   Henrique e Michel dizem "quantitativa e qualitativa". A opção 3 do
   `conferencia_referencias.md` é a resposta pronta caso ele peça o rótulo antigo.
   Não precisa levar como pergunta.
10. ~~**O título continua o mesmo do TCC I, sem citar "Bellestraiko"?**~~
    **Decidido (2026-11-04): manter o título do TCC I.** O nome do produto
    aparece só no corpo (1.1). Não precisa levar.
11. ~~**"Trabalhos Relacionados" como seção 3 e "Metodologia" no lugar de "Material
    e Métodos" estão corretos?**~~ **Resolvida (2026-11-04):** o modelo do próprio
    orientador prevê 3 Trabalhos Relacionados (mínimo 5 trabalhos) e 4 Metodologia;
    os 10 aprovados também. Só o modelo genérico em branco usa "Material e
    Métodos". Não precisa levar.
12. ~~**Os apêndices contam fora das 30 páginas?**~~ **Resolvida (2026-11-04),
    pela numeração impressa dos 10 aprovados:** 7 de 10 terminam as Referências
    exatamente na página 30 (Michel vai a 32, com o corpo sem Referências em 29), e
    os apêndices começam na 31. O meu corpo, do Resumo ao fim das Referências, tem
    29. A quantidade de apêndices vai na pergunta 30.
13. ~~**Sumário, lista de figuras e lista de quadros ficam de fora?**~~
    **Resolvida (2026-11-04):** nenhum dos 10 aprovados tem sumário, lista de
    figuras, lista de quadros nem folha de aprovação; o Resumo é a página 1
    impressa. Não precisa levar.
14. **Palavras-chave com ponto e vírgula está certo?** (O modelo pede `;`; um
    comentário antigo seu no TCC I falava em ponto.) *Evidência para levar:* o
    modelo de artigo dele (p. 4) diz "iniciais em minúscula, exceto substantivos
    próprios, nomes científicos ou siglas, separadas por ponto e vírgula e
    finalizadas por ponto". Nos 10 TCC II aprovados: 5 usam `;`, 4 usam ponto e 1
    usa vírgula. Meu texto: `esports; *League of Legends*; análise de dados;
    *machine learning*; interface em linguagem natural.` (e igual em inglês).

## 4. Resultados e o que ainda dá para mudar (A)

15. ~~**Posso apresentar o modelo de produção atual (XGBoost) ou adoto o modelo com
    variáveis mais ricas?**~~ **Resolvida (2026-11-04): manter o XGBoost de 5 variáveis.**
    O modelo rico (regressão logística, 64 variáveis) dá +0,0080 de AUC-ROC e +0,69 pp de
    acurácia aos 15 minutos, estável no treino no passado, mas o Simulador, o modo "e se",
    a composição e o coach só recebem as 5 diferenças que o usuário digita; adotá-lo
    quebraria o Simulador, e usá-lo só na análise de partida deixaria dois modelos.
    Resposta pronta no guia ("Por que não adotaram o modelo novo?"). Não precisa levar.
16. ~~**A regressão logística empata com o XGBoost. Isso enfraquece a escolha do
    XGBoost?**~~ **Resolvida (2026-11-04): manter o XGBoost e dizer a verdade.** Ela não
    empata: fica à frente por milésimos (0,0010 de AUC-ROC aos 15 minutos; o intervalo
    exclui zero aos 10, 15 e 20 minutos), e com as 59 variáveis novas ganha mais que o
    XGBoost (+0,0080 contra +0,0044). A Seção 5.4 trocou "no mesmo patamar" e
    "estabilidade na faixa intermediária" por: logística à frente por milésimos, XGBoost
    mantido por ser a escolha anterior ao baseline e já sustentar a interface. Checagem 21
    confere os números contra `baseline_e_diferencas.json`. Resposta pronta no guia (48).
    Não precisa levar.
17. ~~**O achado do viés de lado precisa de mais robustez?**~~ **Resolvida
    (2026-11-04):** a Seção 5.3 já diz que só BR1, EUW1 e NA1 excluem 50% (a KR, com
    50,4% e [49,5%, 51,4%], não é distinguível de zero), traz quatro testes de
    robustez e chama a explicação (counter-pick do vermelho) de hipótese. Sem análise
    nova. Não precisa levar.
18. ~~**O viés de seleção da coleta basta como limitação, ou preciso de análise a
    mais?**~~ **Resolvida (2026-11-04): basta a limitação.** A Seção 6.1 já declara
    elo alto, janelas de coleta, jogadores repetidos e o *patch* 16.13 com 40,4%.
    A parte de tempo está medida (treinar no passado e testar no futuro não reduziu
    a AUC-ROC); a de só elo alto não dá para medir sem coletar outros elos, e já é
    trabalho futuro. Não precisa levar.
19. **O benchmark de linguagem natural (23 de 26 = 88%) usa SQL de referência
    escrita por mim e uma única base.** Basta como avaliação ou a banca espera algo
    mais independente? Zhong et al. (2020) propõem vários bancos de teste, o que não
    fiz. *Atualização (2026-11-04):* rodei 50 perguntas livres, escritas por outra
    pessoa, sem ajuste: 10 deram erro (6 por um falso positivo do validador com
    `EXTRACT(... FROM to_timestamp(...))`) e cerca de 12 vieram enganosas; o teto é
    ~28 de 50 (56%), contra 88%. **Decisão do autor: melhorar a precisão da
    consulta antes da entrega.** Levar como informação, não como dúvida.
20. ~~**O recorte "Desafiante a Mestre" está claro?**~~ **Resolvida (2026-11-04):**
    o nome descreve a base (93% dos jogadores cadastrados são Mestre). O primeiro
    texto dizia "Desafiante e Grão-Mestre"; já corrigido. Não precisa levar.

## 5. Trabalhos futuros e chave da Riot (B)

21. **Faz sentido citar o pedido de uma chave de produção da Riot como trabalho
    futuro?** A documentação diz que ela aumenta o limite de requisições e não
    traz dados novos nas APIs padrão; a Riot avalia se o produto ajuda jogadores de
    forma mensurável e diz não querer produtos que "solucionem o jogo". Um preditor
    com orientação estratégica pode ser questionado. *Por quê:* não quero prometer o
    que a banca vá considerar inviável.
22. **Quais dos cinco trabalhos futuros prefere que eu destaque na defesa?** (predição
    ao vivo, seleção de campeão competitiva, monotonicidade, outras filas e outro
    jogo, chave de produção).

## 6. Dados, ética e licença (B)

23. **A declaração "dados secundários e públicos, sem participação de sujeitos
    humanos" basta, ou a universidade pede parecer de ética por causa dos
    identificadores de jogadores (PUUID e Riot ID)?** *Por quê:* os identificadores
    estão no banco; o TCC e os prints não mostram nomes de jogadores do *solo queue*.
24. **Posso publicar o código no GitHub e incluir o link no TCC?** O repositório não
    inclui dados brutos (`.env`, `data/`, CSVs). *Por quê:* os termos da Riot e do
    Oracle's Elixir podem restringir a redistribuição dos dados.
25. **O uso da chave de desenvolvedor da Riot para pesquisa acadêmica é adequado?**
    A chave de desenvolvimento deveria ser só para protótipo, e o produto foi
    desenvolvido localmente, sem uso público.

## 7. Depois da banca (B)

26. **Há prazo e regra para a versão final depois da banca** (correções pedidas,
    depósito na biblioteca)? A pasta dos aprovados tem "Pos Banca".
27. **Há interesse em transformar parte do trabalho em artigo?** Os resultados mais
    publicáveis seriam a inversão do viés de lado e o teste de treino no passado.

## 8. Para fechar (C)

28. **O que costuma derrubar uma defesa nesta banca?** O que você mais gostaria que eu
    reforçasse nos próximos dias?
29. **Posso lhe enviar o documento e os slides em PDF até quinta ou sexta para uma
    revisão final sua?**

## 9. O que entra e o que sai do TCC (A e B)

Estrutura hoje: corpo de 29 páginas (Resumo a Referências), seções 1 a 6, 11
apêndices (A a K), anexo A, 30 quadros e 11 figuras. Abaixo, o que eu hesito em
manter, cortar ou mover, com minha inclinação atual.

30. **Quantos apêndices posso ter? Os Apêndices G a K (fundamentos dos métodos,
    procedência dos dados, objetivos e evidências, importância das variáveis,
    experimentos de precisão) valem a pena, ou 11 apêndices distraem?** (A) *Evidência para levar:* os 10
    aprovados têm no máximo 3 apêndices (6 deles têm algum), de 3 a 9 páginas no
    total, com material de apoio (links, termos, questionários). O meu tem 11
    apêndices e um anexo, 30 quadros e cerca de 27 páginas (estimativa: 59 do
    documento menos capa, folha de rosto e as 29 do corpo). *Inclinação:* manter K
    (é o achado novo) e J; avaliar fundir G na Seção 2 e I em uma tabela da
    Conclusão. *Por quê:* G repete conceitos da fundamentação e I repete a ligação
    objetivo-resultado que o texto já faz.
31. ~~**As Seções 2 e 3 têm subseções com os mesmos temas. Isso repete?**~~
    **Resolvida (2026-11-04):** nenhum dos 10 aprovados repete título idêntico entre
    as duas seções (8 de 10 usam títulos neutros ou sem subseções; Bruno e Eduardo
    organizam por tema, como eu). Troquei os cinco títulos da Seção 3 para descrever
    o conteúdo: 3.1 Predição de vitória em *Dota 2*; 3.2 Estudos de predição em
    *League of Legends*; 3.3 Predição com interpretação em *Counter-Strike*; 3.4
    Sistemas de consulta em linguagem natural sobre dados; 3.5 Visualização
    espaço-temporal de partidas. Corpo segue em 29 páginas. Não precisa levar.
32. ~~**O antigo Apêndice I (estudos de domínio e comparação com a literatura) repete
    a Seção 5.7?**~~ **Resolvida (2026-11-04): removido.** O segundo quadro repetia
    a 5.7 (mesmos números e mesma ressalva) e o primeiro repetia a Seção 3 e a
    coluna de relação da 5.7. Os apêndices J a M viraram I a L. Corpo segue em 29
    páginas; documento em 59. Não precisa levar.
33. ~~**Os experimentos negativos (antigo Apêndice D) e os de precisão 12 a 19 ficam
    separados ou juntos?**~~ **Resolvida (2026-11-04): juntos.** Para isso refiz os
    experimentos 1 a 10 na base congelada, com o mesmo protocolo e intervalo de
    confiança (`reports/experimentos_antigos.json`): nenhum passa de +0,0007 de
    AUC-ROC aos 15 minutos (só os atributos ofensivos têm intervalo que exclui zero);
    o 11 não pode ser refeito. O D foi apagado, o Quadro 5 do corpo ganhou os números
    novos e o Apêndice K traz os 19 experimentos. Corpo segue em 29 páginas. Não
    precisa levar.
34. ~~**Os experimentos 12 a 19 merecem um parágrafo no corpo (5.4), e não só no
    apêndice?**~~ **Resolvida (2026-11-04): sim.** A 5.4 só tratava dos 11 primeiros; o
    +0,0080 aparecia no Resumo e na 6.1 sem a origem. O parágrafo "Experimentos de
    enriquecimento" agora cita os dois ganhos máximos (+0,0007 nos experimentos 1 a 10,
    +0,0080 nos 12 a 19, com regressão logística e mantido no treino no passado) e
    funde a frase do volume de partidas, sem custo de página (692 contra 693
    caracteres). A checagem 21 confere os dois números contra os artefatos. Não
    precisa levar.
35. **O histórico do jogador (+0,0004) e a codificação de campeões e jogadores
    ficam só no apêndice?** (B) São negativos ou quase nulos, mas respondem a "por
    que não usou o histórico do jogador?".
36. ~~**O coach e a separação entre dado medido e conhecimento geral da LLM estão bem
    posicionados?**~~ **Resolvida em parte (2026-11-04).** O coach só aparecia na 4.7, 4.8 e 5.7
    (não no Resumo, nos objetivos, nos resultados nem na Conclusão, e não existia no TCC I),
    e a afirmação de que cada resposta separa dado e conhecimento geral não tinha evidência.
    Auditei 36 respostas (`src/coach/audit_grounding.py`): 0 estatísticas inventadas após
    revisão, ressalva final em 36 de 36, 87 de 87 itens da lista real; a 4.7 ganhou uma
    frase e o Apêndice B um quadro, com o limite declarado (número, não afirmação
    qualitativa). **Resta levar, em uma linha:** o orientador considera o coach parte do
    escopo, já que ele não estava no TCC I?
37. **A parte do competitivo (99.259 jogos, 122 ligas, viés azul de 53,2%) ocupa
    espaço demais num trabalho centrado no *solo queue*?** (B) Em contrapartida, o
    contraste entre os dois cenários é o achado mais citável.
38. **Os três casos que o benchmark de linguagem natural errou (5, 12 e 22)
    aparecem no corpo ou só no Apêndice B?** (B) Mostrar o erro dá credibilidade,
    mas ocupa espaço.
39. **As 11 figuras e as 6 telas do Apêndice E são demais, ou faltam figuras de
    arquitetura e de resultados (curva ROC, calibração)?** (B) Hoje o fluxo do
    sistema é descrito em texto, sem diagrama.
40. **Onde entram a declaração de uso de IA (pergunta 8) e o aviso de que o produto
    não é endossado pela Riot?** (A) Corpo, nota de rodapé ou apêndice?
41. **Trabalhos futuros: mantenho os cinco ou corto para três?** (B) Cinco itens em
    meia seção podem soar como lista de desejos. *Inclinação:* manter predição ao
    vivo, outra fila ou jogo e monotonicidade; a chave de produção só se ele achar
    que ajuda.
42. **O que ele sente falta no texto, ou o que ele via na primeira versão e não
    achou agora?** (A) Pergunta aberta, mas é a mais útil.
43. **Preciso dizer na Seção 3 onde e como busquei os trabalhos relacionados**
    (base de dados, palavras-chave, critério de escolha)? (A) *Evidência para
    levar:* Pablo, Bruno e Eduardo (aprovados) abrem a Seção 3 dizendo que a busca
    foi no Google Acadêmico e com quais palavras-chave; o modelo dele não exige. O
    meu texto atual não diz como os 11 estudos de domínio foram escolhidos, e não
    achei registro disso na documentação do projeto. *Custo:* uma ou duas frases;
    o corpo está em 29 de 30 páginas, então precisaria de corte equivalente.
44. **Vale manter limitações (6.1) e trabalhos futuros (6.2) dentro da Conclusão?**
    (A) *Evidência para levar:* minha Conclusão tem cerca de 1.050 palavras de
    prosa; as dos 10 aprovados têm de 131 a 507 (a maior é a de Pablo, com 507).
    Só 3 dos 10 usam a expressão "trabalhos futuros" no texto (Bruno, Eduardo e
    Letícia); os demais não a trazem explicitamente. *Alternativa:* uma Conclusão
    curta, com limitações e trabalhos futuros em seção própria ou em apêndice
    (o Apêndice F já traz as limitações em detalhe). Pergunta se ele considera
    limitações e trabalhos futuros parte esperada da Conclusão ou excesso.

45. **Posso reportar no Resumo e na Conclusão o conjunto cego (30 de 50, 60%) ao lado do benchmark de 26 (26 de 26)?**
    (A) *Evidência para levar:* o benchmark de 26 perguntas foi o número do TCC 1 e
    do rascunho (23 de 26, 88%), mas as regras do esquema que o levaram a 26 de 26
    foram escritas conhecendo as três falhas: não é independente. Montei um conjunto
    cego de 50 perguntas, rodadas uma vez com o sistema congelado e conferidas contra
    o banco: 24 certas, 6 recusas certas, 11 parciais, 8 erradas e 1 recusa indevida
    (intervalo de 95% de 46% a 72%). Versões anteriores do sistema no mesmo conjunto:
    22 e 24 de 50. *Risco:* o 60% aparece ao lado do 88% que ele já viu.
    *Recomendação:* citar os dois, com o cego explicado, e apresentar as falhas como
    limitação (6.1). *Pergunta:* ele prefere os dois números no Resumo, ou só o cego?
46. **Quem deve julgar as respostas do conjunto cego?** (A) Os 50 vereditos foram
    dados por um só avaliador (eu, com uma consulta independente por pergunta, a
    pedido do autor), sem segunda leitura humana. *Pergunta:* a banca aceita isso
    como limitação declarada, ou ele pede que o orientador ou um colega confira uma
    amostra antes da entrega?

## O que levar

- O `.docx` e o PDF (29 páginas de corpo, apêndices A a K, anexo A).
- Os slides (`docs/bellestraiko_defesa_v4.pptx`, 18 slides) e os prints do site
  (`reports/prints_site/`) para mostrar a demonstração.
- Uma folha com o que mudou desde a última versão: carregador dos jogos profissionais
  corrigido (99.259 jogos em vez de 96.716), apêndices G a K, experimentos de
  precisão 1 a 19, teste de treino no passado e teste no futuro, e a correção da
  referência do RAT-SQL.
- O guia de estudo da banca (`docs/guia_banca.md` ou o site) para ele ver as
  respostas preparadas.
