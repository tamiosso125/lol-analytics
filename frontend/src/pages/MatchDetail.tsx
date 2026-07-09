import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, Castle, Eye, FlaskConical, Flame, Pause, Play, RotateCcw, Shield, Shuffle, Skull } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type ComponentType } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, ChartTooltip, GRID } from "@/components/chart";
import { CoachCard } from "@/components/CoachCard";
import { DraftAnalysisCard } from "@/components/DraftAnalysisCard";
import { MapHeatmap } from "@/components/MapHeatmap";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import {
  api,
  type CoachLane,
  type CoachSynergyItem,
  type FramePlayer,
  type MatchParticipantFull,
  type MatchState,
  type MatchTeam,
  type ProbPoint,
  type WardEvent,
} from "@/lib/api";
import { championDisplayName, championIcon, itemIcon, POSITION_LABELS } from "@/lib/ddragon";
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

const SPEEDS = [1, 2, 4] as const;
const TICK_MS = 1000; // 1 minuto de jogo por segundo real (× velocidade)

/** Curva de probabilidade — modo estático (linha completa, como sempre
 * foi) ou "replay" (a mesma curva, mas animada minuto a minuto como se
 * a partida estivesse ao vivo; era a página /aovivo, fundida aqui
 * porque é o mesmo dado, só que a busca começa de uma partida aleatória
 * em vez de uma escolhida — ver docs/diario_execucao.md 2026-07-06). */
