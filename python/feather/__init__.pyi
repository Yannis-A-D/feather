from typing import Any, Tuple, Optional, Sequence, Union, ContextManager
import PIL.Image
import numpy as np

__version__: str

ColorType = Union[str, Tuple[int, int, int], Tuple[int, int, int, int], Tuple[float, float, float], Tuple[float, float, float, float], int]
PaintType = Union[ColorType, LinearGradient, RadialGradient]

class Font:
    def __init__(self, data: bytes) -> None: ...
    @staticmethod
    def load(path: str) -> Font: ...
    @staticmethod
    def default_font() -> Font: ...

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

    # Transformations & State
    def save_state(self) -> None: ...
    def restore_state(self) -> None: ...
    def translate(self, tx: float, ty: float) -> None: ...
    def rotate(self, degrees: float) -> None: ...
    def scale(self, sx: float, sy: float) -> None: ...
    def reset_transform(self) -> None: ...
    def transform_scope(self) -> ContextManager[Canvas]: ...

    # Clipping Masks
    def clip_path(self, path: Path) -> None: ...
    def clip_rect(self, x: float, y: float, width: float, height: float) -> None: ...
    def clip_circle(self, cx: float, cy: float, radius: float) -> None: ...
    def clip_rounded_rect(self, x: float, y: float, width: float, height: float, rx: float, ry: Optional[float] = None) -> None: ...
    def reset_clip(self) -> None: ...
    def clipping_rect(self, x: float, y: float, width: float, height: float) -> ContextManager[Canvas]: ...
    def clipping_rounded_rect(self, x: float, y: float, width: float, height: float, rx: float, ry: Optional[float] = None) -> ContextManager[Canvas]: ...
    def clipping_circle(self, cx: float, cy: float, radius: float) -> ContextManager[Canvas]: ...

    # Drop Shadows & Glows
    def draw_drop_shadow(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rx: float = 0.0,
        ry: Optional[float] = None,
        blur: float = 10.0,
        offset_x: float = 0.0,
        offset_y: float = 4.0,
        color: Optional[ColorType] = None,
    ) -> None: ...

    def draw_glow(
        self,
        cx: float,
        cy: float,
        radius: float,
        blur: float = 15.0,
        color: Optional[ColorType] = None,
    ) -> None: ...

    # Modern Typography
    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        size: float = 16.0,
        color: Optional[ColorType] = None,
        font: Optional[Font] = None,
    ) -> None: ...

    def draw_text_box(
        self,
        text: str,
        x: float,
        y: float,
        max_width: float,
        size: float = 16.0,
        color: Optional[ColorType] = None,
        line_spacing: float = 4.0,
        font: Optional[Font] = None,
    ) -> Tuple[float, float]: ...

    def measure_text(
        self,
        text: str,
        size: float = 16.0,
        font: Optional[Font] = None,
    ) -> Tuple[float, float]: ...

    # SVG Rendering
    def draw_svg_document(
        self,
        svg_content: str,
        x: float = 0.0,
        y: float = 0.0,
        width: Optional[f32] = None,
        height: Optional[f32] = None,
    ) -> None: ...

    def draw_svg_file(
        self,
        path: str,
        x: float = 0.0,
        y: float = 0.0,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None: ...

    # Basic Drawing Primitives
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

def save_gif(
    frames: Sequence[Canvas],
    path: str,
    fps: int = 20,
    loop_count: int = 0,
) -> None: ...

def version() -> str: ...
