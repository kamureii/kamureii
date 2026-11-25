"""Renders the v3 asymmetric 7/5 split SVG: Process Lineage (left) + Sigma Bio Rule (right)."""

from __future__ import annotations

from typing import Any

from scanner import ScanResult
from sigma_validator import SigmaValidationResult
from theme import V3Theme as T, esc, truncate


def _rail_for_ring(ring: str) -> tuple[str, str]:
    low = ring.lower()
    if low == "kernel":
        return T.CRIMSON, T.CRIMSON_INK
    if low == "minifilter":
        return T.CRIMSON_MID, T.TEXT_SECONDARY
    if low == "usermode":
        return T.COBALT_BRIGHT, T.COBALT_INK
    return T.COBALT_BRIGHT, T.COBALT_INK


def render_lineage_sigma_svg(
    config: dict[str, Any],
    scan: ScanResult,
    sigma_res: SigmaValidationResult,
) -> str:
    projects: list[dict[str, Any]] = list(config.get("process_lineage", []))[:5]
    contact_row = config.get("network_node", {})
    rows = projects + ([contact_row] if contact_row else [])

    # Left panel dimensions (x=0..516), Right panel (x=532..880)
    left_w = 516
    right_x = 532
    right_w = 880 - right_x  # 348
    header_y = 32
    row_h = 52
    panel_h = 44 + len(rows) * row_h
    total_h = header_y + panel_h + 4

    # Build left rows
    left_rows_svg: list[str] = []
    for idx, item in enumerate(rows):
        y = header_y + 44 + idx * row_h
        is_net = item.get("ring", "").lower() == "network"
        row_bg = T.RECESSED_BG if is_net else (T.SLAB_BG if idx % 2 == 0 else T.SLAB_ALT_BG)
        rail_color, tag_color = _rail_for_ring(str(item.get("ring", "kernel")))

        binary = str(item.get("binary", "module.sys"))
        repo_name = str(item.get("repo", ""))
        detail = str(item.get("detail", ""))
        stack = str(item.get("stack", ""))

        # Live star sync if repo exists on GitHub and has stars
        repo_info = scan.repos.get(repo_name)
        if repo_info and repo_info.stars > 0:
            stack = f"{stack} · *{repo_info.stars}"

        name_color = T.TEXT_SECONDARY if is_net else T.TEXT_PRIMARY
        detail_color = T.TEXT_MUTED if is_net else T.TEXT_SECONDARY

        left_rows_svg.append(
            f"""  <rect x="1" y="{y}" width="{left_w - 2}" height="{row_h}" fill="{row_bg}" />
  <rect x="1" y="{y}" width="3" height="{row_h}" fill="{rail_color}" />
  <line x1="1" y1="{y}" x2="{left_w - 1}" y2="{y}" stroke="{T.BORDER_SUBTLE}" stroke-width="1" />
  <text x="16" y="{y + 20}" fill="{name_color}" font-size="12" class="mono">{esc(truncate(binary, 27))}</text>
  <text x="16" y="{y + 36}" fill="{detail_color}" font-size="11" class="mono">{esc(truncate(detail, 54))}</text>
  <text x="{left_w - 14}" y="{y + 27}" text-anchor="end" fill="{tag_color}" font-size="11" class="mono">{esc(truncate(stack, 14))}</text>"""
        )

    # Build right Sigma YAML lines (monochrome + crimson accent)
    rule = sigma_res.rule or {}
    det = rule.get("detection", {}) if isinstance(rule.get("detection"), dict) else {}
    logsrc = rule.get("logsource", {}) if isinstance(rule.get("logsource"), dict) else {}
    ring0_items = det.get("ring0", []) if isinstance(det.get("ring0"), list) else []
    eng_items = det.get("engineering", []) if isinstance(det.get("engineering"), list) else []
    fps = rule.get("falsepositives", []) if isinstance(rule.get("falsepositives"), list) else []

    yaml_lines: list[tuple[str, str, str]] = [
        ("title: ", truncate(str(rule.get("title", "Endpoint & Detection Engineer")), 32), T.TEXT_PRIMARY),
        ("author: ", truncate(str(rule.get("author", "Tran Quoc Hung (Kamureii)")), 31), T.TEXT_PRIMARY),
        ("logsource:", "", T.TEXT_PRIMARY),
        ("  category: ", str(logsrc.get("category", "endpoint_security")), T.TEXT_PRIMARY),
        ("  product: ", str(logsrc.get("product", "windows_kernel")), T.TEXT_PRIMARY),
        ("detection:", "", T.TEXT_PRIMARY),
        ("  ring0:", "", T.TEXT_PRIMARY),
    ]
    for entry in ring0_items[:3]:
        yaml_lines.append(("    - ", truncate(str(entry), 34), T.TEXT_PRIMARY))
    yaml_lines.append(("  engineering:", "", T.TEXT_PRIMARY))
    for entry in eng_items[:2]:
        yaml_lines.append(("    - ", truncate(str(entry), 34), T.TEXT_PRIMARY))
    yaml_lines.append(
        ("  condition: ", truncate(str(det.get("condition", "ring0 and engineering")), 36), T.CRIMSON_INK)
    )
    if fps:
        yaml_lines.append(("falsepositives:", "", T.TEXT_PRIMARY))
        yaml_lines.append(("  - ", truncate(str(fps[0]), 34), T.TEXT_SECONDARY))

    sigma_lines_svg: list[str] = []
    line_y = header_y + 60
    for key_part, val_part, val_color in yaml_lines:
        if line_y > header_y + panel_h - 10:
            break
        sigma_lines_svg.append(
            f'  <text x="{right_x + 14}" y="{line_y}" font-size="11" class="mono">'
            f'<tspan fill="{T.TEXT_MUTED}">{esc(key_part)}</tspan>'
            f'<tspan fill="{val_color}">{esc(val_part)}</tspan></text>'
        )
        line_y += 15

    ci_label = "Sigma CI passing" if sigma_res.passed else "Sigma CI failed"
    ci_color = T.COBALT_INK if sigma_res.passed else T.CRIMSON_INK
    level_str = str(rule.get("level", "critical"))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{total_h}" viewBox="0 0 880 {total_h}" role="img" aria-label="Process Lineage Portfolio and Sigma Identity Rule">
  <title>Process Lineage &amp; Detection Profile</title>
  <style>
    .disp {{ font-family: {T.FONT_DISPLAY}; font-weight: 600; }}
    .mono {{ font-family: {T.FONT_MONO}; font-variant-numeric: tabular-nums; }}
  </style>

  <!-- Section Headings -->
  <text x="0" y="20" fill="{T.TEXT_PRIMARY}" font-size="17" letter-spacing="-0.2" class="disp">Process lineage</text>
  <text x="{left_w}" y="20" text-anchor="end" fill="{T.TEXT_MUTED}" font-size="11" class="mono">Ring 0 -&gt; User mode</text>

  <text x="{right_x}" y="20" fill="{T.TEXT_PRIMARY}" font-size="17" letter-spacing="-0.2" class="disp">Detection profile</text>
  <text x="880" y="20" text-anchor="end" fill="{ci_color}" font-size="11" class="mono">{esc(ci_label)}</text>

  <!-- LEFT PANEL: Process Lineage (Machined Slate #13161E) -->
  <rect x="0.5" y="{header_y + 0.5}" width="{left_w - 1}" height="{panel_h - 1}" fill="{T.SLAB_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />

  <!-- Elevated Kernel Root Bar (#1B1F2B) -->
  <rect x="1" y="{header_y + 1}" width="{left_w - 2}" height="43" fill="{T.HEADER_BG}" />
  <rect x="1" y="{header_y + 1}" width="3" height="43" fill="{T.CRIMSON}" />
  <text x="16" y="{header_y + 27}" fill="{T.TEXT_PRIMARY}" font-size="13" class="mono">ntoskrnl.exe</text>
  <rect x="118" y="{header_y + 13}" width="46" height="19" rx="1" fill="{T.RECESSED_BG}" stroke="{T.BORDER_BASE}" stroke-width="1" />
  <text x="141" y="{header_y + 26}" text-anchor="middle" fill="{T.TEXT_SECONDARY}" font-size="10.5" class="mono">PID 4</text>
  <text x="{left_w - 14}" y="{header_y + 27}" text-anchor="end" fill="{T.TEXT_SECONDARY}" font-size="11" class="mono">Windows Kernel &amp; EDR Engineering</text>

{chr(10).join(left_rows_svg)}

  <!-- RIGHT PANEL: Recessed Sigma Identity Well (#0B0D12) -->
  <rect x="{right_x + 0.5}" y="{header_y + 0.5}" width="{right_w - 1}" height="{panel_h - 1}" fill="{T.RECESSED_BG}" stroke="{T.BORDER_STRONG}" stroke-width="1" />
  <rect x="{right_x + 1}" y="{header_y + 1}" width="{right_w - 2}" height="43" fill="{T.HEADER_BG}" />
  <line x1="{right_x + 1}" y1="{header_y + 44}" x2="879" y2="{header_y + 44}" stroke="{T.BORDER_BASE}" stroke-width="1" />

  <text x="{right_x + 14}" y="{header_y + 27}" fill="{T.TEXT_PRIMARY}" font-size="11.5" class="mono">kamureii_identity.sigma.yml</text>
  <rect x="812" y="{header_y + 13}" width="56" height="19" rx="1" fill="{T.CELL_CRIMSON_BG}" stroke="{T.CRIMSON_BORDER}" stroke-width="1" />
  <text x="840" y="{header_y + 26}" text-anchor="middle" fill="{T.CRIMSON_INK}" font-size="10.5" class="mono">{esc(level_str)}</text>

{chr(10).join(sigma_lines_svg)}
</svg>
"""
