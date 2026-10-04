# Plano de conclusão — TCC II (Bellestraiko)

> **Data-base: 2026-10-03.** Documento de trabalho gerado a partir da revisão
> de consistência (`docs/plano_contexto.md`, fases 0–5) e da geração do
> entregável em `.docx`.
>
> **Estado resumido:** de 6 pendências que o texto registrava, **5 estão
> fechadas** — as duas decisões de escopo (título e Trabalhos Relacionados)
> foram tomadas em 2026-10-03, e **nenhum item depende mais do orientador**.
> Resta 1 confirmação do autor e 2 itens opcionais que usam o espaço que
> sobrou no limite de páginas. **Não falta escrever texto.** O corpo tem 21
> páginas de um limite de 25–30.

---

## Bloco 0 — O que já está pronto (não refazer)

| Entrega | Onde | Estado |
|---|---|---|
| Texto corrido do TCC II | `docs/tcc2_texto.md` (1.215 linhas) | completo |
| Entregável formatado | `docs/tcc2_final.docx` (49 págs) | gerado por script |
| Pipeline de geração | `docs/build_tcc_docx.py` + `finalize-fields.ps1` | automatizado |
| 5 Quadros numerados | campo `SEQ` do Word | automático |
| 6 Figuras do Anexo A | legenda no topo, fonte embaixo | automático |
| Sumário + Listas | 3 campos TOC | preenchidos pelo Word |
| 12 Referências ABNT | estilo `REFERÊNCIAS` + linha em branco | conforme |
| Correlação de código ↔ doc | 31/31 testes front, bateria exit 0 | verificado |

**Ao mexer em `tcc2_texto.md`, regere o `.docx`.** O documento não é editado
à mão — é build. Editar no Word e não propagar ao markdown faz o texto e o
entregável divergirem, que é o que a regra do projeto proíbe.

```powershell
$env:TCC1_REFERENCE_DOCX = 'C:\Users\Home\Downloads\TCC\TCC_Final.docx'
.\.venv\Scripts\python.exe docs\build_tcc_docx.py
powershell -ExecutionPolicy Bypass -File docs\finalize-fields.ps1
```

---

## Bloco 1 — Pendências que bloqueiam a entrega

**As duas decisões de escopo foram tomadas em 2026-10-03.** Nenhum item
deste bloco depende mais do orientador. Resta só a confirmação do autor.

### 1.1 Título acadêmico — ✅ DECIDIDO: não citar Bellestraiko

O título do TCC II é **igual ao TCC I**: "Plataforma Inteligente para Análise
de Dados de Esports: uma proposta para League of Legends com uso de machine
learning e interface em linguagem natural". Por ser o mesmo trabalho, o título
acompanha o da versão anterior.

O nome do produto foi registrado no **corpo**, na Seção 1.1 (página 10):
*"A plataforma, batizada Bellestraiko, constitui a materialização do sistema
desenvolvido e implementado ao longo deste trabalho"*. Antes disso,
Bellestraiko **não aparecia** no texto entregue — só num bloco interno de
pendências.

**Nada a fazer.** Para reverter, seria editar `TITULO_PT`/`TITULO_EN` em
`docs/build_tcc_docx.py` e regerar.

---

### 1.2 Trabalhos Relacionados — ✅ DECIDIDO: não é seção de primeiro nível

Seguindo o **modelo institucional do TCC II** (2026-09-28), que não prevê
essa seção:

- **Seção 2 (Referencial Teórico)** — 2.1 a 2.5 descrevem o que cada
  trabalho relacionado afirma.
- **Seção 5.1 (Discussão)** — a confrontação de cada trabalho com os
  resultados deste, trabalho por trabalho (Hodge, Birant & Birant,
  García-Méndez, Jiang, Wallner).

O TCC I **tem** "3 TRABALHOS RELACIONADOS" como seção de primeiro nível,
aprovada naquele documento. Mas o modelo do TCC II difere, e prevaleceu o do
TCC II.

**Benefício colateral:** com esta decisão, a numeração do corpo fica
**exatamente igual à do modelo** (1 Introdução … 6 Conclusão), sem o deslocamento
que uma seção própria causaria.

A nota de trabalho que existia no fim da Seção 2 perguntando onde posicionar a
comparação foi substituída por uma frase de navegação para o leitor, que
justifica a escolha no próprio texto.

**Nada a fazer.**

---

### 1.3 Título do Quadro 4 — ⚠️ único item restante, precisa do autor

**Estado:** escrito, marcado como `CONFIRMAR com o autor` em
`docs/build_tcc_docx.py`, na lista `QUADROS`.

A tabela do Apêndice C (métricas completas, 4 cortes × 3 modelos) **não tinha
título** no markdown — só uma nota de método acima dela. Tabela sem legenda
viola a regra da instituição. O título foi escrito durante a conversão:

