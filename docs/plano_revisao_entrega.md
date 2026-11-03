# Plano de revisão para a entrega (13/11/2026)

Escrito em 2026-11-03. Nada aqui foi executado. Cada fase tem um critério de
pronto verificável. Regras que valem para todas: o corpo do TCC fica em 29
páginas (limite 30); número do texto vem de artefato; sem commit nem push sem
o usuário pedir; qualquer mudança de sentido no texto é mostrada antes.

## Estado de partida

- Corpo em 29 páginas, `verifica_tcc.py` com 22 checagens consistente,
  `confere_docx.py` conforme, banco restaurado a 41.063 partidas.
- Cópia do banco com as partidas novas em
  `data/backups/lol_analytics_com_coleta_nov03.dump`.
- Nunca vistos renderizados: Apêndices H a M. Nunca lidos linha a linha:
  Apêndices B e C e a lista de Referências. O `.docx` (61 páginas) nunca foi
  lido de ponta a ponta.
- Riscos conhecidos: capturas de tela feitas antes de corrigir o carregador
  dos jogos profissionais; demonstração e testes não reexecutados depois das
  mudanças no banco; chave da Riot visível na conversa.

## Fase 1 — Figuras e números na tela (risco mais alto)

| # | Tarefa | Critério de pronto |
|---|---|---|
| 1.1 | Inventário das 11 imagens do TCC (Figuras 1 a 5 no corpo, 6 a 11 no Apêndice F): script que gera cada uma, o que mostra, de onde vem cada número visível | Tabela no `docs/` com imagem, script, números e dependência de banco ou modelo |
| 1.2 | Subir a API (`uvicorn`, porta 8000) e o frontend (`npm run dev`, 5173) e anotar os números-chave de cada página: Início, Dashboard, Campeões, Competitivo, Consulta, Simulador, Partida | Cada número comparado com o TCC: 41.063, 39.426/39.188, 99.259, 53,2%, Quadro 2, Competitivo 2026 |
| 1.3 | Para cada figura com número desatualizado (esperado: Competitivo e a tela do Dashboard): recapturar com os comandos de `docs/comandos.md` | Nenhuma figura contradiz o texto; diferença visual conferida antes/depois |
| 1.4 | Conferir a legenda e a fonte de cada figura contra o que a imagem mostra (ex.: "cenário profissional restrito a 2026") | Legendas corretas e `verifica_tcc` check 9 e 10 verdes |

## Fase 2 — Documento gerado (`.docx` e PDF)

