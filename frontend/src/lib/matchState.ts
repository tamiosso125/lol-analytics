/** Fases do jogo e ranges dos sliders de estado da partida — compartilhado
 * entre Predição e Montar partida. */
import type { MatchState } from "@/lib/api";

/* fases do jogo (pesquisa: rotas ~1-14 min, placas caem aos 14;
   mid ~14-25; late 25+) — um modelo treinado por corte */
export const PHASES = [
  { minute: 10, label: "10 min", desc: "Fase de rotas" },
  { minute: 15, label: "15 min", desc: "Fim das rotas" },
  { minute: 20, label: "20 min", desc: "Mid game" },
  { minute: 25, label: "25 min", desc: "Late game" },
] as const;

/* ranges do 1º-99º percentil de data/features_phases.csv, por corte */
export const RANGES: Record<number, Record<string, { min: number; max: number; step: number }>> = {
  10: {
    gold_diff: { min: -5500, max: 5500, step: 100 },
    xp_diff: { min: -4500, max: 4500, step: 100 },
    kill_diff: { min: -11, max: 11, step: 1 },
    tower_diff: { min: -2, max: 2, step: 1 },
    dragon_diff: { min: -1, max: 1, step: 1 },
  },
  15: {
    gold_diff: { min: -10000, max: 10000, step: 100 },
    xp_diff: { min: -9000, max: 9000, step: 100 },
    kill_diff: { min: -15, max: 15, step: 1 },
    tower_diff: { min: -4, max: 4, step: 1 },
    dragon_diff: { min: -2, max: 2, step: 1 },
  },
  20: {
    gold_diff: { min: -13500, max: 13500, step: 100 },
    xp_diff: { min: -12000, max: 12000, step: 100 },
    kill_diff: { min: -20, max: 20, step: 1 },
    tower_diff: { min: -8, max: 8, step: 1 },
    dragon_diff: { min: -3, max: 3, step: 1 },
  },
  25: {
    gold_diff: { min: -15000, max: 15000, step: 100 },
    xp_diff: { min: -16000, max: 16000, step: 100 },
    kill_diff: { min: -24, max: 24, step: 1 },
    tower_diff: { min: -11, max: 11, step: 1 },
    dragon_diff: { min: -4, max: 4, step: 1 },
  },
};

export const SLIDER_LABELS: Record<string, string> = {
  gold_diff: "Diferença de ouro",
  xp_diff: "Diferença de XP (nível)",
  kill_diff: "Diferença de abates",
  tower_diff: "Diferença de torres",
  dragon_diff: "Diferença de dragões",
};
export const SLIDER_KEYS = Object.keys(SLIDER_LABELS) as (keyof Omit<MatchState, "minute">)[];

export const INITIAL_STATE: MatchState = {
  gold_diff: 0,
  xp_diff: 0,
  kill_diff: 0,
  tower_diff: 0,
  dragon_diff: 0,
  minute: 15,
};

export const clamp = (v: number, min: number, max: number) =>
  Math.min(max, Math.max(min, v));

/** Ajusta os diffs de um estado para caberem no range da nova fase. */
export function withMinute(s: MatchState, minute: number): MatchState {
  const r = RANGES[minute];
  const next = { ...s, minute };
  for (const k of SLIDER_KEYS) next[k] = clamp(s[k], r[k].min, r[k].max);
  return next;
}
