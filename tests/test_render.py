"""
Visual quality test: renders shapes side-by-side (Pillow vs Feather)
to visually showcase anti-aliasing and vector quality.
"""

import os
from PIL import Image, ImageDraw
from feather import Canvas, LinearGradient, RadialGradient, Path

def generate_visual_comparison():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    w, h = 600, 600

    # 1. Pillow rendering (aliased/pixelated)
    pil_img = Image.new("RGBA", (w, h), (30, 30, 46, 255))
    draw = ImageDraw.Draw(pil_img)

    # Circle
    draw.ellipse([50, 50, 250, 250], fill=(243, 139, 168, 255), outline=(205, 214, 244, 255), width=3)

    # Angled lines
    for i in range(12):
        angle_deg = i * 15
        import math
        rad = math.radians(angle_deg)
        x2 = 450 + 120 * math.cos(rad)
        y2 = 150 + 120 * math.sin(rad)
        draw.line([(450, 150), (x2, y2)], fill=(137, 180, 250, 255), width=2)

    # Rounded rectangle
    draw.rounded_rectangle([50, 350, 300, 520], radius=24, fill=(166, 227, 161, 255), outline=(245, 224, 220, 255), width=3)

    pil_path = os.path.join(output_dir, "comparison_pillow.png")
    pil_img.save(pil_path)

    # 2. Feather rendering (smooth subpixel anti-aliasing & gradients)
    pf_canvas = Canvas(w, h, background="#1e1e2e")

    # Anti-aliased circle with radial gradient
    rad_grad = RadialGradient(150, 150, 100, stops=[(0.0, "#f38ba8"), (1.0, "#cba6f7")])
    pf_canvas.draw_circle(150, 150, 100, fill=rad_grad, stroke="#cdd6f4", stroke_width=3.0)

    # Smooth anti-aliased angled lines with round caps
    import math
    for i in range(12):
        angle_deg = i * 15
        rad = math.radians(angle_deg)
        x2 = 450 + 120 * math.cos(rad)
        y2 = 150 + 120 * math.sin(rad)
        pf_canvas.draw_line(450, 150, x2, y2, stroke="#89b4fa", stroke_width=2.0, line_cap="round")

    # Smooth rounded rectangle with linear gradient
    lin_grad = LinearGradient(50, 350, 300, 520, stops=[(0.0, "#a6e3a1"), (1.0, "#94e2d5")])
    pf_canvas.draw_rounded_rect(50, 350, 250, 170, rx=24, fill=lin_grad, stroke="#f5e0dc", stroke_width=3.0)

    # Smooth, beautifully curved SVG Heart path
    heart = (
        "M 460 415 "
        "C 460 390, 435 375, 410 375 "
        "C 382 375, 365 398, 365 430 "
        "C 365 470, 405 500, 460 535 "
        "C 515 500, 555 470, 555 430 "
        "C 555 398, 538 375, 510 375 "
        "C 485 375, 460 390, 460 415 Z"
    )
    pf_canvas.draw_svg_path(heart, fill="#f38ba8", stroke="#f5c2e7", stroke_width=2.5)

    pf_path = os.path.join(output_dir, "comparison_feather.png")
    pf_canvas.save(pf_path)

    # 3. Create a side-by-side comparison image
    side_by_side = Image.new("RGBA", (w * 2 + 20, h + 60), (17, 17, 27, 255))
    sbs_draw = ImageDraw.Draw(side_by_side)
    sbs_draw.text((w // 2 - 60, 20), "Pillow (PIL) - Aliased / Jagged", fill=(243, 139, 168, 255))
    sbs_draw.text((w + w // 2 - 60, 20), "Feather - Anti-Aliased & Smooth", fill=(166, 227, 161, 255))

    side_by_side.paste(pil_img, (0, 50))
    pf_pil = pf_canvas.to_pillow()
    side_by_side.paste(pf_pil, (w + 20, 50))

    sbs_path = os.path.join(output_dir, "side_by_side.png")
    side_by_side.save(sbs_path)

    print(f"[OK] Visual comparison generated at: {sbs_path}")

if __name__ == "__main__":
    generate_visual_comparison()
