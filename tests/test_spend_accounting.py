"""Учёт расхода: кэш субагентов (compute_spend), расход оркестратора (run_log.usage_by_model,
ap.py spend-orchestrator, finish), таблицы «Кэш» в report-run, правило тихого вывода в executor.md."""
import copy
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import test_ap
from test_dashboard_details import SCRIPT, _states
from test_dashboard_views import NODE, TEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(test_ap.SKILL, "tools"))
import run_log  # noqa: E402
import state_io  # noqa: E402

RUN = "2026-11-16-spend-demo"
SINCE = "2026-06-01T10:00:00+00:00"


def load_ap():
    spec = importlib.util.spec_from_file_location("ap_spend_acc", test_ap.AP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def row(agent, **kw):
    return dict({"k": "executor", "run": RUN + "--wip", "agent_type": agent, "model": "sonnet",
                 "input": 0, "output": 0}, **kw)


class ComputeSpendCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ap = load_ap()

    def spend(self, *rows):
        return self.ap.compute_spend(list(rows), RUN)

    def test_cache_sums_and_hit_in_all_three_buckets_tokens_stay_input_plus_output(self):
        s = self.spend(row("autopilot-executor-01-a", input=100, output=50, cache_read=700, cache_write=200),
                       row("autopilot-executor-01-a", input=100, output=10, cache_read=100, cache_write=0))
        for bucket, key in (("byRole", "executor"), ("byModel", "sonnet"), ("byTicket", "01")):
            a = s[bucket][key]
            self.assertEqual((a["cache_read"], a["cache_write"], a["tokens"]), (800, 200, 260), bucket)
            self.assertEqual(a["hit"], 67, bucket)       # 800 / (200 + 800 + 200) = 66.7 %

    def test_bad_cache_values_count_as_zero_and_no_denominator_gives_none(self):
        s = self.spend(row("autopilot-reviewer-x", cache_read=True, cache_write=-5),
                       row("autopilot-reviewer-x", cache_read="7"),
                       row("autopilot-reviewer-x"))
        a = s["byRole"]["reviewer"]
        self.assertEqual((a["n"], a["cache_read"], a["cache_write"], a["hit"]), (3, 0, 0, None))

    def test_zero_hit_is_zero_not_none(self):
        a = self.spend(row("autopilot-executor-02-a", input=40, cache_write=60))["byRole"]["executor"]
        self.assertEqual(a["hit"], 0)

    def test_orchestrator_keeps_last_row_per_model_and_stays_out_of_byticket(self):
        orch = lambda model, **kw: row(None, role="orchestrator", model=model, agent_type=None, **kw)
        s = self.spend(orch("opus", input=1, output=1, cache_read=10),
                       orch("opus", input=5, output=5, cache_read=90, cache_write=5),   # повторный вызов
                       orch("haiku", input=2, output=2),
                       row("autopilot-executor-03-a", input=7, output=3))
        o = s["byRole"]["orchestrator"]
        self.assertEqual((o["input"], o["output"], o["cache_read"], o["cache_write"]), (7, 7, 90, 5))
        self.assertEqual(s["byModel"]["opus"]["tokens"], 10)
        self.assertEqual(list(s["byTicket"]), ["03"])


class UsageByModel(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ap-usage-")
        self.path = os.path.join(self.d, "session.jsonl")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)

    @staticmethod
    def msg(i, model, ts, side=False, usage=True, **u):
        m = {"id": i, "role": "assistant", "model": model}
        if usage:
            m["usage"] = u
        return json.dumps({"type": "assistant", "timestamp": ts, "isSidechain": side, "message": m})

    def write(self, *lines):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def test_sums_per_model_with_all_filters(self):
        late = "2026-06-01T11:%02d:00.000Z"
        self.write(
            self.msg("old", "opus", "2026-06-01T09:00:00.000Z", input_tokens=999),            # до since
            self.msg("a", "opus", late % 1, input_tokens=1, output_tokens=2,
                     cache_read_input_tokens=100, cache_creation_input_tokens=10),
            self.msg("a", "opus", late % 2, input_tokens=3, output_tokens=4,                   # повтор id: последний
                     cache_read_input_tokens=300, cache_creation_input_tokens=30),
            self.msg("b", "haiku", late % 3, input_tokens=5, output_tokens=6),
            self.msg("c", "opus", late % 4, side=True, input_tokens=777),                      # субагент
            self.msg("d", "opus", late % 5, usage=False),                                      # без usage
            "{не json",
            json.dumps({"type": "user", "timestamp": late % 6, "message": {"role": "user", "content": "секрет"}}))
        got = run_log.usage_by_model(self.path, SINCE)
        self.assertEqual(got, {
            "opus": {"turns": 1, "input": 3, "output": 4, "cache_read": 300, "cache_write": 30},
            "haiku": {"turns": 1, "input": 5, "output": 6, "cache_read": 0, "cache_write": 0}})

    def test_until_cuts_the_tail_and_unreadable_path_is_none(self):
        self.write(self.msg("a", "opus", "2026-06-01T11:00:00Z", input_tokens=1),
                   self.msg("b", "opus", "2026-06-01T13:00:00Z", input_tokens=2))
        got = run_log.usage_by_model(self.path, SINCE, "2026-06-01T12:00:00+00:00")
        self.assertEqual(got["opus"]["input"], 1)
        self.assertIsNone(run_log.usage_by_model(os.path.join(self.d, "нет.jsonl"), SINCE))

    def test_since_with_offset_without_offset_and_none(self):
        # 11:30Z = 14:30+03:00; 10:30Z раньше 11:00Z
        self.write(self.msg("a", "opus", "2026-06-01T10:30:00Z", input_tokens=1),
                   self.msg("b", "opus", "2026-06-01T11:30:00Z", input_tokens=2))
        at = lambda since: run_log.usage_by_model(self.path, since)["opus"]["input"]
        self.assertEqual(at("2026-06-01T14:00:00+03:00"), 2)      # 11:00Z
        self.assertEqual(at("2026-06-01T11:00:00"), 2)            # без пояса = UTC
        self.assertEqual(at(None), 3)

    def test_reads_tens_of_thousands_of_lines(self):
        line = lambda i: self.msg("m%d" % i, "opus", "2026-06-01T11:00:00Z", input_tokens=1, output_tokens=1)
        self.write(*[line(i) for i in range(30000)])
        self.assertEqual(run_log.usage_by_model(self.path, SINCE)["opus"]["turns"], 30000)


class Harness:
    """Проект-харнесс test_ap.Run с startedAt в прошлом и журналом сессии во временной папке."""

    def __init__(self, case, ready=False):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        case.addCleanup(self.h.tearDown)
        self.h.ready_to_finish() if ready else self.h.init()
        path = os.path.join(self.h.a, "state.js")
        st = state_io.read_state_file(path)
        st["startedAt"] = SINCE
        state_io.write_state_file(path, st)
        self.cfg = tempfile.mkdtemp(prefix="ap-cfg-")
        case.addCleanup(lambda: __import__("shutil").rmtree(self.cfg, ignore_errors=True))

    def transcript(self, name="s.jsonl"):
        p = os.path.join(self.cfg, name)
        lines = [json.dumps({"type": "assistant", "timestamp": "2026-06-01T11:00:00.000Z", "isSidechain": False,
                             "message": {"id": "m1", "role": "assistant", "model": "claude-opus-x",
                                         "content": [{"type": "text", "text": "СЕКРЕТНЫЙ ТЕКСТ ОТВЕТА"}],
                                         "usage": {"input_tokens": 11, "output_tokens": 22,
                                                   "cache_read_input_tokens": 330, "cache_creation_input_tokens": 44}}}),
                 json.dumps({"type": "user", "timestamp": "2026-06-01T11:00:01.000Z",
                             "message": {"role": "user", "content": "СЕКРЕТНЫЙ ВОПРОС"}})]
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return p

    def journal(self):
        try:
            with open(os.path.join(self.h.a, "run-log.jsonl"), encoding="utf-8") as f:
                return [json.loads(x) for x in f.read().splitlines() if x.strip()]
        except FileNotFoundError:
            return []


class SpendOrchestratorCommand(unittest.TestCase):
    def test_writes_numbers_and_model_only_and_second_call_does_not_double(self):
        hx = Harness(self)
        tp = hx.transcript()
        code, out = hx.h.ap("spend-orchestrator", "--transcript", tp)
        self.assertEqual(code, 0, out)
        self.assertEqual(self.h_orch(hx), [{"model": "claude-opus-x", "turns": 1, "input": 11, "output": 22,
                                            "cache_read": 330, "cache_write": 44}])
        raw = pathlib.Path(hx.h.a, "run-log.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("СЕКРЕТНЫЙ", raw)
        self.assertEqual(self.h_orch(hx), self.h_orch(hx))
        self.assertEqual(hx.h.ap("spend-orchestrator", "--transcript", tp)[0], 0)
        self.assertEqual(len(self.h_orch(hx)), 2)                       # две строки журнала...
        s = load_ap().compute_spend(hx.journal(), hx.h.state()["dir"])
        self.assertEqual(s["byRole"]["orchestrator"]["input"], 11)      # ...но сумма одна
        self.assertEqual(s["byRole"]["orchestrator"]["cache_read"], 330)

    def test_report_run_collapses_repeated_orchestrator_rows_like_compute_spend(self):
        hx = Harness(self)
        tp = hx.transcript()
        hx.h.ap("spend-orchestrator", "--transcript", tp)
        code, once = hx.h.ap("report-run")
        self.assertEqual(code, 0, once)
        hx.h.ap("spend-orchestrator", "--transcript", tp)
        self.assertEqual(len(self.h_orch(hx)), 2)
        code, twice = hx.h.ap("report-run")
        self.assertEqual(code, 0, twice)
        self.assertEqual(once, twice)
        self.assertIn("| orchestrator | 330 | 44 |", twice)

    def test_failed_journal_write_prints_not_written_line_only(self):
        hx = Harness(self)
        ap = load_ap()
        state = {"startedAt": SINCE, "dir": RUN + "--wip"}
        with mock.patch.object(ap.run_log, "append", return_value=False):
            out = ap.spend_orchestrator(state, hx.transcript())
        self.assertTrue(out.startswith("расход оркестратора не записан: "), out)
        self.assertNotIn("расход оркестратора:", out)

    @staticmethod
    def h_orch(hx):
        keep = ("model", "turns", "input", "output", "cache_read", "cache_write")
        return [{k: r[k] for k in keep} for r in hx.journal() if r.get("role") == "orchestrator"]

    def test_missing_transcript_is_one_line_and_exit_zero(self):
        hx = Harness(self)
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": hx.cfg}):
            code, out = hx.h.ap("spend-orchestrator")
            self.assertEqual(code, 0, out)
            lines = [x for x in out.splitlines() if x.strip()]
            self.assertEqual(len(lines), 1, out)
            self.assertTrue(lines[0].startswith("расход оркестратора не найден: "), out)
            code, out = hx.h.ap("spend-orchestrator", "--transcript", os.path.join(hx.cfg, "нет.jsonl"))
            self.assertEqual(code, 0, out)
            self.assertIn("расход оркестратора не найден: ", out)
        self.assertEqual(self.h_orch(hx), [])

    def test_default_path_is_the_newest_jsonl_of_the_project_folder(self):
        hx = Harness(self)
        name = re.sub(r"[^A-Za-z0-9]", "-", hx.h.root)
        folder = os.path.join(hx.cfg, "projects", name)
        os.makedirs(folder)
        old = hx.transcript("old.jsonl")
        os.replace(old, os.path.join(folder, "old.jsonl"))
        os.utime(os.path.join(folder, "old.jsonl"), (1, 1))
        os.replace(hx.transcript("new.jsonl"), os.path.join(folder, "new.jsonl"))
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": hx.cfg}):
            code, out = hx.h.ap("spend-orchestrator")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.h_orch(hx)), 1)

    def test_finish_does_not_fail_without_and_with_a_session_log(self):
        for with_log in (False, True):
            hx = Harness(self, ready=True)
            if with_log:
                name = re.sub(r"[^A-Za-z0-9]", "-", hx.h.root)
                os.makedirs(os.path.join(hx.cfg, "projects", name))
                os.replace(hx.transcript(), os.path.join(hx.cfg, "projects", name, "s.jsonl"))
            with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": hx.cfg}):
                code, out = hx.h.ap("finish", "--result", "готово")
            self.assertEqual(code, 0, out)
            self.assertEqual(len(self.h_orch(hx)), 1 if with_log else 0, out)
            self.assertEqual(out.count("расход оркестратора"), 1, out)


