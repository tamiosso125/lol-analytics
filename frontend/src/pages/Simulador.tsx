import { useState } from "react";

import { PageHeader } from "@/components/ui";
import { cn } from "@/lib/utils";
import { CompositionPanel } from "@/pages/TeamBuilder";
import { ExplainPanel } from "@/pages/Explain";
import { StatePanel } from "@/pages/Predict";

const TABS = [
  { key: "composicao", label: "Composição", desc: "Monte um 5v5 e veja matchups e sinergias" },
  { key: "estado", label: "Estado", desc: "Ouro, XP e objetivos → probabilidade" },
  { key: "explicabilidade", label: "Explicabilidade", desc: "Por que o modelo pensa assim" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

/** Composição + estado + explicabilidade viviam em 3 páginas separadas
 * (Montar partida, Predição, Explicabilidade) que compartilhavam o
 * mesmo modelo/estado (`lib/matchState.ts`) e a mesma audiência —
 * unificadas aqui em abas para reduzir a navegação de topo (10 → 7
 * itens na sidebar, ver docs/diario_execucao.md 2026-07-06). */
export function Simulador() {
  const [tab, setTab] = useState<TabKey>("composicao");

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Modelo ML" title="Simulador">
        Composição de time, estado da partida ou os dois combinados — e, quando quiser
        entender o porquê, a explicabilidade do modelo por trás de cada número.
      </PageHeader>

      <div className="inline-flex rounded-lg border border-border p-0.5">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            title={t.desc}
            className={cn(
              "rounded-md px-4 py-2 text-left text-sm font-medium transition-colors",
              tab === t.key
                ? "bg-accent/10 text-accent"
                : "text-muted-ink hover:text-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "composicao" && <CompositionPanel />}
      {tab === "estado" && <StatePanel />}
      {tab === "explicabilidade" && <ExplainPanel />}
    </div>
  );
}
