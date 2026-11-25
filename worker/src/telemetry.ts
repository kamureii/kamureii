import { formatIncidentId, formatUtcTimestamp } from "./svg/theme";
import type { DetectionSeverity, TelemetryCounters, TelemetrySnapshot, ThemeMode } from "./types";

const WINDOW_SECONDS = 60;
const RETENTION_SECONDS = 600;
const WRITE_THROTTLE_LIMIT = 25;
const BUCKET_COUNT = 8;

export function parseTheme(raw: string | null): ThemeMode {
  return raw?.toLowerCase() === "light" ? "light" : "dark";
}

export function detectCamoProxy(userAgent: string | null): { viaCamo: boolean; proxyLabel: string } {
  const ua = userAgent ?? "";
  if (/github-camo/i.test(ua)) {
    return { viaCamo: true, proxyLabel: "camo.githubusercontent.com" };
  }
  if (/camo/i.test(ua)) {
    return { viaCamo: true, proxyLabel: "camo-proxy" };
  }
  return { viaCamo: false, proxyLabel: "direct-edge-request" };
}

export function buildCadenceBuckets(timestamps: number[], nowSec: number): number[] {
  const buckets = new Array<number>(BUCKET_COUNT).fill(0);
  const start = nowSec - WINDOW_SECONDS;
  const step = WINDOW_SECONDS / BUCKET_COUNT;

  for (const ts of timestamps) {
    if (ts < start || ts > nowSec) continue;
    const idx = Math.min(BUCKET_COUNT - 1, Math.max(0, Math.floor((ts - start) / step)));
    const current = buckets[idx] ?? 0;
    buckets[idx] = current + 1;
  }
  return buckets;
}

export function classifyDetection(params: {
  theme: ThemeMode;
  burstCount60s: number;
  burstThreshold: number;
  viaCamo: boolean;
}): {
  severity: DetectionSeverity;
  severityBadge: string;
  headline: string;
  description: string;
  posture: "Guarded" | "Elevated" | "Critical";
  postureSub: string;
} {
  const { theme, burstCount60s, burstThreshold, viaCamo } = params;

  if (theme === "light") {
    return {
      severity: "CRITICAL",
      severityBadge: "Critical · T1562",
      headline: "Light mode appearance flagged under Impair Defenses",
      description:
        "Passive prefers-color-scheme: light beacon fired on profile load. Classified as operator anomaly under T1562.",
      posture: "Critical",
      postureSub: "Light mode active",
    };
  }

  if (burstCount60s >= burstThreshold) {
    return {
      severity: "HIGH",
      severityBadge: "High · T1595",
      headline: `Rapid profile enumeration (${burstCount60s} req / 60s)`,
      description: `D1 sliding-window query exceeded ${burstThreshold} hits/min threshold. Mapped to T1595 Active Scanning.`,
      posture: "Elevated",
      postureSub: "Rate limit armed",
    };
  }

  return {
    severity: "LOW",
    severityBadge: "Low severity",
    headline: viaCamo
      ? "External profile inspection intercepted via GitHub proxy"
      : "Direct edge telemetry inspection recorded",
    description: viaCamo
      ? "Edge sensor logged this read via github-camo (T1090 Proxy). Client IP remains masked by GitHub CDN."
      : "Direct edge inspection observed outside GitHub Camo proxy. Passive cadence within normal baseline.",
    posture: "Guarded",
    postureSub: "Baseline rate",
  };
}

export function buildDegradedSnapshot(params: {
  sensorName: string;
  username: string;
  theme: ThemeMode;
  viaCamo: boolean;
  proxyLabel: string;
  burstThreshold: number;
  now?: Date;
}): TelemetrySnapshot {
  const now = params.now ?? new Date();
  return {
    incidentId: "INC-FALLBACK-00000",
    sensorName: `${params.sensorName} · fallback`,
    username: params.username,
    timestampIso: formatUtcTimestamp(now),
    theme: params.theme,
    viaCamo: params.viaCamo,
    proxyLabel: params.proxyLabel,
    severity: "DEGRADED",
    severityBadge: "Degraded mode",
    headline: "Edge sensor running in stateless fallback mode",
    description:
      "Cloudflare D1 store temporarily unavailable. Serving deterministic SVG so profile renders cleanly.",
    posture: "Standby",
    postureSub: "D1 offline",
    burstCount60s: 0,
    burstThreshold: params.burstThreshold,
    cadenceBuckets: [0, 0, 0, 0, 0, 0, 0, 0],
    counters: { visits: 0, benign: 0, escalate: 0, canary: 0, lightMode: 0 },
    degraded: true,
  };
}

