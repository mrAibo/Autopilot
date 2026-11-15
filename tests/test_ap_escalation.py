"""`ap.py ticket NN retry --cause tests --escalate`: единственная эскалация Haiku -> Sonnet.

Каждый тест поднимает временный git-репозиторий, пишет в state.js таск с маршрутом Haiku и
зарегистрированного Sonnet-исполнителя (`repairAgent`) и зовёт ap.py отдельным процессом.
"""

import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(os.path.dirname(HERE), "skills", "autopilot")
TOOLS = os.path.join(SKILL, "tools")
AGENT_FILE = ".claude/agents/autopilot-executor-repair.md"
TICKET = ("# 01 — Переименование\n\n**Требования:** R01\n**Зависит от:** —\n**Зона:** `src/a.py`\n"
          "**Волна:** 1\n**Ревью:** нет\n**Модель:** обычная\n\n## Критерии приёмки\n\n- [ ] что-то\n")


class Escalation(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-esc-")
        self.home = tempfile.mkdtemp(prefix="ap-esc-home-")
        self.git("init", "-q")
        self.a = os.path.join(self.root, ".autopilot")
        os.makedirs(self.a)
        for path in glob.glob(os.path.join(TOOLS, "*.py")):
            shutil.copy(path, self.a)
        shutil.copy(os.path.join(SKILL, "phases", "dashboard-template.html"),
                    os.path.join(self.a, "dashboard.html"))
        self.ap("init", "--slug", "esc", "--title", "Эскалация", "--skill-dir", SKILL)
        self.dir = os.path.join(self.a, self.state()["dir"])
        os.makedirs(os.path.join(self.dir, "tickets"), exist_ok=True)
        with open(os.path.join(self.dir, "tickets", "01-rename.md"), "w", encoding="utf-8") as f:
            f.write(TICKET)
        self.ap("tickets")
        agent = os.path.join(self.root, *AGENT_FILE.split("/"))
        os.makedirs(os.path.dirname(agent))
        with open(agent, "wb") as f:
            f.write(b"---\nname: autopilot-executor-repair\nmodel: sonnet\n---\n")
        with open(agent, "rb") as f:
            self.sha = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), capture_output=True, text=True)

    def ap(self, *args):
        env = dict(os.environ, AUTOPILOT_NO_UPDATE_CHECK="1", AUTOPILOT_HOME=self.home)
        r = subprocess.run([sys.executable, os.path.join(self.a, "ap.py")] + list(args) + ["--no-serve"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=env, cwd=self.root)
        return r.returncode, r.stdout + r.stderr

    def state(self):
        with open(os.path.join(self.a, "state.js"), encoding="utf-8") as f:
            return json.loads(f.read().split("=", 1)[1])

    def edit(self, fn):
        state = self.state()
        fn(state)
        with open(os.path.join(self.a, "state.js"), "w", encoding="utf-8") as f:
            f.write("window.STATE =\n" + json.dumps(state, ensure_ascii=False))

    def prepare(self, model="haiku", retries=1, repair=True, **extra):
        def fn(state):
            tk = state["tickets"][0]
            tk.update(routing={"provider": "anthropic", "model": model, "effort": "high", "verified": True,
                               "agentType": "autopilot-executor-01-rename"},
                      retries=retries, status="in-progress", **extra)
            if repair:
                state["repairAgent"] = {"agentType": "autopilot-executor-repair", "agentFile": AGENT_FILE,
                                        "model": "sonnet", "effort": "high", "effortEnforced": True,
                                        "profileSha": self.sha}
        self.edit(fn)

    def escalate(self, cause="tests"):
        return self.ap("ticket", "01", "retry", "--cause", cause, "--escalate")

    def test_haiku_after_first_retry_moves_to_sonnet_and_is_recorded(self):
        self.prepare()
        code, out = self.escalate()
        self.assertEqual(code, 0, out)
        tk = self.state()["tickets"][0]
        self.assertEqual(tk["escalatedFrom"]["model"], "haiku")
        self.assertEqual((tk["routing"]["model"], tk["routing"]["effort"]), ("sonnet", "high"))
        self.assertEqual(tk["routing"]["agentType"], "autopilot-executor-repair")
        self.assertEqual((tk["retries"], tk["status"]), (2, "in-progress"))
        self.assertTrue(any(e["k"] == "escalate" and e["id"] == "01" for e in self.state()["log"]))
        with open(os.path.join(self.a, "run-log.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(line) for line in f]
        self.assertTrue(any(r["k"] == "ticket" and r.get("act") == "escalate" for r in rows))

    def test_second_escalation_is_refused(self):
        self.prepare()
        self.assertEqual(self.escalate()[0], 0)
        before = self.state()["tickets"][0]
        code, out = self.escalate()
        self.assertNotEqual(code, 0)
        self.assertIn("вторая эскалация не допускается", out)
        self.assertEqual(self.state()["tickets"][0], before)

    def test_ticket_not_on_haiku_is_refused(self):
        self.prepare(model="sonnet")
        code, out = self.escalate()
        self.assertNotEqual(code, 0)
        self.assertIn("только для таска на Haiku", out)
        self.assertNotIn("escalatedFrom", self.state()["tickets"][0])

    def test_before_first_retry_is_refused(self):
        self.prepare(retries=0)
        code, out = self.escalate()
        self.assertNotEqual(code, 0)
        self.assertIn("после первого дозапроса", out)
        self.assertEqual(self.state()["tickets"][0]["routing"]["model"], "haiku")

    def test_other_cause_is_refused_and_keeps_the_haiku_route(self):
        self.prepare()
        code, out = self.escalate(cause="reasoning")  # decide() says replan, not retry
        self.assertNotEqual(code, 0)
        self.assertEqual(self.state()["tickets"][0]["routing"]["model"], "haiku")

    def test_without_registered_sonnet_executor_is_refused(self):
        self.prepare(repair=False)
        code, out = self.escalate()
        self.assertNotEqual(code, 0)
        self.assertIn("нет зарегистрированного Sonnet-исполнителя", out)

    def test_escalate_flag_needs_retry(self):
        self.prepare()
        code, out = self.ap("ticket", "01", "fail", "--escalate")
        self.assertNotEqual(code, 0)
        self.assertIn("--escalate работает только", out)

    def test_plain_retry_does_not_escalate(self):
        self.prepare(retries=0)
        self.assertEqual(self.ap("ticket", "01", "retry", "--cause", "tests")[0], 0)
        tk = self.state()["tickets"][0]
        self.assertEqual(tk["routing"]["model"], "haiku")
        self.assertNotIn("escalatedFrom", tk)


if __name__ == "__main__":
    unittest.main()
