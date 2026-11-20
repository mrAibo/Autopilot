"""R33, R34.2: кнопки дашборда на сервере — POST /.ap-act, serve.answer.json и `ap.py await` (docs/adr/0015).
Сервер — make_server копии ap.py харнесса в потоке; CLI — отдельные процессы. Ожидания взяты из interfaces.md."""
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import unittest

import test_ap
from test_ap_audit import harness, load_ap

TOKEN = "t0ken-act-0123456789abcdef"
# Список разрешённых действий — дословно из спецификации. Новое действие в ap.py без записи здесь роняет тест.
EXPECTED_ACTIONS = ("briefing", "spec", "plan", "accept")
# Запрещённое через кнопку (R34.2): вид ожидания, команды со словами пользователя, подписи, модель, слепая приёмка.
FORBIDDEN = ("stop", "action", "finish", "opus", "reset", "dropped", "gate", "sign", "G1", "model", "blind",
             "escalate", "route", "ticket", "")


class Door(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.h.init()
        with open(os.path.join(self.h.a, "serve.token"), "w", encoding="utf-8") as f:
            f.write(TOKEN + "\n")
        self.m = load_ap(self.h)
        self.srv = self.m.make_server(self.h.a, 0, TOKEN)
        self.port = self.srv.server_port
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.state_js = os.path.join(self.h.a, "state.js")
        self.answer_file = os.path.join(self.h.a, "serve.answer.json")

    # ── помощники ───────────────────────────────────────────────────────────
    def raw_state(self):
        with open(self.state_js, "rb") as f:
            return f.read()

    def ask(self, kind):
        code, out = self.h.ap("ask", kind, "--note", "ждём")
        self.assertEqual(code, 0, out)
        return self.h.state()["waiting"]["since"]

    def post(self, body, path="/.ap-act", token=TOKEN, host=None, origin="auto", ctype="application/json",
             headers=None, raw=None):
        """-> (код, тело JSON или None). origin: "auto" — равен Host, None — без заголовка."""
        host = host or "127.0.0.1:%d" % self.port
        head = {"Host": host}
        if ctype:
            head["Content-Type"] = ctype
        if origin == "auto":
            head["Origin"] = "http://" + host
        elif origin:
            head["Origin"] = origin
        head.update(headers or {})
        data = raw if raw is not None else json.dumps(body, ensure_ascii=False).encode("utf-8")   # как JSON.stringify страницы
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=8)
        try:
            c.request("POST", path + ("?t=" + token if token else ""), body=data, headers=head)
            r = c.getresponse()
            text = r.read()
            try:
                return r.status, json.loads(text)
            except ValueError:
                return r.status, None
        finally:
            c.close()

    def press(self, kind, since, **extra):
        return self.post(dict({"kind": kind, "since": since}, **extra))

    def await_cli(self, *args):
        code, out = self.h.ap("await", *args)
        return code, out.strip()

    def log_answered(self):
        return [e for e in self.h.state()["log"] if e["k"] == "answered"]


class ActionList(Door):
    def test_allowed_actions_are_exactly_the_four_and_wait_kinds_has_accept(self):
        self.assertEqual(tuple(self.m.ALLOWED_ACTIONS), EXPECTED_ACTIONS)
        kinds = list(self.m.WAIT_KINDS)
        self.assertEqual(kinds[kinds.index("plan") + 1], "accept")
        self.assertTrue(set(EXPECTED_ACTIONS) <= set(kinds))
        for kind in ("action", "stop"):
            self.assertIn(kind, kinds)
            self.assertNotIn(kind, self.m.ALLOWED_ACTIONS)

    def test_the_page_lists_the_same_actions(self):
        with open(test_ap.TEMPLATE, encoding="utf-8") as f:
            found = re.search(r"const ACT_KINDS = \[([^\]]*)\]", f.read())
        self.assertEqual(tuple(re.findall(r'"(\w+)"', found.group(1))), EXPECTED_ACTIONS)

    def test_ask_accepts_the_new_kind_and_the_page_state_shows_it(self):
        since = self.ask("accept")
        self.assertEqual(self.h.state()["waiting"]["kind"], "accept")
        self.assertTrue(since)


