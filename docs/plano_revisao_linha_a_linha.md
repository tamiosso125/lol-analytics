# Plano da revisão linha a linha do TCC (2026-11-05)

Entrega em **16/11**; texto congelado em **14/11**. Nada deste plano foi executado.

## Por que outra revisão

A leitura sequencial de 03/11 (`docs/revisao_final_achados.md`, 28 achados aplicados) foi feita
antes das mudanças de 04 e 05/11: Resumo, Abstract, 4.7, 5.6, Conclusão, 6.1, 6.2 e o Apêndice B
foram reescritos para a consulta em linguagem natural, e a 6.2 caiu para três trabalhos futuros.
Além disso, aquela leitura conferiu texto e números, mas **não** conferiu a formatação contra o
modelo linha a linha nem comparou a estrutura com a dos colegas.

## As três réguas

Cada achado cita a régua que o justifica. Achado sem régua é opinião e vai marcado como tal.

| Régua | Fonte | Uso |
|---|---|---|
| **R1 — Modelo e manual** | `TCC II - Modelo de artigo científico da UNISINOS - Exemplo Prof. Elvandi` (.doc e .pdf), `TCC II - ModeloArtigoCientifico` (.doc e .pdf) e `Manual para elaboração de trabalhos acadêmicos 2026 1.pdf`, em `Downloads/TCC II - EXEMPLOS E MATERIAIS/` | Formatação obrigatória: margens, fonte, entrelinha, recuo, títulos, legenda e fonte de quadro e figura, citação ABNT, referências, resumo e palavras-chave, paginação |
| **R2 — Colegas** | os 10 TCC II aprovados da mesma pasta (5 com distinção); `docs/analise_escrita.md` já mediu o estilo | Como a banca aceita na prática: tamanho e ordem das seções, como apresentam resultados e trabalhos relacionados, quantos quadros e apêndices |
| **R3 — Boas práticas** | lista abaixo, aplicada em todo bloco | Argumento e clareza |

**R3 em critérios verificáveis:**
1. Cada objetivo específico (1.4.2, a–g) tem resultado na Seção 5 e retorno na Conclusão.
2. Cada afirmação tem evidência: número de artefato (`verifica_tcc.py`), citação ou dado.
3. Citação diz o que o trabalho citado diz (`docs/conferencia_referencias.md`).
4. Quadro e figura são chamados no texto antes de aparecer e são comentados depois.
5. O corpo faz sentido sem os apêndices (alerta do orientador).
6. O mesmo conceito tem o mesmo nome do começo ao fim; sigla definida na primeira vez.
7. Estrangeirismo em itálico, de forma consistente.
8. Sem repetição entre seções (2 × 3, 5 × 6, Resumo × Conclusão).
9. Limitação dita onde o resultado aparece, não só na 6.1.
10. Português: concordância, regência, crase, vírgula, frase longa (> 40 palavras), voz e
    tempo verbal coerentes (o modelo usa impessoal; checar "eu" e "nós").

## Como cada bloco é revisado

1. **Texto:** leitura de `docs/tcc2_texto.md` linha a linha (R3 e português).
2. **Página renderizada:** as mesmas páginas no PDF gerado do `.docx` (R1), porque formatação
   só aparece renderizada (quebra de quadro, legenda, título sozinho no fim da página).
3. **Comparação:** a seção equivalente em 2 ou 3 colegas (R2), quando houver dúvida de forma.
4. **Achados** em `docs/revisao_linha_a_linha_achados.md`, uma tabela por bloco:
   `# | linha | régua | tipo | problema | proposta | efeito em linhas`.
   Tipos: formato, ABNT, português, argumento, consistência, número.
5. **Nada é editado durante a leitura.** Cada bloco espera a sua aprovação; aplico só o aprovado.
6. Depois de aplicar: `verifica_tcc.py` consistente, `build_tcc_docx.py` + `finalize-fields.ps1`,
   `confere_docx.py` conforme e **corpo em até 30 páginas** (hoje 29, com cerca de 4 linhas de
   folga). Toda proposta que cresce o texto mostra quanto cresce.

## Blocos

