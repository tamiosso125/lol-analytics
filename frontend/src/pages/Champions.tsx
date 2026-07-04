import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Card, ErrorNote, Input, PageHeader, Skeleton } from "@/components/ui";
import { api, type ChampionSort } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

/** Micro-barra inline de tabela (estilo op.gg/leagueofgraphs): a barra
 * codifica magnitude relativa a `max`, o valor exato fica no texto. */
function MicroBar({ value, max, color }: { value: number; max: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 shrink-0 overflow-hidden rounded-full bg-foreground/10">
        <div
          className="h-full rounded-full"
          style={{ width: `${Math.min(100, (value / max) * 100)}%`, background: color }}
        />
      </div>
      <span className="tabular-nums">{pct(value)}</span>
    </div>
  );
}

const COLUMNS: { key: ChampionSort; label: string }[] = [
  { key: "games", label: "Jogos" },
  { key: "win_rate", label: "Win rate" },
  { key: "pick_rate", label: "Pick rate" },
  { key: "ban_rate", label: "Ban rate" },
  { key: "kda", label: "KDA" },
  { key: "avg_cs", label: "CS" },
  { key: "avg_gold", label: "Ouro" },
  { key: "avg_dmg", label: "Dano" },
];

const ROLES = ["", "TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"] as const;

export function Champions() {
  const navigate = useNavigate();
  const [role, setRole] = useState<string>("");
  const [sort, setSort] = useState<ChampionSort>("games");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [minGames, setMinGames] = useState(30);

  useEffect(() => {
    const t = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(t);
  }, [searchInput]);

  const champions = useQuery({
    queryKey: ["champions-full", role, sort, search, minGames],
    queryFn: () => api.champions({ minGames, sort, role, search, limit: 200 }),
    placeholderData: keepPreviousData,
  });

  const maxPick = Math.max(0.01, ...(champions.data?.map((c) => c.pick_rate) ?? []));
  const maxBan = Math.max(0.01, ...(champions.data?.map((c) => c.ban_rate) ?? []));

  return (
    <div className="space-y-5">
      <PageHeader eyebrow="Estatísticas" title="Campeões">
        Estatísticas por campeão nas partidas coletadas (ranqueada solo, Challenger/GM BR).
        Clique num campeão para ver detalhes e matchups.
      </PageHeader>

      <div className="flex flex-wrap items-center gap-3">
        <div className="inline-flex rounded-lg border border-border p-0.5 text-sm">
          {ROLES.map((r) => (
            <button
              key={r || "all"}
              onClick={() => setRole(r)}
              className={cn(
                "rounded-md px-3 py-1.5 font-medium transition-colors",
                role === r
                  ? "bg-accent/10 text-accent"
                  : "text-muted-ink hover:text-foreground",
              )}
            >
              {r === "" ? "Todas" : POSITION_LABELS[r]}
            </button>
          ))}
        </div>
        <div className="relative w-56">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-ink" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Buscar campeão…"
            className="pl-8"
          />
        </div>
        <label className="flex items-center gap-2 text-xs text-muted-ink">
          Mín. jogos
          <select
            value={minGames}
            onChange={(e) => setMinGames(Number(e.target.value))}
            className="rounded-lg border border-border bg-card px-2 py-1.5 text-sm text-foreground"
          >
            {[10, 30, 50, 100, 200].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </label>
        {champions.data && (
          <span className="ml-auto text-xs text-muted-ink">
            {champions.data.length} campeões
          </span>
        )}
      </div>

      <Card className="overflow-hidden">
        {champions.isPending ? (
          <Skeleton className="m-4 h-96" />
        ) : champions.isError ? (
          <div className="p-4">
            <ErrorNote message={champions.error.message} />
          </div>
        ) : (
          <div
            className={cn(
              "overflow-x-auto transition-opacity duration-200",
              champions.isFetching && "opacity-60",
            )}
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-secondary-ink">
                  <th className="px-4 py-3 font-medium">#</th>
                  <th className="px-2 py-3 font-medium">Campeão</th>
                  {COLUMNS.map((c) => (
                    <th key={c.key} className="px-2 py-3 font-medium">
                      <button
                        onClick={() => setSort(c.key)}
                        className={cn(
                          "hover:text-foreground",
                          sort === c.key && "text-accent",
                        )}
                      >
                        {c.label}
                        {sort === c.key && " ↓"}
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {champions.data.map((c, i) => (
                  <tr
                    key={c.champion}
                    onClick={() => navigate(`/campeoes/${c.champion}`)}
                    className="cursor-pointer border-b border-border/50 last:border-0 hover:bg-foreground/5"
                  >
                    <td className="px-4 py-2 text-muted-ink tabular-nums">{i + 1}</td>
                    <td className="px-2 py-2">
                      <div className="flex items-center gap-2.5">
                        <img
                          src={championIcon(c.champion_id)}
                          alt=""
                          loading="lazy"
                          className="size-8 rounded-md"
                        />
                        <div className="min-w-0">
                          <p className="font-medium leading-tight">
                            {championDisplayName(c.champion)}
                          </p>
                          <p className="text-xs text-muted-ink">
                            {POSITION_LABELS[c.main_position] ?? c.main_position}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-2 py-2 tabular-nums">{c.games.toLocaleString("pt-BR")}</td>
                    <td className="px-2 py-2">
                      <MicroBar value={c.win_rate} max={0.65} color="var(--chart-1)" />
                    </td>
                    <td className="px-2 py-2">
                      <MicroBar value={c.pick_rate} max={maxPick} color="var(--chart-2)" />
                    </td>
                    <td className="px-2 py-2">
                      <MicroBar value={c.ban_rate} max={maxBan} color="var(--chart-red)" />
                    </td>
                    <td className="px-2 py-2 tabular-nums">{c.kda ?? "—"}</td>
                    <td className="px-2 py-2 tabular-nums">{c.avg_cs.toLocaleString("pt-BR")}</td>
                    <td className="px-2 py-2 tabular-nums">{c.avg_gold.toLocaleString("pt-BR")}</td>
                    <td className="px-2 py-2 tabular-nums">{c.avg_dmg.toLocaleString("pt-BR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
