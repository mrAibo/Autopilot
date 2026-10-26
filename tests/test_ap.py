"""Тесты skills/autopilot/tools/ap.py — учёта прогона Autopilot.

Запуск из корня репозитория:  python3 -m unittest discover -s tests
Каждый тест поднимает временный git-репозиторий с .autopilot/ и зовёт ap.py
как оркестратор — отдельным процессом, без сервера (--no-serve).
"""

import importlib.util
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
AP = os.path.join(SKILL, "tools", "ap.py")
ROUTER = os.path.join(SKILL, "tools", "model_router.py")
PROFILES = os.path.join(SKILL, "tools", "agent_profiles.py")
WORKTREES = os.path.join(SKILL, "tools", "worktrees.py")
RETRY_POLICY = os.path.join(SKILL, "tools", "retry_policy.py")
SCHEDULER = os.path.join(SKILL, "tools", "scheduler.py")
CONTROLLER = os.path.join(SKILL, "tools", "controller.py")
TEST_EVIDENCE = os.path.join(SKILL, "tools", "test_evidence.py")
TEMPLATE = os.path.join(SKILL, "phases", "dashboard-template.html")

MANIFEST = """# Манифест требований

| ID | Из брифа (дословно) | Статус | Основание | Где |
|----|---------------------|--------|-----------|-----|
| R01 | «принимает заявки» | in-spec | — | spec §2 |
| R02 | «складывает в таблицу» | in-spec | — | spec §4 |
| R03 | «SMS» | dropped | «не надо» | — |
| R05 | «цвета студии» | in-spec | — | spec §6 |
"""


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def ticket(tid, title, reqs, deps, zone, wave, review="нет", model="обычная"):
    return ("# %s — %s\n\n**Требования:** %s\n**Зависит от:** %s\n**Зона:** %s\n"
            "**Волна:** %s\n**Ревью:** %s\n**Модель:** %s\n\n## Критерии приёмки\n\n- [ ] что-то\n"
            % (tid, title, reqs, deps, " · ".join("`%s`" % z for z in zone), wave, review, model))


