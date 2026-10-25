"""Git worktree isolation and safe landing tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import worktrees


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git(self.root, "init", "-q")
        self.git(self.root, "config", "user.name", "Autopilot Test")
        self.git(self.root, "config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(".autopilot/worktrees/\n", encoding="utf-8")
        (self.root / "app.txt").write_text("original\n", encoding="utf-8")
        self.git(self.root, "add", ".gitignore", "app.txt")
        self.git(self.root, "commit", "-qm", "baseline")
        self.base = self.git(self.root, "rev-parse", "HEAD").stdout.strip()

    def git(self, root, *args):
        result = subprocess.run(["git", "-C", str(root), *args],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_worktree_is_detached_from_main(self):
        result = worktrees.create(self.root, "01")
        path = Path(result["cwd"])
        self.assertTrue(path.is_dir())
        self.assertEqual(worktrees.status(self.root, "01")["dirty"], False)
        (path / "isolated.txt").write_text("worker", encoding="utf-8")
        self.assertFalse((self.root / "isolated.txt").exists())

    def test_rejects_invalid_ticket_and_ref(self):
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.create(self.root, "../outside")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.create(self.root, "01", base="--malicious")

    def test_refuses_creation_without_gitignore(self):
        (self.root / ".gitignore").write_text("*.log\n", encoding="utf-8")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.create(self.root, "99")

    def test_dirty_worktree_cannot_be_deleted(self):
        path = Path(worktrees.create(self.root, "02")["cwd"])
        (path / "dirty.txt").write_text("uncommitted", encoding="utf-8")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.remove(self.root, "02", acknowledge_loss=True)

    def test_single_commit_can_be_landed(self):
        path = Path(worktrees.create(self.root, "03")["cwd"])
        (path / "new-file.txt").write_text("new", encoding="utf-8")
        self.git(path, "add", "new-file.txt")
        self.git(path, "commit", "-qm", "T03")
        result = worktrees.land(self.root, "03", self.base)
        self.assertEqual(result["status"], "landed")
        self.assertEqual((self.root / "new-file.txt").read_text(encoding="utf-8"), "new")
        # Cherry-pick may rewrite the source SHA; require an explicit cleanup acknowledgement.
        self.assertEqual(worktrees.remove(self.root, "03", acknowledge_loss=True)["status"], "removed")

    def test_duplicate_landing_recovers_matching_cherry_pick(self):
        path = Path(worktrees.create(self.root, "06")["cwd"])
        (path / "recovery.txt").write_text("crash safe\n", encoding="utf-8")
        self.git(path, "add", "recovery.txt")
        self.git(path, "commit", "-qm", "T06 recovery")
        first = worktrees.land(self.root, "06", self.base)
        self.assertFalse(first["recovered"])
        again = worktrees.land(self.root, "06", self.base)
        self.assertTrue(again["recovered"])
        self.assertEqual(first["landedCommit"], again["landedCommit"])
        detected = worktrees.recover(self.root, "06", self.base)
        self.assertEqual(detected["landedCommit"], first["landedCommit"])
        self.assertEqual(self.git(self.root, "rev-list", "--count", self.base + "..HEAD").stdout.strip(), "1")

    def test_recovery_refuses_uncommitted_executor_changes(self):
        path = Path(worktrees.create(self.root, "07")["cwd"])
        (path / "uncommitted.txt").write_text("hold", encoding="utf-8")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.recover(self.root, "07", self.base)

    def test_multiple_commits_are_not_silently_landed(self):
        path = Path(worktrees.create(self.root, "04")["cwd"])
        self.git(path, "commit", "--allow-empty", "-qm", "T04 part 1")
        self.git(path, "commit", "--allow-empty", "-qm", "T04 part 2")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.land(self.root, "04", self.base)
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD").stdout.strip(), self.base)

    def test_dirty_main_is_never_modified(self):
        path = Path(worktrees.create(self.root, "05")["cwd"])
        self.git(path, "commit", "--allow-empty", "-qm", "T05")
        (self.root / "app.txt").write_text("uncommitted\n", encoding="utf-8")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.land(self.root, "05", self.base)
        self.assertEqual((self.root / "app.txt").read_text(encoding="utf-8"), "uncommitted\n")


if __name__ == "__main__":
    unittest.main()
