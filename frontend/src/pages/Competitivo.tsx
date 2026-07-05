import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
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
import { championIcon } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

/** Frase de conclusão sob o gráfico (mesmo padrão do Dashboard). */
function Takeaway({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-2 border-t border-border pt-2 text-xs leading-relaxed text-secondary-ink">
      <span className="font-medium text-gold">Leitura: </span>
      {children}
    </p>
  );
}

/** Barra dupla azul/vermelho de um contexto (solo queue ou pro). */
function SideBar({ label, blueWr }: { label: string; blueWr: number }) {
  return (
    <div>
      <p className="mb-1 text-xs text-secondary-ink">{label}</p>
      <div className="flex h-5 overflow-hidden rounded-full text-[10px] font-semibold text-white">
        <div
          className="flex items-center justify-center bg-chart-1"
          style={{ width: `${blueWr * 100}%` }}
        >
          {pct(blueWr)}
        </div>
        <div
          className="flex items-center justify-center bg-chart-red"
          style={{ width: `${(1 - blueWr) * 100}%` }}
        >
          {pct(1 - blueWr)}
        </div>
      </div>
    </div>
  );
}

export function Competitivo() {
  const [year, setYear] = useState<number | undefined>(undefined); // undefined = mais recente
  const years = useQuery({ queryKey: ["pro-years"], queryFn: api.proYears });
  const pro = useQuery({
    queryKey: ["pro-overview", year],
    queryFn: () => api.proOverview(year),
  });
  const solo = useQuery({ queryKey: ["overview"], queryFn: api.overview });
  const proGold = useQuery({
    queryKey: ["pro-gold15", year],
    queryFn: () => api.proGold15(year),
  });
  const soloGold = useQuery({ queryKey: ["gold15"], queryFn: api.gold15 });
  const champs = useQuery({
    queryKey: ["pro-champions", year],
    queryFn: () => api.proChampions(15, year),
  });

  if (pro.isPending) return <Skeleton className="h-96" />;
  if (pro.isError) return <ErrorNote message={pro.error.message} />;
  const p = pro.data;
  const s = solo.data;

  // junta as faixas de ouro dos dois contextos (mesmos buckets no backend)
  const goldCompare =
    proGold.data && soloGold.data
      ? proGold.data.map((b) => ({
          label: b.label,
          competitivo: b.blue_win_rate,
          soloqueue:
            soloGold.data.find((sb) => sb.gold_diff_mid === b.gold_diff_mid)?.blue_win_rate ??
            null,
        }))
      : [];

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <PageHeader eyebrow="Pro play" title="Competitivo">
          {p.games.toLocaleString("pt-BR")} jogos profissionais de {p.year} (LPL, LCK, LEC e
          mais — dados do Oracle's Elixir; o acervo completo cobre 2014-2026), lado a lado
          com as {s ? s.matches.toLocaleString("pt-BR") : "…"} partidas de solo queue
          Challenger/GM BR da plataforma. Mesmas métricas, dois contextos — e nem sempre a
          mesma conclusão.
        </PageHeader>
        <label className="flex shrink-0 items-center gap-2 pb-1 text-xs text-muted-ink">
          Ano
          <select
            value={year ?? p.year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-border bg-card px-2 py-1.5 text-sm text-foreground"
          >
            {(years.data ?? [{ year: p.year, games: p.games }]).map((y) => (
              <option key={y.year} value={y.year}>
                {y.year} ({y.games.toLocaleString("pt-BR")})
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Jogos profissionais</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-semibold tabular-nums tracking-tight">
              {p.games.toLocaleString("pt-BR")}
            </span>
            <p className="mt-1 text-xs text-muted-ink">{p.leagues.length}+ ligas cobertas</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Duração média</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-semibold tabular-nums tracking-tight">
              {p.avg_game_min} min
            </span>
            <p className="mt-1 text-xs text-muted-ink">
              solo queue: {s ? `${s.avg_duration_min} min` : "…"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Lado azul vence</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-semibold tabular-nums tracking-tight text-chart-1">
              {pct(p.blue_win_rate)}
            </span>
            <p className="mt-1 text-xs text-muted-ink">
              no solo queue BR: {s ? pct(s.blue_win_rate) : "…"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>O viés de lado INVERTE entre os dois contextos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {s && (
            <>
              <SideBar label="Competitivo 2026 (mundial)" blueWr={p.blue_win_rate} />
              <SideBar label="Solo queue Challenger/GM BR" blueWr={s.blue_win_rate} />
            </>
          )}
          <Takeaway>
            a literatura que aponta "leve vantagem azul" descreve bem o pro play — no
            competitivo o azul vence {pct(p.blue_win_rate)}, puxado pela prioridade de
            primeiro pick (tanto que times escolhem lado nos playoffs). No solo queue de elo
            altíssimo a lógica vira: sem draft coordenado de 5 pessoas, o counter-pick
            garantido do vermelho pesa mais e o azul cai para{" "}
            {s ? pct(s.blue_win_rate) : "…"}. Mesma métrica, sinais opostos — qualquer
            análise precisa dizer de QUAL contexto está falando.
          </Takeaway>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Ouro aos 15 minutos × vitória — pro converte mais?</CardTitle>
          <p className="mt-0.5 text-xs text-muted-ink">
            Win rate do lado azul por faixa de diferença de ouro aos 15 min, nos dois
            contextos (mesmas faixas).
          </p>
        </CardHeader>
        <CardContent className="h-72">
          {proGold.isPending || soloGold.isPending ? (
            <Skeleton className="h-full" />
          ) : proGold.isError ? (
            <ErrorNote message={proGold.error.message} />
          ) : (
            <ResponsiveContainer>
              <BarChart data={goldCompare} barGap={2}>
                <CartesianGrid vertical={false} {...GRID} />
                <XAxis dataKey="label" tick={AXIS_TICK} stroke="var(--baseline)" />
                <YAxis tickFormatter={pct} domain={[0, 1]} tick={AXIS_TICK} stroke="var(--baseline)" />
                <ReferenceLine y={0.5} stroke="var(--muted-ink)" strokeDasharray="4 4" />
                <Tooltip
                  content={<ChartTooltip format={(v) => pct(v)} />}
                  cursor={{ fill: "var(--grid)", opacity: 0.4 }}
                />
                <Legend
                  wrapperStyle={{ fontSize: 12 }}
                  formatter={(v: string) => (
                    <span style={{ color: "var(--secondary-ink)" }}>
                      {v === "competitivo" ? "Competitivo" : "Solo queue BR"}
                    </span>
                  )}
                />
                <Bar dataKey="competitivo" name="competitivo" fill="var(--chart-1)" barSize={18} radius={[4, 4, 0, 0]} />
                <Bar dataKey="soloqueue" name="soloqueue" fill="var(--chart-2)" barSize={18} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
        <CardContent className="pt-0">
          <Takeaway>
            times profissionais convertem vantagem de ouro de forma mais confiável — jogam
            fechado em volta da liderança (macro coordenado), enquanto no solo queue uma
            vantagem igual escorre com mais frequência. É o argumento quantitativo para a
            frase "macro ganha jogo": a MESMA vantagem material vale mais nas mãos de quem
            coordena o mapa.
          </Takeaway>
        </CardContent>
      </Card>

      <div className="grid grid-cols-5 gap-4">
        <div className="col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Jogos por liga</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5">
              {p.leagues.map((l) => (
                <div key={l.league} className="flex items-center gap-2 text-sm">
                  <span className="w-14 shrink-0 font-medium">{l.league}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-foreground/10">
                    <div
                      className="h-full rounded-full bg-chart-1"
                      style={{ width: `${(l.games / p.leagues[0].games) * 100}%` }}
                    />
                  </div>
                  <span className="w-10 text-right text-xs text-muted-ink tabular-nums">
                    {l.games}
                  </span>
                  <span className="w-14 text-right text-xs tabular-nums" title="win rate azul">
                    {pct(l.blue_win_rate)}
                  </span>
                </div>
              ))}
              <p className="border-t border-border pt-2 text-xs text-muted-ink">
                Última coluna: win rate do lado azul na liga.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Meta profissional × solo queue</CardTitle>
              <p className="mt-0.5 text-xs text-muted-ink">
                Campeões mais presentes no competitivo e como eles vão no nosso solo queue.
              </p>
            </CardHeader>
            <CardContent>
              {champs.isPending ? (
                <Skeleton className="h-64" />
              ) : champs.isError ? (
                <ErrorNote message={champs.error.message} />
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-secondary-ink">
                      <th className="py-2 font-medium">Campeão</th>
                      <th className="py-2 font-medium">Presença pro</th>
                      <th className="py-2 font-medium">WR pro</th>
                      <th className="py-2 font-medium">WR solo queue</th>
                    </tr>
                  </thead>
                  <tbody className="tabular-nums">
                    {champs.data.map((c) => (
                      <tr key={c.champion} className="border-b border-border/50 last:border-0">
                        <td className="py-1.5">
                          <span className="flex items-center gap-2">
                            {c.champion_id != null ? (
                              <img src={championIcon(c.champion_id)} alt="" className="size-6 rounded" />
                            ) : (
                              <span className="size-6 rounded border border-dashed border-border" />
                            )}
                            {c.champion}
                          </span>
                        </td>
                        <td className="py-1.5">
                          {pct(c.presence)}
                          <span className="ml-1 text-xs text-muted-ink">({c.pro_games})</span>
                        </td>
                        <td className={cn("py-1.5 font-medium", c.pro_win_rate >= 0.5 ? "text-chart-1" : "text-chart-red")}>
                          {pct(c.pro_win_rate)}
                        </td>
                        <td className="py-1.5">
                          {c.solo_win_rate != null ? (
                            <span className={cn("font-medium", c.solo_win_rate >= 0.5 ? "text-chart-1" : "text-chart-red")}>
                              {pct(c.solo_win_rate)}
                              <span className="ml-1 text-xs font-normal text-muted-ink">
                                ({c.solo_games})
                              </span>
                            </span>
                          ) : (
                            <span className="text-muted-ink">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
