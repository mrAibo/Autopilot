"""Updating a copied dashboard must preserve the actual project's run."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills" / "autopilot" / "tools"))
import dashboard_upgrade as upgrade


class DashboardUpgradeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ap = self.root / ".autopilot"
        self.ap.mkdir()
        self.page = self.ap / "dashboard.html"
        self.state = self.ap / "state.js"
        self.template = Path(__file__).resolve().parents[1] / \
            "skills" / "autopilot" / "phases" / "dashboard-template.html"
        self.page.write_text(
            "<html><script>/*STATE-BEGIN*/window.STATE=" +
            json.dumps({"slug": "synthetic", "rev": 1}) +
            ";/*STATE-END*/</script></html>", encoding="utf-8")
        self.state.write_text(
            'window.STATE =\n' + json.dumps(
                {"slug": "synthetic", "rev": 2, "tickets": [{"id": "01"}]}),
            encoding="utf-8")

    def test_upgrades_old_dashboard_preserving_live_run(self):
        before_state = self.state.read_bytes()
        backup_dir = self.root / "backups"
        result = upgrade.upgrade(self.root, self.template, backup_dir)
        self.assertEqual(result["status"], "upgraded")
        self.assertTrue(Path(result["backup"]).is_file())
        self.assertIn('"rev": 1', Path(result["backup"]).read_text(encoding="utf-8"))
        self.assertIn("cockpit-rail", self.page.read_text(encoding="utf-8"))
        self.assertIn('"rev":2', self.page.read_text(encoding="utf-8"))
        self.assertEqual(before_state, self.state.read_bytes())
        self.assertEqual(upgrade.upgrade(self.root, self.template)["status"],
                         "unchanged")

    def test_dry_run_does_not_write(self):
        original = self.page.read_bytes()
        info = upgrade.upgrade(self.root, self.template, dry_run=True)
        self.assertEqual(info["status"], "would-upgrade")
        self.assertEqual(original, self.page.read_bytes())

    def test_rejects_different_slug_or_bad_state(self):
        self.state.write_text('window.STATE = {"slug":"different"}', encoding="utf-8")
        with self.assertRaisesRegex(upgrade.UpgradeError, "different project"):
            upgrade.upgrade(self.root, self.template)
        self.state.write_text('window.STATE = INVALID', encoding="utf-8")
        with self.assertRaisesRegex(upgrade.UpgradeError, "not valid JSON"):
            upgrade.upgrade(self.root, self.template)

    def test_blocks_corrupted_snapshot_and_symlink(self):
        self.page.write_text("<html>no snapshot</html>", encoding="utf-8")
        with self.assertRaisesRegex(upgrade.UpgradeError, "snapshot marker"):
            upgrade.upgrade(self.root, self.template)


if __name__ == "__main__":
    unittest.main()
