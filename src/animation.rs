use crate::canvas::Canvas;
use image::codecs::gif::{GifEncoder, Repeat};
use image::{Delay, Frame, RgbaImage};
use pyo3::prelude::*;
use std::fs::File;
use std::io::BufWriter;
use std::time::Duration;

#[pyfunction]
#[pyo3(signature = (frames, path, fps=20, loop_count=0))]
pub fn save_gif(
    frames: Vec<Canvas>,
    path: &str,
    fps: u32,
    loop_count: u16,
) -> PyResult<()> {
    if frames.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "frames list cannot be empty",
        ));
    }

    let fps = fps.max(1);
    let frame_millis = (1000.0 / fps as f64).round() as u64;
    let delay = Delay::from_saturating_duration(Duration::from_millis(frame_millis));

    let file = File::create(path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to create file '{}': {}", path, e))
    })?;
    let writer = BufWriter::new(file);
    let mut encoder = GifEncoder::new_with_speed(writer, 10);

    let repeat_mode = if loop_count == 0 {
        Repeat::Infinite
    } else {
        Repeat::Finite(loop_count)
    };
    encoder
        .set_repeat(repeat_mode)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to set repeat: {}", e)))?;

    for canvas in frames {
        let w = canvas.pixmap.width();
        let h = canvas.pixmap.height();
        let img_buf = RgbaImage::from_raw(w, h, canvas.pixmap.data().to_vec()).ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Failed to create frame buffer")
        })?;

        let frame = Frame::from_parts(img_buf, 0, 0, delay);
        encoder.encode_frame(frame).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to encode GIF frame: {}", e))
        })?;
    }

    Ok(())
}
