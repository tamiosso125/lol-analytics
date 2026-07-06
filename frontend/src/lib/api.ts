/** Cliente da API FastAPI (src/api/main.py). */

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** kind distingue a origem do erro para a UI decidir como apresentá-lo:
 *  - "validation": a pergunta/entrada foi rejeitada (400) — não é falha nossa.
 *  - "network": a API não respondeu (servidor fora do ar, CORS, DNS) — é falha nossa.
 *  - "server": a API respondeu com um erro (5xx/422) — é falha nossa. */
export class ApiError extends Error {
  kind: "validation" | "network" | "server";
  status?: number;
  /** SQL gerada e erro real do banco, quando a falha foi na execução da
   * consulta (não na validação) — para diagnosticar, não só "tente de novo". */
  sql?: string;
  cause?: string;

  constructor(
    message: string,
    kind: "validation" | "network" | "server",
    status?: number,
    sql?: string,
    cause?: string,
  ) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
    this.sql = sql;
    this.cause = cause;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(
      `Não foi possível conectar à API em ${API_URL}. Verifique se o servidor está rodando ` +
        "(uvicorn src.api.main:app).",
      "network",
    );
  }
  if (!resp.ok) {
    const body = await resp.json().catch(() => null);
    const detail = body?.detail;
    if (detail && typeof detail === "object") {
      throw new ApiError(detail.message ?? `Erro ${resp.status}`, "server", resp.status, detail.sql, detail.cause);
    }
    const message = typeof detail === "string" ? detail : `Erro ${resp.status} em ${path}`;
    throw new ApiError(message, resp.status === 400 ? "validation" : "server", resp.status);
  }
  return resp.json();
}

export interface Overview {
  matches: number;
  players: number;
  avg_duration_min: number;
  patches: number;
  blue_win_rate: number;
  avg_kills: number;
  late_game_rate: number;
}

export interface PatchStat {
  patch: string;
  matches: number;
  blue_win_rate: number;
}

export interface ComposePlayerEffect {
  name: string;
  games_on_champion: number;
  raw_win_rate: number | null;
  shrunk_win_rate: number;
  logit_delta: number;
}

export interface ComposeLane {
  position: string;
  blue: string;
  blue_id: number;
  red: string;
  red_id: number;
  matchup_games: number;
  blue_lane_win_rate: number;
  /** win rate só pela composição, antes do ajuste de jogador (quando há) */
  composition_win_rate: number;
  source: "matchup" | "perfil";
  blue_player: ComposePlayerEffect | null;
  red_player: ComposePlayerEffect | null;
}

export interface ComposeSynergy {
  a: string;
  a_id: number;
  b: string;
  b_id: number;
  games: number;
  win_rate: number;
  delta: number;
}

export interface ComposeStateAnalysis {
  minute: number;
  /** modelo ML sobre o estado (inclui taxa-base/viés de lado) */
  ml_probability: number;
  /** predição do modelo com tudo zerado no mesmo minuto (só a taxa-base) */
  base_probability: number;
  /** log-odds do ML + log-odds da composição */
  combined_probability: number;
  note: string;
}

export interface ComposeResult {
  lanes: ComposeLane[];
  synergies: { blue: ComposeSynergy[]; red: ComposeSynergy[] };
  estimate: {
    blue_win_probability: number;
    lanes_used: number;
    note: string;
  };
  state_analysis: ComposeStateAnalysis | null;
}

export interface ChampionStat {
  champion: string;
  champion_id: number;
  games: number;
  win_rate: number;
  pick_rate: number;
  ban_rate: number;
  kda: number | null;
  avg_cs: number;
  avg_gold: number;
  avg_dmg: number;
  main_position: string;
}

export type ChampionSort =
  | "games"
  | "win_rate"
  | "pick_rate"
  | "ban_rate"
  | "kda"
  | "avg_cs"
  | "avg_gold"
  | "avg_dmg";

export interface ChampionPositionStat {
  position: string;
  games: number;
  win_rate: number;
  kda: number | null;
}

export interface ChampionMatchup {
  opponent: string;
  opponent_id: number;
  games: number;
  win_rate: number;
}

export interface ChampionRecentGame {
  match_id: string;
  date: string;
  duration_min: number;
  patch: string | null;
  position: string;
  kills: number;
  deaths: number;
  assists: number;
  win: boolean;
}

export interface ChampionDetail {
  champion: string;
  champion_id: number;
  games: number;
  win_rate: number;
  pick_rate: number;
  ban_rate: number;
  kda: number | null;
  avg_cs: number;
  avg_gold: number;
  avg_dmg: number;
  positions: ChampionPositionStat[];
  matchups: ChampionMatchup[];
  recent_games: ChampionRecentGame[];
}

