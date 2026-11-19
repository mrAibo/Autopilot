"""Лёгкие профили обычного прогона (R01), подсказка о размере контекста (R02), замер ходов оркестратора
(R04), маршрут fix-таска и учёт модели (R09), `.meta.json` с BOM и `collapse_agents` (G01, G02)."""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import test_ap
from test_ap import ticket
from test_spend_accounting import load_ap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MEASURE = os.path.join(REPO, "tools", "measure-run.py")
PHASES = os.path.join(test_ap.SKILL, "phases")
sys.path.insert(0, os.path.join(test_ap.SKILL, "tools"))
import agent_profiles  # noqa: E402
import run_log  # noqa: E402

ROLES = {"autopilot-executor": "Read, Grep, Glob, Bash, Edit, Write",
         "autopilot-reviewer": "Read, Grep, Glob, Bash",
         "autopilot-acceptance": "Read, Grep, Glob, Bash",
         "autopilot-explorer": "Read, Grep, Glob"}


def phase(name):
    with open(os.path.join(PHASES, name), encoding="utf-8") as f:
        return f.read()


class Project(unittest.TestCase):
    """Временный проект test_ap.Run; папка настроек Claude Code и AUTOPILOT_HOME — временные."""

    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)
        self.cfg = tempfile.mkdtemp(prefix="ap-cfg-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.cfg, ignore_errors=True))
        env = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.cfg})
        env.start()
        self.addCleanup(env.stop)
        self.agents = os.path.join(self.h.root, ".claude", "agents")

    def init(self, *extra):
        return self.h.ap("init", "--slug", "second-run", "--title", "Бот", "--skill-dir", test_ap.SKILL, *extra)

    def listing(self):
        return sorted(os.listdir(self.agents)) if os.path.isdir(self.agents) else []

    def profile(self, name):
        with open(os.path.join(self.agents, name + ".md"), encoding="utf-8") as f:
            return f.read()