class Refusals(Door):
    """403 без разбора тела и без записи: state.js после отказа тот же байт в байт."""

    def refused(self, status, **kw):
        since = self.ask("plan")
        before = self.raw_state()
        got, _ = self.post({"kind": "plan", "since": since}, **kw)
        self.assertEqual(got, status, kw)
        self.assertEqual(self.raw_state(), before, kw)
        self.assertFalse(os.path.exists(self.answer_file), kw)
        self.assertIsNotNone(self.h.state()["waiting"], kw)

    def test_wrong_or_missing_token(self):
        self.refused(403, token="wrong")
        self.refused(403, token="")

    def test_foreign_or_missing_origin(self):
        self.refused(403, origin="http://evil.example")
        self.refused(403, origin="http://127.0.0.1:1")
        self.refused(403, origin=None)
        self.refused(403, origin="null")

    def test_foreign_host(self):
        self.refused(403, host="evil.example:%d" % self.port)
        self.refused(403, host="127.0.0.1:1")

    def test_cross_site_fetch_metadata(self):
        self.refused(403, headers={"Sec-Fetch-Site": "cross-site"})

    def test_content_type_must_be_json(self):
        self.refused(403, ctype="text/plain")
        self.refused(403, ctype=None)

    def test_forbidden_kinds_are_403_and_change_nothing(self):
        for wait in ("stop", "action", "briefing"):
            since = self.ask(wait)
            before = self.raw_state()
            for kind in FORBIDDEN:
                status, _ = self.post({"kind": kind, "since": since, "answer": "x"})
                self.assertEqual(status, 403, (wait, kind))
                self.assertEqual(self.raw_state(), before, (wait, kind))
            self.assertFalse(os.path.exists(self.answer_file))

    def test_forbidden_kind_without_the_other_fields_is_403_too(self):
        self.ask("stop")
        for body in ({"kind": "finish"}, {"kind": "opus", "tickets": "03"}, {"kind": "stop", "since": None}):
            self.assertEqual(self.post(body)[0], 403, body)

    def test_other_post_paths_are_405(self):
        self.ask("plan")
        before = self.raw_state()
        for path in ("/state.js", "/dashboard.html", "/", "/.ap-ping", "/.ap-act/", "/.ap-act2", "/nope"):
            for token in (TOKEN, ""):
                self.assertEqual(self.post({"kind": "plan"}, path=path, token=token)[0], 405, (path, token))
        self.assertEqual(self.raw_state(), before)

    def test_big_body_is_413_before_it_is_read(self):
        since = self.ask("briefing")
        before = self.raw_state()
        status, _ = self.post(None, raw=json.dumps({"kind": "briefing", "since": since,
                                                    "answer": "я" * 9000}).encode("utf-8"))
        self.assertEqual(status, 413)
        # заявлено 10 МБ, тела нет: сервер решает по Content-Length и не ждёт тела
        s = socket.create_connection(("127.0.0.1", self.port), timeout=5)
        try:
            s.sendall(("POST /.ap-act?t=%s HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nOrigin: http://127.0.0.1:%d\r\n"
                       "Content-Type: application/json\r\nContent-Length: 10000000\r\n\r\n"
                       % (TOKEN, self.port, self.port)).encode())
            self.assertIn(b" 413 ", s.recv(200))
        finally:
            s.close()
        self.assertEqual(self.raw_state(), before)

    def test_a_body_of_exactly_8192_bytes_is_still_read(self):
        since = self.ask("spec")
        pad = " " * (8192 - len(json.dumps({"kind": "spec", "since": since}).encode()))
        raw = json.dumps({"kind": "spec", "since": since}).encode() + pad.encode()
        self.assertEqual(len(raw), 8192)
        self.assertEqual(self.post(None, raw=raw)[0], 200)

    def test_bad_requests_are_400(self):
        since = self.ask("briefing")
        before = self.raw_state()
        for raw in (b"{not json", b"[]", b'"briefing"', b"null", b"\xff\xfe", b""):
            self.assertEqual(self.post(None, raw=raw)[0], 400, raw)
        for body in ({"since": since},                                              # нет kind
                     {"kind": 3, "since": since},
                     {"kind": "briefing"},                                          # нет since
                     {"kind": "briefing", "since": 5, "answer": "да"},
                     {"kind": "briefing", "since": since},                          # нет ответа
                     {"kind": "briefing", "since": since, "answer": ""},
                     {"kind": "briefing", "since": since, "answer": "   \n"},
                     {"kind": "briefing", "since": since, "answer": ["да"]}):
            status, reply = self.post(body)
            self.assertEqual((status, (reply or {}).get("error")), (400, "bad-request"), body)
        self.assertEqual(self.raw_state(), before)
        self.assertFalse(os.path.exists(self.answer_file))

    def test_no_content_length_is_400(self):
        self.ask("plan")
        s = socket.create_connection(("127.0.0.1", self.port), timeout=5)
        try:
            s.sendall(("POST /.ap-act?t=%s HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nOrigin: http://127.0.0.1:%d\r\n"
                       "Content-Type: application/json\r\n\r\n"
                       % (TOKEN, self.port, self.port)).encode())
            self.assertIn(b" 400 ", s.recv(200))
        finally:
            s.close()

    def test_conflicts_are_409_with_a_reason(self):
        # нет ожидания
        status, reply = self.press("plan", "2026-01-01T00:00:00+00:00")
        self.assertEqual((status, reply), (409, {"ok": False, "error": "no-wait"}))
        since = self.ask("plan")
        before = self.raw_state()
        self.assertEqual(self.press("spec", since), (409, {"ok": False, "error": "other-kind"}))
        self.assertEqual(self.press("accept", since), (409, {"ok": False, "error": "other-kind"}))
        self.assertEqual(self.press("plan", since + "x"), (409, {"ok": False, "error": "stale"}))
        self.assertEqual(self.press("plan", ""), (409, {"ok": False, "error": "stale"}))
        self.assertEqual(self.raw_state(), before)
        self.assertFalse(os.path.exists(self.answer_file))

    def test_busy_state_lock_is_503(self):
        since = self.ask("plan")
        before = self.raw_state()
        self.m.ACT_LOCK_TIMEOUT = 0.3
        t0 = time.monotonic()
        with self.m.locked_state():
            status, reply = self.press("plan", since)
        self.assertEqual((status, reply), (503, {"ok": False, "error": "busy"}))
        self.assertGreaterEqual(time.monotonic() - t0, 0.25)             # сервер ждал блокировку, а не упал на ней
        self.assertEqual(self.raw_state(), before)
        self.assertEqual(self.press("plan", since)[0], 200)             # блокировку отпустили — нажатие проходит


