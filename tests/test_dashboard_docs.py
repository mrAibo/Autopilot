"""Docs of the dashboard designs match the template (R29d, R32, R32a)."""
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "skills/autopilot/phases/dashboard-template.html"
DOC = ROOT / "docs/autopilot/dashboard-views.md"
README = ROOT / "mockups/dashboard-2026/README.md"


def _designs():
    """[(id, no, accent, scheme)] as the template declares them, whatever their number."""
    block = TEMPLATE.read_text(encoding="utf-8").split("const DESIGNS = [", 1)[1].split("\n];", 1)[0]
    return re.findall(r"\{id:'(\w+)', no:'(\d+)'.*?accent:'(#\w+)', scheme:'(\w+)'", block, re.S)


class DashboardDocs(unittest.TestCase):
    def setUp(self):
        self.doc = DOC.read_text(encoding="utf-8")

    def test_every_design_has_a_table_row(self):
        designs = _designs()
        self.assertGreaterEqual(len(designs), 6)
        for i, no, accent, scheme in designs:
            self.assertRegex(self.doc, r"\| `%s` \| %s \| `%s` \|[^\n]*\| `%s` \|" % (i, no, scheme, accent))

    def test_sections_present(self):
        for h in ("Registry", "Theme scheme", "Slots", "Single page",
                  "Add a seventh design", "Deviations from the mockups"):
            self.assertRegex(self.doc, r"(?m)^## " + h + r"\s*$")

    def test_seventh_design_step_names_the_selectors_the_tests_look_for(self):
        step = self.doc.split("## Add a seventh design", 1)[1].split("\n## ", 1)[0]
        for selector in ('html[data-design="<id>"][data-theme="<scheme>"][lang]:not([hidden])',
                         'html[data-design="<id>"][lang]:not([hidden]):not([data-theme="none"]){--accent:#rrggbb}'):
            self.assertIn(selector, step)
        self.assertIn("The tests read the registry from the template", step)   # as test_dashboard_designs.registry() does
        self.assertNotIn("`html[data-design=\"<id>\"][lang]:not([hidden])` (and", step)  # the old selector without the scheme

    def test_no_data_view_mechanism(self):
        self.assertNotIn("data-view", self.doc)
        self.assertNotIn("VIEW_IDS", self.doc)

    def test_readme_says_live_data_only_in_template(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("live", text.lower())
        self.assertIn("skills/autopilot/phases/dashboard-template.html", text)

    def test_only_thumbs_tracked_in_shots(self):
        out = subprocess.run(["git", "ls-files", "mockups/dashboard-2026/shots"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        self.assertTrue(out)
        for f in out:
            self.assertRegex(f.rsplit("/", 1)[-1], r"^thumb-0.*\.png$")


if __name__ == "__main__":
    unittest.main()