class PermanentProfiles(Project):
    def test_init_writes_four_light_profiles_without_model_effort_or_task_path(self):
        out = self.h.init()
        self.assertEqual(sorted(os.listdir(self.agents)), sorted(n + ".md" for n in ROLES))
        run = self.h.state()["dir"]
        for name, tools in ROLES.items():
            text = self.profile(name)
            head = text.split("\n---", 1)[0] + "\n"
            self.assertIn("name: %s\n" % name, head)
            self.assertIn("tools: %s\n" % tools, head)
            self.assertNotRegex(head, r"(?m)^(model|effort):")
            for forbidden in ("tickets/", run, run.removesuffix("--wip"), "Task brief", ".autopilot/"):
                self.assertNotIn(forbidden, text, name)
        self.assertIn("лёгкие профили записаны", out)

    def test_second_init_rewrites_nothing_unchanged_restores_edited_and_spares_other_files(self):
        self.h.init()
        old, foreign = "autopilot-executor-01-old-run.md", "my-own-agent.md"
        for name in (old, foreign):
            with open(os.path.join(self.agents, name), "w", encoding="utf-8") as f:
                f.write("чужой текст\n")
        edited = os.path.join(self.agents, "autopilot-reviewer.md")
        with open(edited, "w", encoding="utf-8") as f:
            f.write("правка человека\n")
        stamps = {n: os.stat(os.path.join(self.agents, n + ".md")).st_mtime_ns for n in ROLES}
        time.sleep(0.05)
        code, out = self.init("--force")
        self.assertEqual(code, 0, out)
        self.assertIn("autopilot-reviewer", out.split("лёгкие профили записаны", 1)[1].splitlines()[0])
        reference = {path.stem: text for path, text in agent_profiles.permanent_profiles()}
        self.assertEqual(self.profile("autopilot-reviewer"), reference["autopilot-reviewer"])
        for name in ROLES:
            if name != "autopilot-reviewer":
                self.assertEqual(os.stat(os.path.join(self.agents, name + ".md")).st_mtime_ns, stamps[name], name)
        for name in (old, foreign):
            with open(os.path.join(self.agents, name), encoding="utf-8") as f:
                self.assertEqual(f.read(), "чужой текст\n")

    def test_third_init_with_nothing_to_write_prints_no_profile_line(self):
        self.h.init()
        code, out = self.init("--force")
        self.assertEqual(code, 0, out)
        self.assertNotIn("лёгкие профили", out)

    def test_strict_init_creates_no_permanent_profiles(self):
        self.h.init(strict=True)
        self.assertFalse(any(os.path.exists(os.path.join(self.agents, n + ".md")) for n in ROLES))

    def test_write_failure_is_a_bang_line_not_a_crash(self):
        with open(os.path.join(self.h.root, ".claude"), "w", encoding="utf-8") as f:
            f.write("не папка")                           # .claude/agents создать нельзя
        out = self.h.init()
        self.assertRegex(out, r"(?m)^  ! лёгкие профили не записаны")
        self.assertTrue(os.path.isfile(os.path.join(self.h.a, "state.js")))

    def test_profiles_stay_under_the_existing_gitignore_rule(self):
        self.h.init()
        for name in ROLES:
            r = self.h.git("check-ignore", "-q", ".claude/agents/%s.md" % name)
            self.assertEqual(r.returncode, 0, name)

    def test_role_of_knows_permanent_and_old_names(self):
        for name, role in (("autopilot-executor", "executor"), ("autopilot-reviewer", "reviewer"),
                           ("autopilot-acceptance", "acceptance"), ("autopilot-explorer", "explorer"),
                           ("autopilot-executor-03-escalation", "executor"),
                           ("autopilot-executor-repair-2026-11-15-x", "executor"),
                           ("autopilot-reviewer-2026-11-15-x", "reviewer"),
                           ("autopilot-executors", "agent"), ("general-purpose", "agent"), (None, "agent")):
            self.assertEqual(run_log.role_of(name), role, name)
        ap = load_ap()
        self.assertIsNone(ap.executor_ticket("autopilot-executor"))
        self.assertEqual(ap.executor_ticket("autopilot-executor-03-x"), "03")


