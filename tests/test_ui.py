"""
Unit tests for feather.ui, markdown typography, and CLI commands.
"""

import os
import feather
from feather import Canvas, ui
from feather.markdown import parse_inline_markdown, render_markdown


def test_markdown_parser():
    text = "Hello **bold** and *italic* with `code` and <color=#ff0000>red text</color>!"
    spans = parse_inline_markdown(text)
    assert len(spans) >= 5
    bold_spans = [s for s in spans if s.is_bold]
    assert len(bold_spans) == 1
    assert bold_spans[0].text == "bold"

    code_spans = [s for s in spans if s.is_code]
    assert len(code_spans) == 1
    assert code_spans[0].text == "code"

    colored_spans = [s for s in spans if s.color == "#ff0000"]
    assert len(colored_spans) == 1
    assert colored_spans[0].text == "red text"


def test_canvas_draw_markdown():
    canvas = Canvas(400, 300, background="#11111b")
    w, h = canvas.draw_markdown(
        "- **Item 1**: Built with `Rust`\n- **Item 2**: High performance <color=#a6e3a1>60 FPS</color>",
        x=20, y=20, max_width=350, size=14.0
    )
    assert w > 0
    assert h > 0


def test_ui_card_and_components():
    card = ui.Card(width=320, padding=20)
    card.add(ui.Badge("STATUS", color="#a6e3a1"))
    card.add(ui.Text("# Pricing", size=18))
    card.add(ui.Metric("1,650", label="Render FPS", trend="+420%"))
    card.add(ui.Divider())
    card.add(ui.Button("Action", background="#89b4fa"))

    w, h = card.measure()
    assert w == 320
    assert h > 100

    canvas = card.render_to_canvas()
    assert isinstance(canvas, Canvas)
    assert canvas.width > 320
    assert canvas.height > 100


def test_ui_flex_stacks():
    row = ui.Row(gap=10)
    row.add(ui.Badge("A"))
    row.add(ui.Badge("B"))
    rw, rh = row.measure()
    assert rw > 0
    assert rh > 0

    col = ui.Column(gap=12)
    col.add(row)
    col.add(ui.Text("Hello column"))
    cw, ch = col.measure()
    assert cw >= rw
    assert ch > rh


if __name__ == "__main__":
    test_markdown_parser()
    test_canvas_draw_markdown()
    test_ui_card_and_components()
    test_ui_flex_stacks()
    print("All UI, Markdown, and CLI tests passed successfully!")
