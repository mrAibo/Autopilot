"""Целевая проверка на `ticket NN land`, полная перед ревью (`stage review`) и в `finish` (T02).

Запуск:  python -m unittest discover -s tests -p test_land_targeted.py
"""

import os
import shutil
import tempfile
import unittest

import test_ap
import test_one_command as T

# Один скрипт на обе проверки: метка в argv, режим в `<метка>.mode`, каждый запуск дописывает метку в runs.log.
CHK = r'''import os, sys
here = os.path.dirname(os.path.abspath(__file__))
label = sys.argv[1]
with open(os.path.join(here, "runs.log"), "a") as f:
    f.write(label + "\n")
mode = open(os.path.join(here, label + ".mode")).read().strip()
ran = {"full": 3, "target": 2}[label]
if mode == "green":
    print("Ran %d tests in 0.001s\n\nOK" % ran, file=sys.stderr)
elif mode == "red":
    print("FAIL: test_x (m.C)\nRan %d tests in 0.001s\n\nFAILED (failures=1)" % ran, file=sys.stderr)
    sys.exit(1)
elif mode == "zero":
    print("Ran 0 tests in 0.000s\n\nOK", file=sys.stderr)
'''

FULL_LINE = "Полная проверка: `{py} .autopilot/chk.py full`\n"
INTERFACES = "# Границы\n\n" + FULL_LINE
# в файле таска нельзя путь машины (`ap.py tickets` его отклоняет), поэтому интерпретатор — по имени из PATH
PYNAME = "python" if shutil.which("python") else "python3"
TARGET_LINE = "Целевая проверка: `%s .autopilot/chk.py target`\n" % PYNAME
REPRO = test_ap.ticket("01", "Упавший тест", "R01", "—", ["tests/"], 1).replace(
    "**Волна:** 1", "**Волна:** 1\n**Вид:** воспроизведение")


def load_ap():
    return T.load_ap()


