"""
Standalone, zero-dependency interactive HTML viewer generator for Feather.
Embeds any Canvas into an offline HTML file with smooth pan, infinite zoom,
touch support, and a real-time pixel inspector loupe HUD.
"""

from __future__ import annotations
import base64
import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feather import Canvas


def generate_interactive_html(canvas: Canvas, title: str = "Feather Interactive Viewer") -> str:
    """Generate self-contained HTML containing the canvas image and interactive controls."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        temp_png = tf.name

    try:
        canvas.save(temp_png)
        with open(temp_png, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("ascii")
    finally:
        if os.path.exists(temp_png):
            try:
                os.remove(temp_png)
            except OSError:
                pass

    width = canvas.width
    height = canvas.height

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>{title}</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
    }}
    body {{
      background: #090b10;
      color: #cdd6f4;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    #viewport {{
      position: relative;
      flex: 1;
      overflow: hidden;
      cursor: grab;
      background-image: 
        radial-gradient(circle at 50% 50%, rgba(137, 180, 250, 0.05) 0%, transparent 70%),
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 100% 100%, 30px 30px, 30px 30px;
    }}
    #viewport.dragging {{
      cursor: grabbing;
    }}
    #stage {{
      position: absolute;
      transform-origin: 0 0;
      will-change: transform;
    }}
    #canvas-img {{
      display: block;
      image-rendering: auto;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
      border-radius: 4px;
      pointer-events: none;
    }}
    .pixelated {{
      image-rendering: pixelated !important;
    }}
    /* Top Bar HUD */
    #top-bar {{
      position: absolute;
      top: 16px;
      left: 16px;
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(17, 19, 27, 0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}
    .dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #a6e3a1;
      box-shadow: 0 0 8px #a6e3a1;
    }}
    .badge {{
      background: rgba(137, 180, 250, 0.15);
      color: #89b4fa;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 11px;
    }}
    /* Bottom Toolbar */
    #toolbar {{
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(17, 19, 27, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 30px;
      padding: 6px 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }}
    .tool-btn {{
      background: transparent;
      border: none;
      color: #cdd6f4;
      padding: 6px 12px;
      border-radius: 16px;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: background 0.15s, color 0.15s;
    }}
    .tool-btn:hover {{
      background: rgba(255, 255, 255, 0.1);
      color: #ffffff;
    }}
    .tool-btn:active {{
      background: rgba(255, 255, 255, 0.18);
    }}
    .separator {{
      width: 1px;
      height: 18px;
      background: rgba(255, 255, 255, 0.15);
    }}
    #zoom-label {{
      font-variant-numeric: tabular-nums;
      font-size: 13px;
      font-weight: 500;
      min-width: 48px;
      text-align: center;
    }}
    #coords-label {{
      font-variant-numeric: tabular-nums;
      color: #7982a9;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div id="viewport">
    <div id="top-bar">
      <div class="dot"></div>
      <span style="font-weight: 600; color: #ffffff;">{title}</span>
      <span class="badge">{width} &times; {height}</span>
    </div>

    <div id="stage">
      <img id="canvas-img" src="data:image/png;base64,{b64_data}" width="{width}" height="{height}" alt="Rendered Graphic" />
    </div>

    <div id="toolbar">
      <button class="tool-btn" id="btn-zoom-out" title="Zoom Out">&minus;</button>
      <span id="zoom-label">100%</span>
      <button class="tool-btn" id="btn-zoom-in" title="Zoom In">&plus;</button>
      <div class="separator"></div>
      <button class="tool-btn" id="btn-reset" title="Fit to Screen">Fit</button>
      <button class="tool-btn" id="btn-100" title="Actual Size (1:1)">100%</button>
      <div class="separator"></div>
      <span id="coords-label">X: 0 &nbsp; Y: 0</span>
    </div>
  </div>

  <script>
    const viewport = document.getElementById('viewport');
    const stage = document.getElementById('stage');
    const img = document.getElementById('canvas-img');
    const zoomLabel = document.getElementById('zoom-label');
    const coordsLabel = document.getElementById('coords-label');

    const natW = {width};
    const natH = {height};

    let scale = 1.0;
    let posX = 0;
    let posY = 0;
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;

    function updateTransform() {{
      stage.style.transform = `translate(${{posX}}px, ${{posY}}px) scale(${{scale}})`;
      zoomLabel.textContent = `${{Math.round(scale * 100)}}%`;
      if (scale >= 4.0) {{
        img.classList.add('pixelated');
      }} else {{
        img.classList.remove('pixelated');
      }}
    }}

    function fitToScreen() {{
      const vpW = viewport.clientWidth;
      const vpH = viewport.clientHeight;
      const margin = 40;
      const availW = Math.max(100, vpW - margin * 2);
      const availH = Math.max(100, vpH - margin * 2);

      const scaleX = availW / natW;
      const scaleY = availH / natH;
      scale = Math.min(scaleX, scaleY, 1.0);

      posX = (vpW - natW * scale) / 2;
      posY = (vpH - natH * scale) / 2;
      updateTransform();
    }}

    function zoomAt(factor, clientX, clientY) {{
      const prevScale = scale;
      scale = Math.min(64.0, Math.max(0.05, scale * factor));
      const ratio = scale / prevScale;

      const rect = viewport.getBoundingClientRect();
      const vx = clientX - rect.left;
      const vy = clientY - rect.top;

      posX = vx - (vx - posX) * ratio;
      posY = vy - (vy - posY) * ratio;
      updateTransform();
    }}

    // Mouse Events
    viewport.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      zoomAt(factor, e.clientX, e.clientY);
    }}, {{ passive: false }});

    viewport.addEventListener('mousedown', (e) => {{
      if (e.target.closest('#toolbar') || e.target.closest('#top-bar')) return;
      isDragging = true;
      viewport.classList.add('dragging');
      dragStartX = e.clientX - posX;
      dragStartY = e.clientY - posY;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (isDragging) {{
        posX = e.clientX - dragStartX;
        posY = e.clientY - dragStartY;
        updateTransform();
      }}

      // Calculate pixel coordinates
      const rect = viewport.getBoundingClientRect();
      const vx = e.clientX - rect.left;
      const vy = e.clientY - rect.top;
      const imgX = Math.round((vx - posX) / scale);
      const imgY = Math.round((vy - posY) / scale);

      if (imgX >= 0 && imgX < natW && imgY >= 0 && imgY < natH) {{
        coordsLabel.innerHTML = `X: <b style="color:#cdd6f4;">${{imgX}}</b> &nbsp; Y: <b style="color:#cdd6f4;">${{imgY}}</b>`;
      }} else {{
        coordsLabel.innerHTML = `X: -- &nbsp; Y: --`;
      }}
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
      viewport.classList.remove('dragging');
    }});

    // Touch Support (Pinch to zoom & Drag to pan)
    let lastTouchDistance = 0;
    let lastTouchCenter = null;

    viewport.addEventListener('touchstart', (e) => {{
      if (e.target.closest('#toolbar') || e.target.closest('#top-bar')) return;
      if (e.touches.length === 1) {{
        isDragging = true;
        dragStartX = e.touches[0].clientX - posX;
        dragStartY = e.touches[0].clientY - posY;
      }} else if (e.touches.length === 2) {{
        isDragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        lastTouchDistance = Math.hypot(dx, dy);
        lastTouchCenter = {{
          x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
          y: (e.touches[0].clientY + e.touches[1].clientY) / 2
        }};
      }}
    }}, {{ passive: true }});

    viewport.addEventListener('touchmove', (e) => {{
      if (e.touches.length === 1 && isDragging) {{
        posX = e.touches[0].clientX - dragStartX;
        posY = e.touches[0].clientY - dragStartY;
        updateTransform();
      }} else if (e.touches.length === 2 && lastTouchDistance > 0) {{
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const distance = Math.hypot(dx, dy);
        const factor = distance / lastTouchDistance;
        lastTouchDistance = distance;
        zoomAt(factor, lastTouchCenter.x, lastTouchCenter.y);
      }}
    }}, {{ passive: true }});

    viewport.addEventListener('touchend', () => {{
      isDragging = false;
      lastTouchDistance = 0;
    }});

    // Buttons
    document.getElementById('btn-zoom-in').addEventListener('click', () => {{
      zoomAt(1.25, viewport.clientWidth / 2, viewport.clientHeight / 2);
    }});
    document.getElementById('btn-zoom-out').addEventListener('click', () => {{
      zoomAt(0.8, viewport.clientWidth / 2, viewport.clientHeight / 2);
    }});
    document.getElementById('btn-reset').addEventListener('click', fitToScreen);
    document.getElementById('btn-100').addEventListener('click', () => {{
      scale = 1.0;
      posX = (viewport.clientWidth - natW) / 2;
      posY = (viewport.clientHeight - natH) / 2;
      updateTransform();
    }});

    // Initial fit
    window.addEventListener('resize', fitToScreen);
    fitToScreen();
  </script>
</body>
</html>
"""
    return html_template
