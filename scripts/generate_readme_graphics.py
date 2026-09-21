"""
Generates high-fidelity graphics for the Feather GitHub README.
Uses Feather itself to render its own promotional graphics!
"""

import os
import math
from feather import Canvas, Font, LinearGradient, RadialGradient, save_gif

def generate_all_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    font = Font.default_font()

    # =========================================================================
    # 1. HERO BANNER (1200 x 420)
    # =========================================================================
    print("[1/4] Generating hero_banner.png...")
    bw, bh = 1200, 440
    banner = Canvas(bw, bh, background="#0a0c14")

    # Subtle ambient background glows
    banner.draw_glow(250, 100, radius=180, blur=90.0, color="rgba(99, 102, 241, 0.22)")
    banner.draw_glow(950, 320, radius=200, blur=100.0, color="rgba(236, 72, 153, 0.18)")
    banner.draw_glow(600, 220, radius=220, blur=110.0, color="rgba(56, 189, 248, 0.15)")

    # Tech grid dots
    for gx in range(0, bw, 30):
        for gy in range(0, bh, 30):
            banner.draw_circle(gx, gy, 0.8, fill="#1e2436")

    # Gradient Title Accent Bar
    top_bar_grad = LinearGradient(60, 40, 1140, 40, stops=[
        (0.0, "#6366f1"),
        (0.35, "#38bdf8"),
        (0.7, "#ec4899"),
        (1.0, "#f59e0b")
    ])
    banner.draw_rounded_rect(60, 40, 1080, 4, rx=2, fill=top_bar_grad)

    # Title Typography
    banner.draw_text("FEATHER", 60, 68, size=52, color="#f8fafc", font=font)
    banner.draw_text("HIGH-PERFORMANCE 2D VECTOR GRAPHICS & IMAGE ENGINE FOR PYTHON", 60, 134, size=15, color="#94a3b8", font=font)
    banner.draw_text("Built from scratch in Rust • Zero C Dependencies • SIMD Accelerated • Subpixel Anti-Aliasing", 60, 160, size=13, color="#64748b", font=font)

    # Feature Pill Badges
    badges = [
        ("SIMD AVX2 / NEON", "#6366f1", "#1e1b4b"),
        ("Subpixel AA", "#38bdf8", "#082f49"),
        ("Fontdue Typography", "#a855f7", "#3b0764"),
        ("32-bit WebP & APNG", "#ec4899", "#500724"),
        ("60 FPS Live Viewer", "#10b981", "#022c22"),
        ("Matrix Transforms", "#f59e0b", "#451a03"),
    ]
    bx = 60
    for label, border_col, bg_col in badges:
        banner.draw_rounded_rect(bx, 195, 172, 32, rx=16, fill=bg_col, stroke=border_col, stroke_width=1.5)
        banner.draw_text(label, bx + 18, 204, size=11, color="#f1f5f9", font=font)
        bx += 182

    # Bottom Glassmorphic Preview Cards
    # Card 1: Benchmark callout
    banner.draw_drop_shadow(60, 250, 340, 150, rx=12, blur=18.0, offset_y=8.0, color="rgba(0,0,0,0.5)")
    banner.draw_rounded_rect(60, 250, 340, 150, rx=12, fill="#111422", stroke="#252c42", stroke_width=1.5)
    banner.draw_text("ULTRA-FAST PERFORMANCE", 80, 270, size=13, color="#38bdf8", font=font)
    banner.draw_text("• 60 FPS Interactive Desktop Window", 80, 298, size=12, color="#f8fafc", font=font)
    banner.draw_text("• 68% Smaller Animation Size (WebP)", 80, 324, size=12, color="#f8fafc", font=font)
    banner.draw_text("• Zero GIL Stalls with Multi-Core Rayon", 80, 350, size=12, color="#f8fafc", font=font)

    # Card 2: Code preview card
    banner.draw_drop_shadow(425, 250, 340, 150, rx=12, blur=18.0, offset_y=8.0, color="rgba(0,0,0,0.5)")
    banner.draw_rounded_rect(425, 250, 340, 150, rx=12, fill="#111422", stroke="#252c42", stroke_width=1.5)
    banner.draw_text("PYTHONIC & CONCISE API", 445, 270, size=13, color="#ec4899", font=font)
    banner.draw_text("canvas = Canvas(1000, 700)", 445, 298, size=11, color="#cbd5e1", font=font)
    banner.draw_text("canvas.draw_rounded_rect(..., rx=16)", 445, 322, size=11, color="#cbd5e1", font=font)
    banner.draw_text("canvas.show(title='Live CAD')", 445, 346, size=11, color="#cbd5e1", font=font)

    # Card 3: Modern outputs card
    banner.draw_drop_shadow(790, 250, 350, 150, rx=12, blur=18.0, offset_y=8.0, color="rgba(0,0,0,0.5)")
    banner.draw_rounded_rect(790, 250, 350, 150, rx=12, fill="#111422", stroke="#252c42", stroke_width=1.5)
    banner.draw_text("COMPLETE CREATIVE SUITE", 810, 270, size=13, color="#10b981", font=font)
    banner.draw_text("• WebP, APNG, GIF & PNG Exporters", 810, 298, size=12, color="#f8fafc", font=font)
    banner.draw_text("• Full SVG Document Rasterization", 810, 324, size=12, color="#f8fafc", font=font)
    banner.draw_text("• Zero-Copy NumPy & Pillow Bridge", 810, 350, size=12, color="#f8fafc", font=font)

    hero_path = os.path.join(assets_dir, "hero_banner.png")
    banner.save(hero_path)
    print(f"   [OK] Saved -> {hero_path}")

    # =========================================================================
    # 2. INTERACTIVE WINDOW PREVIEW (800 x 500)
    # =========================================================================
    print("[2/4] Generating interactive_preview.png...")
    iw, ih = 800, 520
    window_preview = Canvas(iw, ih, background="#0d0f17")

    # Window titlebar chrome
    window_preview.draw_rounded_rect(40, 30, 720, 460, rx=10, fill="#161922", stroke="#2d3748", stroke_width=2.0)
    window_preview.draw_rounded_rect(40, 30, 720, 38, rx=10, fill="#1e2433")
    # Traffic light buttons
    window_preview.draw_circle(62, 49, 6, fill="#f56565")
    window_preview.draw_circle(82, 49, 6, fill="#ecc94b")
    window_preview.draw_circle(102, 49, 6, fill="#48c78e")

    # Window Title HUD Loupe text
    window_preview.draw_text("Feather Viewer | 1000x700 | 125% | (450, 320) #48C78E rgba(72, 199, 142, 255)", 130, 43, size=11, color="#cbd5e0", font=font)

    # Canvas Area with dark checkerboard & CAD drawing inside
    cx, cy = 400, 280
    window_preview.draw_circle(cx, cy, 110, stroke="#2d3748", stroke_width=1.5)
    window_preview.draw_circle(cx, cy, 70, stroke="#2d3748", stroke_width=1.5)
    window_preview.draw_circle(cx, cy, 30, stroke="#2d3748", stroke_width=1.5)

    # Crosshair HUD
    window_preview.draw_line(cx - 130, cy, cx + 130, cy, stroke="rgba(99, 179, 237, 0.3)", stroke_width=1.0)
    window_preview.draw_line(cx, cy - 130, cx, cy + 130, stroke="rgba(99, 179, 237, 0.3)", stroke_width=1.0)

    # Signal vector
    window_preview.draw_line(cx, cy, cx + 85, cy - 65, stroke="#48c78e", stroke_width=2.5)
    window_preview.draw_glow(cx + 85, cy - 65, radius=12, blur=12.0, color="rgba(72, 199, 142, 0.7)")
    window_preview.draw_circle(cx + 85, cy - 65, 5, fill="#48c78e")

    # Floating HUD Control Guide Card
    window_preview.draw_rounded_rect(70, 390, 660, 75, rx=6, fill="rgba(15, 17, 23, 0.85)", stroke="#3182ce", stroke_width=1.5)
    window_preview.draw_text("Zoom: Scroll Wheel  •  Pan: Left Click Drag  •  Live Pixel Inspector Loupe", 90, 408, size=11, color="#f0f4f8", font=font)
    window_preview.draw_text("Spacebar: Play/Pause  •  [R]: Reset View  •  [S]: Save Snapshot  •  [Esc]: Exit", 90, 432, size=11, color="#94a3b8", font=font)

    interactive_path = os.path.join(assets_dir, "interactive_preview.png")
    window_preview.save(interactive_path)
    print(f"   [OK] Saved -> {interactive_path}")

    # =========================================================================
    # 3. COPY EXISTING TEST ARTIFACTS TO ASSETS
    # =========================================================================
    print("[3/4] Copying schematic and comparison images to assets/...")
    import shutil
    root_dir = os.path.join(os.path.dirname(__file__), "..")

    schematic_src = os.path.join(root_dir, "schematic_output.png")
    if os.path.exists(schematic_src):
        shutil.copyfile(schematic_src, os.path.join(assets_dir, "schematic_demo.png"))
        print("   [OK] Copied schematic_demo.png")

    side_by_side_src = os.path.join(root_dir, "outputs", "side_by_side.png")
    if os.path.exists(side_by_side_src):
        shutil.copyfile(side_by_side_src, os.path.join(assets_dir, "side_by_side.png"))
        shutil.copyfile(side_by_side_src, os.path.join(assets_dir, "comparison_feather_vs_pillow.png"))
        print("   [OK] Copied side_by_side.png & comparison_feather_vs_pillow.png")

    # =========================================================================
    # 4. ANIMATED SHOWCASE GIF (400 x 300, 30 frames)
    # =========================================================================
    print("[4/4] Generating animated_radar.gif for README...")
    radar_frames = []
    num_frames = 24
    rw, rh = 480, 320

    for fi in range(num_frames):
        theta = (fi / num_frames) * 2.0 * math.pi
        c = Canvas(rw, rh, background="#111420")

        # Subtle CAD grid
        for x in range(0, rw, 24):
            for y in range(0, rh, 24):
                c.draw_circle(x, y, 0.8, fill="#1c2233")

        rcx, rcy = 240, 160
        c.draw_circle(rcx, rcy, 100, stroke="#242e44", stroke_width=1.5)
        c.draw_circle(rcx, rcy, 65, stroke="#242e44", stroke_width=1.5)
        c.draw_circle(rcx, rcy, 30, stroke="#242e44", stroke_width=1.5)

        # Radar sweep beam
        bx = rcx + math.cos(theta) * 100
        by = rcy + math.sin(theta) * 100
        c.draw_line(rcx, rcy, bx, by, stroke="#48c78e", stroke_width=2.5)

        # Glowing ping targets
        t1x = rcx + math.cos(theta * 0.5) * 55
        t1y = rcy + math.sin(theta * 0.5) * 55
        c.draw_glow(t1x, t1y, radius=10, blur=12.0, color="rgba(245, 101, 101, 0.7)")
        c.draw_circle(t1x, t1y, 4, fill="#f56565")

        t2x = rcx - math.cos(theta * 0.7) * 75
        t2y = rcy - math.sin(theta * 0.7) * 75
        c.draw_glow(t2x, t2y, radius=10, blur=12.0, color="rgba(56, 189, 248, 0.7)")
        c.draw_circle(t2x, t2y, 4, fill="#38bdf8")

        # Live telemetry HUD text
        c.draw_rounded_rect(20, 20, 200, 48, rx=6, fill="rgba(22, 27, 42, 0.85)", stroke="#38bdf8", stroke_width=1.0)
        c.draw_text("FEATHER 60 FPS ENGINE", 30, 28, size=11, color="#f8fafc", font=font)
        c.draw_text(f"RADAR_AZIMUTH: {int(math.degrees(theta))} deg", 30, 46, size=9, color="#94a3b8", font=font)

        radar_frames.append(c)

    radar_gif_path = os.path.join(assets_dir, "animated_radar.gif")
    save_gif(radar_frames, radar_gif_path, fps=24, loop_count=0)
    print(f"   [OK] Saved animated_radar.gif -> {radar_gif_path}")

    print("\nAll README graphics generated successfully!")

if __name__ == "__main__":
    generate_all_assets()
