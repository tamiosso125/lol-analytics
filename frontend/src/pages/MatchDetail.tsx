import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, Castle, Eye, FlaskConical, Flame, Shield, Skull } from "lucide-react";
import { useEffect, useMemo, useState, type ComponentType } from "react";
import { Link, useParams } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, ChartTooltip, GRID } from "@/components/chart";
import { MapHeatmap } from "@/components/MapHeatmap";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api, type MatchParticipantFull, type MatchState, type MatchTeam, type ProbPoint } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { deltaColor, formatPct as pct, winColor } from "@/lib/format";
import { RANGES, SLIDER_KEYS, SLIDER_LABELS } from "@/lib/matchState";
import { cn } from "@/lib/utils";

/** Linha de objetivo com barras espelhadas a partir do centro
 * (estilo op.gg): azul cresce para a esquerda, vermelho para a direita. */
function ObjectiveRow({
  icon: Icon,
  label,
  blue,
  red,
}: {
  icon: ComponentType<{ size?: number; className?: string }>;
  label: string;
  blue: number;
  red: number;
}) {
  const max = Math.max(blue, red, 1);
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="flex w-24 shrink-0 items-center gap-1.5 text-xs text-secondary-ink">
        <Icon size={13} className="text-gold" />
        {label}
      </span>
      <span className="w-6 text-right font-semibold tabular-nums text-chart-1">{blue}</span>
      <div className="flex h-2.5 flex-1 items-center">
        <div className="flex h-full flex-1 justify-end overflow-hidden rounded-l-full bg-foreground/10">
          <div
            className="h-full rounded-l-full bg-chart-1"
            style={{ width: `${(blue / max) * 100}%` }}
          />
        </div>
        <div className="h-full w-px shrink-0 bg-foreground/40" />
        <div className="h-full flex-1 overflow-hidden rounded-r-full bg-foreground/10">
          <div
            className="h-full rounded-r-full bg-chart-red"
            style={{ width: `${(red / max) * 100}%` }}
          />
        </div>
      </div>
      <span className="w-6 font-semibold tabular-nums text-chart-red">{red}</span>
    </div>
  );
}

const OBJECTIVES: { key: keyof Omit<MatchTeam, "team_id" | "win">; label: string; icon: ComponentType<{ size?: number; className?: string }> }[] = [
  { key: "towers", label: "Torres", icon: Castle },
  { key: "dragons", label: "Dragões", icon: Flame },
  { key: "barons", label: "Barões", icon: Skull },
  { key: "heralds", label: "Arautos", icon: Eye },
  { key: "inhibitors", label: "Inibidores", icon: Shield },
];

const fmtDiff = (v: number) => (v > 0 ? `+${v.toLocaleString("pt-BR")}` : v.toLocaleString("pt-BR"));

/** Modo "e se": pega o estado REAL da partida no minuto escolhido (da
 * própria curva de probabilidade) e deixa editá-lo — o delta entre a
 * probabilidade real e a editada responde perguntas contrafactuais de
 * estado ("e se aos 14 min o time azul tivesse +1k de ouro?"). É uma
 * intervenção sobre o ESTADO agregado, não sobre uma ação específica —
 * a distinção fica no texto do card. */
