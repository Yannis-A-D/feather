"""
Area and Line charts with smooth cubic spline interpolation and gradient fills.
"""

from __future__ import annotations
from typing import List, Tuple, Sequence, Optional
from feather import Canvas, LinearGradient
from .theme import Theme, resolve_theme


class AreaChart:
    """
    High-performance, anti-aliased Area & Line chart with smooth spline
    interpolation, linear gradient area fills, and glowing point markers.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 420,
        title: str = "",
        subtitle: str = "",
        theme: Theme | str = "dark",
        smooth: bool = True,
        show_points: bool = True,
        show_grid: bool = True,
    ):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.theme = resolve_theme(theme)
        self.smooth = smooth
        self.show_points = show_points
        self.show_grid = show_grid
        self.series: List[dict] = []
        self.x_labels: List[str] = []

    def set_x_labels(self, labels: Sequence[str]) -> AreaChart:
        self.x_labels = list(labels)
        return self

    def add_series(
        self,
        name: str,
        values: Sequence[float],
        color: Optional[str] = None,
        fill_opacity: float = 0.25,
        stroke_width: float = 2.5,
    ) -> AreaChart:
        idx = len(self.series)
        chosen_color = color or self.theme.palette[idx % len(self.theme.palette)]
        self.series.append({
            "name": name,
            "values": [float(v) for v in values],
            "color": chosen_color,
            "fill_opacity": fill_opacity,
            "stroke_width": stroke_width,
        })
        return self

    def _calculate_spline_path(
        self, points: List[Tuple[float, float]], bottom_y: float
    ) -> Tuple[str, str]:
        """
        Compute smooth Catmull-Rom to cubic Bézier spline SVG path data
        for both the stroke line and the closed area polygon.
        """
        if not points:
            return "", ""
        if len(points) == 1:
            x, y = points[0]
            line_path = f"M {x:.2f} {y:.2f}"
            area_path = f"M {x:.2f} {y:.2f} L {x:.2f} {bottom_y:.2f} Z"
            return line_path, area_path

        if not self.smooth or len(points) == 2:
            # Linear polyline
            line_cmds = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
            for x, y in points[1:]:
                line_cmds.append(f"L {x:.2f} {y:.2f}")
            line_str = " ".join(line_cmds)
            area_str = (
                f"{line_str} L {points[-1][0]:.2f} {bottom_y:.2f} "
                f"L {points[0][0]:.2f} {bottom_y:.2f} Z"
            )
            return line_str, area_str

        # Catmull-Rom to Cubic Bézier conversion
        n = len(points)
        line_cmds = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]

        for i in range(n - 1):
            p0 = points[i - 1] if i > 0 else points[i]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[i + 2] if i + 2 < n else p2

            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0

            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0

            line_cmds.append(
                f"C {cp1x:.2f} {cp1y:.2f}, {cp2x:.2f} {cp2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}"
            )

        line_str = " ".join(line_cmds)
        area_str = (
            f"{line_str} L {points[-1][0]:.2f} {bottom_y:.2f} "
            f"L {points[0][0]:.2f} {bottom_y:.2f} Z"
        )
        return line_str, area_str

    def render(self) -> Canvas:
        canvas = Canvas(self.width, self.height, background=self.theme.background)

        # Draw card container
        margin_x = 50.0
        top_y = 70.0 if self.title else 40.0
        bottom_y = self.height - (50.0 if self.x_labels else 35.0)
        plot_w = self.width - margin_x * 2.0
        plot_h = bottom_y - top_y

        # Header Titles
        if self.title:
            canvas.draw_text(self.title, margin_x, 32.0, size=20.0, color=self.theme.text_color)
            if self.subtitle:
                canvas.draw_text(self.subtitle, margin_x, 52.0, size=12.0, color=self.theme.subtext_color)

        if not self.series:
            return canvas

        # Collect min / max across all series
        all_vals = [v for s in self.series for v in s["values"]]
        if not all_vals:
            all_vals = [0.0]
        min_v = min(all_vals)
        max_v = max(all_vals)
        if min_v > 0.0:
            min_v = 0.0  # Anchor to zero if positive
        if max_v == min_v:
            max_v += 1.0

        # Draw Grid & Y-Axis Labels
        num_grid_lines = 5
        for i in range(num_grid_lines + 1):
            ratio = i / num_grid_lines
            gy = bottom_y - ratio * plot_h
            val = min_v + ratio * (max_v - min_v)

            if self.show_grid:
                canvas.draw_line(
                    margin_x, gy, margin_x + plot_w, gy,
                    stroke=self.theme.grid_color, stroke_width=1.0
                )

            val_str = f"{val:.1f}" if (max_v - min_v) < 10.0 else f"{int(round(val)):,}"
            canvas.draw_text(val_str, 12.0, gy - 6.0, size=11.0, color=self.theme.subtext_color)

        # Determine points for each series
        max_points = max(len(s["values"]) for s in self.series)
        step_x = plot_w / max(1, max_points - 1) if max_points > 1 else plot_w

        # Draw Area Fills & Lines
        for s in self.series:
            pts: List[Tuple[float, float]] = []
            for i, val in enumerate(s["values"]):
                px = margin_x + i * step_x
                py = bottom_y - ((val - min_v) / (max_v - min_v)) * plot_h
                pts.append((px, py))

            line_svg, area_svg = self._calculate_spline_path(pts, bottom_y)

            # Area gradient fill
            if s["fill_opacity"] > 0.0:
                grad = LinearGradient(
                    0, top_y, 0, bottom_y,
                    [(0.0, s["color"]), (1.0, "rgba(0, 0, 0, 0.0)")]
                )
                canvas.draw_svg_path(area_svg, fill=grad)

            # Smooth curve line
            canvas.draw_svg_path(
                line_svg,
                stroke=s["color"],
                stroke_width=s["stroke_width"],
            )

            # Data point markers
            if self.show_points:
                for px, py in pts:
                    # Outer glow halo
                    canvas.draw_circle(px, py, 6.0, fill="rgba(255, 255, 255, 0.15)")
                    # Colored ring
                    canvas.draw_circle(px, py, 4.0, fill=self.theme.background, stroke=s["color"], stroke_width=2.0)
                    # Center dot
                    canvas.draw_circle(px, py, 1.8, fill=s["color"])

        # Draw X-Axis Labels
        if self.x_labels:
            num_labels = len(self.x_labels)
            step_lbl = plot_w / max(1, num_labels - 1) if num_labels > 1 else plot_w
            for i, lbl in enumerate(self.x_labels):
                lx = margin_x + i * step_lbl
                canvas.draw_text(lbl, lx - 14.0, bottom_y + 16.0, size=11.0, color=self.theme.subtext_color)

        # Draw Legend at top right
        legend_x = self.width - margin_x
        legend_y = 28.0
        for s in reversed(self.series):
            # Compute approximate text width
            tw = len(s["name"]) * 7.5 + 24.0
            legend_x -= tw
            # Marker dot
            canvas.draw_circle(legend_x + 6.0, legend_y + 6.0, 4.0, fill=s["color"])
            canvas.draw_text(s["name"], legend_x + 16.0, legend_y, size=12.0, color=self.theme.text_color)

        return canvas


# Convenient alias
LineChart = AreaChart