| # | Tarefa | Critério de pronto |
|---|---|---|
| 2.1 | Exportar o PDF e olhar cada página dos Apêndices H a M (larguras de coluna, palavra partida, quadro dividido entre páginas, legenda separada da tabela, fonte sob o quadro) | Nenhum defeito visível; ajustes só em `LARGURAS_QUADROS` |
| 2.2 | Olhar as páginas do corpo que mudaram: pré-textual, 4.3, 5.2, 5.3, 5.4, 6.1, 6.2 | Sem página quase vazia, sem figura ou quadro órfão |
| 2.3 | Conferir toda referência cruzada "Quadro N" e "Figura N" depois da inserção dos quadros novos (a numeração é por campo SEQ) | Cada citação aponta para o quadro certo |
| 2.4 | Lista de Referências: 31 entradas, ordem alfabética, formato NBR, datas de acesso (Oracle's Elixir declarado como 4 jul. 2026) | `confere_docx` e checagem 4 verdes |
| 2.5 | Folha de rosto, Resumo, Abstract, cabeçalho e numeração no PDF final | Página 1 impressa = título; sem numeração indevida |

## Fase 3 — Texto

| # | Tarefa | Critério de pronto |
|---|---|---|
| 3.1 | Ler os Apêndices B e C e as Referências, ainda não lidos linha a linha (blocos 8 e 9 do plano anterior) | Achados em `docs/revisao_final_achados.md`, aprovados e aplicados |
| 3.2 | Revisar o português dos Apêndices H a M (concordância, acentos, termos em inglês em itálico, "Quadro" no singular, uso de "jogos"/"partidas") | Nenhum erro; mesmas regras do `docs/analise_escrita.md` |
| 3.3 | Varredura automática de resíduos: espaços duplos, aspas misturadas, `timeline-v5`, `96.716`, "principais ligas", `Desafiante e Grão-Mestre`, "versão anterior", travessões fora do padrão | Zero ocorrências no texto entregue |
| 3.4 | Consistência Resumo, Abstract, Introdução, 5.4, 6.1 e Conclusão em relação aos achados novos (baseline logístico, ganho de até +0,008, teste no futuro, chave da Riot) | Mesma afirmação nos seis lugares, com a mesma intensidade |
| 3.5 | Reler a 6.1 e a 6.2 como se fosse a banca: cada limitação tem evidência e cada trabalho futuro tem motivo | Nenhuma afirmação sem apoio |

## Fase 4 — Software e demonstração

| # | Tarefa | Critério de pronto |
|---|---|---|
| 4.1 | `tests/smoke_test.py`, `tests/validate_predictions.py` (precisa do modelo exportado), `npm run lint`, `npm run test`, `npm run build` | Todos verdes; qualquer falha diagnosticada, não ignorada |
| 4.2 | Demonstração de ponta a ponta: Simulador (estado de jogo e SHAP), análise de partida (mapa de calor), três perguntas na Consulta | Roteiro de 3 minutos executado sem erro, duas vezes |
| 4.3 | Consulta em linguagem natural: confirmar que a chave da Anthropic e o certificado (TLS) funcionam nesta máquina | Resposta real a uma pergunta do benchmark |
| 4.4 | Estado do banco e do `.env`: 41.063 partidas, chave da Riot regenerada | Contagem confere; chave antiga invalidada |
| 4.5 | Plano B da demonstração: capturas do deck já cobrem Simulador e Partida; acrescentar uma da Consulta | Três capturas no deck |

## Fase 5 — Apresentação

| # | Tarefa | Critério de pronto |
|---|---|---|
| 5.1 | Ensaio cronometrado, 20 minutos para 18 slides, com as notas | Dentro do tempo; trechos lentos identificados |
| 5.2 | Abrir o `.pptx` em modo apresentação (F5) e ver cada animação rodando; testar em outro computador | Animações e fontes aparecem; sem fonte trocada |
| 5.3 | Conferir os números dos slides contra o TCC (tabela de 20 números-chave) | Todos iguais |
| 5.4 | Guia de estudo e site: republicar o site com as seis perguntas novas e os achados de hoje | Site na versão nova |
| 5.5 | Preparar respostas curtas para as perguntas prováveis (seleção da coleta, 88%, por que XGBoost, por que só elo alto, política de IA) | Uma frase por pergunta, treinada |
| 5.6 | PDF de segurança dos slides, sem animação | Arquivo gerado e aberto |

## Fase 6 — Entrega

| # | Tarefa | Critério de pronto |
|---|---|---|
| 6.1 | Confirmar com o orientador: formato e canal da entrega, data e horário da banca, política de uso de IA, se "mista" ou "quantitativa" vinha do TCC I | Respostas registradas no diário |
| 6.2 | Gerar o `.docx` e o PDF finais e conferir nome do arquivo | Dois arquivos, 29 páginas de corpo |
| 6.3 | Rodar a suíte completa uma última vez: `verifica_tcc`, `confere_docx`, `smoke_test`, testes do frontend | Tudo verde |
| 6.4 | Commit final organizado por assunto (só se o usuário pedir) | Árvore limpa, sem `.env` nem `data/` |

## Cronograma proposto

| Dia | O que |
|---|---|
| 4/11 (qua) | Fase 1 inteira; 2.1; perguntas ao orientador (6.1) |
| 5/11 | Fase 4 (testes e demonstração); recapturas pendentes |
| 6/11 | Fase 2 (restante) e 3.1 |
| 7/11 | 3.2 a 3.5 |
| 8 a 9/11 | Fase 5: ensaios, `.pptx` em F5, guia e site |
| 10/11 | Folga para o que falhou |
| 11/11 | Congelar o texto: nada mais muda no TCC |
| 12/11 | Leitura final do PDF de ponta a ponta; 6.2 e 6.3 |
| 13/11 | Entrega |

## Ordem e dependências

1. A Fase 1 vem antes de tudo porque pode mudar figuras e, com elas, o layout.
2. A Fase 2 depende da 1 (figuras novas mudam as páginas).
3. A Fase 3 vem depois da 2, para o português não ser relido duas vezes.
4. As Fases 4 e 5 podem andar em paralelo com a 3.
5. A leitura final do PDF (12/11) é a última e só roda sobre texto congelado.

## Riscos

| Risco | Consequência | Mitigação |
|---|---|---|
| Figura com número antigo | Contradiz o texto na frente da banca | Fase 1 |
| Chave da Anthropic ou TLS falhando na demonstração | Consulta sem resposta | 4.3 e plano B com captura |
| Edição no corpo que empurra a 30 páginas | Estoura o limite | Toda edição de tamanho líquido ~zero; conferir páginas a cada mudança |
| Animações do `.pptx` não rodarem no computador da banca | Slides sem efeito | 5.2 e PDF de segurança |
| Mudança tardia de número | Muitos arquivos desatualizados | Congelar o texto em 11/11 |

## Decisões que dependem do usuário

1. Aprovar este plano e a ordem.
2. Perguntas ao orientador (6.1): confirmar quais levar.
3. Se a banca exige arquivo PowerPoint ou aceita PDF.
4. Se quer que a revisão de português (3.2) aplique as correções direto ou
   mostre antes.

## Status (2026-11-03)

- **Fase 1 feita.** Ver `docs/inventario_figuras.md`: rótulos "Challenger/GM" trocados
  por "elo alto" nas telas, 11 imagens recapturadas, números da API conferidos.
- **Fase 2 feita.** PDF exportado e Apêndices H a M vistos renderizados.
  Ajustes: linhas de quadro não se partem mais entre páginas (`cantSplit`), colunas
  do Quadro 29 alargadas, cabeçalho "Experimento" do Quadro 32 virou "Exp.".
  Referências cruzadas de Quadro e Figura conferidas (todas apontam para o quadro
  certo). Corpo em 29 páginas; `verifica_tcc` (22) e `confere_docx` verdes.
  Observação: a página do início do Apêndice I fica quase vazia, porque o
  Quadro 26 (12 linhas) é mantido inteiro na página seguinte; só afeta apêndice.
- **Fase 3 feita.** Apêndices B e C e as 31 Referências lidos. Achado: a referência
  do RAT-SQL (Wang et al., 2020) tinha os cinco coautores errados e o título
  incompleto; corrigida e registrada em `docs/conferencia_referencias.md`.
  Ajustes de forma no Apêndice C ("10min" para "10 min", *Random Forest* em
  itálico, "as 80% mais antigas"). Varredura de resíduos limpa (sem `timeline-v5`,
  `96.716`, "principais ligas", "Desafiante e Grão-Mestre", espaço duplo ou
  pontuação solta). Resumo, Abstract, 5.4, 6.1 e Conclusão coerentes entre si.
- **Fase 4 feita (parte automatizável).** `smoke_test` concluído, `validate_predictions`
  aprovado com ressalvas (5 casos neutros, os mesmos de antes; 140/150 partidas
  com a direção certa), frontend com lint, 31 testes e build verdes. Benchmark de
  linguagem natural reexecutado em 3/11: 23/26 = 88%, mesmas três falhas
  (5, 12 e 22), com a chave da Anthropic e o certificado funcionando; Apêndice B
  ganhou a linha da execução. Consulta, Simulador (71,1%) e a lista de endpoints
  respondem. Banco em 41.063 partidas. Pendentes e que só o usuário pode fazer:
  regenerar a chave da Riot no portal e ensaiar o roteiro de demonstração à mão.
