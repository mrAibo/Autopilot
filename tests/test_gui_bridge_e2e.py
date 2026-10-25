"""Real OS process bridge test without contacting the paid model provider.

A clean synthetic Git project is initialized using the real ap.py lifecycle.
Only the Codex CLI binary is substituted with an offline Python process,
so bridge receipt writes, subprocess launch, JSONL token tracking, independent
host tests, Git cherry-pick and final acceptance are all real.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills" / "autopilot" / "tools"))
import test_ap
import codex_dispatch
import gui_bridge


FAKE_CODEX = r'''
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

# The stub ONLY writes to the disposable worktree passed by the test.
assert len(sys.argv) == 4 and sys.argv[1] == "--cd" and sys.argv[-1] == "-"
target = Path(sys.argv[2])
assert target.is_dir() and target.as_posix().endswith("/.autopilot/worktrees/T01")
prompt = sys.stdin.read()
assert "Каркас" in prompt
script = target / "src" / "core" / "calc.py"
assert script.is_file()
script.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
for args in (["add", "src/core/calc.py"], ["commit", "-qm", "Synthetic offline Codex worker"]):
    result = subprocess.run(["git", "-C", str(target), *args],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
print(json.dumps({"type":"thread.started","thread_id":"stub-" + uuid4().hex}))
print(json.dumps({"type":"turn.completed","usage":{
    "input_tokens":130,"output_tokens":40,"cached_input_tokens":35}}))
'''


class BridgeRealProcessLifecycle(unittest.TestCase):
    def setUp(self):
        # No actual GUI window is controlled by this test.
        self.harness = test_ap.Run("test_init_creates_run")
        self.harness.setUp()
        self.addCleanup(self.harness.tearDown)
        h = self.harness
        h.plan(strict=True, isolated=True)
        self.assertEqual(h.ap("tickets")[0], 0)
        h.git("config", "user.email", "test@example.invalid")
        h.git("config", "user.name", "Autopilot Offline E2E")
        source = Path(h.root) / "src" / "core"
        source.mkdir(parents=True)
        (source / "calc.py").write_text(
            "def add(a, b):\n    return a - b\n", encoding="utf-8")
        (Path(h.root) / "test_core.py").write_text(
            "import unittest\nfrom src.core.calc import add\n"
            "class TestCalc(unittest.TestCase):\n"
            " def test_add(self): self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8")
        caps = Path(h.a) / "model-capabilities.json"
        caps.write_text(json.dumps({
            "provider": "openai", "model_selection": True,
            "models": {"gpt-6-luna": ["low"]}
        }), encoding="utf-8")
        rc, output = h.ap("ticket", "01", "route", "--provider", "openai",
                          "--model", "gpt-6-luna", "--effort", "low",
                          "--reason", "offline-synthetic-test",
                          "--capabilities", str(caps))
        self.assertEqual(rc, 0, output)
        self.assertEqual(h.ap("budget", "--tokens", "2000")[0], 0)
        h.git("add", "src/core/calc.py", "test_core.py", ".gitignore")
        h.commit("trusted baseline source and unmodified tests")
        self.fake = Path(h.root).parent / ("fake_codex_" + Path(h.root).name + ".py")
        self.fake.write_text(FAKE_CODEX, encoding="utf-8")
        self.addCleanup(lambda: self.fake.unlink(missing_ok=True))
        for name in ("gui_bridge.py", "codex_dispatch.py"):
            shutil.copy(Path(gui_bridge.__file__).parent / name, Path(h.a) / name)

    def controller(self, *opts):
        proc = subprocess.run(
            [sys.executable, str(Path(self.harness.a)/"controller.py"),
             "--root", self.harness.root, *opts], cwd=self.harness.root,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=45)
        self.assertTrue(proc.stdout.strip(), proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_actual_offline_subprocess_to_accepted_git_and_no_replay(self):
        h = self.harness
        for action in ("prepare", "start"):
            code, out = self.controller("--advance")
            self.assertEqual(code, 0, out)
            self.assertEqual(out["completed"]["action"], action)
        before = h.state()["tickets"][0]
        self.assertEqual(before["status"], "in-progress")
        self.assertEqual(before["routing"]["model"], "gpt-6-luna")
        self.assertEqual(before["routing"]["effort"], "low")

        # Full real model-routing/profile/brief check; replace only the
        # external executable with a locally executed offline stub.
        real_checked = codex_dispatch.checked_dispatch
        def offline_checked(*args, **kwargs):
            conf = real_checked(*args, **kwargs)
            conf["command"] = [sys.executable, str(self.fake),
                               "--cd", conf["cwd"]]
            return conf

        with patch.object(codex_dispatch, "checked_dispatch", offline_checked):
            preview = gui_bridge.bridge(h.root, "01", executable=sys.executable,
                                        timeout=45)
            self.assertEqual(preview["status"], "dry-run")
            self.assertFalse((Path(h.a)/"gui-dispatch").exists())
            output = gui_bridge.bridge(
                h.root, "01", execute=True, approval="01",
                executable=sys.executable, timeout=45)
            self.assertEqual(output["status"], "ready-for-review", output)
            self.assertTrue(output["model_invoked"])
            self.assertFalse(output["accepted"])
            self.assertTrue(output["worker_commit"])
            again = gui_bridge.bridge(
                h.root, "01", execute=True, approval="01",
                executable=sys.executable, timeout=45)
            self.assertEqual(again["status"], "blocked")
        receipt = gui_bridge.receipt_status(h.root, "01")
        self.assertEqual(receipt["approved"]["model"], "gpt-6-luna")
        self.assertEqual(receipt["approved"]["effort"], "low")
        self.assertTrue(receipt["usage_recorded"])
        self.assertEqual(receipt["usage"]["input_tokens"], 130)
        ledger = h.state()
        self.assertEqual(len(ledger["usageEvents"]), 1)
        self.assertEqual(ledger["usageEvents"][0]["input"], 130)
        self.assertEqual(ledger["usageEvents"][0]["output"], 40)
        self.assertEqual(ledger["usageEvents"][0]["source"], "codex-jsonl")

        # Controller may NOT accept the worker commit until independent
        # baseline-tracked tests have actually run in the worktree.
        code, blocked = self.controller()
        self.assertNotEqual(code, 0)
        self.assertEqual(blocked["next"]["reason"], "trusted-suite-required")
        for action in ("verify", "land", "accept", "release"):
            code, out = self.controller("--suite", "test_core.py", "--advance")
            self.assertEqual(code, 0, (action, out))
            self.assertEqual(out["completed"]["action"], action, out)
            self.assertFalse(out["model_invoked"])
        ticket = h.state()["tickets"][0]
        self.assertEqual(ticket["status"], "done")
        self.assertEqual(ticket["worktree"]["status"], "released")
        self.assertEqual(
            (Path(h.root)/"src"/"core"/"calc.py").read_text(encoding="utf-8"),
            "def add(a, b):\n    return a + b\n")
        self.assertTrue(ticket["testEvidence"]["status"] == "verified")
        self.assertFalse(h.git("status", "--porcelain", "--", "src").stdout.strip())


    def test_actual_os_process_error_preserves_non_replayable_receipt(self):
        h = self.harness
        for action in ("prepare", "start"):
            code, out = self.controller("--advance")
            self.assertEqual(code, 0, out)
            self.assertEqual(out["completed"]["action"], action)
        self.fake.write_text("import sys; sys.stdin.read(); sys.exit(17)\\n",
                             encoding="utf-8")
        real_checked = codex_dispatch.checked_dispatch
        def offline_error(*args, **kwargs):
            conf = real_checked(*args, **kwargs)
            conf["command"] = [sys.executable, str(self.fake),
                               "--cd", conf["cwd"]]
            return conf
        with patch.object(codex_dispatch, "checked_dispatch", offline_error):
            out = gui_bridge.bridge(h.root, "01", execute=True, approval="01",
                                    executable=sys.executable, timeout=45)
            self.assertEqual(out["status"], "failed")
            self.assertEqual(out["model_invoked"], "unknown")
            again = gui_bridge.bridge(h.root, "01", execute=True, approval="01",
                                      executable=sys.executable, timeout=45)
            self.assertEqual(again["status"], "blocked")
        self.assertEqual(h.state()["tickets"][0]["status"], "in-progress")
        self.assertEqual(h.state()["usageEvents"], [])
        self.assertEqual(gui_bridge.receipt_status(h.root, "01")["status"], "failed")


if __name__ == "__main__":
    unittest.main()
