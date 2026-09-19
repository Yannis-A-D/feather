# ⚡ PixelForge

[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange.svg?logo=rust)](https://www.rust-lang.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![SIMD Accelerated](https://img.shields.io/badge/SIMD-AVX2%20%7C%20SSE4.1%20%7C%20NEON-red.svg)](https://github.com)

**PixelForge** is a high-performance, memory-safe 2D vector graphics and image processing extension for Python, built from the ground up in **Rust**.

Designed as a modern, superior alternative to Pillow's (`PIL.ImageDraw`) rendering engine, PixelForge provides **flawless subpixel anti-aliasing**, **SIMD acceleration**, **multi-core batch processing**, and seamless integration with **NumPy** and **Pillow**.

---

## 🚀 Why PixelForge?

| Feature | Pillow (`PIL.ImageDraw`) | PixelForge |
| :--- | :--- | :--- |
| **Anti-Aliasing** | ❌ Jagged, pixelated edges |  **Flawless subpixel anti-aliasing** |
| **Rounded Rectangles** | ⚠️ Basic or broken corner radii |  **Smooth bezier rounded corners (`rx`, `ry`)** |
| **Gradients** | ❌ None (requires manual loops) |  **Linear & Radial Gradients with stops** |
| **Vector Paths** | ❌ Limited polylines |  **Quadratic/Cubic Beziers & SVG `d` Paths** |
| **Multi-Core / GIL** | ❌ Locks Python GIL, single-threaded |  **Multi-core Rayon parallelism, GIL released** |
| **Image Resizing** | ⚠️ Standard CPU resampling |  **SIMD-accelerated (AVX2/SSE4.1)** |
| **Blend Modes** | ⚠️ Basic alpha compositing |  **24+ Blend Modes (Multiply, Screen, etc.)** |
| **NumPy / Pillow Bridge** | ⚠️ Slow conversions |  **Direct zero-copy buffer interop** |

---

## 📦 Installation

### From Source (Maturin)
```bash
# Clone the repository
git clone https://github.com/yourusername/pixelforge.git
cd pixelforge

# Install directly into your active Python environment
pip install maturin
maturin develop --release
```

---

## 🎨 Quickstart

### 1. Anti-Aliased Shapes & Gradients

```python
from pixelforge import Canvas, LinearGradient, RadialGradient

# Create a high-resolution canvas with a dark background
canvas = Canvas(800, 600, background="#11111b")

# Smooth rounded rectangle with a linear gradient
grad = LinearGradient(
    50, 50, 350, 250,
    stops=[(0.0, "#f38ba8"), (0.5, "#cba6f7"), (1.0, "#89b4fa")]
)
canvas.draw_rounded_rect(
    50, 50, 300, 200,
    rx=24,
    fill=grad,
    stroke="#ffffff",
    stroke_width=2.5
)

# Smooth anti-aliased circles
radial = RadialGradient(
    550, 200, 100,
    stops=[(0.0, "#a6e3a1"), (1.0, "rgba(166, 227, 161, 0)")]
)
canvas.draw_circle(550, 200, radius=90, fill=radial)
canvas.draw_circle(550, 200, radius=90, stroke="#94e2d5", stroke_width=3.0)

# Save directly to PNG, JPEG, or WebP
canvas.save("render.png")
```

---

### 2. SVG Paths & Complex Bezier Curves

```python
from pixelforge import Canvas, Path

canvas = Canvas(400, 400, background="#181825")

# Draw using SVG path syntax directly
heart_svg = "M 200,100 A 45,45 0 0,0 125,160 Q 125,230 200,300 Q 275,230 275,160 A 45,45 0 0,0 200,100 Z"
canvas.draw_svg_path(heart_svg, fill="#f38ba8", stroke="#eba0ac", stroke_width=2)

# Or build programmatically with the Path API
path = Path()
path.move_to(50, 50)
path.cubic_to(100, 20, 200, 80, 250, 50)
path.line_to(250, 150)
path.close()
canvas.draw_path(path, stroke="#89dceb", stroke_width=3.0)

canvas.save("paths.png")
```

---

### 3. SIMD Resizing & Image Filters

```python
from pixelforge import Canvas

# Load an image
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

### 4. Multi-Core Batch Processing

PixelForge releases the Python GIL during heavy computations, allowing native multithreading across all CPU cores with `rayon`:

```python
from pixelforge import Canvas, batch_resize, batch_blur

images = [Canvas.open(f"input_{i}.png") for i in range(100)]

# Resizes 100 images in parallel across all CPU cores
resized_all = batch_resize(images, 512, 512, filter="bilinear")

# Blurs 100 images in parallel
blurred_all = batch_blur(resized_all, sigma=2.0)
```

---

### 5. Seamless Pillow & NumPy Interop

```python
from PIL import Image
import numpy as np
from pixelforge import Canvas

# Pillow -> PixelForge
pil_img = Image.open("avatar.png")
canvas = Canvas.from_pillow(pil_img)

# Draw smooth vector overlays
canvas.draw_circle(100, 100, radius=40, stroke="#00ffcc", stroke_width=4.0)

# PixelForge -> Pillow
result_pil = canvas.to_pillow()

# PixelForge <-> NumPy
np_array = canvas.to_numpy()  # uint8 shape (H, W, 4)
new_canvas = Canvas.from_numpy(np_array)
```

---

## 🏗 Architecture

- **Rasterizer Engine**: Built on [`tiny-skia`](https://github.com/RazrFalcon/tiny-skia), a pure Rust port of Google's Skia software rasterizer. Features full SIMD optimizations for AVX2, SSE4.1, and ARM Neon.
- **Resampling Pipeline**: Uses [`fast_image_resize`](https://github.com/Cykooz/fast_image_resize) for blazing-fast SIMD image convolutions.
- **Concurrency**: Work-stealing thread pools powered by [`rayon`](https://github.com/rayon-rs/rayon).
- **Color Engine**: Parses CSS hex, rgb, rgba, hsl, and named colors via [`csscolorparser`](https://github.com/mazznoer/csscolorparser-rs).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
