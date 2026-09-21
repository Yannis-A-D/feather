"""
Modern pill-capped Bar & Column charts with multi-series grouping.
"""

from __future__ import annotations
from typing import List, Sequence, Optional
from feather import Canvas
from .theme import Theme, resolve_theme


class BarChart:
    """
    Modern Bar & Column chart with rounded pill caps, multi-series
    grouping, value annotations, and automatic category spacing.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 420,
        title: str = "",
        subtitle: str = "",
        theme: Theme | str = "dark",
        horizontal: bool = False,
        show_values: bool = True,
        show_grid: bool = True,
        corner_radius: float = 6.0,
    ):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.theme = resolve_theme(theme)
        self.horizontal = horizontal
        self.show_values = show_values
        self.show_grid = show_grid
        self.corner_radius = corner_radius
        self.categories: List[str] = []
        self.series: List[dict] = []

    def set_categories(self, categories: Sequence[str]) -> BarChart:
        self.categories = list(categories)
        return self

    def add_series(
        self,
        name: str,
        values: Sequence[float],
        color: Optional[str] = None,
    ) -> BarChart:
        idx = len(self.series)
        chosen_color = color or self.theme.palette[idx % len(self.theme.palette)]
        self.series.append({
            "name": name,
            "values": [float(v) for v in values],
            "color": chosen_color,
        })
        return self

    def render(self) -> Canvas:
        canvas = Canvas(self.width, self.height, background=self.theme.background)

        margin_left = 50.0
        margin_right = 30.0
        top_y = 75.0 if self.title else 40.0
        bottom_y = self.height - 45.0
        plot_w = self.width - margin_left - margin_right
        plot_h = bottom_y - top_y

        # Header Titles
        if self.title:
            canvas.draw_text(self.title, margin_left, 24.0, size=16.0, color=self.theme.text_color)
            if self.subtitle:
                canvas.draw_text(self.subtitle, margin_left, 44.0, size=11.0, color=self.theme.subtext_color)

        if not self.series or not self.categories:
            return canvas

        num_cats = len(self.categories)
        num_series = len(self.series)

        all_vals = [v for s in self.series for v in s["values"]]
        max_val = max(all_vals) if all_vals else 1.0
        if max_val <= 0.0:
            max_val = 1.0

        if not self.horizontal:
            # Vertical Columns
            # 1. Grid
            num_grid_lines = 4
            for i in range(num_grid_lines + 1):
                ratio = i / num_grid_lines
                gy = bottom_y - ratio * plot_h
                val = ratio * max_val
                if self.show_grid:
                    canvas.draw_line(
                        margin_left, gy, margin_left + plot_w, gy,
                        stroke=self.theme.grid_color, stroke_width=1.0
                    )
                val_str = f"{int(round(val)):,}" if max_val >= 10.0 else f"{val:.1f}"
                canvas.draw_text(val_str, 12.0, gy - 6.0, size=11.0, color=self.theme.subtext_color)

            # 2. Columns
            group_w = plot_w / num_cats
            bar_padding = group_w * 0.15
            usable_w = group_w - bar_padding * 2.0
            single_bar_w = usable_w / num_series

            for cat_idx, cat in enumerate(self.categories):
                group_x = margin_left + cat_idx * group_w + bar_padding

                # Category Label
                lbl_x = group_x + usable_w * 0.5 - (len(cat) * 3.2)
                canvas.draw_text(cat, lbl_x, bottom_y + 14.0, size=11.0, color=self.theme.subtext_color)

                for s_idx, s in enumerate(self.series):
                    val = s["values"][cat_idx] if cat_idx < len(s["values"]) else 0.0
                    bar_h = (val / max_val) * plot_h
                    bx = group_x + s_idx * single_bar_w
                    by = bottom_y - bar_h

                    bw = max(2.0, single_bar_w - 4.0)

                    # Subtle background track
                    canvas.draw_rounded_rect(
                        bx, top_y, bw, plot_h,
                        rx=self.corner_radius,
                        fill=self.theme.card_bg,
                    )

                    # Filled column
                    if bar_h > 1.0:
                        canvas.draw_rounded_rect(
                            bx, by, bw, bar_h,
                            rx=self.corner_radius,
                            fill=s["color"],
                        )

                    # Value label
                    if self.show_values and bar_h > 15.0:
                        v_str = f"{int(round(val))}" if val >= 10 else f"{val:.1f}"
                        vx = bx + bw * 0.5 - (len(v_str) * 3.0)
                        canvas.draw_text(v_str, vx, by - 14.0, size=10.0, color=self.theme.text_color)

        else:
            # Horizontal Bars
            bar_h = plot_h / num_cats
            single_bar_h = (bar_h * 0.7) / num_series

            for cat_idx, cat in enumerate(self.categories):
                group_y = top_y + cat_idx * bar_h
                canvas.draw_text(cat, 12.0, group_y + bar_h * 0.4, size=11.0, color=self.theme.subtext_color)

                for s_idx, s in enumerate(self.series):
                    val = s["values"][cat_idx] if cat_idx < len(s["values"]) else 0.0
                    bar_len = (val / max_val) * plot_w
                    by = group_y + s_idx * single_bar_h
                    bh = max(2.0, single_bar_h - 4.0)

                    # Track
                    canvas.draw_rounded_rect(
                        margin_left, by, plot_w, bh,
                        rx=self.corner_radius,
                        fill=self.theme.card_bg,
                    )

                    # Bar
                    if bar_len > 1.0:
                        canvas.draw_rounded_rect(
                            margin_left, by, bar_len, bh,
                            rx=self.corner_radius,
                            fill=s["color"],
                        )

                    if self.show_values:
                        v_str = f"{int(round(val))}"
                        canvas.draw_text(v_str, margin_left + bar_len + 8.0, by - 2.0, size=10.0, color=self.theme.text_color)

        # Draw Legend at top right
        legend_x = self.width - margin_right
        legend_y = 24.0
        for s in reversed(self.series):
            tw = len(s["name"]) * 7.5 + 24.0
            legend_x -= tw
            canvas.draw_rounded_rect(legend_x + 2.0, legend_y + 4.0, 8.0, 8.0, rx=2.0, fill=s["color"])
            canvas.draw_text(s["name"], legend_x + 14.0, legend_y, size=12.0, color=self.theme.text_color)

        return canvas