export interface ChampionItemStat {
  item_id: number;
  name: string;
  games: number;
  pick_share: number;
  win_rate: number;
  avg_minute: number;
}

export interface ChampionItems {
  champion: string;
  games: number;
  items: ChampionItemStat[];
}

export interface ChampionPro {
  champion: string;
  year: number;
  games: number;
  win_rate: number | null;
  presence: number;
  leagues: { league: string; games: number; win_rate: number }[];
}

export interface DurationBucket {
  range: string;
  matches: number;
}

export interface Gold15Bucket {
  gold_diff_mid: number;
  label: string;
  blue_win_rate: number;
  matches: number;
}

export interface RecentMatchParticipant {
  team_id: number;
  champion: string;
  champion_id: number;
  position: string;
  kills: number;
  deaths: number;
  assists: number;
}

export interface RecentMatch {
  match_id: string;
  date: string;
  duration_min: number;
  patch: string | null;
  blue_win: boolean;
  participants: RecentMatchParticipant[];
}

export interface ObjectiveStat {
  win: boolean;
  dragons: number;
  barons: number;
  towers: number;
  heralds: number;
}

export interface ProOverview {
  year: number;
  games: number;
  blue_win_rate: number;
  avg_game_min: number;
  leagues: { league: string; games: number; blue_win_rate: number }[];
}

export interface ProYear {
  year: number;
  games: number;
}

export interface ProGold15Bucket {
  gold_diff_mid: number;
  label: string;
  blue_win_rate: number | null;
  matches: number;
}

export interface ProChampion {
  champion: string;
  pro_games: number;
  pro_win_rate: number;
  presence: number;
  champion_id: number | null;
  solo_games: number | null;
  solo_win_rate: number | null;
}

export interface PlayerSearchResult {
  solo: {
    puuid: string;
    name: string;
    tag: string;
    tier: string | null;
    games: number;
    win_rate: number;
  }[];
  pro: { name: string; games: number; team: string | null }[];
}

export interface PlayerProfile {
  puuid: string;
  name: string | null;
  tag: string | null;
  tier: string | null;
  division: string | null;
  league_points: number | null;
  games: number;
  win_rate: number;
  main_position: string | null;
  champion_pool: {
    champion: string;
    champion_id: number;
    games: number;
    win_rate: number;
    kda: number | null;
  }[];
  recent_games: {
    match_id: string;
    date: string;
    duration_min: number;
    champion: string;
    champion_id: number;
    position: string;
    kills: number;
    deaths: number;
    assists: number;
    win: boolean;
  }[];
}

export interface ProPlayerProfile {
  name: string;
  games: number;
  win_rate: number;
  main_position: string | null;
  current_team: string | null;
  seasons: { year: number; team: string; league: string; games: number; win_rate: number }[];
  champion_pool: {
    champion: string;
    games: number;
    win_rate: number;
    champion_id: number | null;
  }[];
}

export interface RegionStat {
  platform: string;
  matches: number;
  red_win_rate: number;
  avg_duration_min: number;
}

