/** Mapa de calor da partida sobre o minimapa de Summoner's Rift.
 *
 * As posições vêm dos participantFrames da timeline (1 frame/minuto). O
 * calor acumula uma janela de minutos até o selecionado (mais recente =
 * mais intenso); os ícones mostram onde cada campeão estava exatamente
 * no minuto escolhido, e os ✕ marcam os abates da janela. */
import { useEffect, useRef, useState } from "react";

import type { MatchPositions } from "@/lib/api";
import { championDisplayName, championIcon, MINIMAP_URL } from "@/lib/ddragon";
import { cn } from "@/lib/utils";

const CANVAS = 512; // resolução interna do canvas (o CSS escala junto do mapa)
const WINDOW = 4; // minutos de histórico acumulados no calor
const RADIUS = 26;

export function MapHeatmap({
  data,
  minute,
  onMinuteChange,
}: {
  data: MatchPositions;
  /** minuto controlado pelo pai (para sincronizar com o card de objetivos) */
  minute: number;
  onMinuteChange: (m: number) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const maxMinute = Math.max(1, data.frames.length - 1);
  const [showKills, setShowKills] = useState(true);

  const { min, max_x, max_y } = data.bounds;
  // normaliza para [0,1]; y invertido (origem do jogo é o canto inferior esquerdo)
  const nx = (x: number) => (x - min) / (max_x - min);
  const ny = (y: number) => 1 - (y - min) / (max_y - min);

  const from = Math.max(1, minute - WINDOW);
  const frame = data.frames[Math.min(minute, maxMinute)];
  const kills = data.kills.filter((k) => k.minute >= from && k.minute <= minute);

  useEffect(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, CANVAS, CANVAS);
    ctx.globalCompositeOperation = "lighter"; // sobreposição soma = calor
    for (const fr of data.frames) {
      if (fr.minute < from || fr.minute > minute) continue;
      const recency = 0.35 + 0.65 * ((fr.minute - from) / Math.max(1, minute - from));
      for (const p of fr.players) {
        const x = nx(p.x) * CANVAS;
        const y = ny(p.y) * CANVAS;
        const rgb = p.team_id === 100 ? "58,135,229" : "230,103,103";
        const g = ctx.createRadialGradient(x, y, 0, x, y, RADIUS);
        g.addColorStop(0, `rgba(${rgb},${0.3 * recency})`);
        g.addColorStop(1, `rgba(${rgb},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, RADIUS, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, minute, from]);

  return (
    <div className="space-y-3">
      <div
        className="relative aspect-square w-full overflow-hidden rounded-xl border border-border"
        style={{ backgroundColor: "#1f1c12" }}
      >
        {/* o PNG tem transparência real nas áreas de selva — a cor de
            fundo acima é que dá o "chão escuro", sem precisar de overlay */}
        <img src={MINIMAP_URL} alt="Summoner's Rift" className="absolute inset-0 size-full" />
        <canvas
          ref={canvasRef}
          width={CANVAS}
          height={CANVAS}
          className="absolute inset-0 size-full"
        />
        {showKills &&
          kills.map((k, i) => (
            <span
              key={i}
              title={`Abate aos ${k.minute} min`}
              className={cn(
                "absolute -translate-x-1/2 -translate-y-1/2 text-[13px] font-bold leading-none drop-shadow-[0_1px_2px_rgba(0,0,0,0.9)]",
                k.killer_team === 100 ? "text-[#7db8f5]" : "text-[#f5a3a3]",
              )}
              style={{ left: `${nx(k.x) * 100}%`, top: `${ny(k.y) * 100}%` }}
            >
              ✕
            </span>
          ))}
        {frame?.players.map((p) => (
          <img
            key={p.champion}
            src={championIcon(p.champion_id)}
            alt={championDisplayName(p.champion)}
            title={`${championDisplayName(p.champion)}${p.level ? ` — nível ${p.level}` : ""}`}
            className={cn(
              "absolute size-7 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 shadow-md",
              p.team_id === 100 ? "ring-[#3987e5]" : "ring-[#e66767]",
            )}
            style={{ left: `${nx(p.x) * 100}%`, top: `${ny(p.y) * 100}%` }}
          />
        ))}
      </div>

      <div className="flex items-center gap-3">
        <input
          type="range"
          min={1}
          max={maxMinute}
          value={Math.min(minute, maxMinute)}
          onChange={(e) => onMinuteChange(Number(e.target.value))}
          className="flex-1 accent-accent"
          aria-label="Minuto da partida"
        />
        <span className="w-16 text-right text-sm font-medium tabular-nums">
          {minute} min
        </span>
        <label className="flex items-center gap-1.5 text-xs text-secondary-ink">
          <input
            type="checkbox"
            checked={showKills}
            onChange={(e) => setShowKills(e.target.checked)}
            className="accent-accent"
          />
          Abates
        </label>
      </div>
      <p className="text-xs leading-relaxed text-muted-ink">
        O calor acumula as posições dos últimos {WINDOW + 1} minutos até o selecionado
        (mais recente = mais intenso); os ícones marcam onde cada campeão estava
        exatamente nesse minuto e ✕ os abates da janela. Arraste para ver a partida se
        mover: rotas separadas no early, agrupamentos em objetivos no mid/late.
      </p>
    </div>
  );
}
