"""Renders deterministic v3 static fallback SVGs matching the Cloudflare Worker output 1:1.

Used before the user sets `edge.worker_url` in profile.config.yml (and for local visual verification).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from theme import V3Theme as T, esc


def render_static_alert_console_svg(config: dict[str, Any]) -> str:
    username = str(config.get("profile", {}).get("username", "kamureii"))
    sensor = str(config.get("edge", {}).get("sensor_name", "kamureii-xdr-edge.sys"))
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="388" viewBox="0 0 880 388" role="img" aria-label="Kamureii Edge Detection Console">
  <title>Kamureii Edge Detection Console — Armed</title>
  <defs>
    <linearGradient id="signalVector" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{T.CRIMSON}" />
      <stop offset="48%" stop-color="{T.CRIMSON_MID}" />
      <stop offset="100%" stop-color="{T.COBALT}" />
    </linearGradient>
    <linearGradient id="traceStroke" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{T.COBALT}" />
      <stop offset="55%" stop-color="{T.CRIMSON_MID}" />
      <stop offset="100%" stop-color="{T.CRIMSON}" />
    </linearGradient>
    <linearGradient id="traceFill" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{T.COBALT}" stop-opacity="0.16" />
      <stop offset="100%" stop-color="{T.CRIMSON}" stop-opacity="0.26" />
    </linearGradient>
  </defs>
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; font-variant-numeric: tabular-nums; }}
    @keyframes diodePulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.28; }}
    }}
    .live-diode {{ animation: diodePulse 2.2s cubic-bezier(0.22, 1, 0.36, 1) infinite; }}
  </style>

  <rect x="0.5" y="0.5" width="879" height="387" fill="{T.SLAB_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <rect x="580" y="3" width="299" height="384" fill="{T.RECESSED_BG}" />
  <line x1="580" y1="3" x2="580" y2="387" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <rect x="0" y="0" width="880" height="3" fill="url(#signalVector)" />

  <path d="M 0 378 L 0 388 L 10 388" fill="none" stroke="{T.CRIMSON}" stroke-width="2" />
  <path d="M 880 378 L 880 388 L 870 388" fill="none" stroke="{T.COBALT_BRIGHT}" stroke-width="2" />

  <rect x="24" y="21" width="8" height="8" fill="{T.CRIMSON}" class="live-diode" />
  <text x="40" y="29" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">{esc(sensor)}</text>
  <text x="218" y="29" fill="{T.TEXT_FAINT}" font-size="12" class="mono">/</text>
  <text x="232" y="29" fill="{T.TEXT_SECONDARY}" font-size="12" class="mono">INC-2026-ARMED</text>

  <rect x="356" y="15" width="122" height="20" rx="1" fill="{T.HEADER_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <text x="417" y="29" text-anchor="middle" fill="{T.TEXT_PRIMARY}" font-size="11" class="mono">Low severity</text>
  <text x="556" y="29" text-anchor="end" fill="{T.TEXT_MUTED}" font-size="11" class="mono">{esc(now_str[11:])}</text>
  <line x1="24" y1="45" x2="556" y2="45" stroke="{T.BORDER_BASE}" stroke-width="1" />

  <text x="24" y="74" fill="{T.TEXT_PRIMARY}" font-size="19" letter-spacing="-0.2" class="disp">External profile inspection intercepted via GitHub proxy</text>
  <text x="24" y="98" fill="{T.TEXT_SECONDARY}" font-size="11.5" class="mono">Edge sensor ready for Cloudflare D1 live binding (github-camo -&gt; T1090).</text>
  <text x="24" y="115" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Deploy worker/ and set edge.worker_url in profile.config.yml to go live.</text>

  <rect x="24" y="132" width="532" height="114" fill="{T.RECESSED_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <rect x="24" y="132" width="532" height="26" fill="{T.HEADER_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <text x="36" y="149" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Observed session lineage</text>
  <text x="544" y="149" text-anchor="end" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Passive edge trace · {esc(now_str[:10])}</text>

  <text x="36" y="177" fill="{T.TEXT_FAINT}" font-size="11" class="mono">01</text>
  <text x="62" y="177" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">visitor_browser.exe</text>
  <text x="218" y="177" fill="{T.TEXT_FAINT}" font-size="11" class="mono">theme=</text>
  <text x="260" y="177" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">dark</text>
  <text x="544" y="177" text-anchor="end" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Dark session verified</text>
  <line x1="25" y1="187" x2="555" y2="187" stroke="{T.BORDER_SUBTLE}" stroke-width="1" />

  <text x="36" y="206" fill="{T.TEXT_FAINT}" font-size="11" class="mono">02</text>
  <text x="62" y="206" fill="{T.TEXT_FAINT}" font-size="12" class="mono">|-</text>
  <text x="86" y="206" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">camo.githubusercontent.com</text>
  <rect x="492" y="193" width="52" height="18" rx="1" fill="{T.KPI_CRIMSON_BG}" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <text x="518" y="206" text-anchor="middle" fill="{T.CRIMSON_INK}" font-size="11" class="mono">T1090</text>
  <line x1="25" y1="216" x2="555" y2="216" stroke="{T.BORDER_SUBTLE}" stroke-width="1" />

  <text x="36" y="236" fill="{T.TEXT_FAINT}" font-size="11" class="mono">03</text>
  <text x="62" y="236" fill="{T.TEXT_FAINT}" font-size="12" class="mono">+-</text>
  <text x="86" y="236" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">GET /{esc(username)}/README.md</text>
  <text x="544" y="236" text-anchor="end" fill="{T.COBALT_INK}" font-size="11" class="mono">1 req / 60s</text>

  <rect x="24" y="260" width="532" height="106" fill="{T.RECESSED_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <text x="36" y="280" fill="{T.TEXT_PRIMARY}" font-size="11" class="mono">Edge request cadence · 60s sliding window</text>
  <text x="544" y="280" text-anchor="end" fill="{T.CRIMSON_INK}" font-size="11" class="mono">Burst threshold (5)</text>
  <line x1="36" y1="302" x2="544" y2="302" stroke="{T.CRIMSON}" stroke-opacity="0.38" stroke-dasharray="4 4" stroke-width="1" />
  <line x1="36" y1="324" x2="544" y2="324" stroke="{T.BORDER_SUBTLE}" stroke-width="1" />
  <line x1="36" y1="348" x2="544" y2="348" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <path d="M 36 342 L 109 342 L 181 336 L 254 342 L 326 332 L 399 338 L 471 334 L 544 328 L 544 348 L 36 348 Z" fill="url(#traceFill)" />
  <path d="M 36 342 L 109 342 L 181 336 L 254 342 L 326 332 L 399 338 L 471 334 L 544 328" fill="none" stroke="url(#traceStroke)" stroke-width="2" stroke-linejoin="miter" />
  <rect x="541" y="325" width="6" height="6" fill="{T.CRIMSON}" />

  <!-- Right 2x2 High-Contrast KPI Deck -->
  <rect x="600" y="24" width="256" height="240" fill="{T.BORDER_STRONG}" />
  <rect x="601" y="25" width="126.5" height="118.5" fill="{T.KPI_NEUTRAL_BG}" />
  <text x="615" y="48" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Detections</text>
  <text x="615" y="90" fill="{T.TEXT_PRIMARY}" font-size="26" class="disp">ARMED</text>
  <text x="615" y="124" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Edge D1 ready</text>

  <rect x="728.5" y="25" width="126.5" height="118.5" fill="{T.KPI_COBALT_BG}" />
  <text x="742" y="48" fill="{T.COBALT_SUB}" font-size="11" class="mono">Verified benign</text>
  <text x="742" y="90" fill="{T.TEXT_PRIMARY}" font-size="26" class="disp">READY</text>
  <text x="742" y="124" fill="{T.COBALT_INK}" font-size="11" class="mono">Triage armed</text>

  <rect x="601" y="144.5" width="126.5" height="118.5" fill="{T.KPI_CRIMSON_BG}" />
  <text x="615" y="168" fill="{T.CRIMSON_SUB}" font-size="11" class="mono">Canary hits</text>
  <text x="615" y="210" fill="{T.CRIMSON_INK}" font-size="26" class="disp">T1552</text>
  <text x="615" y="244" fill="{T.CRIMSON_SUB}" font-size="11" class="mono">Lure deployed</text>

  <rect x="728.5" y="144.5" width="126.5" height="118.5" fill="{T.KPI_NEUTRAL_BG}" />
  <text x="742" y="168" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Posture</text>
  <text x="742" y="208" fill="{T.TEXT_PRIMARY}" font-size="24" class="disp">Guarded</text>
  <text x="742" y="244" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Static preview</text>

  <rect x="600" y="280" width="256" height="86" fill="{T.SLAB_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <rect x="600" y="280" width="3" height="86" fill="{T.CRIMSON}" />
  <text x="614" y="302" fill="{T.TEXT_PRIMARY}" font-size="11" class="mono">Telemetry audit</text>
  <text x="614" y="322" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Rules: T1090 / T1562 / T1595</text>
  <text x="614" y="340" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Honeytoken: T1552 canary</text>
  <text x="614" y="357" fill="{T.TEXT_MUTED}" font-size="10.5" class="mono">Zero PII persisted · D1 edge</text>
</svg>
"""


