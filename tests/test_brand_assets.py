"""Prevent reintroducing upstream screenshots/branding into 2.3 documentation."""
import pathlib
import re
import struct
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BrandingSmoke(unittest.TestCase):
    def test_dashboard_uses_new_wordmark_in_both_states(self):
        dashboard = (ROOT / "skills/autopilot/phases/dashboard-template.html").read_text(encoding="utf-8")
        self.assertNotIn("const LOGO =", dashboard)
        self.assertNotIn('class="logo"', dashboard)
        self.assertEqual(dashboard.count('<div class="brand"'), 2)
        self.assertIn('class="brand-version">2.3 DEV', dashboard)

    def test_readmes_have_only_actual_current_screenshots(self):
        for name in ("README.md", "README.ru.md"):
            with self.subTest(readme=name):
                markdown = (ROOT / name).read_text(encoding="utf-8")
                self.assertNotIn("autopilot-logo", markdown)
                self.assertIn("dashboard-3-models.png", markdown)
                refs = re.findall(r'(?:href|src)="(assets/[^"]+)"', markdown)
                self.assertGreaterEqual(len(refs), 6)
                for path in refs:
                    self.assertTrue((ROOT / path).is_file(), path)

    def test_visual_captures_are_valid_pngs(self):
        for folder in ("assets", "assets/ru"):
            for image in ("desktop", "narrow", "models"):
                with self.subTest(folder=folder, image=image):
                    path = ROOT / folder / ("dashboard-3-" + image + ".png")
                    raw = path.read_bytes()
                    self.assertGreater(len(raw), 30000)
                    self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
                    width, height = struct.unpack(">II", raw[16:24])
                    self.assertGreaterEqual(width, 450)
                    self.assertGreaterEqual(height, 900)


if __name__ == "__main__":
    unittest.main()
