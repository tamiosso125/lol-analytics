/** Formatação de valores/colunas de resultado de SQL gerado dinamicamente
 * (nomes de coluna não são conhecidos com antecedência — a formatação
 * precisa ser inferida a partir do nome e do valor). */
import type { AskResult } from "@/lib/api";

/** true quando o resultado não tem linhas, ou tem só uma linha com todos
 * os valores nulos (ex.: AVG(...) sem GROUP BY sobre zero linhas — a
 * query roda sem erro mas não representa nenhum dado real). */
export function isEmptyResult(result: AskResult): boolean {
  if (result.rows.length === 0) return true;
  return result.rows.every((row) => row.every((cell) => cell === null));
}

/** true quando o LLM sinalizou que não pode responder com o schema
 * disponível — convenção definida em schema_context.py: SELECT '...' AS aviso. */
export function isAdvisory(result: AskResult): boolean {
  return result.columns.length === 1 && result.columns[0].toLowerCase() === "aviso";
}

export function humanizeColumn(name: string): string {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Formata uma fração (0-1) como percentual pt-BR — usado em todas as
 * páginas que mostram win rate/taxas. */
export function formatPct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

/** Classe de cor para uma taxa/resultado: verde a partir de 50% (ou vitória),
 * vermelho abaixo — convenção visual repetida em todas as páginas de stats. */
export function winColor(v: number | boolean): string {
  const isWin = typeof v === "boolean" ? v : v >= 0.5;
  return isWin ? "text-chart-1" : "text-chart-red";
}

/** Classe de cor para um delta (diferença que pode ser negativa): verde
 * quando >= 0, vermelho quando < 0 — distinto de winColor (limiar 0, não 0.5). */
export function deltaColor(v: number): string {
  return v >= 0 ? "text-chart-1" : "text-chart-red";
}

const RATE_COLUMN = /(rate|_pct|percent)/i;

export function formatCell(value: string | number | boolean | null, column: string): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  if (typeof value === "number") {
    if (RATE_COLUMN.test(column) && value >= 0 && value <= 1) {
      return `${(value * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;
    }
    if (Number.isInteger(value)) return value.toLocaleString("pt-BR");
    return value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  }
  return String(value);
}
