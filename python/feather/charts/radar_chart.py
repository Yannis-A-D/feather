"""
Multi-axis Radar & Spider charts with polygonal web grids and translucent fills.
"""

from __future__ import annotations
import math
from typing import List, Sequence, Optional
from feather import Canvas
from .theme import Theme, resolve_theme


class RadarChart:
    """
    Polygonal Radar & Spider chart for skills, benchmarks, and multi-variable
    metric profiling with anti-aliased concentric webs and glowing nodes.
    """

    def __init__(
        self,
        width: int = 500,
        height: int = 450,
        title: str = "",
        subtitle: str = "",
        theme: Theme | str = "dark",
        max_value: Optional[float] = None,
    ):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.theme = resolve_theme(theme)
        self.max_value = max_value
        self.axes: List[str] = []
        self.series: List[dict] = []

    def set_axes(self, axes: Sequence[str]) -> RadarChart:
        self.axes = list(axes)
        return self

    def add_series(
        self,
        name: str,
        values: Sequence[float],
        color: Optional[str] = None,
        fill_opacity: float = 0.25,
    ) -> RadarChart:
        idx = len(self.series)
        chosen_color = color or self.theme.palette[idx % len(self.theme.palette)]
        self.series.append({
            "name": name,
            "values": [float(v) for v in values],
            "color": chosen_color,
            "fill_opacity": fill_opacity,
        })
        return self

    def render(self) -> Canvas:
        canvas = Canvas(self.width, self.height, background=self.theme.background)

        # Header Titles
        if self.title:
            canvas.draw_text(self.title, 40.0, 24.0, size=16.0, color=self.theme.text_color)
            if self.subtitle:
                canvas.draw_text(self.subtitle, 40.0, 44.0, size=11.0, color=self.theme.subtext_color)

        if not self.axes or not self.series:
            return canvas

        num_axes = len(self.axes)
        if num_axes < 3:
            return canvas

        cx = self.width * 0.50
        cy = (self.height + (40.0 if self.title else 0.0)) * 0.50
        radius = min(self.width, self.height) * 0.35

        # Determine Max Value
        all_vals = [v for s in self.series for v in s["values"]]
        max_val = self.max_value or (max(all_vals) if all_vals else 100.0)
        if max_val <= 0:
            max_val = 100.0

        # Draw Concentric Web Polygons
        num_rings = 4
        for r_step in range(1, num_rings + 1):
            ring_r = radius * (r_step / num_rings)
            ring_points = []
            for i in range(num_axes):
                theta = -math.pi / 2.0 + (i / num_axes) * 2.0 * math.pi
                px = cx + ring_r * math.cos(theta)
                py = cy + ring_r * math.sin(theta)
                ring_points.append((px, py))

            canvas.draw_polygon(
                ring_points,
                fill=None,
                stroke=self.theme.grid_color,
                stroke_width=1.0,
            )

        # Draw Radial Spokes and Axis Labels
        for i, axis_name in enumerate(self.axes):
            theta = -math.pi / 2.0 + (i / num_axes) * 2.0 * math.pi
            spoke_x = cx + radius * math.cos(theta)
            spoke_y = cy + radius * math.sin(theta)

            canvas.draw_line(cx, cy, spoke_x, spoke_y, stroke=self.theme.grid_color, stroke_width=1.0)

            # Axis Label
            lbl_r = radius + 20.0
            lbl_x = cx + lbl_r * math.cos(theta) - (len(axis_name) * 3.5)
            lbl_y = cy + lbl_r * math.sin(theta) - 6.0
            canvas.draw_text(axis_name, lbl_x, lbl_y, size=11.0, color=self.theme.subtext_color)

        # Draw Data Series Polygons
        for s in self.series:
            series_points = []
            for i in range(num_axes):
                val = s["values"][i] if i < len(s["values"]) else 0.0
                ratio = min(1.0, max(0.0, val / max_val))
                theta = -math.pi / 2.0 + (i / num_axes) * 2.0 * math.pi
                px = cx + (radius * ratio) * math.cos(theta)
                py = cy + (radius * ratio) * math.sin(theta)
                series_points.append((px, py))

            # Translucent fill
            fill_color = s["color"]
            # Convert hex to rgba if needed or use semi-transparent stroke
            canvas.draw_polygon(
                series_points,
                fill="rgba(255, 255, 255, 0.08)",
                stroke=s["color"],
                stroke_width=2.5,
            )

            # Nodes on vertices
            for px, py in series_points:
                canvas.draw_circle(px, py, 4.0, fill=self.theme.background, stroke=s["color"], stroke_width=1.5)
                canvas.draw_circle(px, py, 2.0, fill=s["color"])

        # Legend at top right
        legend_x = self.width - 40.0
        legend_y = 24.0
        for s in reversed(self.series):
            tw = len(s["name"]) * 7.5 + 24.0
            legend_x -= tw
            canvas.draw_circle(legend_x + 6.0, legend_y + 6.0, 4.0, fill=s["color"])
            canvas.draw_text(s["name"], legend_x + 16.0, legend_y, size=12.0, color=self.theme.text_color)

        return canvas
