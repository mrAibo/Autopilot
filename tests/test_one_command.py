"""Тесты команд «одной командой»: `chore`, `ticket NN land`, `bootstrap`, `doctor`, второй круг `blind`.

Каждый тест поднимает временный git-репозиторий и зовёт ap.py подпроцессом, как оркестратор.
Запуск одного файла:  python -m unittest discover -s tests -p test_one_command.py
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_ap import MANIFEST, read, ticket

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(HERE), "skills", "autopilot")
TOOLS = os.environ.get("AP_TEST_TOOLS") or os.path.join(SKILL, "tools")   # AP_TEST_TOOLS — для красной проверки на старом коде
PY = '"%s"' % sys.executable
NL = chr(10)

GENERATORS = """# Границы

Полная проверка: `{py} .autopilot/check.py`

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| ok | `{py} .autopilot/gen.py out.txt` | `out.txt` |
| stray | `{py} .autopilot/gen.py out.txt stray.txt` | `out.txt` |
| broken | `{py} .autopilot/gen.py out.txt --exit 3` | `out.txt` |
| same | `{py} .autopilot/gen.py same.txt` | `same.txt`, `other.txt` |
"""

GEN = """import sys
args = sys.argv[1:]
code = int(args[args.index("--exit") + 1]) if "--exit" in args else 0
for name in [a for a in args if a.endswith(".txt")]:
    with open(name, "w") as f:
        f.write("gen\\n")
sys.exit(code)
"""

CHECK = """import os, sys
mode = open(os.path.join(os.path.dirname(__file__), "check.mode")).read().strip()
if mode == "green":
    print("Ran 3 tests in 0.001s\\n\\nOK", file=sys.stderr)
elif mode == "red":
    print("Ran 3 tests in 0.001s\\n\\nFAILED (failures=1)", file=sys.stderr)
    sys.exit(1)
elif mode == "zero":
    print("Ran 0 tests in 0.000s\\n\\nOK", file=sys.stderr)
else:
    print("all fine")