def render_static_action_svg(kind: str) -> str:
    specs = {
        "escalate": ("Escalate to Tier 2 · LinkedIn", "ACTION", T.CRIMSON, T.CRIMSON, "#FF8B94", "#F8FAFC", "#FFD4D8"),
        "benign": ("Mark visit benign", "TRIAGE", T.HEADER_BG, T.BORDER_STRONG, T.COBALT_BRIGHT, T.TEXT_PRIMARY, T.COBALT_INK),
        "isolate": ("Isolate & inspect telemetry", "ACTIVE", T.CANARY_BG, T.CRIMSON_BORDER, T.CRIMSON, T.TEXT_PRIMARY, T.CRIMSON_INK),
    }
    label, tag, bg, border, rail, text, tag_col = specs[kind]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="286" height="40" viewBox="0 0 286 40" role="img" aria-label="{esc(label)}">
  <style>.mono {{ font-family: {T.FONT_MONO}; }}</style>
  <rect x="0.5" y="0.5" width="285" height="39" rx="2" fill="{bg}" stroke="{border}" stroke-width="1" />
  <rect x="0.5" y="0.5" width="3" height="39" fill="{rail}" />
  <text x="16" y="24" fill="{text}" font-size="12" class="mono">{esc(label)}</text>
  <text x="272" y="24" text-anchor="end" fill="{tag_col}" font-size="10.5" class="mono">{tag}</text>