function ProbabilityCard({
  curve,
  blueWon,
  autoplay,
  onShuffle,
  shuffling,
  onMinuteChange,
}: {
  curve: ProbPoint[];
  blueWon: boolean;
  autoplay: boolean;
  onShuffle: () => void;
  shuffling: boolean;
  /** durante o replay, propaga o minuto atual pro resto da página (mapa
   * de calor, itens, objetivos) — "assistir partida" vira estilo
   * broadcast: tudo evolui junto, não só a linha de probabilidade */
  onMinuteChange?: (minute: number) => void;
}) {
  const lastIdx = curve.length - 1;
  const [replaying, setReplaying] = useState(autoplay);
  const [idx, setIdx] = useState(autoplay ? 0 : lastIdx);
  const [playing, setPlaying] = useState(autoplay);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [revealed, setRevealed] = useState(!autoplay);

  const timer = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  useEffect(() => {
    clearInterval(timer.current);
    if (!playing) return;
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
  }, [playing, speed, lastIdx]);

  const point = curve[Math.min(idx, lastIdx)];
  const shown = replaying ? curve.slice(0, idx + 1) : curve;
  const modelSaysBlue = point.blue_win_probability >= 0.5;
  const domain: [number, number] = [curve[0].minute, curve[lastIdx].minute];

  // durante o replay, o mapa de calor/itens/objetivos acompanham o
  // mesmo minuto — sem isso o replay era só uma linha isolada
  useEffect(() => {
    if (replaying) onMinuteChange?.(point.minute);
  }, [replaying, point.minute, onMinuteChange]);

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
        <div>
          <CardTitle>Probabilidade de vitória do time azul, minuto a minuto</CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            {replaying
              ? "Reproduzindo minuto a minuto — mapa de calor, itens e objetivos abaixo acompanham o replay."
              : "Cada ponto usa o modelo da fase correspondente (10/15/20/25 min) sobre o estado real da partida naquele minuto."}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {replaying && (
            <>
              <button
                onClick={onShuffle}
                disabled={shuffling}
                className="inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs hover:bg-foreground/5 disabled:opacity-50"
              >
                <Shuffle size={13} /> {shuffling ? "Sorteando…" : "Outra partida"}
              </button>
              <button
                onClick={() => {
                  if (idx >= lastIdx) setIdx(0);
                  setRevealed(false);
                  setPlaying((p) => !p);
                }}
                className="inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs hover:bg-foreground/5"
              >
                {playing ? <Pause size={13} /> : <Play size={13} />}
                {playing ? "Pausar" : idx >= lastIdx ? "Rever" : "Continuar"}
              </button>
              <button
                onClick={() => {
                  setIdx(0);
                  setRevealed(false);
                  setPlaying(true);
                }}
                className="inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs hover:bg-foreground/5"
              >
                <RotateCcw size={13} /> Reiniciar
              </button>
              <div className="inline-flex rounded-lg border border-border p-0.5 text-xs">
                {SPEEDS.map((s) => (
                  <button
                    key={s}
                    onClick={() => setSpeed(s)}
                    className={cn(
                      "rounded-md px-2 py-1 font-medium transition-colors",
                      speed === s ? "bg-accent/10 text-accent" : "text-muted-ink hover:text-foreground",
                    )}
                  >
                    {s}×
                  </button>
                ))}
              </div>
            </>
          )}
          <button
            onClick={() => {
              setReplaying((r) => !r);
              if (!replaying) {
                setIdx(0);
                setPlaying(true);
                setRevealed(false);
              } else {
                setIdx(lastIdx);
                setPlaying(false);
                setRevealed(true);
              }
            }}
            className="rounded-lg bg-accent/10 px-2.5 py-1.5 text-xs font-medium text-accent hover:bg-accent/20"
          >
            {replaying ? "Ver análise completa" : "▶ Assistir como replay"}
          </button>
        </div>
      </CardHeader>
      <CardContent className="h-80">
        {curve.length === 0 ? (
          <p className="text-sm text-muted-ink">Sem timeline disponível para esta partida.</p>
        ) : (
          <>
            {replaying && (
              <div className="mb-2 flex items-baseline gap-3">
                <span
                  className={cn(
                    "text-3xl font-semibold tabular-nums tracking-tight transition-colors",
                    winColor(point.blue_win_probability),
                  )}
                >
                  {pct(point.blue_win_probability)}
                </span>
                <span className="text-xs text-muted-ink tabular-nums">
                  minuto {point.minute}
                  {idx >= lastIdx ? " · fim" : ""}
                </span>
              </div>
            )}
            <ResponsiveContainer width="100%" height={replaying ? "85%" : "100%"}>
              <LineChart data={shown} margin={{ right: 16 }}>
                <CartesianGrid vertical={false} {...GRID} />
                <XAxis
                  dataKey="minute"
                  type="number"
                  domain={domain}
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
                  isAnimationActive={!replaying}
                />
              </LineChart>
            </ResponsiveContainer>
          </>
        )}
      </CardContent>
      {replaying && revealed && curve.length > 0 && (
        <CardContent className="border-t border-border pt-3">
          <p className="text-sm font-medium">
            Resultado real:{" "}
            <span className={winColor(blueWon)}>vitória do time {blueWon ? "azul" : "vermelho"}</span>
          </p>
          <p className="mt-0.5 text-xs text-muted-ink">
            No último minuto o modelo dava {pct(point.blue_win_probability)} para o azul —{" "}
            {modelSaysBlue === blueWon
              ? "apontava o vencedor certo."
              : "apontava o outro lado (uma reviravolta, ou o modelo errou)."}{" "}
            Lembre: cada ponto usa só o estado ATÉ aquele minuto, sem ver o futuro.
          </p>
        </CardContent>
      )}
    </Card>
  );
}

/** Modo "e se": pega o estado REAL da partida no minuto escolhido (da
 * própria curva de probabilidade) e deixa editá-lo — o delta entre a
 * probabilidade real e a editada responde perguntas contrafactuais de
 * estado ("e se aos 14 min o time azul tivesse +1k de ouro?"). É uma
 * intervenção sobre o ESTADO agregado, não sobre uma ação específica —
 * a distinção fica no texto do card. */
