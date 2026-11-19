"""Проверка перед влитием (land_check) и виды работы (kinds): модули, `ticket NN land`, `worktrees.land`.

Запуск одного файла:  python -m unittest discover -s tests -p test_work_kinds.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_ap import MANIFEST, ticket
from test_one_command import GENERATORS, PY, TOOLS, Project, SKILL

sys.path.insert(0, TOOLS)
import kinds  # noqa: E402
import land_check  # noqa: E402
import model_router  # noqa: E402
import worktrees  # noqa: E402

RED = PY + " .autopilot/exit1.py"
GREEN = PY + " .autopilot/exit0.py"


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, encoding="utf-8")


class KindsUnit(unittest.TestCase):
    def test_constants_and_normalize(self):
        self.assertEqual(kinds.KINDS, ("quick", "bug", "task", "refactor"))
        self.assertEqual((kinds.DEFAULT_KIND, kinds.QUICK_MAX_TICKETS, kinds.QUICK_MAX_REQUIREMENTS), ("task", 1, 3))
        self.assertEqual((kinds.normalize(None), kinds.normalize(""), kinds.normalize("bug")), ("task", "task", "bug"))
        for bad in ("авто", "BUG", "fast", True):
            with self.assertRaises(ValueError):
                kinds.normalize(bad)

    def test_plan_problems_per_kind(self):
        repro = {"id": "01", "repro": True, "blockedBy": [], "zone": ["tests/"], "testsEdit": None}
        fix = {"id": "02", "repro": False, "blockedBy": ["01"], "zone": ["src/"], "testsEdit": None}
        self.assertEqual(kinds.plan_problems("task", [repro, fix, fix]), [])
        self.assertEqual(kinds.plan_problems("bug", [repro, fix]), [])
        self.assertTrue(kinds.plan_problems("bug", [fix]))
        self.assertTrue(kinds.plan_problems("bug", [repro, dict(repro, id="03")]))
        self.assertTrue(kinds.plan_problems("bug", [dict(repro, blockedBy=["02"]), fix]))
        self.assertTrue(kinds.plan_problems("quick", [repro, fix]))
        self.assertEqual(kinds.plan_problems("quick", [fix]), [])
        self.assertTrue(kinds.plan_problems("quick", [fix], manifest_rows=kinds.QUICK_MAX_REQUIREMENTS + 1))
        self.assertEqual(kinds.plan_problems("quick", [fix], manifest_rows=kinds.QUICK_MAX_REQUIREMENTS), [])
        tests_zone = dict(fix, zone=["src/", "tests/"])
        self.assertTrue(kinds.plan_problems("refactor", [tests_zone]))
        self.assertEqual(kinds.plan_problems("refactor", [dict(tests_zone, testsEdit="переименование")]), [])
        self.assertEqual(kinds.plan_problems("refactor", [fix]), [])

    def test_land_problems(self):
        tk = {"id": "01", "repro": False, "testsEdit": None}
        self.assertEqual(kinds.land_problems("task", tk, ["tests/test_a.py"], {"tests/test_a.py"}, None), [])
        self.assertTrue(kinds.land_problems("refactor", dict(tk, baseline={"command": "x"}), ["tests/test_a.py"],
                                            {"tests/test_a.py"}, None))
        self.assertEqual(kinds.land_problems("refactor", dict(tk, baseline={"command": "x"}, testsEdit="why"),
                                             ["tests/test_a.py"], {"tests/test_a.py"}, None), [])
        self.assertTrue(kinds.land_problems("refactor", tk, ["src/a.py"], set(), None))        # нет baseline
        self.assertTrue(kinds.land_problems("bug", dict(tk, repro=True), ["tests/t.py"], set(), None))
        self.assertEqual(kinds.land_problems("bug", dict(tk, repro=True), ["tests/t.py"], set(), {"exit": 1}), [])

    def test_router_ignores_kind(self):
        text = ticket("01", "Х", "R01", "—", ["src/"], 1)
        marked = text.replace("**Волна:** 1", "**Волна:** 1\n**Вид:** воспроизведение\n**Правка тестов:** причина")
        self.assertEqual(model_router.assess_ticket(text), model_router.assess_ticket(marked))
        with open(os.path.join(TOOLS, "model_router.py"), encoding="utf-8") as f:
            self.assertNotIn("kind", f.read().lower().replace("kinds of", ""))


class Repo(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-lc-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        git(self.root, "init", "-q")
        with open(os.path.join(self.root, ".gitignore"), "w") as f:
            f.write(".autopilot/worktrees/\n")
        git(self.root, "config", "user.email", "t@t")
        git(self.root, "config", "user.name", "t")
        os.makedirs(os.path.join(self.root, "src"))
        with open(os.path.join(self.root, "src", "a.py"), "w") as f:
            f.write("1\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "base")
        self.base = git(self.root, "rev-parse", "HEAD").stdout.strip()

    def commit_file(self, rel, text="x\n"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "c " + rel)


class LandCheckUnit(Repo):
    def test_preflight_reports_and_changes_nothing(self):
        self.commit_file("src/b.py")
        self.commit_file("docs/x.md")
        with open(os.path.join(self.root, "src", "dirty.py"), "w") as f:
            f.write("d\n")
        before = (git(self.root, "status", "--porcelain").stdout, git(self.root, "rev-parse", "HEAD").stdout)
        rep = land_check.preflight(self.root, self.base, self.base, ["src/"], "01", {"02": ["src/b.py"], "03": ["web/"]})
        after = (git(self.root, "status", "--porcelain").stdout, git(self.root, "rev-parse", "HEAD").stdout)
        self.assertEqual(before, after)
        self.assertEqual(rep["ahead"], 2)
        self.assertEqual(rep["foreign_files"], ["src/b.py"])
        self.assertEqual([n["ticket"] for n in rep["neighbors"]], ["02"])
        self.assertIsNone(rep["unsupported"])
        text = "\n".join(land_check.problems(rep))
        self.assertIn("src/b.py", text)
        self.assertIn("что делать", text)
        self.assertIn("02", text)

    def test_clean_report_has_no_problems(self):
        self.commit_file("docs/x.md")
        rep = land_check.preflight(self.root, self.base, self.base, ["src/"], "01", {})
        self.assertEqual((rep["foreign_files"], rep["neighbors"], land_check.problems(rep)), ([], [], []))

    def test_missing_start_head_checks_only_neighbors(self):
        self.commit_file("src/b.py")
        rep = land_check.preflight(self.root, None, self.base, ["src/"], "01", {})
        self.assertEqual(rep["foreign_files"], [])

    def test_subfolder_project_is_unsupported_warning_not_refusal(self):
        sub = os.path.join(self.root, "src")
        rep = land_check.preflight(sub, self.base, self.base, ["x/"], "01", {})
        self.assertTrue(rep["unsupported"])
        self.assertIn("не поддержано", rep["unsupported"])
        self.assertEqual(land_check.problems(rep), [])


class WorktreeLand(Repo):
    def test_land_runs_the_same_check_before_cherry_pick(self):
        path = worktrees.create(self.root, "01")["cwd"]
        with open(os.path.join(path, "src", "w.py"), "w") as f:
            f.write("w\n")
        git(path, "add", "-A")
        git(path, "commit", "-qm", "T01")
        self.commit_file("src/a.py", "2\n")                       # чужой коммит в зоне после базы
        head = git(self.root, "rev-parse", "HEAD").stdout.strip()
        with self.assertRaisesRegex(worktrees.WorktreeError, "src/a.py"):
            worktrees.land(self.root, "01", self.base, ["src/"])
        self.assertEqual(git(self.root, "rev-parse", "HEAD").stdout.strip(), head)
        self.assertFalse(os.path.exists(os.path.join(self.root, "src", "w.py")))


class LandBase(Project):
    def setUp(self):
        super().setUp()
        self.put(".autopilot/exit0.py", "raise SystemExit(0)\n")
        self.put(".autopilot/exit1.py", "raise SystemExit(1)\n")

    def plan(self, tickets, *init_args, manifest=MANIFEST):
        self.init(*init_args)
        with open(os.path.join(self.dir, "manifest.md"), "w", encoding="utf-8") as f:
            f.write(manifest)
        for name, text in tickets.items():
            with open(os.path.join(self.dir, "tickets", name), "w", encoding="utf-8") as f:
                f.write(text)
        self.interfaces(GENERATORS)
        self.assertEqual(self.ap("tickets", "--no-serve")[0], 0)
        self.commit_all()

    def land(self, tid, *args):
        return self.ap("ticket", tid, "land", "--message", "T%s: работа" % tid, "--no-serve", *args)

    def start(self, tid):
        code, out = self.ap("ticket", tid, "start", "--no-serve")
        self.assertEqual(code, 0, out)

    def tk(self, tid):
        return next(t for t in self.state()["tickets"] if t["id"] == tid)


T1 = {"01-a.md": ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1)}


class LandPreflight(LandBase):
    def test_start_records_start_head(self):
        self.plan(T1)
        self.start("01")
        self.assertEqual(self.tk("01")["startHead"], self.head())

    def test_clean_land_passes_and_prints_how_far_the_target_moved(self):
        self.plan(T1)
        self.start("01")
        self.put("src/core/a.py", "x = 1\n")
        code, out = self.land("01")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last_files(), ["src/core/a.py"])

    def test_foreign_commit_in_the_zone_refuses_with_a_command(self):
        self.plan(T1)
        self.start("01")
        self.put("src/core/other.py", "y\n")
        self.commit_all("чужой")
        self.put("src/core/a.py", "x = 1\n")
        head = self.head()
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("src/core/other.py", out)
        self.assertIn("что делать", out)
        self.assertEqual(self.head(), head)

    def test_foreign_commit_outside_the_zone_does_not_stop_land(self):
        self.plan(T1)
        self.start("01")
        self.put("docs/n.md", "n\n")
        self.commit_all("чужой вне зоны")
        self.put("src/core/a.py", "x = 1\n")
        self.assertEqual(self.land("01")[0], 0)

    def test_neighbor_in_progress_with_overlapping_zone_refuses(self):
        self.plan(dict(T1, **{"02-b.md": ticket("02", "Соседний", "R02", "—", ["src/"], 1)}))
        self.start("01")
        self.start("02")
        self.put("src/core/a.py", "x = 1\n")
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("02", out)
        self.assertIn("что делать", out)

    def test_bypass_signals_are_printed_without_refusal(self):
        self.plan(T1)
        self.start("01")
        self.put("src/core/test_a.py", "import unittest\n@unittest.skip('later')\ndef t(): pass\n")
        code, out = self.land("01")
        self.assertEqual(code, 0, out)
        self.assertIn("skip", out)

    def test_include_commits_a_new_file_outside_the_zone_and_allow_does_not(self):
        self.plan(T1)
        self.start("01")
        self.put("src/core/a.py", "x = 1\n")
        self.put("docs/adr/x.md", "adr\n")
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("--include", out)
        code, out = self.land("01", "--allow", "docs/adr/x.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last_files(), ["src/core/a.py"])
        self.assertIn("?? docs/", self.git("status", "--porcelain").stdout)

    def test_include_puts_the_file_in_the_commit(self):
        self.plan(T1)
        self.start("01")
        self.put("src/core/a.py", "x = 1\n")
        self.put("docs/adr/x.md", "adr\n")
        code, out = self.land("01", "--include", "docs/adr/x.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last_files(), ["docs/adr/x.md", "src/core/a.py"])


class KindState(LandBase):
    def test_init_kind_and_set_kind(self):
        self.init("--kind", "bug")
        self.assertEqual(self.state()["kind"], "bug")
        self.assertEqual(self.ap("set", "kind=refactor", "--no-serve")[0], 0)
        self.assertEqual(self.state()["kind"], "refactor")
        code, out = self.ap("set", "kind=fast", "--no-serve")
        self.assertEqual(code, 1, out)
        self.assertEqual(self.state()["kind"], "refactor")

    def test_init_with_a_bad_kind_refuses_and_default_is_task(self):
        code, out = self.ap("init", "--slug", "demo", "--kind", "fast", "--no-serve")
        self.assertEqual(code, 1, out)
        self.assertFalse(os.path.exists(os.path.join(self.a, "state.js")))
        self.init()
        self.assertEqual(self.state()["kind"], "task")


BUG = {"01-repro.md": ticket("01", "Упавший тест", "R01", "—", ["tests/"], 1).replace(
           "**Волна:** 1", "**Волна:** 1\n**Вид:** воспроизведение"),
       "02-fix.md": ticket("02", "Фикс", "R02", "—", ["src/"], 1)}


class BugKind(LandBase):
    def setUp(self):
        super().setUp()
        self.plan(BUG, "--kind", "bug")

    def test_redproof_rejects_a_green_command_and_records_a_red_one(self):
        self.start("01")
        code, out = self.ap("ticket", "01", "redproof", "--command", GREEN, "--no-serve")
        self.assertEqual(code, 1, out)
        self.assertIn("не красный", out)
        self.assertNotIn("redproof", self.tk("01"))
        code, out = self.ap("ticket", "01", "redproof", "--command", RED, "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.tk("01")["redproof"]["exit"], 1)

    def test_repro_land_needs_the_proof_and_then_skips_the_full_check(self):
        self.start("01")
        self.put("tests/test_bug.py", "def test_x():\n    assert False\n")
        self.mode("red")                                          # полная проверка красная: воспроизведение её не гоняет
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("redproof", out)
        self.assertEqual(self.ap("ticket", "01", "redproof", "--command", RED, "--no-serve")[0], 0)
        code, out = self.land("01")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.tk("01")["status"], "done")

    def test_by_user_does_not_lift_the_missing_redproof_and_no_commit_is_made(self):
        self.start("01")
        self.put("tests/test_bug.py", "def test_x():\n    assert False\n")
        head = git(self.root, "rev-parse", "HEAD").stdout
        code, out = self.land("01", "--by-user", "разрешаю без красного")
        self.assertEqual(code, 2, out)
        self.assertIn("redproof", out)
        self.assertNotEqual(self.tk("01")["status"], "done")
        self.assertEqual(git(self.root, "rev-parse", "HEAD").stdout, head)

    def test_fix_land_needs_the_repro_done_and_by_user_lifts_it(self):
        self.start("02")
        self.put("src/f.py", "ok = 1\n")
        code, out = self.land("02")
        self.assertEqual(code, 2, out)
        self.assertIn("воспроизвед", out)
        code, out = self.land("02", "--by-user", "пользователь разрешил без воспроизведения")
        self.assertEqual(code, 0, out)

    def test_plan_without_a_repro_ticket_fails_check_plan(self):
        os.remove(os.path.join(self.dir, "tickets", "01-repro.md"))
        self.assertEqual(self.ap("tickets", "--no-serve")[0], 0)
        code, out = self.ap("check-plan", "--no-serve")
        self.assertEqual(code, 2, out)
        self.assertIn("воспроизвед", out)


REF = {"01-r.md": ticket("01", "Перепись", "R01", "—", ["src/", "tests/"], 1)}


class RefactorKind(LandBase):
    def prepare(self, edited):
        text = REF["01-r.md"]
        if edited:
            text = text.replace("**Волна:** 1", "**Волна:** 1\n**Правка тестов:** переименован хелпер")
        self.put("tests/test_old.py", "def test_a():\n    pass\n")
        self.commit_all("old test")
        self.plan({"01-r.md": text}, "--kind", "refactor")

    def test_baseline_needs_a_green_command(self):
        self.prepare(True)
        self.start("01")
        code, out = self.ap("ticket", "01", "baseline", "--command", RED, "--no-serve")
        self.assertEqual(code, 1, out)
        self.assertNotIn("baseline", self.tk("01"))
        self.assertEqual(self.ap("ticket", "01", "baseline", "--command", GREEN, "--no-serve")[0], 0)
        self.assertIn("baseline", self.tk("01"))

    def test_land_without_baseline_refuses_and_by_user_does_not_lift(self):
        self.prepare(True)
        self.start("01")
        self.put("src/a.py", "x = 1\n")
        for extra in ([], ["--by-user", "разрешаю"]):
            code, out = self.land("01", *extra)
            self.assertEqual(code, 2, out)
            self.assertIn("baseline", out)

    def test_editing_an_existing_test_without_the_exception_refuses(self):
        self.prepare(False)
        self.start("01")
        self.assertEqual(self.ap("ticket", "01", "baseline", "--command", GREEN, "--no-serve")[0], 0)
        self.put("tests/test_old.py", "def test_a():\n    assert True\n")
        self.put("src/a.py", "x = 1\n")
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("Правка тестов", out)

    def test_exception_in_the_ticket_file_and_new_tests_pass(self):
        self.prepare(True)
        self.start("01")
        self.assertEqual(self.ap("ticket", "01", "baseline", "--command", GREEN, "--no-serve")[0], 0)
        self.put("tests/test_old.py", "def test_a():\n    assert True\n")
        self.put("tests/test_new.py", "def test_b():\n    pass\n")
        code, out = self.land("01")
        self.assertEqual(code, 0, out)

    def test_new_test_file_alone_is_not_an_edit(self):
        self.prepare(False)
        self.start("01")
        self.assertEqual(self.ap("ticket", "01", "baseline", "--command", GREEN, "--no-serve")[0], 0)
        self.put("tests/test_new.py", "def test_b():\n    pass\n")
        self.assertEqual(self.land("01")[0], 0)

    def test_check_plan_flags_a_tests_zone_without_the_exception(self):
        self.prepare(False)
        code, out = self.ap("check-plan", "--no-serve")
        self.assertEqual(code, 2, out)
        self.assertIn("Правка тестов", out)


class QuickKind(LandBase):
    def test_second_ticket_or_a_fat_manifest_fails_check_plan(self):
        self.plan(dict(T1, **{"02-b.md": ticket("02", "Ещё", "R02", "—", ["web/"], 1)}), "--kind", "quick")
        code, out = self.ap("check-plan", "--no-serve")
        self.assertEqual(code, 2, out)
        self.assertIn("quick", out)
        os.remove(os.path.join(self.dir, "tickets", "02-b.md"))
        self.assertEqual(self.ap("tickets", "--no-serve")[0], 0)
        code, out = self.ap("check-plan", "--no-serve")                 # в манифесте 4 строки при пределе 3
        self.assertIn("манифест", [l for l in out.splitlines() if "quick" in l][0])

    def test_task_kind_changes_nothing(self):
        self.plan(dict(T1, **{"02-b.md": ticket("02", "Ещё", "R02", "—", ["web/"], 1)}))
        code, out = self.ap("check-plan", "--no-serve")
        self.assertNotIn("quick", out)


class Texts(unittest.TestCase):
    def test_kind_phases_exist_and_skill_table_names_them(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
            table = f.read()
        for name in ("kind-bug", "kind-refactor", "kind-quick", "kind-auto"):
            path = os.path.join(SKILL, "phases", name + ".md")
            self.assertTrue(os.path.isfile(path), name)
            self.assertIn("phases/%s.md" % name, table)
        read = lambda n: open(os.path.join(SKILL, "phases", n + ".md"), encoding="utf-8").read()
        self.assertIn("Правка тестов", read("kind-refactor"))
        self.assertIn("подтверд", read("kind-refactor"))
        self.assertIn(str(kinds.QUICK_MAX_REQUIREMENTS), read("kind-quick"))
        self.assertIn("full", read("kind-auto"))
        self.assertIn("semi", read("kind-auto"))


if __name__ == "__main__":
    unittest.main()
