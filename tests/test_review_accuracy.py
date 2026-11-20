"""T01: точность приёмки и ревью — plan-fact, чек-лист, второй проход, agent-for в обычном прогоне."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(HERE), "skills", "autopilot")
TOOLS = os.path.join(SKILL, "tools")
sys.path.insert(0, TOOLS)
import plan_items  # noqa: E402
import review_checks  # noqa: E402

TICKET = ("# 01 — Первый\n\n**Требования:** R01\n**Зависит от:** —\n**Зона:** `src/`\n**Волна:** 1\n"
          "**Ревью:** нет\n**Модель:** обычная\n**Класс:** механический\n**Риск:** обычный\n"
          "**Причина класса:** типовая задача\n\n## Что должно заработать\n\n- не пункт плана\n\n"
          "## Критерии приёмки\n\n- [ ] первое\n- [x] второе\n\n- третье\n\n## Другое\n\n- не пункт\n")
MANIFEST = ("# Манифест требований\n\n| ID | Из брифа (дословно) | Статус | Основание | Где |\n"
            "|----|---------------------|--------|-----------|-----|\n| R01 | «заявки» | in-spec | — | spec |\n")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class Units(unittest.TestCase):
    def test_parse_items_reads_the_criteria_section_only(self):
        self.assertEqual(plan_items.parse_items(TICKET), ["первое", "второе", "третье"])

    def test_parse_items_heading_variants_and_no_section(self):
        self.assertEqual(plan_items.parse_items("## Acceptance criteria\n- a\n"), ["a"])
        self.assertEqual(plan_items.parse_items("### Приёмка\n* b\n"), ["b"])
        self.assertEqual(plan_items.parse_items("# T\n\n## Что должно заработать\n- x\n"), [])

    def test_parse_items_ignores_a_level_one_title_with_the_keyword(self):
        text = "# 01 — Точность приёмки и ревью\n\n## Что должно заработать\n- x\n\n## Критерии приёмки\n- [ ] a\n- [ ] b\n"
        self.assertEqual(plan_items.parse_items(text), ["a", "b"])

    def test_build_plan_fact_needs_evidence(self):
        fact = plan_items.build_plan_fact(
            {"02": ["a", "b", "c"]},
            [{"id": "T02.1", "status": "сделано", "evidence": "f.py:3"},
             {"id": "T02.2", "status": "сделано", "evidence": ""},
             {"id": "T02.3", "status": "частично", "evidence": "g.py"}])
        self.assertEqual([i["status"] for i in fact["items"]], ["сделано", "не сделано", "частично"])
        self.assertEqual((fact["done"], fact["total"]), (1, 3))

    def test_fix_ticket_verdicts(self):
        self.assertEqual(plan_items.parse_verdict("F1.2 | сделано | x")["id"], "F1.2")
        self.assertEqual(plan_items.parse_verdict("T02.1 | сделано | x")["id"], "T02.1")
        for bad in ("X1.1 | сделано | x", "1.1 | сделано | x", "F.1 | сделано | x", "FX1.1 | сделано | x"):
            self.assertIsNone(plan_items.parse_verdict(bad), bad)
        fact = plan_items.build_plan_fact({"F1": ["a"]}, [{"id": "F1.1", "status": "сделано", "evidence": "f.py"}])
        self.assertEqual((fact["items"][0]["id"], fact["done"]), ("F1.1", 1))

    def test_missing_checklist(self):
        full = "\n".join("- %s: нет проблем" % p for p in review_checks.CHECKLIST)
        self.assertEqual(review_checks.missing_checklist(full), [])
        part = full.replace("- гонки: нет проблем", "- гонки:").replace("- сбой посередине: нет проблем", "")
        self.assertEqual(review_checks.missing_checklist(part), ["сбой посередине", "гонки"])

    def test_bypass_lines(self):
        diff = ("--- a/t.py\n+++ b/t.py\n+    @unittest.skip('later')\n+x = 1  # noqa\n"
                "-        self.assertEqual(a, b)\n-        assert ok\n"
                "+git commit --no-verify\n context\n")
        got = review_checks.bypass_lines(diff)
        self.assertEqual(len(got), 5, got)
        self.assertIn("удалено: self.assertEqual(a, b)", got)
        self.assertEqual(review_checks.bypass_lines("+print(1)\n-print(2)\n"), [])
        self.assertEqual(review_checks.bypass_lines("-    assert a\n+    assert a == 1\n"), [])


class Cli(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-ra-")
        self.a = os.path.join(self.root, ".autopilot")
        os.makedirs(self.a)
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "i")
        self.home = tempfile.mkdtemp(prefix="ap-home-")
        for name in os.listdir(TOOLS):
            if name.endswith(".py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(self.a, name))
        shutil.copy(os.path.join(SKILL, "phases", "dashboard-template.html"), os.path.join(self.a, "dashboard.html"))
        os.makedirs(os.path.join(self.root, "src"))
        for name in ("a.py", "b.py"):
            with open(os.path.join(self.root, "src", name), "w") as f:
                f.write("x\n")
        self.ap("init", "--slug", "ra", "--title", "T", "--skill-dir", SKILL)
        self.dir = os.path.join(self.a, self.state()["dir"])
        self.write("manifest.md", MANIFEST)
        self.write("tickets/01-first.md", TICKET)
        self.ap("tickets")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True)

    def ap(self, *args):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1", AUTOPILOT_HOME=self.home)
        r = subprocess.run([sys.executable, os.path.join(self.a, "ap.py")] + list(args) + ["--no-serve"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=self.root)
        return r.returncode, r.stdout

    def state(self):
        return json.loads(read(os.path.join(self.a, "state.js")).split("=", 1)[1])

    def write(self, rel, text):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    # plan-fact
    def test_plan_fact_list_prints_ids(self):
        code, out = self.ap("plan-fact", "list")
        self.assertEqual(code, 0, out)
        self.assertIn("T01.1", out)
        self.assertIn("третье", out)
        self.assertNotIn("не пункт", out)

    def test_plan_fact_record_writes_state_and_concerns(self):
        code, out = self.ap("plan-fact", "record", "--verdict", "T01.1 | сделано | src/a.py:3",
                            "--verdict", "T01.2 | частично | src/b.py", "--verdict", "T01.3 | сделано | ")
        self.assertEqual(code, 0, out)
        st = self.state()
        self.assertEqual((st["planFact"]["done"], st["planFact"]["total"]), (1, 3))
        self.assertEqual(st["planFact"]["items"][2]["status"], "не сделано")
        self.assertIn("план: T01.2 — частично — второе", st["concerns"])
        self.assertIn("план: T01.3 — не сделано — третье", st["concerns"])
        self.assertEqual(len([c for c in st["concerns"] if c.startswith("план: ")]), 2)
        code, out = self.ap("plan-fact", "show")
        self.assertIn("план: 1 из 3", out)

    def test_plan_fact_record_by_parts_keeps_other_verdicts(self):
        self.ap("plan-fact", "record", "--verdict", "T01.1 | сделано | src/a.py:3")
        code, out = self.ap("plan-fact", "record", "--verdict", "T01.2 | сделано | src/b.py::f")
        self.assertEqual(code, 0, out)
        self.assertEqual([i["status"] for i in self.state()["planFact"]["items"]], ["сделано", "сделано", "не сделано"])

    def test_plan_fact_done_needs_an_existing_path(self):
        self.ap("plan-fact", "record", "--verdict", "T01.1 | сделано | ок", "--verdict", "T01.2 | сделано | нет.py:1")
        st = self.state()
        self.assertEqual(st["planFact"]["done"], 0)
        self.assertIn("план: T01.1 — не сделано — первое", st["concerns"])

    def test_plan_fact_unknown_id_refuses_and_changes_nothing(self):
        self.ap("plan-fact", "record", "--verdict", "T01.1 | сделано | src/a.py:1")
        before = self.state()
        code, out = self.ap("plan-fact", "record", "--verdict", "T99.1 | сделано | src/a.py:1")
        self.assertEqual(code, 1, out)
        self.assertIn("T99.1", out)
        after = self.state()
        self.assertEqual((after["planFact"], after["concerns"]), (before["planFact"], before["concerns"]))

    def test_plan_fact_repeat_does_not_duplicate_concerns(self):
        args = ("plan-fact", "record", "--verdict", "T01.1 | сделано | src/a.py:1")
        self.ap(*args)
        first = [c for c in self.state()["concerns"] if c.startswith("план: ")]
        self.ap(*args)
        self.assertEqual([c for c in self.state()["concerns"] if c.startswith("план: ")], first)
        self.assertEqual(len(first), 2)

    def test_old_state_without_plan_fact_is_read(self):
        self.assertNotIn("planFact", self.state())
        code, out = self.ap("plan-fact", "show")
        self.assertEqual(code, 0, out)
        self.assertIn("план: 0 из 0", out)
        self.assertEqual(self.ap("stage", "spec")[0], 0)

    def test_ci_runs_the_parallel_runner(self):
        wf = read(os.path.join(os.path.dirname(HERE), ".github", "workflows", "python-tests.yml"))
        self.assertIn("run: python tools/run-tests.py", wf)
        self.assertNotIn("unittest discover", wf)
        self.assertIn("ubuntu-latest, windows-latest", wf)
        self.assertNotIn("CI запускает то же", read(os.path.join(os.path.dirname(HERE), "AGENTS.md")))

    # шаблон дашборда
    def test_dashboard_template_has_plan_line_in_both_languages_under_ceiling(self):
        path = os.path.join(SKILL, "phases", "dashboard-template.html")
        text = read(path)
        self.assertLess(os.path.getsize(path), 450 * 1024)
        self.assertIn("planOf:", text)
        self.assertEqual(len(re.findall(r"planOf:", text)), 2)
        self.assertIn("S.planFact", text)

    # чек-лист
    def test_check_review_report(self):
        full = os.path.join(self.root, "full.md")
        part = os.path.join(self.root, "part.md")
        with open(full, "w", encoding="utf-8") as f:
            f.write("\n".join("%s: ок" % p for p in review_checks.CHECKLIST))
        with open(part, "w", encoding="utf-8") as f:
            f.write("инварианты: ок\n")
        code, out = self.ap("check-review-report", "--file", full)
        self.assertEqual(code, 0, out)
        code, out = self.ap("check-review-report", "--file", part)
        self.assertEqual(code, 1)
        self.assertIn("гонки", out)

    # второй проход
    def open_blocker(self):
        code, out = self.ap("blocker", "open", "--note", "гонка в записи состояния")
        self.assertEqual(code, 0, out)

    def test_blocker_confirm_not_confirmed_downgrades(self):
        self.open_blocker()
        self.assertNotEqual(self.ap("blocker", "confirm", "--id", "B01", "--verdict", "not-confirmed")[0], 0)
        self.assertNotEqual(self.ap("blocker", "confirm", "--id", "B01", "--verdict", "not-confirmed",
                                    "--quote", "  ")[0], 0)
        self.assertEqual(self.state()["blockingFindings"][0]["status"], "open")
        code, out = self.ap("blocker", "confirm", "--id", "B01", "--verdict", "not-confirmed",
                            "--quote", "a.py:5 — запись под замком")
        self.assertEqual(code, 0, out)
        st = self.state()
        self.assertEqual(st["blockingFindings"][0]["status"], "downgraded")
        self.assertIn("не подтверждено вторым проходом: гонка в записи состояния", st["concerns"])
        self.assertEqual(self.ap("blocker", "open", "--note", "второй блокер")[0], 0)   # реестр читается
        self.assertEqual(self.state()["blockingFindings"][1]["id"], "B02")

    def test_blocker_confirm_confirmed_keeps_it_open(self):
        self.open_blocker()
        code, out = self.ap("blocker", "confirm", "--id", "B01", "--verdict", "confirmed",
                            "--quote", "a.py:5 — замка нет")
        self.assertEqual(code, 0, out)
        b = self.state()["blockingFindings"][0]
        self.assertEqual(b["status"], "open")
        self.assertEqual(b["confirmQuote"], "a.py:5 — замка нет")
        self.assertNotEqual(self.ap("blocker", "confirm", "--id", "B01", "--verdict", "maybe", "--quote", "x")[0], 0)

    def test_blocker_second_verdict_is_refused(self):
        self.open_blocker()
        self.ap("blocker", "confirm", "--id", "B01", "--verdict", "confirmed", "--quote", "a.py:5 — замка нет")
        code, out = self.ap("blocker", "confirm", "--id", "B01", "--verdict", "not-confirmed", "--quote", "a.py:6")
        self.assertEqual(code, 1, out)
        b = self.state()["blockingFindings"][0]
        self.assertEqual((b["status"], b["secondPass"]["verdict"]), ("open", "confirmed"))

    def test_blocker_confirm_stores_second_pass_and_logs_verdict(self):
        self.open_blocker()
        self.assertNotIn("secondPass", self.state()["blockingFindings"][0])    # старые блокеры читаются
        self.ap("blocker", "confirm", "--id", "B01", "--verdict", "not-confirmed", "--quote", "a.py:5 — замок")
        sp = self.state()["blockingFindings"][0]["secondPass"]
        self.assertEqual((sp["verdict"], sp["quote"]), ("not-confirmed", "a.py:5 — замок"))
        self.assertTrue(sp["at"])
        events = [e for e in self.state()["log"] if e.get("k") == "blocker" and e.get("act") == "downgraded"]
        self.assertEqual(events[-1]["verdict"], "not-confirmed")

    # agent-for
    def test_agent_for_plain_run_without_plan_models(self):
        self.assertEqual(self.ap("agent-for", "reviewer")[1].strip(), "autopilot-reviewer")
        self.assertEqual(self.ap("agent-for", "repair")[1].strip(), "autopilot-executor")
        # Opus без подписанного подтверждения роли не выбирается, даже на большом диффе
        self.assertEqual(self.ap("agent-for", "reviewer", "--diff-lines", "99999")[1].strip(), "autopilot-reviewer")
        for out in (self.ap("agent-for", "reviewer")[1], self.ap("agent-for", "repair")[1]):
            self.assertNotRegex(out.lower(), "opus|fable")

    # обход замечаний
    def test_check_bypass_prints_added_skips_and_removed_asserts(self):
        with open(os.path.join(self.root, "t.py"), "w", encoding="utf-8") as f:
            f.write("def test():\n    assert 1 == 1\n")
        self.git("add", "t.py")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "one")
        with open(os.path.join(self.root, "t.py"), "w", encoding="utf-8") as f:
            f.write("import unittest\n@unittest.skip('x')\ndef test():\n    pass\n")
        self.git("add", "t.py")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "two")
        code, out = self.ap("check-bypass", "HEAD~1..HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("добавлено: @unittest.skip('x')", out)
        self.assertIn("удалено: assert 1 == 1", out)

    def test_check_bypass_without_args_works_on_a_single_commit_repo(self):
        with open(os.path.join(self.root, "t.py"), "w", encoding="utf-8") as f:
            f.write("import unittest\n@unittest.skip('x')\ndef test():\n    pass\n")
        self.git("add", "t.py")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--amend", "-m", "only")
        code, out = self.ap("check-bypass")
        self.assertEqual(code, 0, out)
        self.assertIn("добавлено: @unittest.skip('x')", out)

    # silence без журнала
    def test_silence_with_missing_transcript_is_not_all_alive(self):
        code, out = self.ap("silence", "--transcript", os.path.join(self.home, "нет.jsonl"))
        self.assertEqual(code, 1, out)
        self.assertIn("журнал не найден", out)
        self.assertNotIn("подают признаки жизни", out)

    def test_silence_without_any_transcript_is_not_all_alive(self):
        code, out = self.ap("silence")
        self.assertEqual(code, 1, out)
        self.assertIn("журнал не найден", out)

    # справка
    def test_help_lists_new_commands(self):
        text = read(os.path.join(TOOLS, "ap.py")).split('"""')[1]
        for word in ("plan-fact", "check-review-report", "check-bypass", "blocker confirm", "ticket 03 redproof",
                     "ticket 03 baseline", "ticket 03 bundle", "silence", "lessons", "profile",
                     "init --kind", "land --include"):
            self.assertIn(word, text)


