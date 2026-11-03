"""Git worktree isolation and safe landing tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import worktrees

ZONES = ["app.txt", "new-file.txt", "recovery.txt"]


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

    def test_host_finalizes_sandboxed_worker_with_explicit_zone(self):
        path = Path(worktrees.create(self.root, "11")["cwd"])
        (path / "app.txt").write_text("fixed\n", encoding="utf-8")
        result = worktrees.finalize(self.root, "11", self.base, ["app.txt"], 2, 0)
        self.assertEqual(result["status"], "finalized")
        self.assertEqual(result["files"], ["app.txt"])
        self.assertEqual(worktrees.status(self.root, "11")["dirty"], False)
        self.assertEqual(worktrees.source_commit(self.root, "11", self.base),
                         result["sourceCommit"])
        landed = worktrees.land(self.root, "11", self.base, ZONES)
        self.assertEqual(landed["status"], "landed")
        self.assertEqual((self.root / "app.txt").read_text(encoding="utf-8"), "fixed\n")

    def test_finalization_fails_closed_on_extra_untracked_file(self):
        path = Path(worktrees.create(self.root, "12")["cwd"])
        (path / "app.txt").write_text("fixed\n", encoding="utf-8")
        (path / "unexpected.txt").write_text("preserve\n", encoding="utf-8")
        with self.assertRaisesRegex(worktrees.WorktreeError, "outside declared zone"):
            worktrees.finalize(self.root, "12", self.base, ["app.txt"], 2, 0)
        self.assertEqual(worktrees.status(self.root, "12")["dirty"], True)
        self.assertTrue((path / "unexpected.txt").exists())
        self.assertEqual(self.git(path, "rev-parse", "HEAD").stdout.strip(), self.base)

    def test_finalization_blocks_unknown_tests_and_wildcards(self):
        path = Path(worktrees.create(self.root, "13")["cwd"])
        (path / "app.txt").write_text("fixed\n", encoding="utf-8")
        for passed, failed in ((0, 0), (2, 1)):
            with self.subTest(passed=passed, failed=failed):
                with self.assertRaisesRegex(worktrees.WorktreeError, "test results"):
                    worktrees.finalize(self.root, "13", self.base, ["app.txt"], passed, failed)
        with self.assertRaisesRegex(worktrees.WorktreeError, "Unsafe or wildcard"):
            worktrees.finalize(self.root, "13", self.base, ["*"], 2, 0)
        with self.assertRaisesRegex(worktrees.WorktreeError, "Unsafe or wildcard"):
            worktrees.finalize(self.root, "13", self.base, ["../"], 2, 0)
        self.assertEqual(self.git(path, "rev-parse", "HEAD").stdout.strip(), self.base)

    def test_single_commit_can_be_landed(self):
        path = Path(worktrees.create(self.root, "03")["cwd"])
        (path / "new-file.txt").write_text("new", encoding="utf-8")
        self.git(path, "add", "new-file.txt")
        self.git(path, "commit", "-qm", "T03")
        result = worktrees.land(self.root, "03", self.base, ZONES)
        self.assertEqual(result["status"], "landed")
        self.assertEqual((self.root / "new-file.txt").read_text(encoding="utf-8"), "new")
        # Cherry-pick may rewrite the source SHA; require an explicit cleanup acknowledgement.
        self.assertEqual(worktrees.remove(self.root, "03", acknowledge_loss=True)["status"], "removed")

    def test_duplicate_landing_recovers_matching_cherry_pick(self):
        path = Path(worktrees.create(self.root, "06")["cwd"])
        (path / "recovery.txt").write_text("crash safe\n", encoding="utf-8")
        self.git(path, "add", "recovery.txt")
        self.git(path, "commit", "-qm", "T06 recovery")
        first = worktrees.land(self.root, "06", self.base, ZONES)
        self.assertFalse(first["recovered"])
        again = worktrees.land(self.root, "06", self.base, ZONES)
        self.assertTrue(again["recovered"])
        self.assertEqual(first["landedCommit"], again["landedCommit"])
        detected = worktrees.recover(self.root, "06", self.base)
        self.assertEqual(detected["landedCommit"], first["landedCommit"])
        self.assertEqual(self.git(self.root, "rev-list", "--count", self.base + "..HEAD").stdout.strip(), "1")

    def test_crash_during_cherry_pick_is_detected_without_destructive_abort(self):
        path = Path(worktrees.create(self.root, "08")["cwd"])
        (path / "app.txt").write_text("executor\n", encoding="utf-8")
        self.git(path, "add", "app.txt")
        self.git(path, "commit", "-qm", "executor modifies app")
        source = self.git(path, "rev-parse", "HEAD").stdout.strip()
        (self.root / "app.txt").write_text("primary\n", encoding="utf-8")
        self.git(self.root, "add", "app.txt")
        self.git(self.root, "commit", "-qm", "primary modifies app")
        conflict = worktrees.git(self.root, "cherry-pick", "-x", source, check=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertTrue(worktrees.interrupted_cherry_pick(self.root))
        with self.assertRaisesRegex(worktrees.WorktreeError, "interrupted"):
            worktrees.recover(self.root, "08", self.base)
        with self.assertRaisesRegex(worktrees.WorktreeError, "interrupted"):
            worktrees.land(self.root, "08", self.base, ZONES)
        # Read-only recovery did not abort or silently reset unrelated changes.
        self.assertTrue(worktrees.interrupted_cherry_pick(self.root))
        self.git(self.root, "cherry-pick", "--abort")
        self.assertEqual((self.root / "app.txt").read_text(encoding="utf-8"), "primary\n")

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
            worktrees.land(self.root, "04", self.base, ZONES)
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD").stdout.strip(), self.base)

    def test_dirty_main_is_never_modified(self):
        path = Path(worktrees.create(self.root, "05")["cwd"])
        self.git(path, "commit", "--allow-empty", "-qm", "T05")
        (self.root / "app.txt").write_text("uncommitted\n", encoding="utf-8")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.land(self.root, "05", self.base, ZONES)
        self.assertEqual((self.root / "app.txt").read_text(encoding="utf-8"), "uncommitted\n")

    def commit_in_worktree(self, ticket, *files):
        path = Path(worktrees.create(self.root, ticket)["cwd"])
        for name in files:
            (path / name).parent.mkdir(parents=True, exist_ok=True)
            (path / name).write_text("x\n", encoding="utf-8")
        self.git(path, "add", "-f", *files)
        self.git(path, "commit", "-qm", "T" + ticket)
        return path

    def test_land_rejects_commit_outside_zone_or_in_protected_dirs(self):
        for n, name in enumerate((".claude/settings.json", ".autopilot/state.js",
                                  ".CLAUDE/settings.json", "other.txt")):
            ticket = "2%d" % n
            self.commit_in_worktree(ticket, "app.txt", name)
            with self.subTest(path=name):
                with self.assertRaisesRegex(worktrees.WorktreeError, "Unsafe worker path|outside declared"):
                    worktrees.land(self.root, ticket, self.base, ["app.txt", ".claude/", ".autopilot/"])
            self.assertEqual(self.git(self.root, "rev-parse", "HEAD").stdout.strip(), self.base)

    def test_land_accepts_dir_zone_and_requires_a_zone(self):
        self.commit_in_worktree("30", "src/a.txt")
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.land(self.root, "30", self.base, [])
        self.assertEqual(worktrees.land(self.root, "30", self.base, ["src/"])["status"], "landed")

    def test_rename_out_of_zone_reports_both_paths_and_is_rejected(self):
        (self.root / "outside").mkdir()
        (self.root / "outside" / "x.txt").write_text("secret\n", encoding="utf-8")
        (self.root / "zone").mkdir()
        self.git(self.root, "add", "outside")
        self.git(self.root, "commit", "-qm", "outside file")
        base = self.git(self.root, "rev-parse", "HEAD").stdout.strip()
        path = Path(worktrees.create(self.root, "31")["cwd"])
        (path / "zone").mkdir()
        self.git(path, "mv", "outside/x.txt", "zone/x.txt")
        self.assertEqual(worktrees.changed_paths(path), ["outside/x.txt", "zone/x.txt"])
        with self.assertRaisesRegex(worktrees.WorktreeError, "outside declared zone: outside/x.txt"):
            worktrees.finalize(self.root, "31", base, ["zone/"], 2, 0)

    def test_dot_github_is_a_valid_zone(self):
        worktrees.check_paths_in_zones([".github/workflows/ci.yml"], [".github/workflows/"])
        with self.assertRaises(worktrees.WorktreeError):
            worktrees.check_paths_in_zones([".git/config"], [".git/"])


if __name__ == "__main__":
    unittest.main()
