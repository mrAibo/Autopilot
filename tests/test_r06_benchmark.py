"""R06 metrology contract: honest synthetic-only observations and paired order."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "offline_r06", ROOT / "tools" / "benchmark-r06.py")
r06 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r06)


class R06BenchmarkContract(unittest.TestCase):
    def test_prompt_delta_is_bytes_not_claimed_tokens(self):
        data = r06.prompt_proxy(ROOT)
        self.assertEqual(data["off_utf8_bytes"], 0)
        self.assertGreater(data["incremental_utf8_bytes"], 0)
        self.assertEqual(data["lean_utf8_bytes"], data["incremental_utf8_bytes"])
        self.assertIsNone(data["measured_provider_tokens"])
        self.assertIsNone(data["measured_provider_cost"])

    def test_fixed_fixture_is_source_and_model_independent(self):
        self.assertIn("R01", r06.MANIFEST)
        self.assertIn("R02", r06.MANIFEST)
        text = r06.task("01", "Safe", "R01", "—", ["src/core/"], 1)
        self.assertIn("**Зона:** `src/core/`", text)
        self.assertIn("**Требования:** R01", text)
        self.assertNotIn("sk-", text)

    def test_repetition_validation_before_any_git_or_model(self):
        with patch.object(r06, "git") as tool:
            with self.assertRaisesRegex(r06.BenchmarkError, "Repeat count"):
                r06.benchmark(ROOT, 0)
            with self.assertRaisesRegex(r06.BenchmarkError, "Repeat count"):
                r06.benchmark(ROOT, 6)
            tool.assert_not_called()

    def test_matched_order_reverses_on_second_iteration(self):
        calls = []
        def fake_git(repo, *args, **kwargs):
            return type("R", (), {"stdout": "" if args[0] == "status" else "a" * 40 + "\n"})()
        def fake_snapshot(repo, revision, dest):
            return "2.2" if revision == r06.BASELINE else "2.3-dev"
        def fake_run(skill, scenario):
            calls.append((skill, scenario))
            good = scenario != "empty-finish"
            return {"elapsed_ms": 100.0 if skill == "2.2" else 110.0,
                    "correct_gate_behavior": good or skill == "2.3-dev",
                    "accepted": good or skill == "2.2",
                    "ap_commands": 12 if good else 2, "git_commits": 3 if good else 0}
        with patch.object(r06, "git", fake_git), \
             patch.object(r06, "snapshot", fake_snapshot), \
             patch.object(r06, "run_fixture", fake_run), \
             patch.object(r06, "prompt_proxy", return_value={"measured_provider_tokens": None}):
            data = r06.benchmark(ROOT, repetitions=2)
        self.assertEqual(calls, [
            ("2.2","empty-finish"), ("2.3-dev","empty-finish"),
            ("2.2","valid-two-tickets"), ("2.3-dev","valid-two-tickets"),
            ("2.3-dev","empty-finish"), ("2.2","empty-finish"),
            ("2.3-dev","valid-two-tickets"), ("2.2","valid-two-tickets")])
        self.assertEqual(data["summary"]["empty-finish"]["2.2"]["correct"], 0)
        self.assertEqual(data["summary"]["empty-finish"]["2.3-dev"]["correct"], 2)
        self.assertIsNone(data["actual_cost"])
        self.assertIsNone(data["actual_input_tokens"])
        self.assertEqual(data["live_executor_count"], 0)

    def test_snapshot_failure_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(r06.subprocess, "run", return_value=type(
                "Result", (), {"returncode": 1, "stderr": b"missing"})()):
                with self.assertRaisesRegex(r06.BenchmarkError, "historical"):
                    r06.snapshot(Path(tmp), r06.BASELINE, Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
