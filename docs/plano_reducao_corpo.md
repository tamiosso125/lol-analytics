# Plano de redução do corpo — quadros e figuras no texto, prosa resumida

> **Substitui o plano de contingência anterior (2026-10-05/20).** Aquele
> plano partia de uma medição errada: o `finalize-fields.ps1` contava da
> Introdução até a página em que REFERÊNCIAS *começa* e reportava "30/30".
> A régua certa, confirmada nos 10 TCC II aprovados em 2026-10-23, vai da
> página do título/Resumo (número 1) até a **última** página das
> Referências. Por ela o documento tinha **37 páginas**; as correções de
> formatação de 2026-10-23 (Referências em espaçamento simples, entre
> outras) baixaram para **35**. O limite é **30**.

## Ponto de partida (medido em 2026-10-23)

| Bloco | Páginas | Observação |
|---|---|---|
| Título + Resumo + Abstract | 2,0 | p. 1–2 numeradas; não encolhe sem mexer no Resumo |
| Corpo (Seções 1–6) | ~29,6 | 10.636 palavras + Quadros 1 e 2 → **~368 palavras/página** |
| Referências | ~3,3 | 32 entradas; não encolhe |
| **Total contado** | **35** | limite 30 |

Palavras por seção hoje: Introdução 1.293 · Fundamentação 1.493 ·
Trabalhos Relacionados 1.225 · Metodologia 1.469 · **Resultados 4.222** ·
Conclusão 934.

## A decisão que muda o plano: quadros e figuras voltam para o texto

O orientador comentou que, com tudo nos apêndices, o texto perde o
sentido: o leitor lê "ver Quadro 3" e precisa ir até o fim do documento.
Então os elementos visuais que o texto discute **entram no corpo**, em
versão compacta, e os apêndices ficam com a versão completa (quando ela
existir). Isso **custa** páginas, e o custo sai da prosa.

| Elemento | Hoje | Vai para | Formato no texto | Custo estimado |
|---|---|---|---|---|
| Quadro 1 (viés por região) | 5.3 | fica | igual | já contado |
| Quadro 2 (modelos, 15 min) | 5.4 | fica | igual | já contado |
| Esquema do banco | Apêndice A | 5.2 | quadro compacto: tabela → o que guarda | ~0,5 p. |
| Métricas por corte | Apêndice C | 5.4 | só AUC e acurácia do XGBoost nos 4 cortes (ou fundido ao Quadro 2) | ~0,35 p. |
| Experimentos negativos | Apêndice D | 5.4 | 11 linhas: experimento → ΔAUC | ~0,5 p. |
| Benchmark NLQ | Apêndice B | 5.6 | resumo por tipo de pergunta (acertos/total) | ~0,3 p. |
| Capturas de tela | Anexo A | 5.3, 5.5, 5.6 | **recortes** da parte que o texto discute, ~8 cm de altura | ~0,45 p. cada |

Figuras candidatas (5, recortadas): viés por região no Dashboard (o
recorte já existe), mapa de calor da Partida (recorte já existe),
Competitivo solo queue × profissional, Simulador (estado + SHAP) e a
consulta em linguagem natural. Início e Campeões ficam fora do corpo.

Efeito colateral bom: as capturas são material **do próprio autor**, e o
modelo oficial reserva "Anexo" para material de terceiros. O que sobrar do
Anexo A vira **Apêndice F**; o Anexo B (documentação da Riot) continua
anexo.

## Orçamento

- Meta: **29 páginas**, não 30. Uma página de folga porque a paginação do
  Word muda de máquina para máquina (fonte, impressora padrão).
- Corpo disponível: 29 − 2,0 (Resumo/Abstract) − 3,3 (Referências) =
  **~23,7 páginas**.
- Visuais no corpo: ~2,3 (quadros) + ~2,25 (5 figuras) = **~4,5 páginas**.
- Sobra para prosa: ~19,2 páginas × 368 ≈ **~7.000 palavras**.
- **Hoje são 10.636. Corte necessário: ~3.600 palavras (≈ 34%).**

## Alvo por seção

| Seção | Hoje | Alvo | Onde está a gordura |
|---|---|---|---|
| 1 Introdução | 1.293 | 850 | 1.2 Delimitação e 1.5 Justificativa repetem a abertura; o modelo pede 6–7 parágrafos na introdução |
| 2 Fundamentação | 1.493 | 1.000 | 2.2 e 2.3 (~380 cada); o modelo pede "1 ou 2 parágrafos por subseção" |
| 3 Trabalhos Relacionados | 1.225 | 850 | 3.6 Síntese (407) pode cair à metade; manter os ≥ 5 trabalhos que o modelo exige |
| 4 Metodologia | 1.469 | 950 | 4.7 (317) antecipa o que a 5.5/5.6 mostra; 4.3 Coleta detalha o que a 5.2 repete |
| 5 Resultados | 4.222 | 2.450 | 5.3 (1.510 → 900): o histórico das medições já está no Apêndice E; 5.7 (517 → 300); **5.8 (950) sai do corpo e se funde com a 6.1** |
| 6 Conclusão | 934 | 850 | recebe as limitações fundidas: a 6.1 passa a ser a única lista de limitações |
| **Total** | **10.636** | **~6.950** | |

