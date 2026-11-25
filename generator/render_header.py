"""Renders the v3 sharp top system header banner SVG."""

from __future__ import annotations

from typing import Any

from theme import V3Theme as T, esc


def render_header_svg(config: dict[str, Any]) -> str:
    prof = config.get("profile", {})
    username = str(prof.get("username", "kamureii"))
    full_name = str(prof.get("full_name", "Tran Quoc Hung"))
    org = str(prof.get("organization", "VNPT Cyber Immunity"))
    location = str(prof.get("location", "Hanoi, VN"))
    role = str(prof.get("role", "Endpoint Security & Detection Engineer"))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="68" viewBox="0 0 880 68" role="img" aria-label="{esc(full_name)} — {esc(role)}">
  <title>{esc(username)} — {esc(role)}</title>
  <defs>
    <linearGradient id="hdrVec" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{T.CRIMSON}" />
      <stop offset="50%" stop-color="{T.CRIMSON_MID}" />
      <stop offset="100%" stop-color="{T.COBALT}" />
    </linearGradient>
  </defs>
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; }}
  </style>

  <rect x="0.5" y="0.5" width="879" height="67" fill="{T.RECESSED_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <rect x="0" y="65" width="880" height="3" fill="url(#hdrVec)" />

  <!-- Left: Ring 0 badge + repo handle + title -->
  <rect x="20" y="16" width="58" height="22" rx="1" fill="{T.CELL_CRIMSON_BG}" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <text x="49" y="31" text-anchor="middle" fill="{T.CRIMSON_INK}" font-size="11" class="mono">Ring 0</text>

  <text x="92" y="32" fill="{T.TEXT_PRIMARY}" font-size="20" letter-spacing="-0.2" class="disp">{esc(full_name)}</text>
  <text x="92" y="51" fill="{T.TEXT_SECONDARY}" font-size="11.5" class="mono">{esc(role)}</text>

  <!-- Right: Org + Location + Handle -->
  <text x="860" y="30" text-anchor="end" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">{esc(org)}</text>
  <text x="860" y="49" text-anchor="end" fill="{T.TEXT_MUTED}" font-size="11.5" class="mono">{esc(username)} / README.md  |  {esc(location)}</text>
</svg>
"""
