"""Claude attestation hook tests (no Claude subscription or process required)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import claude_attest as attest

PRE_INSIDE = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
              "agent_id": "a1", "agent_type": "autopilot-executor-01-calc",
              "effort": {"level": "low"}, "tool_input": {"command": "secret"}}
POST_AGENT = {"hook_event_name": "PostToolUse", "tool_name": "Agent",
              "tool_input": {"subagent_type": "autopilot-executor-01-calc", "prompt": "x"},
              "tool_response": {"status": "completed", "agentId": "a1",
                                "resolvedModel": "claude-haiku-5-5", "totalDurationMs": 1000}}
STOP = {"hook_event_name": "SubagentStop", "agent_id": "a1",
        "agent_type": "autopilot-executor-01-calc", "agent_transcript_path": "/t/a1.jsonl",
        "last_assistant_message": "private"}


class AttestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ap = self.root / ".autopilot"
        self.ap.mkdir()
        (self.ap / "state.js").write_text("window.STATE = {}", encoding="utf-8")
        self.log = self.ap / "attestations.jsonl"

    def run_hook(self, payload, raw=None):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        env["CLAUDE_PROJECT_DIR"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(attest.__file__)], cwd=self.root,
            input=raw if raw is not None else json.dumps(payload), env=env,
            capture_output=True, text=True, encoding="utf-8", timeout=15)

    def lines(self):
        return [json.loads(x) for x in self.log.read_text(encoding="utf-8").splitlines()]

    def test_pre_inside_subagent_records_effort(self):
        self.assertEqual(self.run_hook(PRE_INSIDE).returncode, 0)
        (line,) = self.lines()
        self.assertEqual(line["effort"], "low")
        self.assertEqual(line["agent_type"], "autopilot-executor-01-calc")
        text = self.log.read_text(encoding="utf-8")
        self.assertNotIn("command", text)
        self.assertNotIn("secret", text)

    def test_post_agent_records_resolved_model(self):
        self.assertEqual(self.run_hook(POST_AGENT).returncode, 0)
        (line,) = self.lines()
        self.assertEqual(line["resolved_model"], "claude-haiku-5-5")
        self.assertEqual(line["agent_type"], "autopilot-executor-01-calc")
        self.assertEqual(line["agent_id"], "a1")
        self.assertEqual(line["status"], "completed")
        self.assertNotIn('"x"', self.log.read_text(encoding="utf-8"))

    def test_background_launch_records_status_without_model(self):
        post = json.loads(json.dumps(POST_AGENT))
        post["tool_response"] = {"status": "async_launched", "agentId": "a1"}
        self.assertEqual(self.run_hook(post).returncode, 0)
        (line,) = self.lines()
        self.assertEqual(line["status"], "async_launched")
        self.assertIsNone(line["resolved_model"])

    def test_subagent_stop_never_stores_message(self):
        self.assertEqual(self.run_hook(STOP).returncode, 0)
        self.assertEqual(self.lines()[0]["event"], "SubagentStop")
        self.assertNotIn("private", self.log.read_text(encoding="utf-8"))

    def test_subagent_stop_records_transcript_path(self):
        self.assertEqual(self.run_hook(STOP).returncode, 0)
        (line,) = self.lines()
        self.assertEqual(line["transcript_path"], "/t/a1.jsonl")
        self.assertNotIn("private", self.log.read_text(encoding="utf-8"))

    def test_pre_and_post_lines_have_null_transcript_path(self):
        self.assertEqual(self.run_hook(PRE_INSIDE).returncode, 0)
        self.assertEqual(self.run_hook(POST_AGENT).returncode, 0)
        self.assertEqual([line["transcript_path"] for line in self.lines()], [None, None])

    def test_non_autopilot_agent_ignored(self):
        pre = dict(PRE_INSIDE, agent_type="Explore")
        self.assertEqual(self.run_hook(pre).returncode, 0)
        self.assertFalse(self.log.exists())

    def test_no_state_no_write(self):
        (self.ap / "state.js").unlink()
        self.assertEqual(self.run_hook(PRE_INSIDE).returncode, 0)
        self.assertFalse(self.log.exists())

    def test_malformed_json_exits_zero(self):
        result = self.run_hook(None, raw="{")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.log.exists())

    def test_installer_adds_three_hooks_idempotent(self):
        settings = self.root / ".claude" / "settings.json"
        settings.parent.mkdir()
        settings.write_text(json.dumps({"model": "x", "hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "keep"}]}]}}),
            encoding="utf-8")
        for _ in range(2):
            attest.install_hook(self.root)
        content = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(content["model"], "x")
        ours = [(event, e["matcher"]) for event, entries in content["hooks"].items()
                for e in entries if "claude_attest.py" in json.dumps(e)]
        self.assertEqual(sorted(ours), [("PostToolUse", "Agent"), ("PreToolUse", "*"),
                                        ("SubagentStop", "autopilot-.*")])
        self.assertEqual(len(content["hooks"]["PreToolUse"]), 2)  # unrelated hook kept
        inner = content["hooks"]["PostToolUse"][0]["hooks"][0]
        self.assertEqual(inner["command"], str(Path(sys.executable).resolve()))
        self.assertTrue(inner["args"][0].startswith("${CLAUDE_PROJECT_DIR}"))
        self.assertNotIn("onFailure", inner)


if __name__ == "__main__":
    unittest.main()
