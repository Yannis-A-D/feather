"""
Unit and integration tests for feather.charts.
"""

import os
import pytest
import feather
from feather import charts


def test_area_chart():
    chart = charts.AreaChart(width=600, height=300, title="Test Area", theme="dark", smooth=True)
    chart.set_x_labels(["A", "B", "C", "D", "E"])
    chart.add_series("Series 1", [10, 25, 40, 15, 30])
    canvas = chart.render()
    assert isinstance(canvas, feather.Canvas)
    assert canvas.width == 600
    assert canvas.height == 300


def test_bar_chart():
    chart = charts.BarChart(width=500, height=350, title="Test Bar", theme="light")
    chart.set_categories(["Q1", "Q2", "Q3", "Q4"])
    chart.add_series("Revenue", [100, 200, 150, 300])
    canvas = chart.render()
    assert isinstance(canvas, feather.Canvas)
    assert canvas.width == 500
    assert canvas.height == 350


def test_donut_chart():
    chart = charts.DonutChart(width=400, height=400, title="Test Donut", cutout_ratio=0.5)
    chart.add_slice("Slice A", 40)
    chart.add_slice("Slice B", 60)
    canvas = chart.render()
    assert isinstance(canvas, feather.Canvas)
    assert canvas.width == 400
    assert canvas.height == 400


def test_radar_chart():
    chart = charts.RadarChart(width=450, height=450, title="Test Radar")
    chart.set_axes(["Speed", "Power", "Agility", "Stamina", "Defense"])
    chart.add_series("Player 1", [80, 90, 70, 85, 60])
    canvas = chart.render()
    assert isinstance(canvas, feather.Canvas)
    assert canvas.width == 450
    assert canvas.height == 450


def test_gauge():
    gauge = charts.Gauge(value=75.5, min_value=0, max_value=100, title="CPU Load")
    canvas = gauge.render()
    assert isinstance(canvas, feather.Canvas)
    assert canvas.width == 400
    assert canvas.height == 340


def test_jupyter_repr_png():
    canvas = feather.Canvas(100, 100, background="#ffffff")
    png_bytes = canvas._repr_png_()
    assert isinstance(png_bytes, bytes)
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    test_area_chart()
    test_bar_chart()
    test_donut_chart()
    test_radar_chart()
    test_gauge()
    test_jupyter_repr_png()
    print("All feather.charts tests passed successfully!")
