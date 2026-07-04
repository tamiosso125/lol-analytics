/** Ícones e nomes de exibição de campeões.
 *
 * Ícones via CommunityDragon (CDN público, sem versão manual): usar o
 * champion_id numérico evita divergências de grafia entre o nome interno
 * do match-v5 e o nome de arquivo do Data Dragon (ex.: FiddleSticks). */

export function championIcon(championId: number): string {
  return `https://cdn.communitydragon.org/latest/champion/${championId}/square`;
}

export function championSplash(championId: number): string {
  return `https://cdn.communitydragon.org/latest/champion/${championId}/splash-art/centered`;
}

/** Ícone de item via Data Dragon. Versão fixada: os ícones de item quase
 * não mudam entre patches, e o catálogo em data/items.json foi gerado
 * nesta mesma versão — manter as duas em sincronia se atualizar. */
export function itemIcon(itemId: number): string {
  return `https://ddragon.leagueoflegends.com/cdn/16.13.1/img/item/${itemId}.png`;
}

/** Esquema oficial de Summoner's Rift (arquivo do próprio jogo, servido
 * pelo CommunityDragon a partir do patch ATUAL — `latest`). É o mesmo
 * estilo esquemático (traços chapados, sem textura de terreno) que a
 * própria Riot usa para ilustrar mudanças de mapa em posts oficiais
 * (ex.: o dev blog de mudanças de mapa da temporada 2024) — não é uma
 * arte "antiga": o `map11.png` do Data Dragon é que fica travado numa
 * versão congelada (todas as versões testadas de 6.8 a 16.13 servem o
 * MESMO arquivo); este endpoint reflete o patch corrente de verdade.
 * PNG com transparência real nas áreas de selva — compõe sobre a cor de
 * fundo do próprio container, sem precisar de overlay escuro pesado.
 * Mesma convenção de coordenadas 0-1 já usada para os ícones: losango
 * do mapa preenche quase todo o quadrado, base azul no canto inferior-
 * esquerdo, vermelha no superior-direito. */
export const MINIMAP_URL =
  "https://raw.communitydragon.org/latest/game/assets/maps/info/map11/2dlevelminimap_base_baron1.png";

/** match-v5 usa o nome interno (MonkeyKing, KSante...); mapeia para o
 * nome de exibição. Casos não mapeados: espaço antes de maiúscula no
 * meio (AurelionSol -> Aurelion Sol). */
const DISPLAY_QUIRKS: Record<string, string> = {
  MonkeyKing: "Wukong",
  KSante: "K'Sante",
  Kaisa: "Kai'Sa",
  KhaZix: "Kha'Zix",
  ChoGath: "Cho'Gath",
  VelKoz: "Vel'Koz",
  RekSai: "Rek'Sai",
  BelVeth: "Bel'Veth",
  FiddleSticks: "Fiddlesticks",
  Renata: "Renata Glasc",
};

export function championDisplayName(internalName: string): string {
  const quirk = DISPLAY_QUIRKS[internalName];
  if (quirk) return quirk;
  return internalName.replace(/([a-z])([A-Z])/g, "$1 $2");
}

export const POSITION_LABELS: Record<string, string> = {
  TOP: "Topo",
  JUNGLE: "Selva",
  MIDDLE: "Meio",
  BOTTOM: "Atirador",
  UTILITY: "Suporte",
};
