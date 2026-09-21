"""
Visual themes and color palettes for Feather Charts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Theme:
    name: str
    background: str
    card_bg: str
    card_border: str
    text_color: str
    subtext_color: str
    grid_color: str
    palette: List[str] = field(default_factory=list)


THEME_DARK = Theme(
    name="dark",
    background="#181825",
    card_bg="rgba(255, 255, 255, 0.03)",
    card_border="rgba(255, 255, 255, 0.10)",
    text_color="#cdd6f4",
    subtext_color="#a6adc8",
    grid_color="rgba(255, 255, 255, 0.07)",
    palette=["#89b4fa", "#a6e3a1", "#f38ba8", "#fab387", "#cba6f7", "#94e2d5", "#f9e2af"],
)

THEME_CYBERPUNK = Theme(
    name="cyberpunk",
    background="#0b0e17",
    card_bg="rgba(0, 240, 255, 0.04)",
    card_border="rgba(0, 240, 255, 0.20)",
    text_color="#ffffff",
    subtext_color="#7982a9",
    grid_color="rgba(0, 240, 255, 0.10)",
    palette=["#00f0ff", "#ff007f", "#7000ff", "#00ff66", "#ffe600", "#ff3366"],
)

THEME_EMERALD = Theme(
    name="emerald",
    background="#061a14",
    card_bg="rgba(16, 185, 129, 0.04)",
    card_border="rgba(16, 185, 129, 0.20)",
    text_color="#e6f7f0",
    subtext_color="#6ee7b7",
    grid_color="rgba(16, 185, 129, 0.10)",
    palette=["#10b981", "#34d399", "#06b6d4", "#f59e0b", "#8b5cf6"],
)

THEME_LIGHT = Theme(
    name="light",
    background="#f8fafc",
    card_bg="#ffffff",
    card_border="#e2e8f0",
    text_color="#0f172a",
    subtext_color="#64748b",
    grid_color="#e2e8f0",
    palette=["#3b82f6", "#10b981", "#f43f5e", "#f59e0b", "#8b5cf6", "#06b6d4"],
)

THEMES = {
    "dark": THEME_DARK,
    "cyberpunk": THEME_CYBERPUNK,
    "emerald": THEME_EMERALD,
    "light": THEME_LIGHT,
}


def resolve_theme(theme_input: Theme | str | None) -> Theme:
    if isinstance(theme_input, Theme):
        return theme_input
    if isinstance(theme_input, str):
        return THEMES.get(theme_input.lower(), THEME_DARK)
    return THEME_DARK