class UserLevelProfiles(Project):
    def test_question_is_asked_until_answered_and_refusal_writes_nothing(self):
        out = self.h.init()
        self.assertEqual(len(re.findall(r"(?m)^  \? ", out)), 1, out)
        code, out = self.h.ap("agents", "install-user")
        self.assertNotEqual(code, 0, out)
        code, out = self.h.ap("agents", "install-user", "--by-user", "--decline")   # и слова, и отказ сразу
        self.assertNotEqual(code, 0, out)
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "agents")))
        self.assertIn("  ? ", self.init("--force")[1])                               # ответа всё ещё нет
        code, out = self.h.ap("agents", "install-user", "--decline")
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(os.path.join(self.cfg, "agents")))
        self.assertNotIn("  ? ", self.init("--force")[1])

    def test_consent_with_a_quote_writes_four_files_and_stops_the_question(self):
        self.h.init()
        code, out = self.h.ap("agents", "install-user", "--by-user", "да, поставь профили")
        self.assertEqual(code, 0, out)
        target = os.path.join(self.cfg, "agents")
        self.assertEqual(sorted(os.listdir(target)), sorted(n + ".md" for n in ROLES))
        with open(os.path.join(target, "autopilot-explorer.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), self.profile("autopilot-explorer"))
        self.assertNotIn("  ? ", self.init("--force")[1])


class Phases(unittest.TestCase):
    def test_every_role_names_its_light_profile_in_its_own_phase(self):
        for name, needles in (("5-subagents.md", ("autopilot-executor", "general-purpose")),
                              ("3-spec.md", ("autopilot-explorer", "autopilot-reviewer")),
                              ("6-review.md", ("autopilot-reviewer", "autopilot-executor")),
                              ("8-final.md", ("autopilot-acceptance", "autopilot-executor")),
                              ("9-memory.md", ("autopilot-executor",)),
                              ("0-preflight.md", ("autopilot-explorer",)),
                              ("5-host-claude.md", tuple(ROLES))):
            text = phase(name)
            for needle in needles:
                self.assertIn(needle, text, name)

    def test_host_file_has_the_fallback_and_the_model_rule_and_keeps_strict_text(self):
        text = phase("5-host-claude.md")
        ordinary = text.split("## Ordinary run", 1)[1]
        for needle in ("Agent type not found", "general-purpose", "never a stop", "model", "effort",
                       "Always pass `model` and `effort`", "agents install-user", "ticket F1 route"):
            self.assertIn(needle, ordinary)
        self.assertIn("never fall back", text.split("## Ordinary run", 1)[0])

    def test_hint_lines_are_described_as_hints_that_can_come_twice(self):
        for name in ("0-instruments.md", "0-modes.md"):
            self.assertRegex(phase(name), r"(?i)two", name)
        self.assertIn("AUTOPILOT_CONTEXT_HINT", phase("0-instruments.md"))
        self.assertIn("starts with the context line", phase("0-preflight.md"))


def transcript(path, *lines, raw=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(x) if not isinstance(x, str) else x for x in lines) + raw)
    return path


def reply(i, side=False, **usage):
    return {"type": "assistant", "isSidechain": side, "timestamp": "2026-11-16T10:00:00.000Z",
            "message": {"id": i, "role": "assistant", "model": "m", "usage": usage,
                        "content": [{"type": "text", "text": "СЕКРЕТНЫЙ ТЕКСТ"}]}}


class ContextReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ap = load_ap()

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ap-ctx-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.d, ignore_errors=True))

    def test_sums_input_and_both_cache_counts_of_the_last_main_reply(self):
        p = transcript(os.path.join(self.d, "s.jsonl"),
                       reply("a", input_tokens=1, cache_read_input_tokens=9),
                       reply("b", input_tokens=5, cache_read_input_tokens=100, cache_creation_input_tokens=20, output_tokens=999),
                       reply("c", side=True, input_tokens=777_000),                       # субагент — не считается
                       {"type": "user", "message": {"role": "user", "content": "вопрос"}},
                       raw='\n{"type": "assistant", "mess')                               # оборванная последняя строка
        self.assertEqual(self.ap.last_context_tokens(p), 125)

    def test_only_the_tail_is_read_and_a_cut_first_line_is_skipped(self):
        p = os.path.join(self.d, "big.jsonl")
        filler = json.dumps(reply("old", input_tokens=1)) + "\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(filler * (self.ap.CONTEXT_TAIL // len(filler) + 50))               # заведомо больше хвоста
            f.write(json.dumps(reply("last", input_tokens=42)) + "\n")
        self.assertEqual(self.ap.last_context_tokens(p), 42)

    def test_missing_unreadable_or_replyless_log_is_none(self):
        self.assertIsNone(self.ap.last_context_tokens(os.path.join(self.d, "нет.jsonl")))
        empty = transcript(os.path.join(self.d, "e.jsonl"), {"type": "user", "message": {"role": "user"}})
        self.assertIsNone(self.ap.last_context_tokens(empty))

    def test_truncated_folder_name_is_found_by_common_prefix(self):
        proj = "C:/" + "x" * 150 + "/proj"
        want = re.sub(r"[^A-Za-z0-9]", "-", proj)
        cfg = os.path.join(self.d, "cfg")
        transcript(os.path.join(cfg, "projects", want[:110], "s.jsonl"), reply("a", input_tokens=7))
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": cfg}), mock.patch.object(self.ap, "A", proj + "/.autopilot"):
            self.assertEqual(self.ap.last_context_tokens(), 7)


