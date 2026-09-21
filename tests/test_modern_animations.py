"""
Comprehensive test suite for Feather 0.3.0 Modern Animation Formats:
- Animated WebP (lossless & lossy)
- Animated PNG / APNG (lossless 32-bit RGBA)
- Animated GIF
- Unified save_animation auto-detection
"""

import os
import math
from feather import Canvas, Font, LinearGradient, save_apng, save_webp, save_gif, save_animation

def test_animations():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    font = Font.default_font()

    print("Generating animated frames for test...")
    frames = []
    num_frames = 24
    width, height = 300, 300

    for i in range(num_frames):
        angle = (i / num_frames) * 2.0 * math.pi
        c = Canvas(width, height, background="#0f111a")

        # Rotating gradient star / spinner
        cx, cy = width / 2.0, height / 2.0
        c.save_state()
        c.translate(cx, cy)
        c.rotate(math.degrees(angle))

        # Glowing circles
        c.draw_glow(0, 0, radius=35, blur=18.0, color="rgba(99, 179, 237, 0.6)")
        c.draw_rounded_rect(-30, -30, 60, 60, rx=12, fill="#3182ce", stroke="#63b3ed", stroke_width=2.0)
        c.restore_state()

        # Orbiting satellite with alpha trail
        sx = cx + math.cos(angle) * 80
        sy = cy + math.sin(angle) * 80
        c.draw_circle(sx, sy, 10, fill="#f6ad55", stroke="#ecc94b", stroke_width=2.0)

        # Frame counter text
        c.draw_text(f"Frame {i+1}/{num_frames}", 15, 20, size=14, color="#e2e8f0", font=font)
        frames.append(c)

    print("1. Testing Animated WebP (Lossless)...")
    webp_lossless = os.path.join(out_dir, "test_spinner_lossless.webp")
    save_webp(frames, webp_lossless, fps=24, loop_count=0, lossless=True)
    assert os.path.exists(webp_lossless)
    lossless_sz = os.path.getsize(webp_lossless)
    print(f"   [OK] WebP Lossless saved: {lossless_sz:,} bytes")

    print("2. Testing Animated WebP (Lossy Q=80)...")
    webp_lossy = os.path.join(out_dir, "test_spinner_lossy.webp")
    save_webp(frames, webp_lossy, fps=24, loop_count=0, quality=80.0)
    assert os.path.exists(webp_lossy)
    lossy_sz = os.path.getsize(webp_lossy)
    print(f"   [OK] WebP Lossy saved: {lossy_sz:,} bytes")

    print("3. Testing Animated PNG / APNG...")
    apng_path = os.path.join(out_dir, "test_spinner.apng")
    save_apng(frames, apng_path, fps=24, loop_count=0)
    assert os.path.exists(apng_path)
    apng_sz = os.path.getsize(apng_path)
    print(f"   [OK] APNG saved: {apng_sz:,} bytes")

    print("4. Testing Animated GIF...")
    gif_path = os.path.join(out_dir, "test_spinner.gif")
    save_gif(frames, gif_path, fps=24, loop_count=0)
    assert os.path.exists(gif_path)
    gif_sz = os.path.getsize(gif_path)
    print(f"   [OK] GIF saved: {gif_sz:,} bytes")

    print("5. Testing Unified save_animation auto-detection...")
    auto_webp = os.path.join(out_dir, "auto_detected.webp")
    auto_apng = os.path.join(out_dir, "auto_detected.png")
    auto_gif = os.path.join(out_dir, "auto_detected.gif")

    save_animation(frames, auto_webp, fps=24)
    save_animation(frames, auto_apng, fps=24)
    save_animation(frames, auto_gif, fps=24)

    assert os.path.exists(auto_webp) and os.path.getsize(auto_webp) > 0
    assert os.path.exists(auto_apng) and os.path.getsize(auto_apng) > 0
    assert os.path.exists(auto_gif) and os.path.getsize(auto_gif) > 0
    print("   [OK] Unified auto-detection works seamlessly for .webp, .png, and .gif!")

    print("\n--- Summary Comparison ---")
    print(f"GIF size:          {gif_sz:,} bytes (256 colors)")
    print(f"APNG size:         {apng_sz:,} bytes (Lossless 32-bit RGBA)")
    print(f"WebP Lossless:     {lossless_sz:,} bytes (Lossless 32-bit RGBA)")
    print(f"WebP Lossy (Q=80): {lossy_sz:,} bytes (Compression: {100 - (lossy_sz/gif_sz * 100):.1f}% smaller than GIF!)")

if __name__ == "__main__":
    test_animations()
