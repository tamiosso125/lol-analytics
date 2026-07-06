import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { RecentGameRow } from "@/components/RecentGameRow";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { formatPct as pct, winColor } from "@/lib/format";
import { cn } from "@/lib/utils";

export function PlayerProfile() {
  const { puuid = "" } = useParams();
  const profile = useQuery({
    queryKey: ["player-profile", puuid],
    queryFn: () => api.playerProfile(puuid),
  });

  if (profile.isPending) return <Skeleton className="h-96" />;
  if (profile.isError) return <ErrorNote message={profile.error.message} />;
  const p = profile.data;
  const displayName = p.name ? `${p.name}#${p.tag}` : `${puuid.slice(0, 10)}…`;
  // forma recente: as últimas 10 vs a taxa geral
  const recentWr =
    p.recent_games.length > 0
      ? p.recent_games.filter((g) => g.win).length / p.recent_games.length
      : null;

  return (
    <div className="space-y-5">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm text-secondary-ink hover:text-foreground"
      >
        <ArrowLeft size={14} /> Início
      </Link>

      <PageHeader eyebrow="Jogador — solo queue" title={displayName}>
        {p.tier ? `${p.tier}${p.division ? ` ${p.division}` : ""} · ${p.league_points ?? 0} PDL · ` : ""}
        {p.games.toLocaleString("pt-BR")} partidas no dataset
        {p.main_position ? ` · principal: ${POSITION_LABELS[p.main_position] ?? p.main_position}` : ""}
      </PageHeader>

      <div className="grid grid-cols-3 gap-3">
        <Card>
          <CardHeader>
            <CardTitle>Win rate geral</CardTitle>
          </CardHeader>
          <CardContent>
            <span
              className={cn(
                "text-3xl font-semibold tabular-nums tracking-tight",
                winColor(p.win_rate),
              )}
            >
              {pct(p.win_rate)}
            </span>
            <p className="mt-1 text-xs text-muted-ink">{p.games} partidas</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Forma recente</CardTitle>
          </CardHeader>
          <CardContent>
            <span
              className={cn(
                "text-3xl font-semibold tabular-nums tracking-tight",
                winColor(recentWr ?? 0),
              )}
            >
              {recentWr != null ? pct(recentWr) : "—"}
            </span>
            <p className="mt-1 text-xs text-muted-ink">últimas {p.recent_games.length} partidas</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Campeão mais jogado</CardTitle>
          </CardHeader>
          <CardContent>
            {p.champion_pool[0] ? (
              <span className="flex items-center gap-2">
                <img
                  src={championIcon(p.champion_pool[0].champion_id)}
                  alt=""
                  className="size-9 rounded-md ring-1 ring-gold/40"
                />
                <span>
                  <span className="block font-semibold">
                    {championDisplayName(p.champion_pool[0].champion)}
                  </span>
                  <span className="text-xs text-muted-ink tabular-nums">
                    {p.champion_pool[0].games} jogos · {pct(p.champion_pool[0].win_rate)}
                  </span>
                </span>
              </span>
            ) : (
              "—"
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Pool de campeões</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-secondary-ink">
                  <th className="py-2 font-medium">Campeão</th>
                  <th className="py-2 font-medium">Jogos</th>
                  <th className="py-2 font-medium">Win rate</th>
                  <th className="py-2 font-medium">KDA</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {p.champion_pool.map((c) => (
                  <tr key={c.champion} className="border-b border-border/50 last:border-0">
                    <td className="py-1.5">
                      <Link
                        to={`/campeoes/${c.champion}`}
                        className="flex items-center gap-2 hover:underline"
                      >
                        <img src={championIcon(c.champion_id)} alt="" className="size-6 rounded" />
                        {championDisplayName(c.champion)}
                      </Link>
                    </td>
                    <td className="py-1.5">{c.games}</td>
                    <td
                      className={cn(
                        "py-1.5 font-medium",
                        winColor(c.win_rate),
                      )}
                    >
                      {pct(c.win_rate)}
                    </td>
                    <td className="py-1.5">{c.kda ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Últimas partidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {p.recent_games.map((g) => (
              <RecentGameRow
                key={g.match_id}
                matchId={g.match_id}
                championId={g.champion_id}
                win={g.win}
                positionLabel={POSITION_LABELS[g.position] ?? g.position}
                kills={g.kills}
                deaths={g.deaths}
                assists={g.assists}
                durationMin={g.duration_min}
                date={g.date}
              />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
