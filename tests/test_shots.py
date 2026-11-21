"""R28a: прототип shots.py без запуска настоящего браузера (docs/adr/0030)."""
import contextlib
import io
import os
import socket
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "autopilot", "tools"))
import shots  # noqa: E402


class ShotsTests(unittest.TestCase):
    def test_args_defaults_and_overrides(self):
        a = shots.parse_args(["--url", "http://x/", "--out", "d"])
        self.assertEqual((a.url, a.out, a.width, a.height), ("http://x/", "d", 1440, 2000))
        a = shots.parse_args(["--url", "u", "--out", "d", "--width", "390", "--height", "800"])
        self.assertEqual((a.width, a.height), (390, 800))

    def test_url_and_out_are_required(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            shots.parse_args(["--url", "u"])

    def test_free_port_is_bindable(self):
        port = shots.free_port()
        self.assertGreater(port, 0)
        with socket.socket() as s:
            s.bind(("127.0.0.1", port))

    def test_bad_url_scheme_exit_2_with_reason(self):
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(err),                 mock.patch.object(shots.subprocess, "run") as run:
            code = shots.main(["--url", "ftp://x/", "--out", d])
        self.assertEqual(code, 2)
        self.assertIn("схема", err.getvalue())
        run.assert_not_called()

    def test_no_browser_exit_2_with_reason(self):
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as d, mock.patch.object(shots, "find_browser", return_value=None), \
                contextlib.redirect_stderr(err), mock.patch.object(shots.subprocess, "run") as run:
            code = shots.main(["--url", "http://x/", "--out", d])
        self.assertEqual(code, 2)
        self.assertIn("нет Chrome/Edge", err.getvalue())
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
