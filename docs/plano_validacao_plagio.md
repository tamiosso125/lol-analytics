# Plano de validação de plágio do TCC II

Criado em 2026-11-11. Cada item diz o que validar, onde no TCC, como e quem
faz. A coluna **Situação** é atualizada à medida que o plano anda.

## Base: o que a Unisinos considera plágio

- **Cartilha sobre Plágio Acadêmico** (NITT/Unisinos,
  https://www.unisinos.br/images/pesquisa-e-inovacao/nitt/cartilha-plagio.pdf):
  cópia integral ou parcial; cópia "dissimulada ou disfarçada"; ausência de
  citação da fonte; **citação de obra que não foi pesquisada nem utilizada**;
  plágio de ideias; autoplágio; "fontes alternativas" não citadas (sites,
  blogs, palestras); "colcha de retalhos" (trocar algumas palavras ou a ordem).
  Citação traduzida pelo autor: "tradução nossa" entre parênteses e, **na
  graduação, o texto original em nota de rodapé**. Fotos, tabelas, gráficos e
  imagens de terceiros: indicar autor e fonte. Penalidade: falta grave,
  reprovação, registro no histórico. "Todos os trabalhos produzidos nesta
  universidade são objetos de rastreamento."
- **Resolução CONSUN 35/2025:** texto atribuído ao estudante não pode ser
  integralmente gerado por IA; uso de IA deve ser divulgado (ferramenta,
  versão, data, seções, *prompts*, finalidade); Declaração de Autoria na
  entrega.
- **Orientadores pedagógicos Unisinos (2025):** detectores de IA não são
  considerados eficientes e não devem determinar autoria.
- Ferramenta de similaridade da Unisinos: **não identificada** — perguntar à
  biblioteca.

## Tópicos, por prioridade

| # | Prioridade | Tópico | Onde no TCC | Como validar | Quem | Situação |
|---|---|---|---|---|---|---|
| 1 | Alta | Paráfrase próxima e plágio por tradução (fontes em inglês, texto em português; detectores comuns não pegam) | Seções 2, 3, 5.7 e onde há citação autor-data | Roteiro de frases que citam autores (`docs/roteiro_citacoes.md`) comparadas ao trecho da fonte; opcional: similaridade multilíngue local (exige baixar modelo) | Claude (roteiro) + autor (leitura) | **Feito (2026-11-11):** retrotradução das 50 frases com fonte disponível contra o texto das 24 obras: nenhuma é tradução literal; os 5 sinais são títulos/nomes de método (4) e um termo técnico do Breiman. Trechos idênticos de 8+ palavras contra TCC I, 10 TCCs II, relatórios do ChatGPT e obras lidas e não citadas: só texto institucional da capa (colegas), 2 expressões curtas (ChatGPT) e o reaproveitamento do TCC I (item 8) |
| 2 | Alta | Afirmação atribuída à fonte certa; nenhuma obra citada sem ter sido lida (cartilha, item d) | As 31 referências | Tabela afirmação → página/seção da fonte; exige os PDFs (vários pagos: ACM, IEEE, Springer) | Autor (acesso) + Claude (conferência) | **Feito (2026-11-11):** 43 das 52 frases estão como na conferência de 2-3/11 (`docs/conferencia_referencias.md`); as 9 alteradas depois foram conferidas no texto completo: 8 conferem, 1 corrigida (Zhong em Trabalhos Futuros: a citação cobria "modelo aberto local", que o artigo não trata). Texto completo de 24 das 31 obras; Brown pelo resumo; livros (Gil, Prodanov, Creswell) sem acesso |
| 3 | Alta | Autoria e uso de IA (CONSUN 35/2025) | Trabalho inteiro | `docs/registro_uso_ia.md` + conversa com o orientador + Declaração de Autoria | Autor | Permitido pelo orientador. **Declaração de Autoria e Ineditismo: feita pelo autor (2026-11-11).** Declaração de uso de IA: o autor decidiu não escrevê-la (2026-11-11); a CONSUN 35/2025 (B.I) pede a divulgação, e o levantamento factual fica em `docs/registro_uso_ia.md` caso seja pedido |
| 4 | Alta | Similaridade com textos em português na web | `.docx` inteiro | Verificador (ferramenta da Unisinos, se houver; CopySpider é gratuito). O índice mede semelhança, não plágio; referências e quadros o inflam. **Não usar serviço que guarde o texto** | Autor | **CopySpider 3.5.3.7 executado (2026-11-11):** 10 documentos comparados, Si de 0,25% a 2,76%; os trechos em vermelho são só entradas de referências e o aviso legal da Riot (Apêndice H); nenhum texto do corpo. Dois arquivos que o CopySpider não conseguiu abrir foram comparados à mão (sequências de 8 e 6 palavras contra `docs/tcc2_texto.md`): Unespar, Compêndio vol. 2 (359 p.), só 2 referências (Chen e Guestrin; Creswell) e fórmulas genéricas; Creative Heritage (ArtsIT 2021), só as 12 primeiras páginas, coincide apenas o título/DOI da própria referência de Jadowski e Cunningham. Limites: dissertação da UFC (riufc/83510) não localizada; trabalhos de outros alunos e a base da Unisinos não cobertos. Verificação de frases pela web descartada pelo autor. Ferramenta da Unisinos não identificada (nada no manual de 2026/1 nem em página pública): perguntar ao orientador ou à biblioteca. A cartilha diz que todos os trabalhos são rastreados |
| 5 | Média | Tradução sem "tradução nossa" e sem original em nota | Apêndice H (aviso da Riot) | Corrigir; varrer outras traduções literais | Claude | Corrigido (ver abaixo) |
| 6 | Média | Fontes alternativas não citadas (páginas da web, documentação, dados) | Quadro 27 (portal da Riot); Riot, Oracle's Elixir, Data Dragon, Community Dragon | Fonte de cada quadro/afirmação que vem de página da web | Claude | Quadro 27 corrigido |
| 7 | Média | Quadros e figuras com conteúdo de terceiros | Figuras 3, 6, 8-10 (arte da Riot); Quadros 25, 27 | Linha "Fonte" coerente com a origem | Claude | Figuras já atribuídas; Quadro 27 corrigido |
| 8 | Média | Autoplágio em relação ao TCC I | Introdução, metodologia | Confirmar com o orientador se o TCC I foi publicado; se sim, citá-lo | Autor | **Resolvido:** o TCC I não foi publicado (informado pelo autor em 2026-11-11). Os 4% a 4,8% repetidos são continuação do mesmo trabalho (objetivos, título, questão de pesquisa), não autoplágio |
| 9 | Baixa | Código do repositório público: trechos copiados, licenças, código gerado por IA | `src/`, `frontend/`, `docs/*.py` | Varredura de comentários e URLs; licenças das dependências | Claude | Feito: nenhum comentário indicando código copiado; licenças das dependências permissivas (MIT, BSD, Apache, ISC, PSF; psycopg2 LGPL com exceções); repositório sem arquivo LICENSE (todos os direitos reservados por padrão) |
| 10 | Baixa | Citação ↔ referência; "apud" de obra não lida | Referências | `verifica_tcc.py` (checagem 4) + busca por "apud" | Claude | Verificado (sem "apud") |
| 11 | Baixa | Ideias do orientador | — | Cartilha: não é obrigatório citar; reconhecer informalmente | — | Nada a fazer |

## Ferramentas e cuidados

- Detecção entre idiomas é limitada e não estima intenção (Ferrero e Schwab,
  https://arxiv.org/pdf/1705.08828); a leitura humana do roteiro é o que vale.
- Serviços que guardam o documento enviado podem fazer o próprio TCC aparecer
  como "cópia" numa verificação posterior da universidade.
- Termos de uso do Oracle's Elixir: não encontrados na página de downloads.

## Registro das correções

- 2026-11-11, item 5: aviso da Riot no Apêndice H passou a "(tradução nossa)"
  com o original em inglês em nota de rodapé numerada.
- 2026-11-11, itens 6 e 7: fonte do Quadro 27 passou a citar a página do
  portal de desenvolvedores da Riot de onde vêm os dados
  (https://developer.riotgames.com/docs/portal), conferida em 11 nov. 2026.
- 2026-11-11, item 1: `docs/gera_roteiro_citacoes.py` gera `docs/roteiro_citacoes.md`
  (frase, página, seção e obra citada, com colunas em branco para o trecho da
  fonte e para "redação própria?"). Contagem por obra conferida contra uma busca
  independente no `.docx`.
- 2026-11-11, item 10: nenhum "apud" nem "citado por" no texto.
- 2026-11-11, itens 1 e 2: fontes localizadas (`Downloads/TCC`, `Downloads/ref`,
  `docs/artigos`, PDFs baixados nas sessões anteriores); o "não estão no
  computador" do primeiro rascunho deste plano estava errado. Correção:
  Trabalhos Futuros, citação de Zhong, Yu e Klein (2020) movida para "avaliação
  sobre vários bancos de teste", que é o que o artigo propõe.
- 2026-11-11: três relatórios em `Downloads/TCC` foram gerados pelo ChatGPT
  ("criador: ChatGPT" nos metadados; 13 a 15 abr. 2026). Nenhum trecho deles
  passou para o TCC (só duas expressões curtas coincidem). Registrado também
  em `docs/registro_uso_ia.md`, para a declaração de uso de IA.
- 2026-11-11, itens 3 e 8 (informado pelo autor): o orientador permitiu o uso
  de IA; o TCC I não foi publicado.
- 2026-11-11, livros em português: o e-book do Prodanov e Freitas (2013) foi
  baixado do site oficial da Feevale (`docs/artigos/Prodanov_Freitas_2013.pdf`,
  277 p.). As duas frases que o citam conferem (pesquisa aplicada, seção
  3.4.1; pesquisa documental, p. 55 do PDF) e não são falsa paráfrase (no
  máximo 3 palavras seguidas iguais ao livro). Gil (2002): conferido em 2-3/11
  com os capítulos 4 e 5 (p. 42-44), frases inalteradas desde então; o TCC
  aplica a classificação, não reproduz definições. Creswell e Creswell (2023):
  corrigido em 3/11 para "predominantemente quantitativa", frase inalterada.
