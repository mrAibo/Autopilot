"""Strict routing cannot assume that custom Codex GUI subagents are available."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills" / "autopilot" / "tools"))
import codex_native_agents as native
import agent_profiles


def catalog():
    return {"models": [
        {"slug": "gpt-6-sol", "multi_agent_version": "v2",
         "supported_reasoning_levels": [{"effort": "low"}]},
        {"slug": "gpt-6-luna", "multi_agent_version": "v2",
         "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}]},
        {"slug": "gpt-5.6-luna", "multi_agent_version": "v1",
         "supported_reasoning_levels": [{"effort": "low"}]},
    ]}


class NativeAgentGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.agent = "autopilot-explorer-smoke"
        self.profile = Path(self.tmp.name) / (self.agent + ".toml")
        _, body = agent_profiles.definition("openai", self.agent, "explorer",
                                            {"model": "gpt-6-luna", "effort": "low"}, "PROBE.md")
        self.profile.write_text(body, encoding="utf-8")

    def test_v2_parent_blocks_named_agent(self):
        result = native.catalog_preflight(catalog(), "gpt-6-sol", "gpt-6-luna", "low")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["multi_agent_version"], "v2")

    def test_v1_is_candidate_not_proof(self):
        result = native.catalog_preflight(catalog(), "gpt-5.6-luna",
                                          "gpt-6-luna", "low")
        self.assertEqual(result["status"], "candidate-only")

    def test_unknown_parent_and_effort_fail_closed(self):
        self.assertEqual(native.catalog_preflight(catalog(), "unknown", "gpt-6-luna", "low")["status"],
                         "blocked")
        self.assertEqual(native.catalog_preflight(catalog(), "gpt-5.6-luna",
                                                   "gpt-6-luna", "max")["status"], "blocked")
        with self.assertRaises(native.NativeAgentError):
            native.catalog_preflight(catalog(), "gpt-5.6-luna", "gpt-6-luna", "ridiculous")

    def test_profile_must_pin_exact_model_and_effort(self):
        native.check_profile(self.profile, self.agent, "gpt-6-luna", "low")
        with self.assertRaisesRegex(native.NativeAgentError, "approved model"):
            native.check_profile(self.profile, self.agent, "gpt-6-sol", "low")
        with self.assertRaisesRegex(native.NativeAgentError, "approved model_reasoning_effort"):
            native.check_profile(self.profile, self.agent, "gpt-6-luna", "high")
        self.profile.write_text("name = 'autopilot-explorer-smoke'\n", encoding="utf-8")
        with self.assertRaises(native.NativeAgentError):
            native.check_profile(self.profile, self.agent, "gpt-6-luna", "low")

    def test_model_text_cannot_forge_native_spawn(self):
        events = [{"type": "item.completed", "item": {"type": "agent_message",
                   "text": "I spawned autopilot-explorer-smoke gpt-6-luna low"}}]
        self.assertEqual(native.attested_events(events, self.agent, "gpt-6-luna", "low")["status"],
                         "unverified")

    def test_spawn_without_child_settings_is_not_accepted(self):
        events = [{"type": "item.completed", "item": {"type": "collab_tool_call",
                    "tool": "spawn_agent", "agent_type": self.agent, "child_id": "123"}}]
        self.assertEqual(native.attested_events(events, self.agent, "gpt-6-luna", "low")["status"],
                         "unverified")

    def test_mismatched_child_metadata_is_not_accepted(self):
        spawn = {"type": "item.completed", "item": {"type": "collab_tool_call",
                 "tool": "spawn_agent", "agent_type": self.agent, "child_id": "123"}}
        child = {"type": "item.completed", "item": {"type": "child_session_metadata",
                 "agent_type": self.agent, "child_id": "123",
                 "model": "gpt-6-sol", "model_reasoning_effort": "low"}}
        self.assertEqual(native.attested_events([spawn, child], self.agent,
                                                 "gpt-6-luna", "low")["status"], "unverified")

    def test_synthetic_positive_metadata_shape(self):
        spawn = {"type": "item.completed", "item": {"type": "collab_tool_call",
                 "tool": "spawn_agent", "agent_type": self.agent, "child_id": "123"}}
        child = {"type": "item.completed", "item": {"type": "child_session_metadata",
                 "agent_type": self.agent, "child_id": "123",
                 "model": "gpt-6-luna", "model_reasoning_effort": "low"}}
        self.assertEqual(native.attested_events([spawn, child], self.agent,
                                                 "gpt-6-luna", "low")["status"], "trace-consistent")

    def test_v1_catalog_inspection_without_events_remains_unverified(self):
        with patch.object(native, "resolved_catalog", return_value=catalog()):
            result = native.inspect("ignored", self.profile, self.agent,
                                    "gpt-5.6-luna", "gpt-6-luna", "low")
        self.assertEqual(result["status"], "candidate-only")
        self.assertFalse(result["native_session_verified"])

    def test_local_v1_runtime_had_no_native_spawn_evidence(self):
        fixture = [
            json.dumps({"type": "thread.started", "thread_id": "probe"}),
            json.dumps({"type": "item.completed",
                        "item": {"type": "agent_message", "text": "NAMED_AGENT_UNAVAILABLE"}}),
            json.dumps({"type": "turn.completed", "usage": {"output_tokens": 54}})
        ]
        self.assertEqual(native.attested_events(fixture, self.agent,
                                                "gpt-6-luna", "low")["status"], "unverified")


if __name__ == "__main__":
    unittest.main()