> **Quadro 4 — Métricas completas por corte temporal — comparação entre os três modelos**

**Decisão:** confirmar, trocar, ou deixar sem título e aceitar a não
conformidade. Custo: 2 min.

---

## Bloco 2 — Fechar o corpo (agora é obrigatório, não opcional)

O corpo tem **22 páginas** num limite de **25–30**: está **abaixo do mínimo**,
faltam pelo menos 3. Medido por `docs/finalize-fields.ps1`, que localiza a
Seção 1 e o fim das Referências e reporta a diferença — antes o número era
derivado à mão e não tinha artefato.

Isto **inverteu** a situação que o plano registrava: quando o corpo tinha 21
páginas e a faixa era 25–30, sobrar espaço era luxury. Agora é lacuna.

### 2.1 Ampliar a amostra da NA1 — ✅ feito

**Por que era o maior retorno:** a Seção 5.8 do próprio TCC declarava a NA1
como o elo mais frágil do achado de viés de lado, com 1.446 partidas —
cerca de um décimo da BR1 (11.936).

**Resolvido em 2026-10-04:** a NA1 foi de 1.446 para **7.159 partidas**, e a
taxa de vitória do vermelho foi de 51,9% para 52,2% — a direção não mudou. A
limitação saiu da Seção 5.8.

Os números de modelo também foram atualizados para a base nova (39.188
partidas no corte de 15 min), com AUC do XGBoost de 0,8393 para **0,8473**, e
o Apêndice C passou a ser reproduzível por
`python -m src.models.multi_cutoff_metrics`.

### 2.2 Retreinar o modelo — ✅ feito

**Era:** o modelo de produção estava treinado em **23.133** partidas, com
hiperparâmetros tunados em 10k e **reaplicados** ao volume maior — sem
`GridSearchCV` completo no volume final.

**Resolvido em 2026-10-04:** retreino sobre a base nova.

| Métrica (corte 15 min) | Antes (23 mil) | Agora (39.188) |
|---|---:|---:|
| Acurácia | 0,7573 | **0,7621** |
| AUC-ROC | 0,8393 | **0,8473** |

O `GridSearchCV` sobre as 39 mil linhas devolveu ajuste equivalente (200
árvores a taxa 0,05), o que confirma que a limitação registrada na Seção 5.8
**não é subajuste** — é limitação de taxa-base do estado em empate.

## Bloco 3 — Fechamento

Executar quando os Blocos 1 e 2 estiverem resolvidos.

1. **Regerar** o entregável e conferir a contagem de páginas
   (`finalize-fields.ps1` já reporta).
2. **Revisão visual no Word** — duas coisas que o script não controla:
   - a **capa** (as posições verticais das linhas em branco não são idênticas
     às do TCC I; o pandoc não controla espaçamento vertical de capa);
   - a **legibilidade das 6 capturas** em 15 cm de largura.
3. **Testes** antes de fechar:
   ```powershell
   .venv\Scripts\python.exe tests\smoke_test.py        # exit 0
   .venv\Scripts\python.exe tests\validate_predictions.py  # exit 0
   cd frontend; npm run lint; npm run test; npm run build; cd ..
   ```
4. **Atualizar** `docs/handoff.md` e a lista de pendências do
   `diario_execucao.md` com o estado final.
5. **Commit** com mensagem no formato Conventional Commits em PT-BR.

---

## Ordem sugerida

```
1. [feito]  Confirmar o título do Quadro 4
2. [feito]  Ampliar a NA1 e retreinar (2.1 e 2.2)
3. Regerar o .docx e fazer a revisão visual no Word
4. Testes + commit
```

**O Bloco 2 mudou de natureza.** Era opcional porque o corpo tinha folga; com
22 páginas num limite de 25–30, fechar o corpo virou obrigatório. O que
sobra é a questão de *conteúdo*: escrever mais 3 páginas que não sejam
enchimento.

**Nada no Bloco 1 exige escrever texto novo.** As duas decisões de escopo já
estão tomadas e aplicadas — a numeração do corpo já é a do modelo
institucional.

---

## Armadilhas conhecidas

- **Editar o `.docx` direto no Word** quebra a correspondência com o markdown.
  Sempre voltar por `tcc2_texto.md`.
- **Campos do Word nascem vazios.** Sem rodar `finalize-fields.ps1` o
  documento sai com sumário em branco e Quadros sem número.
- **A chave da Riot expira em 24h.** Erro 401/403 na coleta é isso, não é bug.
- **O `validate_predictions.py` roda ~26 s** e mostra `APROVADO COM
  RESSALVAS` com 1 `LIMITADO` e 3 `NEUTRO`. **Isso é o resultado esperado** —
  são as limitações que o TCC 5.2 declara, não regressão.
- **Resultado diferente no smoke test** (XGBoost abaixo de RandomForest) é
  normal: são 400 partidas sintéticas e diz nada sobre produção.