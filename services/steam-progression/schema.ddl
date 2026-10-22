-- All identifiers and consent remain in private Cloudflare D1; NEVER publish in GitHub Pages JSON.
CREATE TABLE IF NOT EXISTS login_states (
  state_hash TEXT PRIMARY KEY,
  pkce_challenge TEXT NOT NULL,
  player_key TEXT NOT NULL,
  return_route TEXT NOT NULL DEFAULT 'players',
  expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS exchange_codes (
  code_hash TEXT PRIMARY KEY,
  steam_id TEXT NOT NULL,
  player_key TEXT NOT NULL,
  pkce_challenge TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  steam_id TEXT NOT NULL,
  player_key TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS consents (
  steam_id TEXT PRIMARY KEY,
  progression INTEGER NOT NULL DEFAULT 0,
  economy INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS progression_cache (
  steam_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  synced_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_account_idx ON sessions(steam_id);
