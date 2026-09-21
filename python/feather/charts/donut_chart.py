"""
Donut and Pie charts with customizable cutout radius, KPI center labels, and legends.
"""

from __future__ import annotations
import math
from typing import List, Sequence, Optional
from feather import Canvas
from .theme import Theme, resolve_theme


class DonutChart:
    """
    Modern Donut & Pie chart with smooth vector annular sectors,
    customizable cutout ratio, centered KPI metric text, and legend.
    """

    def __init__(
        self,
        width: int = 500,
        height: int = 420,
        title: str = "",
        subtitle: str = "",
        theme: Theme | str = "dark",
        cutout_ratio: float = 0.65,
        center_text: str = "",
        center_subtext: str = "",
    ):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.theme = resolve_theme(theme)
        self.cutout_ratio = cutout_ratio
        self.center_text = center_text
        self.center_subtext = center_subtext
        self.slices: List[dict] = []

    def add_slice(
        self,
        name: str,
        value: float,
        color: Optional[str] = None,
    ) -> DonutChart:
        idx = len(self.slices)
        chosen_color = color or self.theme.palette[idx % len(self.theme.palette)]
        self.slices.append({
            "name": name,
            "value": float(value),
            "color": chosen_color,
        })
        return self

    def render(self) -> Canvas:
        canvas = Canvas(self.width, self.height, background=self.theme.background)

        # Header Titles
        if self.title:
            canvas.draw_text(self.title, 40.0, 32.0, size=20.0, color=self.theme.text_color)
            if self.subtitle:
                canvas.draw_text(self.subtitle, 40.0, 52.0, size=12.0, color=self.theme.subtext_color)

        if not self.slices:
            return canvas

        total = sum(s["value"] for s in self.slices)
        if total <= 0:
            return canvas

        # Center and Radius
        cx = self.width * 0.34
        cy = (self.height + (40.0 if self.title else 0.0)) * 0.5
        outer_r = min(self.width * 0.28, self.height * 0.34)
        inner_r = outer_r * self.cutout_ratio

        # Draw Slices
        start_angle = -math.pi / 2.0  # Start at top (12 o'clock)
        slice_gap = 0.025 if len(self.slices) > 1 else 0.0

        for s in self.slices:
            fraction = s["value"] / total
            angle_span = fraction * 2.0 * math.pi

            a1 = start_angle + slice_gap
            a2 = start_angle + angle_span - slice_gap

            if a2 > a1:
                # Calculate outer coordinates
                x1_out = cx + outer_r * math.cos(a1)
                y1_out = cy + outer_r * math.sin(a1)
                x2_out = cx + outer_r * math.cos(a2)
                y2_out = cy + outer_r * math.sin(a2)

                large_arc = 1 if (a2 - a1) > math.pi else 0

                if inner_r > 0.0:
                    # Annular sector (Donut)
                    x1_in = cx + inner_r * math.cos(a1)
                    y1_in = cy + inner_r * math.sin(a1)
                    x2_in = cx + inner_r * math.cos(a2)
                    y2_in = cy + inner_r * math.sin(a2)

                    path_d = (
                        f"M {x1_out:.2f} {y1_out:.2f} "
                        f"A {outer_r:.2f} {outer_r:.2f} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} "
                        f"L {x2_in:.2f} {y2_in:.2f} "
                        f"A {inner_r:.2f} {inner_r:.2f} 0 {large_arc} 0 {x1_in:.2f} {y1_in:.2f} Z"
                    )
                else:
                    # Pie slice
                    path_d = (
                        f"M {cx:.2f} {cy:.2f} "
                        f"L {x1_out:.2f} {y1_out:.2f} "
                        f"A {outer_r:.2f} {outer_r:.2f} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} Z"
                    )

                canvas.draw_svg_path(path_d, fill=s["color"])

            start_angle += angle_span

        # Center Text (KPI / Total)
        if self.cutout_ratio > 0.4:
            display_text = self.center_text or f"{int(round(total)):,}"
            display_subtext = self.center_subtext or "Total"

            # Center approximation
            tw = len(display_text) * 7.0
            canvas.draw_text(display_text, cx - tw * 0.5, cy - 14.0, size=20.0, color=self.theme.text_color)
            tsw = len(display_subtext) * 4.0
            canvas.draw_text(display_subtext, cx - tsw * 0.5, cy + 10.0, size=11.0, color=self.theme.subtext_color)

        # Legend on the right side
        leg_x = self.width * 0.62
        leg_start_y = cy - (len(self.slices) * 26.0) * 0.5

        for i, s in enumerate(self.slices):
            ly = leg_start_y + i * 26.0
            pct = (s["value"] / total) * 100.0

            # Color pill
            canvas.draw_rounded_rect(leg_x, ly + 2.0, 10.0, 10.0, rx=3.0, fill=s["color"])
            canvas.draw_text(f"{s['name']}", leg_x + 18.0, ly, size=12.0, color=self.theme.text_color)
            canvas.draw_text(f"{pct:.1f}%", leg_x + 18.0 + len(s['name']) * 7.5 + 8.0, ly, size=11.0, color=self.theme.subtext_color)

        return canvas


# Convenient alias
PieChart = DonutChart
