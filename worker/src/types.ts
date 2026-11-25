export type ThemeMode = "dark" | "light";
export type DetectionSeverity = "LOW" | "HIGH" | "CRITICAL" | "DEGRADED";
export type ActionKind = "escalate" | "benign" | "isolate";

export interface TelemetryCounters {
  visits: number;
  benign: number;
  escalate: number;
  canary: number;
  lightMode: number;
}

export interface TelemetrySnapshot {
  incidentId: string;
  sensorName: string;
  username: string;
  timestampIso: string;
  theme: ThemeMode;
  viaCamo: boolean;
  proxyLabel: string;
  severity: DetectionSeverity;
  severityBadge: string;
  headline: string;
  description: string;
  posture: "Guarded" | "Elevated" | "Critical" | "Standby";
  postureSub: string;
  burstCount60s: number;
  burstThreshold: number;
  cadenceBuckets: number[]; // 8 chronological buckets over the last 60s
  counters: TelemetryCounters;
  degraded: boolean;
}
