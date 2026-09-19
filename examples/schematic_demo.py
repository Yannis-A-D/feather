"""
Feather Schematic Rendering Demo
Demonstrates rendering high-precision CAD / electrical schematics with subpixel
anti-aliasing, transform matrix instancing, SVG paths, and typography.
"""

import math
from feather import Canvas, Font

def render_schematic(out_path="schematic_output.png"):
    width, height = 1200, 800
    canvas = Canvas(width, height, background="#161922")  # Dark CAD canvas
    font = Font.default_font()

    # Colors
    GRID_COLOR = "#262c3a"
    WIRE_COLOR = "#48c78e"        # Crisp phosphor green for signals
    POWER_COLOR = "#f56565"       # Coral red for VCC
    GND_COLOR = "#a0aec0"         # Slate gray for GND
    CHIP_BG = "#1e2433"
    CHIP_BORDER = "#63b3ed"       # Cyan accent
    TEXT_MAIN = "#f0f4f8"
    TEXT_DIM = "#94a3b8"
    TEXT_ACCENT = "#f6e05e"       # Yellow for values

    # 1. Engineering Dot Grid (25px spacing)
    for x in range(0, width, 25):
        for y in range(0, height, 25):
            canvas.draw_circle(x, y, 1.0, fill=GRID_COLOR)

    # 2. Title Block
    canvas.draw_rounded_rect(30, 30, 440, 75, rx=8, fill=CHIP_BG, stroke=CHIP_BORDER, stroke_width=1.5)
    canvas.draw_text("NON-INVERTING OP-AMP AMPLIFIER", 50, 48, size=18, color=TEXT_MAIN, font=font)
    canvas.draw_text("FEATHER CAD ENGINE • HIGH-DPI ANTI-ALIASED SCHEMATIC", 50, 75, size=11, color=TEXT_DIM, font=font)

    # --- Reusable Component Symbol Helpers via Matrix Transforms ---
    def draw_resistor(x, y, angle_deg=0, label="R", value="10k"):
        canvas.save_state()
        canvas.translate(x, y)
        canvas.rotate(angle_deg)
        # Resistor leads
        canvas.draw_line(-50, 0, -30, 0, stroke=WIRE_COLOR, stroke_width=2.0)
        # Zigzag path
        zigzag = "M -30 0 L -22 -12 L -10 12 L 2 -12 L 14 12 L 22 -12 L 30 0"
        canvas.draw_svg_path(zigzag, stroke=WIRE_COLOR, stroke_width=2.0)
        canvas.draw_line(30, 0, 50, 0, stroke=WIRE_COLOR, stroke_width=2.0)
        canvas.restore_state()

        # Labels positioned perpendicular to component
        rad = math.radians(angle_deg)
        lx = x - math.sin(rad) * 26
        ly = y + math.cos(rad) * 26
        canvas.draw_text(label, lx - 18, ly - 8, size=13, color=TEXT_MAIN, font=font)
        canvas.draw_text(value, lx - 18, ly + 9, size=11, color=TEXT_ACCENT, font=font)

    def draw_capacitor(x, y, angle_deg=0, label="C", value="100nF"):
        canvas.save_state()
        canvas.translate(x, y)
        canvas.rotate(angle_deg)
        # Leads
        canvas.draw_line(-40, 0, -8, 0, stroke=WIRE_COLOR, stroke_width=2.0)
        canvas.draw_line(8, 0, 40, 0, stroke=WIRE_COLOR, stroke_width=2.0)
        # Parallel plates
        canvas.draw_line(-8, -18, -8, 18, stroke=WIRE_COLOR, stroke_width=2.5)
        canvas.draw_line(8, -18, 8, 18, stroke=WIRE_COLOR, stroke_width=2.5)
        canvas.restore_state()

        canvas.draw_text(label, x - 18, y - 35, size=13, color=TEXT_MAIN, font=font)
        canvas.draw_text(value, x - 18, y + 26, size=11, color=TEXT_ACCENT, font=font)

    def draw_gnd(x, y):
        canvas.draw_line(x, y, x, y + 15, stroke=GND_COLOR, stroke_width=2.0)
        canvas.draw_line(x - 16, y + 15, x + 16, y + 15, stroke=GND_COLOR, stroke_width=2.5)
        canvas.draw_line(x - 10, y + 21, x + 10, y + 21, stroke=GND_COLOR, stroke_width=2.0)
        canvas.draw_line(x - 4, y + 27, x + 4, y + 27, stroke=GND_COLOR, stroke_width=1.5)

    def draw_junction(x, y):
        canvas.draw_circle(x, y, 4.5, fill=WIRE_COLOR)

    # 3. Draw Op-Amp (Triangle symbol)
    op_x, op_y = 620, 400
    triangle_path = f"M {op_x-60} {op_y-60} L {op_x+60} {op_y} L {op_x-60} {op_y+60} Z"
    canvas.draw_svg_path(triangle_path, fill=CHIP_BG, stroke=CHIP_BORDER, stroke_width=2.5)
    
    # Op-amp polarity labels
    canvas.draw_text("+", op_x - 50, op_y - 35, size=20, color=TEXT_MAIN, font=font)
    canvas.draw_text("-", op_x - 50, op_y + 15, size=22, color=TEXT_MAIN, font=font)
    canvas.draw_text("U1:A", op_x - 22, op_y - 12, size=12, color=TEXT_DIM, font=font)
    canvas.draw_text("LM358", op_x - 26, op_y + 4, size=12, color=TEXT_DIM, font=font)

    # 4. Wiring: Input Stage
    canvas.draw_text("SIGNAL IN", 180, 360, size=13, color=TEXT_ACCENT, font=font)
    canvas.draw_line(260, 375, 340, 375, stroke=WIRE_COLOR, stroke_width=2.0)
    
    # Input AC-coupling Capacitor C1
    draw_capacitor(380, 375, angle_deg=0, label="C1", value="10µF")
    
    # Wire from C1 to Non-inverting input (+)
    canvas.draw_line(420, 375, op_x - 60, 375, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_junction(490, 375)
    
    # Bias Resistor R_in to GND
    canvas.draw_line(490, 375, 490, 430, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_resistor(490, 480, angle_deg=90, label="R_bias", value="100k")
    canvas.draw_line(490, 530, 490, 560, stroke=GND_COLOR, stroke_width=2.0)
    draw_gnd(490, 560)

    # 5. Wiring: Inverting Feedback Stage (-)
    canvas.draw_line(op_x - 60, 425, 520, 425, stroke=WIRE_COLOR, stroke_width=2.0)
    canvas.draw_line(520, 425, 520, 520, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_junction(520, 520)
    
    # R1 to GND (from 520, 520 down)
    canvas.draw_line(520, 520, 520, 560, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_resistor(520, 610, angle_deg=90, label="R1", value="1k")
    canvas.draw_line(520, 660, 520, 690, stroke=GND_COLOR, stroke_width=2.0)
    draw_gnd(520, 690)

    # Feedback loop: wire from junction right to R2 lead, then from R2 right lead up to Output
    # R2 is at (650, 520), leads are from 600 to 700
    canvas.draw_line(520, 520, 600, 520, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_resistor(650, 520, angle_deg=0, label="R2 (Feedback)", value="10k")
    canvas.draw_line(700, 520, 760, 520, stroke=WIRE_COLOR, stroke_width=2.0)
    canvas.draw_line(760, 520, 760, 400, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_junction(760, 400)

    # 6. Output wire
    canvas.draw_line(op_x + 60, 400, 850, 400, stroke=WIRE_COLOR, stroke_width=2.0)
    draw_junction(850, 400)
    
    # Output coupling capacitor C2
    draw_capacitor(890, 400, angle_deg=0, label="C2", value="4.7µF")
    canvas.draw_line(930, 400, 1020, 400, stroke=WIRE_COLOR, stroke_width=2.0)
    
    # Output terminal badge
    canvas.draw_rounded_rect(1025, 382, 130, 36, rx=6, fill=CHIP_BG, stroke=WIRE_COLOR, stroke_width=1.5)
    canvas.draw_text("V_OUT (Av = 11)", 1038, 393, size=12, color=TEXT_MAIN, font=font)

    # 7. Power Rail Annotations (VCC / -VCC)
    canvas.draw_line(op_x, op_y - 30, op_x, op_y - 80, stroke=POWER_COLOR, stroke_width=2.0)
    canvas.draw_line(op_x - 10, op_y - 80, op_x + 10, op_y - 80, stroke=POWER_COLOR, stroke_width=2.0)
    canvas.draw_text("+12V (VCC)", op_x - 35, op_y - 102, size=12, color=POWER_COLOR, font=font)

    canvas.draw_line(op_x, op_y + 30, op_x, op_y + 80, stroke=GND_COLOR, stroke_width=2.0)
    draw_gnd(op_x, op_y + 80)

    # 8. Digital MCU Header / Connector Box
    ic_x, ic_y = 100, 520
    canvas.draw_rounded_rect(ic_x, ic_y, 160, 190, rx=6, fill=CHIP_BG, stroke=CHIP_BORDER, stroke_width=2.0)
    canvas.draw_text("MCU_HEADER", ic_x + 24, ic_y + 16, size=14, color=TEXT_MAIN, font=font)

    pins = [
        ("P0.1 (DAC)", POWER_COLOR),
        ("P0.2 (ADC)", WIRE_COLOR),
        ("GND", GND_COLOR),
        ("3V3", POWER_COLOR)
    ]
    for i, (pin_label, pcol) in enumerate(pins):
        py = ic_y + 55 + i * 34
        canvas.draw_line(ic_x + 160, py, ic_x + 185, py, stroke=pcol, stroke_width=2.0)
        canvas.draw_circle(ic_x + 185, py, 3.0, fill=pcol)
        canvas.draw_text(pin_label, ic_x + 18, py - 6, size=11, color=TEXT_DIM, font=font)

    # Save output
    canvas.save(out_path)
    print(f"Schematic successfully generated -> {out_path}")

if __name__ == "__main__":
    render_schematic()
