/** Smoke test das páginas: cada uma renderiza (estado de loading, sem
 * crashar) dentro dos providers reais. `api` é mockado com uma Promise
 * que nunca resolve — testa o caminho de mount/params/loading (onde
 * bugs de hook/useParams/JSX aparecem), não o de dados renderizados
 * (que exigiria fixtures completas para cada endpoint).
 *
 * Simulador ganha um teste à parte que clica nas 3 abas (Composição /
 * Estado / Explicabilidade) — cada uma é um componente com seus
 * próprios hooks, só montado quando a aba é selecionada. */
import { fireEvent, screen } from "@testing-library/react";
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
import { Home } from "@/pages/Home";
import { MatchDetail } from "@/pages/MatchDetail";
import { Nlq } from "@/pages/Nlq";
import { PlayerProfile } from "@/pages/PlayerProfile";
import { ProPlayerProfile } from "@/pages/ProPlayerProfile";
import { Simulador } from "@/pages/Simulador";

const PAGES: { name: string; ui: React.ReactElement; path?: string; route?: string }[] = [
  { name: "Home", ui: <Home /> },
  { name: "Dashboard", ui: <Dashboard /> },
  { name: "Champions", ui: <Champions /> },
  { name: "ChampionDetail", ui: <ChampionDetail />, path: "/campeoes/:name", route: "/campeoes/Ahri" },
  { name: "MatchDetail", ui: <MatchDetail />, path: "/partidas/:id", route: "/partidas/BR1_123" },
  {
    name: "MatchDetail (replay)",
    ui: <MatchDetail />,
    path: "/partidas/:id",
    route: "/partidas/BR1_123?replay=1",
  },
  { name: "Competitivo", ui: <Competitivo /> },
  {
    name: "ProPlayerProfile",
    ui: <ProPlayerProfile />,
    path: "/competitivo/jogadores/:name",
    route: "/competitivo/jogadores/Faker",
  },
  { name: "PlayerProfile", ui: <PlayerProfile />, path: "/jogadores/:puuid", route: "/jogadores/abc123" },
  { name: "Nlq", ui: <Nlq /> },
  { name: "Simulador", ui: <Simulador /> },
];

describe("smoke: todas as páginas renderizam sem crashar", () => {
  for (const { name, ui, path, route } of PAGES) {
    it(name, () => {
      const { container } = renderPage(ui, { path, route });
      expect(container).not.toBeEmptyDOMElement();
    });
  }
});

describe("smoke: abas do Simulador renderizam sem crashar", () => {
  it("Composição → Estado → Explicabilidade", () => {
    renderPage(<Simulador />);
    for (const label of ["Estado", "Explicabilidade", "Composição"]) {
      fireEvent.click(screen.getByRole("button", { name: label }));
    }
  });
});
