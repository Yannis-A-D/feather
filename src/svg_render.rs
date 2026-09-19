use pyo3::prelude::*;
use std::fs;
use tiny_skia::{Pixmap, Transform};

pub fn render_svg_str(
    pixmap: &mut Pixmap,
    svg_content: &str,
    x: f32,
    y: f32,
    target_width: Option<f32>,
    target_height: Option<f32>,
) -> PyResult<()> {
    let opt = usvg::Options::default();
    let tree = usvg::Tree::from_str(svg_content, &opt).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("SVG parsing error: {}", e))
    })?;

    let orig_size = tree.size();
    let orig_w = orig_size.width();
    let orig_h = orig_size.height();

    let sx = if let Some(tw) = target_width {
        tw / orig_w
    } else {
        1.0
    };

    let sy = if let Some(th) = target_height {
        th / orig_h
    } else {
        sx
    };

    let ts = Transform::from_translate(x, y).pre_scale(sx, sy);
    resvg::render(&tree, ts, &mut pixmap.as_mut());
    Ok(())
}

pub fn render_svg_file(
    pixmap: &mut Pixmap,
    path: &str,
    x: f32,
    y: f32,
    target_width: Option<f32>,
    target_height: Option<f32>,
) -> PyResult<()> {
    let content = fs::read_to_string(path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to read SVG file '{}': {}", path, e))
    })?;
    render_svg_str(pixmap, &content, x, y, target_width, target_height)
}
