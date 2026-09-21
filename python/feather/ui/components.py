"""
Ready-to-use modern UI components: Cards, Badges, Metrics, and Buttons.
"""

from __future__ import annotations
from typing import Optional, Sequence, Tuple, Union
from feather import Canvas, LinearGradient
from .layout import Element, Column, Row, Text


class Badge(Element):
    """Pill badge for status indicators, tags, and category labels."""

    def __init__(
        self,
        text: str,
        color: str = "#89b4fa",
        bg_color: Optional[str] = None,
        dot: bool = True,
        size: float = 11.0,
    ):
        self.text = text
        self.color = color
        self.bg_color = bg_color or "rgba(255, 255, 255, 0.08)"
        self.dot = dot
        self.size = size

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        text_w = len(self.text) * self.size * 0.65
        dot_w = 14.0 if self.dot else 0.0
        padding_x = 20.0
        h = self.size + 14.0
        return text_w + dot_w + padding_x, h

    def render(self, canvas: Canvas, x: float, y: float):
        w, h = self.measure()
        rx = h * 0.5

        # Background pill
        canvas.draw_rounded_rect(
            x, y, w, h,
            rx=rx,
            fill=self.bg_color,
            stroke=self.color,
            stroke_width=1.0,
        )

        cur_x = x + 10.0
        if self.dot:
            canvas.draw_circle(cur_x + 3.0, y + h * 0.5, 3.5, fill=self.color)
            cur_x += 12.0

        canvas.draw_text(self.text, cur_x, y + 3.0, size=self.size, color=self.color)


class Button(Element):
    """Rounded action button with solid or gradient fill."""

    def __init__(
        self,
        text: str,
        color: str = "#ffffff",
        background: Union[str, Tuple[str, str]] = "#89b4fa",
        corner_radius: float = 8.0,
        size: float = 13.0,
        padding: Tuple[float, float] = (20.0, 10.0),
    ):
        self.text = text
        self.color = color
        self.background = background
        self.corner_radius = corner_radius
        self.size = size
        self.padding_x, self.padding_y = padding

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        text_w = len(self.text) * self.size * 0.65
        w = text_w + self.padding_x * 2.0
        h = self.size + self.padding_y * 2.0
        return w, h

    def render(self, canvas: Canvas, x: float, y: float):
        w, h = self.measure()

        if isinstance(self.background, (tuple, list)) and len(self.background) >= 2:
            grad = LinearGradient(x, y, x + w, y, [(0.0, self.background[0]), (1.0, self.background[1])])
            canvas.draw_rounded_rect(x, y, w, h, rx=self.corner_radius, fill=grad)
        else:
            canvas.draw_rounded_rect(x, y, w, h, rx=self.corner_radius, fill=self.background)

        tx = x + self.padding_x
        ty = y + self.padding_y - 1.0
        canvas.draw_text(self.text, tx, ty, size=self.size, color=self.color)


class Metric(Element):
    """Stat KPI block featuring primary metric, label, and optional trend pill."""

    def __init__(
        self,
        value: str,
        label: str,
        trend: Optional[str] = None,
        color: str = "#ffffff",
        value_size: float = 28.0,
        label_color: str = "#6c7086",
    ):
        self.value = value
        self.label = label
        self.trend = trend
        self.color = color
        self.value_size = value_size
        self.label_color = label_color

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        vw = len(self.value) * self.value_size * 0.65
        lw = len(self.label) * 8.0
        tw = (len(self.trend) * 7.5 + 20.0) if self.trend else 0.0
        w = max(vw + tw, lw)
        h = self.value_size + 24.0
        return w, h

    def render(self, canvas: Canvas, x: float, y: float):
        # Value
        canvas.draw_text(self.value, x, y, size=self.value_size, color=self.color)

        # Trend badge
        if self.trend:
            vw = len(self.value) * self.value_size * 0.65
            is_pos = self.trend.startswith("+")
            t_col = "#a6e3a1" if is_pos else "#f38ba8"
            t_bg = "rgba(166, 227, 161, 0.15)" if is_pos else "rgba(243, 139, 168, 0.15)"
            badge = Badge(self.trend, color=t_col, bg_color=t_bg, dot=False, size=10.0)
            badge.render(canvas, x + vw + 12.0, y + 4.0)

        # Subtitle label
        canvas.draw_text(self.label, x, y + self.value_size + 4.0, size=12.0, color=self.label_color)


class Card(Element):
    """
    Glassmorphic or solid container card with auto-layout padding,
    borders, rounded corners, and drop shadows.
    """

    def __init__(
        self,
        width: Optional[float] = None,
        padding: float = 24.0,
        corner_radius: float = 16.0,
        background: str = "rgba(255, 255, 255, 0.04)",
        border_color: str = "rgba(255, 255, 255, 0.10)",
        border_width: float = 1.2,
        shadow_blur: float = 20.0,
        shadow_color: str = "rgba(0, 0, 0, 0.40)",
    ):
        self.width = width
        self.padding = padding
        self.corner_radius = corner_radius
        self.background = background
        self.border_color = border_color
        self.border_width = border_width
        self.shadow_blur = shadow_blur
        self.shadow_color = shadow_color
        self.root = Column(gap=14.0)

    def add(self, child: Element) -> Card:
        self.root.add(child)
        return self

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        content_w, content_h = self.root.measure(max_w)
        total_w = self.width or (content_w + self.padding * 2.0)
        total_h = content_h + self.padding * 2.0
        return total_w, total_h

    def render(self, canvas: Canvas, x: float, y: float):
        w, h = self.measure()

        # Diffused drop shadow
        if self.shadow_blur > 0.0:
            canvas.draw_rounded_rect(
                x + 4.0, y + 8.0, w, h,
                rx=self.corner_radius,
                fill=self.shadow_color,
            )

        # Card container
        canvas.draw_rounded_rect(
            x, y, w, h,
            rx=self.corner_radius,
            fill=self.background,
            stroke=self.border_color,
            stroke_width=self.border_width,
        )

        # Render children inside padding
        inner_x = x + self.padding
        inner_y = y + self.padding
        self.root.render(canvas, inner_x, inner_y)

    def render_to_canvas(self, background: str = "#11111b", margin: float = 40.0) -> Canvas:
        """Create a dedicated standalone canvas tightly wrapping this card."""
        w, h = self.measure()
        cw = int(w + margin * 2.0)
        ch = int(h + margin * 2.0)
        canvas = Canvas(cw, ch, background=background)
        self.render(canvas, margin, margin)
        return canvas
