import { useMutation } from "@tanstack/react-query";
import { Swords } from "lucide-react";

import { Button, Card, CardContent, CardHeader, CardTitle, ErrorNote } from "@/components/ui";
import { api, type CoachLane, type CoachSynergyItem } from "@/lib/api";

/** Leitura de draft — win condition, contra-pick, quem escala melhor —
 * usando só os 10 campeões escolhidos, ANTES de existir qualquer estado
 * de jogo. Camada 3 do plano "conhecimento geral aplicado à predição"
 * (ver docs/diario_execucao.md 2026-07-08), pedido explícito de feedback
 * de uso real: "fala sobre o draft em si, qual a win condition, quem
 * contra-pica quem". Quando `lanes`/synergies são fornecidos (Simulador,
 * que já chamou /compose), a leitura cita matchup/sinergia REAL; sem
 * eles (MatchDetail, partida real), é só conhecimento geral sobre os
 * campeões — ainda assim é a mesma pergunta ("quem tem vantagem
 * estratégica pelo draft"), só com menos dado pra apoiar. */
export function DraftAnalysisCard({
  blueChampions,
  redChampions,
  lanes,
  blueSynergies,
  redSynergies,
}: {
  blueChampions: Record<string, string>;
  redChampions: Record<string, string>;
  lanes?: CoachLane[];
  blueSynergies?: CoachSynergyItem[];
  redSynergies?: CoachSynergyItem[];
}) {
  const analysis = useMutation({
    mutationFn: () =>
      api.coachDraft(blueChampions, redChampions, lanes, blueSynergies, redSynergies),
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Swords size={14} className="text-gold" />
            Leitura de draft
          </CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            Win condition, contra-pick e quem escala melhor — conhecimento geral sobre
            estes 10 campeões{lanes?.length ? " + matchups reais do histórico" : ""}, antes
            de qualquer estado de jogo.
          </p>
        </div>
        <Button onClick={() => analysis.mutate()} disabled={analysis.isPending} className="shrink-0">
          {analysis.isPending ? "Gerando…" : analysis.data ? "Gerar de novo" : "Analisar draft"}
        </Button>
      </CardHeader>
      {(analysis.data || analysis.isError) && (
        <CardContent>
          {analysis.isError ? (
            <ErrorNote message={analysis.error.message} />
          ) : (
            <p className="rounded-lg border border-gold/20 bg-gold/5 px-4 py-3 text-sm leading-relaxed text-secondary-ink">
              {analysis.data!.narrative}
            </p>
          )}
        </CardContent>
      )}
    </Card>
  );
}