class ContextHintLine(Project):
    def journal(self, tokens):
        want = re.sub(r"[^A-Za-z0-9]", "-", self.h.root)
        return transcript(os.path.join(self.cfg, "projects", want, "s.jsonl"),
                          reply("a", input_tokens=10, cache_read_input_tokens=tokens - 10))

    def arrows(self, out):
        return re.findall(r"(?m)^  ↑ .*$", out)

    def test_stage_build_review_final_and_init_print_exactly_one_line_above_the_threshold(self):
        self.journal(200_000)
        out = self.h.init()
        self.assertEqual(len(self.arrows(out)), 1, out)
        self.assertIn("200 тыс.", out)
        self.assertIn("/autopilot", self.arrows(out)[0])
        for sid in ("build", "review", "final"):
            code, out = self.h.ap("stage", sid)
            self.assertEqual((code, len(self.arrows(out))), (0, 1), out)
            self.assertNotIn("СЕКРЕТНЫЙ", out)
        self.assertEqual(self.arrows(self.h.ap("stage", "spec")[1]), [])              # другие этапы — без подсказки
        self.assertEqual(self.arrows(self.h.ap("stage", "build", "done")[1]), [])

    def test_below_threshold_off_and_custom_threshold(self):
        self.journal(120_000)
        self.assertEqual(self.arrows(self.h.init()), [])
        for value, expected in (("100000", 1), ("0", 0), ("nonsense", 0), ("120000", 0)):
            with mock.patch.dict(os.environ, {"AUTOPILOT_CONTEXT_HINT": value}):
                code, out = self.h.ap("stage", "build")
            self.assertEqual((code, len(self.arrows(out))), (0, expected), (value, out))

    def test_non_ascii_digit_threshold_is_ignored_not_a_crash(self):
        self.journal(200_000)
        self.h.init()
        with mock.patch.dict(os.environ, {"AUTOPILOT_CONTEXT_HINT": "²"}):
            code, out = self.h.ap("stage", "build")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.arrows(out)), 1, out)

    def test_no_journal_means_no_line_and_no_failure(self):
        out = self.h.init()
        self.assertEqual(self.arrows(out), [])
        code, out = self.h.ap("stage", "build")
        self.assertEqual((code, self.arrows(out)), (0, []))


def stamp(minute, second=0):
    return "2026-11-16T10:%02d:%02dZ" % (minute, second)


def main_reply(i, at, tool=None, **usage):
    content = [{"type": "text", "text": "СЕКРЕТНЫЙ ТЕКСТ"}]
    if tool:
        content.append({"type": "tool_use", "id": tool[0], "name": tool[1], "input": tool[2]})
    return {"type": "assistant", "timestamp": at, "isSidechain": False,
            "message": {"id": i, "role": "assistant", "content": content, "usage": dict({"input_tokens": 10}, **usage)}}


def launched(tool_id, at, agent_id):
    return {"type": "user", "timestamp": at, "toolUseResult": {"isAsync": True, "status": "async_launched", "agentId": agent_id},
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "СЕКРЕТНЫЙ ОТВЕТ"}]}}


