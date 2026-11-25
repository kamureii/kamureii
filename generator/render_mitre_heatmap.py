"""Renders the v3 high-contrast MITRE ATT&CK Coverage Heatmap SVG."""

from __future__ import annotations

from scanner import TACTIC_CATALOG, ScanResult
from theme import V3Theme as T, esc


def _tier_style(tier: str) -> tuple[str, str, str, str]:
    if tier == "high_depth":
        return T.CELL_CRIMSON_BG, T.CELL_CRIMSON_BORDER, T.CELL_CRIMSON_RAIL, T.CELL_CRIMSON_SUB
    if tier == "public":
        return T.CELL_COBALT_BG, T.CELL_COBALT_BORDER, T.CELL_COBALT_RAIL, T.CELL_COBALT_SUB
    return T.CELL_GRAPHITE_BG, T.CELL_GRAPHITE_BORDER, T.CELL_GRAPHITE_RAIL, T.CELL_GRAPHITE_SUB


def render_mitre_heatmap_svg(scan: ScanResult) -> str:
    col_count = len(TACTIC_CATALOG)  # 7 tactics
    pad_x = 16
    gap = 10
    usable_w = 880 - pad_x * 2 - gap * (col_count - 1)
    col_w = usable_w / col_count  # ~112.5px

    top_y = 32
    box_h = 194
    total_h = top_y + box_h + 4

    mapped_total = len(scan.technique_tiers)

    cols_svg: list[str] = []
    for c_idx, (tactic_name, techniques) in enumerate(TACTIC_CATALOG):
        x = pad_x + c_idx * (col_w + gap)
        hdr_y = top_y + 16
        cols_svg.append(
            f"""  <rect x="{x:.1f}" y="{hdr_y}" width="{col_w:.1f}" height="28" fill="{T.HEADER_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <text x="{x + 8:.1f}" y="{hdr_y + 18}" fill="{T.TEXT_PRIMARY}" font-size="11" class="mono">{esc(tactic_name)}</text>"""
        )

        for r_idx, (tid, short_name) in enumerate(techniques):
            cy = hdr_y + 38 + r_idx * 64
            tier = scan.technique_tiers.get(tid, "enterprise")
            bg, border, rail, sub = _tier_style(tier)
            cols_svg.append(
                f"""  <rect x="{x:.1f}" y="{cy}" width="{col_w:.1f}" height="54" rx="2" fill="{bg}" stroke="{border}" stroke-width="1" />
  <rect x="{x:.1f}" y="{cy}" width="3" height="54" fill="{rail}" />
  <text x="{x + 10:.1f}" y="{cy + 21}" fill="{T.TEXT_PRIMARY}" font-size="12" class="mono">{esc(tid)}</text>
  <text x="{x + 10:.1f}" y="{cy + 39}" fill="{sub}" font-size="10.5" class="mono">{esc(short_name)}</text>"""
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{total_h}" viewBox="0 0 880 {total_h}" role="img" aria-label="MITRE ATT&amp;CK Detection and Sensor Coverage Matrix">
  <title>MITRE ATT&amp;CK Coverage — {mapped_total} Techniques Mapped</title>
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>

  <!-- Title + Sharp Square Legend -->
  <text x="0" y="20" fill="{T.TEXT_PRIMARY}" font-size="17" letter-spacing="-0.2" class="disp">MITRE ATT&amp;CK coverage</text>
  <text x="196" y="20" fill="{T.TEXT_MUTED}" font-size="11" class="mono">{mapped_total} techniques mapped · hybrid scan</text>

  <rect x="556" y="10" width="9" height="9" fill="{T.CRIMSON}" />
  <text x="571" y="19" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">High depth</text>

  <rect x="658" y="10" width="9" height="9" fill="{T.COBALT_BRIGHT}" />
  <text x="673" y="19" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Public repo</text>

  <rect x="768" y="10" width="9" height="9" fill="{T.CELL_GRAPHITE_RAIL}" />
  <text x="783" y="19" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Enterprise / Lab</text>

  <!-- Deep Recessed Matrix Well (#0B0D12) -->
  <rect x="0.5" y="{top_y + 0.5}" width="879" height="{box_h - 1}" fill="{T.RECESSED_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />

{chr(10).join(cols_svg)}
</svg>
"""