def put(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def runs(root):
    try:
        with open(os.path.join(root, ".autopilot", "runs.log"), encoding="utf-8") as f:
            return f.read().split()
    except OSError:
        return []


class TargetedCommand(unittest.TestCase):
    """`targeted_check_command(state, id)` читает строку из файла таска."""

    def setUp(self):
        self.a = tempfile.mkdtemp(prefix="ap-tc-")
        self.addCleanup(shutil.rmtree, self.a, ignore_errors=True)
        self.ap = load_ap()
        self.ap.A = self.a
        self.state = {"dir": "2026-01-01-demo--wip"}
        os.makedirs(os.path.join(self.a, self.state["dir"], "tickets"))

    def ticket(self, name, body):
        put(self.a, os.path.join(self.state["dir"], "tickets", name), "# 01 — t\n\n" + body)

    def test_the_line_is_read_with_every_allowed_prefix(self):
        for line in ("Целевая проверка: `cmd a --b`", "* Целевая проверка: `cmd a --b`", "- Целевая проверка: `cmd a --b`",
                     "> Целевая проверка: `cmd a --b`", "**Целевая проверка:** `cmd a --b`",
                     "- **Целевая проверка**: `cmd a --b`", "  Целевая проверка:   `cmd a --b`  "):
            with self.subTest(line=line):
                self.ticket("01-a.md", "**Зона:** `x/`\n" + line + "\n")
                self.assertEqual(self.ap.targeted_check_command(self.state, "01"), "cmd a --b")

    def test_no_line_a_foreign_ticket_or_a_missing_file_is_none(self):
        self.ticket("01-a.md", "**Зона:** `x/`\nПроверка: `cmd`\nЦелевая проверка без команды\n")
        self.ticket("02-b.md", "Целевая проверка: `other`\n")
        self.assertIsNone(self.ap.targeted_check_command(self.state, "01"))
        self.assertEqual(self.ap.targeted_check_command(self.state, "02"), "other")
        self.assertIsNone(self.ap.targeted_check_command(self.state, "03"))


class LandTargeted(T.Project):
    def plan(self, tickets=None, *init_args, target=True, interfaces=INTERFACES):
        self.init(*init_args)
        with open(os.path.join(self.dir, "manifest.md"), "w", encoding="utf-8") as f:
            f.write(test_ap.MANIFEST)
        text = test_ap.ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1)
        tickets = tickets or {"01-karkas.md": text + ("\n" + TARGET_LINE if target else "")}
        for name, body in tickets.items():
            with open(os.path.join(self.dir, "tickets", name), "w", encoding="utf-8") as f:
                f.write(body)
        self.interfaces(interfaces)
        self.put(".autopilot/chk.py", CHK)
        self.put(".autopilot/full.mode", "green")
        self.put(".autopilot/target.mode", "green")
        code, out = self.ap("tickets", "--no-serve")
        self.assertEqual(code, 0, out)
        self.commit_all()

    def land(self, tid="01"):
        return self.ap("ticket", tid, "land", "--message", "T%s: работа" % tid, "--no-serve")

    def work(self, tid="01", path="src/core/a.py"):
        self.assertEqual(self.ap("ticket", tid, "start", "--no-serve")[0], 0)
        self.put(path, "x = 1\n")

    def test_a_targeted_line_runs_instead_of_the_full_check_and_marks_the_land(self):
        self.plan()
        self.work()
        before = self.commits()
        code, out = self.land()
        self.assertEqual(code, 0, out)
        self.assertEqual(runs(self.root), ["target"])
        self.assertEqual(self.commits(), before + 1)
        state = self.state()
        self.assertEqual(state["targetedLands"], ["01"])
        self.assertEqual((state["tickets"][0]["status"], state["tickets"][0]["tests"]), ("done", {"passed": 2, "failed": 0}))

    def test_no_line_keeps_the_old_path_and_the_list_does_not_grow(self):
        self.plan(target=False)
        self.work()
        code, out = self.land()
        self.assertEqual(code, 0, out)
        self.assertEqual(runs(self.root), ["full"])
        self.assertFalse(self.state().get("targetedLands"))
        self.assertEqual(self.state()["tickets"][0]["tests"], {"passed": 3, "failed": 0})

    def test_a_red_targeted_check_does_not_land_and_names_the_failed_test(self):
        self.plan()
        self.work()
        self.put(".autopilot/target.mode", "red")
        head = self.head()
        code, out = self.land()
        self.assertEqual(code, 2, out)
        self.assertIn("красная", out)
        self.assertIn("  - FAIL: test_x (m.C)", out)
        self.assertEqual(self.head(), head)
        self.assertNotEqual(self.state()["tickets"][0]["status"], "done")
        self.assertFalse(self.state().get("targetedLands"))
        self.assertEqual(runs(self.root), ["target"])

    def test_zero_targeted_tests_is_red_too(self):
        self.plan()
        self.work()
        self.put(".autopilot/target.mode", "zero")
        head = self.head()
        code, out = self.land()
        self.assertEqual(code, 2, out)
        self.assertIn("ноль тестов", out)
        self.assertEqual(self.head(), head)
        self.assertFalse(self.state().get("targetedLands"))

    def test_isolated_run_is_untouched_by_the_targeted_line(self):
        self.plan(None, "--isolated-tickets")
        self.put("src/core/a.py", "x = 1\n")
        head = self.head()
        code, out = self.land()
        self.assertEqual(code, 2, out)
        self.assertIn("worktree 01 verify", out)
        self.assertEqual((self.head(), runs(self.root)), (head, []))
        self.assertFalse(self.state().get("targetedLands"))

    def test_a_repro_land_runs_nothing_and_is_not_marked(self):
        self.plan({"01-repro.md": REPRO + "\n" + TARGET_LINE,
                   "02-fix.md": test_ap.ticket("02", "Фикс", "R02", "—", ["src/"], 1)}, "--kind", "bug")
        self.put(".autopilot/exit1.py", "raise SystemExit(1)\n")
        self.work("01", "tests/test_bug.py")
        self.assertEqual(self.ap("ticket", "01", "redproof", "--command", T.PY + " .autopilot/exit1.py", "--no-serve")[0], 0)
        code, out = self.land("01")
        self.assertEqual(code, 0, out)
        self.assertEqual(runs(self.root), [])
        self.assertFalse(self.state().get("targetedLands"))