function WhatIfCard({
  curve,
  minute,
  matchId,
  blueChampions,
  redChampions,
  lanes,
  blueSynergies,
  redSynergies,
}: {
  curve: ProbPoint[];
  minute: number;
  matchId: string;
  blueChampions: Record<string, string>;
  redChampions: Record<string, string>;
  /** matchups/sinergias reais da partida (via /compose) — opcionais,
   * chegam depois do estado/campeões porque exigem uma chamada à parte */
  lanes?: CoachLane[];
  blueSynergies?: CoachSynergyItem[];
  redSynergies?: CoachSynergyItem[];
}) {
  const point = useMemo(
    () => curve.find((p) => p.minute === minute) ?? curve[curve.length - 1],
    [curve, minute],
  );
  const [seededFor, setSeededFor] = useState<ProbPoint | undefined>(undefined);
  const [state, setState] = useState<MatchState | null>(null);

  // re-semeia o editor sempre que o minuto (slider compartilhado) muda —
  // ajuste durante o render, não em efeito (evita um passo de render
  // extra): https://react.dev/learn/you-might-not-need-an-effect
  if (point && point !== seededFor) {
    setSeededFor(point);
    setState({
      gold_diff: point.gold_diff,
      xp_diff: point.xp_diff,
      kill_diff: point.kill_diff,
      tower_diff: point.tower_diff,
      dragon_diff: point.dragon_diff,
      minute: point.model_cutoff,
    });
  }

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
    <>
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
    {predict.data && (
      <CoachCard
        state={state}
        prediction={predict.data}
        context={{
          blueChampions,
          redChampions,
          matchId,
          gameMinute: point.minute,
          lanes,
          blueSynergies,
          redSynergies,
        }}
      />
    )}
    </>
  );
}

/** Controle de visão ao longo do jogo: diferença acumulada (azul −
 * vermelho) de wards colocadas e destruídas, minuto a minuto — mesma
 * convenção "_diff" dos outros gráficos (ouro, abates). Ao contrário do
 * mapa de calor, aqui não há aproximação nenhuma: é só contagem de
 * evento por time, a Riot não precisa da posição da ward pra isso. */
