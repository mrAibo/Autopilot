"""Аудит дашборда, ap.py: пути со скобками, сервер с токеном, отрезки этапов, снимок,
расход и история сборок, свод report-run по моделям."""

import http.client
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

import test_ap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(test_ap.SKILL, "tools"))
import state_io  # noqa: E402

RUN = "2026-11-15-audit-demo"
WIP = RUN + "--wip"


def harness(case, prefix=None):
    """Временный проект-харнесс test_ap.Run; prefix — имя его папки (для скобок и пробела)."""
    h = test_ap.Run("test_skip_needs_a_reason")
    real = tempfile.mkdtemp
    fake = lambda **kw: real(**dict(kw, prefix=prefix if prefix and kw.get("prefix") == "ap-test-" else kw.get("prefix")))
    with mock.patch("tempfile.mkdtemp", fake):
        h.setUp()
    case.addCleanup(h.tearDown)
    return h


def load_ap(h):
    """Копия ap.py харнесса как модуль: A, STATE, PAGE указывают в его .autopilot."""
    spec = importlib.util.spec_from_file_location("ap_audit_%d" % id(h), os.path.join(h.a, "ap.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write_journal(h, rows):
    with open(os.path.join(h.a, "run-log.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(dict({"t": "2026-11-15T10:00:00+01:00"}, **r), ensure_ascii=False) + "\n")


def spent(agent, inp, out, model=None, run=WIP):
    row = {"run": run, "k": "executor", "agent_type": agent, "turns": 3, "input": inp, "output": out}
    row["role"] = "executor" if "executor" in agent else "reviewer"
    if model:
        row["model"] = model
    return row


class PathsWithBrackets(unittest.TestCase):
    def test_tickets_check_plan_and_accept_edit_find_files_in_a_bracketed_project(self):
        h = harness(self, prefix="[ACME] x-")
        self.assertIn("[ACME] x-", h.root)
        h.plan()
        code, out = h.ap("tickets")
        self.assertEqual(code, 0, out)
        self.assertNotIn("нет файлов", out)
        self.assertEqual([t["id"] for t in h.state()["tickets"]], ["01", "02"])
        code, out = h.ap("check-plan")
        self.assertEqual(code, 0, out)
        path = os.path.join(h.a, "state.js")
        st = state_io.read_state_file(path)
        next(t for t in st["tickets"] if t["id"] == "01").update(status="done", commit="abc1234")
        state_io.write_state_file(path, st)
        code, out = h.ap("ticket", "01", "accept-edit", "--note", "скобки")
        self.assertEqual(code, 0, out)

    def test_no_raw_glob_over_the_run_dir_left_in_ap(self):
        with open(test_ap.AP, encoding="utf-8") as f:
            self.assertNotIn("glob.glob(os.path.join(run_dir", f.read())


class Server(unittest.TestCase):
    TOKEN = "t0ken-0123456789abcdef"

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ap-serve-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.dir, ignore_errors=True))
        for rel, text in (("state.js", "window.STATE={}"), ("dashboard.html", "<html>/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"),
                          ("run-log.jsonl", "{}"), ("run/state.js", "x"), ("serve.token", self.TOKEN)):
            os.makedirs(os.path.dirname(os.path.join(self.dir, rel)), exist_ok=True)
            with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as f:
                f.write(text)
        spec = importlib.util.spec_from_file_location("ap_srv", test_ap.AP)
        self.ap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.ap)
        self.srv = self.ap.make_server(self.dir, 0, self.TOKEN)
        self.port = self.srv.server_port
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def get(self, path, host=None, method="GET", **headers):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            c.request(method, path, headers=dict(headers, Host=host or "127.0.0.1:%d" % self.port))
            return c.getresponse().status
        finally:
            c.close()

    def test_state_needs_the_right_host_and_the_token(self):
        t = "?t=" + self.TOKEN
        self.assertEqual(self.get("/state.js" + t), 200)
        self.assertEqual(self.get("/state.js" + t, host="localhost:%d" % self.port), 200)
        self.assertEqual(self.get("/state.js" + t, method="HEAD"), 200)
        self.assertEqual(self.get("/state.js" + t, host="evil.example:%d" % self.port), 403)
        self.assertEqual(self.get("/state.js" + t, host="127.0.0.1:1"), 403)
        self.assertEqual(self.get("/state.js"), 403)
        self.assertEqual(self.get("/state.js?t=wrong"), 403)
        self.assertEqual(self.get("/state.js" + t, **{"Sec-Fetch-Site": "cross-site"}), 403)
        self.assertEqual(self.get("/state.js" + t, **{"Sec-Fetch-Site": "same-origin"}), 200)
        self.assertEqual(self.get("/state.js" + t, Origin="http://evil.example"), 403)

    def test_page_is_open_everything_else_needs_the_token(self):
        self.assertEqual(self.get("/dashboard.html"), 200)
        self.assertEqual(self.get("/dashboard.html", host="evil.example"), 403)
        self.assertEqual(self.get("/dashboard.html", **{"Sec-Fetch-Site": "cross-site"}), 403)
        for path in ("/run-log.jsonl", "/run/state.js", "/run/", "/serve.token", "/nope.md"):
            self.assertEqual(self.get(path), 403, path)
        self.assertEqual(self.get("/run-log.jsonl?t=" + self.TOKEN), 200)
        self.assertEqual(self.get("/serve.token?t=" + self.TOKEN), 403)     # сам токен не отдаём

    def test_token_survives_restart_and_url_carries_it(self):
        first = self.ap.serve_token(self.dir)
        self.assertEqual(first, self.TOKEN)
        fresh = tempfile.mkdtemp(prefix="ap-tok-")
        self.addCleanup(lambda: __import__("shutil").rmtree(fresh, ignore_errors=True))
        made = self.ap.serve_token(fresh)
        self.assertGreaterEqual(len(made), 16)
        self.assertEqual(self.ap.serve_token(fresh), made)                  # второй запуск — тот же токен
        with mock.patch.object(self.ap, "A", fresh):
            self.assertEqual(self.ap.page_url(8123), "http://localhost:8123/dashboard.html?t=" + made)

    def test_server_process_answers_and_init_ignores_the_token_file(self):
        h = harness(self)
        h.init()
        with open(os.path.join(h.root, ".gitignore"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertIn(".autopilot/serve.token", lines)
        self.assertIn(".autopilot/serve.*", lines)
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        proc = subprocess.Popen([sys.executable, os.path.join(h.a, "ap.py"), "--serve", str(port)],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(proc.wait)
        self.addCleanup(proc.terminate)
        status = {}

        def ask(path, host=None):
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            c.request("GET", path, headers={"Host": host or "127.0.0.1:%d" % port})
            r = c.getresponse()
            c.close()
            return r.status

        for _ in range(50):
            try:
                status["page"] = ask("/dashboard.html")
                break
            except OSError:
                time.sleep(0.2)
        self.assertEqual(status.get("page"), 200)
        with open(os.path.join(h.a, "serve.token"), encoding="utf-8") as f:
            token = f.read().strip()
        self.assertEqual(ask("/state.js?t=" + token), 200)
        self.assertEqual(ask("/state.js"), 403)
        self.assertEqual(ask("/state.js?t=" + token, host="evil.example"), 403)
        self.assertEqual(ask("/.ap-ping"), 200)                             # подтверждение сервера без токена в адресе
        self.assertEqual(ask("/.ap-ping", host="evil.example"), 403)
        self.assertTrue(load_ap(h).server_is_ours(port))                    # настоящий процесс: токен он взял из serve.token

    def test_token_never_reaches_the_server_log(self):
        # serve.log — это stderr сервера: в строках запросов токена `?t=` быть не должно
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(self.get("/state.js?t=" + self.TOKEN), 200)
            self.assertEqual(self.get("/state.js?t=" + self.TOKEN, host="evil.example"), 403)
            self.assertEqual(self.get("/serve.token?t=" + self.TOKEN), 403)
        self.assertIn("/state.js", err.getvalue())                          # запросы в журнале есть
        self.assertNotIn(self.TOKEN, err.getvalue())

    def test_own_server_is_recognised_by_its_command_line(self):
        m = self.ap
        self.assertTrue(m.is_ours("%s %s --serve 8123" % (sys.executable, m.__file__)))
        self.assertTrue(m.is_guarded_server("%s %s --serve 8123" % (sys.executable, m.__file__)))
        self.assertFalse(m.is_ours("%s /elsewhere/ap.py --serve 8123" % sys.executable))
        legacy = "python3 -m http.server 8000 --directory %s" % m.A
        self.assertTrue(m.is_ours(legacy))                                  # прежний сервер гасим
        self.assertFalse(m.is_guarded_server(legacy))                       # но защищённым не считаем


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.m = load_ap(self.h)
        self.tmp = self.m.PAGE + ".tmp"

    def test_snapshot_survives_one_sharing_violation(self):
        real, calls = os.replace, []

        def flaky(src, dst, *a, **k):
            if os.fspath(dst) == self.m.PAGE:
                calls.append(src)
                if len(calls) == 1:
                    err = PermissionError(13, "занят")
                    err.winerror = 5
                    raise err
            return real(src, dst, *a, **k)

        with mock.patch.object(self.m.state_io, "WINDOWS", True), mock.patch("os.replace", flaky):
            self.assertEqual(self.m.write_snapshot({"rev": 41}), "дашборд обновлён")
        self.assertEqual(len(calls), 2)
        self.assertFalse(os.path.exists(self.tmp))
        with open(self.m.PAGE, encoding="utf-8") as f:
            self.assertIn('"rev": 41', f.read())

    def test_stuck_page_is_reported_not_raised_and_leaves_no_tmp(self):
        with mock.patch("os.replace", side_effect=PermissionError(13, "занят")):
            out = self.m.write_snapshot({"rev": 42})
        self.assertIn("не обновлён", out)
        self.assertFalse(os.path.exists(self.tmp))


class StageSegments(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.m = load_ap(self.h)
        self.state = self.m.fresh_state({"slug": "demo"})

    def stage(self, action, at):
        self.state["updatedAt"] = at
        with mock.patch.object(self.m, "now", lambda: at):
            self.m.cmd_stage(self.state, ["spec"] + ([action] if action else []), {})
        return next(s for s in self.state["stages"] if s["id"] == "spec")

    @staticmethod
    def minutes(segments):
        import datetime as dt
        return sum((dt.datetime.fromisoformat(s["finishedAt"]) - dt.datetime.fromisoformat(s["startedAt"])).seconds
                   for s in segments) // 60

    def test_returned_stage_accumulates_segments(self):
        self.stage("", "2026-11-15T10:00:00+01:00")
        self.stage("done", "2026-11-15T10:10:00+01:00")
        self.stage("", "2026-11-15T11:00:00+01:00")                          # вернулись к этапу
        s = self.stage("done", "2026-11-15T11:05:00+01:00")
        self.assertEqual(s["segments"], [
            {"startedAt": "2026-11-15T10:00:00+01:00", "finishedAt": "2026-11-15T10:10:00+01:00"},
            {"startedAt": "2026-11-15T11:00:00+01:00", "finishedAt": "2026-11-15T11:05:00+01:00"}])
        self.assertEqual((s["startedAt"], s["finishedAt"]), ("2026-11-15T10:00:00+01:00", "2026-11-15T11:05:00+01:00"))
        self.assertEqual(self.minutes(s["segments"]), 15)                    # не 65 минут «последний конец − первый старт»

    def test_return_closes_the_open_segment_and_opens_a_new_one(self):
        self.stage("", "2026-11-15T10:00:00+01:00")
        s = self.stage("", "2026-11-15T10:30:00+01:00")                    # start у активного — отрезок не дублируется
        self.assertEqual(len(s["segments"]), 1)
        self.assertIsNone(s["segments"][0]["finishedAt"])

    def test_old_state_without_segments_reads_as_before(self):
        next(s for s in self.state["stages"] if s["id"] == "spec").update(
            status="done", startedAt="2026-11-15T09:00:00+01:00", finishedAt="2026-11-15T09:20:00+01:00")
        s = self.stage("", "2026-11-15T12:00:00+01:00")
        self.assertEqual(s["segments"], [
            {"startedAt": "2026-11-15T09:00:00+01:00", "finishedAt": "2026-11-15T09:20:00+01:00"},
            {"startedAt": "2026-11-15T12:00:00+01:00", "finishedAt": None}])
        self.assertEqual(s["startedAt"], "2026-11-15T09:00:00+01:00")
        self.assertNotIn("finishedAt", s)
        untouched = next(x for x in self.state["stages"] if x["id"] == "plan")
        self.assertNotIn("segments", untouched)


class GateReset(unittest.TestCase):
    def test_plan_change_writes_a_reset_line_without_numbers(self):
        h = harness(self)
        h.plan()
        h.ap("tickets")
        self.assertEqual(h.ap("check-plan")[0], 0)
        path = os.path.join(h.a, "state.js")
        st = state_io.read_state_file(path)
        st["gates"].update({g: {"ok": True, "at": "2026-01-01T00:00:00+00:00"} for g in ("G1", "G2", "G4")})
        st["blind"] = {"checked": 3, "matched": 3, "mismatches": []}
        state_io.write_state_file(path, st)
        h.write("tickets/02-priem.md", test_ap.ticket("02", "Приём иначе", "R01.1, R02, A01", "01", ["src/bot/"], 2))
        h.ap("tickets")
        self.assertEqual(h.ap("check-plan")[0], 0)
        entries = [e for e in h.state()["log"] if e["k"] == "gate" and e.get("reason") == "plan-changed"]
        self.assertEqual(sorted(e["g"] for e in entries), ["G1", "G2", "G4"])
        for e in entries:
            self.assertEqual(set(e), {"t", "k", "g", "ok", "reason"}, e)     # никаких open/total/problems
            self.assertIs(e["ok"], False)


class SpendHistory(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.m = load_ap(self.h)

    def archive(self, name, **fields):
        os.makedirs(os.path.join(self.h.a, name), exist_ok=True)
        st = dict({"title": name, "startedAt": "2026-10-01T10:00:00+01:00", "finishedAt": "2026-10-01T11:30:00+01:00",
                   "tickets": [], "waits": [], "result": None}, **fields)
        state_io.write_state_file(os.path.join(self.h.a, name, "state.js"), st)

    def test_spend_by_role_model_and_ticket_with_unspecified_model(self):
        rows = [spent("autopilot-executor-01-karkas", 100, 900, "haiku"),
                spent("autopilot-executor-02-priem", 50, 50, "sonnet"),
                spent("autopilot-reviewer-x", 10, 20),
                spent("autopilot-executor-03-other", 1, 1, "haiku", run="2026-01-01-other")]
        out = self.m.compute_spend(rows, RUN)                                # журнал писался с --wip, прогон сдан без
        old_keys = lambda b: {k: {f: v[f] for f in ("n", "input", "output", "tokens")} for k, v in b.items()}   # кэш — в test_spend_accounting
        self.assertEqual(old_keys(out["byModel"]), {"haiku": {"n": 1, "input": 100, "output": 900, "tokens": 1000},
                                                    "sonnet": {"n": 1, "input": 50, "output": 50, "tokens": 100},
                                                    "не указана": {"n": 1, "input": 10, "output": 20, "tokens": 30}})
        self.assertEqual({k: v["tokens"] for k, v in out["byRole"].items()}, {"executor": 1100, "reviewer": 30})
        self.assertEqual({k: v["tokens"] for k, v in out["byTicket"].items()}, {"01": 1000, "02": 100})

    def test_history_keeps_20_newest_skips_broken_and_sums_tokens(self):
        for day in range(1, 23):
            self.archive("2026-09-%02d-old" % day, startedAt="2026-09-%02dT10:00:00+01:00" % day)
        self.archive("2026-10-05-big", title="Большая", startedAt="2026-10-05T10:00:00+01:00",
                     finishedAt="2026-10-05T11:30:00+01:00", result="сдано",
                     waits=[{"kind": "spec", "from": "2026-10-05T10:10:00+01:00", "to": "2026-10-05T10:40:00+01:00"}],
                     tickets=[{"id": "01", "repairs": 1}, {"id": "02", "repairs": 2}])
        os.makedirs(os.path.join(self.h.a, "2026-10-06-broken"))
        with open(os.path.join(self.h.a, "2026-10-06-broken", "state.js"), "w", encoding="utf-8") as f:
            f.write("window.STATE = {oops")
        os.makedirs(os.path.join(self.h.a, "2026-10-07-empty"))              # без state.js
        records = [spent("autopilot-executor-01-a", 100, 200, run="2026-10-05-big--wip"),
                   spent("autopilot-reviewer-a", 5, 5, run="2026-10-05-big")]
        history = self.m.compute_history(records, WIP)
        self.assertEqual(len(history), 20)
        self.assertEqual(history[0]["dir"], "2026-10-05-big")               # свежие первыми, битые пропущены
        self.assertEqual(history[1]["dir"], "2026-09-22-old")
        self.assertEqual(history[0], {"dir": "2026-10-05-big", "title": "Большая",
                                      "startedAt": "2026-10-05T10:00:00+01:00", "finishedAt": "2026-10-05T11:30:00+01:00",
                                      "minutes": 60, "tickets": 2, "repairs": 3, "tokens": 310, "result": "сдано"})
        self.assertNotIn(RUN, [x["dir"] for x in history])

    def test_history_cache_skips_unchanged_archives_and_recomputes_changed(self):
        self.archive("2026-10-05-a", title="Первая")
        self.archive("2026-10-06-b", title="Вторая")
        first = self.m.compute_history([], WIP)
        self.assertTrue(os.path.exists(os.path.join(self.h.a, "history-cache.json")))
        with mock.patch.object(self.m.state_io, "read_state_file", side_effect=AssertionError("opened")):
            self.assertEqual(self.m.compute_history([], WIP), first)       # архивы не открыты
        self.archive("2026-10-05-a", title="Первая, переименована надолго")  # другой размер
        second = self.m.compute_history([], WIP)
        self.assertIn("Первая, переименована надолго", [x["title"] for x in second])

    def test_history_cache_tokens_are_fresh_and_broken_cache_is_ignored(self):
        self.archive("2026-10-05-a")
        self.m.compute_history([], WIP)
        with open(os.path.join(self.h.a, "history-cache.json"), "w", encoding="utf-8") as f:
            f.write("{oops")
        rows = [spent("autopilot-executor-01-a", 4, 6, run="2026-10-05-a")]
        self.assertEqual(self.m.compute_history(rows, WIP)[0]["tokens"], 10)   # битый кэш — молча заново
        self.assertEqual(self.m.compute_history([], WIP)[0]["tokens"], 0)      # токены не из кэша

    def test_history_cache_row_without_dir_or_startedat_is_recomputed_not_a_keyerror(self):
        self.archive("2026-10-05-a", title="Первая", startedAt="2026-10-05T10:00:00+01:00")
        st = os.stat(os.path.join(self.h.a, "2026-10-05-a", "state.js"))
        for row in ({}, {"dir": "2026-10-05-a"}, {"dir": "2026-10-05-a", "startedAt": "2026-10-05T10:00:00+01:00"},
                    {"dir": "чужая", "startedAt": "x"}):
            with open(os.path.join(self.h.a, "history-cache.json"), "w", encoding="utf-8") as f:
                json.dump({"v": 1, "items": {"2026-10-05-a": {"key": [st.st_mtime_ns, st.st_size], "row": row}}}, f)
            got = self.m.compute_history([], WIP)
            self.assertEqual([(x["dir"], x["title"]) for x in got], [("2026-10-05-a", "Первая")], row)

    def test_state_js_gets_history_spend_and_log_failures(self):
        self.h.init()
        run = self.h.state()["dir"]
        self.archive("2026-10-05-past", title="Прошлая")
        write_journal(self.h, [spent("autopilot-executor-01-a", 7, 3, run=run)])
        st = self.h.state()
        self.assertEqual((st["spend"]["byRole"], st["history"], st["logFailures"]), ({}, [], 0))   # до команды — нет полей
        code, out = self.h.ap()
        self.assertEqual(code, 0, out)
        st = self.h.state()
        self.assertEqual([x["dir"] for x in st["history"]], ["2026-10-05-past"])
        self.assertEqual(st["spend"]["byModel"]["не указана"]["tokens"], 10)
        self.assertEqual([(e["role"], e["tokens"]) for e in st["spendLedger"]], [("executor", 10)])
        self.assertEqual(st["logFailures"], 0)
        for text, want in (("3\n", 3), ("мусор", 0)):
            with open(os.path.join(self.h.a, "run-log.fail"), "w", encoding="utf-8") as f:
                f.write(text)
            self.assertEqual(self.h.ap()[0], 0)
            self.assertEqual(self.h.state()["logFailures"], want)


class ReportRun(unittest.TestCase):
    def test_model_block_per_model_with_unspecified(self):
        h = harness(self)
        t = lambda tid, act: {"run": WIP, "k": "ticket", "id": tid, "act": act}
        write_journal(h, [
            t("01", "start"), spent("autopilot-executor-01-a", 100, 900, "haiku"), t("01", "done"),
            t("02", "start"), spent("autopilot-executor-02-b", 200, 300, "sonnet"), t("02", "repair"), t("02", "done"),
            t("03", "start"), spent("autopilot-executor-03-c", 20, 40), t("03", "done"),
            t("04", "start"), spent("autopilot-executor-04-d", 100, 300, "haiku"), t("04", "retry"), t("04", "done"),
            t("F1", "start"), t("F1", "done")])
        code, out = h.ap("report-run")
        self.assertEqual(code, 0, out)
        block = out[out.index("## Модели"):].split("## Класс", 1)[0]
        self.assertIn("| модель | тасков | сдано с первого раза | починок | токенов на таск |", block)
        rows = [x for x in block.splitlines() if x.startswith("| ") and "модель" not in x]
        self.assertEqual(rows, ["| haiku | 2 | 50% | 0 | 700 |",
                                "| sonnet | 1 | 0% | 1 | 500 |",
                                "| не указана | 2 | 100% | 0 | 30 |"])      # таск 03 и fix-таск F1 (строки расхода нет)


class ClassReport(unittest.TestCase):
    OLD = RUN.replace("-a", "-b", 1) if "-a" in RUN else RUN + "x"

    def rows(self):
        def t(tid, act, run=WIP, **f):
            return dict({"run": run, "k": "ticket", "id": tid, "act": act}, **f)
        mech = {"class": "механический", "effort": "high"}
        return [
            t("01", "start", model="haiku", **mech), spent("autopilot-executor-01-a", 100, 100), t("01", "done"),
            t("02", "start", model="claude-haiku-5-5", **mech), t("02", "retry"), t("02", "escalate"), t("02", "done"),
            t("03", "start", model="claude-sonnet-5-5", **{"class": "обычный", "effort": "medium"}),
            t("03", "done"),
            t("03", "start", run=self.OLD, model="sonnet", **{"class": "обычный", "effort": "medium"}),
            spent("autopilot-executor-03-c", 300, 100, run=self.OLD), t("03", "done", run=self.OLD),
            t("04", "start"), t("04", "done")]

    def test_combo_block_over_all_runs_without_names(self):
        h = harness(self)
        write_journal(h, self.rows())
        for extra in ([], ["--share"]):
            code, out = h.ap("report-run", *extra)
            self.assertEqual(code, 0, out)
            block = out[out.index("## Класс × модель × усилие"):]
            lines = [x for x in block.splitlines() if x.startswith("| ") and "класс" not in x]
            self.assertEqual(lines, ["| механический | haiku | high | 2 | 50% | 1 | 1 | 100 |",
                                     "| не указан | не указан | не указано | 1 | 100% | 0 | 0 | 0 |",
                                     "| обычный | sonnet | medium | 2 | 100% | 0 | 0 | 200 |"])
            self.assertIn("## Модели", out)

    def test_empty_history_has_no_block_and_no_advice(self):
        h = harness(self)
        write_journal(h, [{"run": WIP, "k": "phase", "id": "build", "act": "start"}])
        code, out = h.ap("report-run")
        self.assertEqual(code, 0, out)
        self.assertNotIn("Класс × модель", out)
        self.assertIsNone(load_ap(h).history_advice([]))

    def test_advice_counts_escalated_mechanical_haiku(self):
        self.assertIn("механических тасков на Haiku 2, эскалировано на Sonnet 1",
                      load_ap(harness(self)).history_advice(self.rows()))

    def test_plan_models_forecast_from_history_by_class(self):
        h = harness(self)
        old = "2026-10-01-old"
        t = lambda tid, act, at: {"run": old, "k": "ticket", "id": tid, "act": act, "t": at, "class": "механический"}
        write_journal(h, [
            t("01", "start", "2026-10-01T10:00:00+00:00"), spent("autopilot-executor-01-a", 400, 600, run=old),
            t("01", "done", "2026-10-01T10:10:00+00:00"),
            t("02", "start", "2026-10-01T10:10:00+00:00"), spent("autopilot-executor-02-b", 1000, 2000, run=old),
            t("02", "done", "2026-10-01T10:30:00+00:00")])
        h.plan()
        self.assertEqual(h.ap("tickets")[0], 0)
        code, out = h.ap("plan-models", "--provider", "anthropic")
        self.assertEqual(code, 0, out)
        # два механических таска плана: (1000 + 3000) / 2 на таск, (10 + 20) / 2 минут на таск
        self.assertIn("2 тасков", json.loads(out)["forecast"])
        self.assertIn("≈4000 токенов, ≈30 минут", json.loads(out)["forecast"])
        self.assertIn("оценк", json.loads(out)["forecast"])

    def test_final_report_row_reads_spend_keys_that_state_js_really_has(self):
        h = harness(self)
        h.init()
        write_journal(h, [spent("autopilot-executor-01-a", 7, 3, run=h.state()["dir"])])
        self.assertEqual(h.ap()[0], 0)                          # любая команда обновляет spend
        spend = h.state()["spend"]
        self.assertTrue({"byRole", "byModel", "byTicket"} <= set(spend))
        self.assertEqual(spend["byRole"]["executor"]["tokens"], 10)
        with open(os.path.join(REPO, "skills", "autopilot", "phases", "8-final.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertRegex(text, r"\| Расход и время \| `state\.js` → `spend`")

    def test_plan_models_prints_advice_only_with_haiku_escalation_history(self):
        h = harness(self)
        write_journal(h, self.rows())
        h.plan()
        self.assertEqual(h.ap("tickets")[0], 0)
        code, out = h.ap("plan-models", "--provider", "anthropic")
        self.assertEqual(code, 0, out)
        self.assertIn("механических тасков на Haiku 2, эскалировано на Sonnet 1", json.loads(out)["advice"])
        write_journal(h, [{"run": WIP, "k": "phase", "id": "build", "act": "start"}])
        code, out = h.ap("plan-models", "--provider", "anthropic")
        self.assertEqual(code, 0, out)
        self.assertNotIn("advice", json.loads(out))

    def test_plan_models_has_no_forecast_without_history(self):
        h = harness(self)
        h.plan()
        self.assertEqual(h.ap("tickets")[0], 0)
        code, out = h.ap("plan-models", "--provider", "anthropic")
        self.assertEqual(code, 0, out)
        self.assertNotIn("forecast", json.loads(out))

    def test_route_fields_take_class_from_reason(self):
        m = load_ap(harness(self))
        tk = {"plannedRouting": {"model": "haiku", "effort": "high", "reason": "class=механический; risk=обычный"}}
        self.assertEqual(m.route_fields(tk), {"class": "механический", "model": "haiku", "effort": "high"})
        self.assertEqual(m.route_fields({}), {"class": None, "model": None, "effort": None})


class Gitignore(unittest.TestCase):
    def test_state_lock_is_ignored_in_any_directory(self):
        r = subprocess.run(["git", "-C", REPO, "check-ignore", "-q", "skills/autopilot/tools/state.lock"])
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