class Texts(unittest.TestCase):
    def test_new_prompts_exist_and_skill_lists_them(self):
        skill = read(os.path.join(SKILL, "SKILL.md"))
        for rel in ("prompts/review-checklist.md", "prompts/confirm.md", "phases/8-plan-fact.md"):
            self.assertTrue(os.path.isfile(os.path.join(SKILL, rel)), rel)
            self.assertIn(rel, skill)
        checklist = read(os.path.join(SKILL, "prompts", "review-checklist.md"))
        for p in review_checks.CHECKLIST:
            self.assertIn(p, checklist)
        self.assertIn("blocker confirm", read(os.path.join(SKILL, "prompts", "confirm.md")))

    def test_blind_checker_never_receives_the_plan(self):
        final = read(os.path.join(SKILL, "phases", "8-final.md"))
        row = next(l for l in final.splitlines() if l.startswith("| blind checker"))
        self.assertNotIn("planFact", row.split("|")[3])
        blind = final.split("## 1. Blind acceptance")[1].split("\n## 2.")[0]
        for word in ("planFact", "plan-fact", "plan_items"):
            self.assertNotIn(word, blind)
        self.assertIn("plan-fact", read(os.path.join(SKILL, "phases", "8-plan-fact.md")))
        self.assertIn("8-plan-fact.md", final)

    def test_executor_forbids_bypass_in_one_line(self):
        lines = [l for l in read(os.path.join(SKILL, "prompts", "executor.md")).splitlines() if "check-bypass" in l]
        self.assertEqual(len(lines), 1)

    def test_gated_files_untouched(self):
        diff = subprocess.run(["git", "diff", "HEAD", "--stat", "--", "skills/autopilot/tools/gate_sign.py",
                               "skills/autopilot/tools/claude_agent_guard.py",
                               "skills/autopilot/tools/model_router.py"],
                              cwd=os.path.dirname(HERE), capture_output=True, text=True).stdout
        self.assertEqual(diff.strip(), "")


if __name__ == "__main__":
    unittest.main()
