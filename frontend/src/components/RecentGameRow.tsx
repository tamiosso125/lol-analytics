import { Link } from "react-router-dom";

import { championIcon } from "@/lib/ddragon";
import { winColor } from "@/lib/format";
import { cn } from "@/lib/utils";

/** Uma linha de "últimas partidas" — usada tanto na página de campeão
 * (sem ícone, já se sabe qual campeão) quanto na de jogador (com ícone,
 * já que o pool varia). Vira link para a partida quando `matchId` existe. */
export function RecentGameRow({
  matchId,
  championId,
  win,
  positionLabel,
  kills,
  deaths,
  assists,
  durationMin,
  date,
  extra,
}: {
  matchId: string;
  championId?: number;
  win: boolean;
  positionLabel: string;
  kills: number;
  deaths: number;
  assists: number;
  durationMin: number;
  date: string;
  /** Detalhe extra na cauda da linha (ex.: patch). */
  extra?: string;
}) {
  const className = cn(
    "flex items-center gap-3 rounded-md border-l-2 bg-foreground/5 px-3 py-1.5 text-xs",
    win ? "border-chart-1" : "border-chart-red",
  );
  const content = (
    <>
      {championId != null && (
        <img src={championIcon(championId)} alt="" className="size-6 rounded" />
      )}
      <span className={cn("w-14 font-medium", winColor(win))}>
        {win ? "Vitória" : "Derrota"}
      </span>
      <span className="w-16 text-secondary-ink">{positionLabel}</span>
      <span className="tabular-nums">
        {kills}/{deaths}/{assists}
      </span>
      <span className="ml-auto text-muted-ink tabular-nums">
        {durationMin} min{extra ? ` · ${extra}` : ""} ·{" "}
        {new Date(date).toLocaleDateString("pt-BR")}
      </span>
    </>
  );
  return (
    <Link to={`/partidas/${matchId}`} className={cn(className, "hover:bg-foreground/10")}>
      {content}
    </Link>
  );
}
