# Inventário de figuras e números na tela (Fase 1 do plano de entrega)

Feito em 2026-11-03, com a API em :8000 e o frontend (`vite preview`) em :5173,
sobre o banco restaurado às 41.063 partidas.

## 1.1 As 11 imagens do TCC

| Figura | Arquivo | Script | O que mostra | Depende de |
|---|---|---|---|---|
| 1 (corpo, 5.3) | `reports/figuras_texto/fig_competitivo.png` | `docs/capturar_figuras_texto.py` | Tela Competitivo: viés de lado e conversão de ouro, 2026 | `pro_games`, `matches` |
| 2 (corpo, 5.4) | `reports/figuras_texto/fig_shap_fases.png` | idem | SHAP por fase (Simulador) | modelo exportado |
| 3 (corpo, 5.5) | `reports/figuras_texto/fig_partida.png` | idem | Análise de partida NA1_5653867149 | `raw_timelines` |
| 4 (corpo, 5.5) | `reports/figuras_texto/fig_simulador_estado.png` | idem | Simulador, aba Estado, 71% | modelo exportado |
| 5 (corpo, 5.6) | `reports/figuras_texto/fig_nlq.png` | idem | Consulta NL, pergunta 9 do benchmark, tela com roteamento por base (recapturada em 2026-11-05) | API Anthropic |
| 6 a 11 (Apêndice F) | `reports/anexo_a/01_inicio.png` a `06_simulador.png` | `docs/recapturar_anexo_a.py` | Seis telas inteiras | banco, modelo |

## 1.2 Números da API contra o TCC

| Número | API | TCC | Confere |
|---|---|---|---|
| Partidas, fila 420 | 41.063 (`/stats/overview`) | 41.063 | sim |
| Vermelho por região | BR1 56,3 / EUW1 53,4 / KR 50,4 / NA1 52,2 / EUN1 50,0 | Quadro 2 | sim |
| Azul no agregado | 46,7% | 46,6% na base de 39.188 | sim, bases diferentes |
| Jogos profissionais 2026 | 6.274, azul 53,1% (`/stats/pro/overview`) | 53,1% | sim |
| Jogos por ano (`/stats/pro/years`) | 814, 1.806, 4.081, … 6.274 | Apêndice E | sim |
| Conversão, +2k a +4k, profissional | 81,5% (n = 3.294), pelo script `confere_conversao_advantagem.py` | 81,5% (n = 3.294) | sim |
| Conversão, +2k a +4k, solo | 73,7% (n = 5.165 na API, 5.166 no script) | 73,7% (n = 5.166) | sim; 1 partida de diferença entre as duas consultas |

## 1.3 O que mudou e o que foi feito

- **Telas diziam "Challenger/GM"** (Competitivo, Campeões, Dashboard) e a Início
  dizia "partidas de Challenger e Grandmaster do Brasil". O TCC diz elo alto
  (Desafiante a Mestre), cinco regiões. Troquei os textos nos quatro arquivos
  de `frontend/src/pages/`. Lint, 31 testes e build passam.
- **Recapturadas** as 5 figuras do corpo e as 6 telas do Apêndice F. Mudaram:
  Figura 1 (rótulo e contagem de 2026), e as telas 01, 02, 03 e 05 do Apêndice F.
  As Figuras 2 a 5 e as telas 04 e 06 saíram idênticas.
- Documento regenerado: 29 páginas, `verifica_tcc` e `confere_docx` verdes.
