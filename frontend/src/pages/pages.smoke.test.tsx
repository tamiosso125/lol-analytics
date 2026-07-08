/** Smoke test das 13 páginas: cada uma renderiza (estado de loading,
 * sem crashar) dentro dos providers reais. `api` é mockado com uma
 * Promise que nunca resolve — testa o caminho de mount/params/loading
 * (onde bugs de hook/useParams/JSX aparecem), não o de dados
 * renderizados (que exigiria fixtures completas para cada endpoint). */
import { describe, expect, it, vi } from "vitest";

import { renderPage } from "@/test/renderPage";

vi.mock("@/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api")>();
  const pending = () => new Promise(() => {});
  return { ...actual, api: new Proxy({}, { get: () => pending }) as typeof actual.api };
});

import { ChampionDetail } from "@/pages/ChampionDetail";
import { Champions } from "@/pages/Champions";
import { Competitivo } from "@/pages/Competitivo";
import { Dashboard } from "@/pages/Dashboard";
import { Explain } from "@/pages/Explain";
import { Home } from "@/pages/Home";
import { LiveReplay } from "@/pages/LiveReplay";
import { MatchDetail } from "@/pages/MatchDetail";
import { Matches } from "@/pages/Matches";
import { Nlq } from "@/pages/Nlq";
import { PlayerProfile } from "@/pages/PlayerProfile";
import { Predict } from "@/pages/Predict";
import { ProPlayerProfile } from "@/pages/ProPlayerProfile";
import { TeamBuilder } from "@/pages/TeamBuilder";

const PAGES: { name: string; ui: React.ReactElement; path?: string; route?: string }[] = [
  { name: "Home", ui: <Home /> },
  { name: "Dashboard", ui: <Dashboard /> },
  { name: "Champions", ui: <Champions /> },
  { name: "ChampionDetail", ui: <ChampionDetail />, path: "/campeoes/:name", route: "/campeoes/Ahri" },
  { name: "Matches", ui: <Matches /> },
  { name: "MatchDetail", ui: <MatchDetail />, path: "/partidas/:id", route: "/partidas/BR1_123" },
  { name: "Competitivo", ui: <Competitivo /> },
  {
    name: "ProPlayerProfile",
    ui: <ProPlayerProfile />,
    path: "/competitivo/jogadores/:name",
    route: "/competitivo/jogadores/Faker",
  },
  { name: "PlayerProfile", ui: <PlayerProfile />, path: "/jogadores/:puuid", route: "/jogadores/abc123" },
  { name: "Nlq", ui: <Nlq /> },
  { name: "Predict", ui: <Predict /> },
  { name: "LiveReplay", ui: <LiveReplay /> },
  { name: "TeamBuilder", ui: <TeamBuilder /> },
  { name: "Explain", ui: <Explain /> },
];

describe("smoke: todas as páginas renderizam sem crashar", () => {
  for (const { name, ui, path, route } of PAGES) {
    it(name, () => {
      const { container } = renderPage(ui, { path, route });
      expect(container).not.toBeEmptyDOMElement();
    });
  }
});
