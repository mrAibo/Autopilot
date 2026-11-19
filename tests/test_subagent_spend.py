"""Расход субагентов из журналов Claude Code (без хуков): run_log.usage_by_agent, ap.py spend-subagents,
finish, дедуп по `agent` в compute_spend/summarize, поиск папки сессии по общему префиксу."""
import json
import os
import pathlib
import re
import sys
import tempfile
import unittest
from unittest import mock

import test_ap
from test_spend_accounting import RUN, SINCE, Harness, load_ap, row

sys.path.insert(0, os.path.join(test_ap.SKILL, "tools"))
import run_log  # noqa: E402

SECRET = "СЕКРЕТНЫЙ ПРОМПТ"
DESC = "СЕКРЕТНОЕ ОПИСАНИЕ"


def msg(i, ts, model="claude-sonnet-x", usage=True, **u):
    m = {"id": i, "role": "assistant", "model": model, "content": [{"type": "text", "text": SECRET}]}
    if usage:
        m["usage"] = u
    return json.dumps({"type": "assistant", "timestamp": ts, "isSidechain": True, "message": m})


def put_agent(folder, aid, lines, meta=None):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "agent-%s.jsonl" % aid), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if meta is not None:
        with open(os.path.join(folder, "agent-%s.meta.json" % aid), "w", encoding="utf-8") as f:
            f.write(meta if isinstance(meta, str) else json.dumps(meta))


T = "2026-06-01T11:%02d:00.000Z"


class UsageByAgent(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ap-agents-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.d, ignore_errors=True))

    def test_sums_dedupe_window_bad_lines_and_missing_or_broken_meta(self):
        put_agent(self.d, "aaa", [
            msg("old", "2026-06-01T09:00:00.000Z", input_tokens=999),                        # до since
            msg("m1", T % 1, input_tokens=1, output_tokens=2, cache_read_input_tokens=100, cache_creation_input_tokens=10),
            msg("m1", T % 2, input_tokens=3, output_tokens=4, cache_read_input_tokens=300, cache_creation_input_tokens=30),
            msg("m2", T % 3, "claude-haiku-x", input_tokens=5, output_tokens=6),
            "{не json",
            msg("m3", T % 4, usage=False),
            json.dumps({"type": "user", "timestamp": T % 5, "message": {"role": "user", "content": SECRET}})],
            {"agentType": "autopilot-executor-01-x", "description": DESC})
        put_agent(self.d, "bbb", [msg("b1", T % 7, input_tokens=7)])                          # meta нет
        put_agent(self.d, "ccc", [msg("c1", T % 8, input_tokens=8)], "{битый")                # meta битый
        put_agent(self.d, "ddd", [msg("d1", "2026-06-01T08:00:00Z", input_tokens=1)])         # весь вне окна
        pathlib.Path(self.d, "other.jsonl").write_text(msg("x", T % 9, input_tokens=5), encoding="utf-8")
        got = run_log.usage_by_agent(self.d, SINCE)
        self.assertEqual(got, [
            {"agent": "aaa", "agent_type": "autopilot-executor-01-x", "model": "claude-haiku-x", "first_at": T % 1,
             "turns": 2, "input": 8, "output": 10, "cache_read": 300, "cache_write": 30},
            {"agent": "bbb", "agent_type": "agent", "model": "claude-sonnet-x", "first_at": T % 7,
             "turns": 1, "input": 7, "output": 0, "cache_read": 0, "cache_write": 0},
            {"agent": "ccc", "agent_type": "agent", "model": "claude-sonnet-x", "first_at": T % 8,
             "turns": 1, "input": 8, "output": 0, "cache_read": 0, "cache_write": 0}])
        self.assertNotIn(SECRET, json.dumps(got, ensure_ascii=False))
        self.assertNotIn(DESC, json.dumps(got, ensure_ascii=False))

    def test_until_cuts_the_tail(self):
        put_agent(self.d, "aaa", [msg("a", T % 1, input_tokens=1), msg("b", "2026-06-01T13:00:00Z", input_tokens=2)])
        got = run_log.usage_by_agent(self.d, SINCE, "2026-06-01T12:00:00+00:00")
        self.assertEqual(got[0]["input"], 1)

    def test_no_folder_is_none_and_empty_folder_is_empty_list(self):
        self.assertIsNone(run_log.usage_by_agent(os.path.join(self.d, "нет"), SINCE))
        self.assertEqual(run_log.usage_by_agent(self.d, SINCE), [])


def session(hx):
    """Журнал сессии `<cfg>/s.jsonl` и папка его субагентов `<cfg>/s/subagents`."""
    return hx.transcript(), os.path.join(hx.cfg, "s", "subagents")


