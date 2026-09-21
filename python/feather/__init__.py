"""
Feather: High-performance, anti-aliased 2D vector graphics & image processing.
Powered by Rust, tiny-skia, fontdue, and resvg.
"""

from __future__ import annotations
import contextlib
import os
import sys

# On Windows, ensure native DLL dependencies in the package directory can be loaded
if sys.platform == "win32":
    _pkg_dir = os.path.dirname(__file__)
    if hasattr(os, "add_dll_directory") and os.path.isdir(_pkg_dir):
        try:
            os.add_dll_directory(_pkg_dir)
        except OSError:
            pass

from ._feather import (
    Canvas as _NativeCanvas,
    Path,
    Font,
    LinearGradient,
    RadialGradient,
    batch_resize,
    batch_blur,
    save_gif,
    save_apng,
    save_webp,
    save_animation,
    show_interactive as _native_show_interactive,
    version,
)

__version__ = version()


def show_interactive(
    frames: Canvas | list[Canvas] | tuple[Canvas, ...],
    title: str = "Feather Viewer",
    window_width: int | None = None,
    window_height: int | None = None,
    fps: int = 30,
) -> None:
    """
    Open a blazing-fast native interactive window to view a Canvas or animated sequence.
    Features:
      - Interactive Pan: Click and drag with left mouse button
      - Infinite Zoom: Scroll wheel centered at cursor
      - Pixel Inspector: Live (X, Y) and RGBA/Hex color HUD on hover
      - Playback Controls: Space to Pause/Play, Left/Right arrow keys to step
      - Reset View: Press 'R' to re-center and fit to window
      - Instant Snapshot: Press 'S' to save current view to PNG
      - Close: Press Esc or Q
    """
    if isinstance(frames, _NativeCanvas):
        frames = [frames]
    _native_show_interactive(list(frames), title, window_width, window_height, fps)


show_window = show_interactive


class Canvas(_NativeCanvas):
    """
    A 2D drawing canvas backed by a high-performance, SIMD-accelerated
    premultiplied RGBA pixel buffer with full subpixel anti-aliasing.
    """

    def __repr__(self) -> str:
        return f"<Feather.Canvas size={self.width}x{self.height}>"

    def _repr_png_(self) -> bytes:
        """IPython / Jupyter Notebook rich display hook. Renders PNG bytes automatically."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name
        try:
            self.save(temp_path)
            with open(temp_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def draw_markdown(
        self,
        text: str,
        x: float,
        y: float,
        max_width: float | None = None,
        size: float = 16.0,
        default_color: str = "#cdd6f4",
        line_spacing: float = 6.0,
        font: Font | None = None,
    ) -> tuple[float, float]:
        """
        Render inline Markdown text (**bold**, *italic*, `code`, <color=...>)
        with automatic word wrapping and subpixel baseline alignment.
        Returns (consumed_width, consumed_height).
        """
        from .markdown import render_markdown
        return render_markdown(
            self,
            text,
            x,
            y,
            max_width=max_width,
            size=size,
            default_color=default_color,
            line_spacing=line_spacing,
            font=font,
        )

    # --- Pythonic Context Managers for Clipping Masks ---

    @contextlib.contextmanager
    def clipping_rect(self, x: float, y: float, width: float, height: float):
        """Context manager that applies a rectangular clip mask and restores it on exit."""
        self.save_state()
        self.clip_rect(x, y, width, height)
        try:
            yield self
        finally:
            self.restore_state()

    @contextlib.contextmanager
    def clipping_rounded_rect(self, x: float, y: float, width: float, height: float, rx: float, ry: float | None = None):
        """Context manager that applies a rounded rectangular clip mask and restores it on exit."""
        self.save_state()
        self.clip_rounded_rect(x, y, width, height, rx, ry)
        try:
            yield self
        finally:
            self.restore_state()

    @contextlib.contextmanager
    def clipping_circle(self, cx: float, cy: float, radius: float):
        """Context manager that applies a circular clip mask and restores it on exit."""
        self.save_state()
        self.clip_circle(cx, cy, radius)
        try:
            yield self
        finally:
            self.restore_state()

    @contextlib.contextmanager
    def transform_scope(self):
        """Context manager that saves current transform matrix and restores it on exit."""
        self.save_state()
        try:
            yield self
        finally:
            self.restore_state()

    # --- Interoperability ---

    def to_pillow(self):
        """Convert this canvas to a PIL / Pillow Image instance."""
        try:
            from PIL import Image
        except ImportError as err:
            raise ImportError(
                "Pillow is required for to_pillow(). Install via 'pip install pillow'"
            ) from err

        raw_bytes = self.to_bytes()
        return Image.frombytes("RGBA", (self.width, self.height), raw_bytes)

    @classmethod
    def from_pillow(cls, pil_image) -> Canvas:
        """Create a Canvas from an existing PIL / Pillow Image."""
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")
        raw_bytes = pil_image.tobytes()
        w, h = pil_image.size
        return cls.from_bytes(w, h, raw_bytes)

    def to_numpy(self):
        """Convert this canvas to a NumPy uint8 RGBA array of shape (height, width, 4)."""
        try:
            import numpy as np
        except ImportError as err:
            raise ImportError(
                "NumPy is required for to_numpy(). Install via 'pip install numpy'"
            ) from err

        raw_bytes = self.to_bytes()
        return np.frombuffer(raw_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))

    @classmethod
    def from_numpy(cls, array) -> Canvas:
        """Create a Canvas from a NumPy array of shape (H, W, 4) or (H, W, 3)."""
        try:
            import numpy as np
        except ImportError as err:
            raise ImportError(
                "NumPy is required for from_numpy(). Install via 'pip install numpy'"
            ) from err

        if not isinstance(array, np.ndarray):
            raise TypeError("Input must be a numpy.ndarray")

        if array.ndim != 3:
            raise ValueError(f"Expected 3D array (H, W, C), got shape {array.shape}")

        h, w, c = array.shape
        if c == 3:
            alpha = np.full((h, w, 1), 255, dtype=np.uint8)
            array = np.concatenate([array, alpha], axis=-1)
        elif c != 4:
            raise ValueError(f"Expected 3 (RGB) or 4 (RGBA) channels, got {c}")

        if not array.flags["C_CONTIGUOUS"]:
            array = np.ascontiguousarray(array)

        return cls.from_bytes(w, h, array.tobytes())


from . import charts
from . import ui

__all__ = [
    "Canvas",
    "Path",
    "Font",
    "LinearGradient",
    "RadialGradient",
    "batch_resize",
    "batch_blur",
    "save_gif",
    "save_apng",
    "save_webp",
    "save_animation",
    "show_interactive",
    "show_window",
    "charts",
    "ui",
    "version",
    "__version__",
]
