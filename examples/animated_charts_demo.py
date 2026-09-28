"""
Feather Animated Charts Demo:
Renders smooth 60 FPS transitions directly to an animated WebP file using cubic and bounce easing curves.
"""

import os
import feather
from feather import charts

def run_animation_demo():
    print("Generating Feather Animated Chart Showcase...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "animated_chart_demo.webp")

    # Create an elegant high-tech multi-series bar chart
    bar = charts.BarChart(
        width=800,
        height=450,
        title="Throughput Acceleration (MB/s)",
        subtitle="Smooth cubic ease-out entrance animation with subpixel pill caps",
        theme="dark",
        corner_radius=6.0,
        show_values=True,
    )
    bar.set_categories(["Raw Vectors", "Alpha Blend", "Gradients", "Batch Blur", "Font Rendering"])
    bar.add_series("Feather (SIMD)", [850, 720, 940, 680, 890], color="#89b4fa")
    bar.add_series("Pillow (Baseline)", [180, 150, 210, 110, 195], color="#f38ba8")

    # Render smooth 60 FPS entrance animation directly to WebP
    bar.render_animation(
        out_path,
        duration_seconds=1.6,
        fps=30,
        easing="cubic_out",
        loop_count=0,
        quality=90.0,
        end_pause_seconds=1.0,
    )

    print(f"Animated chart exported to: {out_path} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    run_animation_demo()
