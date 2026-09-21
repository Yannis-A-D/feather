# 🪶 Feather

[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange.svg?logo=rust)](https://www.rust-lang.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SIMD Accelerated](https://img.shields.io/badge/SIMD-AVX2%20%7C%20SSE4.1%20%7C%20NEON-red.svg)](https://github.com)

🤖 *Note: This README documentation was created by AI.*

**Feather** is a high-performance, memory-safe 2D vector graphics and image processing extension for Python, built from the ground up in **Rust**.

Designed as a modern, superior alternative to Pillow's (`PIL.ImageDraw`) rendering engine, Feather provides **flawless subpixel anti-aliasing**, **feathered soft edges**, **SIMD acceleration**, **modern typography**, **native drop shadows**, **clipping masks**, **SVG rendering with `resvg`**, **animated GIFs**, and seamless integration with **NumPy** and **Pillow**.

---

## 🚀 Why Feather?

| Feature | Pillow (`PIL.ImageDraw`) | Feather |
| :--- | :--- | :--- |
| **Anti-Aliasing** | ❌ Jagged, pixelated edges | 🪶 **Flawless subpixel anti-aliasing & soft edges** |
| **Typography & Text Layout** | ⚠️ Clunky bounds, no word-wrap | 🪶 **Subpixel fontdue engine with automatic word-wrap** |
| **Drop Shadows & Glows** | ❌ None (requires 15+ lines of blur hacks) | 🪶 **Native 1-line diffused drop shadows & glows** |
| **Clipping Masks** | ⚠️ Manual `putalpha` masks | 🪶 **Native context managers (`clipping_circle`, etc.)** |
| **Transformation Matrix** | ⚠️ Limited image-level transforms | 🪶 **State stack: `rotate`, `scale`, `translate`** |
| **SVG File Rendering** | ❌ None (requires CairoSVG + GTK DLLs) | 🪶 **Built-in pure Rust `resvg` (0 C dependencies)** |
| **Live Interactive Viewer** | ❌ None (only slow external Photo Viewer) | 🪶 **60 FPS desktop window with pan, zoom, & live pixel loupe** |
| **Modern Animation (WebP/APNG)** | ❌ Poor/None | 🪶 **68% smaller WebP & 32-bit lossless APNG** |
| **Rounded Rectangles** | ⚠️ Basic or broken corner radii | 🪶 **Smooth bezier rounded corners (`rx`, `ry`)** |
| **Gradients** | ❌ None (requires manual loops) | 🪶 **Linear & Radial Gradients with stops** |
| **Vector Paths** | ❌ Limited polylines | 🪶 **Quadratic/Cubic Beziers & SVG `d` Paths** |
| **Multi-Core / GIL** | ❌ Locks Python GIL, single-threaded | 🪶 **Multi-core Rayon parallelism, GIL released** |
| **Image Resizing** | ⚠️ Standard CPU resampling | 🪶 **SIMD-accelerated (AVX2/SSE4.1)** |
| **Blend Modes** | ⚠️ Basic alpha compositing | 🪶 **24+ Blend Modes (Multiply, Screen, etc.)** |
| **NumPy / Pillow Bridge** | ⚠️ Slow conversions | 🪶 **Direct zero-copy buffer interop** |

---

## 📦 Installation

### Option 1: Pre-built Binary Wheel (No Rust or Compilers Needed)
Anyone on Windows can install Feather instantly using the pre-built standalone wheel:
```bash
# Install directly from the repository's releases folder:
pip install releases/feather_render-0.4.0-cp310-abi3-win_amd64.whl
```
*(Multi-platform wheels for Linux, macOS, and Windows are also automatically built and downloadable from the GitHub Releases tab).*

### Option 2: Direct from GitHub via pip
```bash
pip install git+https://github.com/yourusername/feather.git
```

### Option 3: From PyPI
```bash
pip install feather-render
```

### Option 4: Build from Source
```bash
git clone https://github.com/yourusername/feather.git
cd feather
pip install maturin
maturin develop --release
```

---

## 🎨 Quickstart

### 1. Typography & Multi-Line Text Boxes

Feather includes built-in system font fallbacks and subpixel glyph rasterization powered by [`fontdue`](https://github.com/slimsag/fontdue):

```python
from feather import Canvas, Font

canvas = Canvas(800, 600, background="#11111b")

# Single line text
canvas.draw_text("⚡ Feather 0.2.0: Typography Engine", 50, 40, size=28, color="#f5c2e7")

# Multiline text box with automatic word wrapping
long_text = "Feather renders smooth vector graphics with zero C dependencies. Words wrap smoothly and gracefully."
width, height = canvas.draw_text_box(
    long_text,
    x=50, y=100, max_width=350,
    size=18, color="#cdd6f4", line_spacing=6
)

# Load any custom TTF or OTF font
custom_font = Font.load("path/to/custom_font.ttf")
canvas.draw_text("Custom Font", 50, 200, size=22, font=custom_font)
```

---

### 2. Native Drop Shadows & Glow Effects

Create buttery-smooth, diffused glassmorphic cards and glowing badges in a single call:

```python
# Card with soft drop shadow
canvas.draw_drop_shadow(
    x=450, y=90, width=300, height=160,
    rx=18, blur=18.0, offset_x=0.0, offset_y=10.0,
    color="rgba(0, 0, 0, 0.5)"
)
canvas.draw_rounded_rect(450, 90, 300, 160, rx=18, fill="#1e1e2e", stroke="rgba(255, 255, 255, 0.15)", stroke_width=1.5)

# Outer glow effect on badges or buttons
canvas.draw_glow(cx=520, cy=200, radius=25, blur=20.0, color="rgba(243, 139, 168, 0.7)")
canvas.draw_circle(520, 200, radius=25, fill="#f38ba8")
```

---

### 3. Matrix Transformations & Clipping Masks

Crop avatars into circles, rounded rectangles, or rotate vector art effortlessly with Python context managers:

```python
# Rotate and transform shapes
with canvas.transform_scope():
    canvas.translate(150, 420)
    canvas.rotate(degrees=25)
    canvas.draw_rect(-40, -40, 80, 80, fill="#a6e3a1")

# Circular avatar clipping mask
with canvas.clipping_circle(cx=320, cy=420, radius=55):
    canvas.draw_image(avatar_canvas, 265, 365)  # Automatically clipped to a circle!
```

---

### 4. Zero-Dependency SVG File Rendering (`resvg`)

Render entire `.svg` vector files or SVG XML strings directly onto your canvas at arbitrary coordinates and dimensions:

```python
# Render SVG document string or file
svg_xml = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#f38ba8" stroke="#ffffff" stroke-width="4"/>
</svg>
"""
canvas.draw_svg_document(svg_xml, x=100, y=100, width=150, height=150)

# Or directly from a file:
canvas.draw_svg_file("icons/badge.svg", x=300, y=100, width=150, height=150)
```

---

### 5. Modern Animation Exporter (`save_webp`, `save_apng`, `save_animation`)

Render high-framerate multi-frame animations with full **32-bit RGBA alpha transparency** and up to **70% smaller file size** than GIF!

```python
from feather import Canvas, save_animation, save_webp, save_apng, save_gif

frames = []
for i in range(30):
    frame = Canvas(400, 400, background="#0f0f17")
    angle = i * (360 / 30)
    with frame.transform_scope():
        frame.translate(200, 200)
        frame.rotate(angle)
        frame.draw_rounded_rect(-50, -50, 100, 100, rx=16, fill="#89b4fa")
    frames.append(frame)

# 🌐 Animated WebP (68% smaller than GIF, full 32-bit truecolor & alpha!)
save_webp(frames, "animation.webp", fps=30, loop_count=0, lossless=True)

# 🖼️ Animated PNG / APNG (lossless 32-bit RGBA for Discord/browsers)
save_apng(frames, "animation.png", fps=30, loop_count=0)

# 🔄 Unified Auto-Detection (detects .webp, .apng, .png, .gif automatically)
save_animation(frames, "animation.webp", fps=30)
```

| Format | Color Depth | Alpha Transparency | Compression | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **WebP** | 32-bit Truecolor | ✅ Full 8-bit Alpha | **~68% smaller than GIF** | Web, Modern Apps |
| **APNG** | 32-bit Truecolor | ✅ Full 8-bit Alpha | Lossless Truecolor | Discord, Apple, High-DPI |
| **GIF** | 8-bit (256 colors) | ❌ 1-bit Binary Only | Larger file size | Legacy fallback |

---

### 6. Instant Live Interactive Window (`canvas.show()`, `show_interactive()`)

Instead of Pillow's `image.show()` that dumps a temporary BMP to Windows Photo Viewer, Feather boots a **native 60 FPS desktop window**:

```python
from feather import Canvas, show_interactive

canvas = Canvas(1000, 700, background="#161922")
# ... draw anything ...

# 🖥️ Open instant interactive desktop viewer
canvas.show(title="My CAD Blueprint")

# 🎬 Or play multi-frame animations in real-time
show_interactive(frames, title="Signal Flow Simulation", fps=30)
```

**Interactive Controls**:
- 🔍 **Smooth Zoom**: Scroll mouse wheel centered directly at your cursor.
- 🖐️ **Pan**: Click and drag with left mouse button anywhere across the canvas.
- 🎯 **Pixel Inspector**: Hover over any pixel to see exact `(X, Y)` coordinates and Hex/RGBA color live in the title bar HUD.
- ⏯️ **Playback**: Press `Space` to Pause/Play, `Left`/`Right` arrow keys to step through animation frames.
- 🔄 **Reset View**: Press `R` to re-center and fit to window.
- 📸 **Instant Snapshot**: Press `S` to save the current frame as a PNG.
- ❌ **Exit**: Press `Esc` or `Q`.

---

### 7. Anti-Aliased Shapes & Gradients

```python
from feather import Canvas, LinearGradient, RadialGradient

canvas = Canvas(800, 600, background="#11111b")

# Linear gradient
grad = LinearGradient(50, 50, 350, 250, stops=[
    (0.0, "#f38ba8"),
    (0.5, "#cba6f7"),
    (1.0, "#89b4fa")
])
canvas.draw_rounded_rect(50, 50, 300, 200, rx=24, fill=grad, stroke="#ffffff", stroke_width=2.5)

# Radial gradient
radial = RadialGradient(550, 200, 90, stops=[
    (0.0, "#a6e3a1"),
    (1.0, "rgba(166, 227, 161, 0)")
])
canvas.draw_circle(550, 200, radius=90, fill=radial, stroke="#94e2d5", stroke_width=3.0)

canvas.save("render.png")
```

---

### 7. SIMD Resizing & Image Filters

```python
img = Canvas.open("photo.png")

# Ultra-fast SIMD resize (filters: 'bilinear', 'bicubic', 'lanczos3', 'nearest')
thumbnail = img.resize(256, 256, filter="lanczos3")

# Multi-threaded Gaussian Blur (GIL released)
blurred = img.blur(sigma=4.5)

# Adjust brightness and contrast
enhanced = img.adjust_contrast(1.2).adjust_brightness(1.05)
enhanced.save("enhanced.jpg", quality=95)
```

---

### 8. Seamless Pillow & NumPy Interop

```python
from PIL import Image
import numpy as np
from feather import Canvas

# Pillow -> Feather
pil_img = Image.open("avatar.png")
canvas = Canvas.from_pillow(pil_img)

# Feather -> Pillow
result_pil = canvas.to_pillow()

# Feather <-> NumPy
np_array = canvas.to_numpy()  # uint8 shape (H, W, 4)
new_canvas = Canvas.from_numpy(np_array)
```

---

## 🏗 Architecture

- **Rasterizer Engine**: Built on [`tiny-skia`](https://github.com/RazrFalcon/tiny-skia), a pure Rust port of Google's Skia software rasterizer. Features full SIMD optimizations for AVX2, SSE4.1, and ARM Neon.
- **SVG Engine**: Integrated [`resvg`](https://github.com/RazrFalcon/resvg) for 100% pure Rust, zero-dependency SVG vector document rasterization.
- **Font Engine**: Powered by [`fontdue`](https://github.com/slimsag/fontdue) for subpixel glyph coverage rasterization and text measurement.
- **Resampling Pipeline**: Uses [`fast_image_resize`](https://github.com/Cykooz/fast_image_resize) for blazing-fast SIMD image convolutions.
- **Concurrency**: Work-stealing thread pools powered by [`rayon`](https://github.com/rayon-rs/rayon).
- **Color Engine**: Parses CSS hex, rgb, rgba, hsl, and named colors via [`csscolorparser`](https://github.com/mazznoer/csscolorparser-rs).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> 🤖 **Note:** This README was made with AI.

