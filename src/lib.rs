mod batch;
mod canvas;
mod color;
mod filters;
mod gradient;
mod path;
mod transform;

use pyo3::prelude::*;

#[pyfunction]
fn version() -> &'static str {
    "0.1.0"
}

#[pymodule]
fn _pixelforge(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(batch::batch_resize, m)?)?;
    m.add_function(wrap_pyfunction!(batch::batch_blur, m)?)?;
    m.add_class::<canvas::Canvas>()?;
    m.add_class::<path::Path>()?;
    m.add_class::<gradient::LinearGradient>()?;
    m.add_class::<gradient::RadialGradient>()?;
    Ok(())
}
