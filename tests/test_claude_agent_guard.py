"""Claude PreToolUse guard tests (no Claude subscription or process required)."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import claude_agent_guard as guard


class HookGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ap = self.root / ".autopilot"
        self.ap.mkdir()
        self.agents = self.root / ".claude" / "agents"
        self.agents.mkdir(parents=True)
        self.name = "autopilot-executor-01-simple"
        self.file = self.agents / (self.name + ".md")
        self.file.write_text(
            "---\nname: " + self.name +
            "\ndescription: Test\nmodel: haiku\neffort: low\n---\nTask\n",
            encoding="utf-8")
        self.sha = hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.state = {"strictRouting": True, "finishedAt": None,
                      "tickets": [{"routing": {
                          "agentType": self.name, "provider": "anthropic",
                          "model": "haiku", "effort": "low",
                          "profileSha": self.sha, "verified": True,
                      }}]}
        self.save()
        (self.ap / "model-capabilities.json").write_text(
            json.dumps({"provider": "anthropic", "model_selection": True,
                        "models": {"haiku": ["low"]}}), encoding="utf-8")

    def save(self):
        (self.ap / "state.js").write_text("window.STATE =\n" + json.dumps(self.state), encoding="utf-8")

    def payload(self, agent=None, **args):
        return {"tool_name": "Agent",
                "tool_input": {"subagent_type": self.name if agent is None else agent, **args}}

    def test_approved_executor_is_allowed(self):
        ok, why = guard.decision(self.payload(), self.root)
        self.assertTrue(ok, why)

    def test_generic_agent_is_denied(self):
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("Only explicitly", why)

    def test_premium_or_inherited_model_is_denied(self):
        self.file.write_text(self.file.read_text(encoding="utf-8").replace("haiku", "fable"), encoding="utf-8")
        ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("Premium", why)

    def test_override_of_pinned_effort_is_denied(self):
        ok, why = guard.decision(self.payload(effort="high"), self.root)
        self.assertFalse(ok)
        self.assertIn("overrides", why)

    def test_modified_profile_is_denied(self):
        with self.file.open("a", encoding="utf-8") as f:
            f.write("Changed")
        ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("changed", why)

    def test_missing_host_capabilities_denied(self):
        (self.ap / "model-capabilities.json").unlink()
        ok, _ = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)

    def test_no_active_strict_autopilot_leaves_normal_claude_use_unaffected(self):
        self.state["strictRouting"] = False
        self.save()
        ok, _ = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