class ReportTables(unittest.TestCase):
    def rows(self):
        return [row("autopilot-executor-01-secret", role="executor", input=100, output=5, cache_read=300, cache_write=100),
                row("autopilot-reviewer-01-secret", role="reviewer", input=50, output=5)]

    def summary(self):
        rows = [dict(r, run=RUN) for r in self.rows()]
        return run_log.summarize(rows, run=RUN)

    def test_cache_by_role_and_by_profile_but_share_has_no_profiles_or_names(self):
        full = run_log.render_report(self.summary())
        self.assertIn("## Кэш по ролям", full)
        self.assertIn("## Кэш по профилям", full)
        self.assertIn("| executor | 300 | 100 | 60% |", full)       # 300 / (100 + 300 + 100)
        self.assertIn("| reviewer | 0 | 0 | 0% |", full)
        self.assertIn("| autopilot-executor-01-secret | 300 | 100 | 60% |", full)
        shared = run_log.render_report(self.summary(), share=True)
        self.assertIn("## Кэш по ролям", shared)
        self.assertIn("| executor | 300 | 100 | 60% |", shared)
        self.assertNotIn("по профилям", shared)
        self.assertNotIn("secret", shared)


@unittest.skipUnless(NODE, "node is not installed")
class DashboardCacheColumn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        states = _states()
        spend = copy.deepcopy(states["spend"]["spend"])
        spend["byRole"]["executor"].update(cache_read=800, cache_write=200, hit=67)
        spend["byRole"]["reviewer"]["hit"] = None
        spend["byModel"]["sonnet"]["hit"] = 0
        orch = copy.deepcopy(spend)
        orch["byRole"]["orchestrator"] = {"n": 1, "input": 70000, "output": 30000, "tokens": 100000,
                                          "cache_read": 5, "cache_write": 5, "hit": 7}
        fixtures = {"cache": dict(states["spend"], spend=spend), "orch": dict(states["spend"], spend=orch)}
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(SCRIPT, encoding="utf-8")
            done = subprocess.run([NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8",
                                  timeout=120, input=json.dumps({"fixtures": fixtures}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def cells(self, lang):
        html = self.out["cache/det/" + lang]
        spend = html[html.index("data-spend"):]
        return [[re.sub(r"<[^>]*>", "", c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r)]
                for r in re.findall(r"<tr>(.*?)</tr>", spend, re.S)]

    def test_spend_tables_get_cache_column_with_hit_and_dash_for_null(self):
        en, ru = self.cells("en"), self.cells("ru")
        self.assertEqual(en[0], ["What", "Runs", "Tokens", "Cache, %"])
        self.assertEqual(ru[0], ["Что", "Запусков", "Токены", "Кэш, %"])
        by_name = {r[0]: r for r in en}
        self.assertEqual(by_name["executor"][3], "67%")
        self.assertEqual(by_name["reviewer"][3], "—")         # hit: null
        self.assertEqual(by_name["sonnet"][3], "0%")           # 0 — это 0, не «—»
        self.assertEqual(by_name["F1"][3], "—")                # поля hit нет совсем


    def test_orchestrator_stays_in_tables_but_out_of_header_and_tile(self):
        html = self.out["orch/det/en"]
        spend = html[html.index("data-spend"):]
        head = re.sub(r"<[^>]*>", "", re.search(r'<div class="whead">(.*?)</div>', spend, re.S).group(1))
        self.assertIn("4,900", head)
        self.assertNotIn("104,900", head)
        rows = {r[0]: r for r in self.cells_of(spend)}
        self.assertEqual(rows["orchestrator"][2], "100,000")      # строка таблицы осталась
        self.assertEqual(rows["orchestrator"][3], "7%")
        for page in ("now", "res"):                               # плитка «токены»
            self.assertNotIn("104,900", re.sub(r"<[^>]*>", " ", self.out["orch/%s/en" % page]), page)

    @staticmethod
    def cells_of(spend):
        return [[re.sub(r"<[^>]*>", "", c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r)]
                for r in re.findall(r"<tr>(.*?)</tr>", spend, re.S)]


class ExecutorPromptAndDocs(unittest.TestCase):
    def test_executor_prompt_has_quiet_output_rule_and_keeps_the_exit_code_rule(self):
        text = pathlib.Path(ROOT, "skills", "autopilot", "prompts", "executor.md").read_text(encoding="utf-8")
        self.assertIn("тихом режиме", text)
        self.assertIn("полный лог читай, только если красное", text)
        self.assertIn("pipefail", text)
        self.assertIn('test "$rc" -eq 0', text)

    def test_measuring_cost_describes_cache_and_orchestrator_limits(self):
        text = pathlib.Path(ROOT, "docs", "autopilot", "measuring-cost.md").read_text(encoding="utf-8")
        self.assertIn("spend-orchestrator", text)
        self.assertIn("newest", text)
        self.assertIn("not a cost", text)


if __name__ == "__main__":
    unittest.main()
