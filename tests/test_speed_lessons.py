"""Скорость и уроки: silence, worktrees.link_deps, lessons, команды bundle / silence / lessons / profile.

Запуск одного файла:  python -m unittest discover -s tests -p test_speed_lessons.py
"""
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from test_ap import MANIFEST, ticket
from test_one_command import GENERATORS, TOOLS, Project, SKILL

sys.path.insert(0, TOOLS)
import kinds  # noqa: E402
import lessons  # noqa: E402
import silence  # noqa: E402
import state_io  # noqa: E402
import worktrees  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def touch(path, age=0, text="x\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    stamp = time.time() - age
    os.utime(path, (stamp, stamp))


class SilenceUnit(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ap-sil-")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def test_finds_only_files_idle_longer_than_the_limit(self):
        touch(os.path.join(self.dir, "agent-old.jsonl"), age=900)
        touch(os.path.join(self.dir, "agent-new.jsonl"), age=30)
        touch(os.path.join(self.dir, "notes.txt"), age=5000)             # не agent-*.jsonl
        found = silence.silent_agents(self.dir, 600)
        self.assertEqual([x["file"] for x in found], ["agent-old.jsonl"])
        self.assertGreaterEqual(found[0]["idle"], 900)

    def test_now_is_injectable_and_missing_dir_is_empty(self):
        touch(os.path.join(self.dir, "agent-a.jsonl"), age=0)
        later = time.time() + 700
        self.assertEqual(len(silence.silent_agents(self.dir, 600, now=later)), 1)
        self.assertEqual(silence.silent_agents(os.path.join(self.dir, "нет"), 600), [])

    def test_limit_comes_from_the_environment_default_600(self):
        self.assertEqual(silence.DEFAULT_LIMIT, 600)
        with mock.patch.dict(os.environ, {"AUTOPILOT_SILENCE_SECONDS": "42"}):
            self.assertEqual(silence.limit_from_env(), 42)
        with mock.patch.dict(os.environ, {"AUTOPILOT_SILENCE_SECONDS": "мусор"}):
            self.assertEqual(silence.limit_from_env(), 600)
        env = {k: v for k, v in os.environ.items() if k != "AUTOPILOT_SILENCE_SECONDS"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(silence.limit_from_env(), 600)

    def test_long_stages_are_those_open_over_the_minutes(self):
        t = dt.datetime.now().astimezone()
        iso = lambda mins: (t - dt.timedelta(minutes=mins)).isoformat()
        stages = [{"id": "build", "status": "active", "segments": [{"startedAt": iso(130), "finishedAt": None}]},
                  {"id": "review", "status": "active", "segments": [{"startedAt": iso(5), "finishedAt": None}]},
                  {"id": "spec", "status": "done", "segments": [{"startedAt": iso(500), "finishedAt": iso(400)}]},
                  {"id": "plan", "status": "active", "startedAt": iso(90)}]
        got = {i: m for i, m in silence.long_stages(stages, 60, now=t)}
        self.assertEqual(sorted(got), ["build", "plan"])
        self.assertEqual(got["build"], 130)


class LinkDeps(unittest.TestCase):
    def setUp(self):
        base = tempfile.mkdtemp(prefix="ap-deps-")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        self.root, self.wt = os.path.join(base, "r"), os.path.join(base, "w")
        for d in (self.root, self.wt):
            os.makedirs(d)
        touch(os.path.join(self.root, "node_modules", "pkg", "index.js"), text="module\n")
        touch(os.path.join(self.root, "package-lock.json"), text="{}\n")

    def lock(self, wt_text="{}\n"):
        touch(os.path.join(self.wt, "package-lock.json"), text=wt_text)

    def test_windows_keeps_the_old_path(self):
        self.lock()
        with mock.patch.object(worktrees.sys, "platform", "win32"):
            self.assertEqual(worktrees.link_deps(self.root, self.wt), "skipped: windows")
        self.assertFalse(os.path.exists(os.path.join(self.wt, "node_modules")))

    @unittest.skipIf(shutil.which("cp") is None, "нет cp")
    def test_same_locks_copy_node_modules(self):
        self.lock()
        with mock.patch.object(worktrees.sys, "platform", "linux"):
            self.assertEqual(worktrees.link_deps(self.root, self.wt), "copied")
        self.assertTrue(os.path.isfile(os.path.join(self.wt, "node_modules", "pkg", "index.js")))

    def test_different_or_missing_locks_and_modules_are_skipped(self):
        with mock.patch.object(worktrees.sys, "platform", "linux"):
            self.lock("{ другой }\n")
            self.assertTrue(worktrees.link_deps(self.root, self.wt).startswith("skipped"))
            os.remove(os.path.join(self.wt, "package-lock.json"))
            self.assertTrue(worktrees.link_deps(self.root, self.wt).startswith("skipped"))
            self.lock()
            shutil.rmtree(os.path.join(self.root, "node_modules"))
            self.assertTrue(worktrees.link_deps(self.root, self.wt).startswith("skipped"))
        self.assertFalse(os.path.exists(os.path.join(self.wt, "node_modules")))

    def test_copy_failure_is_skipped_not_raised(self):
        self.lock()
        with mock.patch.object(worktrees.sys, "platform", "linux"), \
                mock.patch.object(worktrees.subprocess, "run", side_effect=OSError("диск")):
            self.assertTrue(worktrees.link_deps(self.root, self.wt).startswith("skipped"))


class LessonsUnit(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ap-les-")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.path = os.path.join(self.dir, "lessons.md")

    def test_check_text_refuses_secret_path_and_newline(self):
        self.assertIsNone(lessons.check_text("гонять тесты по одному файлу"))
        for bad in ("ключ sk-abcdefghijklmnopqrstuv1234", "токен ghp_abcdefghijklmnopqrstuvwxyz0123456789",
                    "AKIAABCDEFGHIJKLMNOP", "лежит в C:\\Users\\ivan\\proj", "см. /Us" "ers/ivan/x", "см. /ho" "me/ivan/x",
                    "две\nстроки"):
            self.assertIsNotNone(lessons.check_text(bad), bad)

    def test_render_is_newest_first_and_cut_to_the_limit(self):
        self.assertEqual(lessons.render(self.path), "")
        self.assertEqual(lessons.LESSONS_LIMIT_BYTES, 2048)
        lessons.add(self.path, ["первый", "второй"])
        lines = lessons.render(self.path).splitlines()
        self.assertTrue(lines[0].endswith("второй") and lines[1].endswith("первый"), lines)
        for i in range(60):
            lessons.add(self.path, ["урок номер %d " % i + "я" * 40])
        out = lessons.render(self.path)
        self.assertLessEqual(len(out.encode("utf-8")), 2048)
        self.assertIn("урок номер 59", out)
        self.assertNotIn("первый", out)

    def test_add_reports_refusals_and_respects_max(self):
        refused = lessons.add(self.path, ["нормальный урок", "пароль в C:\\Users\\a\\b"])
        self.assertEqual(len(refused), 1)
        lessons.add(self.path, ["a%d" % i for i in range(9)], max_items=5)
        self.assertEqual(len(lessons.render(self.path, limit=10 ** 6).splitlines()), 1 + 5)

    def test_drop_removes_nth_newest_and_a_deleted_line_never_returns(self):
        lessons.add(self.path, ["один", "два", "три"])
        self.assertTrue(lessons.drop(self.path, 1))                       # самый новый — «три»
        self.assertNotIn("три", lessons.render(self.path))
        self.assertFalse(lessons.drop(self.path, 9))
        with open(self.path, encoding="utf-8") as f:                      # пользователь стёр «два» руками
            keep = [x for x in f.read().splitlines() if "два" not in x]
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(keep) + "\n")
        lessons.add(self.path, ["два", "три"])
        self.assertNotIn("два", lessons.render(self.path))
        self.assertNotIn("три", lessons.render(self.path))

    def test_candidates_from_concerns_retries_and_downgraded(self):
        state = {"concerns": ["c1", "c2", "c3"],
                 "tickets": [{"id": "01", "title": "а", "retries": 0, "repairs": 0},
                             {"id": "02", "title": "б", "retries": 2, "repairs": 0},
                             {"id": "03", "title": "в", "retries": 0, "repairs": 1}],
                 "blockingFindings": [{"id": "B01", "text": "не подтверждено", "status": "downgraded"}]}
        got = lessons.candidates(state, 10)
        self.assertEqual(len(got), 3 + 2 + 1)
        self.assertTrue(any("02" in x for x in got) and not any("таск 01" in x for x in got))
        self.assertEqual(len(lessons.candidates(state, 2)), 2)
        self.assertEqual(lessons.candidates({}, 5), [])

    def test_profile_is_written_once_and_only_when_changed(self):
        with open(os.path.join(self.dir, "AGENTS.md"), "w", encoding="utf-8") as f:
            f.write("# П\n\n## Команды\n\n| Команда | Что |\n|---|---|\n| `make test` | тесты |\n\n"
                    "## Подводные камни\n\n- первый камень\n- второй камень\n\n## Хвост\n\nне нужно\n")
        touch(os.path.join(self.dir, "pyproject.toml"))
        text = lessons.profile_text(self.dir, check="make all")
        for want in ("make test", "make all", "первый камень", "pyproject.toml"):
            self.assertIn(want, text)
        self.assertNotIn("не нужно", text)
        self.assertTrue(lessons.refresh_profile(self.dir, check="make all"))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, ".autopilot", "profile.md")))
        self.assertFalse(lessons.refresh_profile(self.dir, check="make all"))
        self.assertTrue(lessons.refresh_profile(self.dir, check="make other"))

    def test_profile_commands_get_build_and_test_scripts_from_package_json(self):
        with open(os.path.join(self.dir, "package.json"), "w", encoding="utf-8") as f:
            f.write('{"scripts": {"build": "vite build", "test": "vitest run", "lint": "eslint ."}}')
        text = lessons.profile_text(self.dir)
        self.assertIn("`npm run build` (vite build)", text)
        self.assertIn("`npm test` (vitest run)", text)
        self.assertNotIn("eslint", text)
        self.assertTrue(lessons.refresh_profile(self.dir))
        self.assertFalse(lessons.refresh_profile(self.dir))
        os.remove(os.path.join(self.dir, "package.json"))
        self.assertNotIn("npm", lessons.profile_text(self.dir))

    def test_ap_help_kind_line_matches_kinds(self):
        with open(os.path.join(TOOLS, "ap.py"), encoding="utf-8") as f:
            m = re.search(r"init --kind ([\w|]+)", f.read())
        self.assertEqual(tuple(m.group(1).split("|")), kinds.KINDS)


