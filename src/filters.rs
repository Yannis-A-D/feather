use rayon::prelude::*;

pub fn adjust_brightness_inplace(pixels: &mut [u8], factor: f32) {
    pixels.par_chunks_exact_mut(4).for_each(|chunk| {
        for c in 0..3 {
            let val = chunk[c] as f32 * factor;
            chunk[c] = val.clamp(0.0, 255.0) as u8;
        }
    });
}

pub fn adjust_contrast_inplace(pixels: &mut [u8], factor: f32) {
    pixels.par_chunks_exact_mut(4).for_each(|chunk| {
        for c in 0..3 {
            let val = (chunk[c] as f32 - 128.0) * factor + 128.0;
            chunk[c] = val.clamp(0.0, 255.0) as u8;
        }
    });
}

pub fn invert_inplace(pixels: &mut [u8]) {
    pixels.par_chunks_exact_mut(4).for_each(|chunk| {
        chunk[0] = 255 - chunk[0];
        chunk[1] = 255 - chunk[1];
        chunk[2] = 255 - chunk[2];
    });
}

pub fn grayscale_inplace(pixels: &mut [u8]) {
    pixels.par_chunks_exact_mut(4).for_each(|chunk| {
        let lum = (0.299 * chunk[0] as f32 + 0.587 * chunk[1] as f32 + 0.114 * chunk[2] as f32)
            .round()
            .clamp(0.0, 255.0) as u8;
        chunk[0] = lum;
        chunk[1] = lum;
        chunk[2] = lum;
    });
}

/// Fast separable Gaussian Blur using Rayon multi-threading across image rows & columns
pub fn fast_gaussian_blur(
    src: &[u8],
    width: u32,
    height: u32,
    sigma: f32,
) -> Vec<u8> {
    if sigma <= 0.0 || width == 0 || height == 0 {
        return src.to_vec();
    }

    let radius = (sigma * 3.0).ceil() as i32;
    let size = (radius * 2 + 1) as usize;
    let mut kernel = vec![0.0f32; size];
    let two_sigma_sq = 2.0 * sigma * sigma;
    let mut sum = 0.0f32;

    for i in 0..size {
        let x = (i as i32 - radius) as f32;
        let val = (-x * x / two_sigma_sq).exp();
        kernel[i] = val;
        sum += val;
    }
    for val in &mut kernel {
        *val /= sum;
    }

    let w = width as usize;
    let h = height as usize;
    let mut temp = vec![0u8; w * h * 4];

    // Horizontal blur pass (parallel over rows)
    temp.par_chunks_exact_mut(w * 4)
        .enumerate()
        .for_each(|(y, out_row)| {
            let in_row = &src[y * w * 4..(y + 1) * w * 4];
            for x in 0..w {
                let mut r = 0.0f32;
                let mut g = 0.0f32;
                let mut b = 0.0f32;
                let mut a = 0.0f32;

                for k in 0..size {
                    let kx = (x as i32 + k as i32 - radius).clamp(0, (w - 1) as i32) as usize;
                    let weight = kernel[k];
                    let px = kx * 4;
                    r += in_row[px] as f32 * weight;
                    g += in_row[px + 1] as f32 * weight;
                    b += in_row[px + 2] as f32 * weight;
                    a += in_row[px + 3] as f32 * weight;
                }

                let out_idx = x * 4;
                out_row[out_idx] = r.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 1] = g.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 2] = b.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 3] = a.round().clamp(0.0, 255.0) as u8;
            }
        });

    let mut dst = vec![0u8; w * h * 4];

    // Vertical blur pass (parallel over columns or tile rows)
    dst.par_chunks_exact_mut(w * 4)
        .enumerate()
        .for_each(|(y, out_row)| {
            for x in 0..w {
                let mut r = 0.0f32;
                let mut g = 0.0f32;
                let mut b = 0.0f32;
                let mut a = 0.0f32;

                for k in 0..size {
                    let ky = (y as i32 + k as i32 - radius).clamp(0, (h - 1) as i32) as usize;
                    let weight = kernel[k];
                    let px = (ky * w + x) * 4;
                    r += temp[px] as f32 * weight;
                    g += temp[px + 1] as f32 * weight;
                    b += temp[px + 2] as f32 * weight;
                    a += temp[px + 3] as f32 * weight;
                }

                let out_idx = x * 4;
                out_row[out_idx] = r.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 1] = g.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 2] = b.round().clamp(0.0, 255.0) as u8;
                out_row[out_idx + 3] = a.round().clamp(0.0, 255.0) as u8;
            }
        });

    dst
}
