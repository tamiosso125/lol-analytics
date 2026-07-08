import { describe, expect, it } from "vitest";

import { championDisplayName } from "@/lib/ddragon";

describe("championDisplayName", () => {
  it("mapeia os quirks conhecidos (nome interno diferente do nome de exibição)", () => {
    expect(championDisplayName("MonkeyKing")).toBe("Wukong");
    expect(championDisplayName("KSante")).toBe("K'Sante");
    expect(championDisplayName("Kaisa")).toBe("Kai'Sa");
    expect(championDisplayName("KhaZix")).toBe("Kha'Zix");
    expect(championDisplayName("ChoGath")).toBe("Cho'Gath");
    expect(championDisplayName("VelKoz")).toBe("Vel'Koz");
    expect(championDisplayName("RekSai")).toBe("Rek'Sai");
    expect(championDisplayName("BelVeth")).toBe("Bel'Veth");
    expect(championDisplayName("FiddleSticks")).toBe("Fiddlesticks");
    expect(championDisplayName("Renata")).toBe("Renata Glasc");
  });

  it("insere espaço antes de maiúscula no meio do nome (caso genérico)", () => {
    expect(championDisplayName("AurelionSol")).toBe("Aurelion Sol");
    expect(championDisplayName("MissFortune")).toBe("Miss Fortune");
    expect(championDisplayName("TwistedFate")).toBe("Twisted Fate");
  });

  it("nome de uma palavra só passa direto", () => {
    expect(championDisplayName("Ahri")).toBe("Ahri");
    expect(championDisplayName("Yasuo")).toBe("Yasuo");
  });
});
