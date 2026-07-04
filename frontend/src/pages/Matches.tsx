import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Card, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api, type RecentMatchParticipant } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

function TeamRow({ players, won }: { players: RecentMatchParticipant[]; won: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      {players.map((p) => (
        <img
          key={`${p.team_id}-${p.champion}`}
          src={championIcon(p.champion_id)}
          alt={championDisplayName(p.champion)}
          title={`${championDisplayName(p.champion)} (${POSITION_LABELS[p.position] ?? p.position}) — ${p.kills}/${p.deaths}/${p.assists}`}
          className={cn("size-8 rounded-md", !won && "opacity-55 grayscale-35")}
        />
      ))}
    </div>
  );
}

export function Matches() {
  const navigate = useNavigate();
  const matches = useQuery({
    queryKey: ["recent-matches"],
    queryFn: () => api.recentMatches(20),
  });

  return (
    <div className="space-y-5">
      <PageHeader eyebrow="Histórico" title="Partidas recentes">
        Últimas partidas coletadas. Clique numa partida para ver a análise completa, com a
        curva de probabilidade de vitória minuto a minuto.
      </PageHeader>

      {matches.isPending ? (
        <Skeleton className="h-96" />
      ) : matches.isError ? (
        <ErrorNote message={matches.error.message} />
      ) : (
        <div className="space-y-2">
          {matches.data.map((m) => {
            const blue = m.participants.filter((p) => p.team_id === 100);
            const red = m.participants.filter((p) => p.team_id === 200);
            return (
              <Card
                key={m.match_id}
                onClick={() => navigate(`/partidas/${m.match_id}`)}
                className={cn(
                  "flex cursor-pointer items-center gap-4 border-l-4 px-4 py-2.5 hover:bg-foreground/5",
                  m.blue_win ? "border-l-chart-1" : "border-l-chart-red",
                )}
              >
                <div className="w-28 shrink-0 text-xs text-muted-ink">
                  <p className="font-medium text-secondary-ink">
                    {new Date(m.date).toLocaleDateString("pt-BR")}{" "}
                    {new Date(m.date).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
                  </p>
                  <p className="tabular-nums">
                    {m.duration_min} min · patch {m.patch}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={cn(
                      "w-12 text-xs font-medium",
                      m.blue_win ? "text-chart-1" : "text-muted-ink",
                    )}
                  >
                    Azul
                  </span>
                  <TeamRow players={blue} won={m.blue_win} />
                </div>
                <span className="text-xs text-muted-ink">vs</span>
                <div className="flex items-center gap-3">
                  <TeamRow players={red} won={!m.blue_win} />
                  <span
                    className={cn(
                      "w-16 text-xs font-medium",
                      !m.blue_win ? "text-chart-red" : "text-muted-ink",
                    )}
                  >
                    Vermelho
                  </span>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