class MeasureRun(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ap-measure-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.d, ignore_errors=True))
        self.project = os.path.join(self.d, "proj")
        os.makedirs(self.project)
        self.cfg = os.path.join(self.d, "cfg")
        self.logs = os.path.join(self.cfg, "projects", re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(self.project)))

    def build(self, bom=True):
        sub = os.path.join(self.logs, "s1", "subagents")
        os.makedirs(sub)
        def agent(aid, first, last, ctx, meta):
            transcript(os.path.join(sub, "agent-%s.jsonl" % aid),
                       dict(reply("x1", input_tokens=1000, cache_read_input_tokens=ctx - 1000), timestamp=first, isSidechain=True),
                       dict(reply("x2", input_tokens=1000, cache_read_input_tokens=ctx + 5000), timestamp=last, isSidechain=True))
            with open(os.path.join(sub, "agent-%s.meta.json" % aid), "w", encoding="utf-8-sig" if bom else "utf-8") as f:
                f.write(json.dumps(meta))

        agent("a1", stamp(1), stamp(5), 12_000, {"agentType": "autopilot-executor-01-x", "description": "Таск 01: расчёт"})
        agent("a2", stamp(7), stamp(8), 8_000, {"agentType": "autopilot-reviewer-x", "description": "Ревью таска 01"})
        transcript(os.path.join(self.logs, "s1.jsonl"),
                   main_reply("m1", stamp(0), ("tu1", "Agent", {"subagent_type": "autopilot-executor-01-x", "prompt": "СЕКРЕТНЫЙ ПРОМПТ"}), cache_read_input_tokens=100_000),
                   launched("tu1", stamp(0, 1), "a1"),
                   main_reply("m2", stamp(5, 30), ("t1", "Bash", {"command": "git status"}), cache_read_input_tokens=110_000),
                   main_reply("m3", stamp(6), ("t2", "Edit", {"file_path": "x"}), cache_read_input_tokens=111_000),
                   main_reply("m4", stamp(6, 30), ("tu2", "Agent", {"subagent_type": "autopilot-reviewer-x"}), cache_read_input_tokens=112_000),
                   launched("tu2", stamp(6, 31), "a2"),
                   main_reply("m5", stamp(8, 30), cache_read_input_tokens=113_000))      # хвост: следующего запуска нет

    def run_measure(self, *args):
        env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg)
        r = subprocess.run([sys.executable, MEASURE, self.project, *args], capture_output=True, text=True,
                           encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_start_context_agent_type_and_landing_table_with_bom_meta(self):
        self.build(bom=True)
        out = self.run_measure()
        line = next(x for x in out.splitlines() if x.startswith("Таск 01"))
        self.assertRegex(line, r"\s12K\s")                                           # стартовый контекст
        self.assertIn("autopilot-executor-01-x", line)                               # тип агента из meta.json с BOM
        self.assertRegex(out, r"autopilot-reviewer-\*\s+1\s+8K")                    # свод по типам: семейство и старт
        self.assertIn("Ходы оркестратора между субагентами", out)
        self.assertRegex(out, r"исполнитель\s+1\s+3\s+3\.0")                         # шаги m2, m3 и запуск m4
        self.assertIn("посадка таска (окна после исполнителя): 1, в среднем 3.0 шага", out)
        for secret in ("СЕКРЕТНЫЙ", "git status"):
            self.assertNotIn(secret, out)

    def test_all_mode_prints_only_the_two_summary_tables(self):
        self.build(bom=False)
        out = self.run_measure("all")
        self.assertIn("Сессий с субагентами: 1 из 1", out)
        self.assertIn("Стартовый контекст по типам агентов", out)
        self.assertIn("посадка таска (окна после исполнителя): 1", out)
        self.assertNotIn("Структура расхода", out)


class BomAndCollapse(unittest.TestCase):
    def test_meta_json_with_bom_gives_the_agent_type(self):
        d = tempfile.mkdtemp(prefix="ap-bom-")
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        transcript(os.path.join(d, "agent-aaa.jsonl"), dict(reply("m", input_tokens=3), timestamp="2026-06-01T11:00:00Z"))
        with open(os.path.join(d, "agent-aaa.meta.json"), "w", encoding="utf-8-sig") as f:
            f.write(json.dumps({"agentType": "autopilot-reviewer-x"}))
        got = run_log.usage_by_agent(d, "2026-06-01T10:00:00+00:00")
        self.assertEqual([a["agent_type"] for a in got], ["autopilot-reviewer-x"])

    def test_hook_row_for_one_type_does_not_drop_journal_rows_of_other_types(self):
        row = lambda agent_type, agent=None, **kw: dict({"k": "executor", "agent_type": agent_type, "agent": agent, "input": 1}, **kw)
        rows = [row("autopilot-executor-01-a"),                                      # строка хука
                row("autopilot-executor-01-a", "a1", input=10),                      # то же — дубль хука, отбрасывается
                row("autopilot-reviewer-x", "r1", input=20),                         # хука на ревьюера нет — остаётся
                row("general-purpose", "g1", input=30),
                row("autopilot-reviewer-x", "r2", input=40)]
        kept = run_log.collapse_agents(rows)
        self.assertEqual(sorted(r["input"] for r in kept), [1, 20, 30, 40])

    def test_without_any_hook_row_journal_rows_all_stay(self):
        rows = [{"k": "executor", "agent_type": "autopilot-executor-01-a", "agent": "a1", "input": 5}]
        self.assertEqual(run_log.collapse_agents(rows), rows)


class FixTicketRoute(Project):
    def fix(self):
        self.h.init()
        self.h.write("tickets/F1-branch-fix.md", ticket("F1", "Ремонт ветки", "R01", "—", ["src/core/"], 3, "да — ремонт ветки", "сильная"))
        self.assertEqual(self.h.ap("tickets")[0], 0)

    def route(self, *args):
        return self.h.ap("ticket", "F1", "route", *args)

    def routing(self):
        return next(t for t in self.h.state()["tickets"] if t["id"] == "F1").get("routing")

    def test_ordinary_run_records_the_route_without_a_profile(self):
        self.fix()
        before = self.listing()
        code, out = self.route("--model", "sonnet", "--effort", "high", "--reason", "ремонт ветки")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.routing(), {"provider": "anthropic", "model": "sonnet", "effort": "high", "reason": "ремонт ветки"})
        self.assertEqual(self.listing(), before)

    def test_fable_and_unapproved_opus_and_missing_reason_are_refused(self):
        self.fix()
        for model in ("fable", "claude-fable-5-2", "opus", "claude-opus-4-1"):
            code, out = self.route("--model", model, "--effort", "high", "--reason", "x")
            self.assertNotEqual(code, 0, (model, out))
            self.assertIsNone(self.routing(), model)
        self.assertNotEqual(self.route("--model", "sonnet", "--effort", "high")[0], 0)
        self.assertNotEqual(self.route("--model", "sonnet", "--reason", "x")[0], 0)
        self.assertIsNone(self.routing())

    def test_strict_run_still_needs_its_registered_repair_agent(self):
        self.h.init(strict=True)
        self.h.write("tickets/F1-branch-fix.md", ticket("F1", "Ремонт ветки", "R01", "—", ["src/core/"], 3, "да — ремонт ветки", "сильная"))
        self.assertEqual(self.h.ap("tickets")[0], 0)
        code, out = self.route("--model", "sonnet", "--effort", "high", "--reason", "x")
        self.assertNotEqual(code, 0, out)                                            # прежняя строгая ветка: без модели/профиля отказ
        self.assertIsNone(self.routing())


