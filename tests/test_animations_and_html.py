"""
Automated test suite for Feather v0.4.4:
- Feature 4: Standalone Interactive HTML Export (canvas.to_html / canvas.save_html)
- Feature 2: Animated Chart Transitions (render_frames / render_animation)
"""

import os
import unittest
import feather
from feather.charts import BarChart, AreaChart, DonutChart, RadarChart, Gauge


class TestHtmlAndAnimations(unittest.TestCase):
    def setUp(self):
        self.tmp_files = []

    def tearDown(self):
        for f in self.tmp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def test_canvas_to_html_and_save_html(self):
        # 1. Create a canvas with vector shapes
        canvas = feather.Canvas(400, 300, background="#111827")
        canvas.draw_rect(50, 50, 100, 100, fill="#38bdf8")
        canvas.draw_text("Feather HTML Test", 50, 180, size=16, color="#f8fafc")

        # 2. Test to_html string generation
        html_str = canvas.to_html(title="Interactive Test")
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("<title>Interactive Test</title>", html_str)
        self.assertIn("data:image/png;base64,", html_str)
        self.assertIn("canvas-img", html_str)
        self.assertIn("coords-label", html_str)

        # 3. Test canvas.save_html
        html_file = "test_export.html"
        self.tmp_files.append(html_file)
        canvas.save_html(html_file, title="Saved Interactive Test")
        self.assertTrue(os.path.exists(html_file))
        self.assertGreater(os.path.getsize(html_file), 1000)

        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Saved Interactive Test", content)

        # 4. Test top-level feather.save_html and feather.to_html
        top_str = feather.to_html(canvas, title="Top-level Test")
        self.assertIn("Top-level Test", top_str)

        top_file = "test_top_export.html"
        self.tmp_files.append(top_file)
        feather.save_html(canvas, top_file, title="Top-level Saved")
        self.assertTrue(os.path.exists(top_file))
        self.assertGreater(os.path.getsize(top_file), 1000)

    def test_bar_chart_animation(self):
        chart = BarChart(width=400, height=300, title="Animated Bar Chart")
        chart.set_categories(["Q1", "Q2", "Q3", "Q4"])
        chart.add_series("Revenue", [120, 240, 310, 480], color="#6366f1")

        # Test frame rendering
        frames = chart.render_frames(duration_seconds=0.5, fps=20, easing="cubic_out")
        self.assertEqual(len(frames), 20)  # 0.5s * 20 fps = 10 frames + 0.5s pause * 20 = 10 frames = 20
        self.assertIsInstance(frames[0], feather.Canvas)

        # Test WebP export
        webp_path = "test_bar.webp"
        self.tmp_files.append(webp_path)
        chart.render_animation(webp_path, duration_seconds=0.5, fps=20, easing="bounce_out")
        self.assertTrue(os.path.exists(webp_path))
        self.assertGreater(os.path.getsize(webp_path), 500)

    def test_area_chart_animation(self):
        chart = AreaChart(width=400, height=300, title="Animated Area")
        chart.set_x_labels(["Jan", "Feb", "Mar", "Apr"])
        chart.add_series("Active Users", [100, 250, 400, 600], color="#10b981")

        gif_path = "test_area.gif"
        self.tmp_files.append(gif_path)
        chart.render_animation(gif_path, duration_seconds=0.4, fps=15, easing="cubic_in_out")
        self.assertTrue(os.path.exists(gif_path))
        self.assertGreater(os.path.getsize(gif_path), 500)

    def test_donut_chart_animation(self):
        chart = DonutChart(width=350, height=300, title="Animated Donut")
        chart.add_slice("Rust", 65, color="#f97316")
        chart.add_slice("Python", 35, color="#3b82f6")

        webp_path = "test_donut.webp"
        self.tmp_files.append(webp_path)
        chart.render_animation(webp_path, duration_seconds=0.4, fps=15, easing="elastic_out")
        self.assertTrue(os.path.exists(webp_path))
        self.assertGreater(os.path.getsize(webp_path), 500)

    def test_radar_chart_animation(self):
        chart = RadarChart(width=350, height=300, title="Animated Radar")
        chart.set_axes(["Speed", "Memory", "Aesthetics", "Ease"])
        chart.add_series("Feather", [98, 95, 92, 90], color="#a855f7")

        apng_path = "test_radar.apng"
        self.tmp_files.append(apng_path)
        chart.render_animation(apng_path, duration_seconds=0.4, fps=15, easing="cubic_out")
        self.assertTrue(os.path.exists(apng_path))
        self.assertGreater(os.path.getsize(apng_path), 500)

    def test_gauge_animation(self):
        gauge = Gauge(value=88.5, max_value=100.0, title="Engine Power", unit="%")

        webp_path = "test_gauge.webp"
        self.tmp_files.append(webp_path)
        gauge.render_animation(webp_path, duration_seconds=0.4, fps=15, easing="bounce_out")
        self.assertTrue(os.path.exists(webp_path))
        self.assertGreater(os.path.getsize(webp_path), 500)


if __name__ == "__main__":
    unittest.main()
