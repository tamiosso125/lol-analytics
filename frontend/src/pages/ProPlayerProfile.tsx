import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";
import { championIcon } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

const PRO_POSITIONS: Record<string, string> = {
  top: "Topo",
  jng: "Selva",
  mid: "Meio",
  bot: "Atirador",
  sup: "Suporte",
};

export function ProPlayerProfile() {
  const { name = "" } = useParams();
  const profile = useQuery({
    queryKey: ["pro-player", name],
    queryFn: () => api.proPlayerProfile(name),
  });

  if (profile.isPending) return <Skeleton className="h-96" />;
  if (profile.isError) return <ErrorNote message={profile.error.message} />;
  const p = profile.data;

  return (
    <div className="space-y-5">
      <Link
        to="/competitivo"
        className="inline-flex items-center gap-1.5 text-sm text-secondary-ink hover:text-foreground"
      >
        <ArrowLeft size={14} /> Competitivo
      </Link>

      <PageHeader eyebrow="Jogador — profissional" title={p.name}>
        {p.current_team ? `${p.current_team} · ` : ""}
        {p.games.toLocaleString("pt-BR")} jogos no acervo (2014-2026) · win rate{" "}
        {pct(p.win_rate)}
        {p.main_position ? ` · posição: ${PRO_POSITIONS[p.main_position] ?? p.main_position}` : ""}
      </PageHeader>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Temporadas (ano · time · liga)</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-secondary-ink">
                  <th className="py-2 font-medium">Ano</th>
                  <th className="py-2 font-medium">Time</th>
                  <th className="py-2 font-medium">Liga</th>
                  <th className="py-2 font-medium">Jogos</th>
                  <th className="py-2 font-medium">Win rate</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {p.seasons.map((s, i) => (
                  <tr key={i} className="border-b border-border/50 last:border-0">
                    <td className="py-1.5">{s.year}</td>
                    <td className="py-1.5">{s.team}</td>
                    <td className="py-1.5">{s.league}</td>
                    <td className="py-1.5">{s.games}</td>
                    <td
                      className={cn(
                        "py-1.5 font-medium",
                        s.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red",
                      )}
                    >
                      {pct(s.win_rate)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pool de campeões (carreira)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1.5">
            {p.champion_pool.map((c) => (
              <div key={c.champion} className="flex items-center gap-2.5 text-sm">
                {c.champion_id != null ? (
                  <img src={championIcon(c.champion_id)} alt="" className="size-7 rounded-md" />
                ) : (
                  <span className="size-7 rounded-md border border-dashed border-border" />
                )}
                <span className="min-w-0 flex-1 truncate">{c.champion}</span>
                <span className="text-xs text-muted-ink tabular-nums">{c.games} jogos</span>
                <span
                  className={cn(
                    "w-14 text-right font-medium tabular-nums",
                    c.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red",
                  )}
                >
                  {pct(c.win_rate)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