class LockContention(Door):
    """Нажатие и команда CLI идут через один state.lock. На Windows чужая блокировка байта 0 не даёт даже прочитать его:
    второй должен ждать до срока и отказать словами `die`, а не падать на PermissionError."""

    def test_a_second_holder_waits_for_the_first_and_then_gets_the_lock(self):
        got = []

        def second():
            try:
                with self.m.locked_state(timeout=10):
                    got.append("locked")
            except BaseException as exc:                                    # PermissionError или SystemExit
                got.append(repr(exc))
        with self.m.locked_state():
            t = threading.Thread(target=second)
            t.start()
            time.sleep(0.5)
            self.assertEqual(got, [])                                       # ещё ждёт
        t.join(15)
        self.assertEqual(got, ["locked"])

    def test_a_second_holder_that_runs_out_of_time_gets_the_busy_refusal(self):
        got = []

        def second():
            try:
                with self.m.locked_state(timeout=0.3):
                    got.append("locked")
            except BaseException as exc:
                got.append(type(exc).__name__)
        with self.m.locked_state():
            t = threading.Thread(target=second)
            t.start()
            t.join(15)
        self.assertEqual(got, ["SystemExit"])


class Press(Door):
    def test_each_allowed_kind_closes_its_wait_with_source_dashboard(self):
        for kind in EXPECTED_ACTIONS:
            since = self.ask(kind)
            extra = {"answer": "делай через postgres"} if kind == "briefing" else {}
            status, reply = self.press(kind, since, **extra)
            self.assertEqual((status, reply), (200, {"ok": True, "kind": kind}), kind)
            state = self.h.state()
            self.assertIsNone(state["waiting"], kind)
            self.assertEqual(state["waits"][-1]["kind"], kind)
            self.assertEqual(state["waits"][-1]["from"], since)
            last = self.log_answered()[-1]
            self.assertEqual((last["kind"], last["source"]), (kind, "dashboard"))
            self.assertNotIn("postgres", self.raw_state().decode("utf-8"), "ответ не в state.js")
            self.assertTrue(os.path.exists(self.answer_file), kind)
            code, out = self.await_cli("--timeout", "0")
            self.assertEqual(code, 0, out)
            self.assertFalse(os.path.exists(self.answer_file), "await удаляет файл")

    def test_answer_file_holds_the_answer_atomically_and_only_the_contract_fields(self):
        since = self.ask("briefing")
        self.assertEqual(self.press("briefing", since, answer="  таблица, ночь — без звонков  ")[0], 200)
        with open(self.answer_file, encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(set(rec), {"kind", "since", "answer", "source", "at"})
        self.assertEqual((rec["kind"], rec["since"], rec["source"]), ("briefing", since, "dashboard"))
        self.assertEqual(rec["answer"], "таблица, ночь — без звонков")
        self.assertFalse(os.path.exists(self.answer_file + ".tmp"))

    def test_secret_shapes_are_redacted_and_the_answer_is_cut_to_2000(self):
        since = self.ask("briefing")
        fake_key = "sk-" + "a1B2" * 6                                       # по форме ключ, значения нет
        self.assertEqual(self.press("briefing", since, answer="ключ %s и всё" % fake_key)[0], 200)
        with open(self.answer_file, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn(fake_key, text)
        self.assertIn("[REDACTED:API_KEY]", text)
        since = self.ask("briefing")
        self.assertEqual(self.press("briefing", since, answer="я" * 3000)[0], 200)
        with open(self.answer_file, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)["answer"]), 2000)

    def test_extra_body_fields_change_nothing_else(self):
        since = self.ask("plan")
        before = self.h.state()
        status, _ = self.press("plan", since, gate="G3", ok=True, model="opus", signature="x", blind={"ok": True},
                               tier="T9", finish=True, answer="не нужен")
        self.assertEqual(status, 200)
        after = self.h.state()
        moved = {"waiting", "waits", "log", "rev", "updatedAt", "beats"}
        self.assertEqual({k: v for k, v in after.items() if k not in moved},
                         {k: v for k, v in before.items() if k not in moved})
        with open(self.answer_file, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["answer"], "")                    # ответ пишется только для briefing
        self.assertNotIn("не нужен", self.raw_state().decode("utf-8"))

    def test_the_snapshot_in_the_page_is_refreshed(self):
        since = self.ask("spec")
        self.press("spec", since)
        with open(os.path.join(self.h.a, "dashboard.html"), encoding="utf-8") as f:
            snapshot = f.read().split("/*STATE-BEGIN*/", 1)[1].split("/*STATE-END*/", 1)[0]
        self.assertIn('"waiting": null', snapshot)


