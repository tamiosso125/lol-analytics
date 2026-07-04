import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, ChartTooltip, GRID } from "@/components/chart";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader } from "@/components/ui";
import { api, type MatchState } from "@/lib/api";
import {
  INITIAL_STATE as INITIAL,
  PHASES,
  RANGES,
  SLIDER_KEYS,
  SLIDER_LABELS,
  withMinute,
} from "@/lib/matchState";
import { cn } from "@/lib/utils";

export function Predict() {
  const [state, setState] = useState<MatchState>(INITIAL);
  const predict = useMutation({ mutationFn: api.predict });
  const { mutate } = predict;

  // predição automática com debounce enquanto o usuário arrasta os sliders
  useEffect(() => {
    const t = setTimeout(() => mutate(state), 300);
    return () => clearTimeout(t);
  }, [state, mutate]);

  // mantém os valores ao trocar de fase, mas dentro do range da nova
  const setMinute = (minute: number) => setState((s) => withMinute(s, minute));

  const prob = predict.data?.blue_win_probability;
  const shapData = predict.data
    ? Object.entries(predict.data.shap_contributions)
        .map(([key, value]) => ({ feature: SLIDER_LABELS[key] ?? key, value }))
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    : [];
  const ranges = RANGES[state.minute];

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Modelo ML" title="Predição de vitória">
        Escolha a fase do jogo e o estado da partida (time azul − time vermelho). Cada fase
        usa um modelo treinado naquele corte de tempo — repare como a importância de cada
        fator muda: torres quase não pesam aos 10-15 min (as placas só caem aos 14), mas
        passam a pesar no late game.
      </PageHeader>

      <div className="inline-flex rounded-lg border border-border p-0.5">
        {PHASES.map((p) => (
          <button
            key={p.minute}
            onClick={() => setMinute(p.minute)}
            className={cn(
              "rounded-md px-4 py-2 text-left transition-colors",
              state.minute === p.minute
                ? "bg-accent/10 text-accent"
                : "text-muted-ink hover:text-foreground",
            )}
          >
            <span className="block text-sm font-medium">{p.label}</span>
            <span className="block text-xs opacity-80">{p.desc}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Estado aos {state.minute} minutos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5 pt-2">
            {SLIDER_KEYS.map((key) => (
              <div key={key}>
                <div className="mb-1 flex justify-between text-sm">
                  <label htmlFor={key} className="text-secondary-ink">
                    {SLIDER_LABELS[key]}
                  </label>
                  <span className="font-medium tabular-nums">
                    {state[key] > 0
                      ? `+${state[key].toLocaleString("pt-BR")}`
                      : state[key].toLocaleString("pt-BR")}
                  </span>
                </div>
                <input
                  id={key}
                  type="range"
                  min={ranges[key].min}
                  max={ranges[key].max}
                  step={ranges[key].step}
                  value={state[key]}
                  onChange={(e) => setState((s) => ({ ...s, [key]: Number(e.target.value) }))}
                  className="w-full accent-accent"
                />
              </div>
            ))}
            <button
              onClick={() => setState((s) => ({ ...INITIAL, minute: s.minute }))}
              className="text-xs text-muted-ink underline-offset-2 hover:underline"
            >
              Zerar (jogo empatado)
            </button>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>
                Probabilidade de vitória do time azul (aos {state.minute} min)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predict.isError ? (
                <ErrorNote message={predict.error.message} />
              ) : (
                <>
                  <span className="text-5xl font-semibold tabular-nums tracking-tight">
                    {prob != null ? `${(prob * 100).toFixed(1)}%` : "…"}
                  </span>
                  <div
                    className="relative mt-4 h-3 overflow-hidden rounded-full bg-chart-red/25"
                    role="meter"
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-valuenow={prob != null ? Math.round(prob * 100) : undefined}
                    aria-label="Probabilidade de vitória do time azul"
                  >
                    <div
                      className="h-full rounded-full bg-chart-1 transition-[width] duration-300"
                      style={{ width: `${(prob ?? 0.5) * 100}%` }}
                    />
                    <div className="absolute inset-y-0 left-1/2 w-px bg-foreground/40" />
                  </div>
                  <div className="mt-1 flex justify-between text-xs text-muted-ink">
                    <span>Vermelho vence</span>
                    <span>50%</span>
                    <span>Azul vence</span>
                  </div>
                  <p className="mt-3 border-t border-border pt-2 text-xs leading-relaxed text-muted-ink">
                    Com tudo zerado a probabilidade não é 50%: zerar significa "empate em
                    ouro/XP/objetivos", e o modelo aprendeu dos dados que, mesmo empatado, o
                    lado vermelho é estruturalmente favorecido neste elo (counter-pick
                    garantido e acesso ao dragão) — viés que não aparece em nenhum dos 5
                    fatores e por isso vive na taxa-base.
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contribuição de cada fator nesta predição (SHAP)</CardTitle>
            </CardHeader>
            <CardContent className="h-64">
              <ResponsiveContainer>
                <BarChart data={shapData} layout="vertical" margin={{ left: 40, right: 16 }}>
                  <CartesianGrid horizontal={false} {...GRID} />
                  <XAxis type="number" tick={AXIS_TICK} stroke="var(--baseline)" tickFormatter={(v: number) => v.toFixed(1)} />
                  <YAxis type="category" dataKey="feature" width={130} tick={AXIS_TICK} stroke="var(--baseline)" />
                  <ReferenceLine x={0} stroke="var(--baseline)" />
                  <Tooltip
                    content={<ChartTooltip format={(v) => v.toFixed(3)} />}
                    cursor={{ fill: "var(--grid)", opacity: 0.4 }}
                  />
                  <Bar dataKey="value" name="Contribuição" barSize={14} radius={4}>
                    {shapData.map((d) => (
                      <Cell key={d.feature} fill={d.value >= 0 ? "var(--chart-1)" : "var(--chart-red)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <p className="mt-1 text-xs text-muted-ink">
                Azul empurra para vitória do time azul; vermelho, contra. Troque a fase para
                ver a importância de cada fator mudar.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