</svg>
"""


def render_static_canary_svg() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="74" viewBox="0 0 880 74" role="img" aria-label="Diagnostic Artifact Honeytoken T1552">
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>
  <rect x="0.5" y="0.5" width="879" height="73" fill="{T.CANARY_BG}" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <rect x="0" y="0" width="3" height="74" fill="{T.CRIMSON}" />
  <path d="M 0 65 L 0 74 L 9 74" fill="none" stroke="{T.CRIMSON}" stroke-width="2" />
  <path d="M 880 65 L 880 74 L 871 74" fill="none" stroke="{T.COBALT_BRIGHT}" stroke-width="2" />

  <text x="22" y="26" fill="{T.CRIMSON_SUB}" font-size="11" class="mono">Diagnostic artifact · internal symbol dump</text>
  <text x="22" y="51" fill="{T.TEXT_PRIMARY}" font-size="15" text-decoration="underline" class="mono">km_edr_unhook_poc_v2.dmp.enc</text>

  <line x1="590" y1="14" x2="590" y2="60" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <text x="608" y="27" fill="{T.CRIMSON_SUB}" font-size="11" class="mono">MITRE T1552 honeytoken</text>
  <text x="608" y="50" fill="{T.CRIMSON_INK}" font-size="16" class="disp">Sensor armed</text>

  <rect x="794" y="24" width="68" height="26" rx="2" fill="{T.KPI_CRIMSON_BG}" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <text x="828" y="41" text-anchor="middle" fill="{T.TEXT_PRIMARY}" font-size="11" class="mono">Inspect</text>
</svg>
"""
