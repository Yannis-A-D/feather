"""
Feather Standalone Interactive HTML Export Demo:
Renders a complex CAD architectural schematic and exports it as an offline,
fully interactive HTML document with smooth pan, infinite zoom, and HUD pixel inspector.
"""

import os
import sys

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from examples.blueprint_demo import generate_blueprint
import feather

def run_html_export():
    print("Generating Standalone Interactive HTML Blueprint...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)
    html_out = os.path.join(output_dir, "interactive_blueprint.html")

    # Load blueprint PNG into canvas or render directly
    png_path = os.path.join(output_dir, "blueprint_demo.png")
    if os.path.exists(png_path):
        canvas = feather.Canvas.open(png_path)
    else:
        canvas = generate_blueprint()

    # Save to interactive HTML
    canvas.save_html(html_out, title="Quantum Compute Facility - CAD Schematic")

    print(f"[OK] Interactive HTML export generated at: {html_out} ({os.path.getsize(html_out):,} bytes)")

if __name__ == "__main__":
    run_html_export()
