"""Codex dispatch integration contract, no paid model calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(SKILL))
import codex_dispatch
import worktrees


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Autopilot CI")
        (self.root / ".gitignore").write_text(
            ".autopilot/worktrees/\n.codex/agents/autopilot-*.toml\n", encoding="utf-8")
        (self.root / "README.md").write_text("Synthetic, no secrets.\n", encoding="utf-8")
        self.git("add", ".gitignore", "README.md")
        self.git("commit", "-qm", "bootstrap")
        a = self.root / ".autopilot"
        ticketdir = a / "test-run" / "tickets"
        ticketdir.mkdir(parents=True)
        ticket = ticketdir / "01-hello.md"
        ticket.write_text("# T01 — docs\nUpdate README safely.", encoding="utf-8")
        profile = self.root / ".codex" / "agents" / "autopilot-executor-01-hello.toml"
        profile.parent.mkdir(parents=True)
        profile.write_text(
            'name = "autopilot-executor-01-hello"\n'
            'description = "Test"\n'
            'model = "gpt-6-luna"\n'
            'model_reasoning_effort = "low"\n'
            'developer_instructions = "Do exactly one task."\n', encoding="utf-8")
        (a / "model-capabilities.json").write_text(
            json.dumps({"provider": "openai", "model_selection": True,
                        "models": {"gpt-6-luna": ["low"]}}), encoding="utf-8")
        wt = worktrees.create(self.root, "01")
        self.state = {"dir": "test-run", "finishedAt": None,
                      "strictRouting": True, "isolateTickets": True,
                      "usageEvents": [], "budgetTokens": None,
                      "tickets": [{
                          "id": "01", "status": "in-progress",
                          "fingerprint": hashlib.sha256(ticket.read_bytes()).hexdigest(),
                          "routing": {
                              "provider": "openai", "verified": True,
                              "model": "gpt-6-luna", "effort": "low",
                              "agentType": "autopilot-executor-01-hello",
                              "agentFile": ".codex/agents/autopilot-executor-01-hello.toml",
                              "profileSha": hashlib.sha256(profile.read_bytes()).hexdigest()},
                          "worktree": {"status": "prepared",
                                       "cwd": wt["cwd"],
                                       "baseCommit": wt["baseCommit"]}
                      }]}
        self.save()

    def git(self, *args):
        r = subprocess.run(["git", "-C", str(self.root), *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)

    def save(self):
        (self.root / ".autopilot" / "state.js").write_text(
            "window.STATE =\n" + json.dumps(self.state), encoding="utf-8")

    def checked(self):
        return codex_dispatch.checked_dispatch(
            self.root, "01", executable=Path(sys.executable))

    def test_pins_model_effort_cwd_and_sandbox(self):
        cfg = self.checked()
        self.assertEqual(cfg["model"], "gpt-6-luna")
        self.assertEqual(cfg["effort"], "low")
        self.assertIn("--ephemeral", cfg["command"])
        self.assertIn("--ignore-user-config", cfg["command"])
        self.assertIn("workspace-write", cfg["command"])
        self.assertEqual(Path(cfg["cwd"]), Path(self.state["tickets"][0]["worktree"]["cwd"]))
        self.assertIn("Update README safely", cfg["prompt"])

    def test_refuses_profile_tampering(self):
        profile = self.root / self.state["tickets"][0]["routing"]["agentFile"]
        profile.write_text(profile.read_text() + "# modified", encoding="utf-8")
        with self.assertRaisesRegex(codex_dispatch.DispatchError, "edited"):
            self.checked()

    def test_refuses_different_provider_or_finished_run(self):
        self.state["tickets"][0]["routing"]["provider"] = "anthropic"
        self.save()
        with self.assertRaises(codex_dispatch.DispatchError):
            self.checked()
        self.state["tickets"][0]["routing"]["provider"] = "openai"
        self.state["finishedAt"] = "completed"
        self.save()
        with self.assertRaises(codex_dispatch.DispatchError):
            self.checked()

    def test_refuses_dirty_worktree(self):
        (Path(self.state["tickets"][0]["worktree"]["cwd"]) / "rogue.txt").write_text("edit")
        with self.assertRaisesRegex(codex_dispatch.DispatchError, "changed"):
            self.checked()

    def test_refuses_token_threshold(self):
        self.state["budgetTokens"] = 150
        self.state["usageEvents"] = [{"input": 100, "output": 50}]
        self.save()
        with self.assertRaisesRegex(codex_dispatch.DispatchError, "threshold"):
            self.checked()

    def test_refuses_unpublished_ticket_change(self):
        ticket = self.root / ".autopilot" / "test-run" / "tickets" / "01-hello.md"
        ticket.write_text("Changed ticket instructions", encoding="utf-8")
        with self.assertRaisesRegex(codex_dispatch.DispatchError, "changed"):
            self.checked()

    def test_jsonl_token_report_is_bounded_and_accurate(self):
        output = ('{"type":"thread.started","thread_id":"0199a213-81c0-7800-8aa1-bbab2a035a53"}\n'
                  '{"type":"turn.completed","usage":{"input_tokens":70,"output_tokens":12,"cached_input_tokens":15}}\n')
        ident, counts, finished = codex_dispatch.parse_usage(output)
        self.assertTrue(finished)
        self.assertEqual(counts["input_tokens"], 70)
        self.assertEqual(counts["cached_input_tokens"], 15)
        self.assertTrue(ident)
        self.assertIsNone(codex_dispatch.parse_usage("not JSON")[1])

    def test_single_flight_blocks_duplicate_model_invocation(self):
        lock = self.root / ".autopilot" / "dispatch-01.lock"
        with codex_dispatch.single_flight(self.root, "01"):
            self.assertTrue(lock.is_file())
            with self.assertRaisesRegex(codex_dispatch.DispatchError, "Existing dispatch lock"):
                with codex_dispatch.single_flight(self.root, "01"):
                    pass
        self.assertFalse(lock.exists())

    def test_single_flight_releases_after_exception(self):
        lock = self.root / ".autopilot" / "dispatch-01.lock"
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            with codex_dispatch.single_flight(self.root, "01"):
                raise RuntimeError("simulated")
        self.assertFalse(lock.exists())

    def test_lean_rules_are_explicit_and_never_skip_tests(self):
        cfg = codex_dispatch.checked_dispatch(self.root, "01",
                                                executable=Path(sys.executable),
                                                optimization="lean")
        self.assertEqual(cfg["optimization"], "lean")
        self.assertIn("standard library", cfg["prompt"])
        self.assertIn("Do not skip tests", cfg["prompt"])
        self.assertNotIn("standard library", self.checked()["prompt"])
        with self.assertRaises(codex_dispatch.DispatchError):
            codex_dispatch.checked_dispatch(self.root, "01",
                                             executable=Path(sys.executable),
                                             optimization="unknown")

    def test_windows_sandbox_backend_has_no_full_access_mode(self):
        cfg = self.checked()
        if os.name == "nt":
            self.assertIn('windows.sandbox="elevated"', cfg["command"])
        self.assertNotIn("danger-full-access", cfg["command"])

    def test_execution_reports_usage(self):
        cfg = self.checked()
        with patch.object(codex_dispatch, "verify_worker_commit", return_value=(None, "No commit")), \
                patch.object(codex_dispatch.spend_guard, "assert_enforced_cap"), \
                patch.object(codex_dispatch.subprocess, "run") as mock:
            mock.side_effect = [
                subprocess.CompletedProcess([], 0,
                    '{"type":"thread.started","thread_id":"0199a213-81c0-7800-8aa1-bbab2a035a53"}\n'
                    '{"type":"turn.completed","usage":{"input_tokens":90,"output_tokens":3,"cached_input_tokens":40}}\n',
                    ""),
                subprocess.CompletedProcess([], 0, "", "")
            ]
            result = codex_dispatch.run_once(cfg, self.root, timeout=90)
        # The model turn succeeded, but did not create a worker commit.
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["turn_completed"])
        self.assertFalse(result["accepted"])
        self.assertIsNone(result["worker_commit"])
        self.assertTrue(result["usage_recorded"])
        self.assertEqual(mock.call_count, 2)
        self.assertIn("--sandbox", mock.call_args_list[0].args[0])
        self.assertIn("--source", mock.call_args_list[1].args[0])

    def test_invalid_native_binary_path_is_rejected(self):
        with self.assertRaises(codex_dispatch.DispatchError):
            codex_dispatch.checked_dispatch(
                self.root, "01", executable=self.root / "nonexistent.exe")


if __name__ == "__main__":
    unittest.main()
