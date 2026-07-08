import { describe, expect, it } from "vitest";

import type { AskResult } from "@/lib/api";
import {
  deltaColor,
  formatCell,
  formatPct,
  humanizeColumn,
  isAdvisory,
  isEmptyResult,
  winColor,
} from "@/lib/format";

describe("formatPct", () => {
  it("formata fração como percentual pt-BR com 1 casa decimal", () => {
    expect(formatPct(0.4566)).toBe("45.7%");
    expect(formatPct(0)).toBe("0.0%");
    expect(formatPct(1)).toBe("100.0%");
  });
});

describe("winColor", () => {
  it("aceita boolean diretamente", () => {
    expect(winColor(true)).toBe("text-chart-1");
    expect(winColor(false)).toBe("text-chart-red");
  });

  it("usa limiar de 0.5 para número", () => {
    expect(winColor(0.5)).toBe("text-chart-1");
    expect(winColor(0.4999)).toBe("text-chart-red");
    expect(winColor(1)).toBe("text-chart-1");
    expect(winColor(0)).toBe("text-chart-red");
  });
});

describe("deltaColor", () => {
  it("usa limiar de 0, distinto de winColor", () => {
    expect(deltaColor(0)).toBe("text-chart-1");
    expect(deltaColor(0.01)).toBe("text-chart-1");
    expect(deltaColor(-0.01)).toBe("text-chart-red");
  });
});

describe("humanizeColumn", () => {
  it("troca underscore por espaço e capitaliza cada palavra", () => {
    expect(humanizeColumn("blue_win_rate")).toBe("Blue Win Rate");
    expect(humanizeColumn("champion")).toBe("Champion");
  });
});

describe("isEmptyResult", () => {
  it("true para zero linhas", () => {
    expect(isEmptyResult({ sql: "", columns: [], rows: [] })).toBe(true);
  });

  it("true quando toda linha é só null", () => {
    const result: AskResult = { sql: "", columns: ["a", "b"], rows: [[null, null]] };
    expect(isEmptyResult(result)).toBe(true);
  });

  it("false quando há pelo menos um valor não-nulo", () => {
    const result: AskResult = { sql: "", columns: ["a"], rows: [[42]] };
    expect(isEmptyResult(result)).toBe(false);
  });
});

describe("isAdvisory", () => {
  it("true só quando é a convenção SELECT '...' AS aviso", () => {
    expect(isAdvisory({ sql: "", columns: ["aviso"], rows: [] })).toBe(true);
    expect(isAdvisory({ sql: "", columns: ["Aviso"], rows: [] })).toBe(true);
  });

  it("false para resultado normal", () => {
    expect(isAdvisory({ sql: "", columns: ["champion", "win_rate"], rows: [] })).toBe(false);
  });
});

describe("formatCell", () => {
  it("null/undefined viram travessão", () => {
    expect(formatCell(null, "x")).toBe("—");
  });

  it("boolean vira Sim/Não", () => {
    expect(formatCell(true, "win")).toBe("Sim");
    expect(formatCell(false, "win")).toBe("Não");
  });

  it("coluna de taxa (0-1) vira percentual (vírgula decimal, locale pt-BR)", () => {
    expect(formatCell(0.437, "win_rate")).toBe("43,7%");
  });

  it("número fora de [0,1] em coluna de taxa não vira percentual", () => {
    expect(formatCell(15, "win_rate")).toBe("15");
  });

  it("inteiro comum usa separador de milhar pt-BR", () => {
    expect(formatCell(23133, "matches")).toBe("23.133");
  });

  it("string passa direto", () => {
    expect(formatCell("Ahri", "champion")).toBe("Ahri");
  });
});
