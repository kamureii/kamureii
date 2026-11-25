// Locked v3 Sharp Tactical Obsidian & Crimson Design System
export const V3_THEME = {
  // Surfaces (never pure #000000)
  voidBg: "#08090C",
  recessedBg: "#0B0D12",
  slabBg: "#13161E",
  slabAltBg: "#0F1219",
  headerBg: "#1B1F2B",
  kpiNeutralBg: "#12151E",
  kpiCobaltBg: "#10192B",
  kpiCrimsonBg: "#241016",
  canaryBg: "#1B0D12",

  // Borders
  borderStrong: "rgba(255,255,255,0.16)",
  borderBase: "rgba(255,255,255,0.12)",
  borderSubtle: "rgba(255,255,255,0.08)",

  // Text roles (3 disciplined steps)
  textPrimary: "#F3F5F9",
  textSecondary: "#A5ACBC",
  textMuted: "#788092",
  textFaint: "#565E70",

  // Accents (Offense Crimson <-> Defense Cobalt)
  crimson: "#E52E3D",
  crimsonInk: "#FF5765",
  crimsonMid: "#9E2450",
  crimsonSub: "#D19AA0",
  crimsonBorder: "rgba(229,46,61,0.52)",

  cobalt: "#2563EB",
  cobaltBright: "#3B82F6",
  cobaltInk: "#60A5FA",
  cobaltSub: "#93B4F5",
  cobaltBorder: "rgba(59,130,246,0.42)",

  // Typography
  fontDisplay: "'Bahnschrift', 'DIN Alternate', 'Space Grotesk', 'Segoe UI', sans-serif",
  fontMono: "'Cascadia Mono', 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace",
} as const;

export function escXml(input: string): string {
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function formatUtcTimestamp(date: Date): string {
  return date.toISOString().replace("T", " ").slice(0, 19) + " UTC";
}

export function formatIncidentId(visitNumber: number, date: Date): string {
  const year = date.getUTCFullYear();
  return `INC-${year}-${String(Math.max(1, visitNumber)).padStart(5, "0")}`;
}