class Cli(Project):
    def setUp(self):
        super().setUp()
        self.put(".autopilot/exit1.py", "raise SystemExit(1)\n")

    def plan(self, tickets):
        self.init()
        with open(os.path.join(self.dir, "manifest.md"), "w", encoding="utf-8") as f:
            f.write(MANIFEST)
        for name, text in tickets.items():
            with open(os.path.join(self.dir, "tickets", name), "w", encoding="utf-8") as f:
                f.write(text)
        self.interfaces(GENERATORS)
        self.assertEqual(self.ap("tickets", "--no-serve")[0], 0)
        self.commit_all()

    def edit(self, fn):
        path = os.path.join(self.a, "state.js")
        state = state_io.read_state_file(path)
        fn(state)
        state_io.write_state_file(path, state)


T1 = {"01-a.md": ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1)}


class BundleCmd(Cli):
    def test_red_land_stores_the_tail_and_bundle_prints_it_with_the_findings(self):
        self.plan(T1)
        self.assertEqual(self.ap("ticket", "01", "start", "--no-serve")[0], 0)
        self.mode("red")
        self.put("src/core/a.py", "x = 1\n")
        code, out = self.land("01")
        self.assertEqual(code, 2, out)
        self.assertIn("FAILED (failures=1)", next(t for t in self.state()["tickets"] if t["id"] == "01")["lastCheck"])
        self.edit(lambda s: s["tickets"][0].setdefault("concerns", []).append("замечание-ревью-777"))
        self.assertEqual(self.ap("blocker", "open", "--ticket", "01", "--note", "блокер-открыт-555", "--no-serve")[0], 0)
        code, out = self.ap("ticket", "01", "bundle", "--no-serve")
        self.assertEqual(code, 0, out)
        for want in ("FAILED (failures=1)", "блокер-открыт-555", "замечание-ревью-777"):
            self.assertIn(want, out)

    def land(self, tid):
        return self.ap("ticket", tid, "land", "--message", "T%s: работа" % tid, "--no-serve")

    def test_bundle_of_a_clean_ticket_says_so(self):
        self.plan(T1)
        code, out = self.ap("ticket", "01", "bundle", "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("нет", out)


class SilenceCmd(Cli):
    def test_exit_3_for_a_silent_agent_and_0_for_a_fresh_one(self):
        self.init()
        sess = os.path.join(self.home, "sess")
        transcript = sess + ".jsonl"
        touch(transcript)
        touch(os.path.join(sess, "subagents", "agent-a1.jsonl"), age=900)
        code, out = self.ap("silence", "--transcript", transcript, "--no-serve")
        self.assertEqual(code, 3, out)
        self.assertIn("agent-a1", out)
        self.assertEqual(self.ap("silence", "--transcript", transcript, "--limit", "5000", "--no-serve")[0], 0)

    def test_stage_warns_about_a_stage_over_an_hour(self):
        self.init()
        old = (dt.datetime.now().astimezone() - dt.timedelta(minutes=130)).isoformat()

        def age(s):
            b = next(x for x in s["stages"] if x["id"] == "build")
            b.update(status="active", startedAt=old, segments=[{"startedAt": old, "finishedAt": None}])
        self.edit(age)
        code, out = self.ap("stage", "build", "start", "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("build", out.split("\n", 1)[1])
        self.assertIn("130", out)
        self.assertNotIn("130", self.ap("stage", "review", "start", "--no-serve")[1].split("\n", 1)[0])


class LessonsCmd(Cli):
    def les(self, *args):
        return self.ap("lessons", *args, "--no-serve")

    def test_add_show_drop_check_roundtrip(self):
        self.init()
        self.assertEqual(self.les("add", "гонять один файл тестов")[0], 0)
        code, out = self.les("show")
        self.assertIn("гонять один файл тестов", out)
        self.assertEqual(self.les("check")[0], 0)
        code, out = self.les("add", "ключ sk-abcdefghijklmnopqrstuv1234")
        self.assertEqual(code, 1, out)
        self.assertNotIn("sk-abcdefghijklmnopqrstuv1234", out)
        self.assertEqual(self.les("drop", "1")[0], 0)
        self.assertNotIn("гонять", self.les("show")[1])
        self.put(".autopilot/lessons.md", "- 2026-11-19 — путь C:\\Users\\a\\b\n")
        self.assertEqual(self.les("check")[0], 1)

    def test_candidates_respect_max(self):
        self.init()
        for c in ("c1", "c2", "c3"):
            self.assertEqual(self.ap("add", "concerns", c, "--no-serve")[0], 0)
        out = self.les("candidates", "--max", "2")[1]
        self.assertEqual(sum(1 for x in out.splitlines() if x.lstrip().startswith("- ")), 2, out)
        out = self.les("candidates")[1]
        self.assertEqual(sum(1 for x in out.splitlines() if x.lstrip().startswith("- ")), 3, out)

    def test_profile_refresh_writes_then_stays_quiet(self):
        self.init()
        self.put("AGENTS.md", "## Команды\n\n| Команда | Что |\n|---|---|\n| `make t` | тесты |\n")
        code, out = self.ap("profile", "refresh", "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("make t", open(os.path.join(self.a, "profile.md"), encoding="utf-8").read())
        self.assertIn("записан", out)
        self.assertIn("без изменений", self.ap("profile", "refresh", "--no-serve")[1])

    def test_init_reports_the_lesson_lines_when_the_file_is_not_empty(self):
        self.put(".autopilot/lessons.md", "- 2026-11-18 — один\n- 2026-11-18 — два\n")
        code, out = self.ap("init", "--slug", "demo", "--title", "Д", "--skill-dir", os.path.dirname(TOOLS), "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("уроки: 2 строк", out)

    def test_worktree_prepare_reports_the_deps_step(self):
        self.plan(T1)
        code, out = self.ap("worktree", "01", "prepare", "--no-serve")
        self.assertEqual(code, 0, out)
        self.assertIn("зависимости: skipped", out)        # в проекте теста нет ни node_modules, ни lock-файла


class Texts(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(SKILL, *parts), encoding="utf-8") as f:
            return f.read()

    def test_new_phase_files_are_in_the_skill_table(self):
        table = self.read("SKILL.md")
        for name in ("5-parallel.md", "9-lessons.md"):
            self.assertTrue(os.path.isfile(os.path.join(SKILL, "phases", name)))
            self.assertIn("phases/" + name, table)

    def test_executor_prompt_runs_own_tests_and_reads_lessons(self):
        text = self.read("prompts", "executor.md")
        for want in (".autopilot/lessons.md", "profile.md", "`ticket NN land`"):
            self.assertIn(want, text)

    def test_every_ap_import_is_copied_by_the_main_harness(self):
        with open(os.path.join(ROOT, "tests", "test_ap.py"), encoding="utf-8") as f:
            harness = f.read()
        for name in ("silence.py", "lessons.py"):
            self.assertIn('"%s"' % name, harness)

    def test_measuring_cost_records_not_measured_with_a_reason(self):
        with open(os.path.join(ROOT, "docs", "autopilot", "measuring-cost.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Not measured", text)
        with open(os.path.join(ROOT, "docs", "autopilot", "worktrees.md"), encoding="utf-8") as f:
            self.assertIn("link_deps", f.read())

    def test_protected_files_are_untouched(self):
        r = subprocess.run(["git", "-C", ROOT, "diff", "--stat", "HEAD", "--",     # gate_sign.py снят: правка гонки ключа, docs/adr/0029
                            "skills/autopilot/tools/claude_agent_guard.py", "skills/autopilot/tools/model_router.py"], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
