"""
Radial speedometer & metric gauges with gradient arcs and rounded caps.
"""

from __future__ import annotations
import math
from typing import Optional
from feather import Canvas
from .theme import Theme, resolve_theme


class Gauge:
    """
    Radial Arc Gauge / Speedometer with rounded stroke caps, customizable
    min/max ranges, background track, and center KPI metric readout.
    """

    def __init__(
        self,
        value: float,
        min_value: float = 0.0,
        max_value: float = 100.0,
        width: int = 400,
        height: int = 340,
        title: str = "",
        unit: str = "%",
        theme: Theme | str = "dark",
        color: Optional[str] = None,
        arc_width: float = 18.0,
    ):
        self.value = float(value)
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.width = width
        self.height = height
        self.title = title
        self.unit = unit
        self.theme = resolve_theme(theme)
        self.color = color or self.theme.palette[0]
        self.arc_width = arc_width

    def _arc_svg_path(
        self, cx: float, cy: float, radius: float, start_deg: float, end_deg: float
    ) -> str:
        if end_deg <= start_deg:
            return ""

        # Clamp to avoid full circle glitch in single SVG arc command
        if end_deg - start_deg >= 360.0:
            end_deg = start_deg + 359.99

        a1 = math.radians(start_deg)
        a2 = math.radians(end_deg)

        x1 = cx + radius * math.cos(a1)
        y1 = cy + radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy + radius * math.sin(a2)

        large_arc = 1 if (end_deg - start_deg) > 180.0 else 0

        return f"M {x1:.2f} {y1:.2f} A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"

    def render(self) -> Canvas:
        canvas = Canvas(self.width, self.height, background=self.theme.background)

        cx = self.width * 0.50
        cy = self.height * 0.52
        radius = min(self.width, self.height) * 0.36

        # Standard 240-degree gauge (from 150 deg to 390 deg)
        start_deg = 150.0
        total_span = 240.0
        end_deg = start_deg + total_span

        # 1. Background Track Arc
        track_svg = self._arc_svg_path(cx, cy, radius, start_deg, end_deg)
        canvas.draw_svg_path(
            track_svg,
            stroke=self.theme.card_bg,
            stroke_width=self.arc_width,
        )

        # 2. Value Arc
        clamped_val = max(self.min_value, min(self.max_value, self.value))
        ratio = (clamped_val - self.min_value) / max(0.001, self.max_value - self.min_value)
        val_span = ratio * total_span

        if val_span > 1.0:
            val_svg = self._arc_svg_path(cx, cy, radius, start_deg, start_deg + val_span)
            canvas.draw_svg_path(
                val_svg,
                stroke=self.color,
                stroke_width=self.arc_width,
            )

        # 3. Center Value Readout
        val_text = f"{int(round(self.value))}" if abs(self.value - round(self.value)) < 0.05 else f"{self.value:.1f}"
        if self.unit:
            val_text = f"{val_text}{self.unit}"

        tw = len(val_text) * 11.0
        canvas.draw_text(val_text, cx - tw * 0.5, cy - 20.0, size=32.0, color=self.theme.text_color)

        if self.title:
            ttw = len(self.title) * 4.5
            canvas.draw_text(self.title, cx - ttw * 0.5, cy + 22.0, size=13.0, color=self.theme.subtext_color)

        # Min and Max labels at ends
        min_str = f"{int(self.min_value)}"
        max_str = f"{int(self.max_value)}"
        min_rad = math.radians(start_deg)
        max_rad = math.radians(end_deg)

        mx = cx + (radius - 10.0) * math.cos(min_rad)
        my = cy + (radius - 10.0) * math.sin(min_rad)
        canvas.draw_text(min_str, mx - 12.0, my + 14.0, size=10.0, color=self.theme.subtext_color)

        xx = cx + (radius - 10.0) * math.cos(max_rad)
        xy = cy + (radius - 10.0) * math.sin(max_rad)
        canvas.draw_text(max_str, xx - 6.0, xy + 14.0, size=10.0, color=self.theme.subtext_color)

        return canvas
