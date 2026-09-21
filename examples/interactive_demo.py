"""
Feather 0.4.0 Interactive Viewer Demo
Demonstrates the real-time 60 FPS desktop window viewer:
- Interactive Pan: Left-click and drag
- Smooth Zoom: Mouse wheel (centered at cursor)
- Live Pixel Loupe: Hovering displays (X, Y) and RGBA/Hex color live in title bar
- View Reset: Press 'R' to re-center
- Instant Snapshot: Press 'S' to save current view
- Animation Controls: Space to Pause/Play, Left/Right arrow keys to step
- Exit: Press Esc or Q
"""

import math
from feather import Canvas, Font, show_interactive

def run_interactive_demo():
    print("Generating interactive CAD / Circuit Animation frames...")
    font = Font.default_font()
    frames = []
    total_frames = 60
    w, h = 900, 600

    for i in range(total_frames):
        t = (i / total_frames) * 2.0 * math.pi
        c = Canvas(w, h, background="#161922")

        # 1. Subtle CAD dot grid
        for x in range(0, w, 25):
            for y in range(0, h, 25):
                c.draw_circle(x, y, 1.0, fill="#252a38")

        # 2. Header HUD
        c.draw_rounded_rect(30, 25, 460, 65, rx=8, fill="#1e2433", stroke="#63b3ed", stroke_width=1.5)
        c.draw_text("FEATHER 0.4.0 INTERACTIVE VIEWER", 45, 40, size=16, color="#f0f4f8", font=font)
        c.draw_text("Scroll: Zoom | Drag: Pan | Space: Play/Pause | R: Reset | S: Save", 45, 65, size=11, color="#94a3b8", font=font)

        # 3. Rotating radar / signal beacon in center
        cx, cy = 450, 320
        c.draw_circle(cx, cy, 140, stroke="#2d3748", stroke_width=1.5)
        c.draw_circle(cx, cy, 90, stroke="#2d3748", stroke_width=1.5)
        c.draw_circle(cx, cy, 40, stroke="#2d3748", stroke_width=1.5)

        # Sweeping radar beam
        beam_x = cx + math.cos(t) * 140
        beam_y = cy + math.sin(t) * 140
        c.draw_line(cx, cy, beam_x, beam_y, stroke="#48c78e", stroke_width=2.5)

        # Glowing target blips
        blip1_x = cx + math.cos(t * 0.5) * 80
        blip1_y = cy + math.sin(t * 0.5) * 80
        c.draw_glow(blip1_x, blip1_y, radius=12, blur=15.0, color="rgba(245, 101, 101, 0.7)")
        c.draw_circle(blip1_x, blip1_y, 4, fill="#f56565")
        c.draw_text("BLIP_ALPHA", blip1_x + 8, blip1_y - 6, size=10, color="#f56565", font=font)

        # IC Box with pulsating bus activity
        c.draw_rounded_rect(650, 240, 180, 160, rx=8, fill="#1e2433", stroke="#a0aec0", stroke_width=2.0)
        c.draw_text("SIGNAL_DSP_CORE", 670, 260, size=13, color="#f0f4f8", font=font)
        activity_color = "#48c78e" if (i % 6 < 3) else "#ecc94b"
        c.draw_circle(670, 300, 5, fill=activity_color)
        c.draw_text(f"CLK: {50 + (i*2)%20} MHz", 685, 294, size=11, color="#cbd5e0", font=font)

        frames.append(c)

    print("\nOpening Feather Interactive Viewer Window...")
    print("Controls:")
    print("  • Scroll Wheel: Smooth Zoom in/out at cursor")
    print("  • Left Drag: Pan around canvas")
    print("  • Hover Mouse: Live (X, Y) pixel color loupe in title bar")
    print("  • Spacebar: Pause / Resume animation")
    print("  • Left/Right Arrow Keys: Step through frames")
    print("  • Press 'R': Reset zoom and pan")
    print("  • Press 'S': Save snapshot of current view")
    print("  • Press 'Esc' or 'Q': Close window")

    show_interactive(frames, title="Feather Live CAD / Signal Viewer", fps=30)

if __name__ == "__main__":
    run_interactive_demo()
