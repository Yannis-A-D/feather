"""
Feather CAD & Blueprint Demo: High-precision architectural blueprint
with technical grid, hatched walls, door swing arcs, and dimension callouts.
"""

import math
import os
import feather
from feather import Canvas

def generate_blueprint():
    print("Generating Feather Architectural CAD Blueprint...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(output_dir, exist_ok=True)

    w, h = 1280, 820
    # Technical blueprint navy
    canvas = Canvas(w, h, background="#071224")

    # 1. Blueprint Grid
    grid_fine = "rgba(0, 220, 255, 0.05)"
    grid_major = "rgba(0, 220, 255, 0.14)"

    for x in range(0, w, 20):
        color = grid_major if x % 100 == 0 else grid_fine
        canvas.draw_line(float(x), 0.0, float(x), float(h), stroke=color, stroke_width=1.0)
    for y in range(0, h, 20):
        color = grid_major if y % 100 == 0 else grid_fine
        canvas.draw_line(0.0, float(y), float(w), float(y), stroke=color, stroke_width=1.0)

    # 2. Outer Border & Drafting Title Block
    border_color = "rgba(0, 230, 255, 0.70)"
    canvas.draw_rect(30.0, 30.0, w - 60.0, h - 60.0, stroke=border_color, stroke_width=2.0)
    canvas.draw_rect(34.0, 34.0, w - 68.0, h - 68.0, stroke="rgba(0, 230, 255, 0.30)", stroke_width=1.0)

    # Title Block (Bottom Right)
    tb_w, tb_h = 320.0, 100.0
    tb_x, tb_y = w - 34.0 - tb_w, h - 34.0 - tb_h
    canvas.draw_rect(tb_x, tb_y, tb_w, tb_h, fill="rgba(7, 18, 36, 0.90)", stroke=border_color, stroke_width=1.5)
    canvas.draw_line(tb_x, tb_y + 35.0, tb_x + tb_w, tb_y + 35.0, stroke=border_color, stroke_width=1.0)
    canvas.draw_line(tb_x + 180.0, tb_y + 35.0, tb_x + 180.0, tb_y + tb_h, stroke=border_color, stroke_width=1.0)

    canvas.draw_text("QUANTUM COMPUTE FACILITY", tb_x + 14.0, tb_y + 10.0, size=15.0, color="#ffffff")
    canvas.draw_text("LEVEL 02 ARCHITECTURAL SCHEMATIC", tb_x + 14.0, tb_y + 42.0, size=10.0, color="#64b5f6")
    canvas.draw_text("SCALE: 1:50  •  UNITS: METRIC", tb_x + 14.0, tb_y + 60.0, size=10.0, color="#90caf9")
    canvas.draw_text("FEATHER VECTOR ENGINE", tb_x + 14.0, tb_y + 78.0, size=10.0, color="#00e5ff")

    canvas.draw_text("DWG NO: QC-204-B", tb_x + 190.0, tb_y + 45.0, size=11.0, color="#ffffff")
    canvas.draw_text("REV: 0.4.1", tb_x + 190.0, tb_y + 65.0, size=11.0, color="#69f0ae")

    # North Arrow (Top Right)
    na_x, na_y = w - 90.0, 80.0
    canvas.draw_circle(na_x, na_y, 22.0, stroke=border_color, stroke_width=1.5)
    canvas.draw_polygon([(na_x, na_y - 18.0), (na_x - 7.0, na_y + 12.0), (na_x, na_y + 5.0)], fill="#00e5ff")
    canvas.draw_polygon([(na_x, na_y - 18.0), (na_x + 7.0, na_y + 12.0), (na_x, na_y + 5.0)], fill="rgba(0, 229, 255, 0.25)")
    canvas.draw_text("N", na_x - 5.0, na_y - 34.0, size=12.0, color="#ffffff")

    # 3. Wall Layout (Outer Perimeter & Internal Rooms)
    wall_color = "#00e5ff"
    wall_fill = "rgba(0, 229, 255, 0.12)"

    def draw_thick_wall(x, y, width, height, thickness=12.0):
        # Outer wall
        canvas.draw_rect(x, y, width, height, stroke=wall_color, stroke_width=2.0)
        # Inner wall
        canvas.draw_rect(
            x + thickness, y + thickness,
            width - thickness * 2.0, height - thickness * 2.0,
            stroke=wall_color, stroke_width=1.5
        )
        # Angled hatching lines between walls
        # Top & Bottom wall hatching
        step = 10.0
        # Simple cross-section fill
        canvas.draw_rect(x, y, width, height, fill=wall_fill)
        canvas.draw_rect(
            x + thickness, y + thickness,
            width - thickness * 2.0, height - thickness * 2.0,
            fill="#071224"
        )

    # Main Building Shell (800 x 480)
    bx, by, bw, bh = 140.0, 140.0, 840.0, 480.0
    draw_thick_wall(bx, by, bw, bh, thickness=14.0)

    # Interior Partitions
    # Server Room (Left: 340 x 480)
    canvas.draw_line(bx + 340.0, by + 14.0, bx + 340.0, by + bh - 14.0, stroke=wall_color, stroke_width=8.0)
    # Air Lock / Control Room Divider
    canvas.draw_line(bx + 340.0, by + 260.0, bx + bw - 14.0, by + 260.0, stroke=wall_color, stroke_width=8.0)
    canvas.draw_line(bx + 620.0, by + 260.0, bx + 620.0, by + bh - 14.0, stroke=wall_color, stroke_width=8.0)

    # 4. Server Racks in Server Room
    rack_color = "rgba(100, 181, 246, 0.40)"
    rack_stroke = "#64b5f6"
    for row in range(4):
        ry = by + 50.0 + row * 85.0
        for col in range(2):
            rx = bx + 50.0 + col * 120.0
            canvas.draw_rounded_rect(rx, ry, 90.0, 50.0, rx=4.0, fill=rack_color, stroke=rack_stroke, stroke_width=1.5)
            # Rack blade slots
            for slot in range(4):
                canvas.draw_line(rx + 10.0, ry + 12.0 + slot * 9.0, rx + 80.0, ry + 12.0 + slot * 9.0, stroke="rgba(255, 255, 255, 0.5)", stroke_width=1.0)

    # 5. Room Labels
    canvas.draw_text("HPC SERVER CLUSTER", bx + 80.0, by + bh - 40.0, size=14.0, color="#ffffff")
    canvas.draw_text("AREA: 86.4 m² • TEMP: 18°C", bx + 80.0, by + bh - 22.0, size=11.0, color="#90caf9")

    canvas.draw_text("PRIMARY CONTROL LAB", bx + 420.0, by + 120.0, size=14.0, color="#ffffff")
    canvas.draw_text("AREA: 124.8 m² • RATING: ISO-5", bx + 420.0, by + 138.0, size=11.0, color="#90caf9")

    canvas.draw_text("AIR LOCK / DECON", bx + 380.0, by + 370.0, size=13.0, color="#ffffff")
    canvas.draw_text("AREA: 32.0 m²", bx + 380.0, by + 388.0, size=10.0, color="#90caf9")

    canvas.draw_text("POWER & UPS MATRIX", bx + 660.0, by + 370.0, size=13.0, color="#ffffff")
    canvas.draw_text("AREA: 48.0 m²", bx + 660.0, by + 388.0, size=10.0, color="#90caf9")

    # 6. Door Swings (Arc & Door Leaf)
    def draw_door(dx, dy, width, orientation="right"):
        # Door opening leaf
        canvas.draw_line(dx, dy, dx + width, dy, stroke="#ffffff", stroke_width=2.0)
        # 90-degree swing arc
        arc_svg = f"M {dx + width:.2f} {dy:.2f} A {width:.2f} {width:.2f} 0 0 1 {dx:.2f} {dy + width:.2f}"
        canvas.draw_svg_path(arc_svg, stroke="rgba(255, 255, 255, 0.60)", stroke_width=1.2)

    draw_door(bx + 340.0, by + 80.0, 42.0)
    draw_door(bx + 480.0, by + 260.0, 42.0)
    draw_door(bx + 620.0, by + 320.0, 42.0)

    # 7. Dimension Lines with Arrowheads & Callouts
    dim_color = "#ffb74d"
    dim_ext = "rgba(255, 183, 77, 0.40)"

    def draw_dimension(x1, y1, x2, y2, text, offset=35.0, is_horizontal=True):
        if is_horizontal:
            # Extension lines
            dy = y1 - offset
            canvas.draw_line(x1, y1 - 5.0, x1, dy - 6.0, stroke=dim_ext, stroke_width=1.0)
            canvas.draw_line(x2, y2 - 5.0, x2, dy - 6.0, stroke=dim_ext, stroke_width=1.0)
            # Main dimension line
            canvas.draw_line(x1, dy, x2, dy, stroke=dim_color, stroke_width=1.5)
            # End ticks (45-degree architectural slash)
            canvas.draw_line(x1 - 4.0, dy + 4.0, x1 + 4.0, dy - 4.0, stroke=dim_color, stroke_width=2.0)
            canvas.draw_line(x2 - 4.0, dy + 4.0, x2 + 4.0, dy - 4.0, stroke=dim_color, stroke_width=2.0)
            # Text
            mid_x = (x1 + x2) * 0.5 - len(text) * 4.0
            canvas.draw_text(text, mid_x, dy - 16.0, size=12.0, color=dim_color)
        else:
            # Vertical dimension
            dx = x1 - offset
            canvas.draw_line(x1 - 5.0, y1, dx - 6.0, y1, stroke=dim_ext, stroke_width=1.0)
            canvas.draw_line(x2 - 5.0, y2, dx - 6.0, y2, stroke=dim_ext, stroke_width=1.0)
            canvas.draw_line(dx, y1, dx, y2, stroke=dim_color, stroke_width=1.5)
            canvas.draw_line(dx - 4.0, y1 + 4.0, dx + 4.0, y1 - 4.0, stroke=dim_color, stroke_width=2.0)
            canvas.draw_line(dx - 4.0, y2 + 4.0, dx + 4.0, y2 - 4.0, stroke=dim_color, stroke_width=2.0)
            mid_y = (y1 + y2) * 0.5 - 6.0
            canvas.draw_text(text, dx - 54.0, mid_y, size=12.0, color=dim_color)

    # Top horizontal dimensions
    draw_dimension(bx, by, bx + 340.0, by, "6.80 m", offset=35.0, is_horizontal=True)
    draw_dimension(bx + 340.0, by, bx + bw, by, "10.00 m", offset=35.0, is_horizontal=True)
    draw_dimension(bx, by, bx + bw, by, "16.80 m (OVERALL)", offset=70.0, is_horizontal=True)

    # Left vertical dimensions
    draw_dimension(bx, by, bx, by + 260.0, "5.20 m", offset=40.0, is_horizontal=False)
    draw_dimension(bx, by + 260.0, bx, by + bh, "4.40 m", offset=40.0, is_horizontal=False)
    draw_dimension(bx, by, bx, by + bh, "9.60 m (OVERALL)", offset=80.0, is_horizontal=False)

    # Save blueprint
    out_path = os.path.join(output_dir, "blueprint_demo.png")
    canvas.save(out_path)
    print(f"[OK] Feather Architectural CAD Blueprint saved to: {out_path}")

if __name__ == "__main__":
    generate_blueprint()