A 5.8 e a 6.1 hoje dizem duas vezes o que o trabalho não sustenta (viés
subestimado na taxa-base, modelo sem a última rodada, desequilíbrio por
região, ausência de dados de onda). Fundir as duas é o maior ganho sem
perda: ~700 palavras.

## Etapa 1 executada (2026-10-28): visuais no texto, custo medido

Entraram no corpo 6 quadros e 5 figuras recortadas:

| Seção | Quadros | Figuras |
|---|---|---|
| 5.2 | Q1 tabelas do banco (compacto; completo no Apêndice A) | — |
| 5.3 | Q2 viés por região | F1 Competitivo (viés + conversão de vantagem) |
| 5.4 | Q3 modelos a 15 min · Q4 XGBoost por corte · Q5 experimentos negativos (subiu do Apêndice D) | F2 importância SHAP por fase |
| 5.5 | — | F3 análise de partida · F4 Simulador, aba Estado |
| 5.6 | Q6 benchmark por tipo de pergunta | F5 consulta NL |

As telas inteiras viraram **Apêndice F** (autoria própria); o anexo que
sobrou, a documentação da Riot, virou **Anexo A**.

**Medido:** 35 → **39 páginas** (Resumo até o fim das Referências). Os
visuais custaram 4 páginas, perto da estimativa de 4,5. A Figura 3 deixa
meia página em branco porque a Figura 4 não cabe embaixo dela; isso se
resolve sozinho quando o texto em volta encolher, e é a última coisa a
ajustar (a paginação muda a cada corte).

**Alvo de palavras recalculado:** 39 → 29 páginas = **10 páginas de prosa**,
a ~368 palavras/página ≈ **3.700 palavras**. O corpo tinha 10.636; com os
parágrafos novos que citam quadros e figuras, o corte é de ~35%.

## Etapa 2 executada (2026-10-28): Seção 5 e limitações

- **5.8 Limitações saiu do corpo.** A 6.1 virou a lista única, em quatro
  blocos (construto, externa, interna, modelo); o detalhe com números e
  experimentos foi para o novo **Apêndice G**, sem perda.
- **5.3** condensada: a série anual do profissional e o detalhe do teste
  (ii) por faixa foram para o **Apêndice E**; ficaram a frase-síntese e os
  números que sustentam o achado.
- **5.4, 5.5, 5.6** sem repetição do que os quadros e figuras já mostram.
- **5.7** em dois parágrafos, com as onze referências ainda citadas.

**Medido:** Seção 5 de 4.295 para 2.077 palavras; Seção 6 de 934 para
1.044 (recebeu as limitações). Documento de **39 para 34 páginas**.
Faltam 4 a 5 páginas (≈ 1.500-1.800 palavras) das Seções 1 a 4, que é o
que os alvos da tabela acima já previam (5.440 → ~3.650).

## Etapa 3 executada (2026-10-28): Seção 4

1.429 → 1.099 palavras, todas as citações mantidas. Saíram a descrição das
tabelas (agora é o Quadro 1) e o detalhe das telas na 4.7 (a Seção 5 as
mostra). Documento: **34 → 33 páginas**. Faltam ~3 páginas (≈ 1.100-1.300
palavras) das Seções 1 a 3, que somam 4.011.

## Ordem de execução (uma etapa por vez, com sua aprovação)

1. **Inserir os visuais no texto primeiro.** É mecânico e mede o custo
   real, que hoje é estimativa. Depois disso o alvo de palavras é
   recalculado com o número medido.
2. **Seção 5**, a maior: fundir a 5.8 na 6.1, condensar a 5.3 e a 5.7.
3. **Seção 6**: reescrever a 6.1 como a lista única de limitações.
4. **Seção 4**, depois a **2**, depois a **3**, por último a **1**.
5. **Resumo e Abstract**: conferir se ainda descrevem o texto (ex.: a
   menção a "páginas de visualização").

Depois de **cada** etapa: `build_tcc_docx.py` → `finalize-fields.ps1`
(mede) → `verifica_tcc.py` → `confere_docx.py` → você lê a seção no
`.docx`.

## Regras para cada corte

- **Nenhum número sai sem destino.** Número medido que deixa o corpo vai
  para um apêndice ou fica no `diario_execucao.md`; o `verifica_tcc.py`
  cruza vários deles contra artefato, e checagem que quebrar é ajustada
  junto, nunca apagada.
- **Resumir, não reescrever.** Mantém as conclusões e as citações; sai a
  narrativa de processo ("primeiro tentamos X, depois Y"), a repetição e o
  detalhe de procedimento que já está em apêndice.
- **Cada referência continua citada no corpo**, senão ela sai da lista
  (regra ABNT, checada pelo `confere_docx.py`).
- Texto cortado de uma seção não volta em outra.