export interface AskResult {
  sql: string;
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

export interface HistoryTurn {
  question: string;
  sql: string;
}

export interface ExplainResult {
  explanation: string;
}

export interface MatchState {
  gold_diff: number;
  xp_diff: number;
  kill_diff: number;
  tower_diff: number;
  dragon_diff: number;
  minute: number;
}

export interface Prediction {
  blue_win_probability: number;
  shap_contributions: Record<string, number>;
  minute: number;
}

export interface ProbPoint {
  minute: number;
  blue_win_probability: number;
  model_cutoff: number;
  /** estado completo do minuto — semente do modo "e se" */
  gold_diff: number;
  xp_diff: number;
  kill_diff: number;
  tower_diff: number;
  dragon_diff: number;
}

export interface MatchTeam {
  team_id: number;
  win: boolean;
  barons: number;
  dragons: number;
  heralds: number;
  towers: number;
  inhibitors: number;
}

export interface MatchParticipantFull {
  team_id: number;
  champion: string;
  champion_id: number;
  position: string;
  kills: number;
  deaths: number;
  assists: number;
  gold: number;
  cs: number;
  vision: number;
  dmg: number;
  win: boolean;
}

export interface FramePlayer {
  team_id: number;
  champion: string;
  champion_id: number;
  x: number;
  y: number;
  level: number | null;
}

export interface PositionFrame {
  minute: number;
  players: FramePlayer[];
}

export interface KillEvent {
  minute: number;
  x: number;
  y: number;
  killer_team: number | null;
}

export interface ObjectiveEvent {
  minute: number;
  kind: "towers" | "dragons" | "barons" | "heralds" | "inhibitors";
  team_id: number;
}

export interface MatchPositions {
  match_id: string;
  frames: PositionFrame[];
  kills: KillEvent[];
  objectives: ObjectiveEvent[];
  bounds: { min: number; max_x: number; max_y: number };
}

export interface MatchAnalysis {
  match_id: string;
  date: string;
  duration_min: number;
  patch: string | null;
  teams: MatchTeam[];
  participants: MatchParticipantFull[];
  prob_curve: ProbPoint[];
}

export interface Highlights {
  total_matches: number;
  best_player: {
    puuid: string;
    name: string | null;
    tag: string | null;
    tier: string;
    games: number;
    win_rate: number;
  } | null;
  best_champion: {
    champion: string;
    champion_id: number;
    games: number;
    win_rate: number;
  } | null;
  most_lopsided_matchup: {
    champion: string;
    champion_id: number;
    opponent: string;
    opponent_id: number;
    games: number;
    win_rate: number;
  } | null;
  most_banned: { champion: string; champion_id: number; ban_rate: number } | null;
  red_side_win_rate: number;
}

export const api = {
  overview: () => request<Overview>("/stats/overview"),
  champions: (opts: {
    minGames?: number;
    limit?: number;
    sort?: ChampionSort;
    role?: string;
    search?: string;
  } = {}) => {
    const params = new URLSearchParams({
      min_games: String(opts.minGames ?? 20),
      limit: String(opts.limit ?? 200),
      sort: opts.sort ?? "games",
      role: opts.role ?? "",
      search: opts.search ?? "",
    });
    return request<ChampionStat[]>(`/stats/champions?${params}`);
  },
  championDetail: (name: string) =>
    request<ChampionDetail>(`/stats/champion/${encodeURIComponent(name)}`),
  championItems: (name: string) =>
    request<ChampionItems>(`/stats/champion/${encodeURIComponent(name)}/items`),
  championPro: (name: string) =>
    request<ChampionPro>(`/stats/champion/${encodeURIComponent(name)}/pro`),
  durations: () => request<DurationBucket[]>("/stats/durations"),
  gold15: () => request<Gold15Bucket[]>("/stats/gold15"),
  recentMatches: (limit = 15) => request<RecentMatch[]>(`/matches/recent?limit=${limit}`),
  randomMatch: () => request<{ match_id: string }>("/matches/random"),
  matchAnalysis: (matchId: string) =>
    request<MatchAnalysis>(`/matches/${encodeURIComponent(matchId)}/analysis`),
  highlights: () => request<Highlights>("/stats/highlights"),
  patches: () => request<PatchStat[]>("/stats/patches"),
  regions: () => request<RegionStat[]>("/stats/regions"),
  compose: (
    blue: Record<string, string>,
    red: Record<string, string>,
    state?: MatchState,
    bluePlayers?: Record<string, string>,
    redPlayers?: Record<string, string>,
  ) =>
    request<ComposeResult>("/compose", {
      method: "POST",
      body: JSON.stringify({
        blue,
        red,
        state: state ?? null,
        blue_players: bluePlayers ?? {},
        red_players: redPlayers ?? {},
      }),
    }),
  matchPositions: (matchId: string) =>
    request<MatchPositions>(`/matches/${encodeURIComponent(matchId)}/positions`),
  objectives: () => request<ObjectiveStat[]>("/stats/objectives"),
  playersSearch: (q: string) =>
    request<PlayerSearchResult>(`/stats/players/search?q=${encodeURIComponent(q)}`),
  playerProfile: (puuid: string) =>
    request<PlayerProfile>(`/stats/player/${encodeURIComponent(puuid)}`),
  proPlayerProfile: (name: string) =>
    request<ProPlayerProfile>(`/stats/pro/player/${encodeURIComponent(name)}`),
  proYears: () => request<ProYear[]>("/stats/pro/years"),
  proOverview: (year?: number) =>
    request<ProOverview>(`/stats/pro/overview${year ? `?year=${year}` : ""}`),
  proGold15: (year?: number) =>
    request<ProGold15Bucket[]>(`/stats/pro/gold15${year ? `?year=${year}` : ""}`),
  proChampions: (limit = 15, year?: number) =>
    request<ProChampion[]>(
      `/stats/pro/champions?limit=${limit}${year ? `&year=${year}` : ""}`,
    ),
  ask: (question: string, history: HistoryTurn[] = []) =>
    request<AskResult>("/ask", { method: "POST", body: JSON.stringify({ question, history }) }),
  explain: (question: string, result: AskResult) =>
    request<ExplainResult>("/ask/explain", {
      method: "POST",
      body: JSON.stringify({ question, ...result }),
    }),
  predict: (state: MatchState) =>
    request<Prediction>("/predict", { method: "POST", body: JSON.stringify(state) }),
  shapImportancePhases: () =>
    request<Record<string, Record<string, number>>>("/reports/shap_importance_phases.json"),
  reportImage: (name: string) => `${API_URL}/reports/${name}`,
};
