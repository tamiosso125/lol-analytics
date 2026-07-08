import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "@/components/Layout";
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

export default function App() {
  return (
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
  );
}
