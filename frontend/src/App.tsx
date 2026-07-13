import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "@/components/Layout";
import { Skeleton } from "@/components/ui";

// lazy por rota (2026-07-13) — o bundle único passou de 500KB (aviso do
// Vite) depois que as páginas acumularam features; cada página vira um
// chunk separado, carregado só quando o usuário navega até ela.
const ChampionDetail = lazy(() => import("@/pages/ChampionDetail").then((m) => ({ default: m.ChampionDetail })));
const Champions = lazy(() => import("@/pages/Champions").then((m) => ({ default: m.Champions })));
const Competitivo = lazy(() => import("@/pages/Competitivo").then((m) => ({ default: m.Competitivo })));
const Dashboard = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const Home = lazy(() => import("@/pages/Home").then((m) => ({ default: m.Home })));
const MatchDetail = lazy(() => import("@/pages/MatchDetail").then((m) => ({ default: m.MatchDetail })));
const Nlq = lazy(() => import("@/pages/Nlq").then((m) => ({ default: m.Nlq })));
const PlayerProfile = lazy(() => import("@/pages/PlayerProfile").then((m) => ({ default: m.PlayerProfile })));
const ProPlayerProfile = lazy(() =>
  import("@/pages/ProPlayerProfile").then((m) => ({ default: m.ProPlayerProfile })),
);
const Simulador = lazy(() => import("@/pages/Simulador").then((m) => ({ default: m.Simulador })));

export default function App() {
  return (
    <Suspense fallback={<Skeleton className="m-6 h-96" />}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="campeoes" element={<Champions />} />
          <Route path="campeoes/:name" element={<ChampionDetail />} />
          <Route path="partidas/:id" element={<MatchDetail />} />
          <Route path="competitivo" element={<Competitivo />} />
          <Route path="competitivo/jogadores/:name" element={<ProPlayerProfile />} />
          <Route path="jogadores/:puuid" element={<PlayerProfile />} />
          <Route path="consulta" element={<Nlq />} />
          <Route path="simulador" element={<Simulador />} />

          {/* rotas fundidas em 2026-07-06 (ver docs/diario_execucao.md) —
              redirects pra quem tiver essas URLs salvas */}
          <Route path="partidas" element={<Navigate to="/" replace />} />
          <Route path="predicao" element={<Navigate to="/simulador" replace />} />
          <Route path="explicabilidade" element={<Navigate to="/simulador" replace />} />
          <Route path="montar" element={<Navigate to="/simulador" replace />} />
          <Route path="aovivo" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
