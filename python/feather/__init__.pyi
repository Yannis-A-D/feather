from typing import Any, Tuple, Optional, Sequence, Union
import PIL.Image
import numpy as np

__version__: str

ColorType = Union[str, Tuple[int, int, int], Tuple[int, int, int, int], Tuple[float, float, float], Tuple[float, float, float, float], int]
PaintType = Union[ColorType, LinearGradient, RadialGradient]

class LinearGradient:
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stops: Sequence[Tuple[float, ColorType]],
        spread_mode: str = "pad",
    ) -> None: ...

class RadialGradient:
    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float,
        stops: Sequence[Tuple[float, ColorType]],
        spread_mode: str = "pad",
    ) -> None: ...

class Path:
    def __init__(self) -> None: ...
    def move_to(self, x: float, y: float) -> None: ...
    def line_to(self, x: float, y: float) -> None: ...
    def quad_to(self, cx: float, cy: float, x: float, y: float) -> None: ...
    def cubic_to(self, cx1: float, cy1: float, cx2: float, cy2: float, x: float, y: float) -> None: ...
    def close(self) -> None: ...
    def add_rect(self, x: float, y: float, width: float, height: float) -> None: ...
    def add_circle(self, cx: float, cy: float, radius: float) -> None: ...
    @staticmethod
    def from_svg(svg_d: str) -> Path: ...

class Canvas:
    def __init__(
        self,
        width: int,
        height: int,
        background: Optional[ColorType] = None,
    ) -> None: ...

    @property
    def width(self) -> int: ...

    @property
    def height(self) -> int: ...

    @property
    def size(self) -> Tuple[int, int]: ...

    def fill(self, color: ColorType) -> None: ...
    def clear(self) -> None: ...

    def draw_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_rounded_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rx: float,
        ry: Optional[float] = None,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_circle(
        self,
        cx: float,
        cy: float,
        radius: float,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_ellipse(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: PaintType,
        stroke_width: float = 1.0,
        line_cap: str = "round",
    ) -> None: ...

    def draw_polyline(
        self,
        points: Sequence[Tuple[float, float]],
        stroke: PaintType,
        stroke_width: float = 1.0,
        closed: bool = False,
        line_cap: str = "round",
        line_join: str = "round",
    ) -> None: ...

    def draw_polygon(
        self,
        points: Sequence[Tuple[float, float]],
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_path(
        self,
        path: Path,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_svg_path(
        self,
        svg_d: str,
        fill: Optional[PaintType] = None,
        stroke: Optional[PaintType] = None,
        stroke_width: float = 1.0,
    ) -> None: ...

    def draw_image(
        self,
        other: Canvas,
        x: float,
        y: float,
        opacity: float = 1.0,
        blend_mode: str = "source_over",
    ) -> None: ...

    def resize(self, dst_width: int, dst_height: int, filter: str = "bilinear") -> Canvas: ...
    def blur(self, sigma: float) -> Canvas: ...
    def adjust_brightness(self, factor: float) -> Canvas: ...
    def adjust_contrast(self, factor: float) -> Canvas: ...
    def invert(self) -> Canvas: ...
    def grayscale(self) -> Canvas: ...

    def to_bytes(self) -> bytes: ...
    @staticmethod
    def from_bytes(width: int, height: int, data: bytes) -> Canvas: ...
    @staticmethod
    def open(path: str) -> Canvas: ...
    def save(self, path: str, quality: Optional[int] = None) -> None: ...
    def clone_canvas(self) -> Canvas: ...

    def to_pillow(self) -> PIL.Image.Image: ...
    @classmethod
    def from_pillow(cls, pil_image: PIL.Image.Image) -> Canvas: ...
    def to_numpy(self) -> np.ndarray: ...
    @classmethod
    def from_numpy(cls, array: np.ndarray) -> Canvas: ...

def batch_resize(
    images: Sequence[Canvas],
    dst_width: int,
    dst_height: int,
    filter: str = "bilinear",
) -> Sequence[Canvas]: ...

def batch_blur(
    images: Sequence[Canvas],
    sigma: float,
) -> Sequence[Canvas]: ...

def version() -> str: ...
