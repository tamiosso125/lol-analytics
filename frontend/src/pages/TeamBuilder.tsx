import { useMutation, useQuery } from "@tanstack/react-query";
import { Swords, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { Button, Card, CardContent, CardHeader, CardTitle, ErrorNote, PageHeader, Skeleton } from "@/components/ui";
import { api, type ComposeLane, type ComposeSynergy, type MatchState } from "@/lib/api";
import { championDisplayName, championIcon, POSITION_LABELS } from "@/lib/ddragon";
import { deltaColor, formatPct as pct } from "@/lib/format";
import { INITIAL_STATE, PHASES, RANGES, SLIDER_KEYS, SLIDER_LABELS, withMinute } from "@/lib/matchState";
import { cn } from "@/lib/utils";
const POSITIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"] as const;

type Team = Record<string, string>;

/** Barra de probabilidade azul × vermelho com marca nos 50%. */
function ProbMeter({ value }: { value: number }) {
  return (
    <div className="relative mt-4 h-3 overflow-hidden rounded-full bg-chart-red/25">
      <div
        className="h-full rounded-full bg-chart-1 transition-[width] duration-300"
        style={{ width: `${value * 100}%` }}
      />
      <div className="absolute inset-y-0 left-1/2 w-px bg-foreground/40" />
    </div>
  );
}

/** Campo de campeão com busca: digita e filtra por nome, estilo
 * combobox (não um <select> nativo) — teclado (setas/Enter/Esc), clique
 * fora fecha, e um "x" para limpar a escolha do slot. */
function ChampionCombobox({
  value,
  onChange,
  options,
  side,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { name: string; id: number }[];
  side: "blue" | "red";
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  // guarda o timeout do blur para cancelar se um novo foco chegar antes
  // dele disparar (sem isso, um foco rápido logo após um blur — Esc
  // seguido de clique em outro campo — podia fechar o dropdown recém-
  // aberto por causa do timeout antigo ainda pendente)
  const blurTimeout = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const selected = options.find((o) => o.name === value);
  // fechado: mostra o nome do campeão escolhido; aberto: o texto digitado
  const displayValue = open ? query : selected ? championDisplayName(selected.name) : "";

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return needle
      ? options.filter((o) => championDisplayName(o.name).toLowerCase().includes(needle))
      : options;
  }, [query, options]);

  useEffect(() => {
    if (!open) return;
    function onClickOutside(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  const pick = (name: string) => {
    onChange(name);
    setOpen(false);
    setQuery("");
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!open) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, matches.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (matches[highlight]) pick(matches[highlight].name);
    } else if (e.key === "Escape") {
      setOpen(false);
      setQuery("");
      inputRef.current?.blur();
    }
  };

  const icon = selected ? (
    <img src={championIcon(selected.id)} alt="" className="size-8 shrink-0 rounded-md" />
  ) : (
    <div className="size-8 shrink-0 rounded-md border border-dashed border-border" />
  );

  return (
    <div ref={rootRef} className="flex items-center gap-2">
      {side === "blue" && icon}
      <div className="relative min-w-0 flex-1">
        <input
          ref={inputRef}
          value={displayValue}
          onFocus={() => {
            clearTimeout(blurTimeout.current);
            setOpen(true);
            setQuery("");
            setHighlight(0);
          }}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            setHighlight(0);
          }}
          onKeyDown={onKeyDown}
          onBlur={() => {
            blurTimeout.current = setTimeout(() => setOpen(false), 100);
          }}
          placeholder="— escolher —"
          className={cn(
            "w-full rounded-lg border border-border bg-card px-2 py-1.5 text-sm",
            !selected && !open && "text-muted-ink",
            selected && !open && "pr-7",
          )}
        />
        {selected && !open && (
          <button
            type="button"
            aria-label="Limpar campeão"
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => onChange("")}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted-ink hover:text-foreground"
          >
            <X size={13} />
          </button>
        )}
        {open && (
          <div className="absolute inset-x-0 top-full z-20 mt-1 max-h-56 overflow-y-auto rounded-lg border border-border bg-card shadow-lg">
            {matches.length === 0 ? (
              <p className="px-3 py-2 text-xs text-muted-ink">Nenhum campeão encontrado.</p>
            ) : (
              matches.map((o, i) => (
                <button
                  key={o.name}
                  type="button"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => pick(o.name)}
                  className={cn(
                    "flex w-full items-center gap-2 px-2.5 py-1.5 text-left text-sm",
                    i === highlight ? "bg-accent/10 text-accent" : "hover:bg-foreground/5",
                  )}
                >
                  <img src={championIcon(o.id)} alt="" className="size-6 rounded" />
                  {championDisplayName(o.name)}
                </button>
              ))
            )}
          </div>
        )}
      </div>
      {side === "red" && icon}
    </div>
  );
}