export async function readCounters(db: D1Database): Promise<TelemetryCounters> {
  const { results } = await db
    .prepare("SELECT metric, value FROM counters")
    .all<{ metric: string; value: number }>();

  const map = new Map<string, number>();
  for (const row of results) {
    map.set(row.metric, Number(row.value) || 0);
  }

  return {
    visits: map.get("visits") ?? 0,
    benign: map.get("benign") ?? 0,
    escalate: map.get("escalate") ?? 0,
    canary: map.get("canary") ?? 0,
    lightMode: map.get("light_mode") ?? 0,
  };
}

export async function incrementCounter(db: D1Database, metric: string): Promise<number> {
  const nowSec = Math.floor(Date.now() / 1000);
  await db
    .prepare(
      `INSERT INTO counters (metric, value, updated_at) VALUES (?, 1, ?)
       ON CONFLICT(metric) DO UPDATE SET value = value + 1, updated_at = excluded.updated_at`
    )
    .bind(metric, nowSec)
    .run();

  const row = await db
    .prepare("SELECT value FROM counters WHERE metric = ?")
    .bind(metric)
    .first<{ value: number }>();

  return Number(row?.value ?? 0);
}

export async function recordVisitAndBuildSnapshot(params: {
  db: D1Database;
  ctx: ExecutionContext;
  sensorName: string;
  username: string;
  theme: ThemeMode;
  userAgent: string | null;
  burstThreshold: number;
}): Promise<TelemetrySnapshot> {
  const now = new Date();
  const nowSec = Math.floor(now.getTime() / 1000);
  const { viaCamo, proxyLabel } = detectCamoProxy(params.userAgent);

  try {
    // 1. Check recent sliding window first so we can throttle abusive burst inserts
    const recentRows = await params.db
      .prepare("SELECT ts FROM sliding_events WHERE ts >= ? ORDER BY ts ASC LIMIT 100")
      .bind(nowSec - WINDOW_SECONDS)
      .all<{ ts: number }>();

    const recentTimestamps = recentRows.results.map((r) => Number(r.ts));
    const priorBurstCount = recentTimestamps.length;

    // 2. Atomic counter updates (+ bounded sliding event insert)
    const statements: D1PreparedStatement[] = [
      params.db
        .prepare(
          `INSERT INTO counters (metric, value, updated_at) VALUES ('visits', 1, ?)
           ON CONFLICT(metric) DO UPDATE SET value = value + 1, updated_at = excluded.updated_at`
        )
        .bind(nowSec),
    ];

    if (params.theme === "light") {
      statements.push(
        params.db
          .prepare(
            `INSERT INTO counters (metric, value, updated_at) VALUES ('light_mode', 1, ?)
             ON CONFLICT(metric) DO UPDATE SET value = value + 1, updated_at = excluded.updated_at`
          )
          .bind(nowSec)
      );
    }

    if (priorBurstCount < WRITE_THROTTLE_LIMIT) {
      statements.push(
        params.db
          .prepare("INSERT INTO sliding_events (ts, kind) VALUES (?, 'visit')")
          .bind(nowSec)
      );
      recentTimestamps.push(nowSec);
    }

    await params.db.batch(statements);

    // 3. Prune stale sliding_events off the hot path
    params.ctx.waitUntil(
      params.db
        .prepare("DELETE FROM sliding_events WHERE ts < ?")
        .bind(nowSec - RETENTION_SECONDS)
        .run()
        .catch((err) => {
          console.error(
            JSON.stringify({
              message: "sliding_events cleanup failed",
              error: err instanceof Error ? err.message : String(err),
            })
          );
        })
    );

    const counters = await readCounters(params.db);
    const burstCount60s = priorBurstCount + 1;
    const cadenceBuckets = buildCadenceBuckets(recentTimestamps, nowSec);
    const classification = classifyDetection({
      theme: params.theme,
      burstCount60s,
      burstThreshold: params.burstThreshold,
      viaCamo,
    });

    return {
      incidentId: formatIncidentId(counters.visits, now),
      sensorName: params.sensorName,
      username: params.username,
      timestampIso: formatUtcTimestamp(now),
      theme: params.theme,
      viaCamo,
      proxyLabel,
      ...classification,
      burstCount60s,
      burstThreshold: params.burstThreshold,
      cadenceBuckets,
      counters,
      degraded: false,
    };
  } catch (err) {
    console.error(
      JSON.stringify({
        message: "D1 telemetry error, returning degraded SVG",
        error: err instanceof Error ? err.message : String(err),
      })
    );
    return buildDegradedSnapshot({
      sensorName: params.sensorName,
      username: params.username,
      theme: params.theme,
      viaCamo,
      proxyLabel,
      burstThreshold: params.burstThreshold,
      now,
    });
  }
}
