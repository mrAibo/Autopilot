"""No paid provider calls: fail-closed entry points and token-ledger audit."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                        "skills" / "autopilot" / "tools"))
import codex_dispatch
import gui_bridge
import spend_guard
import test_gui_bridge


class SpendGuardTests(unittest.TestCase):
    def setUp(self):
        # Reuse exact pinned-route synthetic project without running its tests.
        f = test_gui_bridge.BridgeTests("test_dry_run_does_not_create_receipts_or_pay")
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.f = f

    def test_bridge_denies_before_receipt_or_any_paid_function(self):
        with patch.object(codex_dispatch, "run_once") as model:
            with self.assertRaisesRegex(spend_guard.CapUnavailable,
                                        "no-verifiable-provider"):
                gui_bridge.bridge(self.f.root, "01", execute=True,
                                  approval="01", executable=Path(sys.executable),
                                  timeout=45)
        model.assert_not_called()
        self.assertFalse((self.f.root / ".autopilot" / "gui-dispatch").exists())
        # controller.lock is a persistent OS lock inode by design; its
        # existence does not signal an active dispatch or billable call.
        preview = gui_bridge.bridge(self.f.root, "01",
                                    executable=Path(sys.executable), timeout=45)
        self.assertEqual(preview["status"], "dry-run")
        self.assertFalse(preview["execution_permitted"])
        self.assertEqual(preview["budget_block_reason"], spend_guard.CAP_REASON)

    def test_lowest_level_run_once_denies_before_lock_or_external_subprocess(self):
        cfg = codex_dispatch.checked_dispatch(
            self.f.root, "01", executable=Path(sys.executable))
        with patch.object(codex_dispatch.subprocess, "run") as external:
            with self.assertRaises(spend_guard.CapUnavailable):
                codex_dispatch.run_once(cfg, self.f.root, timeout=45)
        external.assert_not_called()
        self.assertFalse((self.f.root / ".autopilot" / "dispatch-01.lock").exists())

    def test_direct_cli_execute_denied_even_with_positive_threshold(self):
        from io import StringIO
        from contextlib import redirect_stdout
        cfg = ["01", "--root", str(self.f.root),
               "--codex-exe", sys.executable, "--execute", "--timeout", "45"]
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = codex_dispatch.main(cfg)
        self.assertEqual(exit_code, 2)
        self.assertEqual(json.loads(buffer.getvalue())["status"], "blocked")
        self.assertFalse((self.f.root / ".autopilot" / "dispatch-01.lock").exists())

    def test_audit_reports_actual_counts_and_soft_budget_overage(self):
        self.f.state["budgetTokens"] = 2000
        self.f.state["usageEvents"] = [{
            "ticket": "01", "source": "codex-jsonl",
            "input": 53187, "output": 341, "cacheRead": 46464}]
        self.f.save()
        audit = spend_guard.usage_summary(self.f.root, "01")
        self.assertEqual(audit["recorded_total_tokens"], 53528)
        self.assertEqual(audit["recorded_overage_tokens"], 51528)
        self.assertEqual(audit["recorded_cached_input_tokens"], 46464)
        self.assertTrue(audit["recorded_threshold_exceeded"])
        self.assertFalse(audit["execution_permitted"])
        self.assertIsNone(audit["cost_amount"])
        self.assertFalse(audit["existing_receipt"])
        self.assertFalse((self.f.root / ".autopilot" / "gui-dispatch").exists())

    def test_audit_reads_existing_receipt_without_mutation(self):
        d = self.f.root / ".autopilot" / "gui-dispatch"
        d.mkdir()
        receipt = d / "01.json"
        receipt.write_text(json.dumps({"ticket": "01", "status": "incomplete",
                                       "turn_completed": True,
                                       "worker_commit": None,
                                       "usage_recorded": True}), encoding="utf-8")
        before = receipt.read_bytes()
        result = spend_guard.usage_summary(self.f.root, "01")
        self.assertTrue(result["existing_receipt"])
        self.assertEqual(result["receipt_status"], "incomplete")
        self.assertTrue(result["turn_completed"])
        self.assertFalse(result["worker_commit"])
        self.assertEqual(before, receipt.read_bytes())

    def test_unknown_or_corrupt_ledger_fails_closed(self):
        for bad in (True, "1", -1):
            self.f.state["usageEvents"] = [{"input": bad, "output": 1}]
            self.f.save()
            with self.assertRaises(ValueError):
                spend_guard.usage_summary(self.f.root, "01")
        self.f.state["usageEvents"] = [{"input": 1, "output": 1, "cacheRead": 2}]
        self.f.save()
        with self.assertRaisesRegex(ValueError, "Cached input"):
            spend_guard.usage_summary(self.f.root, "01")

    def test_no_config_file_or_argument_can_enable_an_unverified_hard_cap(self):
        (self.f.root / ".autopilot" / "hard-cap-approved.json").write_text(
            '{"provider_hard_cap_verified":true, "limit":1}', encoding="utf-8")
        for config in (None, {}, {"provider_hard_cap_verified": True,
                                  "max_tokens": 1, "env_override": True}):
            with self.assertRaises(spend_guard.CapUnavailable):
                spend_guard.assert_enforced_cap(config)
        self.assertFalse((self.f.root / ".autopilot" / "gui-dispatch").exists())


if __name__ == "__main__":
    unittest.main()
