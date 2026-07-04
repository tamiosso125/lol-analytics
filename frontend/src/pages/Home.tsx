import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Ban, Crown, Search, Shield, Swords, TrendingUp } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import type { ComponentType } from "react";

import { Card, CardContent, CardHeader, CardTitle, ErrorNote, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";
import { championDisplayName, championIcon, championSplash } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

/** Busca de campeão estilo op.gg: filtra no cliente e navega no clique. */
function ChampionSearch() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const champions = useQuery({
    queryKey: ["champions-all"],
    queryFn: () => api.champions({ minGames: 1, limit: 300 }),
  });
  const matches = useMemo(() => {
    if (q.trim().length < 2 || !champions.data) return [];
    const needle = q.trim().toLowerCase();
    return champions.data
      .filter((c) => championDisplayName(c.champion).toLowerCase().includes(needle))
      .slice(0, 6);
  }, [q, champions.data]);

  return (
    <div className="relative max-w-sm">
      <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-ink" />
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && matches[0]) navigate(`/campeoes/${matches[0].champion}`);
        }}
        placeholder="Buscar um campeão… (ex.: Ahri)"
        className="w-full rounded-full border border-gold/40 bg-background/70 py-2.5 pl-10 pr-4 text-sm backdrop-blur placeholder:text-muted-ink focus:outline-none focus:ring-2 focus:ring-gold/40"
      />
      {matches.length > 0 && (
        <div className="absolute inset-x-0 top-full z-10 mt-1.5 overflow-hidden rounded-xl border border-border bg-card shadow-lg">
          {matches.map((c) => (
            <button
              key={c.champion}
              onClick={() => navigate(`/campeoes/${c.champion}`)}
              className="flex w-full items-center gap-2.5 px-3.5 py-2 text-left text-sm hover:bg-foreground/5"
            >
              <img src={championIcon(c.champion_id)} alt="" className="size-7 rounded-md" />
              <span className="flex-1">{championDisplayName(c.champion)}</span>
              <span className="text-xs text-muted-ink tabular-nums">
                {pct(c.win_rate)} WR · {c.games.toLocaleString("pt-BR")} jogos
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/** Top-5 estilo leagueofgraphs: posição, ícone, nome, micro-barra + valor. */
function RankingCard({
  title,
  metric,
  format = pct,
  color,
  isPending,
  rows,
}: {
  title: string;
  metric: (c: { win_rate: number; ban_rate: number; games: number }) => number;
  /** contagens (jogos) não são percentuais — cada card formata o seu valor */
  format?: (v: number) => string;
  color: string;
  isPending: boolean;
  rows: { champion: string; champion_id: number; win_rate: number; ban_rate: number; games: number }[];
}) {
  const max = Math.max(0.01, ...rows.map(metric));
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        <Link to="/campeoes" className="text-xs text-gold underline-offset-2 hover:underline">
          ver todos
        </Link>
      </CardHeader>
      <CardContent className="space-y-2 pt-1">
        {isPending
          ? Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-8" />)
          : rows.map((c, i) => (
              <Link
                key={c.champion}
                to={`/campeoes/${c.champion}`}
                className="flex items-center gap-2.5 rounded-lg px-1 py-0.5 text-sm hover:bg-foreground/5"
              >
                <span className="w-4 text-xs text-muted-ink tabular-nums">{i + 1}.</span>
                <img src={championIcon(c.champion_id)} alt="" className="size-7 rounded-md" />
                <span className="min-w-0 flex-1 truncate">{championDisplayName(c.champion)}</span>
                <div className="h-1.5 w-16 shrink-0 overflow-hidden rounded-full bg-foreground/10">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${(metric(c) / max) * 100}%`, background: color }}
                  />
                </div>
                <span className="w-12 text-right text-xs font-medium tabular-nums">
                  {format(metric(c))}
                </span>
              </Link>
            ))}
      </CardContent>
    </Card>
  );
}

function InsightCard({
  icon: Icon,
  title,
  headline,
  detail,
  why,
  to,
  image,
}: {
  icon: ComponentType<{ size?: number; className?: string }>;
  title: string;
  headline: string;
  detail: string;
  why: string;
  to?: string;
  image?: string;
}) {
  const body = (
    <Card className="group h-full border-border transition-all hover:border-gold/60 hover:shadow-[0_0_18px_-6px_var(--gold)]">
      <CardContent className="flex h-full flex-col pt-4">
        <div className="hextech-title flex items-center gap-2 text-[11px] font-medium text-gold">
          <Icon size={13} />
          {title}
        </div>
        <div className="mt-3 flex items-center gap-3">
          {image && (
            <img
              src={image}
              alt=""
              className="size-12 rounded-lg ring-1 ring-gold/40 transition-transform group-hover:scale-105"
            />
          )}
          <div>
            <p className="text-2xl font-semibold tracking-tight">{headline}</p>
            <p className="text-sm text-secondary-ink">{detail}</p>
          </div>
        </div>
        <p className="mt-3 border-t border-border pt-2 text-xs leading-relaxed text-muted-ink">
          <span className="font-medium text-secondary-ink">Por quê: </span>
          {why}
        </p>
      </CardContent>
    </Card>
  );
  return to ? <Link to={to}>{body}</Link> : body;
}

function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="pt-2">
      <p className="hextech-title text-[11px] font-medium text-gold">{eyebrow}</p>
      <h2 className="mt-0.5 text-lg font-semibold tracking-tight">{title}</h2>
    </div>
  );
}

export function Home() {
  const highlights = useQuery({ queryKey: ["highlights"], queryFn: api.highlights });
  const overview = useQuery({ queryKey: ["overview"], queryFn: api.overview });
  const topWin = useQuery({
    queryKey: ["home-top-win"],
    queryFn: () => api.champions({ minGames: 200, sort: "win_rate", limit: 5 }),
  });
  const topPlayed = useQuery({
    queryKey: ["home-top-played"],
    queryFn: () => api.champions({ minGames: 30, sort: "games", limit: 5 }),
  });
  const topBanned = useQuery({
    queryKey: ["home-top-banned"],
    queryFn: () => api.champions({ minGames: 30, sort: "ban_rate", limit: 5 }),
  });
  const recent = useQuery({
    queryKey: ["home-recent"],
    queryFn: () => api.recentMatches(4),
  });

  if (highlights.isPending) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64" />
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44" />
          ))}
        </div>
      </div>
    );
  }
  if (highlights.isError) return <ErrorNote message={highlights.error.message} />;
  const h = highlights.data;
  const heroChampion = h.best_champion;
  const o = overview.data;

  return (
    <div className="space-y-5">
      <div className="relative overflow-hidden rounded-2xl border border-gold/30">
        {heroChampion && (
          <img
            src={championSplash(heroChampion.champion_id)}
            alt=""
            className="absolute inset-0 size-full object-cover object-[center_20%]"
          />
        )}
        <div className="absolute inset-0 bg-linear-to-r from-background via-background/85 to-background/30" />
        <div className="relative px-8 py-10">
          <p className="hextech-title text-xs text-gold">Plataforma de análise — TCC</p>
          <h1 className="hextech-title mt-2 text-4xl font-semibold text-gold-bright">
            Hextech Lab
          </h1>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-secondary-ink">
            {h.total_matches.toLocaleString("pt-BR")} partidas ranqueadas de Challenger e
            Grandmaster do Brasil, destiladas em insights com o porquê de cada um. Explore o{" "}
            <Link to="/dashboard" className="text-gold hover:underline">
              dashboard
            </Link>
            , monte cenários na{" "}
            <Link to="/predicao" className="text-gold hover:underline">
              predição
            </Link>{" "}
            ou{" "}
            <Link to="/montar" className="text-gold hover:underline">
              simule um confronto 5v5
            </Link>
            .
          </p>
          <div className="mt-4">
            <ChampionSearch />
          </div>
          {o && (
            <div className="mt-5 flex flex-wrap gap-x-6 gap-y-1 text-sm text-secondary-ink">
              {[
                [o.matches.toLocaleString("pt-BR"), "partidas"],
                [o.players.toLocaleString("pt-BR"), "jogadores"],
                [String(o.patches), "patches"],
                [`${o.avg_duration_min} min`, "duração média"],
              ].map(([v, label]) => (
                <span key={label} className="tabular-nums">
                  <span className="font-semibold text-foreground">{v}</span>{" "}
                  <span className="text-muted-ink">{label}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <SectionTitle eyebrow="Rankings" title="O topo do alto elo BR" />
      <div className="grid grid-cols-3 gap-4">
        <RankingCard
          title="Maior win rate (200+ jogos)"
          metric={(c) => c.win_rate}
          color="var(--chart-1)"
          isPending={topWin.isPending}
          rows={topWin.data ?? []}
        />
        <RankingCard
          title="Mais jogados"
          metric={(c) => c.games}
          format={(v) => v.toLocaleString("pt-BR")}
          color="var(--chart-2)"
          isPending={topPlayed.isPending}
          rows={topPlayed.data ?? []}
        />
        <RankingCard
          title="Mais banidos"
          metric={(c) => c.ban_rate}
          color="var(--chart-red)"
          isPending={topBanned.isPending}
          rows={topBanned.data ?? []}
        />
      </div>

      <SectionTitle eyebrow="Insights" title="O que os dados mostram — e por quê" />
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-3">
        {h.best_player && (
          <InsightCard
            icon={Crown}
            title="Melhor jogador do dataset"
            headline={
              h.best_player.name
                ? `${h.best_player.name}#${h.best_player.tag}`
                : `${h.best_player.puuid.slice(0, 8)}…`
            }
            detail={`${pct(h.best_player.win_rate)} de vitórias em ${h.best_player.games} partidas (${h.best_player.tier})`}
            why={`Maior taxa de vitória entre jogadores com pelo menos 20 partidas coletadas — ${Math.round(
              h.best_player.win_rate * h.best_player.games,
            )} vitórias em ${h.best_player.games} jogos é consistência, não sorte de poucas partidas.`}
          />
        )}
        {h.best_champion && (
          <InsightCard
            icon={TrendingUp}
            title="Melhor campeão para subir de elo"
            headline={championDisplayName(h.best_champion.champion)}
            detail={`${pct(h.best_champion.win_rate)} de vitórias em ${h.best_champion.games.toLocaleString("pt-BR")} jogos`}
            why="Maior win rate entre campeões com 200+ jogos — amostra grande o suficiente para o número ser confiável, não um campeão de nicho com meia dúzia de partidas."
            to={`/campeoes/${h.best_champion.champion}`}
            image={championIcon(h.best_champion.champion_id)}
          />
        )}
        {h.most_lopsided_matchup && (
          <InsightCard
            icon={Swords}
            title="Matchup mais desequilibrado"
            headline={`${championDisplayName(h.most_lopsided_matchup.champion)} × ${championDisplayName(h.most_lopsided_matchup.opponent)}`}
            detail={`${championDisplayName(h.most_lopsided_matchup.champion)} vence ${pct(h.most_lopsided_matchup.win_rate)} (${h.most_lopsided_matchup.games} jogos)`}
            why={`Na mesma posição, ${championDisplayName(h.most_lopsided_matchup.champion)} contra ${championDisplayName(h.most_lopsided_matchup.opponent)} é o confronto mais distante de 50% entre os com 30+ jogos — um counter claro, não ruído de amostra.`}
            to={`/campeoes/${h.most_lopsided_matchup.champion}`}
            image={championIcon(h.most_lopsided_matchup.champion_id)}
          />
        )}
        {h.most_banned && (
          <InsightCard
            icon={Ban}
            title="Campeão mais banido"
            headline={championDisplayName(h.most_banned.champion)}
            detail={`banido em ${pct(h.most_banned.ban_rate)} das partidas`}
            why="A taxa de banimento mede o quanto os jogadores consideram um campeão opressor — mais de metade das partidas removendo-o do jogo é o maior 'voto de medo' do dataset."
            to={`/campeoes/${h.most_banned.champion}`}
            image={championIcon(h.most_banned.champion_id)}
          />
        )}
        <InsightCard
          icon={Shield}
          title="O lado do mapa importa"
          headline={`Vermelho vence ${pct(h.red_side_win_rate)}`}
          detail={`vs ${pct(1 - h.red_side_win_rate)} do lado azul`}
          why="A literatura aponta leve vantagem azul no solo queue — mas no alto elo BR o vermelho domina, provavelmente pelo counter-pick garantido (que pesa mais quando todos sabem punir draft) e pelo acesso ao pit do dragão. Um achado do dataset que qualquer análise aqui precisa descontar."
          to="/dashboard"
        />
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="hextech-title text-[11px] font-medium text-gold">
              Partidas recentes
            </CardTitle>
            <Link
              to="/partidas"
              className="inline-flex items-center gap-1 text-xs text-gold underline-offset-2 hover:underline"
            >
              ver todas <ArrowRight size={11} />
            </Link>
          </CardHeader>
          <CardContent className="space-y-1.5 pt-1">
            {recent.isPending
              ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-8" />)
              : (recent.data ?? []).map((m) => (
                  <Link
                    key={m.match_id}
                    to={`/partidas/${m.match_id}`}
                    className={cn(
                      "flex items-center gap-2 rounded-lg border-l-2 px-2 py-1 text-xs hover:bg-foreground/5",
                      m.blue_win ? "border-l-chart-1" : "border-l-chart-red",
                    )}
                  >
                    <span className="w-14 shrink-0 text-muted-ink tabular-nums">
                      {m.duration_min} min
                    </span>
                    <span className="flex gap-0.5">
                      {m.participants.slice(0, 5).map((p) => (
                        <img
                          key={p.champion}
                          src={championIcon(p.champion_id)}
                          alt=""
                          className="size-5 rounded"
                        />
                      ))}
                    </span>
                    <span className="text-muted-ink">vs</span>
                    <span className="flex gap-0.5">
                      {m.participants.slice(5).map((p) => (
                        <img
                          key={p.champion}
                          src={championIcon(p.champion_id)}
                          alt=""
                          className="size-5 rounded"
                        />
                      ))}
                    </span>
                  </Link>
                ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
