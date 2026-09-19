use crate::color::parse_color;
use crate::filters;
use crate::gradient::{LinearGradient, RadialGradient};
use crate::path::Path;
use crate::shadow;
use crate::svg_render;
use crate::text::{self, Font};
use crate::transform;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PySequence};
use std::fs::File;
use std::io::BufWriter;
use std::path::Path as StdPath;
use tiny_skia::{
    BlendMode, Color, FillRule, LineCap, LineJoin, Mask, Paint, PathBuilder, Pixmap, Rect,
    Stroke, Transform,
};

fn parse_line_cap(cap_str: &str) -> PyResult<LineCap> {
    match cap_str.to_lowercase().as_str() {
        "butt" => Ok(LineCap::Butt),
        "round" => Ok(LineCap::Round),
        "square" => Ok(LineCap::Square),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown line cap '{}'. Valid: 'butt', 'round', 'square'",
            cap_str
        ))),
    }
}

fn parse_line_join(join_str: &str) -> PyResult<LineJoin> {
    match join_str.to_lowercase().as_str() {
        "miter" => Ok(LineJoin::Miter),
        "round" => Ok(LineJoin::Round),
        "bevel" => Ok(LineJoin::Bevel),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown line join '{}'. Valid: 'miter', 'round', 'bevel'",
            join_str
        ))),
    }
}

fn parse_blend_mode(mode_str: &str) -> PyResult<BlendMode> {
    match mode_str.to_lowercase().replace("-", "_").as_str() {
        "source_over" | "src_over" | "normal" => Ok(BlendMode::SourceOver),
        "source" | "src" => Ok(BlendMode::Source),
        "destination_over" | "dst_over" => Ok(BlendMode::DestinationOver),
        "destination" | "dst" => Ok(BlendMode::Destination),
        "clear" => Ok(BlendMode::Clear),
        "source_in" | "src_in" => Ok(BlendMode::SourceIn),
        "destination_in" | "dst_in" => Ok(BlendMode::DestinationIn),
        "source_out" | "src_out" => Ok(BlendMode::SourceOut),
        "destination_out" | "dst_out" => Ok(BlendMode::DestinationOut),
        "source_atyp" | "src_atop" => Ok(BlendMode::SourceAtop),
        "destination_atop" | "dst_atop" => Ok(BlendMode::DestinationAtop),
        "xor" => Ok(BlendMode::Xor),
        "multiply" => Ok(BlendMode::Multiply),
        "screen" => Ok(BlendMode::Screen),
        "overlay" => Ok(BlendMode::Overlay),
        "darken" => Ok(BlendMode::Darken),
        "lighten" => Ok(BlendMode::Lighten),
        "color_dodge" => Ok(BlendMode::ColorDodge),
        "color_burn" => Ok(BlendMode::ColorBurn),
        "hard_light" => Ok(BlendMode::HardLight),
        "soft_light" => Ok(BlendMode::SoftLight),
        "difference" => Ok(BlendMode::Difference),
        "exclusion" => Ok(BlendMode::Exclusion),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown blend mode '{}'",
            mode_str
        ))),
    }
}

fn with_paint<F, R>(paint_obj: &Bound<'_, PyAny>, f: F) -> PyResult<R>
where
    F: for<'a> FnOnce(&Paint<'a>) -> R,
{
    let mut paint = Paint::default();
    paint.anti_alias = true;

    if let Ok(lin_grad) = paint_obj.extract::<pyo3::PyRef<LinearGradient>>() {
        let shader = lin_grad
            .to_shader()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid linear gradient"))?;
        paint.shader = shader;
        Ok(f(&paint))
    } else if let Ok(rad_grad) = paint_obj.extract::<pyo3::PyRef<RadialGradient>>() {
        let shader = rad_grad
            .to_shader()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid radial gradient"))?;
        paint.shader = shader;
        Ok(f(&paint))
    } else {
        let color = parse_color(paint_obj)?;
        paint.set_color(color);
        Ok(f(&paint))
    }
}

#[derive(Clone)]
struct CanvasState {
    transform: Transform,
    mask: Option<Mask>,
}