class SpendSubagentsCommand(unittest.TestCase):
    def sub_rows(self, hx):
        return [r for r in hx.journal() if r.get("agent")]

    def test_writes_numbers_only_and_second_call_does_not_double(self):
        hx = Harness(self)
        tp, folder = session(hx)
        put_agent(folder, "aaa", [msg("m", T % 1, input_tokens=10, output_tokens=5, cache_read_input_tokens=70,
                                       cache_creation_input_tokens=20)],
                  {"agentType": "autopilot-reviewer-x", "description": DESC})
        code, out = hx.h.ap("spend-subagents", "--transcript", tp)
        self.assertEqual(code, 0, out)
        self.assertIn("расход субагентов", out)
        rows = self.sub_rows(hx)
        self.assertEqual([(r["k"], r["agent"], r["agent_type"], r["role"], r["model"], r["turns"], r["input"],
                           r["output"], r["cache_read"], r["cache_write"]) for r in rows],
                         [("executor", "aaa", "autopilot-reviewer-x", "reviewer", "claude-sonnet-x", 1, 10, 5, 70, 20)])
        raw = pathlib.Path(hx.h.a, "run-log.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(SECRET, raw)
        self.assertNotIn(DESC, raw)
        hx.h.ap("spend-subagents", "--transcript", tp)
        self.assertEqual(len(self.sub_rows(hx)), 2)                   # две строки журнала...
        dirname = hx.h.state()["dir"]
        s = load_ap().compute_spend(hx.journal(), dirname)
        self.assertEqual((s["byRole"]["reviewer"]["n"], s["byRole"]["reviewer"]["input"]), (1, 10))   # ...сумма одна
        t = run_log.summarize(hx.journal(), run=dirname)
        self.assertEqual(len([e for e in t["tokens"] if e.get("agent")]), 1)

    def test_no_subagents_folder_is_an_honest_line(self):
        hx = Harness(self)
        tp, _ = session(hx)
        code, out = hx.h.ap("spend-subagents", "--transcript", tp)
        self.assertEqual(code, 0, out)
        self.assertIn("субагентов нет", out)
        self.assertEqual(self.sub_rows(hx), [])

    def test_finish_calls_it_next_to_orchestrator_and_survives_without_folder(self):
        for with_agents in (False, True):
            hx = Harness(self, ready=True)
            name = re.sub(r"[^A-Za-z0-9]", "-", hx.h.root)
            os.makedirs(os.path.join(hx.cfg, "projects", name))
            os.replace(hx.transcript(), os.path.join(hx.cfg, "projects", name, "s.jsonl"))
            if with_agents:
                put_agent(os.path.join(hx.cfg, "projects", name, "s", "subagents"), "aaa",
                          [msg("m", T % 1, input_tokens=3, output_tokens=4)], {"agentType": "general-purpose"})
            with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": hx.cfg}):
                code, out = hx.h.ap("finish", "--result", "готово")
            self.assertEqual(code, 0, out)
            self.assertEqual(out.count("расход оркестратора"), 1, out)
            self.assertEqual(len(self.sub_rows(hx)), 1 if with_agents else 0, out)
            self.assertIn("расход субагентов" if with_agents else "субагентов нет", out)

    def test_failed_journal_write_and_exceptions_do_not_raise(self):
        hx = Harness(self)
        tp, folder = session(hx)
        put_agent(folder, "aaa", [msg("m", T % 1, input_tokens=3)])
        ap = load_ap()
        state = {"startedAt": SINCE, "dir": RUN + "--wip", "tickets": []}
        with mock.patch.object(ap.run_log, "append", return_value=False):
            self.assertIn("не записан", ap.spend_subagents(state, tp))
        with mock.patch.object(ap.run_log, "usage_by_agent", side_effect=RuntimeError):
            self.assertIn("расход субагентов", ap.spend_subagents(state, tp))


class TicketByWindow(unittest.TestCase):
    def tickets_for(self, tickets, first_at=T % 30, agent_type=None):
        hx = Harness(self)
        tp, folder = session(hx)
        put_agent(folder, "aaa", [msg("m", first_at, input_tokens=1)],
                  {"agentType": agent_type} if agent_type else None)
        ap = load_ap()
        calls = []
        with mock.patch.object(ap.run_log, "append", side_effect=lambda *a, **k: calls.append(k) or True):
            ap.spend_subagents({"startedAt": SINCE, "dir": RUN + "--wip", "tickets": tickets}, tp)
        return [c.get("ticket") for c in calls]

    def test_single_window_gives_the_ticket(self):
        got = self.tickets_for([
            {"id": "01", "startedAt": "2026-06-01T11:00:00+00:00", "finishedAt": "2026-06-01T11:20:00+00:00"},
            {"id": "02", "startedAt": "2026-06-01T11:20:00+00:00", "finishedAt": "2026-06-01T12:00:00+00:00"}])
        self.assertEqual(got, ["02"])

    def test_profile_ticket_wins_over_the_time_window(self):
        got = self.tickets_for([
            {"id": "02", "startedAt": "2026-06-01T11:00:00+00:00", "finishedAt": "2026-06-01T12:00:00+00:00"}],
            agent_type="autopilot-executor-01-x")
        self.assertEqual(got, ["01"])

    def test_reviewer_is_not_given_somebody_elses_ticket(self):
        got = self.tickets_for([
            {"id": "02", "startedAt": "2026-06-01T11:00:00+00:00", "finishedAt": "2026-06-01T12:00:00+00:00"}],
            agent_type="autopilot-reviewer-x")
        self.assertEqual(got, [None])

    def test_open_window_runs_until_now(self):
        self.assertEqual(self.tickets_for([{"id": "03", "startedAt": "2026-06-01T11:00:00+00:00"}]), ["03"])

    def test_parallel_wave_or_no_window_gives_no_ticket(self):
        wave = [{"id": "01", "startedAt": "2026-06-01T11:00:00+00:00", "finishedAt": "2026-06-01T12:00:00+00:00"},
                {"id": "02", "startedAt": "2026-06-01T11:10:00+00:00", "finishedAt": "2026-06-01T12:00:00+00:00"}]
        self.assertEqual(self.tickets_for(wave), [None])
        self.assertEqual(self.tickets_for(wave[:1], first_at="2026-06-01T13:00:00Z"), [None])
        self.assertEqual(self.tickets_for([]), [None])


class DedupeInReaders(unittest.TestCase):
    ap = None

    @classmethod
    def setUpClass(cls):
        cls.ap = load_ap()

    def journal_row(self, agent, aid, **kw):
        return dict(row(agent, role=run_log.role_of(agent), **kw), agent=aid)

    def test_last_row_per_agent_and_ticket_from_row(self):
        rows = [self.journal_row("general-purpose", "aaa", input=1, output=1, ticket="05"),
                self.journal_row("general-purpose", "aaa", input=10, output=5, ticket="05"),
                self.journal_row("general-purpose", "bbb", input=2, output=2)]
        s = self.ap.compute_spend(rows, RUN)
        self.assertEqual((s["byRole"]["agent"]["n"], s["byRole"]["agent"]["tokens"]), (2, 19))
        self.assertEqual(s["byTicket"]["05"]["tokens"], 15)
        self.assertEqual(list(s["byTicket"]), ["05"])
        t = run_log.summarize([dict(r, run=RUN) for r in rows], run=RUN)
        self.assertEqual(sorted((e["agent"], e["input"]) for e in t["tokens"]), [("aaa", 10), ("bbb", 2)])

    def test_ticket_falls_back_to_profile_name(self):
        s = self.ap.compute_spend([self.journal_row("autopilot-executor-07-x", "aaa", input=4)], RUN)
        self.assertEqual(list(s["byTicket"]), ["07"])

    def test_hook_rows_win_over_journal_rows_of_autopilot_agents(self):
        hook = row("autopilot-executor-01-x", role="executor", input=100, output=0)
        mine = self.journal_row("autopilot-executor-01-x", "aaa", input=100)
        other = self.journal_row("general-purpose", "bbb", input=5)
        s = self.ap.compute_spend([hook, mine, other], RUN)
        self.assertEqual((s["byRole"]["executor"]["n"], s["byRole"]["executor"]["input"]), (1, 100))
        self.assertEqual(s["byRole"]["agent"]["input"], 5)
        t = run_log.summarize([dict(r, run=RUN) for r in (hook, mine, other)], run=RUN)
        self.assertEqual(sorted(e["role"] for e in t["tokens"]), ["agent", "executor"])
        # без хуковых строк журнальные остаются
        s = self.ap.compute_spend([mine], RUN)
        self.assertEqual(s["byRole"]["executor"]["input"], 100)

    def test_orchestrator_row_is_not_a_hook_row(self):
        orch = row(None, role="orchestrator", agent_type=None, input=1)
        mine = self.journal_row("autopilot-executor-01-x", "aaa", input=100)
        self.assertEqual(self.ap.compute_spend([orch, mine], RUN)["byRole"]["executor"]["input"], 100)


class SessionTranscriptPrefix(unittest.TestCase):
    def setUp(self):
        self.cfg = tempfile.mkdtemp(prefix="ap-cfg-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.cfg, ignore_errors=True))
        self.ap = load_ap()
        self.proj = "C:/" + "x" * 150 + "/proj"
        self.want = re.sub(r"[^A-Za-z0-9]", "-", self.proj)

    def log(self, folder, mtime):
        p = os.path.join(self.cfg, "projects", folder, "s.jsonl")
        os.makedirs(os.path.dirname(p))
        pathlib.Path(p).write_text("{}\n", encoding="utf-8")
        os.utime(p, (mtime, mtime))
        return p

    def find(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.cfg}), \
                mock.patch.object(self.ap, "A", self.proj + "/.autopilot"):
            return self.ap.session_transcript()

    def test_truncated_name_is_found_by_common_prefix_and_decoys_lose(self):
        cut = self.log(self.want[:110], 100)
        self.log(self.want[:60] + "-other", 999)                   # префикс короче 100: не подходит
        self.assertEqual(self.find(), cut)

    def test_exact_folder_beats_a_truncated_one(self):
        exact = self.log(self.want, 100)
        self.log(self.want[:110], 999)
        self.assertEqual(self.find(), exact)

    def test_nothing_found_is_none(self):
        self.log("совсем-другая-папка", 5)
        self.assertIsNone(self.find())


if __name__ == "__main__":
    unittest.main()
