"""Renders the v3 Sysmon EventID=11 Activity Stream SVG."""

from __future__ import annotations

from scanner import ScanResult
from theme import V3Theme as T, esc, truncate


def render_sysmon_feed_svg(scan: ScanResult) -> str:
    events = scan.activities[:5]
    top_y = 32
    head_h = 34
    row_h = 38
    panel_h = head_h + max(1, len(events)) * row_h
    total_h = top_y + panel_h + 4

    status_label = "Sysmon EventID 11 · sensor online" if scan.sensor_online else "Sysmon EventID 11 · standby"
    status_color = T.COBALT_INK if scan.sensor_online else T.TEXT_MUTED

    rows_svg: list[str] = []
    for idx, ev in enumerate(events):
        y = top_y + head_h + idx * row_h
        bg = T.SLAB_BG if idx % 2 == 0 else T.SLAB_ALT_BG
        ev_color = T.COBALT_INK if ev.is_security else T.TEXT_MUTED
        scope_color = T.TEXT_SECONDARY if ev.is_security else T.TEXT_MUTED
        rows_svg.append(
            f"""  <rect x="1" y="{y}" width="878" height="{row_h}" fill="{bg}" />
  <line x1="1" y1="{y}" x2="879" y2="{y}" stroke="{T.BORDER_SUBTLE}" stroke-width="1" />
  <text x="18" y="{y + 23}" fill="{T.TEXT_MUTED}" font-size="11.5" class="mono">{esc(ev.timestamp)}</text>
  <text x="204" y="{y + 23}" fill="{ev_color}" font-size="11.5" class="mono">{esc(ev.event_id)}</text>
  <text x="348" y="{y + 23}" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">{esc(truncate(ev.repo, 38))}</text>
  <text x="862" y="{y + 23}" text-anchor="end" fill="{scope_color}" font-size="11.5" class="mono">{esc(truncate(ev.scope, 24))}</text>"""
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{total_h}" viewBox="0 0 880 {total_h}" role="img" aria-label="Sysmon EventID 11 GitHub Activity Stream">
  <title>Activity Stream — Sysmon EventID 11</title>
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>

  <text x="0" y="20" fill="{T.TEXT_PRIMARY}" font-size="17" letter-spacing="-0.2" class="disp">Activity stream</text>
  <text x="880" y="20" text-anchor="end" fill="{status_color}" font-size="11" class="mono">{esc(status_label)}</text>

  <rect x="0.5" y="{top_y + 0.5}" width="879" height="{panel_h - 1}" fill="{T.SLAB_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <rect x="1" y="{top_y + 1}" width="878" height="{head_h - 1}" fill="{T.HEADER_BG}" />
  <line x1="1" y1="{top_y + head_h}" x2="879" y2="{top_y + head_h}" stroke="{T.BORDER_BASE}" stroke-width="1" />

  <text x="18" y="{top_y + 21}" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Timestamp (UTC)</text>
  <text x="204" y="{top_y + 21}" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Event</text>
  <text x="348" y="{top_y + 21}" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Target repository</text>
  <text x="862" y="{top_y + 21}" text-anchor="end" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Scope</text>

{chr(10).join(rows_svg)}
</svg>
"""
