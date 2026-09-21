use crate::canvas::Canvas;
use minifb::{Key, KeyRepeat, MouseButton, MouseMode, Scale, ScaleMode, Window, WindowOptions};
use pyo3::prelude::*;
use rayon::prelude::*;
use std::time::{Duration, Instant};

/// Interactive viewer options
#[pyfunction]
#[pyo3(signature = (frames, title="Feather Viewer", window_width=None, window_height=None, fps=30))]
pub fn show_interactive(
    frames: Vec<Canvas>,
    title: &str,
    window_width: Option<usize>,
    window_height: Option<usize>,
    fps: u32,
) -> PyResult<()> {
    if frames.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "frames list cannot be empty",
        ));
    }

    let cw = frames[0].pixmap.width() as usize;
    let ch = frames[0].pixmap.height() as usize;

    let target_w = window_width.unwrap_or_else(|| cw.clamp(640, 1400));
    let target_h = window_height.unwrap_or_else(|| ch.clamp(480, 900));

    let window_opts = WindowOptions {
        resize: true,
        scale: Scale::X1,
        scale_mode: ScaleMode::Stretch,
        ..WindowOptions::default()
    };

    let mut window = Window::new(title, target_w, target_h, window_opts).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to open window: {:?}", e))
    })?;

    // Target ~60 FPS update rate for smooth UI response
    window.set_target_fps(60);

    // Viewport and camera transform
    let fit_zoom = ((target_w as f32 / cw as f32).min(target_h as f32 / ch as f32) * 0.95).min(1.0);
    let mut zoom: f32 = fit_zoom.max(0.1);
    let mut pan_x: f32 = (target_w as f32 - cw as f32 * zoom) / 2.0;
    let mut pan_y: f32 = (target_h as f32 - ch as f32 * zoom) / 2.0;

    let mut last_mouse_pos: Option<(f32, f32)> = None;
    let total_frames = frames.len();
    let mut current_frame: usize = 0;
    let mut paused = total_frames <= 1;

    let target_frame_duration = Duration::from_secs_f64(1.0 / (fps.max(1) as f64));
    let mut last_frame_time = Instant::now();
    let mut buffer: Vec<u32> = vec![0; target_w * target_h];

    let base_title = title.to_string();

    while window.is_open() && !window.is_key_down(Key::Escape) && !window.is_key_down(Key::Q) {
        let (vw, vh) = window.get_size();
        if buffer.len() != vw * vh {
            buffer.resize(vw * vh, 0);
        }

        // --- Keyboard Handling ---
        if window.is_key_pressed(Key::Space, KeyRepeat::No) && total_frames > 1 {
            paused = !paused;
        }

        if window.is_key_pressed(Key::Right, KeyRepeat::Yes) && total_frames > 1 {
            current_frame = (current_frame + 1) % total_frames;
        }

        if window.is_key_pressed(Key::Left, KeyRepeat::Yes) && total_frames > 1 {
            current_frame = (current_frame + total_frames - 1) % total_frames;
        }

        // Reset View ('R')
        if window.is_key_pressed(Key::R, KeyRepeat::No) {
            zoom = ((vw as f32 / cw as f32).min(vh as f32 / ch as f32) * 0.95).min(1.0);
            pan_x = (vw as f32 - cw as f32 * zoom) / 2.0;
            pan_y = (vh as f32 - ch as f32 * zoom) / 2.0;
        }

        // Save Snapshot ('S')
        if window.is_key_pressed(Key::S, KeyRepeat::No) {
            let timestamp = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            let filename = format!("snapshot_{}.png", timestamp);
            if let Ok(()) = frames[current_frame].pixmap.save_png(&filename) {
                println!("Snapshot saved to: {}", filename);
            }
        }

        // --- Mouse Handling (Zoom & Pan) ---
        let current_mouse_pos = window.get_mouse_pos(MouseMode::Pass);

        // Scroll Wheel Zoom
        if let Some((_sx, sy)) = window.get_scroll_wheel() {
            if sy != 0.0 {
                let zoom_factor = if sy > 0.0 { 1.15 } else { 1.0 / 1.15 };
                let new_zoom = (zoom * zoom_factor).clamp(0.02, 100.0);

                if let Some((mx, my)) = current_mouse_pos {
                    let cx = (mx - pan_x) / zoom;
                    let cy = (my - pan_y) / zoom;
                    pan_x = mx - cx * new_zoom;
                    pan_y = my - cy * new_zoom;
                }
                zoom = new_zoom;
            }
        }

        // Left Click Drag Pan
        if window.get_mouse_down(MouseButton::Left) {
            if let (Some((mx, my)), Some((lx, ly))) = (current_mouse_pos, last_mouse_pos) {
                pan_x += mx - lx;
                pan_y += my - ly;
            }
        }
        last_mouse_pos = current_mouse_pos;

        // --- Animation Playback Step ---
        if !paused && total_frames > 1 {
            if last_frame_time.elapsed() >= target_frame_duration {
                current_frame = (current_frame + 1) % total_frames;
                last_frame_time = Instant::now();
            }
        }

        // --- Live HUD / Title Bar Pixel Inspection ---
        let active_canvas = &frames[current_frame];
        let mut hovered_color_str = String::new();

        if let Some((mx, my)) = current_mouse_pos {
            let cx = ((mx - pan_x) / zoom).floor() as i32;
            let cy = ((my - pan_y) / zoom).floor() as i32;

            if cx >= 0 && cx < cw as i32 && cy >= 0 && cy < ch as i32 {
                let pixel_idx = cy as usize * cw + cx as usize;
                let pixel = active_canvas.pixmap.pixels()[pixel_idx].demultiply();
                let hex = format!("#{:02X}{:02X}{:02X}", pixel.red(), pixel.green(), pixel.blue());
                hovered_color_str = format!(
                    " | ({}, {}) {} rgba({},{},{},{})",
                    cx,
                    cy,
                    hex,
                    pixel.red(),
                    pixel.green(),
                    pixel.blue(),
                    pixel.alpha()
                );
            }
        }

        let hud_title = if total_frames > 1 {
            let status = if paused { "Paused" } else { "Play" };
            format!(
                "{} | Frame {}/{} [{}] | {:.0}%{}",
                base_title,
                current_frame + 1,
                total_frames,
                status,
                zoom * 100.0,
                hovered_color_str
            )
        } else {
            format!(
                "{} | {}x{} | {:.0}%{}",
                base_title,
                cw,
                ch,
                zoom * 100.0,
                hovered_color_str
            )
        };
        window.set_title(&hud_title);

        // --- Render Viewport (Parallel row-by-row) ---
        let inv_zoom = 1.0 / zoom;
        let p_pan_x = pan_x;
        let p_pan_y = pan_y;
        let pixels_slice = active_canvas.pixmap.pixels();

        buffer
            .par_chunks_exact_mut(vw)
            .enumerate()
            .for_each(|(vy, row)| {
                let cy_f = (vy as f32 - p_pan_y) * inv_zoom;
                let cy = cy_f.floor() as i32;

                for (vx, pixel_out) in row.iter_mut().enumerate() {
                    let cx_f = (vx as f32 - p_pan_x) * inv_zoom;
                    let cx = cx_f.floor() as i32;

                    if cx >= 0 && cx < cw as i32 && cy >= 0 && cy < ch as i32 {
                        let idx = cy as usize * cw + cx as usize;
                        let pixel = pixels_slice[idx];
                        let demul = pixel.demultiply();
                        let a = demul.alpha() as u32;

                        if a == 255 {
                            *pixel_out = ((demul.red() as u32) << 16)
                                | ((demul.green() as u32) << 8)
                                | (demul.blue() as u32);
                        } else if a == 0 {
                            // High-contrast CAD checkerboard
                            let tile = ((cx / 8) + (cy / 8)) % 2 == 0;
                            *pixel_out = if tile { 0x002c313d } else { 0x001e222b };
                        } else {
                            // Semi-transparent alpha blend over checkerboard
                            let tile = ((cx / 8) + (cy / 8)) % 2 == 0;
                            let bg: u32 = if tile { 0x2c } else { 0x1e };
                            let inv_a = 255 - a;
                            let r = (demul.red() as u32 * a + bg * inv_a) / 255;
                            let g = (demul.green() as u32 * a + bg * inv_a) / 255;
                            let b = (demul.blue() as u32 * a + bg * inv_a) / 255;
                            *pixel_out = (r << 16) | (g << 8) | b;
                        }
                    } else {
                        // Canvas outline border & backdrop
                        let is_border = (cx == -1 || cx == cw as i32)
                            && (cy >= -1 && cy <= ch as i32)
                            || (cy == -1 || cy == ch as i32) && (cx >= -1 && cx <= cw as i32);
                        if is_border {
                            *pixel_out = 0x004a5568; // Clean subtle gray frame border
                        } else {
                            *pixel_out = 0x00111218; // Sleek modern dark backdrop
                        }
                    }
                }
            });

        window
            .update_with_buffer(&buffer, vw, vh)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Window update error: {:?}", e)))?;
    }

    Ok(())
}
