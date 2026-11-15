"""Доделки после аудита: страница без токена не несёт данных (R01), адрес с токеном печатает
только `url` (R02), копия страницы обновляется из шаблона (A01)."""

import contextlib
import http.client
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
from unittest import mock

import test_ap
from test_ap_audit import harness, load_ap

TOKEN = "followups-token-0123456789"
PAGE = '<html><script>/*STATE-BEGIN*/window.STATE={"slug":"secret-run"};/*STATE-END*/</script></html>'


class TokenlessPage(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ap-fu-")
        self.addCleanup(shutil.rmtree, self.dir, True)
        for rel, text in (("dashboard.html", PAGE), ("index.html", PAGE), ("state.js", "window.STATE={}")):
            with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as f:
                f.write(text)
        spec = importlib.util.spec_from_file_location("ap_fu", test_ap.AP)
        self.ap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.ap)
        self.srv = self.ap.make_server(self.dir, 0, TOKEN)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def fetch(self, path, method="GET"):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_port, timeout=5)
        try:
            c.request(method, path, headers={"Host": "127.0.0.1:%d" % self.srv.server_port})
            r = c.getresponse()
            return r.status, r.read().decode("utf-8")
        finally:
            c.close()

    def test_without_the_token_the_page_comes_with_null_state(self):
        for path in ("/dashboard.html", "/dashboard.html?t=wrong", "/", "/index.html"):
            status, body = self.fetch(path)
            self.assertEqual(status, 200, path)
            self.assertIn("window.STATE=null;", body, path)
            self.assertNotIn("secret-run", body, path)

    def test_with_the_token_the_page_carries_the_snapshot(self):
        status, body = self.fetch("/dashboard.html?t=" + TOKEN)
        self.assertEqual(status, 200)
        self.assertIn('window.STATE={"slug":"secret-run"};', body)

    def test_the_file_on_disk_is_not_touched_and_head_still_works(self):
        self.fetch("/dashboard.html")
        with open(os.path.join(self.dir, "dashboard.html"), encoding="utf-8") as f:
            self.assertEqual(f.read(), PAGE)
        self.assertEqual(self.fetch("/dashboard.html", "HEAD")[0], 200)


class FailedSubstitution(TokenlessPage):
    """Подмена снимка не удалась — страница без токена не отдаётся как есть."""

    def put(self, data, rel="dashboard.html"):
        with open(os.path.join(self.dir, rel), "wb") as f:
            f.write(data if isinstance(data, bytes) else data.encode("utf-8"))

    def test_a_page_the_substitution_cannot_handle_is_403_not_the_raw_file(self):
        for label, data in (("no markers", "<html>secret-run</html>"),
                            ("end before begin", "<html>secret-run /*STATE-END*/ /*STATE-BEGIN*/ x</html>"),
                            ("not utf-8", bytes([255, 254]) + b" secret-run /*STATE-BEGIN*/x/*STATE-END*/")):
            self.put(data)
            for method in ("GET", "HEAD"):
                status, body = self.fetch("/dashboard.html", method)
                self.assertEqual(status, 403, "%s %s" % (label, method))
                self.assertNotIn("secret-run", body, label)
            self.assertEqual(self.fetch("/dashboard.html?t=wrong")[0], 403, label)

    def test_the_end_marker_inside_the_snapshot_does_not_cut_the_substitution_short(self):
        raw = ('<html><script>/*STATE-BEGIN*/window.STATE={"note":"a/*STATE-END*/leak-me","slug":"secret-run"};'
               '/*STATE-END*/</script><p>tail</p></html>')
        self.put(raw)
        status, body = self.fetch("/dashboard.html")
        self.assertEqual(status, 200)
        self.assertIn("/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/</script><p>tail</p>", body)
        self.assertNotIn("leak-me", body)
        self.assertNotIn("secret-run", body)
        self.assertEqual(self.fetch("/dashboard.html?t=" + TOKEN)[1], raw)

    def test_the_snapshot_writer_escapes_the_end_marker(self):
        h = harness(self)
        h.init()
        m = load_ap(h)
        m.write_snapshot(dict(h.state(), note="a/*STATE-END*/b"))
        with open(m.PAGE, encoding="utf-8") as f:
            page = f.read()
        self.assertEqual(page.count("/*STATE-END*/"), 1)
        found = re.search(r"/\*STATE-BEGIN\*/window\.STATE=(.*?);/\*STATE-END\*/", page, re.S)
        self.assertEqual(json.loads(found.group(1))["note"], "a/*STATE-END*/b")


