import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, ChartTooltip, GRID } from "@/components/chart";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";
import { PHASES } from "@/lib/matchState";
import { cn } from "@/lib/utils";

const FEATURE_LABELS: Record<string, string> = {
  gold_diff: "Diferença de ouro",
  xp_diff: "Diferença de XP",
  kill_diff: "Diferença de abates",
  tower_diff: "Diferença de torres",
  dragon_diff: "Diferença de dragões",
};

/* uma cor da paleta por feature — consistente entre os dois gráficos */
const FEATURE_COLORS: Record<string, string> = {
  gold_diff: "var(--chart-1)",
  xp_diff: "var(--chart-2)",
  kill_diff: "var(--chart-3)",
  tower_diff: "var(--chart-4)",
  dragon_diff: "var(--chart-red)",
};

export function Explain() {
  const [phase, setPhase] = useState("15");
  const importance = useQuery({
    queryKey: ["shap-importance-phases"],
    queryFn: api.shapImportancePhases,
  });

  const data = importance.data?.[phase]
    ? Object.entries(importance.data[phase])
        .map(([key, value]) => ({ feature: FEATURE_LABELS[key] ?? key, value, key }))
        .sort((a, b) => b.value - a.value)
    : [];

  // evolução da importância: uma linha por feature, X = corte de tempo
  const evolution = importance.data
    ? PHASES.map((p) => ({ minute: p.label, ...importance.data[String(p.minute)] }))
    : [];
  const towerRatio =
    importance.data?.["25"]?.tower_diff && importance.data?.["15"]?.tower_diff
      ? importance.data["25"].tower_diff / importance.data["15"].tower_diff
      : null;

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Modelo ML" title="Explicabilidade do modelo">
        Um modelo que só diz "azul vence com 78%" é uma caixa-preta. Os valores SHAP abrem
        essa caixa: eles decompõem cada predição na contribuição exata de cada fator, o que
        torna o modelo auditável (metodologia de Hodge et al., 2021, com explicabilidade via
        SHAP).
      </PageHeader>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle>O que pesa na vitória, por fase do jogo (média |SHAP|)</CardTitle>
            <p className="mt-0.5 text-xs text-muted-ink">
              Quanto maior a barra, mais aquele fator influencia a predição naquela fase.
            </p>
          </div>
          <div className="inline-flex shrink-0 rounded-lg border border-border p-0.5 text-xs">
            {PHASES.map((p) => (
              <button
                key={p.minute}
                onClick={() => setPhase(String(p.minute))}
                title={p.desc}
                className={cn(
                  "rounded-md px-2.5 py-1 font-medium transition-colors",
                  phase === String(p.minute)
                    ? "bg-accent/10 text-accent"
                    : "text-muted-ink hover:text-foreground",
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="h-72">
          {importance.isPending ? (
            <Skeleton className="h-full" />
          ) : importance.isError ? (
            <ErrorNote message={importance.error.message} />
          ) : (
            <ResponsiveContainer>
              <BarChart data={data} layout="vertical" margin={{ left: 40, right: 40 }}>
                <CartesianGrid horizontal={false} {...GRID} />
                <XAxis type="number" tick={AXIS_TICK} stroke="var(--baseline)" tickFormatter={(v: number) => v.toFixed(2)} />
                <YAxis type="category" dataKey="feature" width={140} tick={AXIS_TICK} stroke="var(--baseline)" interval={0} />
                <Tooltip
                  content={<ChartTooltip format={(v) => v.toFixed(3)} />}
                  cursor={{ fill: "var(--grid)", opacity: 0.4 }}
                />
                <Bar
                  dataKey="value"
                  name="média |SHAP|"
                  barSize={16}
                  radius={[0, 4, 4, 0]}
                  label={{ position: "right", formatter: (v: unknown) => Number(v).toFixed(2), fill: "var(--muted-ink)", fontSize: 11 }}
                >
                  {data.map((d) => (
                    <Cell key={d.key} fill={FEATURE_COLORS[d.key] ?? "var(--chart-1)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
        <CardContent className="border-t border-border pt-3">
          <p className="text-xs leading-relaxed text-secondary-ink">
            <span className="font-medium text-foreground">Como ler: </span>
            o ouro domina em todas as fases e cresce de importância conforme o jogo avança. As
            torres são quase irrelevantes aos 10-15 min — as placas só caem aos 14, então
            pouquíssimas torres foram destruídas — mas ganham peso no late game (veja a
            evolução no gráfico abaixo). Já os abates perdem importância no late: eles
            importam pelo ouro/XP que geram, e esses já estão capturados nas outras variáveis.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Como a importância de cada fator evolui ao longo do jogo</CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            A mesma importância (média |SHAP|), agora com as quatro fases lado a lado — uma
            linha por fator.
          </p>
        </CardHeader>
        <CardContent className="h-72">
          {importance.isPending ? (
            <Skeleton className="h-full" />
          ) : importance.isError ? (
            <ErrorNote message={importance.error.message} />
          ) : (
            <ResponsiveContainer>
              <LineChart data={evolution} margin={{ right: 24, top: 8 }}>
                <CartesianGrid vertical={false} {...GRID} />
                <XAxis dataKey="minute" tick={AXIS_TICK} stroke="var(--baseline)" />
                <YAxis
                  tick={AXIS_TICK}
                  stroke="var(--baseline)"
                  tickFormatter={(v: number) => v.toFixed(1)}
                />
                <Tooltip
                  content={<ChartTooltip format={(v) => v.toFixed(3)} />}
                  cursor={{ stroke: "var(--grid)" }}
                />
                <Legend
                  wrapperStyle={{ fontSize: 12 }}
                  formatter={(value: string) => (
                    <span style={{ color: "var(--secondary-ink)" }}>
                      {FEATURE_LABELS[value] ?? value}
                    </span>
                  )}
                />
                {Object.keys(FEATURE_LABELS).map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    name={key}
                    stroke={FEATURE_COLORS[key]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
        <CardContent className="border-t border-border pt-3">
          <p className="text-xs leading-relaxed text-secondary-ink">
            <span className="font-medium text-gold">Leitura: </span>
            este é o achado central do modelo por fases: o ouro cresce e domina sempre, mas
            as torres saem de quase zero aos 15 minutos para{" "}
            {towerRatio ? `${Math.round(towerRatio)}× mais importância` : "dezenas de vezes mais importância"}{" "}
            aos 25 — as placas caem aos 14, então antes disso quase não há torre destruída
            para o modelo usar. Os abates fazem o caminho inverso: no late game o que eles
            geram (ouro e XP) já está contado nas outras linhas. Um único modelo de "15
            minutos" esconderia tudo isso.
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Distribuição dos valores SHAP (beeswarm, corte de 15 min)</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={api.reportImage("shap_beeswarm.png")}
              alt="Gráfico beeswarm dos valores SHAP por feature"
              className="w-full rounded-lg bg-white"
            />
            <p className="mt-2 text-xs leading-relaxed text-secondary-ink">
              <span className="font-medium text-foreground">Como ler: </span>
              cada ponto é uma partida real. A posição horizontal diz o quanto aquela feature
              empurrou a predição (direita = a favor do azul); a cor diz se o valor da feature
              era alto (vermelho) ou baixo (azul). No gold_diff, pontos vermelhos (muito ouro à
              frente) à direita = liderar em ouro empurra fortemente para a vitória.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Curva de calibração dos modelos</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={api.reportImage("calibration_curve.png")}
              alt="Curva de calibração comparando RandomForest, XGBoost e MLP"
              className="w-full rounded-lg bg-white"
            />
            <p className="mt-2 text-xs leading-relaxed text-secondary-ink">
              <span className="font-medium text-foreground">Como ler: </span>
              calibração responde "quando o modelo diz 70%, ele acerta 70% das vezes?". Quanto
              mais próxima da diagonal, mais as probabilidades podem ser lidas literalmente —
              essencial para usar o modelo como medida de chance real, não só como
              classificador.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
