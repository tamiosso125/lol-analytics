# Plano de revisão final do TCC (2026-11-03)

Cada passo tem um critério verificável. Status ao fim da sessão.

| # | Passo | Critério | Status |
|---|---|---|---|
| 1 | Citações no texto x lista de referências | todo autor citado tem entrada; toda entrada é citada | feito: 31 referências, sem órfãs (coautores em "et al." conferidos à mão) |
| 2 | Números do texto x artefatos | `verifica_tcc.py` com 21 checagens consistente | feito |
| 3 | Fontes de dados x código/banco/documentação | conferência Riot API e Oracle's Elixir | feito: 5 correções aplicadas |
| 4 | Termos do domínio sem resíduo | grep de "timeline-v5", "96.716", "principais ligas", "Desafiante e Grão-Mestre" no texto e nos docs | feito: zero no TCC; docs de diário mantêm o histórico |
| 5 | Formato e páginas | corpo <= 30 páginas; `confere_docx.py` conforme | feito: 29 páginas |
| 6 | Docs sincronizados | README, handoff, comandos, scripts, diário, guia | feito |
| 7 | Site de estudo | números e termos iguais ao texto | feito (versão 14) |
| 8 | Leitura sequencial do texto | 9 blocos, achados em `docs/revisao_final_achados.md` | feito: 28 achados aplicados, 29 páginas (Apêndices B e C e Referências não relidos linha a linha) |
| 9 | Slides e demonstração | roteiro do site, teste de API + frontend | **aberto** |
| 10 | Perguntas ao orientador | lista de 29 no guia | **aberto** (reunião de quarta) |

## Passo 8 em detalhe: leitura sequencial do TCC

**Por quê.** Até 2026-11-03 o texto foi conferido por checagens (números,
citações, resíduos) e por edições pontuais. Nunca foi lido de ponta a ponta
depois das últimas mudanças. Checagem automática não pega argumento frouxo,
repetição, frase quebrada nem erro de português.

**Como (sessão nova, contexto limpo).** Ler `docs/tcc2_texto.md` em blocos,
um por vez, sem carregar o guia nem as conferências:

| Bloco | Linhas | Seção |
|---|---|---|
| 1 | 34-90 | Resumo e Abstract |
| 2 | 91-215 | 1 Introdução |
| 3 | 216-317 | 2 Fundamentação teórica |
| 4 | 318-410 | 3 Trabalhos relacionados |
| 5 | 411-545 | 4 Metodologia |
| 6 | 546-831 | 5 Resultados e análise |
| 7 | 832-945 | 6 Conclusão |
| 8 | 946-1100 | Referências |
| 9 | 1101-1465 | Apêndices e Anexo (leitura mais leve) |

**O que procurar em cada bloco.**
1. Erro de português, concordância, pontuação, termo em inglês sem itálico.
2. Frase que afirma mais do que o dado sustenta (intensidade).
3. Repetição entre seções (mesma ideia ou mesmo número dito duas vezes).
4. Número sem fonte ou que difere de outro trecho.
5. Promessa feita numa seção e não cumprida em outra (objetivos a-e da 1
   contra a conclusão).
6. Referência cruzada errada ("Seção X", "Quadro N", "Figura N").

**Regras.**
- Cada bloco gera uma lista de achados em
  `docs/revisao_final_achados.md` (linha, trecho, problema, proposta). Nada é
  editado durante a leitura.
- O usuário aprova a lista do bloco; depois as edições são aplicadas.
- Toda edição no corpo (blocos 1-7) tem tamanho líquido ~zero: o corpo está
  com 29 páginas e ~1 linha de folga. Depois de cada bloco aplicado, rodar
  build (com `TCC1_REFERENCE_DOCX`), `finalize-fields.ps1`, `verifica_tcc.py`
  e `confere_docx.py`, e conferir que continua em 29.
- Número só de artefato real (AGENTS.md). Nada de estimar.
- Sem commit sem pedido do usuário.

**Pronto quando:** os 9 blocos lidos, achados aprovados aplicados, 29 páginas,
as duas verificações limpas, passo 8 marcado como feito na tabela acima.
