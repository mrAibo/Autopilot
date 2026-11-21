import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_dashboard_browser", ROOT / "tools" / "check-dashboard-browser.py")
cdb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cdb)


class PlanLine(unittest.TestCase):
    def test_present(self):
        for n, m in ((0, 1), (3, 5), (12, 120)):
            self.assertTrue(cdb.plan_line_ok(["Дальше", "план: %d из %d" % (n, m)]))

    def test_absent_or_malformed(self):
        for texts in ([], ["Что делать дальше"], ["план: из 5"], ["план: 3 из"], ["plan: 3 из 5"], ["Итог план: 3 из 5"]):
            self.assertFalse(cdb.plan_line_ok(texts), texts)

    def test_skip_without_chrome(self):
        with mock.patch.object(cdb, "chrome_browser", return_value=None), \
                mock.patch.object(cdb.sys, "argv", ["x", "--plan"]), \
                mock.patch.object(cdb.subprocess, "run") as run, mock.patch("builtins.print") as out:
            self.assertEqual(cdb.main(), 0)
        run.assert_not_called()
        self.assertIn("не проверено", out.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
