"""Регрессии hardening-волны 2026-11: schemaVersion, единый ledger расхода,
literal pathspec в commit_paths и неполный history-cache."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import test_ap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_ap.SKILL, "tools"))
import run_log  # noqa: E402
import state_io  # noqa: E402


def load_ap():
    spec = importlib.util.spec_from_file_location("ap_hardening", test_ap.AP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SchemaVersion(unittest.TestCase):
    def setUp(self):
        self.ap = load_ap()

    def test_legacy_state_gets_the_version_and_a_newer_one_is_a_clear_error(self):
        state = {"version": 2}
        self.assertTrue(state_io.ensure_schema_version(state))
        self.assertEqual(state["schemaVersion"], state_io.SCHEMA_VERSION)
        self.assertFalse(state_io.ensure_schema_version(state))
        for bad in (True, 0, "1"):
            with self.assertRaises(state_io.StateError):
                state_io.ensure_schema_version({"schemaVersion": bad})
        with self.assertRaises(state_io.StateError):
            state_io.ensure_schema_version({"schemaVersion": state_io.SCHEMA_VERSION + 1})

    def test_fresh_state_carries_the_version(self):
        state = self.ap.fresh_state({"slug": "x"})
        self.assertEqual(state["schemaVersion"], state_io.SCHEMA_VERSION)

    def test_read_state_upgrades_an_old_snapshot_in_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.js")
            with open(path, "w", encoding="utf-8") as f:
                f.write("window.STATE = {\n  \"version\": 2\n};\n")
            old = self.ap.STATE
            self.ap.STATE = path
            try:
                got = self.ap.read_state()
            finally:
                self.ap.STATE = old
        self.assertEqual(got["schemaVersion"], state_io.SCHEMA_VERSION)


class SpendLedger(unittest.TestCase):
    def test_executor_and_spend_rows_are_one_normalized_ledger_with_last_agent_row(self):
        rows = [
            {"k": "executor", "run": "r--wip", "agent": "a", "agent_type": "autopilot-executor-01-x",
             "input": 10, "output": 2, "cache_read": 30, "cache_write": 10},
            {"k": "executor", "run": "r", "agent": "a", "agent_type": "autopilot-executor-01-x",
             "input": 20, "output": 5, "cache_read": 50, "cache_write": 5, "source": "hook"},
            {"k": "spend", "run": "r", "agent": "b", "role": "reviewer", "model": "haiku", "input": 7},
        ]
        got = run_log.spend_rows(rows, "r")
        self.assertEqual(len(got), 2)
        a = next(r for r in got if r["agent"] == "a")
        self.assertEqual((a["input"], a["output"], a["tokens"], a["source"], a["role"]),
                         (20, 5, 25, "hook", "executor"))
        self.assertEqual(a["hit"], 67)                 # 50 / (20 + 50 + 5) = 66.7 %
        b = next(r for r in got if r["agent"] == "b")
        self.assertEqual((b["role"], b["source"]), ("reviewer", "claude"))

    def test_snapshot_is_bounded_and_chronological(self):
        rows = [{"k": "spend", "run": "r", "t": "2026-01-01T00:00:0%d+00:00" % i, "agent": "a%d" % i,
                 "input": i} for i in range(4)]
        got = run_log.spend_snapshot(rows, "r", limit=2)
        self.assertEqual([r["agent"] for r in got], ["a2", "a3"])

    def test_spend_kind_is_accepted_by_append_and_compute_spend(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(run_log.append(tmp, "spend", run="r", source="manual", agent="a", input=3))
            rows = run_log.read_all(tmp)
            self.assertEqual(rows[0]["k"], "spend")
            self.assertEqual(rows[0]["source"], "manual")
        spend = load_ap().compute_spend([{"k": "spend", "run": "r", "role": "executor", "input": 4}], "r")
        self.assertEqual(spend["byRole"]["executor"]["tokens"], 4)


@unittest.skipUnless(shutil.which("git"), "git is required")
class CommitPathsLiteral(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-literal-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        for name in ("a[1].txt", "a1.txt"):
            with open(os.path.join(self.root, name), "w", encoding="utf-8") as f:
                f.write("old\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        for name in ("a[1].txt", "a1.txt"):
            with open(os.path.join(self.root, name), "w", encoding="utf-8") as f:
                f.write("new\n")
        self.ap = load_ap()
        self.ap.ROOT = self.root

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", check=True).stdout

    def test_brackets_are_not_a_glob(self):
        sha = self.ap.commit_paths(["a[1].txt"], "literal path", [])
        self.assertTrue(sha)
        status = self.git("status", "--porcelain")
        self.assertIn(" M a1.txt", status)
        self.assertNotIn("a[1].txt", status)


if __name__ == "__main__":
    unittest.main()