| # | Bloco | Linhas do `.md` | Foco extra |
|---|---|---|---|
| B0 | Preparação | — | Extrair do modelo e do manual um **checklist R1 com página de referência** (não de memória); gerar o PDF atual; montar a tabela R2 por seção (palavras por seção nos 10 colegas) |
| B1 | Elementos pré-textuais, Resumo, Abstract, palavras-chave | 1–82 | Capa e folha de rosto renderizadas; Resumo e Abstract dizem o mesmo; tamanho do resumo contra o modelo |
| B2 | 1 Introdução | 83–207 | Problema, objetivos e justificativa encadeados; objetivos a–g verificáveis |
| B3 | 2 Fundamentação teórica | 208–308 | Só o que a Seção 5 usa; sem repetir a Seção 3 |
| B4 | 3 Trabalhos relacionados | 309–401 | Citações fiéis; 3.6 posiciona o trabalho; **depende da pergunta 3 ao orientador** (como a busca foi feita) |
| B5 | 4 Metodologia | 402–526 | Classificação da pesquisa; reprodutibilidade; 4.7 e 4.8 coerentes com a 5.6 nova |
| B6 | 5.1 a 5.3 | 527–642 | Números contra artefatos; quadros comentados |
| B7 | 5.4 e 5.5 | 643–733 | Comparação de modelos; figuras chamadas e legíveis |
| B8 | 5.6 e 5.7 | 734–776 | Texto novo de 05/11 (gabarito de 203); 5.7 dialoga com a Seção 3 |
| B9 | 6 Conclusão, 6.1 e 6.2 | 777–865 | Cada objetivo respondido; **depende da pergunta 4** (limitações e trabalhos futuros dentro da Conclusão) |
| B10 | Referências | 866–1019 | Cada entrada no padrão ABNT do modelo; toda citada aparece e vice-versa |
| B11 | Apêndices A a K e Anexo A | 1020–1547 | Passada mais leve (não contam páginas): legenda, fonte, chamada no corpo; **depende da pergunta 2** (quantidade de apêndices) |
| B12 | Passada global | documento inteiro | Consistência de termos, siglas e itálico; numeração e chamadas de quadros e figuras; leitura do PDF inteiro de ponta a ponta |

A seção "Pendências finais antes da entrega" (linha 1548 em diante) é nota interna: o
`build_tcc_docx.py` a retira do documento. Fica fora da revisão.

## Cronograma

| Dia | Blocos |
|---|---|
| 06/11 | B0, B1, B2 |
| 07/11 | B3, B4 (sem a parte que depende do orientador) |
| 08/11 | B5, B6 |
| 09/11 | B7, B8 |
| 10/11 | B9, B10 (com as respostas do orientador, se já houver) |
| 11/11 | B11, B12 |
| 12/11 | Leitura do PDF final de ponta a ponta (só correções pequenas) |
| 13/11 | Site de estudo e `.pptx` antigo (combinado para o final); folga |
| 14/11 | Texto congelado |

Se as respostas do orientador chegarem depois de 10/11, B4, B9 e B11 recebem só o que ele pedir,
sem nova leitura completa.

## Riscos

- **Páginas:** cerca de 4 linhas de folga. Qualquer acréscimo pede um corte equivalente no
  mesmo bloco.
- **Dupla leitura:** se o orientador pedir mudança estrutural (fundir apêndices, tirar 6.1 e 6.2
  da Conclusão), parte de B9 e B11 é refeita. Por isso esses blocos ficam para o fim.
- **Números:** nenhuma edição de redação pode mudar número; `verifica_tcc.py` roda depois de
  cada bloco aplicado.
- **Formatação gerada:** parte da formatação (caixa alta e negrito de títulos, legendas,
  referências) é aplicada pelo `build_tcc_docx.py`, não pelo `.md`. Achado de formatação corrige
  o script de build, não o texto à mão.

## Decisões que dependem de você

1. Aprovar os blocos e o cronograma.
2. Se a revisão de português entra junto em cada bloco (proposta) ou numa passada própria.
3. A data da reunião com o orientador, para encaixar B4, B9 e B11.
