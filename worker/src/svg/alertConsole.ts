import type { TelemetrySnapshot } from "../types";
import { escXml, V3_THEME as T } from "./theme";

function buildCadencePaths(buckets: number[], burstThreshold: number): {
  linePath: string;
  areaPath: string;
  headX: number;
  headY: number;
  thresholdY: number;
} {
  const x0 = 36;
  const width = 508;
  const yTop = 294;
  const yBottom = 348;
  const height = yBottom - yTop;

  const maxVal = Math.max(burstThreshold + 1, ...buckets, 5);
  const count = Math.max(2, buckets.length);
  const stepX = width / (count - 1);

  const pts = buckets.map((val, i) => {
    const x = Math.round(x0 + i * stepX);
    const norm = Math.min(1, val / maxVal);
    const y = Math.round(yBottom - norm * height);
    return { x, y };
  });

  const linePath = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const last = pts[pts.length - 1] ?? { x: x0 + width, y: yBottom };
  const areaPath = `${linePath} L ${last.x} ${yBottom} L ${x0} ${yBottom} Z`;
  const thresholdY = Math.round(yBottom - Math.min(1, burstThreshold / maxVal) * height);

  return { linePath, areaPath, headX: last.x, headY: last.y, thresholdY };
}

function wrapText(text: string, maxChars: number): [string, string] {
  const clean = text.trim().replace(/\s+/g, " ");
  if (clean.length <= maxChars) return [clean, ""];
  const cut = clean.lastIndexOf(" ", maxChars);
  const idx = cut > 20 ? cut : maxChars;
  const line1 = clean.slice(0, idx).trim();
  const rest = clean.slice(idx).trim();
  const line2 = rest.length > maxChars ? rest.slice(0, maxChars - 3).trimEnd() + "..." : rest;
  return [line1, line2];
}

