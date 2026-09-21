"""
Feather Charts: Zero-dependency, modern 2D vector charting engine for Python.
"""

from __future__ import annotations
from .theme import (
    Theme,
    THEME_DARK,
    THEME_CYBERPUNK,
    THEME_EMERALD,
    THEME_LIGHT,
    THEMES,
    resolve_theme,
)
from .area_chart import AreaChart, LineChart
from .bar_chart import BarChart
from .donut_chart import DonutChart, PieChart
from .radar_chart import RadarChart
from .gauge import Gauge

__all__ = [
    "Theme",
    "THEME_DARK",
    "THEME_CYBERPUNK",
    "THEME_EMERALD",
    "THEME_LIGHT",
    "THEMES",
    "resolve_theme",
    "AreaChart",
    "LineChart",
    "BarChart",
    "DonutChart",
    "PieChart",
    "RadarChart",
    "Gauge",
]