#[pyclass(subclass)]
#[derive(Clone)]
pub struct Canvas {
    pub(crate) pixmap: Pixmap,
    pub(crate) transform: Transform,
    pub(crate) mask: Option<Mask>,
    state_stack: Vec<CanvasState>,
}

#[pymethods]
impl Canvas {
    #[new]
    #[pyo3(signature = (width, height, background=None))]
    pub fn new(width: u32, height: u32, background: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        if width == 0 || height == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Canvas dimensions must be greater than zero",
            ));
        }

        let mut pixmap = Pixmap::new(width, height).ok_or_else(|| {
            pyo3::exceptions::PyMemoryError::new_err("Failed to allocate canvas pixel buffer")
        })?;

        if let Some(bg_obj) = background {
            let color = parse_color(bg_obj)?;
            pixmap.fill(color);
        }

        Ok(Self {
            pixmap,
            transform: Transform::identity(),
            mask: None,
            state_stack: Vec::new(),
        })
    }

    #[getter]
    pub fn width(&self) -> u32 {
        self.pixmap.width()
    }

    #[getter]
    pub fn height(&self) -> u32 {
        self.pixmap.height()
    }

    #[getter]
    pub fn size(&self) -> (u32, u32) {
        (self.pixmap.width(), self.pixmap.height())
    }

    // --- State Stack & Transformations ---

    pub fn save_state(&mut self) {
        self.state_stack.push(CanvasState {
            transform: self.transform,
            mask: self.mask.clone(),
        });
    }

    pub fn restore_state(&mut self) -> PyResult<()> {
        if let Some(state) = self.state_stack.pop() {
            self.transform = state.transform;
            self.mask = state.mask;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err(
                "No saved states left on canvas stack to restore",
            ))
        }
    }

    pub fn translate(&mut self, tx: f32, ty: f32) {
        self.transform = self.transform.pre_translate(tx, ty);
    }

    pub fn rotate(&mut self, degrees: f32) {
        self.transform = self.transform.pre_rotate(degrees);
    }

    pub fn scale(&mut self, sx: f32, sy: f32) {
        self.transform = self.transform.pre_scale(sx, sy);
    }

    pub fn reset_transform(&mut self) {
        self.transform = Transform::identity();
    }

    // --- Clipping Masks ---

    pub fn clip_path(&mut self, path: &mut Path) -> PyResult<()> {
        let skia_path = path
            .get_skia_path()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Empty path cannot be used for clipping"))?;

        if let Some(existing) = &mut self.mask {
            existing.intersect_path(&skia_path, FillRule::Winding, true, self.transform);
        } else {
            let mut mask = match Mask::new(self.pixmap.width(), self.pixmap.height()) {
                Some(m) => m,
                None => return Err(pyo3::exceptions::PyMemoryError::new_err("Failed to allocate clip mask")),
            };
            mask.fill_path(&skia_path, FillRule::Winding, true, self.transform);
            self.mask = Some(mask);
        }
        Ok(())
    }

    pub fn clip_rect(&mut self, x: f32, y: f32, width: f32, height: f32) -> PyResult<()> {
        let rect = Rect::from_xywh(x, y, width, height)
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid clip rect dimensions"))?;
        let mut pb = PathBuilder::new();
        pb.push_rect(rect);
        let skia_path = pb.finish().unwrap();

        let mut path_obj = Path {
            builder: None,
            finished: Some(skia_path),
        };
        self.clip_path(&mut path_obj)
    }

    pub fn clip_circle(&mut self, cx: f32, cy: f32, radius: f32) -> PyResult<()> {
        if radius <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err("Clip circle radius must be positive"));
        }
        let mut pb = PathBuilder::new();
        pb.push_circle(cx, cy, radius);
        let skia_path = pb.finish().unwrap();

        let mut path_obj = Path {
            builder: None,
            finished: Some(skia_path),
        };
        self.clip_path(&mut path_obj)
    }

    #[pyo3(signature = (x, y, width, height, rx, ry=None))]
    pub fn clip_rounded_rect(
        &mut self,
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        rx: f32,
        ry: Option<f32>,
    ) -> PyResult<()> {
        let ry = ry.unwrap_or(rx);
        let mut path = Path::new();
        path.add_rect(x, y, width, height)?;
        // Use smooth bezier rounded rectangle for clipping
        let right = x + width;
        let bottom = y + height;
        let k = 0.552284749831f32;
        let dx = rx * (1.0 - k);
        let dy = ry * (1.0 - k);

        let mut pb = PathBuilder::new();
        pb.move_to(x + rx, y);
        pb.line_to(right - rx, y);
        pb.cubic_to(right - dx, y, right, y + dy, right, y + ry);
        pb.line_to(right, bottom - ry);
        pb.cubic_to(right, bottom - dy, right - dx, bottom, right - rx, bottom);
        pb.line_to(x + rx, bottom);
        pb.cubic_to(x + dx, bottom, x, bottom - dy, x, bottom - ry);
        pb.line_to(x, y + ry);
        pb.cubic_to(x, y + dy, x + dx, y, x + rx, y);
        pb.close();

        let skia_path = pb.finish().ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct rounded rect clip")
        })?;

        let mut path_obj = Path {
            builder: None,
            finished: Some(skia_path),
        };
        self.clip_path(&mut path_obj)
    }

    pub fn reset_clip(&mut self) {
        self.mask = None;
    }

    // --- Drop Shadows & Glow ---

    #[pyo3(signature = (x, y, width, height, rx=0.0, ry=None, blur=10.0, offset_x=0.0, offset_y=4.0, color=None))]
    pub fn draw_drop_shadow(
        &mut self,
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        rx: f32,
        ry: Option<f32>,
        blur: f32,
        offset_x: f32,
        offset_y: f32,
        color: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let c = if let Some(c_obj) = color {
            parse_color(c_obj)?
        } else {
            Color::from_rgba8(0, 0, 0, 128)
        };

        shadow::render_drop_shadow_rect(
            &mut self.pixmap,
            x,
            y,
            width,
            height,
            rx,
            ry.unwrap_or(rx),
            blur,
            offset_x,
            offset_y,
            c,
        );
        Ok(())
    }

    #[pyo3(signature = (cx, cy, radius, blur=15.0, color=None))]
    pub fn draw_glow(
        &mut self,
        cx: f32,
        cy: f32,
        radius: f32,
        blur: f32,
        color: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let c = if let Some(c_obj) = color {
            parse_color(c_obj)?
        } else {
            Color::from_rgba8(255, 255, 255, 180)
        };

        shadow::render_drop_shadow_circle(
            &mut self.pixmap,
            cx,
            cy,
            radius,
            blur,
            0.0,
            0.0,
            c,
        );
        Ok(())
    }

    // --- Modern Typography ---

    #[pyo3(signature = (text, x, y, size=16.0, color=None, font=None))]
    pub fn draw_text(
        &mut self,
        text: &str,
        x: f32,
        y: f32,
        size: f32,
        color: Option<&Bound<'_, PyAny>>,
        font: Option<&Font>,
    ) -> PyResult<()> {
        let c = if let Some(c_obj) = color {
            parse_color(c_obj)?
        } else {
            Color::BLACK
        };

        let resolved_font = if let Some(f) = font {
            f.clone()
        } else {
            Font::get_default()?
        };

        text::draw_text_to_pixmap(
            &mut self.pixmap,
            &resolved_font.inner,
            text,
            x,
            y,
            size,
            c,
        );
        Ok(())
    }

    #[pyo3(signature = (text, x, y, max_width, size=16.0, color=None, line_spacing=4.0, font=None))]
    pub fn draw_text_box(
        &mut self,
        text: &str,
        x: f32,
        y: f32,
        max_width: f32,
        size: f32,
        color: Option<&Bound<'_, PyAny>>,
        line_spacing: f32,
        font: Option<&Font>,
    ) -> PyResult<(f32, f32)> {
        let c = if let Some(c_obj) = color {
            parse_color(c_obj)?
        } else {
            Color::BLACK
        };

        let resolved_font = if let Some(f) = font {
            f.clone()
        } else {
            Font::get_default()?
        };

        let mut cur_y = y;
        let mut max_line_w = 0.0f32;

        for line in text.split('\n') {
            let words = line.split_whitespace().collect::<Vec<_>>();
            if words.is_empty() {
                cur_y += size + line_spacing;
                continue;
            }

            let mut cur_line = String::new();
            for word in words {
                let test_line = if cur_line.is_empty() {
                    word.to_string()
                } else {
                    format!("{} {}", cur_line, word)
                };

                let (tw, _) = text::measure_text_dimensions(&resolved_font.inner, &test_line, size);
                if tw > max_width && !cur_line.is_empty() {
                    let (lw, _) = text::measure_text_dimensions(&resolved_font.inner, &cur_line, size);
                    if lw > max_line_w {
                        max_line_w = lw;
                    }
                    text::draw_text_to_pixmap(
                        &mut self.pixmap,
                        &resolved_font.inner,
                        &cur_line,
                        x,
                        cur_y,
                        size,
                        c,
                    );
                    cur_y += size + line_spacing;
                    cur_line = word.to_string();
                } else {
                    cur_line = test_line;
                }
            }

            if !cur_line.is_empty() {
                let (lw, _) = text::measure_text_dimensions(&resolved_font.inner, &cur_line, size);
                if lw > max_line_w {
                    max_line_w = lw;
                }
                text::draw_text_to_pixmap(
                    &mut self.pixmap,
                    &resolved_font.inner,
                    &cur_line,
                    x,
                    cur_y,
                    size,
                    c,
                );
                cur_y += size + line_spacing;
            }
        }

        let total_height = cur_y - y;
        Ok((max_line_w, total_height))
    }

    #[pyo3(signature = (text, size=16.0, font=None))]
    pub fn measure_text(
        &self,
        text: &str,
        size: f32,
        font: Option<&Font>,
    ) -> PyResult<(f32, f32)> {
        let resolved_font = if let Some(f) = font {
            f.clone()
        } else {
            Font::get_default()?
        };
        Ok(text::measure_text_dimensions(&resolved_font.inner, text, size))
    }

    // --- Full SVG Rendering (resvg) ---

    #[pyo3(signature = (svg_content, x=0.0, y=0.0, width=None, height=None))]
    pub fn draw_svg_document(
        &mut self,
        svg_content: &str,
        x: f32,
        y: f32,
        width: Option<f32>,
        height: Option<f32>,
    ) -> PyResult<()> {
        svg_render::render_svg_str(&mut self.pixmap, svg_content, x, y, width, height)
    }

    #[pyo3(signature = (path, x=0.0, y=0.0, width=None, height=None))]
    pub fn draw_svg_file(
        &mut self,
        path: &str,
        x: f32,
        y: f32,
        width: Option<f32>,
        height: Option<f32>,
    ) -> PyResult<()> {
        svg_render::render_svg_file(&mut self.pixmap, path, x, y, width, height)
    }

    // --- Basic Drawing Primitives ---

    pub fn fill(&mut self, color_obj: &Bound<'_, PyAny>) -> PyResult<()> {
        let color = parse_color(color_obj)?;
        self.pixmap.fill(color);
        Ok(())
    }

    pub fn clear(&mut self) {
        self.pixmap.fill(Color::TRANSPARENT);
    }

    #[pyo3(signature = (x, y, width, height, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_rect(
        &mut self,
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        let rect = Rect::from_xywh(x, y, width, height).ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Invalid rectangle coordinates or dimensions")
        })?;

        let mut pb = PathBuilder::new();
        pb.push_rect(rect);
        let path = pb.finish().unwrap();

        self.apply_path_draw(&path, fill, stroke, stroke_width, LineCap::Butt, LineJoin::Miter)
    }

    #[pyo3(signature = (x, y, width, height, rx, ry=None, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_rounded_rect(
        &mut self,
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        rx: f32,
        ry: Option<f32>,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        let radius_y = ry.unwrap_or(rx);
        let rx = rx.min(width / 2.0);
        let ry = radius_y.min(height / 2.0);

        let mut pb = PathBuilder::new();
        let right = x + width;
        let bottom = y + height;

        let k = 0.552284749831f32;
        let dx = rx * (1.0 - k);
        let dy = ry * (1.0 - k);

        pb.move_to(x + rx, y);
        pb.line_to(right - rx, y);
        pb.cubic_to(right - dx, y, right, y + dy, right, y + ry);
        pb.line_to(right, bottom - ry);
        pb.cubic_to(right, bottom - dy, right - dx, bottom, right - rx, bottom);
        pb.line_to(x + rx, bottom);
        pb.cubic_to(x + dx, bottom, x, bottom - dy, x, bottom - ry);
        pb.line_to(x, y + ry);
        pb.cubic_to(x, y + dy, x + dx, y, x + rx, y);
        pb.close();

        let path = pb.finish().ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct rounded rectangle path")
        })?;

        self.apply_path_draw(&path, fill, stroke, stroke_width, LineCap::Round, LineJoin::Round)
    }

    #[pyo3(signature = (cx, cy, radius, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_circle(
        &mut self,
        cx: f32,
        cy: f32,
        radius: f32,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        if radius <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err("Circle radius must be positive"));
        }

        let mut pb = PathBuilder::new();
        pb.push_circle(cx, cy, radius);
        let path = pb.finish().unwrap();

        self.apply_path_draw(&path, fill, stroke, stroke_width, LineCap::Round, LineJoin::Round)
    }

    #[pyo3(signature = (cx, cy, rx, ry, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_ellipse(
        &mut self,
        cx: f32,
        cy: f32,
        rx: f32,
        ry: f32,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        if rx <= 0.0 || ry <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Ellipse radii must be positive",
            ));
        }

        let k = 0.552284749831f32;
        let ox = rx * k;
        let oy = ry * k;

        let mut pb = PathBuilder::new();
        pb.move_to(cx - rx, cy);
        pb.cubic_to(cx - rx, cy - oy, cx - ox, cy - ry, cx, cy - ry);
        pb.cubic_to(cx + ox, cy - ry, cx + rx, cy - oy, cx + rx, cy);
        pb.cubic_to(cx + rx, cy + oy, cx + ox, cy + ry, cx, cy + ry);
        pb.cubic_to(cx - ox, cy + ry, cx - rx, cy + oy, cx - rx, cy);
        pb.close();

        let path = pb.finish().unwrap();
        self.apply_path_draw(&path, fill, stroke, stroke_width, LineCap::Round, LineJoin::Round)
    }

    #[pyo3(signature = (x1, y1, x2, y2, stroke, stroke_width=1.0, line_cap="round"))]
    pub fn draw_line(
        &mut self,
        x1: f32,
        y1: f32,
        x2: f32,
        y2: f32,
        stroke: &Bound<'_, PyAny>,
        stroke_width: f32,
        line_cap: &str,
    ) -> PyResult<()> {
        let mut pb = PathBuilder::new();
        pb.move_to(x1, y1);
        pb.line_to(x2, y2);
        let path = pb.finish().unwrap();

        let cap = parse_line_cap(line_cap)?;
        self.apply_path_draw(&path, None, Some(stroke), stroke_width, cap, LineJoin::Round)
    }

    #[pyo3(signature = (points, stroke, stroke_width=1.0, closed=false, line_cap="round", line_join="round"))]
    pub fn draw_polyline(
        &mut self,
        points: &Bound<'_, PyAny>,
        stroke: &Bound<'_, PyAny>,
        stroke_width: f32,
        closed: bool,
        line_cap: &str,
        line_join: &str,
    ) -> PyResult<()> {
        let seq = points.downcast::<PySequence>()?;
        let len = seq.len()?;
        if len < 2 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Polyline must contain at least 2 points",
            ));
        }

        let mut pb = PathBuilder::new();
        for i in 0..len {
            let pt_obj = seq.get_item(i)?;
            let pt = pt_obj.downcast::<PySequence>()?;
            let px: f32 = pt.get_item(0)?.extract()?;
            let py: f32 = pt.get_item(1)?.extract()?;
            if i == 0 {
                pb.move_to(px, py);
            } else {
                pb.line_to(px, py);
            }
        }
        if closed {
            pb.close();
        }

        let path = pb.finish().ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct polyline path")
        })?;

        let cap = parse_line_cap(line_cap)?;
        let join = parse_line_join(line_join)?;
        self.apply_path_draw(&path, None, Some(stroke), stroke_width, cap, join)
    }

    #[pyo3(signature = (points, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_polygon(
        &mut self,
        points: &Bound<'_, PyAny>,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        let seq = points.downcast::<PySequence>()?;
        let len = seq.len()?;
        if len < 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Polygon must contain at least 3 points",
            ));
        }

        let mut pb = PathBuilder::new();
        for i in 0..len {
            let pt_obj = seq.get_item(i)?;
            let pt = pt_obj.downcast::<PySequence>()?;
            let px: f32 = pt.get_item(0)?.extract()?;
            let py: f32 = pt.get_item(1)?.extract()?;
            if i == 0 {
                pb.move_to(px, py);
            } else {
                pb.line_to(px, py);
            }
        }
        pb.close();

        let path = pb.finish().ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct polygon path")
        })?;

        self.apply_path_draw(&path, fill, stroke, stroke_width, LineCap::Round, LineJoin::Round)
    }

    #[pyo3(signature = (path, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_path(
        &mut self,
        path: &mut Path,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        let skia_path = path
            .get_skia_path()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Empty or unfinished path"))?;

        self.apply_path_draw(&skia_path, fill, stroke, stroke_width, LineCap::Round, LineJoin::Round)
    }

    #[pyo3(signature = (svg_d, fill=None, stroke=None, stroke_width=1.0))]
    pub fn draw_svg_path(
        &mut self,
        svg_d: &str,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
    ) -> PyResult<()> {
        let mut path = Path::from_svg(svg_d)?;
        self.draw_path(&mut path, fill, stroke, stroke_width)
    }

    #[pyo3(signature = (other, x, y, opacity=1.0, blend_mode="source_over"))]
    pub fn draw_image(
        &mut self,
        other: &Canvas,
        x: f32,
        y: f32,
        opacity: f32,
        blend_mode: &str,
    ) -> PyResult<()> {
        let bm = parse_blend_mode(blend_mode)?;
        let mut paint = tiny_skia::PixmapPaint::default();
        paint.opacity = opacity.clamp(0.0, 1.0);
        paint.blend_mode = bm;

        self.pixmap.draw_pixmap(
            x.round() as i32,
            y.round() as i32,
            other.pixmap.as_ref(),
            &paint,
            self.transform,
            self.mask.as_ref(),
        );
        Ok(())
    }

    #[pyo3(signature = (dst_width, dst_height, filter="bilinear"))]
    pub fn resize(&self, dst_width: u32, dst_height: u32, filter: &str) -> PyResult<Canvas> {
        let ftype = transform::parse_filter_type(filter)?;
        let resized_bytes = transform::resize_rgba(
            self.pixmap.data(),
            self.pixmap.width(),
            self.pixmap.height(),
            dst_width,
            dst_height,
            ftype,
        )?;

        let mut out = Canvas::new(dst_width, dst_height, None)?;
        out.pixmap.data_mut().copy_from_slice(&resized_bytes);
        Ok(out)
    }

    pub fn blur(&self, sigma: f32) -> PyResult<Canvas> {
        let blurred_bytes = filters::fast_gaussian_blur(
            self.pixmap.data(),
            self.pixmap.width(),
            self.pixmap.height(),
            sigma,
        );

        let mut out = Canvas::new(self.pixmap.width(), self.pixmap.height(), None)?;
        out.pixmap.data_mut().copy_from_slice(&blurred_bytes);
        Ok(out)
    }

    pub fn adjust_brightness(&self, factor: f32) -> PyResult<Canvas> {
        let mut out = self.clone();
        filters::adjust_brightness_inplace(out.pixmap.data_mut(), factor);
        Ok(out)
    }

    pub fn adjust_contrast(&self, factor: f32) -> PyResult<Canvas> {
        let mut out = self.clone();
        filters::adjust_contrast_inplace(out.pixmap.data_mut(), factor);
        Ok(out)
    }

    pub fn invert(&self) -> PyResult<Canvas> {
        let mut out = self.clone();
        filters::invert_inplace(out.pixmap.data_mut());
        Ok(out)
    }

    pub fn grayscale(&self) -> PyResult<Canvas> {
        let mut out = self.clone();
        filters::grayscale_inplace(out.pixmap.data_mut());
        Ok(out)
    }

    pub fn to_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new_bound(py, self.pixmap.data())
    }

    #[staticmethod]
    pub fn from_bytes(width: u32, height: u32, data: &[u8]) -> PyResult<Self> {
        let expected_len = (width as usize) * (height as usize) * 4;
        if data.len() != expected_len {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Data size mismatch: expected {} bytes for {}x{} RGBA, got {}",
                expected_len,
                width,
                height,
                data.len()
            )));
        }

        let mut canvas = Canvas::new(width, height, None)?;
        canvas.pixmap.data_mut().copy_from_slice(data);
        Ok(canvas)
    }

    #[staticmethod]
    pub fn open(path: &str) -> PyResult<Self> {
        let img = image::open(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to open image '{}': {}", path, e))
        })?;
        let rgba = img.to_rgba8();
        let (w, h) = rgba.dimensions();
        let mut canvas = Canvas::new(w, h, None)?;
        canvas.pixmap.data_mut().copy_from_slice(rgba.as_raw());
        Ok(canvas)
    }

    #[pyo3(signature = (path, quality=None))]
    pub fn save(&self, path: &str, quality: Option<u8>) -> PyResult<()> {
        let file = File::create(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to create file '{}': {}", path, e))
        })?;
        let writer = BufWriter::new(file);

        let ext = StdPath::new(path)
            .extension()
            .and_then(|s| s.to_str())
            .unwrap_or("png")
            .to_lowercase();

        let w = self.pixmap.width();
        let h = self.pixmap.height();
        let data = self.pixmap.data();

        match ext.as_str() {
            "png" => {
                self.pixmap.save_png(path).map_err(|e| {
                    pyo3::exceptions::PyIOError::new_err(format!("Failed to save PNG: {}", e))
                })?;
            }
            "jpg" | "jpeg" => {
                let img_buf = image::RgbaImage::from_raw(w, h, data.to_vec()).ok_or_else(|| {
                    pyo3::exceptions::PyRuntimeError::new_err("Failed to construct image buffer")
                })?;
                let rgb_buf = image::DynamicImage::ImageRgba8(img_buf).to_rgb8();
                let q = quality.unwrap_or(90);
                let mut encoder = image::codecs::jpeg::JpegEncoder::new_with_quality(writer, q);
                encoder
                    .encode(
                        rgb_buf.as_raw(),
                        w,
                        h,
                        image::ExtendedColorType::Rgb8,
                    )
                    .map_err(|e| {
                        pyo3::exceptions::PyIOError::new_err(format!("JPEG encoding failed: {}", e))
                    })?;
            }
            "webp" => {
                let img_buf = image::RgbaImage::from_raw(w, h, data.to_vec()).ok_or_else(|| {
                    pyo3::exceptions::PyRuntimeError::new_err("Failed to construct image buffer")
                })?;
                let dyn_img = image::DynamicImage::ImageRgba8(img_buf);
                dyn_img
                    .save_with_format(path, image::ImageFormat::WebP)
                    .map_err(|e| {
                        pyo3::exceptions::PyIOError::new_err(format!("WebP encoding failed: {}", e))
                    })?;
            }
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unsupported image format '{}'. Supported: .png, .jpg, .jpeg, .webp",
                    ext
                )));
            }
        }
        Ok(())
    }

    pub fn clone_canvas(&self) -> Canvas {
        self.clone()
    }
}

impl Canvas {
    fn apply_path_draw(
        &mut self,
        path: &tiny_skia::Path,
        fill: Option<&Bound<'_, PyAny>>,
        stroke: Option<&Bound<'_, PyAny>>,
        stroke_width: f32,
        line_cap: LineCap,
        line_join: LineJoin,
    ) -> PyResult<()> {
        if let Some(fill_obj) = fill {
            with_paint(fill_obj, |paint| {
                self.pixmap.fill_path(
                    path,
                    paint,
                    FillRule::Winding,
                    self.transform,
                    self.mask.as_ref(),
                );
            })?;
        }

        if let Some(stroke_obj) = stroke {
            with_paint(stroke_obj, |paint| {
                let mut s = Stroke::default();
                s.width = stroke_width;
                s.line_cap = line_cap;
                s.line_join = line_join;
                self.pixmap.stroke_path(
                    path,
                    paint,
                    &s,
                    self.transform,
                    self.mask.as_ref(),
                );
            })?;
        }

        Ok(())
    }
}
