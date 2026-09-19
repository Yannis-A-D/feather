use crate::canvas::Canvas;
use crate::filters;
use crate::transform;
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
#[pyo3(signature = (images, dst_width, dst_height, filter="bilinear"))]
pub fn batch_resize(
    py: Python<'_>,
    images: Vec<Canvas>,
    dst_width: u32,
    dst_height: u32,
    filter: &str,
) -> PyResult<Vec<Canvas>> {
    let ftype = transform::parse_filter_type(filter)?;

    py.allow_threads(|| {
        images
            .into_par_iter()
            .map(|canvas| {
                let resized = transform::resize_rgba(
                    canvas.pixmap.data(),
                    canvas.pixmap.width(),
                    canvas.pixmap.height(),
                    dst_width,
                    dst_height,
                    ftype,
                )?;
                let mut out = Canvas::new(dst_width, dst_height, None)?;
                out.pixmap.data_mut().copy_from_slice(&resized);
                Ok(out)
            })
            .collect()
    })
}

#[pyfunction]
pub fn batch_blur(
    py: Python<'_>,
    images: Vec<Canvas>,
    sigma: f32,
) -> PyResult<Vec<Canvas>> {
    py.allow_threads(|| {
        images
            .into_par_iter()
            .map(|canvas| {
                let blurred = filters::fast_gaussian_blur(
                    canvas.pixmap.data(),
                    canvas.pixmap.width(),
                    canvas.pixmap.height(),
                    sigma,
                );
                let mut out = Canvas::new(canvas.pixmap.width(), canvas.pixmap.height(), None)?;
                out.pixmap.data_mut().copy_from_slice(&blurred);
                Ok(out)
            })
            .collect()
    })
}
