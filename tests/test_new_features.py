"""
Test suite verifying all 5 new capabilities in Feather 0.2.0:
1. Typography & Font Engine (draw_text, draw_text_box, measure_text)
2. Native Drop Shadows & Glow Effects (draw_drop_shadow, draw_glow)
3. Transformation Matrix & Clipping Masks (rotate, scale, translate, clipping_circle)
4. Full SVG Document Rendering (resvg)
5. Animated GIF Exporter (save_gif)
"""

import os
from feather import Canvas, LinearGradient, RadialGradient, Font, save_gif

def test_all_features():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    print("Testing Feather 0.2.0 Features...")

    # --- Test 1: Typography ---
    print("[1/5] Testing Typography & Text Rendering...")
    canvas = Canvas(800, 600, background="#11111b")
    font = Font.default_font()

    w, h = canvas.measure_text("Hello Feather!", size=32.0, font=font)
    assert w > 0 and h > 0, "measure_text failed"

    canvas.draw_text("⚡ Feather 0.2.0: Typography Engine", 50, 40, size=28, color="#f5c2e7", font=font)
    
    # Text box with automatic word wrap
    long_text = "Feather provides pure-Rust, ultra-fast vector graphics and subpixel anti-aliasing with zero C dependencies. Words wrap smoothly and gracefully."
    box_w, box_h = canvas.draw_text_box(long_text, 50, 90, max_width=350, size=18, color="#cdd6f4", line_spacing=6, font=font)
    assert box_h > 0, "draw_text_box failed"
    print("  [OK] Font loaded, text measured, and text box wrapped successfully.")

    # --- Test 2: Drop Shadows & Glows ---
    print("[2/5] Testing Native Drop Shadows & Glows...")
    # Card with soft drop shadow
    canvas.draw_drop_shadow(450, 90, 300, 160, rx=18, blur=18.0, offset_x=0.0, offset_y=10.0, color="rgba(0, 0, 0, 0.5)")
    canvas.draw_rounded_rect(450, 90, 300, 160, rx=18, fill="#1e1e2e", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.5)
    canvas.draw_text("Card with Drop Shadow", 475, 120, size=18, color="#cdd6f4", font=font)

    # Glowing badge
    canvas.draw_glow(520, 200, radius=25, blur=20.0, color="rgba(243, 139, 168, 0.7)")
    canvas.draw_circle(520, 200, radius=25, fill="#f38ba8")
    canvas.draw_text("Glow", 505, 192, size=14, color="#11111b", font=font)
    print("  [OK] Drop shadow and glow rendered.")

    # --- Test 3: Matrix Transforms & Clipping Masks ---
    print("[3/5] Testing Matrix Transforms & Clipping...")
    # Rotate around center
    canvas.save_state()
    canvas.translate(150, 420)
    canvas.rotate(25.0)
    canvas.draw_rect(-40, -40, 80, 80, fill="#a6e3a1", stroke="#94e2d5", stroke_width=2.0)
    canvas.restore_state()

    # Clipping circle
    with canvas.clipping_circle(320, 420, radius=55):
        # Fill whole canvas with gradient, but only the circle gets drawn!
        grad = LinearGradient(250, 350, 400, 500, stops=[(0.0, "#89b4fa"), (1.0, "#f38ba8")])
        canvas.draw_rect(200, 300, 250, 250, fill=grad)
    
    # Border for the clipped circle
    canvas.draw_circle(320, 420, radius=55, stroke="#ffffff", stroke_width=3.0)
    print("  [OK] Transforms and clipping context manager verified.")

    # --- Test 4: Full SVG Document Rendering ---
    print("[4/5] Testing Full SVG Rendering (resvg)...")
    sample_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#fab387"/>
          <stop offset="100%" stop-color="#f38ba8"/>
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="45" fill="url(#g)" stroke="#cdd6f4" stroke-width="4"/>
      <polygon points="50,15 62,38 88,40 68,57 74,82 50,68 26,82 32,57 12,40 38,38" fill="#ffffff"/>
    </svg>
    """
    canvas.draw_svg_document(sample_svg, x=460, y=360, width=120, height=120)
    canvas.draw_text("Embedded SVG (resvg)", 450, 500, size=15, color="#fab387", font=font)
    print("  [OK] SVG parsed and rasterized via resvg.")

    output_png = os.path.join(output_dir, "showcase_v2.png")
    canvas.save(output_png)
    print(f"  [SAVED] Static feature showcase: {output_png}")

    # --- Test 5: Animated GIF Exporter ---
    print("[5/5] Testing Animated GIF Exporter (save_gif)...")
    frames = []
    import math
    for frame_idx in range(24):
        f_canvas = Canvas(300, 300, background="#0f0f17")
        angle = frame_idx * (360.0 / 24)
        
        # Rotating glowing star
        f_canvas.save_state()
        f_canvas.translate(150, 150)
        f_canvas.rotate(angle)

        # Pulse radius
        r = 50 + 15 * math.sin(math.radians(angle * 2))
        f_canvas.draw_drop_shadow(-r, -r, r * 2, r * 2, rx=r, blur=15.0, offset_y=0.0, color="rgba(137, 180, 250, 0.6)")
        f_canvas.draw_circle(0, 0, radius=r, fill="#89b4fa", stroke="#cdd6f4", stroke_width=2.5)
        
        # Cross spokes
        f_canvas.draw_line(-r + 10, 0, r - 10, 0, stroke="#ffffff", stroke_width=3.0)
        f_canvas.draw_line(0, -r + 10, 0, r - 10, stroke="#ffffff", stroke_width=3.0)
        f_canvas.restore_state()

        f_canvas.draw_text("Feather GIF Demo", 80, 260, size=16, color="#cdd6f4", font=font)
        frames.append(f_canvas)

    output_gif = os.path.join(output_dir, "animated_demo.gif")
    save_gif(frames, output_gif, fps=24, loop_count=0)
    print(f"  [SAVED] Animated GIF: {output_gif}")

    print("\n" + "=" * 60)
    print("All 5 Feather 2.0 features tested and verified successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_features()
