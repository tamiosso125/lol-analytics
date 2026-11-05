/** Tela de consulta com o roteamento solo queue × competitivo.
 *
 * `api.ask` e `api.explain` são simulados. Confere o que o plano prometeu
 * (docs/plano_roteamento_nlq.md): todo resultado mostra de qual base veio; pergunta
 * ambígua mostra as duas, lado a lado, e a falha de uma base não esconde a outra; a
 * continuação envia ao backend a base de cada resultado. */
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { AskResult } from "@/lib/api";
import { renderPage } from "@/test/renderPage";

const ask = vi.fn();
const explain = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api")>();
  return { ...actual, api: new Proxy({}, { get: (_, k) => (k === "ask" ? ask : explain) }) as typeof actual.api };
});

import { Nlq } from "@/pages/Nlq";

const SOLO = {
  base: "solo" as const,
  sql: "SELECT COUNT(*) AS n FROM matches",
  columns: ["n"],
  rows: [[41063]],
  tentativas: 1,
  erro: null,
};
const PRO = {
  base: "competitivo" as const,
  sql: "SELECT COUNT(DISTINCT game_id) AS n FROM pro_games",
  columns: ["n"],
  rows: [[99259]],
  tentativas: 1,
  erro: null,
};

function resposta(partes: Partial<AskResult> & Pick<AskResult, "resultados">): AskResult {
  const primeiro = partes.resultados!.find((r) => !r.erro)!;
  return {
    sql: primeiro.sql ?? "",
    columns: primeiro.columns,
    rows: primeiro.rows,
    base: "ambos",
    roteamento: { classe: "ambos", origem: "modelo" },
    ...partes,
  };
}

async function perguntar(texto: string) {
  fireEvent.change(screen.getByPlaceholderText(/Ex\.: qual posição/), { target: { value: texto } });
  fireEvent.click(screen.getByRole("button", { name: /Perguntar/ }));
}

beforeEach(() => {
  ask.mockReset();
  explain.mockReset();
  explain.mockResolvedValue({ explanation: "explicação simulada" });
});

describe("Nlq: roteamento solo queue × competitivo", () => {
  it("uma base: mostra o selo e não avisa que são duas", async () => {
    ask.mockResolvedValueOnce(
      resposta({
        resultados: [SOLO],
        base: "solo",
        roteamento: { classe: "solo", origem: "regras" },
      }),
    );
    renderPage(<Nlq />);
    await perguntar("qual o win rate do time azul?");
    expect(await screen.findByText("Solo queue", { selector: "span" })).toBeInTheDocument();
    expect(screen.queryByText("Competitivo", { selector: "span" })).not.toBeInTheDocument();
    expect(screen.queryByText(/não diz de qual base/)).not.toBeInTheDocument();
    expect(await screen.findByText("41.063")).toBeInTheDocument();
  });

  it("ambígua: mostra as duas bases lado a lado, cada uma com o selo", async () => {
    ask.mockResolvedValueOnce(resposta({ resultados: [SOLO, PRO] }));
    renderPage(<Nlq />);
    await perguntar("quantas partidas existem no banco?");
    expect(await screen.findByText(/não diz de qual base/)).toBeInTheDocument();
    expect(screen.getByText("Solo queue", { selector: "span" })).toBeInTheDocument();
    expect(screen.getByText("Competitivo", { selector: "span" })).toBeInTheDocument();
    expect(screen.getByText("41.063")).toBeInTheDocument();
    expect(screen.getByText("99.259")).toBeInTheDocument();
    // com duas bases a explicação fica sob demanda: nada foi buscado ainda
    expect(explain).not.toHaveBeenCalled();
  });

  it("uma base falha, a outra aparece", async () => {
    const falha = {
      ...PRO,
      sql: "SELECT x",
      columns: [],
      rows: [],
      tentativas: null,
      erro: { tipo: "execucao" as const, message: "A consulta gerada falhou ao executar no banco.", sql: "SELECT x", cause: "coluna x não existe" },
    };
    ask.mockResolvedValueOnce(resposta({ resultados: [SOLO, falha] }));
    renderPage(<Nlq />);
    await perguntar("quantas partidas existem no banco?");
    expect(await screen.findByText("41.063")).toBeInTheDocument();
    expect(screen.getByText(/falhou ao executar no banco/)).toBeInTheDocument();
    expect(screen.getByText("Competitivo", { selector: "span" })).toBeInTheDocument();
  });

  it("recusa de uma base aparece como aviso naquela base", async () => {
    const recusa = {
      ...PRO,
      sql: "SELECT 'não é possível responder: falta a coluna' AS aviso",
      columns: ["aviso"],
      rows: [["não é possível responder: falta a coluna"]],
    };
    ask.mockResolvedValueOnce(resposta({ resultados: [SOLO, recusa] }));
    renderPage(<Nlq />);
    await perguntar("quais jogadores fizeram pentakill?");
    expect(await screen.findByText(/não é possível responder: falta a coluna/)).toBeInTheDocument();
    expect(screen.getByText("41.063")).toBeInTheDocument();
  });

  it("a continuação envia uma entrada de histórico por base", async () => {
    ask.mockResolvedValueOnce(resposta({ resultados: [SOLO, PRO] }));
    ask.mockResolvedValueOnce(
      resposta({
        resultados: [PRO],
        base: "competitivo",
        roteamento: { classe: "competitivo", origem: "regras" },
      }),
    );
    renderPage(<Nlq />);
    await perguntar("quantas partidas existem no banco?");
    await screen.findByText("99.259");
    const cartao = screen.getByPlaceholderText("Continuar esta consulta…");
    fireEvent.change(cartao, { target: { value: "e só de 2026?" } });
    fireEvent.keyDown(cartao, { key: "Enter" });
    await waitFor(() => expect(ask).toHaveBeenCalledTimes(2));
    const [, historico] = ask.mock.calls[1];
    expect(historico).toEqual([
      { question: "quantas partidas existem no banco?", sql: SOLO.sql, base: "solo" },
      { question: "quantas partidas existem no banco?", sql: PRO.sql, base: "competitivo" },
    ]);
  });

  it("a página mostra a dica de como escolher a base", () => {
    renderPage(<Nlq />);
    const dica = screen.getByText(/Dica:/);
    expect(within(dica).getByText(/no competitivo/, { exact: false })).toBeInTheDocument();
  });
});
