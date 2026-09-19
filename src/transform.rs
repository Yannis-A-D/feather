use fast_image_resize::images::{Image, ImageRef};
use fast_image_resize::{FilterType, PixelType, ResizeAlg, ResizeOptions, Resizer};
use pyo3::prelude::*;

pub fn parse_filter_type(filter_str: &str) -> PyResult<FilterType> {
    match filter_str.to_lowercase().as_str() {
        "nearest" | "box" => Ok(FilterType::Box),
        "bilinear" | "linear" | "triangle" => Ok(FilterType::Bilinear),
        "catmull_rom" | "catmullrom" => Ok(FilterType::CatmullRom),
        "bicubic" | "mitchell" => Ok(FilterType::Mitchell),
        "lanczos3" | "lanczos" => Ok(FilterType::Lanczos3),
        "gaussian" => Ok(FilterType::Gaussian),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown resize filter '{}'. Supported: 'nearest', 'bilinear', 'bicubic', 'lanczos3', 'catmull_rom', 'gaussian'",
            filter_str
        ))),
    }
}

pub fn resize_rgba(
    src_data: &[u8],
    src_width: u32,
    src_height: u32,
    dst_width: u32,
    dst_height: u32,
    filter: FilterType,
) -> PyResult<Vec<u8>> {
    if src_width == 0 || src_height == 0 || dst_width == 0 || dst_height == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Image dimensions must be non-zero",
        ));
    }

    let src_ref = ImageRef::new(src_width, src_height, src_data, PixelType::U8x4)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid src image: {}", e)))?;

    let mut dst_image = Image::new(dst_width, dst_height, PixelType::U8x4);
    let mut resizer = Resizer::new();
    let options = ResizeOptions::new().resize_alg(ResizeAlg::Convolution(filter));

    resizer
        .resize(&src_ref, &mut dst_image, &options)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Resize failed: {}", e)))?;

    Ok(dst_image.into_vec())
}
