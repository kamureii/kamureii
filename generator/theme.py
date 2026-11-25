"""Locked v3 Sharp Tactical Obsidian & Crimson SVG design tokens."""

from __future__ import annotations

from xml.sax.saxutils import escape


class V3Theme:
    # Surfaces (never pure #000000)
    VOID_BG = "#08090C"
    RECESSED_BG = "#0B0D12"
    SLAB_BG = "#13161E"
    SLAB_ALT_BG = "#0F1219"
    HEADER_BG = "#1B1F2B"
    KPI_NEUTRAL_BG = "#12151E"
    KPI_COBALT_BG = "#10192B"
    KPI_CRIMSON_BG = "#241016"
    CANARY_BG = "#1B0D12"

    # High-contrast MITRE tiers
    CELL_CRIMSON_BG = "#251016"
    CELL_CRIMSON_BORDER = "rgba(229,46,61,0.48)"
    CELL_CRIMSON_RAIL = "#E52E3D"
    CELL_CRIMSON_SUB = "#D19AA0"

    CELL_COBALT_BG = "#10192B"
    CELL_COBALT_BORDER = "rgba(59,130,246,0.40)"
    CELL_COBALT_RAIL = "#3B82F6"
    CELL_COBALT_SUB = "#93B4F5"

    CELL_GRAPHITE_BG = "#191D28"
    CELL_GRAPHITE_BORDER = "rgba(255,255,255,0.14)"
    CELL_GRAPHITE_RAIL = "#6B7280"
    CELL_GRAPHITE_SUB = "#9CA3AF"

    # Borders
    BORDER_STRONG = "rgba(255,255,255,0.16)"
    BORDER_BASE = "rgba(255,255,255,0.12)"
    BORDER_SUBTLE = "rgba(255,255,255,0.08)"

    # Text roles
    TEXT_PRIMARY = "#F3F5F9"
    TEXT_SECONDARY = "#A5ACBC"
    TEXT_MUTED = "#788092"
    TEXT_FAINT = "#565E70"

    # Accents (Offense Crimson <-> Defense Cobalt)
    CRIMSON = "#E52E3D"
    CRIMSON_INK = "#FF5765"
    CRIMSON_MID = "#9E2450"
    CRIMSON_SUB = "#D19AA0"
    CRIMSON_BORDER = "rgba(229,46,61,0.52)"

    COBALT = "#2563EB"
    COBALT_BRIGHT = "#3B82F6"
    COBALT_INK = "#60A5FA"
    COBALT_SUB = "#93B4F5"

    # Typography
    FONT_DISPLAY = "'Bahnschrift', 'DIN Alternate', 'Space Grotesk', 'Segoe UI', sans-serif"
    FONT_MONO = "'Cascadia Mono', 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"


def esc(text: str) -> str:
    """XML-escape text for safe embedding inside SVG elements and attributes."""
    return escape(str(text), {'"': "&quot;", "'": "&apos;"})


def truncate(text: str, max_len: int) -> str:
    """Trim text cleanly with an ASCII ellipsis if longer than max_len."""
    clean = " ".join(str(text).split())
    if len(clean) <= max_len:
        return clean
    return clean[: max(1, max_len - 3)].rstrip() + "..."
