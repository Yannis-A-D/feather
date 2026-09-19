use crate::filters;
use tiny_skia::{Color, FillRule, Paint, PathBuilder, Pixmap, PixmapPaint, Rect, Transform};

pub fn render_drop_shadow_rect(
    dst: &mut Pixmap,
    x: f32,
    y: f32,
    w: f32,
    h: f32,
    rx: f32,
    ry: f32,
    blur_sigma: f32,
    offset_x: f32,
    offset_y: f32,
    color: Color,
) {
    if blur_sigma <= 0.0 && offset_x == 0.0 && offset_y == 0.0 {
        return;
    }

    let pad = (blur_sigma * 3.0).ceil().max(1.0) as u32 + 4;
    let pad_f = pad as f32;
    let sw = (w.ceil() as u32) + pad * 2;
    let sh = (h.ceil() as u32) + pad * 2;

    let mut temp = match Pixmap::new(sw, sh) {
        Some(p) => p,
        None => return,
    };

    let mut pb = PathBuilder::new();
    let sx = pad_f;
    let sy = pad_f;
    let right = sx + w;
    let bottom = sy + h;

    if rx > 0.0 || ry > 0.0 {
        let rx = rx.min(w / 2.0);
        let ry = ry.min(h / 2.0);
        let k = 0.552284749831f32;
        let dx = rx * (1.0 - k);
        let dy = ry * (1.0 - k);

        pb.move_to(sx + rx, sy);
        pb.line_to(right - rx, sy);
        pb.cubic_to(right - dx, sy, right, sy + dy, right, sy + ry);
        pb.line_to(right, bottom - ry);
        pb.cubic_to(right, bottom - dy, right - dx, bottom, right - rx, bottom);
        pb.line_to(sx + rx, bottom);
        pb.cubic_to(sx + dx, bottom, sx, bottom - dy, sx, bottom - ry);
        pb.line_to(sx, sy + ry);
        pb.cubic_to(sx, sy + dy, sx + dx, sy, sx + rx, sy);
        pb.close();
    } else {
        if let Some(rect) = Rect::from_xywh(sx, sy, w, h) {
            pb.push_rect(rect);
        }
    }

    if let Some(path) = pb.finish() {
        let mut paint = Paint::default();
        paint.anti_alias = true;
        paint.set_color(Color::WHITE);
        temp.fill_path(&path, &paint, FillRule::Winding, Transform::identity(), None);
    }

    // Apply fast gaussian blur to generate the soft diffused shadow
    let blurred = filters::fast_gaussian_blur(temp.data(), sw, sh, blur_sigma);

    // Modulate alpha and tint with the shadow color
    let mut shadow_pixmap = match Pixmap::new(sw, sh) {
        Some(p) => p,
        None => return,
    };

    let cr = (color.red() * 255.0).round() as u32;
    let cg = (color.green() * 255.0).round() as u32;
    let cb = (color.blue() * 255.0).round() as u32;
    let ca = (color.alpha() * 255.0).round() as u32;

    let out_data = shadow_pixmap.data_mut();
    for i in 0..(sw * sh) as usize {
        let src_idx = i * 4;
        let coverage = blurred[src_idx + 3] as u32;
        if coverage > 0 {
            let a = (ca * coverage) / 255;
            let r = (cr * a) / 255;
            let g = (cg * a) / 255;
            let b = (cb * a) / 255;

            out_data[src_idx] = r as u8;
            out_data[src_idx + 1] = g as u8;
            out_data[src_idx + 2] = b as u8;
            out_data[src_idx + 3] = a as u8;
        }
    }

    // Draw shadow onto destination canvas
    let target_x = (x + offset_x - pad_f).round() as i32;
    let target_y = (y + offset_y - pad_f).round() as i32;

    let pp = PixmapPaint::default();
    dst.draw_pixmap(target_x, target_y, shadow_pixmap.as_ref(), &pp, Transform::identity(), None);
}

pub fn render_drop_shadow_circle(
    dst: &mut Pixmap,
    cx: f32,
    cy: f32,
    radius: f32,
    blur_sigma: f32,
    offset_x: f32,
    offset_y: f32,
    color: Color,
) {
    let d = radius * 2.0;
    render_drop_shadow_rect(
        dst,
        cx - radius,
        cy - radius,
        d,
        d,
        radius,
        radius,
        blur_sigma,
        offset_x,
        offset_y,
        color,
    );
}
