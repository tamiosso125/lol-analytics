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

## Bloco 2 — Opcional, usa o espaço que sobrou

O corpo tem **21 páginas** num limite de **25–30**. Sobram 4 a 9. Nada abaixo
é obrigatório; os dois existem porque há espaço e porque ambos têm retorno
real, não porque o documento esteja incompleto.

### 2.1 Ampliar a amostra da NA1 — 🟢 maior retorno sobre esforço

**Por que:** a Seção 5.2 do próprio TCC declara a NA1 como o elo mais frágil
do achado de viés de lado. Está em **1.446 partidas** — cerca de um décimo da
BR1 (11.936) — e **não avançou** nas duas últimas rodadas de coleta, enquanto
EUW1 e KR quase dobraram.

É a **única** pendência da lista que adiciona *evidência* em vez de fechar
burocracia. E o achado é o pilar mais forte do trabalho: as quatro regiões com
amostra relevante pendem para o vermelho, e a NA1 é a única cujo volume não
sustenta a generalização.

**Custo:** roda em background, sem blocking. Chave de dev da Riot expira em
24h — se expirar, pedir **Personal API Key** no portal (sem expiração diária).
O banco está de pé com 33.713 partidas.

**Efeito no documento:** se entrar coleta nova, **os números do TCC
envelhecem**. Escolher **antes** de coletar:

| Opção | Consequência |
|---|---|
| Congelar em 33.713 (data de hoje) | nada a fazer; só escrever que a coleta continuou depois |
| Atualizar para o número novo | Atualizar Seção 4.3 (tabela regional), 4.2 (volume), 5.2 (limitação), e a entrada de diário. ~30 min de trabalho de consistência |

**Recomendação:** coletar, e atualizar. A NA1 é o único ponto onde o TCC admite
fragilidade, e é barato resolver.

### 2.2 Retreinar o modelo em 33.713 partidas — 🟡 retorno duvidoso

**Estado:** o modelo de produção foi treinado em **23.133** partidas. Os
hiperparâmetros foram tunados em 10k e **reaplicados** ao volume maior — não
houve `GridSearchCV` completo no volume final.

**A favor:** o próprio TCC registra que volume é o **único** lever que
funcionou (AUC 0,8214 → 0,8393 num ciclo). E há 10 mil partidas novas.

**Contra:** o diário registra que tuning por fase deu hiperparâmetros
**idênticos** aos de produção em 3 de 4 cortes — o ganho tende a ser
marginal. E reescrever a Seção 4.4 inteira + Apêndice C invalidaria trabalho
já conferido.

**Custo:** ~10 min de `tune_models` + `export_model` + bateria, **ou** ~2 h se
exigir reescrever Seção 4.4, Apêndice C e `handoff.md` com os números novos.

**Recomendação:** só se o orientador pedir tuning completo. É a mudança com
maior raio de-diff e menor retorno esperado.

---

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
1. Confirmar o título do Quadro 4 (2 min) — único item que bloqueia
2. Disparar a coleta da NA1 em background (2.1), se quiser o achado mais forte
3. Quando a coleta terminar: atualizar 4.3/4.2/5.2 + entrada de diário
4. Regerar o .docx e fazer a revisão visual no Word
5. Testes + commit
```

**Nada no Bloco 1 exige escrever texto novo.** As duas decisões de escopo já
estão tomadas e aplicadas — a numeração do corpo já é a do modelo
institucional. O Bloco 2 é opcional por completo.

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