function VisionCard({ wards, maxMinute }: { wards: WardEvent[]; maxMinute: number }) {
  const series = useMemo(() => {
    const out: { minute: number; ward_diff: number; ward_kill_diff: number }[] = [];
    let placedDiff = 0;
    let destroyedDiff = 0;
    for (let m = 0; m <= maxMinute; m++) {
      for (const w of wards) {
        if (w.minute !== m) continue;
        const sign = w.team_id === 100 ? 1 : -1;
        if (w.kind === "placed") placedDiff += sign;
        else destroyedDiff += sign;
      }
      out.push({ minute: m, ward_diff: placedDiff, ward_kill_diff: destroyedDiff });
    }
    return out;
  }, [wards, maxMinute]);

  if (wards.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Controle de visão (azul − vermelho, acumulado)</CardTitle>
        <p className="mt-0.5 text-xs text-muted-ink">
          Wards colocadas e wards inimigas destruídas por time, ao longo do jogo — só
          contagem de evento (sem aproximação de posição, diferente do mapa de calor).
        </p>
      </CardHeader>
      <CardContent className="h-56">
        <ResponsiveContainer>
          <LineChart data={series} margin={{ right: 16 }}>
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
            <Legend
              wrapperStyle={{ fontSize: 12 }}
              formatter={(value: string) => <span style={{ color: "var(--secondary-ink)" }}>{value}</span>}
            />
            {/* cores neutras (chart-2/chart-4), não chart-1/chart-red — as
                duas linhas JÁ são diffs azul-menos-vermelho; usar as cores
                de time aqui sugeriria (errado) "linha do time azul" */}
            <Line
              type="monotone"
              dataKey="ward_diff"
              name="Wards colocadas (azul − vermelho)"
              stroke="var(--chart-2)"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="ward_kill_diff"
              name="Wards destruídas (azul − vermelho)"
              stroke="var(--chart-4)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function TeamTable({
  players,
  label,
  won,
  statsAtMinute,
  minute,
}: {
  players: MatchParticipantFull[];
  label: string;
  won: boolean;
  /** champion_id -> estado NO `minute` (itens/ouro/CS/dano/KDA — tudo
   * reconstruído daquele momento). null = ainda carregando /positions;
   * cai pros totais finais do /analysis nesse meio-tempo. */
  statsAtMinute: Record<number, FramePlayer> | null;
  minute: number;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className={winColor(won)}>
            {label} — {won ? "Vitória" : "Derrota"}
          </CardTitle>
          {statsAtMinute !== null && (
            <p className="mt-0.5 text-xs text-muted-ink">
              KDA/Ouro/CS/Dano/Itens mostram o estado aos {minute} min (siga o slider do
              mapa de calor), não o final da partida. Visão é sempre o total final — a
              Riot não grava esse número por minuto.
            </p>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-secondary-ink">
              <th className="px-2 py-2 font-medium first:pl-0">Campeão</th>
              <th className="px-2 py-2 font-medium">KDA</th>
              <th className="px-2 py-2 font-medium">Ouro</th>
              <th className="px-2 py-2 font-medium">CS</th>
              <th className="px-2 py-2 font-medium">Dano</th>
              <th className="px-2 py-2 font-medium" title="Sempre o total final da partida">
                Visão
              </th>
              <th className="px-2 py-2 font-medium">Itens</th>
            </tr>
          </thead>
          <tbody className="tabular-nums">
            {players.map((p) => {
              // enquanto /positions ainda carrega, mostra os totais finais
              // (itens com trinket); depois disso, estado NO minuto do
              // slider — reconstruído da timeline, itens não têm trinket
              const showFinal = statsAtMinute === null;
              const snap = showFinal ? null : statsAtMinute[p.champion_id];
              const displayItems = snap ? snap.items.slice(0, 6) : p.items.slice(0, 6);
              const kda = snap ? `${snap.kills}/${snap.deaths}/${snap.assists}` : `${p.kills}/${p.deaths}/${p.assists}`;
              const gold = snap ? snap.gold : p.gold;
              const cs = snap ? snap.cs : p.cs;
              const dmg = snap ? snap.dmg : p.dmg;
              return (
                <tr key={p.champion} className="border-b border-border/50 last:border-0">
                  <td className="px-2 py-1.5 first:pl-0">
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
                  <td className="px-2 py-1.5">{kda}</td>
                  <td className="px-2 py-1.5">{gold.toLocaleString("pt-BR")}</td>
                  <td className="px-2 py-1.5">{cs}</td>
                  <td className="px-2 py-1.5">{dmg.toLocaleString("pt-BR")}</td>
                  <td className="px-2 py-1.5">{p.vision}</td>
                  <td className="px-2 py-1.5">
                    <div className="flex gap-0.5">
                      {Array.from({ length: 6 }).map((_, i) => {
                        const itemId = displayItems[i];
                        return itemId ? (
                          <img
                            key={i}
                            src={itemIcon(itemId)}
                            alt=""
                            className="size-6 rounded border border-border/50"
                          />
                        ) : (
                          <div key={i} className="size-6 rounded border border-dashed border-border/50" />
                        );
                      })}
                      {showFinal && (
                        <div className="ml-1 border-l border-border pl-1">
                          {p.items[6] ? (
                            <img
                              src={itemIcon(p.items[6])}
                              alt=""
                              title="Trinket"
                              className="size-6 rounded-full border border-gold/50"
                            />
                          ) : (
                            <div className="size-6 rounded-full border border-dashed border-border/50" />
                          )}
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        </div>
      </CardContent>
    </Card>
  );
}

export function MatchDetail() {
  const { id = "" } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [minute, setMinute] = useState(14);
  const analysis = useQuery({
    queryKey: ["match-analysis", id],
    queryFn: () => api.matchAnalysis(id),
  });
  const positions = useQuery({
    queryKey: ["match-positions", id],
    queryFn: () => api.matchPositions(id),
  });
  const shuffle = useMutation({
    mutationFn: api.randomMatch,
    onSuccess: ({ match_id }) => navigate(`/partidas/${match_id}?replay=1`, { replace: true }),
  });
  // campeões da partida real por posição — calculado antes do
  // early-return (hooks não podem vir depois de um return condicional)
  // pra poder alimentar o useQuery do /compose logo abaixo
  const blueChampions = Object.fromEntries(
    (analysis.data?.participants.filter((p) => p.team_id === 100) ?? []).map((p) => [
      p.position,
      p.champion,
    ]),
  );
  const redChampions = Object.fromEntries(
    (analysis.data?.participants.filter((p) => p.team_id === 200) ?? []).map((p) => [
      p.position,
      p.champion,
    ]),
  );
  // idem, mas puuid — dá pro /compose ajustar a leitura pelo win rate do
  // JOGADOR naquele campeão (não só o campeão em abstrato); ver
  // docs/diario_execucao.md 2026-07-08 (feedback: "deveríamos saber quem
  // é o jogador... a análise do draft deveria fazer isso")
  const bluePlayers = Object.fromEntries(
    (analysis.data?.participants.filter((p) => p.team_id === 100) ?? []).map((p) => [
      p.position,
      p.puuid,
    ]),
  );
  const redPlayers = Object.fromEntries(
    (analysis.data?.participants.filter((p) => p.team_id === 200) ?? []).map((p) => [
      p.position,
      p.puuid,
    ]),
  );
  // matchups/sinergias REAIS da partida (mesmos dados do /compose usado
  // no Simulador) — fecha o gap do WhatIfCard/DraftAnalysisCard só
  // citarem campeão sem número de matchup
  const compose = useQuery({
    queryKey: ["match-compose", id],
    queryFn: () => api.compose(blueChampions, redChampions, undefined, bluePlayers, redPlayers),
    enabled: !!analysis.data,
  });

  if (analysis.isPending) return <Skeleton className="h-96" />;
  if (analysis.isError) return <ErrorNote message={analysis.error.message} />;
  const m = analysis.data;
  const blue = m.participants.filter((p) => p.team_id === 100);
  const red = m.participants.filter((p) => p.team_id === 200);
  const blueTeam = m.teams.find((t) => t.team_id === 100);
  const redTeam = m.teams.find((t) => t.team_id === 200);

  // itens/ouro/CS/dano/KDA que cada campeão já tinha NO MINUTO do
  // slider (não os totais finais) — champion_id é chave segura, LoL
  // não permite campeão repetido na mesma partida (nem entre times)
  const posFrames = positions.data?.frames;
  const statsAtMinute: Record<number, FramePlayer> | null = posFrames
    ? Object.fromEntries(
        (posFrames[Math.min(minute, posFrames.length - 1)]?.players ?? []).map((fp) => [
          fp.champion_id,
          fp,
        ]),
      )
    : null;

  return (
    <div className="space-y-5">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm text-secondary-ink hover:text-foreground"
      >
        <ArrowLeft size={14} /> Início
      </Link>

      <PageHeader eyebrow="Análise" title="Análise da partida">
        <span className="tabular-nums">
          {new Date(m.date).toLocaleString("pt-BR")} · {m.duration_min} min · patch {m.patch} ·{" "}
          <span className={winColor(!!blueTeam?.win)}>
            {blueTeam?.win ? "vitória do time azul" : "vitória do time vermelho"}
          </span>
        </span>
      </PageHeader>

      <DraftAnalysisCard
        blueChampions={blueChampions}
        redChampions={redChampions}
        lanes={compose.data?.lanes}
        blueSynergies={compose.data?.synergies.blue}
        redSynergies={compose.data?.synergies.red}
      />

      <ProbabilityCard
        curve={m.prob_curve}
        blueWon={blueTeam?.win ?? false}
        autoplay={searchParams.get("replay") === "1" && m.prob_curve.length > 1}
        onShuffle={() => shuffle.mutate()}
        shuffling={shuffle.isPending}
        onMinuteChange={setMinute}
      />

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

      {m.prob_curve.length > 0 && (
        <WhatIfCard
          curve={m.prob_curve}
          minute={minute}
          matchId={id}
          blueChampions={blueChampions}
          redChampions={redChampions}
          lanes={compose.data?.lanes}
          blueSynergies={compose.data?.synergies.blue}
          redSynergies={compose.data?.synergies.red}
        />
      )}

      {positions.data && positions.data.wards.length > 0 && (
        <VisionCard wards={positions.data.wards} maxMinute={positions.data.frames.length - 1} />
      )}

      <div className="grid grid-cols-2 gap-4">
        <TeamTable
          players={blue}
          label="Time azul"
          won={blueTeam?.win ?? false}
          statsAtMinute={statsAtMinute}
          minute={Math.min(minute, posFrames ? posFrames.length - 1 : minute)}
        />
        <TeamTable
          players={red}
          label="Time vermelho"
          won={!(blueTeam?.win ?? false)}
          statsAtMinute={statsAtMinute}
          minute={Math.min(minute, posFrames ? posFrames.length - 1 : minute)}
        />
      </div>
    </div>
  );
}
