-- Schema PostgreSQL pour le pipeline CDC Debezium
-- Cree automatiquement au demarrage du conteneur postgres-data
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Catalogue des sources
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(200) NOT NULL,
    url VARCHAR(500),
    qualite VARCHAR(50) DEFAULT 'officielle',
    actif BOOLEAN DEFAULT true,
    cree_le TIMESTAMP DEFAULT NOW()
);

-- Indicateurs economiques (table principale surveillee par Debezium)
CREATE TABLE IF NOT EXISTS indicators (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    label VARCHAR(300),
    value DOUBLE PRECISION,
    year INTEGER,
    source VARCHAR(100),
    source_detail VARCHAR(200),
    qualite VARCHAR(50) DEFAULT 'officielle',
    raw_json JSONB,
    ingested_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(code, year, source)
);

-- Journal des imports API
CREATE TABLE IF NOT EXISTS fetch_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    endpoint VARCHAR(500),
    status VARCHAR(20),
    records_count INTEGER,
    error_message TEXT,
    duration_ms INTEGER,
    fetched_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les requetes dashboards
CREATE INDEX IF NOT EXISTS idx_indicators_code ON indicators(code);
CREATE INDEX IF NOT EXISTS idx_indicators_source ON indicators(source);
CREATE INDEX IF NOT EXISTS idx_indicators_year ON indicators(year);
CREATE INDEX IF NOT EXISTS idx_indicators_code_year ON indicators(code, year);
CREATE INDEX IF NOT EXISTS idx_fetch_log_source ON fetch_log(source);

-- Vues materialisees pour les dashboards
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_indicators AS
SELECT DISTINCT ON (code)
    code, label, value, year, source, ingested_at
FROM indicators
ORDER BY code, year DESC;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_source_stats AS
SELECT
    source,
    COUNT(DISTINCT code) AS indicator_count,
    COUNT(*) AS total_records,
    MAX(year) AS latest_year,
    MIN(year) AS earliest_year,
    MAX(ingested_at) AS last_update
FROM indicators
GROUP BY source;

-- Sources par defaut
INSERT INTO sources (code, nom, url) VALUES
    ('WORLD_BANK', 'World Bank Open Data', 'https://api.worldbank.org/v2/'),
    ('HCP', 'Haut-Commissariat au Plan', 'https://www.hcp.ma/'),
    ('BAM', 'Bank Al-Maghrib', 'https://www.bkam.ma/'),
    ('FMI', 'Fonds Monetaire International', 'https://www.imf.org/')
ON CONFLICT (code) DO NOTHING;
