"""Offline host-loop checks: no AI launch, real two-ticket Git acceptance."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                        "skills" / "autopilot" / "tools"))
import host_loop
import test_ap


class LoopUnitTests(unittest.TestCase):
    def test_only_unique_explicit_test_suites(self):
        self.assertEqual(host_loop.parse_suites(["01=test_a.py", "02=test_b.py"]),
                         {"01": "test_a.py", "02": "test_b.py"})
        for args in (["bogus"], ["01="], ["x=t.py"], ["01=a", "01=b"],
                     ["12345=t.py"], ["01=x\x00.py"]):
            with self.subTest(args=args), self.assertRaises(ValueError):
                host_loop.parse_suites(args)

    def test_invalid_step_limit_denied(self):
        for value in (0, 33, 1.5, True, -2):
            with self.subTest(value=value), self.assertRaises(ValueError):
                host_loop.loop(".", max_steps=value)

    @patch.object(host_loop.controller, "advance")
    def test_read_only_preview_never_advances(self, advance):
        advance.return_value = {"status": "dry-run",
                                "next": {"action": "prepare", "ticket": "01"}}
        result = host_loop.loop(".", {"01": "test_a.py"})
        self.assertEqual(result["status"], "dry-run")
        self.assertEqual(result["completed"], [])
        self.assertFalse(result["model_invoked"])
        advance.assert_called_once()
        self.assertEqual(advance.call_args.kwargs["execute"], False)

    @patch.object(host_loop.controller, "advance")
    def test_bounded_loop_stops_without_model_launch(self, advance):
        steps = [{"action": "prepare", "ticket": "01"},
                 {"action": "start", "ticket": "01"}]
        order = iter([
            {"status": "dry-run", "next": steps[0]},
            {"status": "advanced", "completed": steps[0],
             "next": steps[1]},
            {"status": "dry-run", "next": steps[1]},
            {"status": "advanced", "completed": steps[1],
             "next": {"action": "blocked", "ticket": "01",
                      "reason": host_loop.AWAIT_WORKER}},
            {"status": "blocked", "next": {"action": "blocked", "ticket": "01",
                                         "reason": host_loop.AWAIT_WORKER}},
        ])
        advance.side_effect = lambda *a, **k: next(order)
        result = host_loop.loop(".", execute=True, max_steps=8)
        self.assertEqual(result["status"], "paused")
        self.assertEqual(result["completed"], steps)
        self.assertFalse(result["model_invoked"])
        self.assertEqual(advance.call_count, 5)

    @patch.object(host_loop.controller, "advance")
    def test_failure_does_not_retry(self, advance):
        action = {"action": "verify", "ticket": "01", "suite": "test_a.py"}
        advance.side_effect = [
            {"status": "dry-run", "next": action},
            {"status": "blocked", "next": action,
             "reason": "host-transition-failed-inspect-ledger"}
        ]
        result = host_loop.loop(".", {"01": "test_a.py"}, execute=True)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["completed"], [])
        self.assertEqual(advance.call_count, 2)

    @patch.object(host_loop.controller, "advance")
    def test_concurrent_state_shift_stops_even_after_one_transition(self, advance):
        action = {"action": "prepare", "ticket": "01"}
        other = {"action": "start", "ticket": "02"}
        advance.side_effect = [
            {"status": "dry-run", "next": action},
            {"status": "advanced", "completed": other, "next": action}
        ]
        result = host_loop.loop(".", execute=True)
        self.assertEqual(result["reason"], "concurrent-state-shift")
        self.assertEqual(result["completed"], [other])
        self.assertEqual(advance.call_count, 2)


class LoopRealGitTests(unittest.TestCase):
    def setUp(self):
        self.h = test_ap.Run("test_init_creates_run")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)
        h = self.h
        h.plan(strict=True, isolated=True)
        self.assertEqual(h.ap("tickets")[0], 0)
        capabilities = Path(h.a) / "model-capabilities.json"
        capabilities.write_text(json.dumps({
            "provider": "anthropic", "model_selection": True,
            "models": {"haiku": ["low"]}
        }), encoding="utf-8")
        for tid in ("01", "02"):
            rc, output = h.ap("ticket", tid, "route", "--provider", "anthropic",
                              "--model", "haiku", "--effort", "low",
                              "--reason", "offline-worktree-test",
                              "--capabilities", str(capabilities))
            self.assertEqual(rc, 0, output)
        h.attest_routes()
        h.git("config", "user.email", "test@example.invalid")
        h.git("config", "user.name", "Autopilot Offline Host Loop")
        for folder, source, fn, broken, expected in (
            ("core", "add", "add", "a - b", "a + b"),
            ("bot", "mul", "mul", "a + b", "a * b")
        ):
            dest = Path(h.root) / "src" / folder
            dest.mkdir(parents=True)
            (dest / "calc.py").write_text(
                f"def {fn}(a, b):\n    return {broken}\n", encoding="utf-8")
            (Path(h.root) / f"test_{folder}.py").write_text(
                "import unittest\n" +
                f"from src.{folder}.calc import {fn}\n" +
                f"class Tests(unittest.TestCase):\n" +
                f" def test_result(self): self.assertEqual({fn}(2, 3), " +
                ("5" if folder == "core" else "6") + ")\n",
                encoding="utf-8")
        h.git("add", "src", "test_core.py", "test_bot.py", ".gitignore")
        h.commit("trusted baseline with deliberately broken implementation")
        shutil.copy(host_loop.__file__, Path(h.a) / "host_loop.py")

    def invoke(self, *args):
        h = self.h
        p = subprocess.run(
            [sys.executable, str(Path(h.a) / "host_loop.py"),
             "--root", h.root, *args], cwd=h.root,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=90)
        self.assertTrue(p.stdout.strip(), p.stderr)
        return p.returncode, json.loads(p.stdout)

    def edit(self, tid, folder, expression):
        ticket = next(t for t in self.h.state()["tickets"] if t["id"] == tid)
        path = Path(ticket["worktree"]["cwd"]) / "src" / folder / "calc.py"
        fn = "add" if folder == "core" else "mul"
        path.write_text(f"def {fn}(a, b):\n    return {expression}\n",
                        encoding="utf-8")

    def test_two_tickets_failed_suite_then_recovery_without_ai(self):
        h = self.h
        code, preview = self.invoke()
        self.assertEqual(code, 0, preview)
        self.assertEqual(preview["next"]["action"], "prepare")
        self.assertFalse((Path(h.a) / "controller.lock").exists())

        code, first = self.invoke("--advance")
        self.assertEqual(code, 0, first)
        self.assertEqual([s["action"] for s in first["completed"]],
                         ["prepare", "start"])
        self.assertEqual(first["status"], "paused")
        self.assertEqual(first["next"]["reason"], host_loop.AWAIT_WORKER)
        self.assertEqual(h.state()["tickets"][0]["status"], "in-progress")

        # Simulated manual edit in an isolated disposable worker, no model call.
        self.edit("01", "core", "a + b")
        code, result = self.invoke("--advance", "--suite", "01=test_core.py")
        self.assertEqual(code, 0, result)
        self.assertEqual([s["action"] for s in result["completed"]],
                         ["verify", "finalize", "land", "accept", "release",
                          "prepare", "start"])
        self.assertEqual(result["status"], "paused")
        self.assertEqual(h.state()["tickets"][0]["status"], "done")

        self.edit("02", "bot", "a - b")
        code, failed = self.invoke("--advance", "--suite", "02=test_bot.py")
        self.assertEqual(code, 2, failed)
        self.assertEqual(failed["status"], "blocked")
        self.assertEqual(failed["completed"], [])
        self.assertEqual(h.state()["tickets"][1]["status"], "in-progress")
        self.assertFalse(h.state()["tickets"][1].get("testEvidence"))

        self.edit("02", "bot", "a * b")
        code, recovered = self.invoke("--advance", "--suite", "02=test_bot.py")
        self.assertEqual(code, 0, recovered)
        self.assertEqual(recovered["status"], "tickets-settled")
        self.assertEqual([s["action"] for s in recovered["completed"]],
                         ["verify", "finalize", "land", "accept", "release"])
        self.assertTrue(all(t["status"] == "done" for t in h.state()["tickets"]))
        self.assertTrue(all(t["worktree"]["status"] == "released"
                            for t in h.state()["tickets"]))
        self.assertFalse(h.state()["usageEvents"])
        self.assertFalse(h.git("status", "--porcelain", "--", "src").stdout.strip())


if __name__ == "__main__":
    unittest.main()
