# Plano de análise — modelos e materiais do TCC II (UNISINOS)

> **Data-base: 2026-10-04.** 20 arquivos em
> `C:\Users\Home\Downloads\TCC II - EXEMPLOS E MATERIAIS\TCC II - EXEMPLOS E MATERIAIS\`.
>
> **Objetivo:** extrair a formatação **e** o padrão de estrutura dos
> documentos de referência, e reconciliar o `tcc2_final.docx` com eles. A
> formatação dos modelos é **obrigatória** — não é sugestão.

---

## Por que isso importa agora

O `tcc2_final.docx` está internamente consistente e herda a formatação do
TCC **I**. Mas:

1. O TCC I é um documento **diferente** (projeto de pesquisa, não TCC II).
2. Agora há **10 TCC II aprovados** —idelos a resposta empírica.
3. Apareceu uma regra nova que **não** está aplicada: recuo de parágrafo de
   **1,25 cm** (`Ajustes LATEX.txt`).

Sem esta análise, qualquer diferença é achismo meu. Com ela, é medição.

---

## Bloco 1 — Extração (mecânica, toda automatizável)

Nenhum PDF precisa de leitura manual. O venv já tem **`pypdf`** (verificado na
Fase 4 do `plano_contexto`).

### 1.1 Os 10 TCC II aprovados — a fonte mais valiosa

Cinco PDFs têm no nome **"(Aprov. Destição)"** e três **"Pos Banca"** — ou
seja, passaram por banca. É a **evidência empírica** do padrão exigido.

Para cada um, extrair:

| Extrair | Por que |
|---|---|
| **Estrutura de seções de 1º nível** | responde se "Trabalhos Relacionados" é seção própria — a pendência que mais custou |
| **Títulos exatos** das seções | o modelo 2026-09-28 diz `MATERIAL(IS) E MÉTODOS`; verificar nos aprovados |
| **Contagem de páginas do corpo** | a regra é 25–30; nosso corpo tem 21. Confirmar a métrica (o que conta?) |
| **Sumário / Listas** | existem? quais? |
| **Estilo dos títulos** | maiúscula? negrito? o Prof. Elvandi já corrigiu para "maiúscula **sem** negrito" |
| **Legenda de figura/quadro** | convenção real: legenda acima ou abaixo? |
| **Como as referências são formatadas** | comparar com o estilo `REFERÊNCIAS` do TCC I |
| **Fonte, tamanho, entrelinha, margens, recuo** | comparar com o que herdamos do TCC I e com o `\parindent 1,25cm` |

**Método:** `pypdf` extrai texto página a página; `docx`/inspeção de metadados
complementa. Varrer `doc.get_outline()` quando houver bookmarks.

### 1.2 Documento normativo

**`Manual para elaboração de trabalhos acadêmicos 2026 1.pdf`** (4,9 MB) — é o
manual **oficial do ano corrente**. Prevalece sobre qualquer inferência. Extrair:
regras de formatação, estrutura obrigatória, regras de citação/referências,
página de apresentação.

### 1.3 Os dois modelos em `.doc`

- `TCC II - Modelo de artigo científico da UNISINOS - Exemplo Prof. Elvandi.doc`
  (2.2 MB) — **o modelo do próprio orientador**. É o mais autoritativo dos
  modelos de formato.
- `TCC II - ModeloArtigoCientifico.doc` (4,2 MB)

Ambos são OLE2 Compound (Word binário), **não** `.docx` nem LaTeX — não são
XML. Precisam de conversão (LibreOffice headless) ou `antiword` para leitura.
**Provável bloqueio** — tratar como dependência opcional; se não converter, usar
só os aprovados em PDF, que são mais richos.

### 1.4 `Ajustes LATEX.txt` — **já lido, ação imediata**

```
linha 235   \setlength{\parindent}{1.25cm}
linha 397   %\textbf{\uppercase\expandafter{\@unidade}}\\
```

Duas regras:

1. **Recuo de parágrafo = 1,25 cm.** Não está no `tcc2_final.docx` — herdamos
   o padrão do TCC I. **Aplicar.**
2. `\textbf{\uppercase{...}}` comentado: título de seção em **negrito +
   maiúscula** é a intenção original da classe. Mas o Prof. Elvandi corrigiu
   para **sem negrito** no TCC I. **Conflito real** — prevalecer a correção do
   professor sobre o comentário da classe, e registrar.

### 1.5 Livros de metodologia (referência, não formatação)

- `Metodologia de pesquisa em adminstração - Lisiane Vasconcellos da Silva.pdf`
- `Métodos e procedimentos de pesquisa - Debora Azevedo.pdf`

Não são norma de formato. Útil para conferir se a Seção 3 (Material e Métodos)
está academicamente sólida — especialmente a classificação da pesquisa
(natureza, abordagem, estratégia), que é onde banca costuma apertar.

### 1.6 Documentos administrativos (não afetam o texto)

`Configuração Proxy UNISINOS.pdf`, `DocumentoAcompanhamentoOrientacao.doc`,
`DocumentoEscolhaOrientadorTCCII.doc`,
`Formulário Aluno - PROPOSTA DE TCC II Bacharelado.docx`.

São de procedimento, não de conteúdo. Verificar se o formulário de proposta
exige algo que não foi preenchido (é.a.proposta de TCC II, não o TCCfinal).

---

## Bloco 2 — Reconciliação

Cruzar o que foi extraído com `tcc2_final.docx` e `docs/build_tcc_docx.py` e
produzir uma **tabela de conformidade**: regra → fonte → estado (aplicado /
não aplicado / divergente) → ação.

Conformidade **obrigatória** já confirmada:

| Regra | Estado atual |
|---|---|
| Corpo 25–30 páginas | ✅ 21 |
| 5 Quadros, numeração automática + Lista de Quadros | ✅ |
| 6 Figuras, legenda acima, fonte abaixo | ✅ |
| Títulos de seção **sem negrito** | ✅ (correção do Elvandi) |
| **Recuo de parágrafo 1,25 cm** | ❌ **não aplicado** |
| Referências com 1 linha em branco | ✅ |
| A4, margens 3/2/3/2, Arial 12, entrelinha 1,5 | ✅ herdado do TCC I |

A **única divergência concreta já identificada** é o recuo. O resto depende
do Bloco 1.

---

## Bloco 3 — Decisões de escopo

Três decisões que os documentos podem resolver sozinhos (e que hoje são
pendências ou suposições):

1. **Trabalhos Relacionados é seção de 1º nível?** Se 8 de 10 aprovados
   tiverem, a decisão que tomei ("seguir o modelo") precisa ser revista.
2. **`MATERIAL(IS) E MÉTODOS` vs `METODOLOGIA`.** O modelo de 2026-09-28 diz
   `MATERIAL(IS)`; o TCC I dizia `METODOLOGIA`.
3. **Título deve citar "Bellestraiko"?** Os aprovados mostram o padrão de
   título do TCC II.

---

## Bloco 4 — Aplicação no pipeline

`docs/build_tcc_docx.py` é o ponto único de mudança. Alterações de estilo
entram lá, não no `.docx` à mão (a regra do projeto: editar markdown → regerar).

- `\parindent` 1,25 cm → `paragraph_format.first_line_indent = Cm(1.25)`
  no `Normal`.
- Estrutura/seções → se Bloco 3 mudar algo, é revisão do `tcc2_texto.md`, e
  o pipeline regera numeração, sumário e listas sozinho.

---

## Dependências

| Necessário | Para quê | Status |
|---|---|---|
| `pypdf` | extrair texto dos 12 PDFs | ✅ no venv |
| `python-docx` | ler os `.docx` | ✅ no venv |
| LibreOffice headless | converter os 2 `.doc` binários | ❌ **não instalado** — opcional |
| `antiword` | alternativa p/ `.doc` | ❌ não instalado |

Os PDFs cobrem o essential. A conversão dos `.doc` é **nice-to-have**.

---

## Ordem sugerida

```
1. Extrair os 10 aprovados (pypdf)           <- maior valor, sem dependência
2. Extrair o Manual 2026 (pypdf)             <- norma oficial
3. Tabela de conformidade  regra × estado
4. Aplicar recuo 1,25 cm no build_tcc_docx.py
5. Decidir os 3 itens do Bloco 3 com dado real
6. Regerar .docx + revisão visual
```

**Não depende de conversor de `.doc`.** Se quiser o modelo do Elvandi lido,
instalar LibreOffice é o caminho — mas é **2 GB** e os aprovados em PDF já
dão a mesma evidência.

---

## Armadilhas

- **Os `.doc` não são XML.** Tentar ler com `python-docx` falha. Não insistir.
- **`pypdf` extrai texto, não layout.** Para verificar "recuo 1,25 cm" o texto
  não basta — precisa-se converter para DOCX e medir, ou gerar o `.docx` e
  conferir no Word.
- **PDF de TCC com figures grandes** pode ter paginação que distorce a
  contagem. Preferir contagem pelo sumário interno quando houver.
- **`Ajustes LATEX.txt` é sobre LaTeX**, e estamos gerando `.docx`. A regra do
  `\parindent` é transferível; o resto da classe LaTeX não se aplica.