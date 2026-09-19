use crate::color::parse_color;
use pyo3::prelude::*;
use pyo3::types::PySequence;
use tiny_skia::{GradientStop, Point, SpreadMode, Transform};

fn parse_spread_mode(mode_str: &str) -> PyResult<SpreadMode> {
    match mode_str.to_lowercase().as_str() {
        "pad" | "clamp" => Ok(SpreadMode::Pad),
        "repeat" => Ok(SpreadMode::Repeat),
        "reflect" => Ok(SpreadMode::Reflect),
        _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown spread mode '{}', valid are 'pad', 'repeat', 'reflect'",
            mode_str
        ))),
    }
}

fn parse_stops(stops_obj: &Bound<'_, PyAny>) -> PyResult<Vec<GradientStop>> {
    let seq = stops_obj.downcast::<PySequence>()?;
    let mut stops = Vec::new();
    for i in 0..seq.len()? {
        let item = seq.get_item(i)?;
        let tuple = item.downcast::<PySequence>()?;
        if tuple.len()? != 2 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Each gradient stop must be a tuple: (offset: float, color)",
            ));
        }
        let pos: f32 = tuple.get_item(0)?.extract()?;
        let color = parse_color(&tuple.get_item(1)?)?;
        stops.push(GradientStop::new(pos.clamp(0.0, 1.0), color));
    }
    if stops.len() < 2 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Gradient must have at least 2 color stops",
        ));
    }
    Ok(stops)
}

#[pyclass]
#[derive(Clone)]
pub struct LinearGradient {
    pub(crate) x1: f32,
    pub(crate) y1: f32,
    pub(crate) x2: f32,
    pub(crate) y2: f32,
    pub(crate) stops: Vec<GradientStop>,
    pub(crate) spread_mode: SpreadMode,
}

#[pymethods]
impl LinearGradient {
    #[new]
    #[pyo3(signature = (x1, y1, x2, y2, stops, spread_mode="pad"))]
    pub fn new(
        x1: f32,
        y1: f32,
        x2: f32,
        y2: f32,
        stops: &Bound<'_, PyAny>,
        spread_mode: &str,
    ) -> PyResult<Self> {
        let parsed_stops = parse_stops(stops)?;
        let mode = parse_spread_mode(spread_mode)?;
        Ok(Self {
            x1,
            y1,
            x2,
            y2,
            stops: parsed_stops,
            spread_mode: mode,
        })
    }
}

impl LinearGradient {
    pub fn to_shader<'a>(&'a self) -> Option<tiny_skia::Shader<'a>> {
        tiny_skia::LinearGradient::new(
            Point::from_xy(self.x1, self.y1),
            Point::from_xy(self.x2, self.y2),
            self.stops.clone(),
            self.spread_mode,
            Transform::identity(),
        )
    }
}

#[pyclass]
#[derive(Clone)]
pub struct RadialGradient {
    pub(crate) cx: f32,
    pub(crate) cy: f32,
    pub(crate) radius: f32,
    pub(crate) stops: Vec<GradientStop>,
    pub(crate) spread_mode: SpreadMode,
}

#[pymethods]
impl RadialGradient {
    #[new]
    #[pyo3(signature = (cx, cy, radius, stops, spread_mode="pad"))]
    pub fn new(
        cx: f32,
        cy: f32,
        radius: f32,
        stops: &Bound<'_, PyAny>,
        spread_mode: &str,
    ) -> PyResult<Self> {
        if radius <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Radial gradient radius must be positive",
            ));
        }
        let parsed_stops = parse_stops(stops)?;
        let mode = parse_spread_mode(spread_mode)?;
        Ok(Self {
            cx,
            cy,
            radius,
            stops: parsed_stops,
            spread_mode: mode,
        })
    }
}

impl RadialGradient {
    pub fn to_shader<'a>(&'a self) -> Option<tiny_skia::Shader<'a>> {
        tiny_skia::RadialGradient::new(
            Point::from_xy(self.cx, self.cy),
            Point::from_xy(self.cx, self.cy),
            self.radius,
            self.stops.clone(),
            self.spread_mode,
            Transform::identity(),
        )
    }
}
