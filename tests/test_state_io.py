"""Тесты state_io: разбор и запись .autopilot/state.js."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "autopilot" / "tools"))
import state_io  # noqa: E402

BOM = chr(0xFEFF)
DATA = {"slug": "демо", "tickets": [], "rev": 3}


def winerror(code):
    exc = PermissionError(13, "denied")
    exc.winerror = code
    return exc


class ParseTests(unittest.TestCase):
    def test_accepts_all_wrappers(self):
        body = json.dumps(DATA, ensure_ascii=False)
        for text in ("window.STATE =\n" + body, "window.STATE = " + body + ";\n",
                     "" + BOM + "window.STATE = " + body, body, "" + BOM + "" + body + ";"):
            self.assertEqual(state_io.parse_state_text(text), DATA, repr(text[:20]))

    def test_rejects_empty_garbage_and_non_objects(self):
        for text in ("", "  \n", "" + BOM + "", "window.STATE = ", "window.STATE = {bad}",
                     "window.STATE = []", "hello", "x = {}"):
            with self.assertRaises(state_io.StateError, msg=repr(text)):
                state_io.parse_state_text(text)

    def test_read_file_bom_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.js"
            p.write_bytes(b"\xef\xbb\xbf" + b"window.STATE = " + json.dumps(DATA).encode() + b";")
            self.assertEqual(state_io.read_state_file(p)["rev"], 3)
            with self.assertRaises(state_io.StateError):
                state_io.read_state_file(Path(d) / "nope.js")
            p.write_bytes(b"\xff\xfe\x00bad")
            with self.assertRaises(state_io.StateError):
                state_io.read_state_file(p)


class WriteTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = Path(self.dir.name) / "state.js"

    def test_roundtrip_and_prefix(self):
        state_io.write_state_file(self.path, DATA)
        self.assertTrue(self.path.read_text(encoding="utf-8").startswith("window.STATE = {"))
        self.assertEqual(state_io.read_state_file(self.path), DATA)
        state_io.write_state_file(self.path, DATA, prefix="window.STATE =\n")
        self.assertTrue(self.path.read_text(encoding="utf-8").startswith("window.STATE =\n{"))
        self.assertFalse(Path(str(self.path) + ".tmp").exists())

    def test_retries_winerror_5_twice_then_succeeds(self):
        real, calls = os.replace, []

        def flaky(src, dst):
            calls.append(1)
            if len(calls) <= 2:
                raise winerror(5)
            real(src, dst)

        with mock.patch.object(state_io, "WINDOWS", True), \
                mock.patch.object(state_io.os, "replace", flaky), \
                mock.patch.object(state_io.time, "sleep"):
            state_io.write_state_file(self.path, DATA)
        self.assertEqual(len(calls), 3)
        self.assertEqual(state_io.read_state_file(self.path), DATA)

    def test_permanent_lock_raises_state_error_and_cleans_tmp(self):
        calls = []

        def locked(src, dst):
            calls.append(1)
            raise winerror(32)

        with mock.patch.object(state_io, "WINDOWS", True), \
                mock.patch.object(state_io.os, "replace", locked), \
                mock.patch.object(state_io.time, "sleep"):
            with self.assertRaises(state_io.StateError):
                state_io.write_state_file(self.path, DATA)
        self.assertEqual(len(calls), 12)
        self.assertFalse(Path(str(self.path) + ".tmp").exists())
        self.assertFalse(self.path.exists())

    def test_other_errors_are_not_retried(self):
        calls = []

        def broken(src, dst):
            calls.append(1)
            raise winerror(1234)

        with mock.patch.object(state_io, "WINDOWS", True), \
                mock.patch.object(state_io.os, "replace", broken):
            with self.assertRaises(state_io.StateError):
                state_io.write_state_file(self.path, DATA)
        self.assertEqual(len(calls), 1)

    def test_no_retry_off_windows(self):
        calls = []

        def denied(src, dst):
            calls.append(1)
            raise winerror(5)

        with mock.patch.object(state_io, "WINDOWS", False), \
                mock.patch.object(state_io.os, "replace", denied):
            with self.assertRaises(state_io.StateError):
                state_io.write_state_file(self.path, DATA)
        self.assertEqual(len(calls), 1)


class InstrumentsCopyListTests(unittest.TestCase):
    """Phase 0 installs the tools with `ap.py bootstrap`, which copies every `.py` of `tools/`:
    a sibling import of a copied tool can no longer be left out of a hand-kept `cp` list."""

    PHASE = Path(__file__).resolve().parent.parent / "skills" / "autopilot" / "phases" / "0-instruments.md"

    def test_phase_installs_through_bootstrap_not_a_hand_kept_cp_list(self):
        text = self.PHASE.read_text(encoding="utf-8")
        self.assertIn('tools/ap.py" bootstrap --project', text)
        self.assertNotIn('cp "${TPL%/phases/*}/tools/', text)


if __name__ == "__main__":
    unittest.main()
