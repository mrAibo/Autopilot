"""Host test evidence cannot be forged by logs or reused after source changes."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
