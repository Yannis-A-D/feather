"""
Core layout primitives and flexbox stacks for Feather UI.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from feather import Canvas


class Element(ABC):
    """Abstract base element for Feather UI components."""

    @abstractmethod
    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        """Return (width, height) required by this element."""
        pass

    @abstractmethod
    def render(self, canvas: Canvas, x: float, y: float):
        """Draw this element onto the canvas at (x, y)."""
        pass


class Spacer(Element):
    """Empty space with fixed dimensions."""

    def __init__(self, width: float = 0.0, height: float = 0.0):
        self.width = width
        self.height = height

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        return self.width, self.height

    def render(self, canvas: Canvas, x: float, y: float):
        pass


class Divider(Element):
    """Horizontal or vertical hairline separator."""

    def __init__(
        self,
        length: Optional[float] = None,
        color: str = "rgba(255, 255, 255, 0.10)",
        thickness: float = 1.0,
        margin: float = 8.0,
    ):
        self.length = length
        self.color = color
        self.thickness = thickness
        self.margin = margin

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        w = self.length or (max_w if max_w else 100.0)
        h = self.thickness + self.margin * 2.0
        return w, h

    def render(self, canvas: Canvas, x: float, y: float):
        w = self.length or 100.0
        draw_y = y + self.margin
        canvas.draw_line(x, draw_y, x + w, draw_y, stroke=self.color, stroke_width=self.thickness)


class Text(Element):
    """Rich or plain text element with word-wrapping."""

    def __init__(
        self,
        text: str,
        size: float = 14.0,
        color: str = "#cdd6f4",
        markdown: bool = True,
        max_width: Optional[float] = None,
        line_spacing: float = 4.0,
    ):
        self.text = text
        self.size = size
        self.color = color
        self.markdown = markdown
        self.max_width = max_width
        self.line_spacing = line_spacing
        self._measured_size: Optional[Tuple[float, float]] = None

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        effective_max = self.max_width or max_w
        # Approximate measurement or line count
        lines = self.text.split("\n")
        num_lines = len(lines)
        approx_w = min(effective_max or 800.0, max(len(line) * self.size * 0.58 for line in lines))
        approx_h = num_lines * (self.size + self.line_spacing)
        self._measured_size = (approx_w, approx_h)
        return approx_w, approx_h

    def render(self, canvas: Canvas, x: float, y: float):
        if self.markdown:
            canvas.draw_markdown(
                self.text,
                x=x,
                y=y,
                max_width=self.max_width,
                size=self.size,
                default_color=self.color,
                line_spacing=self.line_spacing,
            )
        else:
            canvas.draw_text(self.text, x=x, y=y, size=self.size, color=self.color)


class Row(Element):
    """Horizontal flex stack with configurable gap and alignment."""

    def __init__(
        self,
        children: Optional[Sequence[Element]] = None,
        gap: float = 8.0,
        align: str = "center",
    ):
        self.children: List[Element] = list(children) if children else []
        self.gap = gap
        self.align = align.lower()

    def add(self, child: Element) -> Row:
        self.children.append(child)
        return self

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        total_w = 0.0
        max_h = 0.0
        for i, child in enumerate(self.children):
            cw, ch = child.measure()
            total_w += cw
            if i > 0:
                total_w += self.gap
            max_h = max(max_h, ch)
        return total_w, max_h

    def render(self, canvas: Canvas, x: float, y: float):
        _, row_h = self.measure()
        cur_x = x
        for child in self.children:
            cw, ch = child.measure()
            offset_y = 0.0
            if self.align == "center":
                offset_y = (row_h - ch) * 0.5
            elif self.align == "end":
                offset_y = row_h - ch

            child.render(canvas, cur_x, y + offset_y)
            cur_x += cw + self.gap


class Column(Element):
    """Vertical flex stack with configurable gap and alignment."""

    def __init__(
        self,
        children: Optional[Sequence[Element]] = None,
        gap: float = 8.0,
        align: str = "start",
    ):
        self.children: List[Element] = list(children) if children else []
        self.gap = gap
        self.align = align.lower()

    def add(self, child: Element) -> Column:
        self.children.append(child)
        return self

    def measure(self, max_w: Optional[float] = None) -> Tuple[float, float]:
        max_w_val = 0.0
        total_h = 0.0
        for i, child in enumerate(self.children):
            cw, ch = child.measure(max_w)
            max_w_val = max(max_w_val, cw)
            total_h += ch
            if i > 0:
                total_h += self.gap
        return max_w_val, total_h

    def render(self, canvas: Canvas, x: float, y: float):
        col_w, _ = self.measure()
        cur_y = y
        for child in self.children:
            cw, ch = child.measure()
            offset_x = 0.0
            if self.align == "center":
                offset_x = (col_w - cw) * 0.5
            elif self.align == "end":
                offset_x = col_w - cw

            child.render(canvas, x + offset_x, cur_y)
            cur_y += ch + self.gap
