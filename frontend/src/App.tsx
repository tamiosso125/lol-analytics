import { Route, Routes } from "react-router-dom";

import { Layout } from "@/components/Layout";
import { ChampionDetail } from "@/pages/ChampionDetail";
import { Champions } from "@/pages/Champions";
import { Dashboard } from "@/pages/Dashboard";
import { Explain } from "@/pages/Explain";
import { Home } from "@/pages/Home";
import { MatchDetail } from "@/pages/MatchDetail";
import { Matches } from "@/pages/Matches";
import { Nlq } from "@/pages/Nlq";
import { Predict } from "@/pages/Predict";
import { TeamBuilder } from "@/pages/TeamBuilder";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="campeoes" element={<Champions />} />
        <Route path="campeoes/:name" element={<ChampionDetail />} />
        <Route path="partidas" element={<Matches />} />
        <Route path="partidas/:id" element={<MatchDetail />} />
        <Route path="consulta" element={<Nlq />} />
        <Route path="predicao" element={<Predict />} />
        <Route path="montar" element={<TeamBuilder />} />
        <Route path="explicabilidade" element={<Explain />} />
      </Route>
    </Routes>
  );
}
