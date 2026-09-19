"""
Feather: High-performance, anti-aliased 2D vector graphics & image processing.
Powered by Rust, tiny-skia, and fast_image_resize.
"""

from __future__ import annotations
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
    LinearGradient,
    RadialGradient,
    batch_resize,
    batch_blur,
    version,
)

__version__ = version()


class Canvas(_NativeCanvas):
    """
    A 2D drawing canvas backed by a high-performance, SIMD-accelerated
    premultiplied RGBA pixel buffer with full subpixel anti-aliasing.
    """

    def __repr__(self) -> str:
        return f"<Feather.Canvas size={self.width}x{self.height}>"

    def to_pillow(self):
        """
        Convert this canvas to a PIL / Pillow Image instance.
        """
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
        """
        Create a Canvas from an existing PIL / Pillow Image.
        """
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")
        raw_bytes = pil_image.tobytes()
        w, h = pil_image.size
        return cls.from_bytes(w, h, raw_bytes)

    def to_numpy(self):
        """
        Convert this canvas to a NumPy uint8 RGBA array of shape (height, width, 4).
        """
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
        """
        Create a Canvas from a NumPy array of shape (height, width, 4) or (height, width, 3).
        """
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
            # Convert RGB to RGBA
            alpha = np.full((h, w, 1), 255, dtype=np.uint8)
            array = np.concatenate([array, alpha], axis=-1)
        elif c != 4:
            raise ValueError(f"Expected 3 (RGB) or 4 (RGBA) channels, got {c}")

        if not array.flags["C_CONTIGUOUS"]:
            array = np.ascontiguousarray(array)

        return cls.from_bytes(w, h, array.tobytes())


__all__ = [
    "Canvas",
    "Path",
    "LinearGradient",
    "RadialGradient",
    "batch_resize",
    "batch_blur",
    "version",
    "__version__",
]
