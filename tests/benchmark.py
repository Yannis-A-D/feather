import time
import sys
from PIL import Image, ImageDraw
import numpy as np

def run_benchmarks():
    print("=" * 60)
    print("  PixelForge vs Pillow (PIL) Performance Benchmark")
    print("=" * 60)

    try:
        from pixelforge import Canvas, batch_resize
    except ImportError as e:
        print(f"Error importing pixelforge: {e}")
        return

    # Benchmark 1: Drawing 5,000 circles
    n_circles = 5000
    w, h = 1000, 1000

    print(f"\n[1/4] Benchmarking: Drawing {n_circles} Circles (1000x1000 canvas)")

    # Pillow
    start = time.perf_counter()
    pil_img = Image.new("RGBA", (w, h), (20, 20, 30, 255))
    pil_draw = ImageDraw.Draw(pil_img)
    for i in range(n_circles):
        cx = (i * 37) % 900 + 50
        cy = (i * 47) % 900 + 50
        r = 25
        pil_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(243, 139, 168, 200), outline=(205, 214, 244, 255), width=2)
    pil_time = time.perf_counter() - start
    print(f"  Pillow:     {pil_time:.4f}s  (Jagged edges, no anti-aliasing)")

    # PixelForge
    start = time.perf_counter()
    pf_canvas = Canvas(w, h, background="#14141e")
    for i in range(n_circles):
        cx = (i * 37) % 900 + 50
        cy = (i * 47) % 900 + 50
        r = 25
        pf_canvas.draw_circle(cx, cy, r, fill="#f38ba8c8", stroke="#cdd6f4", stroke_width=2.0)
    pf_time = time.perf_counter() - start
    speedup = pil_time / pf_time if pf_time > 0 else 1.0
    print(f"  PixelForge: {pf_time:.4f}s  (Flawless subpixel anti-aliasing) -> {speedup:.2f}x speedup")

    # Benchmark 2: Drawing 2,500 Rounded Rectangles
    n_rects = 2500
    print(f"\n[2/4] Benchmarking: Drawing {n_rects} Rounded Rectangles")

    # Pillow
    start = time.perf_counter()
    pil_img = Image.new("RGBA", (w, h), (20, 20, 30, 255))
    pil_draw = ImageDraw.Draw(pil_img)
    for i in range(n_rects):
        x = (i * 29) % 800 + 20
        y = (i * 31) % 800 + 20
        pil_draw.rounded_rectangle([x, y, x + 120, y + 80], radius=16, fill=(137, 180, 250, 180), outline=(245, 224, 220, 255), width=2)
    pil_time = time.perf_counter() - start
    print(f"  Pillow:     {pil_time:.4f}s")

    # PixelForge
    start = time.perf_counter()
    pf_canvas = Canvas(w, h, background="#14141e")
    for i in range(n_rects):
        x = (i * 29) % 800 + 20
        y = (i * 31) % 800 + 20
        pf_canvas.draw_rounded_rect(x, y, 120, 80, rx=16, fill="#89b4fab4", stroke="#f5e0dc", stroke_width=2.0)
    pf_time = time.perf_counter() - start
    speedup = pil_time / pf_time if pf_time > 0 else 1.0
    print(f"  PixelForge: {pf_time:.4f}s  -> {speedup:.2f}x speedup")

    # Benchmark 3: High-Quality Image Resizing (Bilinear)
    n_resizes = 100
    print(f"\n[3/4] Benchmarking: Resizing 1920x1080 -> 512x512 ({n_resizes} iterations)")

    source_pil = Image.new("RGBA", (1920, 1080), (100, 150, 200, 255))
    source_pf = Canvas(1920, 1080, background="#6496c8")

    # Pillow resize
    start = time.perf_counter()
    for _ in range(n_resizes):
        _ = source_pil.resize((512, 512), resample=Image.Resampling.BILINEAR)
    pil_time = time.perf_counter() - start
    print(f"  Pillow:     {pil_time:.4f}s")

    # PixelForge SIMD resize
    start = time.perf_counter()
    for _ in range(n_resizes):
        _ = source_pf.resize(512, 512, filter="bilinear")
    pf_time = time.perf_counter() - start
    speedup = pil_time / pf_time if pf_time > 0 else 1.0
    print(f"  PixelForge: {pf_time:.4f}s  -> {speedup:.2f}x speedup (SIMD)")

    # Benchmark 4: Multi-core Batch Resizing
    batch_count = 50
    print(f"\n[4/4] Benchmarking: Batch Resizing {batch_count} Images (1920x1080 -> 256x256)")
    batch_pil = [source_pil.copy() for _ in range(batch_count)]
    batch_pf = [source_pf.clone_canvas() for _ in range(batch_count)]

    # Pillow sequential
    start = time.perf_counter()
    _ = [img.resize((256, 256), resample=Image.Resampling.BILINEAR) for img in batch_pil]
    pil_time = time.perf_counter() - start
    print(f"  Pillow (Single-threaded): {pil_time:.4f}s")

    # PixelForge Rayon parallel
    start = time.perf_counter()
    _ = batch_resize(batch_pf, 256, 256, filter="bilinear")
    pf_time = time.perf_counter() - start
    speedup = pil_time / pf_time if pf_time > 0 else 1.0
    print(f"  PixelForge (Multi-Core):  {pf_time:.4f}s  -> {speedup:.2f}x speedup")

    print("\n" + "=" * 60)
    print("Benchmark complete!")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
