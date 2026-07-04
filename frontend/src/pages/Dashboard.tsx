import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AXIS_TICK, ChartTooltip, GRID } from "@/components/chart";
import { Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

function SectionTitle({ eyebrow, title, desc }: { eyebrow: string; title: string; desc?: string }) {
  return (
    <div className="pt-2">
      <p className="hextech-title text-[11px] font-medium text-gold">{eyebrow}</p>
      <h2 className="mt-0.5 text-lg font-semibold tracking-tight">{title}</h2>
      {desc && <p className="mt-0.5 text-sm text-secondary-ink">{desc}</p>}
    </div>
  );
}

/** Uma frase de conclusão sob o gráfico — o que o leitor deve levar dele. */
function Takeaway({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-2 border-t border-border pt-2 text-xs leading-relaxed text-secondary-ink">
      <span className="font-medium text-gold">Leitura: </span>
      {children}
    </p>
  );
}

function KpiCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <span className="text-3xl font-semibold tabular-nums tracking-tight">{value}</span>
        {hint && <p className="mt-1 text-xs text-muted-ink">{hint}</p>}
      </CardContent>
    </Card>
  );
}

export function Dashboard() {
  const overview = useQuery({ queryKey: ["overview"], queryFn: api.overview });
  const gold15 = useQuery({ queryKey: ["gold15"], queryFn: api.gold15 });
  const durations = useQuery({ queryKey: ["durations"], queryFn: api.durations });
  const objectives = useQuery({ queryKey: ["objectives"], queryFn: api.objectives });
  const patches = useQuery({ queryKey: ["patches"], queryFn: api.patches });

  const objData = objectives.data
    ? (["dragons", "barons", "towers", "heralds"] as const).map((k) => ({
        objetivo: { dragons: "Dragões", barons: "Barões", towers: "Torres", heralds: "Arautos" }[k],
        vitoria: objectives.data.find((o) => o.win)?.[k] ?? 0,
        derrota: objectives.data.find((o) => !o.win)?.[k] ?? 0,
      }))
    : [];
  const o = overview.data;

  // números para as "leituras" — calculados dos próprios dados exibidos
  const topGold = gold15.data?.at(-1);
  const bottomGold = gold15.data?.[0];
  const dragonsWin = objectives.data?.find((x) => x.win)?.dragons;
  const dragonsLose = objectives.data?.find((x) => !x.win)?.dragons;
  const modalDuration = durations.data?.reduce(
    (a, b) => (b.matches > (a?.matches ?? 0) ? b : a),
    durations.data[0],
  );
  const topPatch = patches.data?.reduce(
    (a, b) => (b.matches > (a?.matches ?? 0) ? b : a),
    patches.data[0],
  );
  const totalPatchGames = patches.data?.reduce((s, p) => s + p.matches, 0) ?? 0;

  return (
    <div className="space-y-5">
      <PageHeader eyebrow="Visão analítica" title="Dashboard">
        Três perguntas, em ordem: o que decide partidas neste elo, como é o meta dessas
        partidas, e de onde vêm os dados. Cada gráfico traz a leitura direta logo abaixo.
      </PageHeader>

      {/* ---------------- o que decide partidas ---------------- */}
      <SectionTitle
        eyebrow="Seção 1"
        title="O que decide partidas"
        desc="Os fatores que separam vitória de derrota — a base do modelo de predição."
      />

      <Card>
        <CardHeader>
          <CardTitle>Vantagem de ouro aos 15 minutos × chance de vitória</CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            Cada barra é uma faixa de diferença de ouro (azul − vermelho) aos 15 min. Barras
            azuis: azul na frente; vermelhas: vermelho na frente.
          </p>
        </CardHeader>
        <CardContent className="h-72">
          {gold15.isPending ? (
            <Skeleton className="h-full" />
          ) : gold15.isError ? (
            <ErrorNote message={gold15.error.message} />
          ) : (
            <ResponsiveContainer>
              <BarChart data={gold15.data} barGap={2}>
                <CartesianGrid vertical={false} {...GRID} />
                <XAxis dataKey="label" tick={AXIS_TICK} stroke="var(--baseline)" />
                <YAxis
                  tickFormatter={pct}
                  domain={[0, 1]}
                  tick={AXIS_TICK}
                  stroke="var(--baseline)"
                />
                <ReferenceLine y={0.5} stroke="var(--muted-ink)" strokeDasharray="4 4" />
                <Tooltip
                  content={
                    <ChartTooltip
                      format={(v, name) => (name === "Partidas" ? String(v) : pct(v))}
                    />
                  }
                  cursor={{ fill: "var(--grid)", opacity: 0.4 }}
                />
                <Bar dataKey="blue_win_rate" name="Win rate azul" barSize={40} radius={[4, 4, 0, 0]}>
                  {gold15.data.map((b) => (
                    <Cell
                      key={b.gold_diff_mid}
                      fill={b.gold_diff_mid >= 0 ? "var(--chart-1)" : "var(--chart-red)"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
        {topGold && bottomGold && (
          <CardContent className="pt-0">
            <Takeaway>
              o ouro aos 15 minutos praticamente decide a partida nas pontas: com{" "}
              {topGold.label} o azul vence {pct(topGold.blue_win_rate)}; com {bottomGold.label}
              , só {pct(bottomGold.blue_win_rate)}. Perto do empate (−2k a +2k) a partida
              segue aberta — é aí que o resto (composição, objetivos, lado) desempata.
            </Takeaway>
          </CardContent>
        )}
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Objetivos por resultado (média por partida)</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            {objectives.isPending ? (
              <Skeleton className="h-full" />
            ) : objectives.isError ? (
              <ErrorNote message={objectives.error.message} />
            ) : (
              <ResponsiveContainer>
                <BarChart data={objData} barGap={2}>
                  <CartesianGrid vertical={false} {...GRID} />
                  <XAxis dataKey="objetivo" tick={AXIS_TICK} stroke="var(--baseline)" />
                  <YAxis tick={AXIS_TICK} stroke="var(--baseline)" />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--grid)", opacity: 0.4 }} />
                  <Legend
                    wrapperStyle={{ fontSize: 12 }}
                    formatter={(value: string) => (
                      <span style={{ color: "var(--secondary-ink)" }}>{value}</span>
                    )}
                  />
                  <Bar dataKey="vitoria" name="Vitória" fill="var(--chart-1)" barSize={22} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="derrota" name="Derrota" fill="var(--chart-red)" barSize={22} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
          {dragonsWin != null && dragonsLose != null && (
            <CardContent className="pt-0">
              <Takeaway>
                times vencedores fazem {(dragonsWin / Math.max(0.1, dragonsLose)).toFixed(1)}×
                mais dragões que os derrotados — objetivos neutros são o termômetro de
                controle de mapa, não só o ouro que dão.
              </Takeaway>
            </CardContent>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>O lado do mapa</CardTitle>
          </CardHeader>
          <CardContent>
            {overview.isPending ? (
              <Skeleton className="h-40" />
            ) : o ? (
              <>
                <div className="space-y-3 pt-2">
                  {[
                    { label: "Lado azul", value: o.blue_win_rate, color: "var(--chart-1)" },
                    { label: "Lado vermelho", value: 1 - o.blue_win_rate, color: "var(--chart-red)" },
                  ].map((s) => (
                    <div key={s.label} className="flex items-center gap-3 text-sm">
                      <span className="w-28 shrink-0 text-secondary-ink">{s.label}</span>
                      <div className="h-4 flex-1 overflow-hidden rounded-full bg-foreground/10">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${s.value * 100}%`, background: s.color }}
                        />
                      </div>
                      <span className="w-14 text-right font-semibold tabular-nums">
                        {pct(s.value)}
                      </span>
                    </div>
                  ))}
                </div>
                <Takeaway>
                  a literatura aponta leve vantagem azul no solo queue (~50,6-53%), mas neste
                  recorte (Challenger/GM BR) o vermelho domina — estável em todos os patches.
                  Hipótese: counter-pick garantido pesa mais no elo em que todos punem draft,
                  somado ao acesso ao pit do dragão. É por isso que a predição "empatada" não
                  dá 50%.
                </Takeaway>
              </>
            ) : null}
          </CardContent>
        </Card>
      </div>

      {/* ---------------- retrato do meta ---------------- */}
      <SectionTitle
        eyebrow="Seção 2"
        title="Retrato do meta"
        desc="Como são as partidas deste elo — ritmo, duração e agressividade."
      />

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Duração das partidas (minutos)</CardTitle>
            </CardHeader>
            <CardContent className="h-56">
              {durations.isPending ? (
                <Skeleton className="h-full" />
              ) : durations.isError ? (
                <ErrorNote message={durations.error.message} />
              ) : (
                <ResponsiveContainer>
                  <BarChart data={durations.data}>
                    <CartesianGrid vertical={false} {...GRID} />
                    <XAxis dataKey="range" tick={AXIS_TICK} stroke="var(--baseline)" />
                    <YAxis tick={AXIS_TICK} stroke="var(--baseline)" />
                    <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--grid)", opacity: 0.4 }} />
                    <Bar
                      dataKey="matches"
                      name="Partidas"
                      fill="var(--chart-1)"
                      barSize={28}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
            {modalDuration && o && (
              <CardContent className="pt-0">
                <Takeaway>
                  a faixa mais comum é {modalDuration.range} min e {pct(o.late_game_rate)} das
                  partidas passam dos 25 — por isso o modelo tem um corte específico de late
                  game: boa parte dos jogos chega lá.
                </Takeaway>
              </CardContent>
            )}
          </Card>
        </div>
        <div className="flex flex-col gap-4">
          <KpiCard
            label="Abates por partida"
            value={o?.avg_kills ?? "…"}
            hint="média dos dois times somados — meta agressivo"
          />
          <KpiCard
            label="Chegam ao late game"
            value={o ? pct(o.late_game_rate) : "…"}
            hint="partidas com 25+ minutos"
          />
          <KpiCard
            label="Duração média"
            value={o ? `${o.avg_duration_min} min` : "…"}
          />
        </div>
      </div>

      {/* ---------------- cobertura do dataset ---------------- */}
      <SectionTitle
        eyebrow="Seção 3"
        title="Cobertura do dataset"
        desc="De onde vêm os números — tamanho e distribuição da amostra."
      />

      <div className="grid grid-cols-3 gap-4">
        <div className="flex flex-col gap-4">
          <KpiCard label="Partidas" value={o?.matches.toLocaleString("pt-BR") ?? "…"} />
          <KpiCard label="Jogadores únicos" value={o?.players.toLocaleString("pt-BR") ?? "…"} />
          <KpiCard
            label="Patches cobertos"
            value={o?.patches ?? "…"}
            hint="versões completas do cliente; o gráfico agrupa por patch de balanceamento (16.x)"
          />
        </div>
        <div className="col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Partidas por patch</CardTitle>
            </CardHeader>
            <CardContent className="h-56">
              {patches.isPending ? (
                <Skeleton className="h-full" />
              ) : patches.isError ? (
                <ErrorNote message={patches.error.message} />
              ) : (
                <ResponsiveContainer>
                  <BarChart data={patches.data}>
                    <CartesianGrid vertical={false} {...GRID} />
                    <XAxis dataKey="patch" tick={AXIS_TICK} stroke="var(--baseline)" />
                    <YAxis tick={AXIS_TICK} stroke="var(--baseline)" />
                    <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--grid)", opacity: 0.4 }} />
                    <Bar
                      dataKey="matches"
                      name="Partidas"
                      fill="var(--chart-1)"
                      barSize={26}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
            {topPatch && totalPatchGames > 0 && (
              <CardContent className="pt-0">
                <Takeaway>
                  o patch {topPatch.patch} concentra{" "}
                  {pct(topPatch.matches / totalPatchGames)} do dataset — estatísticas de meta
                  (win/ban rate) refletem sobretudo essa versão; patches com poucas partidas
                  merecem menos confiança.
                </Takeaway>
              </CardContent>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
