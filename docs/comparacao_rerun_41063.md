# Comparação: base congelada (39.426) × base completa (41.063)

Gerada em 2026-11-06 pela rodada de reprodução. **Adotada em 2026-11-06**: o TCC passou a usar a base completa (41.063).
Antes = cópia em `data/backups/pre_rerun_41063/` (fora do git); depois = `reports/`.
Antes = `data/backups/pre_rerun_41063/reports/`; depois = `reports/` após a rodada.

### Quadros 3 e 4 e Apêndice C: três modelos por corte

| Corte | Modelo | Partidas | Acurácia (antes → depois) | AUC-ROC (antes → depois) |
|---|---|---|---|---|
| 10 min | XGBoost | 39.309 → 40.942 | 0,7004 → 0,7028 (+0,0024) | 0,7742 → 0,7752 (+0,0010) |
| 10 min | MLP | 39.309 → 40.942 | 0,7020 → 0,7017 (-0,0003) | 0,7735 → 0,7750 (+0,0015) |
| 10 min | RandomForest | 39.309 → 40.942 | 0,6704 → 0,6770 (+0,0066) | 0,7341 → 0,7390 (+0,0049) |
| 15 min | XGBoost | 39.188 → 40.816 | 0,7621 → 0,7636 (+0,0015) | 0,8473 → 0,8490 (+0,0017) |
| 15 min | MLP | 39.188 → 40.816 | 0,7610 → 0,7598 (-0,0012) | 0,8455 → 0,8454 (-0,0001) |
| 15 min | RandomForest | 39.188 → 40.816 | 0,7457 → 0,7475 (+0,0018) | 0,8277 → 0,8287 (+0,0010) |
| 20 min | XGBoost | 34.337 → 35.637 | 0,7917 → 0,7924 (+0,0007) | 0,8762 → 0,8772 (+0,0010) |
| 20 min | MLP | 34.337 → 35.637 | 0,7866 → 0,7903 (+0,0037) | 0,8729 → 0,8750 (+0,0021) |
| 20 min | RandomForest | 34.337 → 35.637 | 0,7785 → 0,7799 (+0,0014) | 0,8623 → 0,8642 (+0,0019) |
| 25 min | XGBoost | 26.837 → 27.761 | 0,8241 → 0,8261 (+0,0020) | 0,9090 → 0,9092 (+0,0002) |
| 25 min | MLP | 26.837 → 27.761 | 0,8240 → 0,8246 (+0,0006) | 0,9072 → 0,9080 (+0,0008) |
| 25 min | RandomForest | 26.837 → 27.761 | 0,8147 → 0,8146 (-0,0001) | 0,8975 → 0,8989 (+0,0014) |

**Quem tem a maior acurácia / maior AUC em cada corte**

- 10 min: acurácia MLP → XGBoost; AUC XGBoost → XGBoost
- 15 min: acurácia XGBoost → XGBoost; AUC XGBoost → XGBoost
- 20 min: acurácia XGBoost → XGBoost; AUC XGBoost → XGBoost
- 25 min: acurácia XGBoost → XGBoost; AUC XGBoost → XGBoost

### Regressão logística (baseline) e diferença do XGBoost em AUC-ROC

| Corte | Acurácia LR | AUC LR | XGBoost − LR em AUC [IC 95%] | IC antes | IC depois |
|---|---|---|---|---|---|
| 10 min | 0,7016 → 0,7018 | 0,7748 → 0,7758 | -0,0006 [-0,0011; -0,0002] → -0,0006 [-0,0011; -0,0002] | exclui 0 | exclui 0 |
| 15 min | 0,7631 → 0,7649 | 0,8483 → 0,8498 | -0,0010 [-0,0014; -0,0006] → -0,0008 [-0,0012; -0,0005] | exclui 0 | exclui 0 |
| 20 min | 0,7933 → 0,7938 | 0,8771 → 0,8778 | -0,0009 [-0,0012; -0,0006] → -0,0006 [-0,0010; -0,0003] | exclui 0 | exclui 0 |
| 25 min | 0,8248 → 0,8247 | 0,9091 → 0,9092 | -0,0002 [-0,0006; 0,0003] → -0,0000 [-0,0004; 0,0004] | inclui 0 | inclui 0 |

### Busca em grade (5.4, 6.1 e Apêndice F)

| Modelo | Item | Antes | Depois |
|---|---|---|---|
| XGBoost | auc_melhor | 0.8475 | 0.8491 |
| XGBoost | auc_producao | 0.8473 | 0.849 |
| XGBoost | posicao_producao_na_grade | 2 | 3 |
| XGBoost | acuracia_producao | 0.7621 | 0.7636 |
| RandomForest | acuracia_quadro3 | 0.7617 | 0.7625 |
| RandomForest | auc_quadro3 | 0.8468 | 0.8484 |
| MLP | acuracia_quadro3 | 0.7619 | 0.7645 |
| MLP | auc_quadro3 | 0.8477 | 0.8494 |
| XGBoost | melhor combinação | {'learning_rate': 0.05, 'max_depth': 3, 'n_estimators': 200} | {'learning_rate': 0.05, 'max_depth': 3, 'n_estimators': 200} |
| RandomForest | melhor combinação | {'max_depth': 6, 'min_samples_leaf': 5, 'n_estimators': 200} | {'max_depth': 6, 'min_samples_leaf': 2, 'n_estimators': 300} |
| MLP | melhor combinação | {'mlpclassifier__alpha': 0.001, 'mlpclassifier__hidden_layer_sizes': [32]} | {'mlpclassifier__alpha': 0.001, 'mlpclassifier__hidden_layer_sizes': [32]} |

### Diferença entre 5 e 10 dobras (Apêndice C; texto diz até 0,0008 em acurácia e 0,0006 em AUC)

