-- Kamureii XDR Edge Sensor Schema (Zero PII)
-- Stores ONLY aggregate numeric counters and anonymous epoch timestamps for 60s burst correlation.

CREATE TABLE IF NOT EXISTS counters (
  metric TEXT PRIMARY KEY,
  value INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sliding_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'visit'
);

CREATE INDEX IF NOT EXISTS idx_sliding_events_ts ON sliding_events(ts);

INSERT OR IGNORE INTO counters (metric, value, updated_at) VALUES
  ('visits', 0, 0),
  ('benign', 0, 0),
  ('escalate', 0, 0),
  ('canary', 0, 0),
  ('light_mode', 0, 0);
