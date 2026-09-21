"""
Feather Feature Showcase
Demonstrates anti-aliasing, linear/radial gradients, rounded rectangles,
custom vector paths, SVG paths, blend modes, and filter effects.
"""

from feather import Canvas, LinearGradient, RadialGradient, Path

def run_showcase():
    print("Creating Feather Showcase Image...")
    canvas = Canvas(1000, 700, background="#0f0f17")

    # 1. Header with linear gradient
    header_grad = LinearGradient(50, 40, 950, 40, stops=[
        (0.0, "#ff758c"),
        (0.5, "#ff7eb3"),
        (1.0, "#70a6ff"),
    ])
    canvas.draw_rounded_rect(50, 30, 900, 70, rx=18, fill=header_grad)

    # 2. Glassmorphic card 1: Anti-aliased geometric primitives
    canvas.draw_rounded_rect(50, 130, 420, 240, rx=20, fill="rgba(255, 255, 255, 0.05)", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.5)
    
    # Nested circles with radial gradients
    rad1 = RadialGradient(160, 250, 80, stops=[
        (0.0, "#f38ba8"),
        (0.8, "rgba(243, 139, 168, 0.4)"),
        (1.0, "rgba(243, 139, 168, 0.0)"),
    ])
    canvas.draw_circle(160, 250, 75, fill=rad1)
    canvas.draw_circle(160, 250, 75, stroke="#f38ba8", stroke_width=2.5)

    rad2 = RadialGradient(320, 250, 80, stops=[
        (0.0, "#89b4fa"),
        (0.8, "rgba(137, 180, 250, 0.4)"),
        (1.0, "rgba(137, 180, 250, 0.0)"),
    ])
    canvas.draw_circle(320, 250, 75, fill=rad2)
    canvas.draw_circle(320, 250, 75, stroke="#89b4fa", stroke_width=2.5)

    # 3. Glassmorphic card 2: SVG Paths & Custom Polygons
    canvas.draw_rounded_rect(530, 130, 420, 240, rx=20, fill="rgba(255, 255, 255, 0.05)", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.5)
    
    # Heart SVG (Smooth cubic Bézier curves)
    heart_svg = (
        "M 740 220 "
        "C 740 195, 715 180, 690 180 "
        "C 662 180, 645 203, 645 235 "
        "C 645 275, 685 305, 740 340 "
        "C 795 305, 835 275, 835 235 "
        "C 835 203, 818 180, 790 180 "
        "C 765 180, 740 195, 740 220 Z"
    )
    canvas.draw_svg_path(heart_svg, fill="#f38ba8", stroke="#eba0ac", stroke_width=2.5)

    # 4. Star Polygon
    star_points = []
    import math
    for i in range(10):
        r = 60 if i % 2 == 0 else 25
        angle = i * (math.pi / 5) - math.pi / 2
        star_points.append((620 + r * math.cos(angle), 250 + r * math.sin(angle)))
    canvas.draw_polygon(star_points, fill="#f9e2af", stroke="#fab387", stroke_width=2.0)

    # 5. Bottom card: Polylines & Smooth Curves
    canvas.draw_rounded_rect(50, 400, 900, 260, rx=20, fill="rgba(255, 255, 255, 0.05)", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.5)

    # Sinusoidal smooth curves
    for offset, color in enumerate(["#89dceb", "#94e2d5", "#a6e3a1", "#cba6f7"]):
        wave = Path()
        wave.move_to(80, 520 + offset * 15)
        for x in range(80, 920, 20):
            y = 520 + offset * 15 + math.sin((x + offset * 50) * 0.02) * 35
            wave.line_to(x, y)
        canvas.draw_path(wave, stroke=color, stroke_width=3.0)

    canvas.save("outputs/showcase.png")
    print("Saved showcase image to: outputs/showcase.png")

if __name__ == "__main__":
    run_showcase()
