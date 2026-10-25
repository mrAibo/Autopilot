"""No paid calls: one-shot GUI to pinned CLI bridge with durable anti-replay."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import codex_dispatch
import gui_bridge
import test_codex_dispatch as dispatch_fixture


class BridgeTests(unittest.TestCase):
    """Reuse fixture helpers without re-running the dispatch suite twice."""
    git = dispatch_fixture.DispatchTests.git
    save = dispatch_fixture.DispatchTests.save

    def setUp(self):
        dispatch_fixture.DispatchTests.setUp(self)
        self.state["tickets"][0]["zone"] = ["README.md"]
        self.state["budgetTokens"] = 20000
        self.save()

    def preview(self):
        return gui_bridge.bridge(self.root, "01", executable=Path(sys.executable),
                                 timeout=60)

    def execute(self, **extra):
        # Synthetic-only test permits mock run_once: production guard remains
        # unconditional, with no user/environment bypass.
        with patch.object(gui_bridge.spend_guard, "assert_enforced_cap"):
            return gui_bridge.bridge(self.root, "01", execute=True, approval="01",
                                     executable=Path(sys.executable), timeout=60, **extra)

    def test_dry_run_does_not_create_receipts_or_pay(self):
        with patch.object(codex_dispatch, "run_once") as paid:
            result = self.preview()
        self.assertEqual(result["status"], "dry-run")
        self.assertEqual(result["preview"]["model"], "gpt-6-luna")
        self.assertEqual(result["preview"]["effort"], "low")
        self.assertEqual(result["preview"]["recorded_remaining_tokens"], 20000)
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())
        self.assertFalse((self.root / ".autopilot" / "controller.lock").exists())
        paid.assert_not_called()

    def test_requires_exact_matching_paid_approval(self):
        with self.assertRaisesRegex(gui_bridge.BridgeError, "needs --approve-ticket"):
            gui_bridge.bridge(self.root, "01", execute=True,
                              executable=Path(sys.executable))
        with self.assertRaises(gui_bridge.BridgeError):
            gui_bridge.bridge(self.root, "01", execute=True, approval="02",
                              executable=Path(sys.executable))
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())

    def test_one_paid_call_receipt_and_no_automatic_acceptance(self):
        reply = {"status": "ready-for-review", "worker_commit": "abcdef1234",
                 "turn_completed": True, "usage_recorded": True,
                 "usage": {"input_tokens": 100, "cached_input_tokens": 10,
                           "output_tokens": 15}}
        with patch.object(codex_dispatch, "run_once", return_value=reply) as runner:
            result = self.execute()
        self.assertEqual(result["status"], "ready-for-review")
        self.assertFalse(result["accepted"])
        self.assertFalse(result["tests_verified"])
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(runner.call_args.kwargs["timeout"], 60)
        saved = gui_bridge.receipt_status(self.root, "01")
        self.assertEqual(saved["worker_commit"], "abcdef1234")
        self.assertEqual(saved["approved"]["ticket"], "01")
        self.assertEqual(saved["approved"]["model"], "gpt-6-luna")
        self.assertEqual(saved["approved"]["effort"], "low")
        self.assertNotIn("prompt", str(saved).lower())

    def test_one_shot_duplicate_blocks_before_model_call(self):
        with patch.object(codex_dispatch, "run_once",
                          return_value={"status": "incomplete"}) as runner:
            self.assertEqual(self.execute()["status"], "incomplete")
            self.assertEqual(self.execute()["status"], "blocked")
            self.assertEqual(runner.call_count, 1)
        self.assertEqual(self.preview()["status"], "blocked")

    def test_process_crash_or_timeout_cannot_replay(self):
        with patch.object(codex_dispatch, "run_once",
                          side_effect=TimeoutError("provider may have billed")) as runner:
            first = self.execute()
            second = self.execute()
            self.assertEqual(first["status"], "invocation-uncertain")
            self.assertEqual(second["status"], "blocked")
            self.assertEqual(runner.call_count, 1)
        receipt = gui_bridge.receipt_status(self.root, "01")
        self.assertEqual(receipt["model_invoked"], "unknown")

    def test_orphaned_claim_prevents_reexecution(self):
        config, summary = gui_bridge.consent_preflight(
            self.root, "01", Path(sys.executable), timeout=60)
        path, record = gui_bridge.claim_attempt(self.root, "01", config, summary)
        self.assertEqual(record["status"], "invocation-uncertain")
        self.assertTrue(path.exists())
        with patch.object(codex_dispatch, "run_once") as paid:
            self.assertEqual(self.execute()["status"], "blocked")
            paid.assert_not_called()

    def test_unset_or_exhausted_token_budget_blocks(self):
        self.state["budgetTokens"] = None
        self.save()
        with self.assertRaisesRegex(gui_bridge.BridgeError, "positive recorded token"):
            self.preview()
        self.state["budgetTokens"] = 20000
        self.state["usageEvents"] = [{"input": 19999, "output": 1}]
        self.save()
        with self.assertRaises(gui_bridge.BridgeError):
            self.preview()

    def test_refuse_unknown_spend_and_dirty_worktree(self):
        self.state["usageEvents"] = [{"input": "oops", "output": 6}]
        self.save()
        with self.assertRaises(gui_bridge.BridgeError):
            self.preview()
        self.state["usageEvents"] = []
        self.save()
        (Path(self.state["tickets"][0]["worktree"]["cwd"]) / "rogue.md").write_text(
            "bad", encoding="utf-8")
        with self.assertRaises(gui_bridge.BridgeError):
            self.preview()

    def test_damaged_receipt_blocks_all_retries(self):
        dir_ = gui_bridge.receipt_dir(self.root)
        (dir_ / "01.json").write_text("partial", encoding="utf-8")
        with self.assertRaises(gui_bridge.BridgeError):
            self.execute()

    def test_route_edit_blocks_before_claim(self):
        self.state["tickets"][0]["routing"]["model"] = "gpt-6-sol"
        self.save()
        with patch.object(codex_dispatch, "run_once") as run:
            with self.assertRaises(codex_dispatch.DispatchError):
                self.execute()
            run.assert_not_called()
        self.assertIsNone(gui_bridge.receipt_status(self.root, "01"))

    def test_unrelated_active_ticket_disallows_spend(self):
        other = {**self.state["tickets"][0], "id": "02"}
        self.state["tickets"].append(other)
        self.save()
        with self.assertRaises(gui_bridge.BridgeError):
            self.preview()

    def test_pending_or_already_changed_ticket_disallowed(self):
        self.state["tickets"][0]["status"] = "pending"
        self.save()
        with self.assertRaises(gui_bridge.BridgeError):
            self.preview()

    def test_receipt_never_stores_prompt_or_ticket_brief(self):
        with patch.object(codex_dispatch, "run_once", return_value={
              "status": "failed", "usage_recorded": False}) as paid:
            self.execute()
        value=(self.root / ".autopilot/gui-dispatch/01.json").read_text(encoding="utf-8")
        self.assertNotIn("Update README safely", value)
        self.assertNotIn("developer_instructions", value)
        paid.assert_called_once()

    def test_runtime_doctor_uses_binary_and_current_catalog_read_only(self):
        import subprocess
        real_run = subprocess.run
        expected = {"gpt-6-luna": ["low", "medium"]}
        def inspect(command, *args, **kwargs):
            if (len(command) == 2 and command[1] == "--version"
                    and Path(command[0]).resolve() == Path(sys.executable).resolve()):
                return subprocess.CompletedProcess(command, 0, "codex-cli 0.165.0\n", "")
            if (len(command) == 3 and command[1:] == ["exec", "--help"]
                    and Path(command[0]).resolve() == Path(sys.executable).resolve()):
                return subprocess.CompletedProcess(
                    command, 0,
                    "--model --cd --sandbox --ephemeral --ignore-user-config --json", "")
            return real_run(command, *args, **kwargs)
        with patch.object(gui_bridge.codex_capabilities, "discover",
                          return_value=expected) as query, \
                patch.object(gui_bridge.subprocess, "run",
                             side_effect=inspect):
            result = gui_bridge.runtime_doctor(self.root, "01",
                                               executable=sys.executable, timeout=60)
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["model_invoked"])
        self.assertFalse(result["verified_provider_execution"])
        self.assertFalse(result["provider_budget_hard_cap"])
        self.assertTrue(result["current_catalog_model_effort"])
        query.assert_called_once()
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())
        self.assertFalse((self.root / ".autopilot" / "controller.lock").exists())

    def test_runtime_doctor_rejects_stale_catalog_without_attempt_receipt(self):
        with patch.object(gui_bridge.codex_capabilities, "discover",
                          return_value={"gpt-6-luna": ["medium"]}):
            with self.assertRaisesRegex(gui_bridge.BridgeError, "CURRENT"):
                gui_bridge.runtime_doctor(self.root, "01",
                                          executable=sys.executable, timeout=60)
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())

    def test_runtime_doctor_rejects_unknown_binary_without_attempt_receipt(self):
        import subprocess
        real_run = subprocess.run
        def inspect(command, *args, **kwargs):
            if (len(command) == 2 and command[1] == "--version"
                    and Path(command[0]).resolve() == Path(sys.executable).resolve()):
                return subprocess.CompletedProcess(command, 0, "unknown-binary\n", "")
            return real_run(command, *args, **kwargs)
        with patch.object(gui_bridge.codex_capabilities, "discover",
                          return_value={"gpt-6-luna": ["low"]}), \
                patch.object(gui_bridge.subprocess, "run",
                             side_effect=inspect):
            with self.assertRaisesRegex(gui_bridge.BridgeError, "recognized Codex CLI"):
                gui_bridge.runtime_doctor(self.root, "01",
                                          executable=sys.executable, timeout=60)
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())

    def test_runtime_doctor_cli_refuses_execute_together(self):
        from io import StringIO
        from contextlib import redirect_stdout
        buf = StringIO()
        args = ["--root", str(self.root), "--ticket", "01", "--check-runtime",
                "--execute", "--approve-ticket", "01"]
        with redirect_stdout(buf):
            result = gui_bridge.main(args)
        self.assertEqual(result, 2)
        self.assertEqual(json.loads(buf.getvalue())["status"], "blocked")
        self.assertFalse((self.root / ".autopilot" / "gui-dispatch").exists())

    def test_cli_dry_run_and_protected_execute(self):
        with patch.object(sys, "argv", ["gui_bridge.py", "--root", str(self.root),
                                        "--ticket", "01", "--codex-exe",
                                        sys.executable, "--timeout", "60"]):
            # Capture JSON without actual provider call.
            from io import StringIO
            from contextlib import redirect_stdout
            buf = StringIO()
            with redirect_stdout(buf):
                rc = gui_bridge.main()
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(buf.getvalue())["status"], "dry-run")


if __name__ == "__main__":
    unittest.main()
