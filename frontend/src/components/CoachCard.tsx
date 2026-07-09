import { useMutation } from "@tanstack/react-query";
import { Compass } from "lucide-react";

import { Button, Card, CardContent, CardHeader, CardTitle, ErrorNote } from "@/components/ui";
import { api, type CoachContext, type MatchState, type Prediction } from "@/lib/api";
import { championDisplayName, itemIcon } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

/** Orientação estratégica gerada por LLM em cima do estado + predição já
 * calculados pelo /predict (não recalcula nada) — camada 1 do plano
 * "conhecimento geral aplicado à predição" (ver docs/diario_execucao.md
 * 2026-07-08). Compartilhado entre o card "E se..." (MatchDetail) e a
 * aba Estado do Simulador — os dois já têm state+prediction prontos.
 *
 * Camada 2 (opcional, via `context`): quando quem chama já tem campeões
 * e/ou matchups/sinergias calculados (MatchDetail sabe os campeões da
 * partida real; o Simulador tem tudo isso do /compose), a orientação
 * cita campeão específico em vez de só "time azul"/"time vermelho". */
export function CoachCard({
  state,
  prediction,
  context,
}: {
  state: MatchState;
  prediction: Prediction;
  context?: CoachContext;
}) {
  const advice = useMutation({
    mutationFn: () => api.coach(state, prediction, context),
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
            Conhecimento geral de League of Legends aplicado a este estado
            {context?.lanes?.length ? " e à composição" : ""}
            {context?.matchId
              ? ", com itens, visão, momentum de abates e posição reais desta partida (posição aproximada)"
              : ""}
            . O estado de wave/minion não é observável.
          </p>
        </div>
        <Button onClick={() => advice.mutate()} disabled={advice.isPending} className="shrink-0">
          {advice.isPending ? "Gerando…" : advice.data ? "Gerar de novo" : "Gerar orientação"}
        </Button>
      </CardHeader>
      {(advice.data || advice.isError) && (
        <CardContent className="space-y-3">
          {advice.isError ? (
            <ErrorNote message={advice.error.message} />
          ) : (
            <>
              <p className="rounded-lg border border-gold/20 bg-gold/5 px-4 py-3 text-sm leading-relaxed text-secondary-ink">
                {advice.data!.narrative}
              </p>
              {advice.data!.build_suggestions.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-ink">Build sugerida</p>
                  {advice.data!.build_suggestions.map((s, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 rounded-lg border border-border px-3 py-2"
                    >
                      <span
                        className={cn(
                          "shrink-0 text-sm font-medium",
                          s.team === "blue" ? "text-chart-1" : "text-chart-red",
                        )}
                      >
                        {championDisplayName(s.champion)}
                      </span>
                      <div className="flex shrink-0 gap-1">
                        {s.items.map((itemId, j) => (
                          <img
                            key={j}
                            src={itemIcon(itemId)}
                            alt=""
                            className="size-7 rounded border border-border/50"
                          />
                        ))}
                      </div>
                      <p className="text-xs leading-relaxed text-muted-ink">{s.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </CardContent>
      )}
    </Card>
  );
}
