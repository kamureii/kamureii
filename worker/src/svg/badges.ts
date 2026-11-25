import type { ActionKind } from "../types";
import { escXml, V3_THEME as T } from "./theme";

export function renderActionButtonSvg(kind: ActionKind): string {
  const configs: Record<
    ActionKind,
    { label: string; tag: string; bg: string; border: string; rail: string; text: string; tagColor: string }
  > = {
    escalate: {
      label: "Escalate to Tier 2 · LinkedIn",
      tag: "ACTION",
      bg: T.crimson,
      border: T.crimson,
      rail: "#FF8B94",
      text: "#F8FAFC",
      tagColor: "#FFD4D8",
    },
    benign: {
      label: "Mark visit benign",
      tag: "TRIAGE",
      bg: T.headerBg,
      border: T.borderStrong,
      rail: T.cobaltBright,
      text: T.textPrimary,
      tagColor: T.cobaltInk,
    },
    isolate: {
      label: "Isolate & inspect telemetry",
      tag: "ACTIVE",
      bg: T.canaryBg,
      border: T.crimsonBorder,
      rail: T.crimson,
      text: T.textPrimary,
      tagColor: T.crimsonInk,
    },
  };

  const c = configs[kind];

  return `<svg xmlns="http://www.w3.org/2000/svg" width="286" height="40" viewBox="0 0 286 40" role="img" aria-label="${escXml(c.label)}">
  <style>
    .mono { font-family: ${T.fontMono}; }
  </style>
  <rect x="0.5" y="0.5" width="285" height="39" rx="2" fill="${c.bg}" stroke="${c.border}" stroke-width="1" />
  <rect x="0.5" y="0.5" width="3" height="39" fill="${c.rail}" />
  <text x="16" y="24" fill="${c.text}" font-size="12" class="mono">${escXml(c.label)}</text>
  <text x="272" y="24" text-anchor="end" fill="${c.tagColor}" font-size="10.5" class="mono">${c.tag}</text>
</svg>`;
}

export function renderCanaryBannerSvg(canaryCount: number, degraded = false): string {
  const countLabel = degraded ? "Standby" : `${canaryCount} times`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="880" height="74" viewBox="0 0 880 74" role="img" aria-label="Diagnostic Artifact Honeytoken T1552">
  <style>
    .disp { font-family: ${T.fontDisplay}; font-weight: 600; }
    .mono { font-family: ${T.fontMono}; font-variant-numeric: tabular-nums; }
  </style>
  <rect x="0.5" y="0.5" width="879" height="73" fill="${T.canaryBg}" stroke="${T.crimsonBorder}" stroke-width="1" />
  <rect x="0" y="0" width="3" height="74" fill="${T.crimson}" />
  <!-- Bottom reticle ticks -->
  <path d="M 0 65 L 0 74 L 9 74" fill="none" stroke="${T.crimson}" stroke-width="2" />
  <path d="M 880 65 L 880 74 L 871 74" fill="none" stroke="${T.cobaltBright}" stroke-width="2" />

  <text x="22" y="26" fill="${T.crimsonSub}" font-size="11" class="mono">Diagnostic artifact · internal symbol dump</text>
  <text x="22" y="51" fill="${T.textPrimary}" font-size="15" text-decoration="underline" class="mono">km_edr_unhook_poc_v2.dmp.enc</text>

  <line x1="590" y1="14" x2="590" y2="60" stroke="${T.crimsonBorder}" stroke-width="1" />
  <text x="608" y="27" fill="${T.crimsonSub}" font-size="11" class="mono">MITRE T1552 honeytoken</text>
  <text x="608" y="50" fill="${T.crimsonInk}" font-size="16" class="disp">Triggered ${escXml(countLabel)}</text>

  <rect x="794" y="24" width="68" height="26" rx="2" fill="${T.kpiCrimsonBg}" stroke="${T.crimsonBorder}" stroke-width="1" />
  <text x="828" y="41" text-anchor="middle" fill="${T.textPrimary}" font-size="11" class="mono">Inspect</text>
</svg>`;
}
