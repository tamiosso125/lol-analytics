-- Schema inicial: plataforma de análise de dados de LoL (TCC)
-- Estratégia: guardar o JSON bruto (raw_*) para reprocessamento
-- e tabelas relacionais normalizadas para análise/ML.

CREATE TABLE IF NOT EXISTS players (
    puuid          VARCHAR(100) PRIMARY KEY,
    game_name      VARCHAR(64),
    tag_line       VARCHAR(16),
    tier           VARCHAR(16),      -- CHALLENGER, GRANDMASTER, MASTER...
    division       VARCHAR(4),
    league_points  INT,
    platform       VARCHAR(8),
    updated_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw_matches (
    match_id     VARCHAR(32) PRIMARY KEY,
    payload      JSONB NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw_timelines (
    match_id     VARCHAR(32) PRIMARY KEY REFERENCES raw_matches(match_id),
    payload      JSONB NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS matches (
    match_id      VARCHAR(32) PRIMARY KEY,
    platform_id   VARCHAR(8),
    queue_id      INT,               -- 420 = ranked solo
    game_version  VARCHAR(32),
    game_creation TIMESTAMPTZ,
    game_duration_s INT
);

CREATE TABLE IF NOT EXISTS teams (
    match_id     VARCHAR(32) REFERENCES matches(match_id),
    team_id      INT,                -- 100 = azul, 200 = vermelho
    win          BOOLEAN,
    barons       INT,
    dragons      INT,
    heralds      INT,
    towers       INT,
    inhibitors   INT,
    PRIMARY KEY (match_id, team_id)
);

CREATE TABLE IF NOT EXISTS participants (
    match_id        VARCHAR(32) REFERENCES matches(match_id),
    puuid           VARCHAR(100),
    team_id         INT,
    team_position   VARCHAR(12),     -- TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY
    champion_id     INT,
    champion_name   VARCHAR(32),
    kills           INT,
    deaths          INT,
    assists         INT,
    gold_earned     INT,
    cs_total        INT,             -- minions + neutros
    vision_score    INT,
    dmg_to_champions INT,
    win             BOOLEAN,
    PRIMARY KEY (match_id, puuid)
);

CREATE TABLE IF NOT EXISTS bans (
    match_id     VARCHAR(32) REFERENCES matches(match_id),
    team_id      INT,               -- time que baniu
    pick_turn    INT,
    champion_id  INT,               -- campeão banido (linhas com -1/sem ban não são gravadas)
    PRIMARY KEY (match_id, team_id, pick_turn)
);

-- Compras/vendas EFETIVAS de itens, extraídas dos eventos das timelines
-- (src/etl/load_items.py). ITEM_UNDO já é aplicado no ETL: a compra
-- desfeita não entra aqui — a tabela reflete o que o jogador de fato
-- manteve, não cada clique na loja.
CREATE TABLE IF NOT EXISTS item_events (
    id        BIGSERIAL PRIMARY KEY,
    match_id  VARCHAR(32) REFERENCES matches(match_id),
    puuid     VARCHAR(100),
    ts_ms     BIGINT,               -- timestamp do evento na partida (ms)
    item_id   INT,
    action    VARCHAR(4)            -- BUY | SELL
);

CREATE INDEX IF NOT EXISTS idx_item_events_match     ON item_events(match_id);
CREATE INDEX IF NOT EXISTS idx_item_events_item      ON item_events(item_id);
CREATE INDEX IF NOT EXISTS idx_item_events_puuid     ON item_events(puuid);

CREATE INDEX IF NOT EXISTS idx_bans_champion         ON bans(champion_id);
CREATE INDEX IF NOT EXISTS idx_participants_champion ON participants(champion_id);
CREATE INDEX IF NOT EXISTS idx_participants_puuid    ON participants(puuid);
CREATE INDEX IF NOT EXISTS idx_matches_version       ON matches(game_version);
