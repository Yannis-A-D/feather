use crate::canvas::Canvas;
use image::codecs::gif::{GifEncoder, Repeat};
use image::{Delay, Frame as GifFrame, RgbaImage};
use pyo3::prelude::*;
use std::fs::File;
use std::io::BufWriter;
use std::time::Duration;

/// Extract unpremultiplied RGBA8 bytes from tiny-skia pixmap
fn get_straight_rgba(pixmap: &tiny_skia::Pixmap) -> Vec<u8> {
    let mut data = Vec::with_capacity((pixmap.width() * pixmap.height() * 4) as usize);
    for pixel in pixmap.pixels() {
        let c = pixel.demultiply();
        data.push(c.red());
        data.push(c.green());
        data.push(c.blue());
        data.push(c.alpha());
    }
    data
}

fn validate_frames(frames: &[Canvas]) -> PyResult<(u32, u32)> {
    if frames.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "frames list cannot be empty",
        ));
    }
    let w = frames[0].pixmap.width();
    let h = frames[0].pixmap.height();
    for (i, f) in frames.iter().enumerate() {
        if f.pixmap.width() != w || f.pixmap.height() != h {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Frame {} dimensions ({}x{}) do not match initial frame dimensions ({}x{})",
                i,
                f.pixmap.width(),
                f.pixmap.height(),
                w,
                h
            )));
        }
    }
    Ok((w, h))
}

#[pyfunction]
#[pyo3(signature = (frames, path, fps=20, loop_count=0))]
pub fn save_gif(
    frames: Vec<Canvas>,
    path: &str,
    fps: u32,
    loop_count: u16,
) -> PyResult<()> {
    let (w, h) = validate_frames(&frames)?;

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
        let straight_rgba = get_straight_rgba(&canvas.pixmap);
        let img_buf = RgbaImage::from_raw(w, h, straight_rgba).ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Failed to create frame buffer")
        })?;

        let frame = GifFrame::from_parts(img_buf, 0, 0, delay);
        encoder.encode_frame(frame).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to encode GIF frame: {}", e))
        })?;
    }

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (frames, path, fps=20, loop_count=0))]
pub fn save_apng(
    frames: Vec<Canvas>,
    path: &str,
    fps: u32,
    loop_count: u16,
) -> PyResult<()> {
    let (w, h) = validate_frames(&frames)?;

    let mut png_images = Vec::with_capacity(frames.len());
    for canvas in &frames {
        let raw_data = get_straight_rgba(&canvas.pixmap);
        png_images.push(apng::PNGImage {
            width: w,
            height: h,
            data: raw_data,
            color_type: png::ColorType::Rgba,
            bit_depth: png::BitDepth::Eight,
        });
    }

    let file = File::create(path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to create file '{}': {}", path, e))
    })?;
    let mut writer = BufWriter::new(file);

    let config = apng::create_config(&png_images, Some(loop_count as u32)).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("APNG config error: {:?}", e))
    })?;
    let mut encoder = apng::Encoder::new(&mut writer, config).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("APNG encoder initialization error: {:?}", e))
    })?;

    let frame_meta = apng::Frame {
        delay_num: Some(1),
        delay_den: Some(fps.max(1) as u16),
        ..Default::default()
    };

    encoder
        .encode_all(png_images, Some(&frame_meta))
        .map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("APNG encode failed: {:?}", e))
        })?;

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (frames, path, fps=20, loop_count=0, quality=None, lossless=true))]
pub fn save_webp(
    frames: Vec<Canvas>,
    path: &str,
    fps: u32,
    loop_count: u16,
    quality: Option<f32>,
    lossless: bool,
) -> PyResult<()> {
    let (w, h) = validate_frames(&frames)?;

    let fps = fps.max(1);
    let frame_duration_ms = 1000.0 / (fps as f64);

    let encoding_config = if let Some(q) = quality {
        webp_animation::prelude::EncodingConfig::new_lossy(q.clamp(0.0, 100.0))
    } else if lossless {
        webp_animation::prelude::EncodingConfig {
            encoding_type: webp_animation::prelude::EncodingType::Lossless,
            quality: 100.0,
            method: 4,
        }
    } else {
        webp_animation::prelude::EncodingConfig::new_lossy(80.0)
    };

    let options = webp_animation::prelude::EncoderOptions {
        anim_params: webp_animation::AnimParams {
            loop_count: loop_count as i32,
        },
        encoding_config: Some(encoding_config),
        ..Default::default()
    };

    let mut encoder = webp_animation::prelude::Encoder::new_with_options((w, h), options)
        .map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to initialize WebP encoder: {:?}",
                e
            ))
        })?;

    for (i, canvas) in frames.iter().enumerate() {
        let rgba = get_straight_rgba(&canvas.pixmap);
        let timestamp_ms = (i as f64 * frame_duration_ms).round() as i32;
        encoder.add_frame(&rgba, timestamp_ms).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to add WebP frame {}: {:?}",
                i, e
            ))
        })?;
    }

    let total_timestamp_ms = (frames.len() as f64 * frame_duration_ms).round() as i32;
    let webp_data = encoder.finalize(total_timestamp_ms).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!(
            "Failed to finalize WebP animation: {:?}",
            e
        ))
    })?;

    std::fs::write(path, &*webp_data).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to write WebP file '{}': {}", path, e))
    })?;

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (frames, path, fps=20, loop_count=0, quality=None, lossless=true))]
pub fn save_animation(
    frames: Vec<Canvas>,
    path: &str,
    fps: u32,
    loop_count: u16,
    quality: Option<f32>,
    lossless: bool,
) -> PyResult<()> {
    let ext = std::path::Path::new(path)
        .extension()
        .and_then(|s| s.to_str())
        .unwrap_or("gif")
        .to_lowercase();

    match ext.as_str() {
        "webp" => save_webp(frames, path, fps, loop_count, quality, lossless),
        "apng" | "png" => save_apng(frames, path, fps, loop_count),
        "gif" => save_gif(frames, path, fps, loop_count),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unsupported animation extension '{}'. Supported: .webp, .apng, .png, .gif",
            ext
        ))),
    }
}
