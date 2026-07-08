import { useMutation } from "@tanstack/react-query";
import { Compass } from "lucide-react";

import { Button, Card, CardContent, CardHeader, CardTitle, ErrorNote } from "@/components/ui";
import { api, type MatchState, type Prediction } from "@/lib/api";

/** Orientação estratégica gerada por LLM em cima do estado + predição já
 * calculados pelo /predict (não recalcula nada) — camada 1 do plano
 * "conhecimento geral aplicado à predição" (ver docs/diario_execucao.md
 * 2026-07-08). Compartilhado entre o card "E se..." (MatchDetail) e a
 * aba Estado do Simulador — os dois já têm state+prediction prontos. */
export function CoachCard({ state, prediction }: { state: MatchState; prediction: Prediction }) {
  const advice = useMutation({
    mutationFn: () => api.coach(state, prediction),
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Compass size={14} className="text-gold" />
            Orientação estratégica
          </CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            Conhecimento geral de League of Legends aplicado a este estado — não é
            verificado pelos dados desta partida.
          </p>
        </div>
        <Button onClick={() => advice.mutate()} disabled={advice.isPending} className="shrink-0">
          {advice.isPending ? "Gerando…" : advice.data ? "Gerar de novo" : "Gerar orientação"}
        </Button>
      </CardHeader>
      {(advice.data || advice.isError) && (
        <CardContent>
          {advice.isError ? (
            <ErrorNote message={advice.error.message} />
          ) : (
            <p className="rounded-lg border border-gold/20 bg-gold/5 px-4 py-3 text-sm leading-relaxed text-secondary-ink">
              {advice.data!.narrative}
            </p>
          )}
        </CardContent>
      )}
    </Card>
  );
}