export function renderAlertConsoleSvg(snap: TelemetrySnapshot): string {
  const isAlert = snap.severity === "CRITICAL" || snap.severity === "HIGH";
  const sevFill = isAlert ? T.kpiCrimsonBg : T.headerBg;
  const sevStroke = isAlert ? T.crimsonBorder : T.borderStrong;
  const sevText = isAlert ? T.crimsonInk : T.textPrimary;

  const postureBg = isAlert ? T.kpiCrimsonBg : T.kpiNeutralBg;
  const postureText = isAlert ? T.crimsonInk : T.textPrimary;
  const postureSubColor = isAlert ? T.crimsonSub : T.textMuted;

  const velocityColor =
    snap.severity === "HIGH" ? T.crimsonInk : snap.degraded ? T.textMuted : T.cobaltInk;
  const velocityLabel = snap.degraded
    ? "Unavailable"
    : snap.burstCount60s >= snap.burstThreshold
      ? `${snap.burstCount60s} req / 60s (breached)`
      : `${snap.burstCount60s} req / 60s`;

  const themeNote = snap.degraded
    ? "Stateless pass-through"
    : snap.theme === "light"
      ? "Anomaly flagged (T1562)"
      : "Dark session verified";
  const themeNoteColor = snap.theme === "light" ? T.crimsonInk : T.textMuted;

  const benignPct =
    snap.counters.visits > 0
      ? `${((snap.counters.benign / snap.counters.visits) * 100).toFixed(1)}% triaged`
      : "0.0% triaged";

  const [descLine1, descLine2] = wrapText(snap.description, 70);
  const headlineSafe = snap.headline.length > 56 ? snap.headline.slice(0, 53) + "..." : snap.headline;
  const cadence = buildCadencePaths(snap.cadenceBuckets, snap.burstThreshold);
  const diodeClass = snap.degraded ? "" : 'class="live-diode"';
  const diodeFill = snap.degraded ? T.textMuted : T.crimson;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="880" height="388" viewBox="0 0 880 388" role="img" aria-label="Kamureii Live Edge Detection Console">
  <title>Kamureii Edge Detection Console — ${escXml(snap.incidentId)}</title>
  <defs>
    <linearGradient id="signalVector" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${T.crimson}" />
      <stop offset="48%" stop-color="${T.crimsonMid}" />
      <stop offset="100%" stop-color="${T.cobalt}" />
    </linearGradient>
    <linearGradient id="traceStroke" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${T.cobalt}" />
      <stop offset="55%" stop-color="${T.crimsonMid}" />
      <stop offset="100%" stop-color="${T.crimson}" />
    </linearGradient>
    <linearGradient id="traceFill" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${T.cobalt}" stop-opacity="0.16" />
      <stop offset="100%" stop-color="${T.crimson}" stop-opacity="0.26" />
    </linearGradient>
  </defs>

  <style>
    .disp { font-family: ${T.fontDisplay}; font-weight: 600; }
    .mono { font-family: ${T.fontMono}; font-variant-numeric: tabular-nums; }
    @keyframes diodePulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.28; }
    }
    .live-diode { animation: diodePulse 2.2s cubic-bezier(0.22, 1, 0.36, 1) infinite; }
  </style>

  <!-- Outer Sharp Frame (0px radius, Machined Carbon Left + Recessed Obsidian Right) -->
  <rect x="0.5" y="0.5" width="879" height="387" fill="${T.slabBg}" stroke="${T.borderStrong}" stroke-width="1" />
  <rect x="580" y="3" width="299" height="384" fill="${T.recessedBg}" />
  <line x1="580" y1="3" x2="580" y2="387" stroke="${T.borderStrong}" stroke-width="1" />

  <!-- Top 3px Red-to-Blue Offense-Defense Telemetry Horizon -->
  <rect x="0" y="0" width="880" height="3" fill="url(#signalVector)" />

  <!-- Architectural Bottom Reticle Brackets (Crimson Left / Cobalt Right) -->
  <path d="M 0 378 L 0 388 L 10 388" fill="none" stroke="${T.crimson}" stroke-width="2" />
  <path d="M 880 378 L 880 388 L 870 388" fill="none" stroke="${T.cobaltBright}" stroke-width="2" />

  <!-- ==================== LEFT 8 COLS: VERDICT + TRACE + CADENCE ==================== -->

  <!-- Top Status Strip -->
  <rect x="24" y="21" width="8" height="8" fill="${diodeFill}" ${diodeClass} />
  <text x="40" y="29" fill="${T.textPrimary}" font-size="12" class="mono">${escXml(snap.sensorName)}</text>
  <text x="218" y="29" fill="${T.textFaint}" font-size="12" class="mono">/</text>
  <text x="232" y="29" fill="${T.textSecondary}" font-size="12" class="mono">${escXml(snap.incidentId)}</text>

  <!-- Sharp Severity Tag -->
  <rect x="356" y="15" width="122" height="20" rx="1" fill="${sevFill}" stroke="${sevStroke}" stroke-width="1" />
  <text x="417" y="29" text-anchor="middle" fill="${sevText}" font-size="11" class="mono">${escXml(snap.severityBadge)}</text>

  <text x="556" y="29" text-anchor="end" fill="${T.textMuted}" font-size="11" class="mono">${escXml(snap.timestampIso.slice(11))}</text>
  <line x1="24" y1="45" x2="556" y2="45" stroke="${T.borderBase}" stroke-width="1" />

  <!-- Headline & Technical Description -->
  <text x="24" y="74" fill="${T.textPrimary}" font-size="19" letter-spacing="-0.2" class="disp">${escXml(headlineSafe)}</text>
  <text x="24" y="98" fill="${T.textSecondary}" font-size="11.5" class="mono">${escXml(descLine1)}</text>
  ${
    descLine2
      ? `<text x="24" y="115" fill="${T.textSecondary}" font-size="11.5" class="mono">${escXml(descLine2)}</text>`
      : ""
  }

  <!-- Recessed Session Lineage Well (#0B0D12) -->
  <rect x="24" y="132" width="532" height="114" fill="${T.recessedBg}" stroke="${T.borderBase}" stroke-width="1" />
  <rect x="24" y="132" width="532" height="26" fill="${T.headerBg}" stroke="${T.borderBase}" stroke-width="1" />
  <text x="36" y="149" fill="${T.textSecondary}" font-size="11" class="mono">Observed session lineage</text>
  <text x="544" y="149" text-anchor="end" fill="${T.textMuted}" font-size="11" class="mono">Passive edge trace · ${escXml(snap.timestampIso.slice(0, 10))}</text>

  <!-- Row 01 -->
  <text x="36" y="177" fill="${T.textFaint}" font-size="11" class="mono">01</text>
  <text x="62" y="177" fill="${T.textPrimary}" font-size="12" class="mono">visitor_browser.exe</text>
  <text x="218" y="177" fill="${T.textFaint}" font-size="11" class="mono">theme=</text>
  <text x="260" y="177" fill="${T.textSecondary}" font-size="11" class="mono">${escXml(snap.theme)}</text>
  <text x="544" y="177" text-anchor="end" fill="${themeNoteColor}" font-size="11" class="mono">${escXml(themeNote)}</text>
  <line x1="25" y1="187" x2="555" y2="187" stroke="${T.borderSubtle}" stroke-width="1" />

  <!-- Row 02 -->
  <text x="36" y="206" fill="${T.textFaint}" font-size="11" class="mono">02</text>
  <text x="62" y="206" fill="${T.textFaint}" font-size="12" class="mono">|-</text>
  <text x="86" y="206" fill="${T.textPrimary}" font-size="12" class="mono">${escXml(snap.proxyLabel)}</text>
  <rect x="492" y="193" width="52" height="18" rx="1" fill="${T.kpiCrimsonBg}" stroke="${T.crimsonBorder}" stroke-width="1" />
  <text x="518" y="206" text-anchor="middle" fill="${T.crimsonInk}" font-size="11" class="mono">${snap.viaCamo ? "T1090" : "EDGE"}</text>
  <line x1="25" y1="216" x2="555" y2="216" stroke="${T.borderSubtle}" stroke-width="1" />

  <!-- Row 03 -->
  <text x="36" y="236" fill="${T.textFaint}" font-size="11" class="mono">03</text>
  <text x="62" y="236" fill="${T.textFaint}" font-size="12" class="mono">+-</text>
  <text x="86" y="236" fill="${T.textPrimary}" font-size="12" class="mono">GET /${escXml(snap.username)}/README.md</text>
  <text x="544" y="236" text-anchor="end" fill="${velocityColor}" font-size="11" class="mono">${escXml(velocityLabel)}</text>

  <!-- Recessed 60s Cadence Oscilloscope Well (#0B0D12) -->
  <rect x="24" y="260" width="532" height="106" fill="${T.recessedBg}" stroke="${T.borderBase}" stroke-width="1" />
  <text x="36" y="280" fill="${T.textPrimary}" font-size="11" class="mono">Edge request cadence · 60s sliding window</text>
  <text x="544" y="280" text-anchor="end" fill="${T.crimsonInk}" font-size="11" class="mono">Burst threshold (${snap.burstThreshold})</text>

  <!-- Oscilloscope Gridlines -->
  <line x1="36" y1="${cadence.thresholdY}" x2="544" y2="${cadence.thresholdY}" stroke="${T.crimson}" stroke-opacity="0.38" stroke-dasharray="4 4" stroke-width="1" />
  <line x1="36" y1="322" x2="544" y2="322" stroke="${T.borderSubtle}" stroke-width="1" />
  <line x1="36" y1="348" x2="544" y2="348" stroke="${T.borderStrong}" stroke-width="1" />

  <!-- Signal Area + Stroke + Square Trace Head -->
  <path d="${cadence.areaPath}" fill="url(#traceFill)" />
  <path d="${cadence.linePath}" fill="none" stroke="url(#traceStroke)" stroke-width="2" stroke-linejoin="miter" />
  <rect x="${cadence.headX - 3}" y="${cadence.headY - 3}" width="6" height="6" fill="${T.crimson}" />

  <!-- ==================== RIGHT 4 COLS: 2x2 HIGH-CONTRAST KPI DECK ==================== -->

  <!-- Outer 1px Hairline Border for 2x2 Grid (x=600..856, y=24..264) -->
  <rect x="600" y="24" width="256" height="240" fill="${T.borderStrong}" />

  <!-- Cell 1: Detections (Machined Graphite) -->
  <rect x="601" y="25" width="126.5" height="118.5" fill="${T.kpiNeutralBg}" />
  <text x="615" y="48" fill="${T.textSecondary}" font-size="11" class="mono">Detections</text>
  <text x="615" y="92" fill="${T.textPrimary}" font-size="32" class="disp">${snap.counters.visits}</text>
  <text x="615" y="124" fill="${T.textMuted}" font-size="11" class="mono">All-time D1</text>

  <!-- Cell 2: Verified Benign (Cobalt Slate) -->
  <rect x="728.5" y="25" width="126.5" height="118.5" fill="${T.kpiCobaltBg}" />
  <text x="742" y="48" fill="${T.cobaltSub}" font-size="11" class="mono">Verified benign</text>
  <text x="742" y="92" fill="${T.textPrimary}" font-size="32" class="disp">${snap.counters.benign}</text>
  <text x="742" y="124" fill="${T.cobaltInk}" font-size="11" class="mono">${escXml(benignPct)}</text>

  <!-- Cell 3: Canary Hits (Crimson Slab) -->
  <rect x="601" y="144.5" width="126.5" height="118.5" fill="${T.kpiCrimsonBg}" />
  <text x="615" y="168" fill="${T.crimsonSub}" font-size="11" class="mono">Canary hits</text>
  <text x="615" y="212" fill="${T.crimsonInk}" font-size="32" class="disp">${snap.counters.canary}</text>
  <text x="615" y="244" fill="${T.crimsonSub}" font-size="11" class="mono">T1552 lure</text>

  <!-- Cell 4: Posture (Adaptive Alert Slab) -->
  <rect x="728.5" y="144.5" width="126.5" height="118.5" fill="${postureBg}" />
  <text x="742" y="168" fill="${isAlert ? T.crimsonSub : T.textSecondary}" font-size="11" class="mono">Posture</text>
  <text x="742" y="208" fill="${postureText}" font-size="24" class="disp">${escXml(snap.posture)}</text>
  <text x="742" y="244" fill="${postureSubColor}" font-size="11" class="mono">${escXml(snap.postureSub)}</text>

  <!-- Telemetry Compliance & Response Pointer Strip -->
  <rect x="600" y="280" width="256" height="86" fill="${T.slabBg}" stroke="${T.borderBase}" stroke-width="1" />
  <rect x="600" y="280" width="3" height="86" fill="${T.crimson}" />
  <text x="614" y="302" fill="${T.textPrimary}" font-size="11" class="mono">Telemetry audit</text>
  <text x="614" y="322" fill="${T.textSecondary}" font-size="11" class="mono">Light anomalies: ${snap.counters.lightMode}</text>
  <text x="614" y="340" fill="${T.textSecondary}" font-size="11" class="mono">Tier-2 escalations: ${snap.counters.escalate}</text>
  <text x="614" y="357" fill="${T.textMuted}" font-size="10.5" class="mono">Zero PII persisted · D1 edge</text>
</svg>`;
}