class Races(Door):
    def test_second_press_with_the_same_since_is_409(self):
        since = self.ask("plan")
        self.assertEqual(self.press("plan", since)[0], 200)
        self.assertEqual(self.press("plan", since), (409, {"ok": False, "error": "no-wait"}))
        self.assertEqual(len(self.log_answered()), 1)

    def test_two_presses_at_once_one_wins(self):
        since = self.ask("plan")
        out = []
        gate = threading.Barrier(2)

        def go():
            gate.wait()
            out.append(self.press("plan", since)[0])
        threads = [threading.Thread(target=go) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(20)
        self.assertEqual(sorted(out), [200, 409])
        self.assertEqual(len(self.log_answered()), 1)
        self.assertEqual(len(self.h.state()["waits"]), 1)

    def test_cli_answered_first_then_the_press_is_409(self):
        since = self.ask("plan")
        self.assertEqual(self.h.ap("answered")[0], 0)
        self.assertEqual(self.press("plan", since), (409, {"ok": False, "error": "no-wait"}))
        self.assertNotIn("source", self.log_answered()[-1])                  # у команды CLI source не пишется
        self.assertFalse(os.path.exists(self.answer_file))

    def test_press_first_then_cli_answered_closes_nothing_twice(self):
        since = self.ask("plan")
        self.assertEqual(self.press("plan", since)[0], 200)
        self.assertEqual(self.h.ap("answered")[0], 0)
        self.assertEqual(len(self.log_answered()), 1)
        self.assertEqual(len(self.h.state()["waits"]), 1)

    def test_press_and_cli_queued_on_the_lock_exactly_one_wins(self):
        since = self.ask("plan")
        result = {}
        with self.m.locked_state():
            presser = threading.Thread(target=lambda: result.update(press=self.press("plan", since)))
            presser.start()
            cli = threading.Thread(target=lambda: result.update(cli=self.h.ap("answered")))
            cli.start()
            time.sleep(0.8)                                                 # оба ждут блокировку
        presser.join(30)
        cli.join(30)
        self.assertEqual(result["cli"][0], 0)
        entries = self.log_answered()
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(self.h.state()["waits"]), 1)
        if result["press"][0] == 200:
            self.assertEqual(entries[0]["source"], "dashboard")
        else:
            self.assertEqual(result["press"], (409, {"ok": False, "error": "no-wait"}))
            self.assertNotIn("source", entries[0])


