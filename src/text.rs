use fontdue::{Font as FdFont, FontSettings};
use pyo3::prelude::*;
use std::fs::File;
use std::io::Read;
use std::sync::Arc;
use tiny_skia::{Color, Pixmap};

#[pyclass]
#[derive(Clone)]
pub struct Font {
    pub(crate) inner: Arc<FdFont>,
}

impl Font {
    pub fn get_default() -> PyResult<Self> {
        // Try common system fonts across Windows, macOS, and Linux
        let candidates = [
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\calibri.ttf",
            "/System/Library/Fonts/SFNS.ttf",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ];

        for path in candidates {
            if let Ok(mut file) = File::open(path) {
                let mut buffer = Vec::new();
                if file.read_to_end(&mut buffer).is_ok() {
                    if let Ok(font) = FdFont::from_bytes(buffer, FontSettings::default()) {
                        return Ok(Font {
                            inner: Arc::new(font),
                        });
                    }
                }
            }
        }

        Err(pyo3::exceptions::PyRuntimeError::new_err(
            "No default system font found. Please load a font explicitly with Font.load('path/to/font.ttf')",
        ))
    }
}

#[pymethods]
impl Font {
    #[new]
    pub fn new(data: &[u8]) -> PyResult<Self> {
        let font = FdFont::from_bytes(data, FontSettings::default()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Failed to parse font data: {}", e))
        })?;
        Ok(Font {
            inner: Arc::new(font),
        })
    }

    #[staticmethod]
    pub fn load(path: &str) -> PyResult<Self> {
        let mut file = File::open(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Cannot open font file '{}': {}", path, e))
        })?;
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to read font file '{}': {}", path, e))
        })?;
        Self::new(&buffer)
    }

    #[staticmethod]
    pub fn default_font() -> PyResult<Self> {
        Self::get_default()
    }
}

pub fn measure_text_dimensions(
    font: &FdFont,
    text: &str,
    size: f32,
) -> (f32, f32) {
    let mut width = 0.0f32;
    let mut max_height = size;

    for ch in text.chars() {
        if ch == '\n' {
            continue;
        }
        let metrics = font.metrics(ch, size);
        width += metrics.advance_width;
        if metrics.height as f32 > max_height {
            max_height = metrics.height as f32;
        }
    }

    (width, max_height)
}

pub fn draw_text_to_pixmap(
    pixmap: &mut Pixmap,
    font: &FdFont,
    text: &str,
    mut x: f32,
    y: f32,
    size: f32,
    color: Color,
) {
    let pw = pixmap.width() as i32;
    let ph = pixmap.height() as i32;
    let baseline_y = y + size * 0.8;

    let cr = (color.red() * 255.0).round() as u32;
    let cg = (color.green() * 255.0).round() as u32;
    let cb = (color.blue() * 255.0).round() as u32;
    let ca = (color.alpha() * 255.0).round() as u32;

    for ch in text.chars() {
        if ch == '\n' {
            continue;
        }

        let (metrics, bitmap) = font.rasterize(ch, size);
        let gx = (x + metrics.xmin as f32).round() as i32;
        let gy = (baseline_y - metrics.height as f32 - metrics.ymin as f32).round() as i32;

        let gw = metrics.width as i32;
        let gh = metrics.height as i32;

        let pixels = pixmap.data_mut();

        for row in 0..gh {
            let py = gy + row;
            if py < 0 || py >= ph {
                continue;
            }

            for col in 0..gw {
                let px = gx + col;
                if px < 0 || px >= pw {
                    continue;
                }

                let coverage = bitmap[(row * gw + col) as usize] as u32;
                if coverage == 0 {
                    continue;
                }

                // Premultiplied alpha blend with coverage
                let alpha = (ca * coverage) / 255;
                if alpha == 0 {
                    continue;
                }

                let src_r = (cr * alpha) / 255;
                let src_g = (cg * alpha) / 255;
                let src_b = (cb * alpha) / 255;

                let idx = ((py * pw + px) * 4) as usize;
                let dst_r = pixels[idx] as u32;
                let dst_g = pixels[idx + 1] as u32;
                let dst_b = pixels[idx + 2] as u32;
                let dst_a = pixels[idx + 3] as u32;

                let inv_a = 255 - alpha;
                pixels[idx] = (src_r + (dst_r * inv_a) / 255).min(255) as u8;
                pixels[idx + 1] = (src_g + (dst_g * inv_a) / 255).min(255) as u8;
                pixels[idx + 2] = (src_b + (dst_b * inv_a) / 255).min(255) as u8;
                pixels[idx + 3] = (alpha + (dst_a * inv_a) / 255).min(255) as u8;
            }
        }

        x += metrics.advance_width;
    }
}
