"""
Feather Charts Showcase: Generate an executive multi-panel analytics dashboard
demonstrating AreaChart, BarChart, DonutChart, RadarChart, and Gauge.
"""

import os
import feather
from feather import Canvas, charts

def generate_dashboard():
    print("Generating Feather Charts Showcase Dashboard...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Main Canvas (1400 x 960) with deep Catppuccin Mocha aesthetic
    dashboard = Canvas(1400, 960, background="#11111b")

    # Header Banner
    dashboard.draw_text("FEATHER ANALYTICS ENGINE", 50.0, 36.0, size=24.0, color="#ffffff")
    dashboard.draw_text("Real-Time Telemetry & Vector Graphics Metrics • 60 FPS Subpixel Anti-Aliased", 50.0, 68.0, size=13.0, color="#6c7086")


    # -------------------------------------------------------------------------
    # Panel 1: Area Chart (Top Half: 1300 x 360)
    # -------------------------------------------------------------------------
    area = charts.AreaChart(
        width=1300,
        height=350,
        title="Network Throughput & Frame Latency",
        subtitle="Smooth cubic Bézier spline interpolation with linear gradient area fills",
        theme="dark",
        smooth=True,
    )
    area.set_x_labels(["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "24:00"])
    area.add_series("Inbound (MB/s)", [140, 220, 180, 490, 620, 850, 710, 530, 920], color="#89b4fa", fill_opacity=0.3)
    area.add_series("Outbound (MB/s)", [80, 110, 95, 240, 380, 490, 420, 310, 580], color="#a6e3a1", fill_opacity=0.25)
    
    area_c = area.render()
    dashboard.draw_image(area_c, 50.0, 100.0)

    # -------------------------------------------------------------------------
    # Panel 2: Bar Chart (Bottom Left: 430 x 430)
    # -------------------------------------------------------------------------
    bar = charts.BarChart(
        width=410,
        height=430,
        title="Benchmarks (FPS)",
        subtitle="Higher is better",
        theme="dark",
        corner_radius=6.0,
    )
    bar.set_categories(["Lines", "Beziers", "Circles", "SVG"])
    bar.add_series("Feather", [1420, 980, 1650, 820], color="#89b4fa")
    bar.add_series("Pillow", [310, 180, 420, 120], color="#f38ba8")
    
    bar_c = bar.render()
    dashboard.draw_image(bar_c, 50.0, 480.0)

    # -------------------------------------------------------------------------
    # Panel 3: Donut Chart (Bottom Center: 430 x 430)
    # -------------------------------------------------------------------------
    donut = charts.DonutChart(
        width=410,
        height=430,
        title="Memory Allocation",
        subtitle="Zero-copy buffer segmentation",
        theme="dark",
        cutout_ratio=0.62,
        center_text="4.2 GB",
        center_subtext="Total VRAM",
    )
    donut.add_slice("Pixel Buffers", 48.0, color="#89b4fa")
    donut.add_slice("Glyph Atlas", 24.0, color="#cba6f7")
    donut.add_slice("Clip Masks", 16.0, color="#a6e3a1")
    donut.add_slice("Rayon Threads", 12.0, color="#fab387")

    donut_c = donut.render()
    dashboard.draw_image(donut_c, 495.0, 480.0)

    # -------------------------------------------------------------------------
    # Panel 4: Radar & Gauge (Bottom Right: 410 x 430)
    # -------------------------------------------------------------------------
    radar = charts.RadarChart(
        width=410,
        height=430,
        title="Engine Profile",
        subtitle="Capability scores",
        theme="dark",
    )
    radar.set_axes(["Anti-Aliasing", "Concurrency", "SIMD", "Filters", "Formats", "Low-Memory"])
    radar.add_series("Feather", [98, 95, 92, 88, 94, 90], color="#94e2d5")
    radar.add_series("Legacy", [35, 10, 20, 40, 50, 60], color="#f38ba8")

    radar_c = radar.render()
    dashboard.draw_image(radar_c, 940.0, 480.0)

    # Save to assets
    out_path = os.path.join(output_dir, "charts_dashboard.png")
    dashboard.save(out_path)
    print(f"[OK] Feather Charts Dashboard saved to: {out_path}")

if __name__ == "__main__":
    generate_dashboard()
