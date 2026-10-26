"""Host test evidence cannot be forged by logs or reused after source changes."""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] /
                       "skills" / "autopilot" / "tools"))
import test_evidence
import worktrees


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        for args in (("init", "-q"), ("config", "user.name", "Evidence Test"),
                     ("config", "user.email", "test@example.invalid")):
            self.git(*args)
        (self.root / ".gitignore").write_text(
            ".autopilot/worktrees/\n", encoding="utf-8")
        (self.root / "calc.py").write_text("def add(a,b): return a-b\n", encoding="utf-8")
        (self.root / "test_calc.py").write_text(
            "import unittest\nfrom calc import add\n"
            "class Check(unittest.TestCase):\n"
            " def test_add(self): self.assertEqual(add(2,3),5)\n",
            encoding="utf-8")
        self.git("add", ".gitignore", "calc.py", "test_calc.py")
        self.git("commit", "-qm", "baseline")
        self.base = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
        self.wt = pathlib.Path(worktrees.create(self.root, "01")["cwd"])

    def git(self, *args):
        r = subprocess.run(["git", "-C", str(self.root), *args],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_success_then_changed_source_invalidates_proof(self):
        (self.wt / "calc.py").write_text("def add(a,b): return a+b\n", encoding="utf-8")
        proof = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        self.assertEqual((proof["passed"], proof["failed"]), (1, 0))
        self.assertEqual(test_evidence.check(self.root, "01", self.base, proof)["passed"], 1)
        (self.wt / "calc.py").write_text("def add(a,b): return a-b\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "changed after tests"):
            test_evidence.check(self.root, "01", self.base, proof)

    def test_actual_failed_test_cannot_be_recorded_as_passed(self):
        with self.assertRaisesRegex(test_evidence.EvidenceError, "did not pass"):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_modified_suite_is_rejected_before_execution(self):
        (self.wt / "test_calc.py").write_text(
            "import unittest\nclass Check(unittest.TestCase):\n"
            " def test_add(self): self.assertTrue(True)\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Modified test suite"):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_suite_path_traversal_is_rejected(self):
        for bad in ("../secret.py", ".git/config.py", "/tmp/test_calc.py", "calc.py;echo"):
            with self.subTest(bad=bad), self.assertRaises(test_evidence.EvidenceError):
                test_evidence.verify(self.root, "01", self.base, bad)

    def test_fake_evidence_and_timeout_are_rejected(self):
        (self.wt / "calc.py").write_text("def add(a,b): return a+b\n", encoding="utf-8")
        evidence = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        for key, value in (("status", "unverified"), ("passed", 0), ("baseCommit", "bad")):
            forged = dict(evidence, **{key: value})
            with self.assertRaises(test_evidence.EvidenceError):
                test_evidence.check(self.root, "01", self.base, forged)
        with self.assertRaises(test_evidence.EvidenceError):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py", timeout=0)

    def test_fabricated_positive_receipt_cannot_turn_a_failing_suite_green(self):
        # A user-controlled state.js record can match HEAD and the source
        # fingerprint without ever having been produced by verify().
        forged = {"status": "verified", "runner": "python-unittest",
                  "suite": "test_calc.py", "baseCommit": self.base,
                  "workerHead": self.base,
                  "fingerprint": test_evidence.fingerprint(self.wt),
                  "passed": 999, "failed": 0}
        with self.assertRaisesRegex(test_evidence.EvidenceError, "did not pass"):
            test_evidence.check(self.root, "01", self.base, forged)

    def test_tampered_test_count_cannot_reuse_real_green_receipt(self):
        (self.wt / "calc.py").write_text("def add(a,b): return a+b\n", encoding="utf-8")
        genuine = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        inflated = dict(genuine, passed=999)
        with self.assertRaisesRegex(test_evidence.EvidenceError, "count"):
            test_evidence.check(self.root, "01", self.base, inflated)

    def test_legacy_green_receipt_without_timeout_is_rechecked(self):
        (self.wt / "calc.py").write_text("def add(a,b): return a+b\n", encoding="utf-8")
        genuine = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        genuine.pop("timeout")
        self.assertEqual(test_evidence.check(self.root, "01", self.base, genuine),
                         {"passed": 1, "failed": 0})

    def test_ignored_python_dependency_is_refused_before_execution(self):
        # An ignored module can change independently of the worktree hash.
        (self.wt / ".gitignore").write_text(
            ".autopilot/worktrees/\nhidden_helper.py\n", encoding="utf-8")
        (self.wt / "hidden_helper.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "from hidden_helper import add\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Ignored Python"):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_nested_ignored_python_dependency_is_refused(self):
        (self.wt / ".gitignore").write_text(
            ".autopilot/worktrees/\nlocal_modules/\n", encoding="utf-8")
        nested = self.wt / "local_modules"
        nested.mkdir()
        (nested / "hidden_helper.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "from local_modules.hidden_helper import add\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Ignored Python"):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_ignored_python_added_after_verify_invalidates_receipt(self):
        (self.wt / ".gitignore").write_text(
            ".autopilot/worktrees/\nhidden_helper.py\n", encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        proof = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        (self.wt / "hidden_helper.py").write_text(
            "def add(a,b): return 42\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Ignored Python"):
            test_evidence.check(self.root, "01", self.base, proof)

    def test_ignored_uppercase_extension_is_refused(self):
        (self.wt / ".gitignore").write_text(
            ".autopilot/worktrees/\n*.PY\n", encoding="utf-8")
        (self.wt / "IGNORED_HELPER.PY").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        with self.assertRaisesRegex(test_evidence.EvidenceError, "Ignored Python"):
            test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_inherited_pythonpath_cannot_supply_untracked_test_code(self):
        # PYTHONPATH from the host must never become a silent test dependency.
        external = self.root / "external_lib"
        external.mkdir()
        (external / "outside_helper.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "from outside_helper import add\n", encoding="utf-8")
        with patch.dict(os.environ, {"PYTHONPATH": str(external)}):
            with self.assertRaisesRegex(test_evidence.EvidenceError, "did not pass"):
                test_evidence.verify(self.root, "01", self.base, "test_calc.py")

    def test_inherited_pythonhome_does_not_break_clean_host_tests(self):
        (self.wt / "calc.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        with patch.dict(os.environ, {"PYTHONHOME": str(self.root / "nonexistent-python")}):
            proof = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        self.assertEqual(proof["passed"], 1)

    def test_ignored_non_python_data_does_not_block_tracked_unittest(self):
        (self.wt / ".gitignore").write_text(
            ".autopilot/worktrees/\nnotes.json\n", encoding="utf-8")
        (self.wt / "notes.json").write_text(
            '{"synthetic":true}\n', encoding="utf-8")
        (self.wt / "calc.py").write_text(
            "def add(a,b): return a+b\n", encoding="utf-8")
        proof = test_evidence.verify(self.root, "01", self.base, "test_calc.py")
        self.assertEqual(test_evidence.check(self.root, "01", self.base, proof)["passed"], 1)


if __name__ == "__main__":
    unittest.main()