"""


def load_ap():
    spec = importlib.util.spec_from_file_location("ap_under_test", os.path.join(TOOLS, "ap.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Project(unittest.TestCase):
    """Временный git-проект с `.autopilot/` из инструментов навыка."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-one-")
        self.home = tempfile.mkdtemp(prefix="ap-home-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.git("commit", "-q", "--allow-empty", "-m", "init")
        self.a = os.path.join(self.root, ".autopilot")
        os.makedirs(self.a)
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        shutil.copy(os.path.join(SKILL, "phases", "dashboard-template.html"), os.path.join(self.a, "dashboard.html"))
        self.put(".autopilot/gen.py", GEN)
        self.put(".autopilot/check.py", CHECK)
        self.mode("green")

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True, encoding="utf-8")

    def put(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def mode(self, word):
        self.put(".autopilot/check.mode", word)

    def ap(self, *args, script=None):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1", AUTOPILOT_HOME=self.home,
                   CLAUDE_CONFIG_DIR=os.path.join(self.home, "claude"))
        r = subprocess.run([sys.executable, script or os.path.join(self.a, "ap.py")] + list(args),
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=self.root)
        return r.returncode, r.stdout + r.stderr

    def state(self):
        return json.loads(read(os.path.join(self.a, "state.js")).split("=", 1)[1])

    def init(self, *extra):
        code, out = self.ap("init", "--slug", "demo", "--title", "Демо", "--skill-dir", os.path.dirname(TOOLS), "--no-serve", *extra)
        self.assertEqual(code, 0, out)
        self.dir = os.path.join(self.a, self.state()["dir"])

    def interfaces(self, text):
        with open(os.path.join(self.dir, "interfaces.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text.format(py=PY))

    def commit_all(self, message="setup"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    def commits(self):
        return int(self.git("rev-list", "--count", "HEAD").stdout.strip())

    def last_files(self):
        return sorted(self.git("show", "--name-only", "--pretty=format:", "HEAD").stdout.split())


class Chore(Project):
    def setUp(self):
        super().setUp()
        self.init()
        self.interfaces(GENERATORS)
        self.commit_all()

    def chore(self, name):
        return self.ap("chore", name, "--no-serve")

    def test_declared_command_commits_only_its_files_with_the_run_trailer(self):
        self.put("unrelated.txt", "dirty before the run\n")        # грязный файл до запуска: не «лишний» и не в коммите
        before = self.commits()
        code, out = self.chore("ok")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.commits(), before + 1)
        self.assertEqual(self.last_files(), ["out.txt"])
        self.assertIn("Autopilot-Run: " + self.state()["dir"].removesuffix("--wip"),
                      self.git("log", "-1", "--format=%B").stdout)
        self.assertIn("?? unrelated.txt", self.git("status", "--porcelain").stdout)

    def test_an_extra_changed_file_refuses_and_commits_nothing(self):
        head = self.head()
        code, out = self.chore("stray")
        self.assertEqual(code, 2, out)
        self.assertIn("stray.txt", out)
        self.assertEqual(self.head(), head)
        self.assertNotIn("out.txt", self.git("show", "--name-only", "--pretty=format:", "HEAD").stdout)

    def test_a_dirty_generator_file_is_named_with_the_action_and_left_untouched(self):
        self.put("out.txt", "user edit\n")
        head = self.head()
        code, out = self.chore("ok")
        self.assertEqual(code, 2, out)
        self.assertIn("out.txt", out)
        self.assertIn("закоммить или отмени правки", out)
        self.assertEqual(self.head(), head)
        self.assertEqual(read(os.path.join(self.root, "out.txt")), "user edit\n")

    def test_an_undeclared_name_refuses(self):
        head = self.head()
        code, out = self.chore("nope")
        self.assertEqual(code, 2, out)
        self.assertIn("ok", out)                                   # назвал, какие объявлены
        self.assertEqual(self.head(), head)

    def test_a_nonzero_exit_refuses_without_a_commit(self):
        head = self.head()
        code, out = self.chore("broken")
        self.assertEqual(code, 2, out)
        self.assertIn("код 3", out)
        self.assertEqual(self.head(), head)

    def test_unchanged_declared_files_are_nothing_to_commit(self):
        self.put("same.txt", "gen\n")
        self.put("other.txt", "x\n")
        self.commit_all("same")
        head = self.head()
        code, out = self.chore("same")
        self.assertEqual(code, 0, out)
        self.assertIn("нечего коммитить", out)
        self.assertEqual(self.head(), head)


class Land(Project):
    def plan(self, *init_args, interfaces=GENERATORS):
        self.init(*init_args)
        with open(os.path.join(self.dir, "manifest.md"), "w", encoding="utf-8") as f:
            f.write(MANIFEST)
        with open(os.path.join(self.dir, "tickets", "01-karkas.md"), "w", encoding="utf-8") as f:
            f.write(ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1))
        self.interfaces(interfaces)
        self.assertEqual(self.ap("tickets", "--no-serve")[0], 0)
        self.commit_all()

    def land(self, *args):
        return self.ap("ticket", "01", "land", "--message", "T01: каркас", "--no-serve", *args)

    def work(self):
        self.assertEqual(self.ap("ticket", "01", "start", "--no-serve")[0], 0)
        self.put("src/core/a.py", "x = 1\n")

    def refused(self, out, code, head, words, lines=3):
        self.assertEqual(code, 2, out)
        self.assertLessEqual(len(out.strip().splitlines()), lines, out)
        self.assertIn(words, out)
        self.assertEqual(self.head(), head)
        self.assertNotEqual(self.state()["tickets"][0]["status"], "done")

    def test_green_path_commits_the_zone_and_marks_the_ticket_done(self):
        self.plan()
        self.work()
        code, out = self.land("--requirements", "R01,R05")
        self.assertEqual(code, 0, out)
        self.assertLessEqual(len(out.strip().splitlines()), 5, out)
        self.assertEqual(self.last_files(), ["src/core/a.py"])
        body = self.git("log", "-1", "--format=%B").stdout
        self.assertIn("T01: каркас", body)
        self.assertIn("Autopilot-Run: " + self.state()["dir"].removesuffix("--wip"), body)
        self.assertIn("Requirements: R01, R05", body)
        tk = self.state()["tickets"][0]
        self.assertEqual((tk["status"], tk["tests"], tk["commit"]), ("done", {"passed": 3, "failed": 0}, self.head()[:7]))

    def test_zone_comes_from_the_ticket_and_an_explicit_zone_wins(self):
        self.plan()
        self.work()
        self.put("docs/x.md", "x\n")
        code, out = self.land("--zone", "docs/,src/core/a.py")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.last_files(), ["docs/x.md", "src/core/a.py"])

    def test_a_file_outside_the_zone_stops_before_anything_runs(self):
        self.plan()
        self.work()
        self.put("src/other.py", "y = 2\n")
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "src/other.py")
        self.assertIn("вне зоны", out)

    def test_a_red_check_stops_without_a_commit(self):
        self.plan()
        self.work()
        self.mode("red")
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "красная", lines=5)

    def test_zero_tests_is_red(self):
        self.plan()
        self.work()
        self.mode("zero")
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "ноль тестов")

    def test_unrecognised_check_output_is_red(self):
        self.plan()
        self.work()
        self.mode("quiet")
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "не смог посчитать тесты")

    def test_no_full_check_line_is_a_refusal(self):
        self.plan(interfaces="# Границы\n\nПроверка: что-нибудь\n")
        self.work()
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "Полная проверка")

    def test_an_empty_zone_is_red(self):
        self.plan()
        self.assertEqual(self.ap("ticket", "01", "start", "--no-serve")[0], 0)
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "нечего коммитить")

    def test_isolated_run_refuses_with_the_worktree_hint_and_done_still_works(self):
        self.plan("--isolated-tickets")
        self.put("src/core/a.py", "x = 1\n")
        head = self.head()
        code, out = self.land()
        self.refused(out, code, head, "worktree 01 verify")
        code, out = self.ap("ticket", "01", "done", "--tests", "3/0", "--no-serve")
        self.assertNotEqual(code, 0, out)                          # прежний путь отвечает своим текстом
        self.assertIn("worktree", out)