class AddressPrinting(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.h.init()
        self.m = load_ap(self.h)

    def test_page_url_has_the_token_only_when_asked(self):
        self.assertNotIn("?t=", self.m.page_url(8123, with_token=False))
        self.assertEqual(self.m.page_url(8123, with_token=False), "http://localhost:8123/dashboard.html")
        self.assertIn("?t=" + self.m.serve_token(), self.m.page_url(8123))

    def test_serve_reports_the_running_server_without_the_token(self):
        with mock.patch.object(self.m, "recorded", return_value=(8123, 1)), \
                mock.patch.object(self.m, "http_ok", return_value=True), \
                mock.patch.object(self.m, "is_guarded_server", return_value=True), \
                mock.patch.object(self.m, "cmdline", return_value=""):
            state = self.h.state()
            self.assertNotIn("?t=", self.m.serve(state))
            self.assertIn("?t=", self.m.serve(state, with_token=True))

    def test_no_command_form_asks_serve_for_the_token(self):
        asked = []

        def fake(state, with_token=False):
            asked.append(with_token)
            return "сервер"
        for argv in ([], ["sync"]):
            with mock.patch.object(self.m, "serve", fake), mock.patch.object(sys, "argv", ["ap.py"] + argv), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.m.main()
            self.assertFalse(asked[-1], argv)
            self.assertNotIn("?t=", out.getvalue())

    def test_url_command_prints_the_address_with_the_token_and_creates_it(self):
        token_file = os.path.join(self.h.a, "serve.token")
        self.assertFalse(os.path.exists(token_file))
        with open(os.path.join(self.h.a, "serve.pid"), "w", encoding="utf-8") as f:
            f.write("54321 99999\n")
        code, out = self.h.ap("url")
        self.assertEqual(code, 0, "url упал")
        with open(token_file, encoding="utf-8") as f:
            token = f.read().strip()
        self.assertGreaterEqual(len(token), 16)
        self.assertIn("http://localhost:54321/dashboard.html?t=" + token, out)

    def run_main(self, m, *argv):
        with mock.patch.object(m, "recorded", return_value=(8123, 1)),                 mock.patch.object(m, "http_ok", return_value=True),                 mock.patch.object(m, "is_guarded_server", return_value=True),                 mock.patch.object(m, "cmdline", return_value=""),                 mock.patch.dict(os.environ, {"SSH_CONNECTION": "", "CI": ""}),                 mock.patch.object(sys, "argv", ["ap.py"] + list(argv)),                 contextlib.redirect_stdout(io.StringIO()) as out:
            m.main()
        return out.getvalue()

    def test_real_serve_path_of_stage_and_init_prints_no_token(self):
        self.h.write("manifest.md", test_ap.MANIFEST)
        with open(os.path.join(self.h.a, "serve.token"), "w", encoding="utf-8") as f:
            f.write(TOKEN + chr(10))
        fresh = harness(self)
        mf = load_ap(fresh)
        with open(os.path.join(fresh.a, "serve.token"), "w", encoding="utf-8") as f:
            f.write(TOKEN + chr(10))
        for m, argv in ((self.m, ("stage", "spec")),
                        (mf, ("init", "--slug", "repair-bot", "--title", "Бот", "--skill-dir", test_ap.SKILL))):
            out = self.run_main(m, *argv)
            self.assertIn("http://localhost:8123/dashboard.html", out, argv[0])
            self.assertNotIn("?t=", out, argv[0])
            self.assertNotIn(TOKEN, out, argv[0])


class RefreshDashboard(unittest.TestCase):
    def setUp(self):
        self.h = harness(self)
        self.h.init()
        self.m = load_ap(self.h)
        self.page = os.path.join(self.h.a, "dashboard.html")

    def stale(self, mark="<!--old-->"):
        with open(self.page, "a", encoding="utf-8") as f:
            f.write(mark)

    def test_a_current_copy_is_left_alone(self):
        before = os.stat(self.page).st_mtime_ns
        self.assertEqual(self.m.refresh_dashboard(self.h.state()), "")
        self.assertEqual(os.stat(self.page).st_mtime_ns, before)

    def test_a_stale_copy_is_upgraded_from_the_template(self):
        self.stale()
        line = self.m.refresh_dashboard(self.h.state())
        self.assertIn("обновлён", line)
        with open(self.page, encoding="utf-8") as f:
            self.assertNotIn("<!--old-->", f.read())
        self.assertEqual(self.m.refresh_dashboard(self.h.state()), "")

    def test_a_failed_upgrade_is_one_line_not_an_exception(self):
        self.stale()
        fake = tempfile.mkdtemp(prefix="ap-skill-")
        self.addCleanup(shutil.rmtree, fake, True)
        os.makedirs(os.path.join(fake, "phases"))
        with open(os.path.join(fake, "phases", "dashboard-template.html"), "w", encoding="utf-8") as f:
            f.write("<html>not a dashboard</html>")
        line = self.m.refresh_dashboard(dict(self.h.state(), skillDir=fake))
        self.assertTrue(line.startswith("!") and "\n" not in line, line)

    def project_without_the_upgrade_module(self):
        os.remove(os.path.join(self.h.a, "dashboard_upgrade.py"))
        paths = [p for p in sys.path if not os.path.exists(os.path.join(p, "dashboard_upgrade.py"))]
        for patch in (mock.patch.object(sys, "path", paths), mock.patch.dict(sys.modules)):
            patch.start()
            self.addCleanup(patch.stop)
        sys.modules.pop("dashboard_upgrade", None)

    def test_a_live_project_without_dashboard_upgrade_py_takes_it_from_the_skill(self):
        self.stale("<!--old-live-->")      # другой текст: бэкап называется по хэшу, два прогона за секунду столкнулись бы
        self.project_without_the_upgrade_module()
        line = self.m.refresh_dashboard(self.h.state())
        self.assertEqual(line, "дашборд обновлён из шаблона навыка")
        with open(self.page, encoding="utf-8") as f:
            self.assertNotIn("<!--old-live-->", f.read())

    def test_an_untrusted_skill_dir_is_not_imported_from_and_is_one_line(self):
        self.stale()
        self.project_without_the_upgrade_module()
        with mock.patch.object(self.m, "skill_dir_trusted", return_value=False):
            line = self.m.refresh_dashboard(self.h.state())
        self.assertTrue(line.startswith("!") and chr(10) not in line, line)

    def test_stage_refreshes_a_stale_copy(self):
        self.stale()
        code, out = self.h.ap("stage", "spec")
        self.assertEqual(code, 0, out)
        self.assertIn("дашборд обновлён из шаблона", out)
        with open(self.page, encoding="utf-8") as f:
            self.assertNotIn("<!--old-->", f.read())


if __name__ == "__main__":
    unittest.main()
