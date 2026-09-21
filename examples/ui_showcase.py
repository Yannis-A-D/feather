"""
Feather UI & Markdown Showcase: Composing modern glassmorphic cards,
flexbox auto-layout stacks, KPI metrics, and inline markdown typography.
"""

import os
import feather
from feather import Canvas, ui

def generate_ui_preview():
    print("Generating Feather UI & Markdown Showcase...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)

    # Master canvas
    w, h = 1280, 720
    canvas = Canvas(w, h, background="#0d0f18")

    # Ambient backdrop glows
    canvas.draw_circle(250.0, 200.0, 280.0, fill="rgba(137, 180, 250, 0.05)")
    canvas.draw_circle(1000.0, 500.0, 320.0, fill="rgba(203, 166, 247, 0.05)")

    # Title header
    canvas.draw_text("FEATHER UI COMPONENT ENGINE", 60.0, 40.0, size=22.0, color="#ffffff")
    canvas.draw_text("Auto-Layout Flexbox Stacks, Glassmorphism & Inline Markdown Typography", 60.0, 68.0, size=13.0, color="#6c7086")

    # =========================================================================
    # CARD 1: Subscription / Plan Card (Left: x=60, y=120, w=360)
    # =========================================================================
    card1 = ui.Card(
        width=360.0,
        padding=26.0,
        corner_radius=18.0,
        background="rgba(255, 255, 255, 0.04)",
        border_color="rgba(255, 255, 255, 0.12)",
        shadow_blur=24.0,
        shadow_color="rgba(0, 0, 0, 0.50)",
    )

    # Header row with title and badge
    header_row = ui.Row(gap=12.0)
    header_row.add(ui.Badge("PRO CLOUD", color="#a6e3a1", bg_color="rgba(166, 227, 161, 0.15)"))
    header_row.add(ui.Badge("MOST POPULAR", color="#cba6f7", bg_color="rgba(203, 166, 247, 0.15)", dot=False))
    card1.add(header_row)

    card1.add(ui.Text("# $49 / month", size=24.0, color="#ffffff"))
    card1.add(ui.Text("Billed annually or $59 billed month-to-month.", size=12.0, color="#7982a9"))
    card1.add(ui.Divider(thickness=1.0, color="rgba(255, 255, 255, 0.08)", margin=6.0))

    # Feature checklist with inline markdown
    features_md = (
        "- **Unlimited** vector raster passes\n"
        "- **Rayon** multi-core threading (GIL released)\n"
        "- Full `resvg` SVG engine integration\n"
        "- <color=#a6e3a1>60 FPS</color> live desktop viewer\n"
        "- Priority 24/7 dedicated compute"
    )
    card1.add(ui.Text(features_md, size=13.0, color="#cdd6f4", line_spacing=6.0))
    card1.add(ui.Spacer(height=8.0))
    card1.add(ui.Button("Upgrade to Pro", background=("#89b4fa", "#cba6f7"), size=14.0, corner_radius=10.0))

    card1.render(canvas, 60.0, 120.0)

    # =========================================================================
    # CARD 2: Analytics KPI Telemetry (Center: x=460, y=120, w=440)
    # =========================================================================
    card2 = ui.Card(
        width=420.0,
        padding=26.0,
        corner_radius=18.0,
        background="rgba(255, 255, 255, 0.04)",
        border_color="rgba(255, 255, 255, 0.12)",
    )

    card2.add(ui.Row([
        ui.Badge("CLUSTER TELEMETRY", color="#89b4fa"),
        ui.Text("Region: `us-east-1`", size=11.0, color="#7982a9")
    ], gap=16.0))

    card2.add(ui.Text("### Pipeline Execution", size=17.0, color="#ffffff"))

    metrics_row = ui.Row(gap=30.0)
    metrics_row.add(ui.Metric("1,650", label="SIMD Render FPS", trend="+420%"))
    metrics_row.add(ui.Metric("14 ms", label="Avg Frame Latency", trend="-65%"))
    card2.add(metrics_row)

    card2.add(ui.Divider(thickness=1.0, color="rgba(255, 255, 255, 0.08)", margin=6.0))

    card2.add(ui.Text(
        "**Feather** optimizes CPU memory usage via *zero-copy* buffer bridges.\n"
        "Benchmark shows <color=#89b4fa>5.2x faster</color> throughput than competition.",
        size=12.5,
        color="#a6adc8",
        line_spacing=5.0,
    ))

    card2.add(ui.Spacer(height=6.0))
    actions_row = ui.Row(gap=12.0)
    actions_row.add(ui.Button("Live Profiler", background="#313244", size=12.0))
    actions_row.add(ui.Button("Export Report", background="rgba(255, 255, 255, 0.08)", size=12.0))
    card2.add(actions_row)

    card2.render(canvas, 460.0, 120.0)

    # =========================================================================
    # CARD 3: Rich Typography & Markdown Terminal (Right: x=920, y=120, w=300)
    # =========================================================================
    card3 = ui.Card(
        width=300.0,
        padding=22.0,
        corner_radius=18.0,
        background="rgba(17, 19, 29, 0.85)",
        border_color="rgba(137, 180, 250, 0.25)",
    )

    card3.add(ui.Badge("RICH TYPOGRAPHY", color="#fab387", bg_color="rgba(250, 179, 135, 0.15)"))
    card3.add(ui.Text("## Markdown Support", size=16.0, color="#ffffff"))
    
    code_demo = (
        "Feather's `draw_markdown` renders:\n\n"
        "- **Bold** emphasis\n"
        "- *Italic* styling\n"
        "- Inline `code` badges\n"
        "- <color=#f38ba8>Custom</color> <color=#fab387>color</color> <color=#a6e3a1>tags</color>\n"
        "- Automatic line wrapping\n\n"
        "Zero coordinate guesswork."
    )
    card3.add(ui.Text(code_demo, size=12.0, color="#cdd6f4", line_spacing=5.0))

    card3.render(canvas, 920.0, 120.0)

    out_path = os.path.join(output_dir, "ui_components_preview.png")
    canvas.save(out_path)
    print(f"[OK] Feather UI Showcase saved to: {out_path}")

if __name__ == "__main__":
    generate_ui_preview()