function WhatIfCard({ curve, minute }: { curve: ProbPoint[]; minute: number }) {
  const point = useMemo(
    () => curve.find((p) => p.minute === minute) ?? curve[curve.length - 1],
    [curve, minute],
  );
  const [state, setState] = useState<MatchState | null>(null);

  // re-semeia o editor sempre que o minuto (slider compartilhado) muda
  useEffect(() => {
    if (point) {
      setState({
        gold_diff: point.gold_diff,
        xp_diff: point.xp_diff,
        kill_diff: point.kill_diff,
        tower_diff: point.tower_diff,
        dragon_diff: point.dragon_diff,
        minute: point.model_cutoff,
      });
    }
  }, [point]);

  const predict = useMutation({ mutationFn: api.predict });
  const { mutate } = predict;
  useEffect(() => {
    if (!state) return;
    const t = setTimeout(() => mutate(state), 300);
    return () => clearTimeout(t);
  }, [state, mutate]);

  if (!point || !state) return null;

  const real = point.blue_win_probability;
  const whatIf = predict.data?.blue_win_probability;
  const delta = whatIf != null ? whatIf - real : null;
  const edited = SLIDER_KEYS.some((k) => state[k] !== point[k]);
  const baseRanges = RANGES[point.model_cutoff];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FlaskConical size={14} className="text-gold" />E se, aos {point.minute} minutos…
        </CardTitle>
        <p className="mt-0.5 text-xs text-muted-ink">
          O estado abaixo é o REAL da partida nesse minuto (siga o slider do mapa de calor).
          Edite-o e veja como a probabilidade mudaria — uma intervenção sobre o estado
          agregado, segundo o modelo da fase ({point.model_cutoff} min).
        </p>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          {SLIDER_KEYS.map((key) => {
            // range da fase, esticado se o valor real da partida passar dele
            const min = Math.min(baseRanges[key].min, point[key]);
            const max = Math.max(baseRanges[key].max, point[key]);
            return (
              <div key={key}>
                <div className="mb-0.5 flex justify-between text-xs">
                  <label htmlFor={`ws-${key}`} className="text-secondary-ink">
                    {SLIDER_LABELS[key]}
                  </label>
                  <span className="tabular-nums">
                    <span
                      className={cn(
                        "font-medium",
                        state[key] !== point[key] && "text-gold",
                      )}
                    >
                      {fmtDiff(state[key])}
                    </span>
                    {state[key] !== point[key] && (
                      <span className="ml-1 text-muted-ink">(real: {fmtDiff(point[key])})</span>
                    )}
                  </span>
                </div>
                <input
                  id={`ws-${key}`}
                  type="range"
                  min={min}
                  max={max}
                  step={baseRanges[key].step}
                  value={state[key]}
                  onChange={(e) => setState((s) => s && { ...s, [key]: Number(e.target.value) })}
                  className="w-full accent-accent"
                />
              </div>
            );
          })}
          <button
            onClick={() =>
              setState({
                gold_diff: point.gold_diff,
                xp_diff: point.xp_diff,
                kill_diff: point.kill_diff,
                tower_diff: point.tower_diff,
                dragon_diff: point.dragon_diff,
                minute: point.model_cutoff,
              })
            }
            className="text-xs text-muted-ink underline-offset-2 hover:underline"
          >
            Voltar ao estado real
          </button>
        </div>

        <div className="flex flex-col justify-center">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-ink">Real (aconteceu)</p>
              <p className="mt-0.5 text-3xl font-semibold tabular-nums tracking-tight">
                {(real * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-ink">E se…</p>
              <p
                className={cn(
                  "mt-0.5 text-3xl font-semibold tabular-nums tracking-tight",
                  edited && "text-gold-bright",
                )}
              >
                {predict.isError ? "—" : whatIf != null ? `${(whatIf * 100).toFixed(1)}%` : "…"}
              </p>
            </div>
          </div>
          {delta != null && edited && (
            <p
              className={cn(
                "mt-3 text-sm font-medium tabular-nums",
                deltaColor(delta),
              )}
            >
              {delta >= 0 ? "+" : ""}
              {(delta * 100).toFixed(1)} pontos percentuais para o time azul
            </p>
          )}
          {predict.isError && <ErrorNote message={predict.error.message} />}
          <p className="mt-4 border-t border-border pt-2 text-xs leading-relaxed text-muted-ink">
            Leitura honesta: isto responde "e se o ESTADO fosse outro" — não "e se o
            jogador tivesse feito a jogada Y" (a mesma diferença de ouro pode vir de
            jogadas diferentes; ações específicas exigiriam dados de replay que a API da
            Riot não fornece).
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function TeamTable({ players, label, won }: { players: MatchParticipantFull[]; label: string; won: boolean }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className={winColor(won)}>
          {label} — {won ? "Vitória" : "Derrota"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-secondary-ink">
              <th className="py-2 font-medium">Campeão</th>
              <th className="py-2 font-medium">KDA</th>
              <th className="py-2 font-medium">Ouro</th>
              <th className="py-2 font-medium">CS</th>
              <th className="py-2 font-medium">Dano</th>
              <th className="py-2 font-medium">Visão</th>
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {players.map((p) => (
              <tr key={p.champion} className="border-b border-border/50 last:border-0">
                <td className="py-1.5">
                  <Link to={`/campeoes/${p.champion}`} className="flex items-center gap-2 hover:underline">
                    <img src={championIcon(p.champion_id)} alt="" className="size-7 rounded-md" />
                    <span>
                      {championDisplayName(p.champion)}
                      <span className="ml-1.5 text-xs text-muted-ink">
                        {POSITION_LABELS[p.position] ?? p.position}
                      </span>
                    </span>
                  </Link>
                </td>
                <td className="py-1.5">{p.kills}/{p.deaths}/{p.assists}</td>
                <td className="py-1.5">{p.gold.toLocaleString("pt-BR")}</td>
                <td className="py-1.5">{p.cs}</td>
                <td className="py-1.5">{p.dmg.toLocaleString("pt-BR")}</td>
                <td className="py-1.5">{p.vision}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

export function MatchDetail() {
  const { id = "" } = useParams();
  const [minute, setMinute] = useState(14);
  const analysis = useQuery({
    queryKey: ["match-analysis", id],
    queryFn: () => api.matchAnalysis(id),
  });
  const positions = useQuery({
    queryKey: ["match-positions", id],
    queryFn: () => api.matchPositions(id),
  });

  if (analysis.isPending) return <Skeleton className="h-96" />;
  if (analysis.isError) return <ErrorNote message={analysis.error.message} />;
  const m = analysis.data;
  const blue = m.participants.filter((p) => p.team_id === 100);
  const red = m.participants.filter((p) => p.team_id === 200);
  const blueTeam = m.teams.find((t) => t.team_id === 100);
  const redTeam = m.teams.find((t) => t.team_id === 200);

  return (
    <div className="space-y-5">
      <Link
        to="/partidas"
        className="inline-flex items-center gap-1.5 text-sm text-secondary-ink hover:text-foreground"
      >
        <ArrowLeft size={14} /> Partidas
      </Link>

      <PageHeader eyebrow="Análise" title="Análise da partida">
        <span className="tabular-nums">
          {new Date(m.date).toLocaleString("pt-BR")} · {m.duration_min} min · patch {m.patch} ·{" "}
          <span className={winColor(!!blueTeam?.win)}>
            {blueTeam?.win ? "vitória do time azul" : "vitória do time vermelho"}
          </span>
        </span>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle>Probabilidade de vitória do time azul, minuto a minuto</CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            Cada ponto usa o modelo da fase correspondente (10/15/20/25 min) sobre o estado
            real da partida naquele minuto — é a leitura retrospectiva do que o modelo diria
            ao vivo.
          </p>
        </CardHeader>
        <CardContent className="h-80">
          {m.prob_curve.length === 0 ? (
            <p className="text-sm text-muted-ink">
              Sem timeline disponível para esta partida.
            </p>
          ) : (
            <ResponsiveContainer>
              <LineChart data={m.prob_curve} margin={{ right: 16 }}>
                <CartesianGrid vertical={false} {...GRID} />
                <XAxis
                  dataKey="minute"
                  tick={AXIS_TICK}
                  stroke="var(--baseline)"
                  tickFormatter={(v: number) => `${v}'`}
                />
                <YAxis
                  domain={[0, 1]}
                  tickFormatter={pct}
                  tick={AXIS_TICK}
                  stroke="var(--baseline)"
                />
                <ReferenceLine y={0.5} stroke="var(--muted-ink)" strokeDasharray="4 4" />
                <Tooltip
                  content={
                    <ChartTooltip
                      format={(v, name) =>
                        name === "Prob. vitória azul" ? pct(v) : v.toLocaleString("pt-BR")
                      }
                    />
                  }
                />
                <Line
                  type="monotone"
                  dataKey="blue_win_probability"
                  name="Prob. vitória azul"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Mapa de calor da partida</CardTitle>
            <p className="mt-0.5 text-xs text-muted-ink">
              Onde os dois times estavam em cada momento — arraste o minuto.
            </p>
          </CardHeader>
          <CardContent>
            {positions.isPending ? (
              <Skeleton className="aspect-square w-full" />
            ) : positions.isError ? (
              <p className="text-sm text-muted-ink">
                Sem timeline com posições para esta partida.
              </p>
            ) : (
              <MapHeatmap data={positions.data} minute={minute} onMinuteChange={setMinute} />
            )}
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Diferença de ouro (azul − vermelho)</CardTitle>
            </CardHeader>
            <CardContent className="h-56">
              {m.prob_curve.length > 0 && (
                <ResponsiveContainer>
                  <LineChart data={m.prob_curve} margin={{ right: 16 }}>
                    <CartesianGrid vertical={false} {...GRID} />
                    <XAxis
                      dataKey="minute"
                      tick={AXIS_TICK}
                      stroke="var(--baseline)"
                      tickFormatter={(v: number) => `${v}'`}
                    />
                    <YAxis tick={AXIS_TICK} stroke="var(--baseline)" />
                    <ReferenceLine y={0} stroke="var(--baseline)" />
                    <Tooltip content={<ChartTooltip format={(v) => v.toLocaleString("pt-BR")} />} />
                    <Line
                      type="monotone"
                      dataKey="gold_diff"
                      name="Diferença de ouro"
                      stroke="var(--chart-2)"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          {blueTeam && redTeam && (
            <Card className="flex-1">
              <CardHeader>
                <CardTitle>
                  Objetivos{positions.data ? ` até o minuto ${minute}` : " (final)"}
                </CardTitle>
                <p className="mt-0.5 text-xs text-muted-ink">
                  <span className="font-medium text-chart-1">azul</span> ×{" "}
                  <span className="font-medium text-chart-red">vermelho</span>
                  {positions.data
                    ? " — sincronizado com o slider do mapa de calor"
                    : " — barras espelhadas a partir do centro"}
                </p>
              </CardHeader>
              <CardContent className="space-y-3 pt-2">
                {OBJECTIVES.map((o) => {
                  // com timeline, conta os eventos até o minuto do slider;
                  // sem ela, cai para os totais finais da tabela teams
                  const count = (team: number) =>
                    positions.data
                      ? positions.data.objectives.filter(
                          (e) => e.kind === o.key && e.team_id === team && e.minute <= minute,
                        ).length
                      : (team === 100 ? blueTeam : redTeam)[o.key];
                  return (
                    <ObjectiveRow
                      key={o.key}
                      icon={o.icon}
                      label={o.label}
                      blue={count(100)}
                      red={count(200)}
                    />
                  );
                })}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {m.prob_curve.length > 0 && <WhatIfCard curve={m.prob_curve} minute={minute} />}

      <div className="grid grid-cols-2 gap-4">
        <TeamTable players={blue} label="Time azul" won={blueTeam?.win ?? false} />
        <TeamTable players={red} label="Time vermelho" won={!(blueTeam?.win ?? false)} />
      </div>
    </div>
  );
}
