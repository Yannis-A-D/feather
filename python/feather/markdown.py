"""
Inline Markdown and rich-text typography engine for Feather.
Supports **bold**, *italic*, `code`, <color=...>, bullet lists, and automatic word-wrapping.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from feather import Canvas, Font


@dataclass
class StyledSpan:
    text: str
    is_bold: bool = False
    is_italic: bool = False
    is_code: bool = False
    color: Optional[str] = None
    size_multiplier: float = 1.0


# Regex pattern to match formatting tokens
# 1. `code`
# 2. **bold**
# 3. *italic*
# 4. <color=#hex>...</color>
TOKEN_REGEX = re.compile(
    r"(`(?P<code>[^`]+)`)"
    r"|(\*\*(?P<bold>[^*]+)\*\*)"
    r"|(\*(?P<italic>[^*]+)\*)"
    r"|(<color=(?P<color_val>[^>]+)>(?P<colored_text>.*?)</color>)",
    re.DOTALL,
)


def parse_inline_markdown(text: str, default_color: str = "#cdd6f4") -> List[StyledSpan]:
    """Parse inline markdown tags into a sequence of StyledSpan objects."""
    spans: List[StyledSpan] = []
    last_idx = 0

    for match in TOKEN_REGEX.finditer(text):
        start, end = match.span()
        if start > last_idx:
            plain = text[last_idx:start]
            if plain:
                spans.append(StyledSpan(text=plain, color=default_color))

        if match.group("code"):
            spans.append(StyledSpan(text=match.group("code"), is_code=True, color="#89b4fa"))
        elif match.group("bold"):
            spans.append(StyledSpan(text=match.group("bold"), is_bold=True, color=default_color))
        elif match.group("italic"):
            spans.append(StyledSpan(text=match.group("italic"), is_italic=True, color=default_color))
        elif match.group("color_val"):
            spans.append(StyledSpan(text=match.group("colored_text"), color=match.group("color_val")))

        last_idx = end

    if last_idx < len(text):
        spans.append(StyledSpan(text=text[last_idx:], color=default_color))

    return spans


def render_markdown(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    max_width: Optional[float] = None,
    size: float = 16.0,
    default_color: str = "#cdd6f4",
    line_spacing: float = 6.0,
    font: Optional[Font] = None,
) -> Tuple[float, float]:
    """
    Render multiline markdown text onto canvas with subpixel typography,
    word-wrapping, inline styles, code badges, and bullet points.
    Returns (consumed_width, consumed_height).
    """
    cursor_y = y
    max_line_width = 0.0

    raw_lines = text.split("\n")

    for raw_line in raw_lines:
        line_size = size
        is_bullet = False
        line_prefix = ""

        # Headings & Bullets
        stripped = raw_line.strip()
        if stripped.startswith("# "):
            raw_line = stripped[2:]
            line_size = size * 1.6
        elif stripped.startswith("## "):
            raw_line = stripped[3:]
            line_size = size * 1.35
        elif stripped.startswith("### "):
            raw_line = stripped[4:]
            line_size = size * 1.15
        elif stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            is_bullet = True
            raw_line = stripped[2:]
            line_prefix = "• "

        spans = parse_inline_markdown(raw_line, default_color=default_color)

        # Tokenize into words while preserving spans
        words: List[Tuple[str, StyledSpan]] = []
        if is_bullet:
            bullet_span = StyledSpan(text=line_prefix, color="#89b4fa", is_bold=True)
            words.append((line_prefix, bullet_span))

        for span in spans:
            split_words = span.text.split(" ")
            for i, w in enumerate(split_words):
                suffix = " " if i < len(split_words) - 1 else ""
                words.append((w + suffix, span))

        # Flow line words with wrapping
        cur_x = x
        current_line_tokens: List[Tuple[float, float, str, StyledSpan]] = []
        current_line_h = line_size + line_spacing

        for word_str, span in words:
            if not word_str:
                continue

            tok_size = line_size * span.size_multiplier
            tw, _ = canvas.measure_text(word_str, size=tok_size, font=font)

            if max_width and (cur_x + tw - x > max_width) and (cur_x > x):
                # Wrap to next line
                # Render accumulated line
                for tx, ty, tstr, tspan in current_line_tokens:
                    _draw_span(canvas, tx, ty, tstr, tspan, line_size, font)

                max_line_width = max(max_line_width, cur_x - x)
                cur_x = x + (18.0 if is_bullet else 0.0)
                cursor_y += current_line_h
                current_line_tokens.clear()

            current_line_tokens.append((cur_x, cursor_y, word_str, span))
            cur_x += tw

        # Render remaining tokens on line
        for tx, ty, tstr, tspan in current_line_tokens:
            _draw_span(canvas, tx, ty, tstr, tspan, line_size, font)

        max_line_width = max(max_line_width, cur_x - x)
        cursor_y += current_line_h

    total_height = cursor_y - y
    return max_line_width, total_height


def _draw_span(
    canvas: Canvas,
    x: float,
    y: float,
    text: str,
    span: StyledSpan,
    base_size: float,
    font: Optional[Font],
):
    effective_size = base_size * span.size_multiplier
    text_to_draw = text.rstrip(" ")
    trailing_space = " " if text.endswith(" ") else ""

    if span.is_code:
        # Draw code pill background
        tw, th = canvas.measure_text(text_to_draw, size=effective_size, font=font)
        canvas.draw_rounded_rect(
            x - 3.0, y - 2.0, tw + 6.0, th + 4.0,
            rx=3.0, fill="rgba(255, 255, 255, 0.08)", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.0
        )
        canvas.draw_text(text_to_draw, x, y, size=effective_size, color=span.color, font=font)
    elif span.is_bold:
        # Bold simulation: double-strike with subpixel offset for enhanced visual weight
        canvas.draw_text(text_to_draw, x, y, size=effective_size, color=span.color, font=font)
        canvas.draw_text(text_to_draw, x + 0.6, y, size=effective_size, color=span.color, font=font)
    else:
        canvas.draw_text(text_to_draw, x, y, size=effective_size, color=span.color, font=font)
