import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle, ErrorNote, Skeleton } from "@/components/ui";
import { api, type ChampionMatchup } from "@/lib/api";
import { championDisplayName, championIcon, itemIcon, POSITION_LABELS } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-card px-4 py-3">
      <p className="text-xs text-muted-ink">{label}</p>
      <p className="mt-0.5 text-xl font-semibold tabular-nums tracking-tight">{value}</p>
    </div>
  );
}

/** Itens finalizados mais construídos pelo campeão, com win rate e
 * minuto médio da compra — dos eventos reais das timelines. */
function ItemsCard({ championName }: { championName: string }) {
  const items = useQuery({
    queryKey: ["champion-items", championName],
    queryFn: () => api.championItems(championName),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Itens finalizados mais construídos</CardTitle>
        <p className="mt-0.5 text-xs text-muted-ink">
          Compras reais extraídas das timelines — % dos jogos com o item, win rate nesses
          jogos e minuto médio da compra.
        </p>
      </CardHeader>
      <CardContent>
        {items.isPending ? (
          <Skeleton className="h-48" />
        ) : items.isError ? (
          <ErrorNote message={items.error.message} />
        ) : items.data.items.length === 0 ? (
          <p className="text-sm text-muted-ink">
            Sem itens com amostra suficiente (≥ 20 jogos com o item).
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-secondary-ink">
                <th className="py-2 font-medium">Item</th>
                <th className="py-2 font-medium">Jogos</th>
                <th className="py-2 font-medium">Win rate</th>
                <th className="py-2 text-right font-medium">Compra média</th>
              </tr>
            </thead>
            <tbody className="tabular-nums">
              {items.data.items.map((it) => (
                <tr key={it.item_id} className="border-b border-border/50 last:border-0">
                  <td className="py-1.5">
                    <span className="flex items-center gap-2">
                      <img src={itemIcon(it.item_id)} alt="" className="size-7 rounded" />
                      <span className="truncate">{it.name}</span>
                    </span>
                  </td>
                  <td className="py-1.5">
                    {it.games.toLocaleString("pt-BR")}
                    <span className="ml-1 text-xs text-muted-ink">({pct(it.pick_share)})</span>
                  </td>
                  <td
                    className={cn(
                      "py-1.5 font-medium",
                      it.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red",
                    )}
                  >
                    {pct(it.win_rate)}
                  </td>
                  <td className="py-1.5 text-right text-secondary-ink">{it.avg_minute} min</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
}

/** Presença e desempenho do campeão no COMPETITIVO (Oracle's Elixir),
 * ao lado das estatísticas de solo queue da página. */
function ProCard({ championName }: { championName: string }) {
  const pro = useQuery({
    queryKey: ["champion-pro", championName],
    queryFn: () => api.championPro(championName),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>No competitivo{pro.data ? ` (${pro.data.year})` : ""}</CardTitle>
        <p className="mt-0.5 text-xs text-muted-ink">
          Jogos profissionais (Oracle's Elixir) — presença, win rate e ligas onde aparece.
        </p>
      </CardHeader>
      <CardContent>
        {pro.isPending ? (
          <Skeleton className="h-40" />
        ) : pro.isError ? (
          <ErrorNote message={pro.error.message} />
        ) : pro.data.games === 0 ? (
          <p className="text-sm text-muted-ink">
            Não apareceu no competitivo em {pro.data.year} — pode ser um pick de solo queue
            que os times profissionais não priorizam (ou o inverso do hype).
          </p>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <p className="text-xs text-muted-ink">Presença</p>
                <p className="mt-0.5 text-xl font-semibold tabular-nums">
                  {pct(pro.data.presence)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-ink">Jogos</p>
                <p className="mt-0.5 text-xl font-semibold tabular-nums">
                  {pro.data.games.toLocaleString("pt-BR")}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-ink">Win rate pro</p>
                <p
                  className={cn(
                    "mt-0.5 text-xl font-semibold tabular-nums",
                    (pro.data.win_rate ?? 0) >= 0.5 ? "text-chart-1" : "text-chart-red",
                  )}
                >
                  {pro.data.win_rate != null ? pct(pro.data.win_rate) : "—"}
                </p>
              </div>
            </div>
            <div className="mt-4 space-y-1.5 border-t border-border pt-3">
              {pro.data.leagues.map((l) => (
                <div key={l.league} className="flex items-center gap-2 text-sm">
                  <span className="w-14 shrink-0 font-medium">{l.league}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-foreground/10">
                    <div
                      className="h-full rounded-full bg-chart-1"
                      style={{
                        width: `${(l.games / pro.data.leagues[0].games) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="w-14 text-right text-xs text-muted-ink tabular-nums">
                    {l.games} jogos
                  </span>
                  <span
                    className={cn(
                      "w-12 text-right text-xs font-medium tabular-nums",
                      l.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red",
                    )}
                  >
                    {pct(l.win_rate)}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function MatchupList({ title, matchups }: { title: string; matchups: ChampionMatchup[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {matchups.length === 0 ? (
          <p className="text-sm text-muted-ink">Sem matchups com amostra suficiente (≥ 15 jogos).</p>
        ) : (
          matchups.map((m) => (
            <Link
              key={m.opponent}
              to={`/campeoes/${m.opponent}`}
              className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 hover:bg-foreground/5"
            >
              <img src={championIcon(m.opponent_id)} alt="" className="size-7 rounded-md" />
              <span className="min-w-0 flex-1 truncate text-sm">
                {championDisplayName(m.opponent)}
              </span>
              <span className="text-xs text-muted-ink tabular-nums">{m.games} jogos</span>
              <span
                className={cn(
                  "w-14 text-right text-sm font-medium tabular-nums",
                  m.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red",
                )}
              >
                {pct(m.win_rate)}
              </span>
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  );
}

export function ChampionDetail() {
  const { name = "" } = useParams();
  const detail = useQuery({
    queryKey: ["champion-detail", name],
    queryFn: () => api.championDetail(name),
  });

  if (detail.isPending) {
    return <Skeleton className="h-96" />;
  }
  if (detail.isError) {
    return <ErrorNote message={detail.error.message} />;
  }
  const d = detail.data;
  const best = d.matchups.slice(0, 5);
  const worst = [...d.matchups].reverse().slice(0, 5);

  return (
    <div className="space-y-5">
      <Link
        to="/campeoes"
        className="inline-flex items-center gap-1.5 text-sm text-secondary-ink hover:text-foreground"
      >
        <ArrowLeft size={14} /> Campeões
      </Link>

      <div className="flex items-center gap-4">
        <img src={championIcon(d.champion_id)} alt="" className="size-16 rounded-xl ring-1 ring-gold/40" />
        <div>
          <h1 className="hextech-title text-2xl font-semibold text-gold-bright">
            {championDisplayName(d.champion)}
          </h1>
          <p className="text-sm text-secondary-ink">
            {d.games.toLocaleString("pt-BR")} jogos analisados
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 lg:grid-cols-6">
        <StatTile label="Win rate" value={pct(d.win_rate)} />
        <StatTile label="Pick rate" value={pct(d.pick_rate)} />
        <StatTile label="Ban rate" value={pct(d.ban_rate)} />
        <StatTile label="KDA" value={d.kda != null ? String(d.kda) : "—"} />
        <StatTile label="CS médio" value={d.avg_cs.toLocaleString("pt-BR")} />
        <StatTile label="Ouro médio" value={d.avg_gold.toLocaleString("pt-BR")} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Por posição</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-secondary-ink">
                  <th className="py-2 font-medium">Posição</th>
                  <th className="py-2 font-medium">Jogos</th>
                  <th className="py-2 font-medium">Win rate</th>
                  <th className="py-2 font-medium">KDA</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {d.positions.map((p) => (
                  <tr key={p.position} className="border-b border-border/50 last:border-0">
                    <td className="py-2">{POSITION_LABELS[p.position] ?? p.position}</td>
                    <td className="py-2">{p.games.toLocaleString("pt-BR")}</td>
                    <td className={cn("py-2 font-medium", p.win_rate >= 0.5 ? "text-chart-1" : "text-chart-red")}>
                      {pct(p.win_rate)}
                    </td>
                    <td className="py-2">{p.kda ?? "—"}</td>
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
            {d.recent_games.map((g) => (
              <div
                key={g.match_id}
                className={cn(
                  "flex items-center gap-3 rounded-md border-l-2 bg-foreground/5 px-3 py-1.5 text-xs",
                  g.win ? "border-chart-1" : "border-chart-red",
                )}
              >
                <span className={cn("w-14 font-medium", g.win ? "text-chart-1" : "text-chart-red")}>
                  {g.win ? "Vitória" : "Derrota"}
                </span>
                <span className="w-16 text-secondary-ink">
                  {POSITION_LABELS[g.position] ?? g.position}
                </span>
                <span className="tabular-nums">
                  {g.kills}/{g.deaths}/{g.assists}
                </span>
                <span className="ml-auto text-muted-ink tabular-nums">
                  {g.duration_min} min · patch {g.patch} ·{" "}
                  {new Date(g.date).toLocaleDateString("pt-BR")}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <MatchupList title="Melhores matchups (win rate contra)" matchups={best} />
        <MatchupList title="Piores matchups (win rate contra)" matchups={worst} />
      </div>

      <div className="grid grid-cols-5 gap-4">
        <div className="col-span-3">
          <ItemsCard championName={d.champion} />
        </div>
        <div className="col-span-2">
          <ProCard championName={d.champion} />
        </div>
      </div>
    </div>
  );
}
