# Revisão do conjunto cego v2 (perguntas 101–150)

Perguntas novas escritas pelo autor do TCC (nenhuma repete v1 ou desenvolvimento, checado por
código), rodadas **uma vez** com o sistema congelado no commit 1fe0014 (hashes em
`reports/nlq_cego_v2_resultado.json`). Cada resposta foi recalculada no banco com SQL
independente; vereditos e motivos em `reports/nlq_cego_v2_vereditos.json`. Julgador único
(Claude), que viu as perguntas ao receber o arquivo, mas não ajustou o sistema depois.

| Veredito | n |
|---|---|
| Certa (C) | 18 |
| Recusa certa (RC) | 9 |
| Parcial (P) | 9 |
| Errada (E) | 13 |
| Recusa indevida (RE) | 1 |

**27 de 50 certas (54%)**, Wilson 95%: 40,4%–67,0%. A v1 teve 30/50 (60%); os intervalos se
sobrepõem, então não há diferença demonstrável entre as duas medidas.

## O que a v2 mostra
- **Falha dominante (9 erros): substituto não rotulado quando o dado não existe.** Para
  "primeira torre", "primeiro sangue", "primeiro Barão", "primeiro dragão", "série" e "dano a
  torres", o sistema calculou outra coisa (torres>0, kills, dragões=0, series_id inventado) e
  apresentou como resposta. Das ~19 perguntas que pedem dado ausente, 9 foram recusadas
  corretamente e 9–10 receberam número fabricado. É a violação do invariante 2 (honestidade).
- Erros de cálculo: contagem dobrada (143), divisão por si mesma (144), mínimo global em vez
  de por jogo (104), kills+assists no lugar de kills (119), timeout (120).
- As correções da v1 (amostra mínima, agregação por jogo, sequências) generalizaram: nenhuma
  das 18 certas depende de pergunta da v1.

## Limites
- v2 não é mais cega para novos ajustes: qualquer mudança feita a partir daqui vira
  desenvolvimento, e o número desta rodada fica congelado.
- A v2 tem mais perguntas sem dado no schema do que a v1, o que a torna mais difícil.
