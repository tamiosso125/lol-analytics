/** Tokens compartilhados dos gráficos (Recharts + cores do tema).
 *
 * Separado de components/chart.tsx (2026-07-13) — esse arquivo só pode
 * exportar componentes React pro Fast Refresh funcionar direito; exportar
 * essas constantes junto gerava warning do eslint-plugin-react-refresh. */

export const AXIS_TICK = { fill: "var(--muted-ink)", fontSize: 12 } as const;
export const GRID = { stroke: "var(--grid)", strokeDasharray: "0" } as const;
