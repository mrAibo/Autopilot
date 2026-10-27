"""Read-only project-independent Git diagnostics, using disposable repositories."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / "skills/autopilot/tools/repo_doctor.py"
spec = importlib.util.spec_from_file_location("repo_doctor", MODULE)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Unit Test")
        (self.root / ".gitignore").write_text(".autopilot/worktrees/\n")
        (self.root / "app.txt").write_text("base\n")
        self.git("add", ".gitignore", "app.txt")
        self.git("commit", "-qm", "baseline")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def git_status(self):
        return subprocess.check_output(
            ["git", "-C", str(self.root), "status",
             "--porcelain", "-z", "--untracked-files=all"])

    def test_clean_repo_ready_and_read_only(self):
        before = self.git_status()
        head = self.git("rev-parse", "HEAD").stdout.strip()
        result = doctor.inspect(self.root)
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["can_prepare_worktree"])
        self.assertEqual(result["base_commit"], head)
        self.assertEqual(result["source"],
                         {"staged": 0, "unstaged": 0, "untracked": 0, "conflicted": 0})
        self.assertEqual(self.git_status(), before)
        self.assertFalse((self.root / ".autopilot").exists())

    def test_dirty_counts_no_filenames_and_no_git_change(self):
        secret = self.root / "private-dont-display.key"
        secret.write_text("do not output\n")
        (self.root / "app.txt").write_text("working changes\n")
        self.git("add", "app.txt")
        (self.root / "app.txt").write_text("unstaged changes\n")
        before = self.git_status()
        report = doctor.inspect(self.root)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["source"]["staged"], 1)
        self.assertEqual(report["source"]["unstaged"], 1)
        self.assertEqual(report["source"]["untracked"], 1)
        self.assertIn("source-has-uncommitted-changes", report["blockers"])
        self.assertNotIn(secret.name, json.dumps(report))
        self.assertNotIn("do not output", json.dumps(report))
        self.assertEqual(self.git_status(), before)
        self.assertTrue(secret.is_file())

    def test_missing_ignore_rule_blocks_without_writing_ignore(self):
        (self.root / ".gitignore").write_text("*.log\n")
        before = (self.root / ".gitignore").read_bytes()
        report = doctor.inspect(self.root)
        self.assertIn("worktree-directory-not-ignored", report["blockers"])
        self.assertEqual((self.root / ".gitignore").read_bytes(), before)

    def test_uncommitted_changes_only_in_autopilot_ledger_are_ignored(self):
        ap = self.root / ".autopilot"
        ap.mkdir()
        (ap / "state.js").write_text("internal data\n")
        report = doctor.inspect(self.root)
        self.assertEqual(report["status"], "ready")
        self.assertFalse(report["source"]["untracked"])

    def test_non_python_stack_is_reported_not_executed(self):
        (self.root / "Cargo.toml").write_text("[package]\nname='probe'\nversion='0.1.0'\n")
        report = doctor.inspect(self.root)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any("Rust" in w for w in report["warnings"]))
        self.assertEqual(report["test_runners"]["available"], ["python-unittest"])

    def test_wrong_root_and_unborn_repo_fail_closed(self):
        with self.assertRaises(doctor.DoctorError):
            doctor.inspect(self.root / "missing")
        sub = self.root / "nested"
        sub.mkdir()
        with self.assertRaises(doctor.DoctorError):
            doctor.inspect(sub)
        with tempfile.TemporaryDirectory() as empty:
            subprocess.run(["git", "-C", empty, "init", "-q"], check=True)
            report = doctor.inspect(empty)
            self.assertIn("no-baseline-commit", report["blockers"])

    def test_symlink_worktree_target_blocked_when_supported(self):
        ap = self.root / ".autopilot"
        ap.mkdir()
        target = self.root / "link-target"
        target.mkdir()
        try:
            (ap / "worktrees").symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable for current Windows user")
        report = doctor.inspect(self.root)
        self.assertIn("unsafe-worktree-path", report["blockers"])

    def test_cli_json_and_status(self):
        cmd = [sys.executable, str(MODULE), "--root", str(self.root)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "ready")
        (self.root / "dirty.txt").write_text("untracked")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
