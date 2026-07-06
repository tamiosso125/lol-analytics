import { useMutation } from "@tanstack/react-query";
import { Pause, Play, RotateCcw, Shuffle } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, GRID } from "@/components/chart";
import { Button, Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api, type MatchAnalysis } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { formatPct as pct, winColor } from "@/lib/format";
import { cn } from "@/lib/utils";

const SPEEDS = [1, 2, 4] as const;
const TICK_MS = 1000; // 1 minuto de jogo por segundo real (× velocidade)

/** Painel de um fator do estado atual (ouro/abates/etc), com sinal e cor. */
function StateStat({ label, value, unit }: { label: string; value: number; unit?: string }) {
  const fmt = value > 0 ? `+${value.toLocaleString("pt-BR")}` : value.toLocaleString("pt-BR");
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2">
      <p className="text-xs text-muted-ink">{label}</p>
      <p
        className={cn(
          "mt-0.5 text-lg font-semibold tabular-nums",
          value > 0 ? "text-chart-1" : value < 0 ? "text-chart-red" : "text-secondary-ink",
        )}
      >
        {fmt}
        {unit && <span className="ml-0.5 text-xs font-normal text-muted-ink">{unit}</span>}
      </p>
    </div>
  );
}

export function LiveReplay() {
  const [data, setData] = useState<MatchAnalysis | null>(null);
  const [idx, setIdx] = useState(0); // índice na prob_curve (minuto atual)
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [revealed, setRevealed] = useState(false);

  const load = useMutation({
    mutationFn: async () => {
      const { match_id } = await api.randomMatch();
      return api.matchAnalysis(match_id);
    },
    onSuccess: (d) => {
      setData(d);
      setIdx(0);
      setRevealed(false);
      setPlaying(d.prob_curve.length > 1);
    },
  });

  const curve = data?.prob_curve ?? [];
  const lastIdx = curve.length - 1;

  // avança um minuto por tick; pausa e revela o resultado ao chegar no fim
  const timer = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  useEffect(() => {
    clearInterval(timer.current);
    if (!playing || curve.length === 0) return;
    timer.current = setInterval(() => {
      setIdx((i) => {
        if (i >= lastIdx) {
          setPlaying(false);
          setRevealed(true);
          return i;
        }
        return i + 1;
      });
    }, TICK_MS / speed);
    return () => clearInterval(timer.current);
  }, [playing, speed, lastIdx, curve.length]);

  const point = curve[idx];
  const shown = useMemo(() => curve.slice(0, idx + 1), [curve, idx]);
  const blueTeam = data?.teams.find((t) => t.team_id === 100);
  const blueWon = blueTeam?.win ?? false;
  const modelSaysBlue = point ? point.blue_win_probability >= 0.5 : false;

  return (
    <div className="space-y-5">
      <PageHeader eyebrow="Tempo real" title="Ao vivo (simulação)">
        Uma partida real reproduzida minuto a minuto, como se estivesse acontecendo agora — a
        probabilidade de vitória sobe e desce a cada minuto, do jeito que o modelo veria ao
        vivo. É a base da análise em tempo real (o mesmo motor rodaria sobre um feed real de
        jogo); aqui o "feed" é uma partida já coletada, para demonstrar sem depender de haver
        jogo no ar.
      </PageHeader>

      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={() => load.mutate()} disabled={load.isPending}>
          <Shuffle size={14} />
          {load.isPending ? "Sorteando…" : data ? "Nova partida" : "Simular uma partida"}
        </Button>
        {data && (
          <>
            <button
              onClick={() => {
                if (idx >= lastIdx) setIdx(0);
                setRevealed(false);
                setPlaying((p) => !p);
              }}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm hover:bg-foreground/5"
            >
              {playing ? <Pause size={14} /> : <Play size={14} />}
              {playing ? "Pausar" : idx >= lastIdx ? "Rever" : "Continuar"}
            </button>
            <button
              onClick={() => {
                setIdx(0);
                setRevealed(false);
                setPlaying(false);
              }}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm hover:bg-foreground/5"
            >
              <RotateCcw size={14} /> Reiniciar
            </button>
            <div className="inline-flex rounded-lg border border-border p-0.5 text-xs">
              {SPEEDS.map((s) => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={cn(
                    "rounded-md px-2.5 py-1 font-medium transition-colors",
                    speed === s ? "bg-accent/10 text-accent" : "text-muted-ink hover:text-foreground",
                  )}
                >
                  {s}×
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {load.isError && <ErrorNote message={load.error.message} />}
      {load.isPending && <Skeleton className="h-96" />}

      {data && point && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <Card className="col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Probabilidade de vitória — time azul</CardTitle>
                <span className="text-sm text-muted-ink tabular-nums">
                  minuto {point.minute}
                  {idx >= lastIdx ? " · fim" : ""}
                </span>
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline gap-3">
                  <span
                    className={cn(
                      "text-5xl font-semibold tabular-nums tracking-tight transition-colors",
                      winColor(point.blue_win_probability),
                    )}
                  >
                    {pct(point.blue_win_probability)}
                  </span>
                  <span className="text-sm text-secondary-ink">
                    para o azul ({pct(1 - point.blue_win_probability)} vermelho)
                  </span>
                </div>
                <div className="relative mt-3 h-3 overflow-hidden rounded-full bg-chart-red/25">
                  <div
                    className="h-full rounded-full bg-chart-1 transition-[width] duration-500"
                    style={{ width: `${point.blue_win_probability * 100}%` }}
                  />
                  <div className="absolute inset-y-0 left-1/2 w-px bg-foreground/40" />
                </div>
                <div className="mt-4 h-48">
                  <ResponsiveContainer>
                    <LineChart data={shown} margin={{ right: 12 }}>
                      <CartesianGrid vertical={false} {...GRID} />
                      <XAxis
                        dataKey="minute"
                        type="number"
                        domain={[1, lastIdx + 1]}
                        tick={AXIS_TICK}
                        stroke="var(--baseline)"
                        tickFormatter={(v: number) => `${v}'`}
                      />
                      <YAxis domain={[0, 1]} tickFormatter={pct} tick={AXIS_TICK} stroke="var(--baseline)" />
                      <ReferenceLine y={0.5} stroke="var(--muted-ink)" strokeDasharray="4 4" />
                      <Line
                        type="monotone"
                        dataKey="blue_win_probability"
                        stroke="var(--chart-1)"
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Estado aos {point.minute} min (azul − vermelho)</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-2">
                <StateStat label="Ouro" value={point.gold_diff} />
                <StateStat label="XP" value={point.xp_diff} />
                <StateStat label="Abates" value={point.kill_diff} />
                <StateStat label="Torres" value={point.tower_diff} />
                <StateStat label="Dragões" value={point.dragon_diff} />
                <div className="rounded-lg border border-dashed border-border px-3 py-2">
                  <p className="text-xs text-muted-ink">Modelo da fase</p>
                  <p className="mt-0.5 text-lg font-semibold tabular-nums">
                    {point.model_cutoff} min
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {revealed && blueTeam && (
            <Card
              className={cn(
                "border-2",
                modelSaysBlue === blueWon ? "border-chart-1/50" : "border-chart-red/50",
              )}
            >
              <CardContent className="flex items-center justify-between gap-4 pt-4">
                <div>
                  <p className="text-sm font-medium">
                    Resultado real:{" "}
                    <span className={winColor(blueWon)}>
                      vitória do time {blueWon ? "azul" : "vermelho"}
                    </span>
                  </p>
                  <p className="mt-0.5 text-xs text-muted-ink">
                    No último minuto o modelo dava {pct(point.blue_win_probability)} para o azul —{" "}
                    {modelSaysBlue === blueWon
                      ? "apontava o vencedor certo."
                      : "apontava o outro lado (uma reviravolta, ou o modelo errou)."}{" "}
                    Lembre: cada ponto usa só o estado ATÉ aquele minuto, sem ver o futuro.
                  </p>
                </div>
                <Link
                  to={`/partidas/${data.match_id}`}
                  className="shrink-0 text-sm text-gold underline-offset-2 hover:underline"
                >
                  Ver análise completa →
                </Link>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-2 gap-4">
            {[100, 200].map((teamId) => {
              const players = data.participants.filter((p) => p.team_id === teamId);
              const won = teamId === 100 ? blueWon : !blueWon;
              return (
                <Card key={teamId}>
                  <CardHeader>
                    <CardTitle className={teamId === 100 ? "text-chart-1" : "text-chart-red"}>
                      Time {teamId === 100 ? "azul" : "vermelho"}
                      {revealed && (won ? " — venceu" : " — perdeu")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex flex-wrap gap-2">
                    {players.map((p) => (
                      <span
                        key={p.champion}
                        title={`${championDisplayName(p.champion)} (${POSITION_LABELS[p.position] ?? p.position})`}
                        className="flex items-center gap-1.5 rounded-md bg-foreground/5 px-2 py-1 text-xs"
                      >
                        <img src={championIcon(p.champion_id)} alt="" className="size-5 rounded" />
                        {championDisplayName(p.champion)}
                      </span>
                    ))}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      )}

      {!data && !load.isPending && (
        <Card>
          <CardContent className="py-12 text-center text-sm text-secondary-ink">
            Clique em <span className="font-medium">Simular uma partida</span> para sortear uma
            partida coletada e assistir à curva de probabilidade evoluir minuto a minuto.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
