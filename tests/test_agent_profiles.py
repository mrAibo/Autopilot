"""Integration contracts for native Claude Code and Codex agent configuration."""
import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"
sys.path.insert(0, str(TOOLS))
import agent_profiles


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ticket = self.root / ".autopilot" / "run" / "tickets" / "01-simple.md"
        self.ticket.parent.mkdir(parents=True)
        self.ticket.write_text("# T01\n**Зона:** `docs/`\nSmall documentation edit", encoding="utf-8")
        self.caps = self.root / "capabilities.json"

    def capabilities(self, provider="anthropic", model="haiku", effort="low", enforced=True):
        self.caps.write_text(json.dumps({
            "provider": provider, "model_selection": enforced,
            "models": {model: [effort]},
        }), encoding="utf-8")
        return self.caps

    @staticmethod
    def easy():
        return {"algorithm": 0, "coupling": 0, "uncertainty": 0,
                "context": 0, "testing": 0, "risk": 0}

    def test_claude_profile_explicit_model_effort_and_tools(self):
        self.capabilities()
        result = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        "executor", scores=self.easy(), install=True)
        text = (self.root / result["agent_file"]).read_text(encoding="utf-8")
        self.assertIn("model: haiku", text)
        self.assertIn("effort: low", text)
        self.assertIn("tools: Read, Grep, Glob, Bash, Edit, Write", text)
        self.assertFalse(result["host_execution_verified"])

    def _claude_text(self, role):
        self.capabilities()
        result = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        role, scores=self.easy(), install=True)
        return (self.root / result["agent_file"]).read_text(encoding="utf-8")

    def test_acceptance_profile_has_bash_but_no_edit(self):
        text = self._claude_text("acceptance")
        self.assertIn("tools: Read, Grep, Glob, Bash\n", text)
        self.assertIn("disallowedTools: Edit, Write, Agent\n", text)
        self.assertIn("omitClaudeMd: true\n", text)

    def test_reviewer_profile_has_bash_but_no_edit(self):
        text = self._claude_text("reviewer")
        self.assertIn("tools: Read, Grep, Glob, Bash\n", text)
        self.assertIn("disallowedTools: Edit, Write, Agent\n", text)
        self.assertNotIn("omitClaudeMd", text)

    def test_executor_profile_unchanged(self):
        text = self._claude_text("executor")
        self.assertIn("tools: Read, Grep, Glob, Bash, Edit, Write\n", text)
        self.assertNotIn("disallowedTools", text)
        self.assertNotIn("omitClaudeMd", text)

    def test_codex_profile_is_valid_toml(self):
        self.capabilities("openai", "gpt-6-luna", "low")
        result = agent_profiles.prepare(self.root, self.ticket, "openai", self.caps,
                                        "executor", scores=self.easy(), install=True)
        config = tomllib.loads((self.root / result["agent_file"]).read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "gpt-6-luna")
        self.assertEqual(config["model_reasoning_effort"], "low")
        self.assertEqual(config["name"], result["agent_type"])
        self.assertIn("developer_instructions", config)

    def test_model_only_profiles_omit_unenforceable_effort(self):
        for provider, model in (("openai", "gpt-6-luna"),
                                ("anthropic", "haiku")):
            with self.subTest(provider=provider):
                self.capabilities(provider, model, "high")
                self.caps.write_text(json.dumps({
                    "provider": provider, "model_selection": True,
                    "effort_selection": False,
                    "models": {model: []}}), encoding="utf-8")
                result = agent_profiles.prepare(
                    self.root, self.ticket, provider, self.caps,
                    "executor", scores=self.easy(), install=True)
                text = (self.root / result["agent_file"]).read_text(encoding="utf-8")
                self.assertIn(model, text)
                self.assertFalse(result["effort_enforced"])
                if provider == "anthropic":
                    self.assertNotIn("\\neffort:", text)
                else:
                    self.assertNotIn("model_reasoning_effort =", text)

    def test_dry_run_does_not_install_or_change_repo(self):
        self.capabilities()
        result = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        "executor", scores=self.easy())
        self.assertEqual(result["action"], "dry-run")
        self.assertFalse((self.root / result["agent_file"]).exists())

    def test_second_install_is_idempotent(self):
        self.capabilities()
        first = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                       "explorer", scores=self.easy(), install=True)
        second = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        "explorer", scores=self.easy(), install=True)
        self.assertEqual((first["action"], second["action"]), ("created", "unchanged"))
        content = (self.root / first["agent_file"]).read_text(encoding="utf-8")
        self.assertIn("tools: Read, Grep, Glob\n", content)

    def test_refuses_overwrite_of_modified_profile(self):
        self.capabilities()
        result = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        "executor", scores=self.easy(), install=True)
        (self.root / result["agent_file"]).write_text("MANUAL", encoding="utf-8")
        with self.assertRaises(agent_profiles.ProfileError):
            agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                   "executor", scores=self.easy(), install=True)

    def test_blocked_without_host_model_selection(self):
        self.capabilities(enforced=False)
        with self.assertRaises(agent_profiles.ProfileError):
            agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                   "executor", scores=self.easy(), install=True)
        self.assertFalse((self.root / ".claude").exists())

    def test_rejects_ticket_outside_project(self):
        self.capabilities()
        other = Path(tempfile.mkdtemp()) / "outside.md"
        self.addCleanup(lambda: other.parent.rmdir())
        self.addCleanup(lambda: other.unlink(missing_ok=True))
        other.write_text("Test", encoding="utf-8")
        with self.assertRaises(agent_profiles.ProfileError):
            agent_profiles.prepare(self.root, other, "anthropic", self.caps,
                                   "executor", scores=self.easy())

    def test_premium_rejected_even_if_host_advertises(self):
        self.capabilities("anthropic", "fable", "low")
        policy = self.root / "policy.json"
        policy.write_text(json.dumps({
            "providers": {
                "anthropic": {"cheap": {"model": "fable", "effort": "low"}}
            }
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                   "executor", policy=policy, scores=self.easy(), install=True)

    def test_security_sensitive_routes_to_stronger_model(self):
        self.capabilities("anthropic", "sonnet", "high")
        scores = dict(self.easy(), risk=10)
        result = agent_profiles.prepare(self.root, self.ticket, "anthropic", self.caps,
                                        "reviewer", scores=scores, install=True)
        self.assertEqual(result["model"], "sonnet")
        self.assertEqual(result["effort"], "high")
        text = (self.root / result["agent_file"]).read_text(encoding="utf-8")
        self.assertNotIn("tools: Read, Grep, Glob, Bash, Edit, Write", text)
        self.assertIn("disallowedTools: Edit, Write, Agent", text)


if __name__ == "__main__":
    unittest.main()