class FullGates(unittest.TestCase):
    """`stage review` и `finish` гоняют полную проверку, пока в `targetedLands` есть таски."""

    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)

    def prepare(self, mode="green", lands=("01",), interfaces=INTERFACES, plan=False):
        h = self.h
        if plan:
            h.ready_to_finish()
        else:
            h.init()
        put(h.a, "chk.py", CHK)
        put(h.a, "full.mode", mode)
        h.write("interfaces.md", interfaces.format(py=T.PY))
        if lands:
            h.edit_state(targetedLands=list(lands))
        if plan:
            h.git("add", "-A")
            h.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "interfaces")

    def test_review_stops_on_a_red_full_check_and_records_no_transition(self):
        self.prepare("red")
        code, out = self.h.ap("stage", "review")
        self.assertNotEqual(code, 0, out)
        self.assertIn("  - FAIL: test_x (m.C)", out)
        self.assertEqual(self.h.stage("review")["status"], "pending")
        self.assertEqual(self.h.state()["targetedLands"], ["01"])

    def test_review_with_zero_full_tests_stops(self):
        self.prepare("zero")
        code, out = self.h.ap("stage", "review")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self.h.stage("review")["status"], "pending")

    def test_review_on_a_green_full_check_moves_on_records_tests_and_clears_the_list(self):
        self.prepare("green")
        code, out = self.h.ap("stage", "review")
        self.assertEqual(code, 0, out)
        state = self.h.state()
        self.assertEqual(self.h.stage("review")["status"], "active")
        self.assertEqual((state["tests"], state["targetedLands"]), ({"passed": 3, "failed": 0}, []))
        self.assertEqual(runs(self.h.root), ["full"])

    def test_review_with_an_empty_list_runs_nothing(self):
        self.prepare("red", lands=())
        code, out = self.h.ap("stage", "review")
        self.assertEqual(code, 0, out)
        self.assertEqual(runs(self.h.root), [])
        self.assertEqual(self.h.stage("review")["status"], "active")

    def test_review_without_a_full_check_line_warns_and_runs_nothing(self):
        self.prepare("red", interfaces="# Границы\n\nПроверка: что-нибудь\n")
        code, out = self.h.ap("stage", "review")
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"(?m)^[ ]*! .*Полная проверка")
        self.assertEqual(runs(self.h.root), [])
        self.assertEqual(self.h.stage("review")["status"], "active")

    def test_finish_stops_on_a_red_full_check_and_leaves_the_run_open(self):
        self.prepare("red", lands=("02",), plan=True)
        code, out = self.h.ap("finish", "--result", "готово")
        self.assertNotEqual(code, 0, out)
        self.assertIn("  - FAIL: test_x (m.C)", out)
        state = self.h.state()
        self.assertFalse(state.get("finishedAt"))
        self.assertEqual(state["targetedLands"], ["02"])

    def test_finish_on_a_green_full_check_lands_and_clears_the_list(self):
        self.prepare("green", lands=("02",), plan=True)
        code, out = self.h.ap("finish", "--result", "готово")
        self.assertEqual(code, 0, out)
        state = self.h.state()
        self.assertTrue(state["finishedAt"])
        self.assertEqual((state["tests"], state["targetedLands"]), ({"passed": 3, "failed": 0}, []))

    def test_finish_with_an_empty_list_runs_nothing(self):
        self.prepare("red", lands=(), plan=True)
        code, out = self.h.ap("finish", "--result", "готово")
        self.assertEqual(code, 0, out)
        self.assertEqual(runs(self.h.root), [])

    def test_finish_without_a_full_check_line_warns_and_still_lands(self):
        self.prepare("red", lands=("02",), plan=True, interfaces="# Границы\n")
        code, out = self.h.ap("finish", "--result", "готово")
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"(?m)^[ ]*! .*Полная проверка")
        self.assertEqual(runs(self.h.root), [])


if __name__ == "__main__":
    unittest.main()