| Corte | Modelo | |Δ acurácia| | |Δ AUC| |
|---|---|---|---|
| 10 min | XGBoost | 0,0006 → 0,0001 | 0,0001 → 0,0000 |
| 15 min | XGBoost | 0,0002 → 0,0003 | 0,0001 → 0,0000 |
| 15 min | RandomForest | 0,0002 → 0,0025 | 0,0004 → 0,0005 |
| 15 min | MLP | 0,0002 → 0,0025 | 0,0006 → 0,0009 |
| 20 min | XGBoost | 0,0004 → 0,0003 | 0,0001 → 0,0001 |
| 25 min | XGBoost | 0,0008 → 0,0010 | 0,0000 → 0,0002 |

### Treino no passado e teste no futuro, XGBoost (Apêndice C)

| Corte | Divisão | Teste | AUC-ROC |
|---|---|---|---|
| 10 min | cronologica | 7862 → 8189 | 0,7789 → 0,7795 |
| 10 min | por_patch | 15852 → 17303 | 0,7832 → 0,7844 |
| 10 min | aleatoria | 7862 → 8189 | 0,7723 → 0,7724 |
| 10 min | **pior diferença temporal − aleatória** |  | 0,0066 → 0,0071 |
| 15 min | cronologica | 7838 → 8164 | 0,8545 → 0,8573 |
| 15 min | por_patch | 15812 → 17258 | 0,8542 → 0,8569 |
| 15 min | aleatoria | 7838 → 8164 | 0,8432 → 0,8503 |
| 15 min | **pior diferença temporal − aleatória** |  | 0,0110 → 0,0066 |
| 20 min | cronologica | 6868 → 7128 | 0,8829 → 0,8839 |
| 20 min | por_patch | 13728 → 14883 | 0,8810 → 0,8824 |
| 20 min | aleatoria | 6868 → 7128 | 0,8814 → 0,8740 |
| 20 min | **pior diferença temporal − aleatória** |  | -0,0004 → 0,0084 |
| 25 min | cronologica | 5368 → 5553 | 0,9142 → 0,9136 |
| 25 min | por_patch | 10395 → 11215 | 0,9120 → 0,9124 |
| 25 min | aleatoria | 5368 → 5553 | 0,9111 → 0,9112 |
| 25 min | **pior diferença temporal − aleatória** |  | 0,0009 → 0,0012 |

### Vitória do azul no estado de empate (5.3, 6.1 e Apêndice F)

| Corte | Partidas empatadas | Azul nos dados | Azul no modelo |
|---|---|---|---|
| 10 min | 7349 → 7641 | 46,4% → 46,5% | 49,2% → 49,0% |
| 15 min | 3970 → 4126 | 47,9% → 47,8% | 49,6% → 50,4% |
| 20 min | 2423 → 2501 | 46,7% → 46,9% | 51,4% → 51,4% |
| 25 min | 1430 → 1478 | 47,1% → 47,4% | 49,0% → 49,8% |

### Importância SHAP por variável (Apêndice J)

| Corte | Variável | Antes | Depois |
|---|---|---|---|
| 10 min | gold_diff | 0,6643 | 0,6528 |
| 10 min | xp_diff | 0,2741 | 0,2759 |
| 10 min | kill_diff | 0,0209 | 0,0260 |
| 10 min | tower_diff | 0,0044 | 0,0038 |
| 10 min | dragon_diff | 0,1879 | 0,1878 |
| 15 min | gold_diff | 0,8989 | 0,9036 |
| 15 min | xp_diff | 0,4073 | 0,4178 |
| 15 min | kill_diff | 0,0680 | 0,0658 |
| 15 min | tower_diff | 0,0060 | 0,0082 |
| 15 min | dragon_diff | 0,2267 | 0,2260 |
| 20 min | gold_diff | 1,0693 | 1,0688 |
| 20 min | xp_diff | 0,4855 | 0,4898 |
| 20 min | kill_diff | 0,0166 | 0,0189 |
| 20 min | tower_diff | 0,0031 | 0,0015 |
| 20 min | dragon_diff | 0,2650 | 0,2683 |
| 25 min | gold_diff | 1,0642 | 1,0522 |
| 25 min | xp_diff | 0,8104 | 0,8190 |
| 25 min | kill_diff | 0,0028 | 0,0026 |
| 25 min | tower_diff | 0,0928 | 0,0927 |
| 25 min | dragon_diff | 0,2567 | 0,2590 |

### Experimentos de precisão, calibração e demais (resumo)

- **Experimentos 12 a 19 (Apêndice K):** maior ganho de AUC-ROC (regressão logística, 15 min) +0,0080 → +0,0078. Conclusão igual.
- **Experimentos 1 a 10:** maior ganho +0,0012 → +0,0012 (atributos ofensivos, regressão logística). Igual.
- **Placas de torre (exp. 10):** ganho de +0,0000 a +0,0001. Igual.
- **Calibração (Apêndice F):** desvio da taxa-base do XGBoost de produção aos 15 min **1,7 pp → 2,5 pp** (taxa-base 49,6% → 50,4%); a Random Forest de profundidade 6 passa de 0,6 pp para 0,5 pp. Variantes que pioram o desvio: eram 4, agora só a calibração isotônica. A conclusão (não é subajuste; só a Random Forest fecha) se mantém, mas os números do Apêndice F e da 6.1 mudam.
- **Faixa de duração:** sem alteração (já usava as 41.063).
- **Não rerodados:** experimento 11 (consulta à API, estado atual do jogador), NLQ e auditoria do coach.

Os arquivos novos estão em `data/backups/rerun_41063/` (fora do git); os antigos foram restaurados e `verifica_tcc` segue consistente.
