use pyo3::prelude::*;
use pyo3::types::{PyFloat, PyInt, PySequence, PyString};
use tiny_skia::Color;

pub fn parse_color(obj: &Bound<'_, PyAny>) -> PyResult<Color> {
    if let Ok(s) = obj.downcast::<PyString>() {
        let text = s.to_str()?;
        let parsed = csscolorparser::parse(text).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid color string '{}': {}", text, e))
        })?;
        Color::from_rgba(
            parsed.r as f32,
            parsed.g as f32,
            parsed.b as f32,
            parsed.a as f32,
        )
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid color component ranges"))
    } else if let Ok(seq) = obj.downcast::<PySequence>() {
        let len = seq.len()?;
        if len != 3 && len != 4 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Color sequence must contain 3 (RGB) or 4 (RGBA) elements",
            ));
        }

        let extract_comp = |item: Bound<'_, PyAny>| -> PyResult<f32> {
            if let Ok(i) = item.downcast::<PyInt>() {
                let val: i64 = i.extract()?;
                Ok((val as f32 / 255.0).clamp(0.0, 1.0))
            } else if let Ok(f) = item.downcast::<PyFloat>() {
                let val: f64 = f.extract()?;
                if val > 1.0 {
                    Ok((val as f32 / 255.0).clamp(0.0, 1.0))
                } else {
                    Ok((val as f32).clamp(0.0, 1.0))
                }
            } else {
                Err(pyo3::exceptions::PyTypeError::new_err(
                    "Color components must be int (0-255) or float (0.0-1.0)",
                ))
            }
        };

        let r = extract_comp(seq.get_item(0)?)?;
        let g = extract_comp(seq.get_item(1)?)?;
        let b = extract_comp(seq.get_item(2)?)?;
        let a = if len == 4 {
            extract_comp(seq.get_item(3)?)?
        } else {
            1.0
        };

        Color::from_rgba(r, g, b, a).ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct RGBA color")
        })
    } else if let Ok(int_val) = obj.downcast::<PyInt>() {
        let val: u32 = int_val.extract()?;
        let (r, g, b, a) = if val <= 0xFFFFFF {
            (
                ((val >> 16) & 0xFF) as f32 / 255.0,
                ((val >> 8) & 0xFF) as f32 / 255.0,
                (val & 0xFF) as f32 / 255.0,
                1.0,
            )
        } else {
            (
                ((val >> 24) & 0xFF) as f32 / 255.0,
                ((val >> 16) & 0xFF) as f32 / 255.0,
                ((val >> 8) & 0xFF) as f32 / 255.0,
                (val & 0xFF) as f32 / 255.0,
            )
        };
        Color::from_rgba(r, g, b, a).ok_or_else(|| {
            pyo3::exceptions::PyValueError::new_err("Failed to construct color from int")
        })
    } else {
        Err(pyo3::exceptions::PyTypeError::new_err(
            "Color must be a CSS/hex string (e.g. '#ff0000', 'rgba(255,0,0,0.5)'), an RGB(A) tuple/list, or an integer",
        ))
    }
}