class ReportRunModels(Project):
    def test_no_unspecified_model_where_the_subagent_journal_has_one(self):
        self.h.init()
        run = self.h.state()["dir"]
        ticket_row = lambda tid, act: {"run": run, "k": "ticket", "id": tid, "act": act}
        spent = lambda agent_type, ticket_id, model, **kw: dict(
            {"run": run, "k": "executor", "agent": "x" + agent_type[-3:] + ticket_id, "agent_type": agent_type, "role": "executor",
             "ticket": ticket_id, "model": model, "input": 100, "output": 50}, **kw)
        rows = [ticket_row("01", "start"), spent("general-purpose", "01", "claude-haiku-5-5"), ticket_row("01", "done"),
                ticket_row("F1", "start"), spent("general-purpose", "F1", "claude-sonnet-5-5"), ticket_row("F1", "done")]
        with open(os.path.join(self.h.a, "run-log.jsonl"), "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r) for r in rows) + "\n")
        code, out = self.h.ap("report-run")
        self.assertEqual(code, 0, out)
        block = out[out.index("## Модели"):]
        self.assertNotIn("не указана", block)
        self.assertIn("| claude-haiku-5-5 | 1 |", block)
        self.assertIn("| claude-sonnet-5-5 | 1 |", block)                            # fix-таск F1 больше не пропущен


if __name__ == "__main__":
    unittest.main()
