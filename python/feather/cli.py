"""
Feather CLI: Multi-core SIMD image processing and inspection tool.
"""

from __future__ import annotations
import argparse
import os
import sys
import time
import feather
from feather import Canvas


def cmd_info(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)

    c = Canvas.open(args.input)
    size_bytes = os.path.getsize(args.input)
    size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.2f} MB"

    print("=" * 45)
    print("[FEATHER] IMAGE TELEMETRY")
    print("=" * 45)
    print(f"File Path     : {os.path.abspath(args.input)}")
    print(f"Dimensions    : {c.width} x {c.height} px")
    print(f"Aspect Ratio  : {c.width / max(1, c.height):.2f} : 1")
    print(f"File Size     : {size_str}")
    print(f"Buffer Memory : {c.width * c.height * 4 / (1024 * 1024):.2f} MB (RGBA)")
    print("=" * 45)


def cmd_resize(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)

    output = args.output or f"resized_{os.path.basename(args.input)}"
    c = Canvas.open(args.input)

    w = args.width or int(c.width * (args.height / c.height))
    h = args.height or int(c.height * (args.width / c.width))

    t0 = time.perf_counter()
    resized = c.resize(w, h, filter=args.filter)
    resized.save(output)
    t1 = time.perf_counter()

    print(f"[OK] Resized {c.width}x{c.height} -> {w}x{h} ({args.filter}) in {(t1 - t0) * 1000:.2f} ms")
    print(f"   Saved output to: {output}")


def cmd_convert(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)

    base, _ = os.path.splitext(args.input)
    fmt = args.format.lower().lstrip(".")
    output = args.output or f"{base}.{fmt}"

    t0 = time.perf_counter()
    c = Canvas.open(args.input)
    c.save(output, quality=args.quality)
    t1 = time.perf_counter()

    print(f"[OK] Converted to {fmt.upper()} in {(t1 - t0) * 1000:.2f} ms")
    print(f"   Saved output to: {output}")


def cmd_blur(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)

    output = args.output or f"blurred_{os.path.basename(args.input)}"
    c = Canvas.open(args.input)

    t0 = time.perf_counter()
    blurred = c.blur(args.sigma)
    blurred.save(output)
    t1 = time.perf_counter()

    print(f"[OK] Applied Gaussian Blur (sigma={args.sigma}) in {(t1 - t0) * 1000:.2f} ms")
    print(f"   Saved output to: {output}")


def cmd_view(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)

    c = Canvas.open(args.input)
    print(f"[VIEWER] Opening 60 FPS interactive desktop window for: {args.input}")
    c.show(title=f"Feather Viewer - {os.path.basename(args.input)}")


def cmd_benchmark(args):
    print("=" * 55)
    print("[FEATHER] MULTI-CORE SIMD ENGINE BENCHMARKS")
    print("=" * 55)

    c = Canvas(1920, 1080, background="#11111b")

    # 1. Circle rendering
    t0 = time.perf_counter()
    for _ in range(5000):
        c.draw_circle(960, 540, 300, stroke="#89b4fa", stroke_width=2.0)
    t_circles = time.perf_counter() - t0

    # 2. Rounded rects
    t0 = time.perf_counter()
    for _ in range(5000):
        c.draw_rounded_rect(200, 200, 400, 300, rx=24, fill="rgba(255,255,255,0.05)")
    t_rects = time.perf_counter() - t0

    # 3. SIMD Resize
    t0 = time.perf_counter()
    for _ in range(20):
        _ = c.resize(800, 600, filter="lanczos3")
    t_resize = time.perf_counter() - t0

    # 4. Multi-threaded Blur
    t0 = time.perf_counter()
    for _ in range(10):
        _ = c.blur(sigma=5.0)
    t_blur = time.perf_counter() - t0

    print(f"* 5,000 Anti-Aliased Circles     : {5000 / t_circles:,.0f} ops/sec  ({t_circles * 1000:.1f} ms)")
    print(f"* 5,000 Bezier Rounded Rects     : {5000 / t_rects:,.0f} ops/sec  ({t_rects * 1000:.1f} ms)")
    print(f"* 1080p -> 800x600 Lanczos3 SIMD : {20 / t_resize:,.1f} FPS      ({t_resize / 20 * 1000:.2f} ms/frame)")
    print(f"* 1080p Rayon Multi-Core Blur    : {10 / t_blur:,.1f} FPS      ({t_blur / 10 * 1000:.2f} ms/frame)")
    print("=" * 55)
    print("All tests completed at native hardware speed.")


def main():
    parser = argparse.ArgumentParser(
        prog="feather",
        description="Feather: High-performance 2D vector graphics & image CLI",
    )
    parser.add_argument("--version", "-v", action="version", version=f"Feather {feather.__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # info
    p_info = subparsers.add_parser("info", help="Inspect image resolution and metadata")
    p_info.add_argument("input", help="Path to input image")

    # resize
    p_resize = subparsers.add_parser("resize", help="SIMD-accelerated image resize")
    p_resize.add_argument("input", help="Path to input image")
    p_resize.add_argument("-w", "--width", type=int, help="Target width")
    p_resize.add_argument("-H", "--height", type=int, help="Target height")
    p_resize.add_argument("-f", "--filter", default="lanczos3", choices=["nearest", "bilinear", "bicubic", "lanczos3"])
    p_resize.add_argument("-o", "--output", help="Output path")

    # convert
    p_convert = subparsers.add_parser("convert", help="Convert image formats (PNG, JPEG, WebP, BMP)")
    p_convert.add_argument("input", help="Path to input image")
    p_convert.add_argument("-f", "--format", default="webp", help="Target format (webp, png, jpeg, bmp)")
    p_convert.add_argument("-q", "--quality", type=int, default=85, help="Quality 1-100 (for WebP/JPEG)")
    p_convert.add_argument("-o", "--output", help="Output path")

    # blur
    p_blur = subparsers.add_parser("blur", help="Multi-threaded Gaussian blur")
    p_blur.add_argument("input", help="Path to input image")
    p_blur.add_argument("-s", "--sigma", type=float, default=4.0, help="Blur radius sigma")
    p_blur.add_argument("-o", "--output", help="Output path")

    # view
    p_view = subparsers.add_parser("view", help="Open image in 60 FPS interactive desktop window")
    p_view.add_argument("input", help="Path to input image")

    # benchmark
    subparsers.add_parser("benchmark", help="Run live multi-core SIMD engine benchmark")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "info": cmd_info,
        "resize": cmd_resize,
        "convert": cmd_convert,
        "blur": cmd_blur,
        "view": cmd_view,
        "benchmark": cmd_benchmark,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