class AnswerFile(Door):
    def pressed(self, kind="briefing", **extra):
        since = self.ask(kind)
        self.assertEqual(self.press(kind, since, **extra)[0], 200)
        self.assertTrue(os.path.exists(self.answer_file))
        return since

    def test_ask_removes_a_stale_answer(self):
        self.pressed(answer="да")
        self.ask("briefing")
        self.assertFalse(os.path.exists(self.answer_file))

    def test_answered_removes_the_answer(self):
        self.pressed(answer="да")
        self.assertEqual(self.h.ap("answered")[0], 0)
        self.assertFalse(os.path.exists(self.answer_file))

    def test_a_command_that_closes_an_open_wait_removes_a_stale_answer(self):
        self.ask("plan")
        with open(self.answer_file, "w", encoding="utf-8") as f:        # залежавшийся файл прошлого ожидания
            f.write("{}")
        self.assertEqual(self.h.ap("tests", "1/0")[0], 0)               # `tests` закрывает ожидание сам (MOVES_ON)
        self.assertIsNone(self.h.state()["waiting"])
        self.assertFalse(os.path.exists(self.answer_file))


class Await(Door):
    def spawn(self, *args):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1", AUTOPILOT_HOME=self.h.home)
        proc = subprocess.Popen([sys.executable, os.path.join(self.h.a, "ap.py"), "await"] + list(args),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                env=env, cwd=self.h.root)
        self.addCleanup(lambda: proc.poll() is None and proc.kill())
        return proc

    def finish(self, proc, timeout=40):
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out.strip()

    def test_no_wait_is_code_4(self):
        code, out = self.await_cli("--timeout", "0")
        self.assertEqual(code, 4, out)
        self.assertIn("ожидания нет", out)

    def test_nothing_came_in_time_is_code_3(self):
        self.ask("plan")
        t0 = time.monotonic()
        code, out = self.await_cli("--timeout", "2")
        self.assertEqual(code, 3, out)
        self.assertIn("нет ответа", out)
        self.assertGreaterEqual(time.monotonic() - t0, 1.9)
        self.assertEqual(self.h.state()["waiting"]["kind"], "plan")      # ожидание не тронуто

    def test_a_press_during_await_returns_the_answer_and_removes_the_file(self):
        since = self.ask("briefing")
        proc = self.spawn("--timeout", "60")
        time.sleep(2.5)
        self.assertIsNone(proc.poll())
        self.assertEqual(self.press("briefing", since, answer="ночью не звоним")[0], 200)
        code, out = self.finish(proc)
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out), {"answered": True, "kind": "briefing", "source": "dashboard",
                                            "answer": "ночью не звоним"})
        self.assertFalse(os.path.exists(self.answer_file))

    def test_an_answer_in_chat_closes_await_without_an_answer_field(self):
        self.ask("spec")
        proc = self.spawn("--timeout", "60")
        time.sleep(2.5)
        self.assertEqual(self.h.ap("answered")[0], 0)                    # await не держит state.lock
        code, out = self.finish(proc)
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out), {"answered": True, "kind": "spec", "source": "chat"})

    def test_a_non_briefing_press_is_source_dashboard_with_an_empty_answer(self):
        since = self.ask("accept")
        self.press("accept", since)
        code, out = self.await_cli("--timeout", "0")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out), {"answered": True, "kind": "accept", "source": "dashboard", "answer": ""})

    def test_a_press_before_await_is_not_lost(self):
        since = self.ask("briefing")
        self.press("briefing", since, answer="вкладка закрылась, а ответ дошёл")
        code, out = self.await_cli("--timeout", "0")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["answer"], "вкладка закрылась, а ответ дошёл")
        self.assertEqual(self.await_cli("--timeout", "0")[0], 4)         # файл забрали: второй раз — ничего нет

    def test_a_new_wait_of_the_same_kind_is_not_the_awaited_one(self):
        self.ask("plan")
        proc = self.spawn("--timeout", "60")
        time.sleep(2.5)
        self.h.ap("answered")
        self.ask("plan")
        code, out = self.finish(proc)
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["source"], "chat")

    def test_await_does_not_hold_the_state_lock(self):
        self.ask("plan")
        proc = self.spawn("--timeout", "60")
        time.sleep(2.0)
        self.assertIsNone(proc.poll())                                   # await ещё ждёт
        with self.m.locked_state(timeout=2):                             # занято — die: тест упадёт
            pass
        proc.kill()
        proc.communicate()

    def test_timeout_must_be_a_number_and_is_capped(self):
        self.ask("plan")
        code, out = self.await_cli("--timeout", "много")
        self.assertEqual(code, 1, out)
        self.assertEqual(self.m.AWAIT_MAX, 3500)
        self.assertEqual(self.m.AWAIT_DEFAULT, 300)

    def test_await_without_state_is_an_error(self):
        os.unlink(self.state_js)
        code, out = self.await_cli("--timeout", "0")
        self.assertEqual(code, 1, out)
        self.assertIn("await: state.js", out)


if __name__ == "__main__":
    unittest.main()
