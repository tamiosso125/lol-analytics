import io
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

P = r"docs\tcc2_texto.md"
L = io.open(P, encoding="utf-8").read().split("\n")

# ---- rewrap do paragrafo dos quatro testes --------------------------------
i = next(k for k, l in enumerate(L) if l.startswith("Os quatro testes de robustez"))
j = i
while L[j].strip():
    j += 1
paragrafo = " ".join(x.strip() for x in L[i:j])
L[i:j] = []
texto = io.open(P, encoding="utf-8").read()

REWRAP = """Os quatro testes de robustez definidos na Seção 4.5 se aplicam todos aqui,
com o desfecho de cada um. O teste (i), de replicação regional, restringe a
análise à BR1 isoladamente e reproduz a assimetria, descartando mistura
regional como explicação. O teste (ii), de faixa de duração, confirma que a
taxa de vitória incondicional do **azul** por faixa de duração total de
partida permaneceu estável (medido em 2026-10-04 sobre as 41.063 partidas:
45,6% a 47,3% entre as faixas de duração, amplitude de 1,7 ponto percentual,
todas abaixo de 50%), o que descarta a hipótese de que "partidas longas são um
tipo diferente de jogo". O teste (iii), o intervalo de Wilson, está aplicado
acima: mostra que nenhum dos quatro cortes admite 50%. E o teste (iv), a
comparação de pares com correção de Holm, é o que sustenta a afirmação de
constância e está detalhado no parágrafo anterior. É ele que substituiu o
teste que antes sustentava a alegação de enfraquecimento, deixando de ser
aplicável quando a forma deixou de existir."""

if paragrafo.replace("\n", " ") != REWRAP.replace("\n", " ").replace("  ", " "):
    # só substitui se for exatamente o mesmo parágrafo, reescrito com wrap
    igual = re.sub(r"\s+", " ", paragrafo) == re.sub(r"\s+", " ", REWRAP)
    if igual:
        L[i:i] = REWRAP.split("\n")
        io.open(P, "w", encoding="utf-8").write("\n".join(L))
        print("ok  paragrafo dos quatro testes reescrito com wrap correto")
    else:
        print("!!  o paragrafo nao e o que esperava — nada tocado")
else:
    print("ok  paragrafo ja esta com o wrap correto")

# ---- o detector de frase quebrada ----------------------------------------
t = io.open(P, encoding="utf-8").read()
# assinatura de complemento apagado: palavra minuscula seguida de maiuscula,
# sem pontuação entre elas e sem quebra de linha no meio
PADRAO = re.compile(r"[a-zà-õç,;]\s+[A-ZÀ-Ý][a-zà-õç]{2,}\s")
cands = [(t[:m.start()].count("\n") + 1, m.group(0).strip()) for m in PADRAO.finditer(t)]
print(f"\n=== detector 'minuscula seguida de maiuscula': {len(cands)} ocorrencias ===")
for ln, g in cands[:25]:
    print(f"  L{ln}: {g!r}")