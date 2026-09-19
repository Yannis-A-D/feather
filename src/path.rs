use pyo3::prelude::*;
use tiny_skia::{Path as SkiaPath, PathBuilder, Rect};

#[pyclass]
#[derive(Clone)]
pub struct Path {
    pub(crate) builder: Option<PathBuilder>,
    pub(crate) finished: Option<SkiaPath>,
}

#[pymethods]
impl Path {
    #[new]
    pub fn new() -> Self {
        Self {
            builder: Some(PathBuilder::new()),
            finished: None,
        }
    }

    pub fn move_to(&mut self, x: f32, y: f32) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.move_to(x, y);
        Ok(())
    }

    pub fn line_to(&mut self, x: f32, y: f32) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.line_to(x, y);
        Ok(())
    }

    pub fn quad_to(&mut self, cx: f32, cy: f32, x: f32, y: f32) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.quad_to(cx, cy, x, y);
        Ok(())
    }

    pub fn cubic_to(
        &mut self,
        cx1: f32,
        cy1: f32,
        cx2: f32,
        cy2: f32,
        x: f32,
        y: f32,
    ) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.cubic_to(cx1, cy1, cx2, cy2, x, y);
        Ok(())
    }

    pub fn close(&mut self) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.close();
        Ok(())
    }

    pub fn add_rect(&mut self, x: f32, y: f32, width: f32, height: f32) -> PyResult<()> {
        let builder = self.get_builder()?;
        if let Some(rect) = Rect::from_xywh(x, y, width, height) {
            builder.push_rect(rect);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid rectangle dimensions",
            ))
        }
    }

    pub fn add_circle(&mut self, cx: f32, cy: f32, radius: f32) -> PyResult<()> {
        let builder = self.get_builder()?;
        builder.push_circle(cx, cy, radius);
        Ok(())
    }

    #[staticmethod]
    pub fn from_svg(svg_d: &str) -> PyResult<Self> {
        let mut builder = PathBuilder::new();

        for segment in svgtypes::SimplifyingPathParser::from(svg_d) {
            let seg = segment.map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(format!("Invalid SVG path: {}", e))
            })?;
            match seg {
                svgtypes::SimplePathSegment::MoveTo { x, y } => {
                    builder.move_to(x as f32, y as f32);
                }
                svgtypes::SimplePathSegment::LineTo { x, y } => {
                    builder.line_to(x as f32, y as f32);
                }
                svgtypes::SimplePathSegment::Quadratic { x1, y1, x, y } => {
                    builder.quad_to(x1 as f32, y1 as f32, x as f32, y as f32);
                }
                svgtypes::SimplePathSegment::CurveTo {
                    x1,
                    y1,
                    x2,
                    y2,
                    x,
                    y,
                } => {
                    builder.cubic_to(
                        x1 as f32, y1 as f32, x2 as f32, y2 as f32, x as f32, y as f32,
                    );
                }
                svgtypes::SimplePathSegment::ClosePath => {
                    builder.close();
                }
            }
        }

        let skia_path = builder
            .finish()
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Failed to build SVG path"))?;
        Ok(Self {
            builder: None,
            finished: Some(skia_path),
        })
    }
}

impl Path {
    fn get_builder(&mut self) -> PyResult<&mut PathBuilder> {
        if self.builder.is_none() {
            if let Some(finished) = self.finished.take() {
                let mut b = PathBuilder::new();
                for seg in finished.segments() {
                    match seg {
                        tiny_skia::PathSegment::MoveTo(p) => b.move_to(p.x, p.y),
                        tiny_skia::PathSegment::LineTo(p) => b.line_to(p.x, p.y),
                        tiny_skia::PathSegment::QuadTo(p0, p1) => b.quad_to(p0.x, p0.y, p1.x, p1.y),
                        tiny_skia::PathSegment::CubicTo(p0, p1, p2) => {
                            b.cubic_to(p0.x, p0.y, p1.x, p1.y, p2.x, p2.y)
                        }
                        tiny_skia::PathSegment::Close => b.close(),
                    }
                }
                self.builder = Some(b);
            } else {
                self.builder = Some(PathBuilder::new());
            }
        }
        Ok(self.builder.as_mut().unwrap())
    }

    pub fn get_skia_path(&mut self) -> Option<SkiaPath> {
        if let Some(finished) = &self.finished {
            return Some(finished.clone());
        }
        if let Some(builder) = self.builder.take() {
            let path = builder.finish();
            self.finished = path.clone();
            return path;
        }
        None
    }
}
