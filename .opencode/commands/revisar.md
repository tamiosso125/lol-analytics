---
description: Revisa as mudanças pendentes do Bellestraiko com o subagente revisor
agent: revisor
---

Revise as mudanças pendentes deste repositório.

Diff atual (arquivos alterados e conteúdo):

!`git status --short && git diff && git diff --cached && git log --oneline -5`

Aplique o checklist completo: vazamento de dados nas features, segurança do
text-to-SQL, separação entre dado medido e conhecimento da LLM, idempotência
dos ETL/coletores, e corretude geral (Python e frontend).

Escopo adicional: $ARGUMENTS

Ordene os achados por severidade com `arquivo:linha` e não edite arquivos.