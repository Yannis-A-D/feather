"""
Animation and easing transition engine for Feather Charts.
Generates smooth 60 FPS entrance and data animations exported directly to
Animated WebP, APNG, or GIF.
"""

from __future__ import annotations
import copy
import math
import os
from typing import Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from feather import Canvas


# --- Mathematical Easing Curves ---

def linear(t: float) -> float:
    return max(0.0, min(1.0, t))


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3.0)


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0


def ease_out_bounce(t: float) -> float:
    t = max(0.0, min(1.0, t))
    n1 = 7.5625
    d1 = 2.75

    if t < 1.0 / d1:
        return n1 * t * t
    elif t < 2.0 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_out_elastic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t == 0.0 or t == 1.0:
        return t
    p = 0.3
    s = p / 4.0
    return math.pow(2.0, -10.0 * t) * math.sin((t - s) * (2.0 * math.pi) / p) + 1.0


EASING_MAP = {
    "linear": linear,
    "cubic_out": ease_out_cubic,
    "ease_out_cubic": ease_out_cubic,
    "cubic_in_out": ease_in_out_cubic,
    "bounce_out": ease_out_bounce,
    "ease_out_bounce": ease_out_bounce,
    "elastic_out": ease_out_elastic,
    "ease_out_elastic": ease_out_elastic,
}


def resolve_easing(easing: str | Callable[[float], float]) -> Callable[[float], float]:
    if callable(easing):
        return easing
    return EASING_MAP.get(str(easing).lower(), ease_out_cubic)


class AnimatableChartMixin:
    """Mixin class providing .render_frames() and .render_animation() to all charts."""

    def render_frames(
        self,
        duration_seconds: float = 1.5,
        fps: int = 30,
        easing: str | Callable[[float], float] = "cubic_out",
        end_pause_seconds: float = 0.5,
    ) -> List[Canvas]:
        """
        Generate a list of Canvas frames showing a smooth animated entrance of this chart.
        """
        ease_fn = resolve_easing(easing)
        total_anim_frames = max(2, int(duration_seconds * fps))
        pause_frames = max(0, int(end_pause_seconds * fps))

        frames: List[Canvas] = []

        # Polymorphic frame generation based on chart type
        chart_type = self.__class__.__name__

        for i in range(total_anim_frames):
            progress = i / max(1, total_anim_frames - 1)
            eased_val = ease_fn(progress)

            frame = self._render_at_progress(eased_val, chart_type)
            frames.append(frame)

        # Hold the final completed frame for the pause duration
        if frames and pause_frames > 0:
            final_frame = frames[-1]
            for _ in range(pause_frames):
                frames.append(final_frame)

        return frames

    def _render_at_progress(self, progress: float, chart_type: str) -> Canvas:
        """Interpolate chart data and render at normalized progress [0.0, 1.0]."""
        # Shallow copy or clone chart to preserve original data
        clone = copy.copy(self)

        if chart_type in ("BarChart", "AreaChart", "LineChart", "RadarChart"):
            # Deepcopy series values
            clone.series = []
            for s in self.series:
                s_copy = dict(s)
                s_copy["values"] = [v * progress for v in s["values"]]
                clone.series.append(s_copy)

            if chart_type == "BarChart" and progress < 0.2:
                clone.show_values = False

            return clone.render()

        elif chart_type in ("DonutChart", "PieChart"):
            clone.slices = []
            for s in self.slices:
                s_copy = dict(s)
                s_copy["value"] = s["value"] * progress
                clone.slices.append(s_copy)
            return clone.render()

        elif chart_type == "Gauge":
            target_val = self.value
            clone.value = self.min_value + (target_val - self.min_value) * progress
            return clone.render()

        # Fallback to standard render
        return self.render()

    def render_animation(
        self,
        output_path: str,
        duration_seconds: float = 1.5,
        fps: int = 30,
        easing: str | Callable[[float], float] = "cubic_out",
        loop_count: int = 0,
        quality: float = 85.0,
        end_pause_seconds: float = 0.5,
    ) -> None:
        """
        Render the chart animation and save directly to Animated WebP, APNG, or GIF.
        """
        import feather

        frames = self.render_frames(
            duration_seconds=duration_seconds,
            fps=fps,
            easing=easing,
            end_pause_seconds=end_pause_seconds,
        )

        ext = os.path.splitext(output_path)[1].lower()

        if ext == ".webp":
            feather.save_webp(frames, output_path, fps=fps, loop_count=loop_count, quality=quality)
        elif ext == ".apng":
            feather.save_apng(frames, output_path, fps=fps, loop_count=loop_count)
        elif ext == ".gif":
            feather.save_gif(frames, output_path, fps=fps, loop_count=loop_count)
        else:
            feather.save_animation(frames, output_path, fps=fps, loop_count=loop_count, quality=quality)
