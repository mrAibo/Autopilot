"""worker_outcome.inspect: read-only zone check over everything the worker changed."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import worker_outcome
import worktrees


class InspectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for args in (("init", "-q"), ("config", "user.name", "T"), ("config", "user.email", "t@example.invalid")):
            self.git(self.root, *args)
        (self.root / ".gitignore").write_text(".autopilot/worktrees/\n", encoding="utf-8")
        (self.root / "outside").mkdir()
        (self.root / "outside" / "x.txt").write_text("secret\n", encoding="utf-8")
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-qm", "base")
        made = worktrees.create(self.root, "01")
        self.wt = Path(made["cwd"])
        (self.wt / "zone").mkdir()
        state = {"tickets": [{"id": "01", "status": "in-progress", "zone": ["zone/"],
                              "worktree": {"status": "prepared", "cwd": made["cwd"],
                                           "baseCommit": made["baseCommit"]}}]}
        (self.root / ".autopilot").mkdir(exist_ok=True)
        (self.root / ".autopilot" / "state.js").write_text(
            "window.STATE = " + json.dumps(state), encoding="utf-8")

    def git(self, where, *args):
        run = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_change_inside_zone_is_eligible(self):
        (self.wt / "zone" / "a.txt").write_text("ok\n", encoding="utf-8")
        result = worker_outcome.inspect(self.root, "01")
        self.assertEqual((result["eligible"], result["changed_files"]), (True, 1))

    def test_rename_out_of_zone_is_rejected_because_the_old_path_is_listed(self):
        self.git(self.wt, "mv", "outside/x.txt", "zone/x.txt")
        self.assertEqual(worktrees.changed_paths(self.wt), ["outside/x.txt", "zone/x.txt"])
        result = worker_outcome.inspect(self.root, "01")
        self.assertEqual((result["eligible"], result["reason"]), (False, "change-outside-zone"))

    def test_protected_roots_are_rejected_in_any_case(self):
        for name in (".claude", ".Autopilot"):
            with self.subTest(name=name):
                (self.wt / name).mkdir(exist_ok=True)
                (self.wt / name / "f.json").write_text("{}", encoding="utf-8")
                result = worker_outcome.inspect(self.root, "01")
                self.assertEqual((result["eligible"], result["reason"]), (False, "unsafe-change-path"))
                (self.wt / name / "f.json").unlink()
                (self.wt / name).rmdir()


if __name__ == "__main__":
    unittest.main()