/** Campo de jogador com busca no servidor (Riot ID) — mesmo estilo do
 * ChampionCombobox, mas os resultados vêm de /stats/players/search em
 * vez de um catálogo local. Guarda o puuid; o rótulo (name#tag) é
 * repassado pra quem chama exibir sem precisar buscar de novo. */
function PlayerCombobox({
  value,
  displayName,
  onChange,
  disabled,
}: {
  value: string;
  displayName: string;
  onChange: (puuid: string, label: string) => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);
  const blurTimeout = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const needle = query.trim();

  const search = useQuery({
    queryKey: ["player-search-tb", needle],
    queryFn: () => api.playersSearch(needle),
    enabled: needle.length >= 3,
  });
  const matches = search.data?.solo ?? [];
  const displayValue = open ? query : value ? displayName : "";

  useEffect(() => {
    if (!open) return;
    function onClickOutside(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  return (
    <div ref={rootRef} className="relative flex-1">
      <input
        value={displayValue}
        disabled={disabled}
        onFocus={() => {
          clearTimeout(blurTimeout.current);
          setOpen(true);
          setQuery("");
        }}
        onChange={(e) => setQuery(e.target.value)}
        onBlur={() => {
          blurTimeout.current = setTimeout(() => setOpen(false), 100);
        }}
        placeholder={disabled ? "escolha o campeão primeiro" : "Riot ID (opcional)…"}
        className={cn(
          "w-full rounded-lg border border-border bg-card px-2 py-1.5 text-xs disabled:opacity-50",
          !value && "text-muted-ink",
          value && !open && "pr-6",
        )}
      />
      {value && !open && (
        <button
          type="button"
          aria-label="Limpar jogador"
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => onChange("", "")}
          className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted-ink hover:text-foreground"
        >
          <X size={11} />
        </button>
      )}
      {open && needle.length >= 3 && (
        <div className="absolute inset-x-0 top-full z-20 mt-1 max-h-48 overflow-y-auto rounded-lg border border-border bg-card shadow-lg">
          {search.isPending ? (
            <p className="px-3 py-2 text-xs text-muted-ink">Buscando…</p>
          ) : matches.length === 0 ? (
            <p className="px-3 py-2 text-xs text-muted-ink">Nenhum jogador encontrado.</p>
          ) : (
            matches.map((p) => (
              <button
                key={p.puuid}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => {
                  onChange(p.puuid, `${p.name}#${p.tag}`);
                  setOpen(false);
                  setQuery("");
                }}
                className="flex w-full items-center gap-2 px-2.5 py-1.5 text-left text-xs hover:bg-foreground/5"
              >
                <span className="min-w-0 flex-1 truncate">
                  {p.name}#{p.tag}
                </span>
                <span className="text-muted-ink tabular-nums">
                  {p.games}j · {pct(p.win_rate)}
                </span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}

/** Nota do ajuste de jogador numa lane, quando há pelo menos um lado
 * com jogador selecionado — mostra o cálculo de shrinkage por trás do
 * número, para não virar caixa-preta. */
function PlayerAdjustmentNote({ lane }: { lane: ComposeLane }) {
  if (!lane.blue_player && !lane.red_player) return null;
  const parts: string[] = [];
  if (lane.blue_player) {
    const bp = lane.blue_player;
    parts.push(
      `${bp.name} (azul): ${bp.games_on_champion} jogos${
        bp.raw_win_rate != null ? `, ${pct(bp.raw_win_rate)} bruto` : ""
      } → ${pct(bp.shrunk_win_rate)} após shrinkage`,
    );
  }
  if (lane.red_player) {
    const rp = lane.red_player;
    parts.push(
      `${rp.name} (vermelho): ${rp.games_on_champion} jogos${
        rp.raw_win_rate != null ? `, ${pct(rp.raw_win_rate)} bruto` : ""
      } → ${pct(rp.shrunk_win_rate)} após shrinkage`,
    );
  }
  return (
    <p className="pl-16 text-xs text-muted-ink">
      {parts.join(" · ")} — sem jogador, a lane seria {pct(lane.composition_win_rate)}.
    </p>
  );
}

function SynergyList({ title, synergies }: { title: string; synergies: ComposeSynergy[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {synergies.length === 0 ? (
          <p className="text-sm text-muted-ink">
            Sem duplas com amostra suficiente (≥ 20 jogos juntos).
          </p>
        ) : (
          synergies.map((s) => (
            <div key={`${s.a}-${s.b}`} className="flex items-center gap-2 text-sm">
              <img src={championIcon(s.a_id)} alt="" className="size-6 rounded" />
              <img src={championIcon(s.b_id)} alt="" className="size-6 rounded" />
              <span className="min-w-0 flex-1 truncate">
                {championDisplayName(s.a)} + {championDisplayName(s.b)}
              </span>
              <span className="text-xs text-muted-ink tabular-nums">{s.games} jogos</span>
              <span
                className={cn(
                  "w-16 text-right font-medium tabular-nums",
                  deltaColor(s.delta),
                )}
              >
                {s.delta >= 0 ? "+" : ""}
                {(s.delta * 100).toFixed(1)}pp
              </span>
            </div>
          ))
        )}
        <p className="border-t border-border pt-2 text-xs text-muted-ink">
          Sinergia = win rate da dupla junta vs a média individual dos dois (pontos
          percentuais).
        </p>
      </CardContent>
    </Card>
  );
}

export function TeamBuilder() {
  const [blue, setBlue] = useState<Team>({});
  const [red, setRed] = useState<Team>({});
  const [withState, setWithState] = useState(false);
  const [state, setState] = useState<MatchState>(INITIAL_STATE);
  const [withPlayers, setWithPlayers] = useState(false);
  const [bluePlayers, setBluePlayers] = useState<Team>({}); // posição -> puuid
  const [redPlayers, setRedPlayers] = useState<Team>({});
  const [bluePlayerNames, setBluePlayerNames] = useState<Team>({}); // posição -> "nome#tag"
  const [redPlayerNames, setRedPlayerNames] = useState<Team>({});

  const champions = useQuery({
    queryKey: ["champions-all"],
    queryFn: () => api.champions({ minGames: 1, limit: 300 }),
  });
  const options = useMemo(
    () =>
      (champions.data ?? [])
        .map((c) => ({ name: c.champion, id: c.champion_id }))
        .sort((a, b) => championDisplayName(a.name).localeCompare(championDisplayName(b.name), "pt-BR")),
    [champions.data],
  );
  // um campeão só pode ser escolhido uma vez na partida — cada select só
  // oferece os que ainda não foram usados (mantendo o valor atual do slot)
  const picked = useMemo(
    () => new Set([...Object.values(blue), ...Object.values(red)].filter(Boolean)),
    [blue, red],
  );
  const optionsFor = (current: string) =>
    options.filter((o) => o.name === current || !picked.has(o.name));

  const analyze = useMutation({
    mutationFn: () =>
      api.compose(
        blue,
        red,
        withState ? state : undefined,
        withPlayers ? bluePlayers : undefined,
        withPlayers ? redPlayers : undefined,
      ),
  });
  const lanesFilled = POSITIONS.filter((p) => blue[p] && red[p]).length;
  const result = analyze.data;
  const ranges = RANGES[state.minute];

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Simulador" title="Montar partida">
        Escolha os campeões dos dois times e receba a análise do confronto: matchup de cada
        lane, sinergias de dupla e uma estimativa geral — tudo calculado do histórico real
        de partidas. Opcionalmente, simule também um momento da partida (minuto, ouro,
        abates e objetivos) para combinar a composição com o modelo ML.
      </PageHeader>

      <Card>
        <CardContent className="pt-4">
          {champions.isPending ? (
            <Skeleton className="h-72" />
          ) : champions.isError ? (
            <ErrorNote message={champions.error.message} />
          ) : (
            <div className="space-y-2">
              <div className="mb-1 grid grid-cols-[1fr_90px_1fr] items-center gap-3 text-center">
                <span className="text-sm font-medium text-chart-1">Time azul</span>
                <span />
                <span className="text-sm font-medium text-chart-red">Time vermelho</span>
              </div>
              {POSITIONS.map((pos) => (
                <div key={pos} className="grid grid-cols-[1fr_90px_1fr] items-center gap-3">
                  <ChampionCombobox
                    side="blue"
                    value={blue[pos] ?? ""}
                    onChange={(v) => setBlue((t) => ({ ...t, [pos]: v }))}
                    options={optionsFor(blue[pos] ?? "")}
                  />
                  <span className="text-center text-xs font-medium text-muted-ink">
                    {POSITION_LABELS[pos]}
                  </span>
                  <ChampionCombobox
                    side="red"
                    value={red[pos] ?? ""}
                    onChange={(v) => setRed((t) => ({ ...t, [pos]: v }))}
                    options={optionsFor(red[pos] ?? "")}
                  />
                </div>
              ))}
              <div className="flex items-center gap-3 pt-2">
                <Button
                  onClick={() => analyze.mutate()}
                  disabled={lanesFilled === 0 || analyze.isPending}
                >
                  <Swords size={14} />
                  {analyze.isPending ? "Analisando…" : "Analisar confronto"}
                </Button>
                <button
                  onClick={() => {
                    setBlue({});
                    setRed({});
                    setState(INITIAL_STATE);
                    setBluePlayers({});
                    setRedPlayers({});
                    setBluePlayerNames({});
                    setRedPlayerNames({});
                    analyze.reset();
                  }}
                  className="text-xs text-muted-ink underline-offset-2 hover:underline"
                >
                  Limpar
                </button>
                <span className="ml-auto text-xs text-muted-ink">
                  {lanesFilled}/5 lanes preenchidas nos dois times
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Jogadores (opcional)</CardTitle>
            <p className="mt-0.5 text-xs text-muted-ink">
              Ajusta cada lane pelo desempenho do jogador NAQUELE campeão — com shrinkage
              bayesiano: poucos jogos pesam pouco (perto da média do campeão), muitos jogos
              aproximam do desempenho real observado. Só solo queue.
            </p>
          </div>
          <label className="flex shrink-0 items-center gap-2 text-sm text-secondary-ink">
            <input
              type="checkbox"
              checked={withPlayers}
              onChange={(e) => setWithPlayers(e.target.checked)}
              className="accent-accent"
            />
            Incluir
          </label>
        </CardHeader>
        {withPlayers && (
          <CardContent className="space-y-2 pt-2">
            {POSITIONS.map((pos) => (
              <div key={pos} className="grid grid-cols-[1fr_90px_1fr] items-center gap-3">
                <PlayerCombobox
                  value={bluePlayers[pos] ?? ""}
                  displayName={bluePlayerNames[pos] ?? ""}
                  disabled={!blue[pos]}
                  onChange={(puuid, label) => {
                    setBluePlayers((t) => ({ ...t, [pos]: puuid }));
                    setBluePlayerNames((t) => ({ ...t, [pos]: label }));
                  }}
                />
                <span className="text-center text-xs font-medium text-muted-ink">
                  {POSITION_LABELS[pos]}
                </span>
                <PlayerCombobox
                  value={redPlayers[pos] ?? ""}
                  displayName={redPlayerNames[pos] ?? ""}
                  disabled={!red[pos]}
                  onChange={(puuid, label) => {
                    setRedPlayers((t) => ({ ...t, [pos]: puuid }));
                    setRedPlayerNames((t) => ({ ...t, [pos]: label }));
                  }}
                />
              </div>
            ))}
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Estado da partida (opcional)</CardTitle>
            <p className="mt-0.5 text-xs text-muted-ink">
              Simule um momento: minuto, ouro, XP (nível), abates, torres e dragões — o
              modelo ML da fase entra na conta junto com a composição.
            </p>
          </div>
          <label className="flex shrink-0 items-center gap-2 text-sm text-secondary-ink">
            <input
              type="checkbox"
              checked={withState}
              onChange={(e) => setWithState(e.target.checked)}
              className="accent-accent"
            />
            Incluir
          </label>
        </CardHeader>
        {withState && (
          <CardContent className="space-y-4 pt-2">
            <div className="inline-flex rounded-lg border border-border p-0.5">
              {PHASES.map((p) => (
                <button
                  key={p.minute}
                  onClick={() => setState((s) => withMinute(s, p.minute))}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-left transition-colors",
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
            <div className="grid grid-cols-2 gap-x-8 gap-y-4 xl:grid-cols-3">
              {SLIDER_KEYS.map((key) => (
                <div key={key}>
                  <div className="mb-1 flex justify-between text-sm">
                    <label htmlFor={`tb-${key}`} className="text-secondary-ink">
                      {SLIDER_LABELS[key]}
                    </label>
                    <span className="font-medium tabular-nums">
                      {state[key] > 0
                        ? `+${state[key].toLocaleString("pt-BR")}`
                        : state[key].toLocaleString("pt-BR")}
                    </span>
                  </div>
                  <input
                    id={`tb-${key}`}
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
            </div>
            <p className="text-xs text-muted-ink">
              Valores azul − vermelho, aos {state.minute} minutos. Tudo em zero = partida
              empatada nesse minuto.
            </p>
          </CardContent>
        )}
      </Card>

      {analyze.isError && <ErrorNote message={analyze.error.message} />}

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>
                {result.state_analysis ? "Estimativa combinada do confronto" : "Estimativa do confronto"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-3">
                <span className="text-5xl font-semibold tabular-nums tracking-tight">
                  {pct(
                    result.state_analysis?.combined_probability ??
                      result.estimate.blue_win_probability,
                  )}
                </span>
                <span className="text-sm text-secondary-ink">
                  de chance para o time azul
                  {result.state_analysis
                    ? ` — composição + estado aos ${result.state_analysis.minute} min`
                    : ` (${result.estimate.lanes_used} lanes analisadas)`}
                </span>
              </div>
              <ProbMeter
                value={
                  result.state_analysis?.combined_probability ??
                  result.estimate.blue_win_probability
                }
              />
              {result.state_analysis ? (
                <>
                  <div className="mt-4 grid grid-cols-3 gap-3 border-t border-border pt-3 text-sm">
                    <div>
                      <p className="text-xs text-muted-ink">Só a composição (heurística)</p>
                      <p className="mt-0.5 text-xl font-semibold tabular-nums">
                        {pct(result.estimate.blue_win_probability)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-ink">
                        Só o estado (modelo ML, {result.state_analysis.minute} min)
                      </p>
                      <p className="mt-0.5 text-xl font-semibold tabular-nums">
                        {pct(result.state_analysis.ml_probability)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-ink">
                        Empate nesse minuto (taxa-base, com viés de lado)
                      </p>
                      <p className="mt-0.5 text-xl font-semibold tabular-nums">
                        {pct(result.state_analysis.base_probability)}
                      </p>
                    </div>
                  </div>
                  <p className="mt-3 text-xs text-muted-ink">{result.state_analysis.note}</p>
                </>
              ) : (
                <p className="mt-3 text-xs text-muted-ink">{result.estimate.note}</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Matchup por lane (chance do campeão azul)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {result.lanes.map((l) => (
                <div key={l.position} className="space-y-0.5">
                  <div className="flex items-center gap-3 text-sm">
                    <span className="w-16 text-xs text-muted-ink">
                      {POSITION_LABELS[l.position] ?? l.position}
                    </span>
                    <img src={championIcon(l.blue_id)} alt="" className="size-7 rounded" />
                    <span className="w-28 truncate">{championDisplayName(l.blue)}</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-chart-red/30">
                      <div
                        className="h-full bg-chart-1"
                        style={{ width: `${l.blue_lane_win_rate * 100}%` }}
                      />
                    </div>
                    <span className="w-14 text-right font-medium tabular-nums">
                      {pct(l.blue_lane_win_rate)}
                    </span>
                    <span className="w-28 truncate text-right">{championDisplayName(l.red)}</span>
                    <img src={championIcon(l.red_id)} alt="" className="size-7 rounded" />
                    <span className="w-24 text-right text-xs text-muted-ink tabular-nums">
                      {l.source === "matchup"
                        ? `${l.matchup_games} jogos diretos`
                        : "perfil geral*"}
                    </span>
                  </div>
                  <PlayerAdjustmentNote lane={l} />
                </div>
              ))}
              <p className="border-t border-border pt-2 text-xs text-muted-ink">
                *Quando o confronto direto tem menos de 10 jogos, usamos a diferença dos win
                rates gerais dos dois campeões como aproximação.
              </p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 gap-4">
            <SynergyList title="Sinergias — time azul" synergies={result.synergies.blue} />
            <SynergyList title="Sinergias — time vermelho" synergies={result.synergies.red} />
          </div>
        </>
      )}
    </div>
  );
}
