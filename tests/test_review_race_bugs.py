"""Три бага из PROGRESS.md: start зависимого при `review`, переименование в `commit_paths`.

Третий баг (гонка `gate_sign`) покрыт в test_gate_sign.py. Каждый тест здесь красный на прежнем коде.
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest

import test_ap

WAITING = "сначала заверши зависимости"


class DependentStart(unittest.TestCase):
    """Таск 02 зависит от 01 (`test_ap.Run.plan`): start допускает `review`, done ждёт `done`."""

    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)
        self.h.plan()
        self.assertEqual(self.h.ap("tickets")[0], 0)

    def status(self, ident):
        return {t["id"]: t for t in self.h.state()["tickets"]}[ident]["status"]

    def move(self, *steps):
        for step in steps:
            code, out = self.h.ap("ticket", "01", *step)
            self.assertEqual(code, 0, out)

    def test_start_passes_while_the_dependency_is_in_review(self):
        self.move(["start"], ["review"])
        code, out = self.h.ap("ticket", "02", "start")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.status("02"), "in-progress")

    def test_start_still_refuses_a_dependency_that_is_not_committed_or_in_review(self):
        cases = {"pending": [], "in-progress": [["start"]],
                 "repair": [["start"], ["review"], ["repair", "--note", "ключ схемы"]],
                 "failed": [["start"], ["fail", "--note", "git отказал"]]}
        for status, steps in cases.items():
            with self.subTest(dependency=status):
                self.setUp()
                self.move(*steps)
                self.assertEqual(self.status("01"), status)
                code, out = self.h.ap("ticket", "02", "start")
                self.assertNotEqual(code, 0, out)
                self.assertIn(WAITING, out)
                self.assertEqual(self.status("02"), "pending")

    def test_done_waits_for_the_dependency_to_be_done(self):
        self.move(["start"], ["review"])
        self.assertEqual(self.h.ap("ticket", "02", "start")[0], 0)
        sha = self.h.commit("T02")
        code, out = self.h.ap("ticket", "02", "done", "--tests", "5/0", "--commit", sha)
        self.assertNotEqual(code, 0, out)
        self.assertIn(WAITING, out)
        self.assertEqual(self.status("02"), "in-progress")
        self.move(["done", "--tests", "3/0", "--commit", self.h.commit("T01")])
        code, out = self.h.ap("ticket", "02", "done", "--tests", "5/0", "--commit", sha)
        self.assertEqual(code, 0, out)
        self.assertEqual(self.status("02"), "done")


def load_ap():
    spec = importlib.util.spec_from_file_location("ap_review_race", test_ap.AP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(shutil.which("git"), "git is required")
class CommitPathsRename(unittest.TestCase):
    """`git mv old new` ставит в индекс `D old` и `A new`: коммит нового пути уносит и удаление старого."""

    BODY = "".join("line %d\n" % n for n in range(20))

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-rename-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        for name in ("old.txt", "a.txt", "x.txt"):
            self.put(name, self.BODY)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self.ap = load_ap()
        self.ap.ROOT = self.root

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", check=True).stdout

    def put(self, name, text):
        with open(os.path.join(self.root, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def changed_by_head(self):
        shown = self.git("show", "--name-status", "--no-renames", "--format=", "HEAD")
        return sorted(line for line in shown.splitlines() if line)

    def test_the_old_path_of_a_staged_rename_goes_in_the_same_commit(self):
        self.git("mv", "old.txt", "new.txt")
        sha = self.ap.commit_paths(["new.txt"], "rename", [])
        self.assertTrue(sha)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.changed_by_head(), ["A\tnew.txt", "D\told.txt"])

    def test_a_rename_with_edited_content_is_found_too(self):
        self.git("mv", "old.txt", "new.txt")
        self.put("new.txt", self.BODY.replace("line 3\n", "line three\n"))
        self.assertTrue(self.ap.commit_paths(["new.txt"], "rename and edit", []))
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.changed_by_head(), ["A\tnew.txt", "D\told.txt"])

    def test_an_unrelated_staged_rename_is_left_alone(self):
        self.git("mv", "x.txt", "y.txt")
        self.put("a.txt", "changed\n")
        self.assertTrue(self.ap.commit_paths(["a.txt"], "plain", []))
        self.assertEqual(self.changed_by_head(), ["M\ta.txt"])
        self.assertEqual(self.git("status", "--porcelain").strip(), "R  x.txt -> y.txt")

    def test_a_zone_directory_carries_the_old_path_of_a_rename_inside_it(self):
        # R02: `dir/` и `dir` покрывают новый путь, старый путь каталога тоже внутри — в коммит оба
        for folder, spec in (("da", "da/"), ("db", "db")):
            os.makedirs(os.path.join(self.root, folder))
            self.put(folder + "/old.txt", self.BODY)
            self.git("add", folder + "/old.txt")
            self.git("commit", "-q", "-m", "add " + folder)
            self.git("mv", folder + "/old.txt", folder + "/new.txt")
            self.assertTrue(self.ap.commit_paths([spec], "rename " + spec, []))
            self.assertEqual(self.git("status", "--porcelain"), "")
            self.assertEqual(self.changed_by_head(), ["A\t%s/new.txt" % folder, "D\t%s/old.txt" % folder])

    def test_a_rename_from_outside_the_zone_directory_into_it_is_carried(self):
        self.git("mv", "old.txt", "dir_new.txt")
        os.makedirs(os.path.join(self.root, "dir"))
        self.git("mv", "dir_new.txt", "dir/new.txt")
        self.assertTrue(self.ap.commit_paths(["dir/"], "move in", []))
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.changed_by_head(), ["A\tdir/new.txt", "D\told.txt"])

    def test_a_foreign_rename_stays_staged_when_a_directory_is_committed(self):
        self.git("mv", "x.txt", "y.txt")
        os.makedirs(os.path.join(self.root, "dir"))
        self.put("dir/a.txt", "changed\n")
        self.assertTrue(self.ap.commit_paths(["dir/"], "plain", []))
        self.assertEqual(self.changed_by_head(), ["A\tdir/a.txt"])
        self.assertEqual(self.git("status", "--porcelain").strip(), "R  x.txt -> y.txt")

    def test_a_plain_path_commits_only_itself_and_nothing_to_commit_is_none(self):
        self.put("a.txt", "changed\n")
        self.assertTrue(self.ap.commit_paths(["a.txt"], "plain", ["Autopilot-Run: r"]))
        self.assertEqual(self.changed_by_head(), ["M\ta.txt"])
        self.assertIn("Autopilot-Run: r", self.git("log", "-1", "--format=%B"))
        self.assertIsNone(self.ap.commit_paths(["a.txt"], "again", []))


if __name__ == "__main__":
    unittest.main()
