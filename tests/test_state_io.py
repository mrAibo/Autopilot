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
    """Phase 0 copies tools into the project; an import of a module that is not copied crashes there."""

    TOOLS = Path(__file__).resolve().parent.parent / "skills" / "autopilot" / "tools"
    PHASE = Path(__file__).resolve().parent.parent / "skills" / "autopilot" / "phases" / "0-instruments.md"

    def copied(self):
        import re
        return set(re.findall(r'^cp "\$\{TPL%/phases/\*\}/tools/(\w+)\.py"', self.PHASE.read_text(encoding="utf-8"),
                              re.M))

    def sibling_imports(self, module):
        import ast
        siblings = {p.stem for p in self.TOOLS.glob("*.py")}
        tree = ast.parse((self.TOOLS / (module + ".py")).read_text(encoding="utf-8"))
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                found.add(node.module.split(".")[0])
        return (found & siblings) - {module}

    def test_state_io_is_copied(self):
        self.assertIn("state_io", self.copied())

    def test_every_sibling_a_copied_tool_imports_is_copied_too(self):
        copied = self.copied()
        self.assertIn("ap", copied)
        for module in sorted(copied):
            with self.subTest(module=module):
                self.assertTrue((self.TOOLS / (module + ".py")).is_file(), "listed but missing")
                self.assertLessEqual(self.sibling_imports(module), copied)

    # Модули, что запускаются только из навыка (в проект не копируются). Новый модуль tools/
    # надо внести либо в 0-instruments.md, либо сюда. Динамические импорты (importlib,
    # __import__) AST-разбор не видит — предел проверки.
    RUN_FROM_SKILL = {"bounded_api_pilot", "dashboard_upgrade",
                      "offline_fixture_worker", "offline_supervisor", "process_gate", "repo_doctor"}

    def unlisted(self, copied, run_from_skill):
        return {p.stem for p in self.TOOLS.glob("*.py")} - copied - run_from_skill

    def test_every_tool_is_copied_or_named_as_run_from_skill(self):
        self.assertEqual(self.unlisted(self.copied(), self.RUN_FROM_SKILL), set())

    def test_a_module_in_neither_list_fails_the_check(self):
        self.assertEqual(self.unlisted(self.copied() - {"run_log"}, self.RUN_FROM_SKILL), {"run_log"})
        self.assertEqual(self.unlisted(self.copied(), self.RUN_FROM_SKILL - {"repo_doctor"}), {"repo_doctor"})

    def test_ap_imports_are_copied(self):
        self.assertLessEqual(self.sibling_imports("ap"), self.copied())


if __name__ == "__main__":
    unittest.main()