class CountTests(unittest.TestCase):
    def test_unittest_pytest_and_cargo_outputs(self):
        ap = load_ap()
        self.assertEqual(ap.count_tests("Ran 987 tests in 5.0s\n\nOK (skipped=5)\n"), (982, 0))
        self.assertEqual(ap.count_tests("Ran 10 tests in 1s\n\nFAILED (failures=2, errors=1)\n"), (7, 3))
        self.assertEqual(ap.count_tests("===== 2 failed, 31 passed, 1 skipped in 3.20s =====\n"), (31, 2))
        self.assertEqual(ap.count_tests("34 passed in 0.5s\n"), (34, 0))
        self.assertEqual(ap.count_tests("test result: ok. 5 passed; 0 failed; 0 ignored\n"
                                        "test result: FAILED. 2 passed; 1 failed; 0 ignored\n"), (7, 1))
        self.assertIsNone(ap.count_tests("всё хорошо\n"))


class Bootstrap(Project):
    def fake_skill(self):
        base = tempfile.mkdtemp(prefix="ap-skill-")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        shutil.copytree(TOOLS, os.path.join(base, "tools"), ignore=shutil.ignore_patterns("__pycache__", "*.lock"))
        os.makedirs(os.path.join(base, "phases"))
        shutil.copy(os.path.join(SKILL, "SKILL.md"), base)
        shutil.copy(os.path.join(SKILL, "phases", "dashboard-template.html"), os.path.join(base, "phases"))
        return base

    def boot(self, skill, project):
        return self.ap("bootstrap", "--project", project, script=os.path.join(skill, "tools", "ap.py"))

    def setUp(self):
        super().setUp()
        shutil.rmtree(self.a)                                      # здесь проект чистый, без .autopilot/
        self.skill = self.fake_skill()

    def snapshot(self):
        return {n: (read(os.path.join(self.a, n)) if n.endswith((".py", ".html")) else "link",
                    os.path.getmtime(os.path.join(self.a, n))) for n in sorted(os.listdir(self.a))}

    def test_clean_folder_gets_tools_dashboard_index_and_prints_skill_dir(self):
        code, out = self.boot(self.skill, self.root)
        self.assertEqual(code, 0, out)
        self.assertIn("skillDir = " + self.skill, out)
        names = {n for n in os.listdir(os.path.join(self.skill, "tools")) if n.endswith(".py")}
        self.assertTrue(names <= set(os.listdir(self.a)))
        for name in ("dashboard.html", "index.html"):
            self.assertTrue(os.path.lexists(os.path.join(self.a, name)), name)
        self.assertFalse(os.path.exists(os.path.join(self.skill, "tools", "state.lock")))

    def test_second_run_changes_nothing(self):
        self.boot(self.skill, self.root)
        before = self.snapshot()
        code, out = self.boot(self.skill, self.root)
        self.assertEqual(code, 0, out)
        self.assertIn("уже на месте", out)
        self.assertEqual(self.snapshot(), before)

    def test_a_project_with_state_gets_the_dashboard_through_dashboard_upgrade(self):
        os.makedirs(self.a)
        shutil.copy(os.path.join(SKILL, "phases", "dashboard-template.html"), os.path.join(self.a, "dashboard.html"))
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        self.init()
        template = os.path.join(self.skill, "phases", "dashboard-template.html")
        with open(template, "a", encoding="utf-8") as f:
            f.write("\n<!-- bootstrap-marker -->\n")
        code, out = self.boot(self.skill, self.root)
        self.assertEqual(code, 0, out)
        page = read(os.path.join(self.a, "dashboard.html"))
        self.assertIn("bootstrap-marker", page)
        self.assertIn("window.STATE=", page.replace(" ", ""))      # снимок прогона не затёрт

    def test_upgrade_tools_delivers_a_new_skill_file(self):
        os.makedirs(self.a)
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        self.init()
        with open(os.path.join(self.skill, "tools", "brand_new_tool.py"), "w", encoding="utf-8") as f:
            f.write("X = 1\n")
        state = self.state()
        state["skillDir"] = self.skill
        with open(os.path.join(self.a, "state.js"), "w", encoding="utf-8") as f:
            f.write("window.STATE = " + json.dumps(state))
        code, out = self.ap("upgrade-tools", "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("brand_new_tool.py", out)
        self.assertTrue(os.path.isfile(os.path.join(self.a, "brand_new_tool.py")))

    def test_a_signed_run_refuses_a_foreign_skill_dir(self):
        os.makedirs(self.a)
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        code, out = self.ap("init", "--slug", "demo", "--title", "Демо", "--skill-dir", self.skill, "--strict-routing", "--no-serve")
        self.assertEqual(code, 0, out)
        other = self.fake_skill()
        with open(os.path.join(other, "tools", "retry_policy.py"), "a", encoding="utf-8") as f:
            f.write("\n# чужая версия\n")
        before = read(os.path.join(self.a, "retry_policy.py"))
        code, out = self.boot(other, self.root)
        self.assertNotEqual(code, 0, out)
        self.assertIn("skillDir", out)
        self.assertEqual(read(os.path.join(self.a, "retry_policy.py")), before)
        self.assertEqual(self.boot(self.skill, self.root)[0], 0)   # зафиксированный при init каталог работает

    def test_a_ticket_in_work_refuses(self):
        os.makedirs(self.a)
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        self.init()
        state = self.state()
        state["tickets"] = [{"id": "01", "status": "in-progress"}]
        with open(os.path.join(self.a, "state.js"), "w", encoding="utf-8") as f:
            f.write("window.STATE = " + json.dumps(state))
        code, out = self.boot(self.skill, self.root)
        self.assertNotEqual(code, 0, out)
        self.assertIn("в работе", out)


class Doctor(Project):
    def setUp(self):
        super().setUp()
        shutil.rmtree(self.a)
        self.put(".gitignore", ".autopilot/worktrees/\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "ignore")
        self.skill = tempfile.mkdtemp(prefix="ap-skill-")
        self.addCleanup(shutil.rmtree, self.skill, ignore_errors=True)
        shutil.copytree(TOOLS, os.path.join(self.skill, "tools"), ignore=shutil.ignore_patterns("__pycache__", "*.lock"))

    def doctor(self, *args):
        return self.ap("doctor", *args, script=os.path.join(self.skill, "tools", "ap.py"))

    def test_everything_green_is_four_lines_and_code_zero(self):
        code, out = self.doctor("--text", "2.1.320")
        self.assertEqual(code, 0, out)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 5, out)
        for word in ("git: запись разрешена", "Claude Code 2.1.320", "advisorModel: не задан", "repo_doctor: готов"):
            self.assertIn(word, out)
        self.assertFalse(os.path.exists(os.path.join(self.skill, "tools", "state.lock")))

    def test_a_git_refusal_is_code_two_and_the_other_checks_still_print(self):
        open(os.path.join(self.root, ".git", "index.lock"), "w").close()
        code, out = self.doctor("--text", "2.1.320")
        self.assertEqual(code, 2, out)
        self.assertIn("index.lock", out)
        self.assertIn("advisorModel", out)
        self.assertIn("repo_doctor", out)

    def test_a_claude_version_below_the_minimum_is_code_two(self):
        code, out = self.doctor("--text", "2.1.100")
        self.assertEqual(code, 2, out)
        self.assertIn("ниже минимума", out)

    def test_an_unreadable_version_is_a_line_not_a_refusal(self):
        code, out = self.doctor("--text", "что-то непонятное")
        self.assertEqual(code, 0, out)
        self.assertIn("не определена", out)

    def test_advisor_model_and_repo_blockers_are_lines_with_code_zero(self):
        self.put(".claude/settings.json", json.dumps({"advisorModel": "x"}))
        code, out = self.doctor("--text", "2.1.320")
        self.assertEqual(code, 0, out)
        self.assertIn("advisorModel: задан в", out)
        self.assertIn("CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1", out)
        self.assertIn("source-has-uncommitted-changes", out)


class SecondBlindRound(Project):
    def setUp(self):
        super().setUp()
        self.init()

    def blind(self, *args):
        return self.ap("blind", *args, "--no-serve")

    def test_round_two_merges_with_round_one(self):
        self.assertEqual(self.blind("checked=4", "matched=2", "--mismatch", "R01 — нет", "--mismatch", "R02 — частично")[0], 0)
        code, out = self.blind("checked=3", "matched=2", "--mismatch", "R02 — частично")
        self.assertEqual(code, 0, out)
        s = self.state()
        self.assertEqual((s["blind"]["checked"], s["blind"]["matched"], s["blind"]["mismatches"]),
                         (4, 3, ["R02 — частично"]))
        self.assertEqual([(r["checked"], r["matched"]) for r in s["blind"]["rounds"]], [(4, 2), (3, 2)])
        self.assertEqual(s["blindRounds"], 2)
        self.assertFalse(s["gates"]["G4"]["ok"])

    def test_a_clean_round_two_passes_g4_with_round_one_checked(self):
        self.blind("checked=4", "matched=3", "--mismatch", "R01 — нет")
        code, out = self.blind("checked=1", "matched=1")
        self.assertEqual(code, 0, out)
        s = self.state()
        self.assertEqual((s["blind"]["checked"], s["blind"]["matched"], s["blind"]["mismatches"]), (4, 4, []))
        self.assertTrue(s["gates"]["G4"]["ok"])

    def test_the_main_scenario_not_coming_up_is_accepted_as_a_new_mismatch(self):
        self.blind("checked=4", "matched=4")
        code, out = self.blind("checked=1", "matched=0", "--mismatch", "основной сценарий не поднялся")
        self.assertEqual(code, 0, out)
        s = self.state()
        self.assertEqual((s["blind"]["checked"], s["blind"]["matched"], s["blind"]["mismatches"]),
                         (4, 3, ["основной сценарий не поднялся"]))
        self.assertFalse(s["gates"]["G4"]["ok"])

    def test_round_two_checking_more_than_the_mismatches_plus_one_is_refused_without_a_write(self):
        self.blind("checked=4", "matched=3", "--mismatch", "R01 — нет")
        before = read(os.path.join(self.a, "state.js"))
        code, out = self.blind("checked=3", "matched=3")
        self.assertNotEqual(code, 0, out)
        self.assertIn("не больше 2", out)
        self.assertEqual(read(os.path.join(self.a, "state.js")), before)

    def test_a_third_round_is_still_refused(self):
        self.blind("checked=4", "matched=3", "--mismatch", "R01 — нет")
        self.blind("checked=1", "matched=1")
        before = read(os.path.join(self.a, "state.js"))
        code, out = self.blind("checked=1", "matched=1")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(read(os.path.join(self.a, "state.js")), before)


class Texts(unittest.TestCase):
    """Тексты навыка и документы называют новые команды."""

    def phase(self, name):
        with open(os.path.join(SKILL, "phases", name), encoding="utf-8") as f:
            return f.read()

    def test_the_plan_declares_the_full_check_line_and_the_generators_table(self):
        text = self.phase("4-plan.md")
        for needle in ("Полная проверка", "Команды-генераторы", "Имя | Команда | Файлы", "ap.py chore"):
            self.assertIn(needle, text)

    def test_rule_five_got_exactly_one_chore_clarification_and_the_new_calls_are_allowed(self):
        text = read(os.path.join(SKILL, "SKILL.md"))
        rule = next(x for x in text.splitlines() if x.startswith("5. **The orchestrator does not write"))
        self.assertEqual(rule.count("ap.py chore"), 1)
        self.assertIn("not writing code", rule)
        head = next(x for x in text.splitlines() if x.startswith("allowed-tools:"))
        for word in ("bootstrap", "doctor"):
            self.assertNotIn("tools/ap.py* " + word, head)   # путь навыка не закрепить без свободной «*»

    def test_after_each_ticket_is_rewritten_around_land_and_is_shorter(self):
        text = self.phase("5-subagents.md")
        section = text[text.index("## After each ticket"):text.index("## When the build is over")]
        self.assertIn("ticket 03 land", section)
        for needle in ("INTERFACES", "interfaces.md", "debt.placeholders", "debt.emptyEnv", "One plain line"):
            self.assertIn(needle, section)
        self.assertLess(len(text.encode("utf-8")), 14711)        # размер файла до этого таска

    def test_phase_zero_installs_with_bootstrap_and_preflight_names_doctor(self):
        instruments = self.phase("0-instruments.md")
        self.assertIn('tools/ap.py" bootstrap --project', instruments)
        self.assertNotIn('cp "${TPL', instruments)
        for command in ("chore <name>", "ticket 02 land", "bootstrap --project .", 'ap.py" doctor'):
            self.assertIn(command, instruments)
        preflight = self.phase("0-preflight.md")
        self.assertIn('ap.py" doctor', preflight)
        for word in ("advisorModel", "CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1", "ap.py claude-version"):
            self.assertIn(word, preflight)

    def test_final_phase_holds_the_second_round_request(self):
        text = self.phase("8-final.md")
        part = text[text.index("**Round 2 asks only about the mismatches.**"):]
        part = part[:part.index("Record it in one call")]
        for needle in ("whole", "«частично» or «нет»", "does not see `spec.md`", "новый" + NL + "> клон", "основной сценарий один раз"):
            self.assertIn(needle, part)

    def test_ap_py_docstring_lists_the_new_commands_and_the_r05_decision_is_written(self):
        head = read(os.path.join(TOOLS, "ap.py")).split('"""', 2)[1]
        for needle in ("ap.py chore", "ticket 03 land", "bootstrap --project", 'ap.py" doctor'):
            self.assertIn(needle, head)
        doc = read(os.path.join(os.path.dirname(HERE), "docs", "autopilot", "measuring-cost.md"))
        self.assertIn("Решение по R05: три шага и больше", doc)


if __name__ == "__main__":
    unittest.main()
