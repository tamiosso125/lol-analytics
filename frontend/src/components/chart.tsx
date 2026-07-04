/** Peças compartilhadas dos gráficos (Recharts + tokens do tema). */

export const AXIS_TICK = { fill: "var(--muted-ink)", fontSize: 12 } as const;
export const GRID = { stroke: "var(--grid)", strokeDasharray: "0" } as const;

type Formatter = (value: number, name: string) => string;

interface ChartTooltipProps {
  active?: boolean;
  payload?: { dataKey?: string | number; name?: string; value?: number; color?: string }[];
  label?: string | number;
  format?: Formatter;
}

export function ChartTooltip({ active, payload, label, format }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-md">
      {label != null && <p className="mb-1 font-medium">{label}</p>}
      {payload.map((p) => (
        <p key={p.dataKey as string} className="flex items-center gap-1.5 text-secondary-ink">
          <span
            className="inline-block size-2 rounded-full"
            style={{ background: p.color }}
          />
          {p.name}:{" "}
          <span className="font-medium text-foreground">
            {format ? format(p.value as number, p.name as string) : p.value}
          </span>
        </p>
      ))}
    </div>
  );
}