class Run(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-test-")
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
        self.a = os.path.join(self.root, ".autopilot")
        os.makedirs(self.a)
        shutil.copy(TEMPLATE, os.path.join(self.a, "dashboard.html"))
        shutil.copy(AP, os.path.join(self.a, "ap.py"))
        shutil.copy(ROUTER, os.path.join(self.a, "model_router.py"))
        shutil.copy(PROFILES, os.path.join(self.a, "agent_profiles.py"))
        shutil.copy(WORKTREES, os.path.join(self.a, "worktrees.py"))
        shutil.copy(RETRY_POLICY, os.path.join(self.a, "retry_policy.py"))
        shutil.copy(SCHEDULER, os.path.join(self.a, "scheduler.py"))
        shutil.copy(CONTROLLER, os.path.join(self.a, "controller.py"))
        shutil.copy(TEST_EVIDENCE, os.path.join(self.a, "test_evidence.py"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True)

    def ap(self, *args):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1")
        r = subprocess.run([sys.executable, os.path.join(self.a, "ap.py")] + list(args) + ["--no-serve"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=self.root)
        return r.returncode, r.stdout + ("\n[stderr] " + r.stderr[-2000:] if r.returncode and r.stderr else "")

    def state(self):
        raw = read(os.path.join(self.a, "state.js"))
        return json.loads(raw.split("=", 1)[1])

    def stage(self, sid):
        return next(s for s in self.state()["stages"] if s["id"] == sid)

    def init(self, strict=False, isolated=False):
        args = ["init", "--slug", "repair-bot", "--title", "Бот", "--skill-dir", SKILL]
        if strict:
            args.append("--strict-routing")
        if isolated:
            args.append("--isolated-tickets")
        code, out = self.ap(*args)
        self.assertEqual(code, 0, out)
        self.dir = os.path.join(self.a, self.state()["dir"])
        return out

    def write(self, rel, text):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def manifest(self):
        return read(os.path.join(self.dir, "manifest.md"))

    def commit(self, name):
        result = self.git("-c", "user.email=t@t", "-c", "user.name=t",
                          "commit", "-q", "--allow-empty", "-m", name)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.git("rev-parse", "--short", "HEAD").stdout.strip()

    def ready_to_finish(self):
        self.plan()
        self.ap("tickets")
        self.ap("stage", "spec")
        self.ap("coverage", "found=0", "fixed=0", "deferred=0")
        self.ap("check-plan")
        self.ap("ticket", "01", "start")
        sha1 = self.commit("T01")
        code, out = self.ap("ticket", "01", "done", "--tests", "3/0",
                            "--commit", sha1, "--placeholder", "R05")
        self.assertEqual(code, 0, out)
        self.ap("ticket", "02", "start")
        sha2 = self.commit("T02")
        code, out = self.ap("ticket", "02", "done", "--tests", "5/0", "--commit", sha2)
        self.assertEqual(code, 0, out)
        self.ap("tests", "5/0")
        self.ap("blind", "checked=4", "matched=4")
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "run")

    # ── init ───────────────────────────────────────────────────────────────
    def test_init_creates_run(self):
        self.init()
        s = self.state()
        self.assertTrue(re.match(r"\d{4}-\d{2}-\d{2}-repair-bot--wip$", s["dir"]))
        self.assertTrue(os.path.isdir(os.path.join(self.dir, "tickets")))
        self.assertEqual([x["status"] for x in s["stages"]], ["active"] + ["pending"] * 7)
        self.assertRegex(s["startedAt"], r"T\d\d:\d\d:\d\d[+-]\d\d:\d\d$")
        self.assertIn("в работе", read(os.path.join(self.a, "README.md")))
        self.assertIn(".autopilot/serve.*", read(os.path.join(self.root, ".gitignore")))
        self.assertIn(".autopilot/worktrees/", read(os.path.join(self.root, ".gitignore")))
        self.assertIn(".autopilot/model-capabilities.json", read(os.path.join(self.root, ".gitignore")))
        self.assertIn(".autopilot/offline-worker/", read(os.path.join(self.root, ".gitignore")))
        self.assertIn(".autopilot/offline-test-consent", read(os.path.join(self.root, ".gitignore")))
        self.assertIn("window.STATE={", read(os.path.join(self.a, "dashboard.html")))

    def test_init_refuses_on_live_run(self):
        self.init()
        code, out = self.ap("init", "--slug", "other")
        self.assertNotEqual(code, 0)
        self.assertIn("продолжение", out)

    def test_init_archives_finished_run(self):
        self.ready_to_finish()
        first = self.state()["dir"]
        self.ap("finish", "--result", "готово")
        code, out = self.ap("init", "--slug", "second")
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.exists(os.path.join(self.a, first.replace("--wip", ""), "state.js")))
        self.assertTrue(self.state()["dir"].endswith("second--wip"))

    # ── stages ─────────────────────────────────────────────────────────────
    def test_opening_a_stage_closes_the_previous(self):
        self.init()
        self.ap("stage", "manifest")
        self.assertEqual(self.stage("preflight")["status"], "done")
        self.assertEqual(self.stage("manifest")["status"], "active")

    def test_review_closes_build(self):
        self.init()
        self.ap("stage", "build")
        self.ap("stage", "review")
        self.assertEqual(self.stage("build")["status"], "done")

    def test_passed_stage_with_artifact_is_marked_done(self):
        self.init()
        self.write("manifest.md", MANIFEST)
        code, out = self.ap("stage", "spec")
        self.assertEqual(self.stage("manifest")["status"], "done")
        self.assertIn("briefing", out)                     # ни файла, ни отметки — подсказка
        self.assertEqual(self.stage("briefing")["status"], "pending")

    def test_skip_needs_a_reason(self):
        self.init()
        code, _ = self.ap("stage", "briefing", "skip")
        self.assertNotEqual(code, 0)
        self.ap("stage", "briefing", "skip", "--note", "полный автомат — самобрифинг")
        self.assertEqual(self.stage("briefing")["status"], "skipped")

    # ── tickets and the manifest ───────────────────────────────────────────
    def plan(self, strict=False, isolated=False):
        self.init(strict=strict, isolated=isolated)
        self.write("manifest.md", MANIFEST)
        self.write("tickets/01-karkas.md", ticket("01", "Каркас", "R01, R05", "—", ["src/core/"], 1, "да — фундамент", "сильная"))
        self.write("tickets/02-priem.md", ticket("02", "Приём", "R01.1, R02, A01", "01", ["src/bot/"], 2))

    def test_tickets_publish_and_move_rows_in_ticket(self):
        self.plan()
        code, out = self.ap("tickets")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["02"]["requirements"], ["R01.1", "R02", "A01"])
        self.assertEqual(t["02"]["blockedBy"], ["01"])
        self.assertEqual(t["01"]["zone"], ["src/core/"])
        self.assertEqual(t["01"]["review"], "да — фундамент")
        self.assertEqual(t["02"]["status"], "pending")
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| in-ticket \|[^\n]*T01, T02")
        self.assertRegex(m, r"\| R03 \|[^\n]*\| dropped \|")
        self.assertEqual(self.state()["requirements"]["inTicket"], 3)

    def test_check_plan_passes_a_sound_plan(self):
        self.plan()
        code, out = self.ap("check-plan")
        self.assertIn("G3: трасса сходится", out)

    def test_check_plan_catches_defects(self):
        self.plan()
        self.write("tickets/03-tablica.md", ticket("03", "Таблица", "R02", "02", ["src/bot/sheets/"], 2))
        self.write("tickets/04-nichei.md", ticket("04", "Ничей", "", "—", [], 1))
        code, out = self.ap("check-plan")
        self.assertIn("в волне 2, но его зависимости позволяют не раньше 3", out)
        self.assertIn("таски 02 и 03 в одной волне пишут в src/bot/sheets/", out)
        self.assertIn("таск 04 ни к чему не привязан", out)
        self.assertIn("у таска 04 нет зоны", out)

    def test_check_plan_blocks_previously_done_unowned_requirement(self):
        self.plan()
        self.write("manifest.md", MANIFEST +
                   "| G01 | «ранее сделано» | done | — | T99 |\n")
        code, out = self.ap("check-plan")
        self.assertNotEqual(code, 0, out)
        self.assertIn("требование G01 (done) не попало", out)
        self.assertFalse(self.state()["gates"]["G3"]["ok"])

    def test_check_plan_blocks_duplicate_manifest_ids(self):
        self.plan()
        self.write("manifest.md", MANIFEST +
                   "| R01 | «другая формулировка» | done | — | T01 |\n")
        code, out = self.ap("check-plan")
        self.assertNotEqual(code, 0, out)
        self.assertIn("повторяются ID требований", out)
        self.assertFalse(self.state()["gates"]["G3"]["ok"])

    def test_check_plan_catches_a_requirement_in_no_ticket(self):
        self.plan()
        self.write("manifest.md", MANIFEST + "| G01 | «отмена» | in-spec | — | spec §5 |\n")
        code, out = self.ap("check-plan")
        self.assertIn("требование G01", out)

    def test_done_closes_rows_only_when_all_their_tickets_are_done(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        sha1 = self.commit("T01")
        self.ap("ticket", "01", "done", "--tests", "3/0", "--commit", sha1, "--placeholder", "R05")
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| in-ticket \|")     # ещё и в таске 02
        self.assertIn("placeholder", m)
        self.ap("ticket", "02", "start")
        sha2 = self.commit("T02")
        self.ap("ticket", "02", "done", "--tests", "5/0", "--commit", sha2)
        m = self.manifest()
        self.assertRegex(m, r"\| R01 \|[^\n]*\| done \|")
        self.assertRegex(m, r"\| R02 \|[^\n]*\| done \|")
        s = self.state()
        self.assertEqual(s["requirements"]["done"], 2)
        self.assertEqual(s["requirements"]["placeholder"], 1)
        self.assertEqual(s["tests"], {"passed": 5, "failed": 0})

    def test_ticket_lifecycle_counters(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        self.ap("ticket", "01", "review")
        self.ap("ticket", "01", "repair", "--note", "ключ схемы — R01")
        self.ap("ticket", "02", "retry")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["01"]["status"], "repair")
        self.assertEqual(t["01"]["repairs"], 1)
        self.assertEqual(t["01"]["repairFindings"], ["ключ схемы — R01"])
        self.assertEqual(t["02"]["retries"], 1)
        self.assertTrue(t["02"]["startedAt"])
        self.ap("ticket", "02", "reset")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["02"]["status"], "pending")
        self.assertNotIn("startedAt", t["02"])

    def test_unknown_ticket_is_an_error(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("ticket", "09", "start")
        self.assertNotEqual(code, 0)

    def test_escaped_pipe_in_a_quote(self):
        self.init()
        self.write("manifest.md", MANIFEST.replace("«складывает в таблицу»", "«таблица \\| или база»"))
        self.write("tickets/01-a.md", ticket("01", "A", "R01, R02, R05", "—", ["a/"], 1))
        self.ap("tickets")
        self.assertRegex(self.manifest(), r"\| R02 \| «таблица \\\| или база» \| in-ticket \|")

    def test_d_rows_are_constraints_not_requirements(self):
        self.plan()
        self.write("manifest.md", MANIFEST + "| D01 | схема не держит два адреса | in-spec | таск 02 | spec §3 |\n")
        code, out = self.ap("check-plan")
        self.assertNotIn("D01", out)
        self.assertEqual(self.state()["requirements"]["total"], 4)

    def test_dependencies_accept_a_t_prefix(self):
        self.plan()
        self.write("tickets/03-c.md", ticket("03", "C", "R02", "T1, T02", ["c/"], 3))
        self.ap("tickets")
        t = {x["id"]: x for x in self.state()["tickets"]}
        self.assertEqual(t["03"]["blockedBy"], ["01", "02"])

    def test_empty_tickets_dir_does_not_pass_the_plan(self):
        self.init()
        self.write("manifest.md", MANIFEST)
        self.ap("stage", "build")
        self.assertEqual(self.stage("plan")["status"], "pending")
        self.write("tickets/01-a.md", ticket("01", "A", "R01", "—", ["a/"], 1))
        self.ap()
        self.assertEqual(self.stage("plan")["status"], "done")

    # ── lists and numbers ──────────────────────────────────────────────────
    def test_add_set_and_numbers(self):
        self.init()
        self.ap("add", "concerns", "src/x.ts:4 — два формата даты")
        self.ap("add", "debt.emptyEnv", "TELEGRAM_BOT_TOKEN")
        self.ap("add", "debt.emptyEnv", "TELEGRAM_BOT_TOKEN")      # без дублей
        self.ap("set", "tier=T2", "baseCommit=abc1234")
        self.ap("coverage", "found=2", "fixed=1", "deferred=1", "--item", "R07 — отложено")
        self.ap("add", "report", "два формата даты", "лишний отступ")
        self.ap("blind", "checked=4", "matched=3", "--mismatch", "R02 — не видно")
        s = self.state()
        self.assertEqual(s["concerns"], ["src/x.ts:4 — два формата даты"])
        self.assertEqual(s["debt"]["emptyEnv"], ["TELEGRAM_BOT_TOKEN"])
        self.assertEqual((s["tier"], s["baseCommit"]), ("T2", "abc1234"))
        self.assertEqual(s["coverage"], {"found": 2, "fixed": 1, "deferred": 1, "items": ["R07 — отложено"]})
        self.assertEqual(s["report"], ["два формата даты", "лишний отступ"])
        self.assertEqual(s["blind"], {"checked": 4, "matched": 3, "mismatches": ["R02 — не видно"]})

    def test_every_event_leaves_a_beat(self):
        # updatedAt перезаписывается; журнал хранит каждое событие, чтобы рабочее
        # время считалось и тогда, когда дашборд их не видел (сон, мёртвый сервер)
        self.init()
        first = self.state()["beats"]
        self.assertEqual(first, [self.state()["startedAt"]])
        self.ap("add", "report", "раз")
        self.ap()                                   # синхронизация — не событие
        s = self.state()
        self.assertEqual(s["beats"][-1], s["updatedAt"])
        self.assertLessEqual(len(s["beats"]), 2)
        self.assertEqual(s["beats"], sorted(set(s["beats"])))

    # ── what the dashboard reads ───────────────────────────────────────────
    def test_waiting_for_the_user_is_kept_apart_from_work(self):
        # Ожидание ответа — не работа сборки: дашборд вычитает waits из часов
        self.init()
        self.ap("stage", "briefing")
        self.ap("ask", "briefing", "--note", "три вопроса")
        s = self.state()
        self.assertEqual((s["waiting"]["kind"], s["waiting"]["note"]), ("briefing", "три вопроса"))
        self.assertEqual(s["waiting"]["since"], s["updatedAt"])
        self.ap("answered")
        s = self.state()
        self.assertIsNone(s["waiting"])
        self.assertEqual(len(s["waits"]), 1)
        self.assertEqual(s["waits"][0]["kind"], "briefing")
        self.assertLessEqual(s["waits"][0]["from"], s["waits"][0]["to"])

    def test_moving_on_closes_a_forgotten_wait(self):
        self.init()
        self.ap("ask", "spec")
        self.ap("add", "report", "раз")                    # учёт — не ответ пользователя
        self.assertIsNotNone(self.state()["waiting"])
        self.ap("stage", "plan")
        s = self.state()
        self.assertIsNone(s["waiting"])
        self.assertEqual([w["kind"] for w in s["waits"]], ["spec"])

    def test_ask_needs_a_known_kind(self):
        self.init()
        code, _ = self.ap("ask", "whatever")
        self.assertNotEqual(code, 0)

    def test_log_records_events_not_syncs(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        self.ap("ticket", "01", "repair", "--note", "пустой адрес")
        sha = self.commit("T01")
        self.ap("ticket", "01", "done", "--tests", "7/0", "--commit", sha)
        self.ap()
        kinds = [(e["k"], e.get("act")) for e in self.state()["log"]]
        self.assertEqual(kinds, [("init", None), ("tickets", None), ("ticket", "start"),
                                 ("ticket", "repair"), ("ticket", "done")])
        last = self.state()["log"][-1]
        self.assertEqual((last["ids"], last["tests"]), (["01"], {"passed": 7, "failed": 0}))
        self.assertEqual(self.state()["log"][3]["note"], "пустой адрес")

    def test_gates_follow_the_events_that_decide_them(self):
        self.plan()
        self.write("manifest.md", MANIFEST.replace("| R02 | «складывает в таблицу» | in-spec",
                                                   "| R02 | «складывает в таблицу» | open"))
        self.ap("stage", "spec")
        g = self.state()["gates"]["G1"]
        self.assertEqual((g["ok"], g["open"], g["total"]), (False, 1, 4))
        self.write("manifest.md", MANIFEST)
        self.ap("stage", "spec", "done")
        self.assertTrue(self.state()["gates"]["G1"]["ok"])
        self.ap("coverage", "found=2", "fixed=1", "deferred=1")
        self.ap("check-plan")
        self.ap("blind", "checked=4", "matched=3", "--mismatch", "R02 — не видно")
        g = self.state()["gates"]
        self.assertTrue(g["G2"]["ok"])
        self.assertTrue(g["G3"]["ok"])
        self.assertEqual((g["G4"]["ok"], g["G4"]["matched"], g["G4"]["checked"]), (False, 3, 4))

    def test_requirements_carry_the_users_words(self):
        self.init()
        self.write("manifest.md", MANIFEST.replace("«цвета студии»", "*(подразумевается)* «таблица \\| база»")
                   + "| D01 | схема | in-spec | — | — |\n")
        self.ap()
        req = {r["id"]: r for r in self.state()["reqList"]}
        self.assertEqual(sorted(req), ["R01", "R02", "R03", "R05"])     # D## — не требование
        self.assertEqual(req["R01"], {"id": "R01", "text": "«принимает заявки»", "status": "in-spec"})
        self.assertEqual(req["R03"]["why"], "«не надо»")
        self.assertEqual(req["R05"]["text"], "(подразумевается) «таблица | база»")

    def test_every_write_bumps_rev(self):
        # Дашборд перерисовывается по rev: синхронизация тоже меняет то, что он показывает
        self.init()
        r = self.state()["rev"]
        self.ap()
        self.assertEqual(self.state()["rev"], r + 1)

    # ── finish ─────────────────────────────────────────────────────────────
    def test_strict_routing_blocks_unverified_dispatch(self):
        self.plan(strict=True)
        self.ap("tickets")
        code, out = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("строгая маршрутизация", out)
        sha = self.commit("T01")
        code, out = self.ap("ticket", "01", "done", "--tests", "1/0", "--commit", sha)
        self.assertNotEqual(code, 0)
        self.assertIn("строгая маршрутизация", out)
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as target:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"haiku": ["low"]}}, target)
        code, out = self.ap("ticket", "01", "route", "--provider", "anthropic",
                            "--model", "haiku", "--effort", "low", "--reason", "simple",
                            "--capabilities", caps)
        self.assertEqual(code, 0, out)
        route = self.state()["tickets"][0]["routing"]
        self.assertTrue(route["verified"])
        self.assertIn("autopilot-executor-01-karkas", route["agentType"])
        self.assertTrue(os.path.isfile(os.path.join(self.root, route["agentFile"])))
        code, out = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.root, route["agentFile"]), "a", encoding="utf-8") as profile_file:
            profile_file.write("\n# modified")
        self.ap("ticket", "01", "reset")
        code, out = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("строгая маршрутизация", out)

    def test_route_custom_policy_is_applied_and_mutation_blocks_strict_start(self):
        self.plan(strict=True)
        self.ap("tickets")
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as target:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"haiku": ["low", "medium"]}}, target)
        policy = os.path.join(self.a, "model-policy.json")
        with open(policy, "w", encoding="utf-8") as target:
            json.dump({"providers": {
                "anthropic": {"cheap": {"effort": "medium"}}}}, target)
        args = ("ticket", "01", "route", "--provider", "anthropic",
                "--model", "haiku", "--reason", "approved custom effort",
                "--capabilities", caps, "--policy", policy)
        code, output = self.ap(*args, "--effort", "low")
        self.assertNotEqual(code, 0)
        self.assertIn("не одобрены", output)
        code, output = self.ap(*args, "--effort", "medium")
        self.assertEqual(code, 0, output)
        route = self.state()["tickets"][0]["routing"]
        self.assertEqual(route["effort"], "medium")
        self.assertEqual(route["policyFile"], ".autopilot/model-policy.json")
        self.assertEqual(len(route["policySha"]), 64)
        code, output = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, output)
        self.ap("ticket", "01", "reset")
        with open(policy, "w", encoding="utf-8") as target:
            json.dump({"providers": {
                "anthropic": {"cheap": {"effort": "low"}}}}, target)
        code, output = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("строгая маршрутизация", output)
        self.assertEqual(self.state()["tickets"][0]["status"], "pending")

    def test_route_policy_outside_project_is_denied(self):
        self.plan(strict=True)
        self.ap("tickets")
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as target:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"haiku": ["low"]}}, target)
        path = os.path.join(os.path.dirname(self.root), "external-policy.json")
        code, output = self.ap(
            "ticket", "01", "route", "--provider", "anthropic",
            "--model", "haiku", "--effort", "low",
            "--reason", "route", "--capabilities", caps,
            "--policy", path)
        self.assertNotEqual(code, 0)
        self.assertIn("внутри проекта", output)

    def test_route_rejects_unapproved_model_even_with_host_advertisement(self):
        self.plan()
        self.ap("tickets")
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as target:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"fable": ["high"], "haiku": ["low"]}}, target)
        code, out = self.ap("ticket", "01", "route", "--provider", "anthropic",
                            "--model", "fable", "--effort", "high", "--reason", "default",
                            "--capabilities", caps)
        self.assertNotEqual(code, 0)
        self.assertIn("не одобрены", out)

    def test_usage_is_deduplicated_and_budget_blocks_new_work(self):
        self.plan()
        self.ap("tickets")
        params = ("usage", "01", "--call-id", "host:001",
                  "--input", "150", "--output", "20", "--source", "host-reported")
        code, out = self.ap(*params)
        self.assertEqual(code, 0, out)
        code, out = self.ap(*params)
        self.assertEqual(code, 0, out)
        events = self.state()["usageEvents"]
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0]["input"], events[0]["output"]), (150, 20))
        code, out = self.ap("budget", "--tokens", "160")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("лимит известных токенов достигнут", out)

    def test_usage_rejects_conflicting_id_and_invalid_counts(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("usage", "01", "--call-id", "call-001",
                            "--input", "13", "--output", "2", "--source", "manual")
        self.assertEqual(code, 0, out)
        code, out = self.ap("usage", "01", "--call-id", "call-001",
                            "--input", "20", "--output", "2", "--source", "manual")
        self.assertNotEqual(code, 0)
        self.assertIn("уже существует", out)
        code, out = self.ap("usage", "01", "--call-id", "call-002",
                            "--input", "-2", "--output", "3", "--source", "manual")
        self.assertNotEqual(code, 0)
        self.assertEqual(len(self.state()["usageEvents"]), 1)

    def test_set_cannot_override_protected_accounting_state(self):
        self.init()
        code, out = self.ap("set", "strictRouting=null")
        self.assertNotEqual(code, 0)
        self.assertIn("разрешены только", out)
        code, out = self.ap("set", "budgetTokens=1")
        self.assertNotEqual(code, 0)

    def test_retry_requires_diagnosed_cause_and_respects_limit(self):
        self.plan(strict=True)
        self.ap("tickets")
        code, out = self.ap("ticket", "01", "retry")
        self.assertNotEqual(code, 0)
        self.assertIn("подтверждённой модели", out)  # route required even for retry
        # The non-strict mode supports bounded, diagnosed retries for legacy projects.
        self.state()
        # Initialize a second test run with the legacy mode in a fresh instance below.

    def test_legacy_retry_is_capped_and_does_not_escalate_environment(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("ticket", "01", "retry", "--cause", "environment")
        self.assertNotEqual(code, 0)
        self.assertIn("повтор не разрешён", out)
        code, out = self.ap("ticket", "01", "retry", "--cause", "tests")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "retry", "--cause", "tests")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "retry", "--cause", "tests")
        self.assertNotEqual(code, 0)
        self.assertIn("предел повторов", out)
        self.assertEqual(self.state()["tickets"][0]["retries"], 2)
        self.assertEqual(self.state()["tickets"][0]["retryAdvice"]["model"], "same")

    def test_recover_crash_after_git_worktree_add_before_state_save(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("baseline")
        result = subprocess.run(
            [sys.executable, os.path.join(self.a, "worktrees.py"), "create", "01",
             "--root", self.root], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.state()["tickets"][0].get("worktree"))
        code, out = self.ap("worktree", "01", "recover")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "prepared")
        code, out = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, out)

    def test_recover_crash_after_cherry_pick_before_state_save(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("baseline")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, out)
        wt = self.state()["tickets"][0]["worktree"]
        (os.makedirs(os.path.join(wt["cwd"], "feature"), exist_ok=True))
        with open(os.path.join(wt["cwd"], "feature", "recover.txt"), "w", encoding="utf-8") as f:
            f.write("safe after restart\n")
        self.git("-C", wt["cwd"], "add", "feature/recover.txt")
        self.git("-C", wt["cwd"], "commit", "-qm", "T01 recover")
        # Simulate power loss: Git cherry-pick completed but ap.py state write did not.
        result = subprocess.run(
            [sys.executable, os.path.join(self.a, "worktrees.py"), "land", "01",
             "--root", self.root, "--base", wt["baseCommit"]],
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "prepared")
        code, out = self.ap("worktree", "01", "recover", "--tests", "4/0")
        self.assertEqual(code, 0, out)
        landed = self.state()["tickets"][0]["worktree"]["landedCommit"]
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "landed")
        code, out = self.ap("ticket", "01", "done", "--commit", landed[:12])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["tickets"][0]["status"], "done")

    def test_reset_refuses_unreleased_worktree(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("baseline")
        self.ap("worktree", "01", "prepare")
        code, out = self.ap("ticket", "01", "reset")
        self.assertNotEqual(code, 0)
        self.assertIn("освободи worktree", out)

    def test_ticket_cannot_be_started_twice(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("только из pending", out)

    def test_recover_deleted_worktree_after_cleanup_crash(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("baseline")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        self.ap("ticket", "01", "start")
        wt = self.state()["tickets"][0]["worktree"]
        with open(os.path.join(wt["cwd"], "cleanup-proof.txt"), "w", encoding="utf-8") as f:
            f.write("proof\n")
        self.git("-C", wt["cwd"], "add", "cleanup-proof.txt")
        self.git("-C", wt["cwd"], "commit", "-qm", "T01 cleanup")
        code, out = self.ap("worktree", "01", "land", "--tests", "3/0")
        self.assertEqual(code, 0, out)
        landed = self.state()["tickets"][0]["worktree"]["landedCommit"]
        code, out = self.ap("ticket", "01", "done", "--commit", landed[:12])
        self.assertEqual(code, 0, out)
        # Simulate crash after deletion of Git worktree, before saving status.
        clean = subprocess.run([sys.executable, os.path.join(self.a, "worktrees.py"),
                                "remove", "01", "--root", self.root,
                                "--acknowledge-loss"], capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "landed")
        code, out = self.ap("worktree", "01", "recover")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "released")
        code, out = self.ap("worktree", "01", "release")
        self.assertEqual(code, 0, out)

    def test_schedule_machine_readable_dependency_order(self):
        self.plan()
        self.ap("tickets")
        code, payload = self.ap("schedule", "--max-parallel", "2")
        self.assertEqual(code, 0, payload)
        plan = json.loads(payload)
        self.assertEqual([x["ticket"] for x in plan["selected"]], ["01"])
        self.assertEqual(plan["selected"][0]["action"], "start")
        self.assertEqual(plan["blocked"][0]["reason"], "dependencies")
        self.assertFalse(plan["automaticLaunch"])

    def test_controller_two_ticket_real_host_lifecycle_and_failed_test(self):
        """Two actual Git worktrees, trusted tests and one recoverable red."""
        self.plan(strict=True, isolated=True)
        self.ap("tickets")
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as out:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"haiku": ["low"]}}, out)
        for tid in ("01", "02"):
            code, msg = self.ap("ticket", tid, "route", "--provider", "anthropic",
                                "--model", "haiku", "--effort", "low",
                                "--reason", "synthetic", "--capabilities", caps)
            self.assertEqual(code, 0, msg)
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Autopilot Controller Test")
        os.makedirs(os.path.join(self.root, "src", "core"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "src", "bot"), exist_ok=True)
        with open(os.path.join(self.root, "src", "core", "calc.py"), "w", encoding="utf-8") as f:
            f.write("def add(a,b): return a-b\n")
        with open(os.path.join(self.root, "src", "bot", "calc.py"), "w", encoding="utf-8") as f:
            f.write("def mul(a,b): return a+b\n")
        with open(os.path.join(self.root, "test_core.py"), "w", encoding="utf-8") as f:
            f.write("import unittest\nfrom src.core.calc import add\n"
                    "class Tests(unittest.TestCase):\n"
                    " def test_add(self): self.assertEqual(add(2,3),5)\n")
        with open(os.path.join(self.root, "test_bot.py"), "w", encoding="utf-8") as f:
            f.write("import unittest\nfrom src.bot.calc import mul\n"
                    "class Tests(unittest.TestCase):\n"
                    " def test_mul(self): self.assertEqual(mul(2,3),6)\n")
        self.git("add", "-A")
        self.commit("controller verified fixture")
        def drive(suite=None):
            cmd = [sys.executable, os.path.join(self.a, "controller.py")]
            if suite:
                cmd += ["--suite", suite]
            p = subprocess.run(cmd + ["--advance", "--root", self.root], cwd=self.root,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            try:
                obj = json.loads(p.stdout)
            except ValueError:
                self.fail("Controller invalid JSON: " + p.stdout + p.stderr)
            return p.returncode, obj
        code, first = drive()
        self.assertEqual((code, first["completed"]["action"]), (0, "prepare"), first)
        code, second = drive()
        self.assertEqual((code, second["completed"]["action"]), (0, "start"), second)
        code, blocked = drive()
        self.assertEqual(blocked["status"], "blocked", blocked)
        self.assertEqual(blocked["next"]["reason"], "await-separately-approved-pinned-worker")
        wt1 = self.state()["tickets"][0]["worktree"]["cwd"]
        with open(os.path.join(wt1, "src", "core", "calc.py"), "w", encoding="utf-8") as f:
            f.write("def add(a,b): return a+b\n")
        for expected in ("verify", "finalize", "land", "accept", "release"):
            code, result = drive("test_core.py")
            self.assertEqual(code, 0, result)
            self.assertEqual(result["completed"]["action"], expected, result)
            self.assertFalse(result["model_invoked"])
        self.assertEqual(self.state()["tickets"][0]["status"], "done")
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "released")
        for expected in ("prepare", "start"):
            code, obj = drive()
            self.assertEqual(code, 0, obj)
            self.assertEqual(obj["completed"]["action"], expected)
        wt2 = self.state()["tickets"][1]["worktree"]["cwd"]
        with open(os.path.join(wt2, "src", "bot", "calc.py"), "w", encoding="utf-8") as f:
            f.write("def mul(a,b): return a-b\n")
        code, failed = drive("test_bot.py")
        self.assertNotEqual(code, 0)
        self.assertEqual(failed["status"], "blocked")
        self.assertEqual(self.state()["tickets"][1]["status"], "in-progress")
        self.assertFalse(self.state()["tickets"][1].get("testEvidence"))
        with open(os.path.join(wt2, "src", "bot", "calc.py"), "w", encoding="utf-8") as f:
            f.write("def mul(a,b): return a*b\n")
        for expected in ("verify", "finalize", "land", "accept", "release"):
            code, result = drive("test_bot.py")
            self.assertEqual(code, 0, result)
            self.assertEqual(result["completed"]["action"], expected, result)
        self.assertTrue(all(t["status"] == "done" for t in self.state()["tickets"]))
        self.assertFalse(self.git("status", "--porcelain", "--", "src").stdout.strip())
        self.assertEqual((drive()[1])["status"], "blocked")

    def test_schedule_isolated_preparation_and_reservation(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("bootstrap")
        code, payload = self.ap("schedule")
        self.assertEqual(code, 0, payload)
        plan = json.loads(payload)
        self.assertEqual(plan["selected"][0]["action"], "prepare")
        self.ap("worktree", "01", "prepare")
        code, payload = self.ap("schedule")
        self.assertEqual(code, 0, payload)
        plan = json.loads(payload)
        self.assertEqual(plan["selected"][0]["action"], "start")
        self.assertEqual(plan["reserved"], 1)
        self.assertEqual(plan["selected"][0]["cwd"], self.state()["tickets"][0]["worktree"]["cwd"])

    def test_schedule_blocks_launch_after_recorded_token_threshold(self):
        self.plan()
        self.ap("tickets")
        self.ap("budget", "--tokens", "12")
        self.ap("usage", "01", "--call-id", "test-call-123",
                "--input", "10", "--output", "2", "--source", "manual")
        code, payload = self.ap("schedule")
        self.assertEqual(code, 0, payload)
        self.assertFalse(json.loads(payload)["selected"])
        self.assertIn("recorded-token-budget", [b["reason"] for b in json.loads(payload)["blocked"]])

    def test_strict_isolated_host_evidence_proves_unittest_and_unchanged_code(self):
        self.plan(strict=True, isolated=True)
        self.ap("tickets")
        caps = os.path.join(self.a, "model-capabilities.json")
        with open(caps, "w", encoding="utf-8") as out:
            json.dump({"provider": "anthropic", "model_selection": True,
                       "models": {"haiku": ["low"]}}, out)
        code, out = self.ap("ticket", "01", "route", "--provider", "anthropic",
                            "--model", "haiku", "--effort", "low",
                            "--reason", "synthetic", "--capabilities", caps)
        self.assertEqual(code, 0, out)
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Autopilot Test")
        os.makedirs(os.path.join(self.root, "src", "core"), exist_ok=True)
        with open(os.path.join(self.root, "src", "core", "calc.py"), "w", encoding="utf-8") as out:
            out.write("def add(a, b):\n    return a - b\n")
        with open(os.path.join(self.root, "test_calc.py"), "w", encoding="utf-8") as out:
            out.write("import unittest\nfrom src.core.calc import add\n"
                      "class CalcTest(unittest.TestCase):\n"
                      "    def test_add(self): self.assertEqual(add(2,3),5)\n")
        self.git("add", ".gitignore", "src/core/calc.py", "test_calc.py")
        self.commit("test baseline")
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        self.ap("ticket", "01", "start")
        wt = self.state()["tickets"][0]["worktree"]
        dest = os.path.join(wt["cwd"], "src", "core", "calc.py")
        with open(dest, "w", encoding="utf-8") as out:
            out.write("def add(a, b):\n    return a + b\n")
        code, out = self.ap("worktree", "01", "finalize", "--tests", "1/0")
        self.assertNotEqual(code, 0)
        self.assertIn("host test evidence", out)
        code, out = self.ap("worktree", "01", "verify", "--suite", "test_calc.py")
        self.assertEqual(code, 0, out)
        proof = self.state()["tickets"][0]["testEvidence"]
        self.assertEqual((proof["passed"], proof["failed"]), (1, 0))
        with open(dest, "a", encoding="utf-8") as out_file:
            out_file.write("# changed since independent testing\n")
        code, out = self.ap("worktree", "01", "finalize")
        self.assertNotEqual(code, 0)
        self.assertIn("Source changed after tests", out)
        with open(dest, "w", encoding="utf-8") as out_file:
            out_file.write("def add(a, b):\n    return a + b\n")
        code, out = self.ap("worktree", "01", "finalize", "--tests", "99/0")
        self.assertNotEqual(code, 0)
        self.assertIn("не совпадают", out)
        code, out = self.ap("worktree", "01", "finalize")
        self.assertEqual(code, 0, out)
        code, out = self.ap("worktree", "01", "land", "--tests", "99/0")
        self.assertNotEqual(code, 0)
        code, out = self.ap("worktree", "01", "land")
        self.assertEqual(code, 0, out)
        commit = self.state()["tickets"][0]["worktree"]["landedCommit"]
        code, out = self.ap("ticket", "01", "done", "--commit", commit[:12])
        self.assertEqual(code, 0, out)
        code, out = self.ap("worktree", "01", "release")
        self.assertEqual(code, 0, out)

    def test_host_side_finalize_then_land_and_done(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("config", "user.name", "Autopilot Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("add", ".gitignore")
        self.commit("bootstrap")
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        self.ap("ticket", "01", "start")
        wt = self.state()["tickets"][0]["worktree"]
        src = os.path.join(wt["cwd"], "src", "core")
        os.makedirs(src, exist_ok=True)
        with open(os.path.join(src, "change.txt"), "w", encoding="utf-8") as stream:
            stream.write("sandboxed code edit\n")
        code, out = self.ap("worktree", "01", "finalize", "--tests", "2/0")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["tickets"][0]["tests"]["passed"], 2)
        code, out = self.ap("worktree", "01", "land", "--tests", "2/0")
        self.assertEqual(code, 0, out)
        self.assertEqual(read(os.path.join(self.root, "src", "core", "change.txt")),
                         "sandboxed code edit\n")
        commit = self.state()["tickets"][0]["worktree"]["landedCommit"]
        code, out = self.ap("ticket", "01", "done", "--commit", commit[:12])
        self.assertEqual(code, 0, out)
        code, out = self.ap("worktree", "01", "release")
        self.assertEqual(code, 0, out)

    def test_isolated_ticket_full_lifecycle(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("checkpoint: before executor")
        code, out = self.ap("ticket", "01", "start")
        self.assertNotEqual(code, 0)
        self.assertIn("подготовь worktree", out)
        code, out = self.ap("worktree", "02", "prepare")
        self.assertNotEqual(code, 0)
        self.assertIn("зависимости", out)
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        wt = self.state()["tickets"][0]["worktree"]
        self.assertTrue(os.path.isdir(wt["cwd"]))
        code, out = self.ap("ticket", "01", "start")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "01", "done", "--tests", "3/0",
                            "--commit", wt["baseCommit"][:12])
        self.assertNotEqual(code, 0)
        self.assertIn("сначала интегрируй worktree", out)
        with open(os.path.join(wt["cwd"], "worker.txt"), "w", encoding="utf-8") as stream:
            stream.write("executor edit\n")
        self.git("-C", wt["cwd"], "add", "worker.txt")
        result = subprocess.run(
            ["git", "-C", wt["cwd"], "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-qm", "T01: worker edit"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        code, out = self.ap("worktree", "01", "land", "--tests", "3/0")
        self.assertEqual(code, 0, out)
        wt = self.state()["tickets"][0]["worktree"]
        self.assertEqual(wt["status"], "landed")
        self.assertEqual(read(os.path.join(self.root, "worker.txt")), "executor edit\n")
        code, out = self.ap("ticket", "01", "done", "--commit", wt["landedCommit"][:12])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.state()["tickets"][0]["status"], "done")
        code, out = self.ap("worktree", "01", "release")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.isdir(wt["cwd"]))
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "released")

    def test_isolated_done_never_bypasses_preparation(self):
        self.plan(isolated=True)
        self.ap("tickets")
        sha = self.commit("T01")
        code, out = self.ap("ticket", "01", "done", "--tests", "3/0", "--commit", sha)
        self.assertNotEqual(code, 0)
        self.assertIn("требует интеграции worktree", out)

    def test_ticket_source_change_cannot_invalidate_live_worktree(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("checkpoint: worktree baseline")
        code, out = self.ap("worktree", "01", "prepare")
        self.assertEqual(code, 0, out)
        self.write("tickets/01-karkas.md",
                   ticket("01", "Other requirements", "R01, R05", "—", ["src/core/"], 1))
        code, out = self.ap("tickets")
        self.assertNotEqual(code, 0)
        self.assertIn("существующем worktree", out)

    def test_isolated_ticket_rejects_failed_tests_before_landing(self):
        self.plan(isolated=True)
        self.ap("tickets")
        self.git("add", ".gitignore")
        self.commit("checkpoint: before executor")
        self.ap("worktree", "01", "prepare")
        self.ap("ticket", "01", "start")
        code, out = self.ap("worktree", "01", "land", "--tests", "0/1")
        self.assertNotEqual(code, 0)
        self.assertIn("пройденные тесты", out)
        self.assertEqual(self.state()["tickets"][0]["worktree"]["status"], "prepared")

    def test_finish_rejects_incomplete_work(self):
        self.plan()
        self.ap("tickets")
        code, out = self.ap("finish", "--result", "ложный успех")
        self.assertNotEqual(code, 0)
        self.assertIn("finish заблокирован", out)
        self.assertIsNone(self.state()["finishedAt"])

    def test_finish_requires_all_gates(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        sha1 = self.commit("T01")
        self.ap("ticket", "01", "done", "--tests", "2/0", "--commit", sha1)
        self.ap("ticket", "02", "start")
        sha2 = self.commit("T02")
        self.ap("ticket", "02", "done", "--tests", "2/0", "--commit", sha2)
        code, out = self.ap("finish", "--result", "ложный успех")
        self.assertNotEqual(code, 0)
        self.assertIn("проверки G1, G2, G3, G4", out)

    def test_ticket_done_rejects_failed_tests_and_invalid_commit(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        c, out = self.ap("ticket", "01", "done", "--tests", "0/1", "--commit", "badc0de")
        self.assertNotEqual(c, 0)
        self.assertIn("без успешных тестов", out)
        c, out = self.ap("ticket", "01", "done", "--tests", "1/0", "--commit", "badc0de")
        self.assertNotEqual(c, 0)
        self.assertIn("существующий коммит", out)

    def test_review_rolls_back_requirement_status(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        sha = self.commit("T01")
        self.ap("ticket", "01", "done", "--tests", "3/0",
                "--commit", sha, "--placeholder", "R05")
        self.assertIn("placeholder", self.manifest())
        self.ap("ticket", "01", "review")
        self.assertRegex(self.manifest(), r"\| R05 \|[^\n]*\| in-ticket \|")
        self.ap("ticket", "01", "done")
        self.assertRegex(self.manifest(), r"\| R05 \|[^\n]*\| placeholder \|")

    def test_plan_requires_rows_and_tickets(self):
        self.init()
        code, out = self.ap("check-plan")
        self.assertNotEqual(code, 0)
        self.assertIn("манифест отсутствует или пуст", out)
        self.assertIn("план пуст", out)
        self.assertFalse(self.state()["gates"]["G3"]["ok"])

    def test_changed_ticket_resets_previous_acceptance(self):
        self.plan()
        self.ap("tickets")
        self.ap("ticket", "01", "start")
        sha = self.commit("T01")
        self.ap("ticket", "01", "done", "--tests", "3/0", "--commit", sha)
        self.write("tickets/01-karkas.md", ticket("01", "Новая версия", "R01, R05", "—", ["src/core/"], 1))
        self.ap("tickets")
        t = {t["id"]: t for t in self.state()["tickets"]}["01"]
        self.assertEqual(t["status"], "pending")
        self.assertRegex(self.manifest(), r"\| R05 \|[^\n]*\| in-ticket \|")

    def test_finish_lands_the_run(self):
        self.ready_to_finish()
        code, out = self.ap("finish", "--result", "Бот принимает заявки")
        s = self.state()
        self.assertTrue(s["finishedAt"])
        self.assertFalse(s["dir"].endswith("--wip"))
        self.assertTrue(os.path.isdir(os.path.join(self.a, s["dir"])))
        self.assertTrue(all(x["status"] in ("done", "skipped") for x in s["stages"]))
        self.assertIn("| сдан | Бот принимает заявки |", read(os.path.join(self.a, "README.md")))
        self.assertEqual(s["result"], "Бот принимает заявки")
        self.assertIn("R", self.git("status", "--short").stdout)    # переименование через git mv

    def test_finish_rechecks_requirement_added_after_g3_even_if_marked_done(self):
        self.ready_to_finish()
        self.write("manifest.md", self.manifest() +
                   "| G01 | «новая функция» | done | — | T99 |\n")
        code, out = self.ap("finish", "--result", "необоснованная сдача")
        self.assertNotEqual(code, 0, out)
        self.assertIn("G3", out)
        self.assertIsNone(self.state()["finishedAt"])

    def test_finish_rechecks_ticket_edited_after_g3(self):
        self.ready_to_finish()
        self.write("tickets/01-karkas.md",
                   ticket("01", "Изменённые критерии", "R01, R05", "—",
                          ["src/core/"], 1, "да — фундамент", "сильная"))
        code, out = self.ap("finish", "--result", "устаревший план")
        self.assertNotEqual(code, 0, out)
        self.assertIsNone(self.state()["finishedAt"])

    def test_finish_rejects_changed_requirement_words_after_g3(self):
        self.ready_to_finish()
        self.write("manifest.md", self.manifest().replace(
            "«принимает заявки»", "«удаляет заявки»"))
        code, out = self.ap("finish", "--result", "устаревший бриф")
        self.assertNotEqual(code, 0, out)
        self.assertIn("измен", out.lower())
        self.assertIsNone(self.state()["finishedAt"])

    def test_rechecking_changed_plan_revokes_earlier_acceptance(self):
        self.ready_to_finish()
        self.write("manifest.md", self.manifest().replace(
            "«принимает заявки»", "«показывает чужие заявки»"))
        code, out = self.ap("check-plan")
        self.assertEqual(code, 0, out)
        self.assertIn("G3: трасса сходится", out)
        state = self.state()
        self.assertTrue(state["gates"]["G3"]["ok"])
        self.assertTrue(all(not state["gates"][g]["ok"] for g in ("G1", "G2", "G4")))
        self.assertIsNone(state["blind"])
        code, out = self.ap("finish", "--result", "устаревшая слепая приёмка")
        self.assertNotEqual(code, 0, out)
        self.assertIn("проверки G1, G2, G4", out)
        self.assertIsNone(self.state()["finishedAt"])

    def test_rechecking_unchanged_plan_preserves_valid_acceptance(self):
        self.ready_to_finish()
        before = self.state()["planContractDigest"]
        code, out = self.ap("check-plan")
        self.assertEqual(code, 0, out)
        state = self.state()
        self.assertEqual(state["planContractDigest"], before)
        self.assertTrue(all(state["gates"][g]["ok"] for g in ("G1", "G2", "G3", "G4")))
        code, out = self.ap("finish", "--result", "всё подтверждено")
        self.assertEqual(code, 0, out)

    def test_finish_detects_removed_redundant_completed_ticket(self):
        self.ready_to_finish()
        # Let T02 also cover R05, so removing T01 cannot be discovered merely
        # from the list of requirements that still have one remaining owner.
        self.write("tickets/02-priem.md",
                   ticket("02", "Приём", "R01, R02, R05, A01", "01",
                          ["src/bot/"], 2))
        code, out = self.ap("tickets")
        self.assertEqual(code, 0, out)
        code, out = self.ap("ticket", "02", "start")
        self.assertEqual(code, 0, out)
        sha = self.commit("T02 revised")
        code, out = self.ap("ticket", "02", "done", "--tests", "5/0",
                            "--commit", sha)
        self.assertEqual(code, 0, out)
        code, out = self.ap("check-plan")
        self.assertEqual(code, 0, out)
        self.assertIn("G3: трасса сходится", out)
        # A changed plan deliberately revokes G1/G2/G4. Re-certify them
        # before testing *removal detection*, not that separate safety gate.
        for command in (("stage", "spec", "done"),
                        ("coverage", "found=0", "fixed=0", "deferred=0"),
                        ("blind", "checked=4", "matched=4")):
            code, out = self.ap(*command)
            self.assertEqual(code, 0, out)
        self.assertTrue(all(self.state()["gates"][g]["ok"]
                            for g in ("G1", "G2", "G3", "G4")))
        os.unlink(os.path.join(self.dir, "tickets", "01-karkas.md"))
        code, out = self.ap("finish", "--result", "удалённый таск")
        self.assertNotEqual(code, 0, out)
        self.assertIn("измен", out.lower())
        self.assertIsNone(self.state()["finishedAt"])

    def test_finish_rejects_done_ticket_after_git_history_rewrite(self):
        self.ready_to_finish()
        old_state = self.state()
        lost = old_state["tickets"][1]["commit"]
        kept = old_state["tickets"][0]["commit"]
        self.assertNotEqual(kept, lost)
        # Keep the state and working files intact; only HEAD ancestry changes.
        result = self.git("reset", "--soft", kept)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.git("merge-base", "--is-ancestor", lost, "HEAD").returncode, 0)
        code, out = self.ap("finish", "--result", "ложная сдача после rebase")
        self.assertNotEqual(code, 0)
        self.assertIn("коммиты сданных тасков отсутствуют", out)
        self.assertIn("02", out)
        after = self.state()
        self.assertIsNone(after["finishedAt"])
        self.assertEqual(after["tickets"][1]["status"], "done")
        self.assertEqual(after["dir"], old_state["dir"])
        self.assertEqual(after["stages"], old_state["stages"])
        self.assertNotIn("ложная сдача после rebase", read(os.path.join(self.a, "README.md")))

    def test_reopen_puts_wip_back(self):
        self.ready_to_finish()
        self.ap("finish", "--result", "готово")
        self.ap("reopen")
        s = self.state()
        self.assertTrue(s["dir"].endswith("--wip"))
        self.assertIsNone(s["finishedAt"])
        self.assertEqual(self.stage("manifest")["status"], "active")
        self.assertEqual(self.stage("final")["status"], "pending")
        self.assertNotIn("finishedAt", self.stage("final"))

    def test_commits_flags_a_done_ticket_whose_commit_left_history(self):
        self.plan()
        self.ap("tickets")
        commit = lambda m: self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", m)
        commit("T01")
        kept = self.git("rev-parse", "--short", "HEAD").stdout.strip()
        commit("T02")
        lost = self.git("rev-parse", "--short", "HEAD").stdout.strip()
        self.ap("ticket", "01", "done", "--tests", "1/0", "--commit", kept)
        self.ap("ticket", "02", "done", "--tests", "1/0", "--commit", lost)
        events = len(self.state()["log"])
        code, out = self.ap("commits")
        self.assertIn("коммиты сданных тасков на месте", out)
        self.git("reset", "-q", "--hard", kept)
        code, out = self.ap("commits")
        self.assertEqual(code, 0, out)
        self.assertIn("! таск 02: коммита %s нет в истории" % lost, out)
        self.assertNotIn("таск 01", out)
        self.assertEqual(self.state()["tickets"][1]["status"], "done")   # сбрасывает оркестратор
        self.assertEqual(len(self.state()["log"]), events)               # проверка — не событие


class Pure(unittest.TestCase):
    """Функции без процесса: опознание своего сервера и версия навыка."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("ap", AP)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_is_ours(self):
        a = self.m.A
        self.assertTrue(self.m.is_ours("/usr/bin/python3 -m http.server 8000 --bind 127.0.0.1 --directory %s" % a))
        self.assertFalse(self.m.is_ours("python3 -m http.server 8000 --directory %s2" % a))
        self.assertFalse(self.m.is_ours("node http-server --directory %s" % a))

    def test_version(self):
        self.assertEqual(self.m._version('---\nname: x\nmetadata:\n  version: "2.0.1"\n---\nversion: 9'), (2, 0, 1))
        self.assertIsNone(self.m._version("---\nname: x\n---\nversion: 3\n"))

    def test_skill_declares_a_version(self):
        text = read(os.path.join(SKILL, "SKILL.md"))
        self.assertIsNotNone(self.m._version(text))


if __name__ == "__main__":
    unittest.main()
