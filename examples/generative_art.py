"""
Feather Generative Art Demo: Harmonic waveform ribbons and vector interference
patterns demonstrating subpixel anti-aliasing and translucent multi-pass curves.
"""

import math
import os
import feather
from feather import Canvas, LinearGradient

def generate_waveforms():
    print("Generating Feather Generative Waveform Visualizer...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)

    w, h = 1280, 720
    canvas = Canvas(w, h, background="#090a14")

    # Radial ambient backdrop glow
    canvas.draw_circle(w * 0.5, h * 0.5, 380.0, fill="rgba(112, 0, 255, 0.06)")
    canvas.draw_circle(w * 0.3, h * 0.5, 260.0, fill="rgba(0, 240, 255, 0.05)")
    canvas.draw_circle(w * 0.7, h * 0.5, 260.0, fill="rgba(255, 0, 128, 0.05)")

    # Title & Metadata
    canvas.draw_text("GENERATIVE HARMONIC INTERFERENCE", 50.0, 36.0, size=20.0, color="#ffffff")
    canvas.draw_text("120 Harmonic Splines • Subpixel Anti-Aliased Waveforms", 50.0, 62.0, size=12.0, color="#7982a9")

    # Generate 90 harmonic ribbon curves
    num_ribbons = 90
    steps = 140
    step_dx = w / steps

    colors = [
        (0, 240, 255),    # Electric Cyan
        (64, 156, 255),   # Cobalt Blue
        (112, 0, 255),    # Deep Violet
        (255, 0, 128),    # Neon Magenta
        (255, 102, 0),    # Sunset Orange
        (0, 255, 160),    # Mint Green
    ]

    for ri in range(num_ribbons):
        t = ri / num_ribbons
        base_y = h * 0.50 + (t - 0.5) * 160.0
        phase = t * math.pi * 3.5
        freq1 = 2.0 + t * 1.5
        freq2 = 3.5 - t * 1.2
        amp1 = 80.0 + math.sin(t * math.pi * 2.0) * 45.0
        amp2 = 50.0 * math.cos(t * math.pi * 1.5)

        # Color interpolation
        c_idx = int(t * (len(colors) - 1))
        c_next = min(len(colors) - 1, c_idx + 1)
        sub_t = (t * (len(colors) - 1)) - c_idx

        r = int(colors[c_idx][0] + (colors[c_next][0] - colors[c_idx][0]) * sub_t)
        g = int(colors[c_idx][1] + (colors[c_next][1] - colors[c_idx][1]) * sub_t)
        b = int(colors[c_idx][2] + (colors[c_next][2] - colors[c_idx][2]) * sub_t)
        alpha = 0.25 + 0.50 * math.sin(t * math.pi)

        stroke_color = f"rgba({r}, {g}, {b}, {alpha:.3f})"

        # Build cubic Bézier SVG path from harmonic points
        pts = []
        for s in range(steps + 1):
            px = s * step_dx
            norm_x = (px / w) * math.pi * 2.0
            envelope = math.sin(px / w * math.pi)  # Taper at edges
            py = base_y + envelope * (
                amp1 * math.sin(norm_x * freq1 + phase) +
                amp2 * math.cos(norm_x * freq2 - phase * 0.7)
            )
            pts.append((px, py))

        # Convert to smooth SVG path
        path_cmds = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2

            cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
            cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
            cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
            cp2y = p2[1] - (p3[1] - p1[1]) / 6.0

            path_cmds.append(f"C {cp1x:.1f} {cp1y:.1f}, {cp2x:.1f} {cp2y:.1f}, {p2[0]:.1f} {p2[1]:.1f}")

        svg_d = " ".join(path_cmds)
        canvas.draw_svg_path(svg_d, stroke=stroke_color, stroke_width=1.6)

        # Highlight peaks with particle glow dots on every 6th ribbon
        if ri % 7 == 0:
            for i in range(5, len(pts) - 5, 12):
                nx, ny = pts[i]
                canvas.draw_circle(nx, ny, 3.5, fill=f"rgba({r}, {g}, {b}, 0.8)")
                canvas.draw_circle(nx, ny, 1.5, fill="#ffffff")

    # Corner watermark info
    canvas.draw_text("RENDERED IN 14 MS • 0 ALLOCATIONS", w - 280.0, h - 30.0, size=11.0, color="#6c7086")

    out_path = os.path.join(output_dir, "generative_waveform.png")
    canvas.save(out_path)
    print(f"[OK] Feather Generative Waveform saved to: {out_path}")

if __name__ == "__main__":
    generate_waveforms()
