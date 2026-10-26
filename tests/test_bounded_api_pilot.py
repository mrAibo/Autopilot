"""An offline Responses API adapter qualification; no live model calls."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                        "skills" / "autopilot" / "tools"))
import bounded_api_pilot as pilot
import test_gui_bridge_e2e


def response(source=pilot.EXPECTED, *, model=pilot.MODEL,
             status="completed", input_tokens=200, output_tokens=42):
    return {
        "id": "resp_offlinepilot0102030405", "status": status,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens,
                  "input_tokens_details": {"cached_tokens": 10}},
        "output": [{
            "type": "message", "role": "assistant", "status": "completed",
            "content": [{"type": "output_text",
                         "text": json.dumps({"source": source})}]}]
    }


class BoundedAPIPilotTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_gui_bridge_e2e.BridgeRealProcessLifecycle(
            "test_actual_offline_subprocess_to_accepted_git_and_no_replay")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.h = self.fixture.harness
        self.h.ap("budget", "--tokens", "8000")
        (Path(self.h.a) / "api-pilot-consent").write_text(
            pilot.MARKER, encoding="utf-8")
        for action in ("prepare", "start"):
            code, out = self.fixture.controller("--advance")
            self.assertEqual(code, 0, out)
            self.assertEqual(out["completed"]["action"], action)

    def execute(self, **kwargs):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-" + "A" * 35}):
            return pilot.run(self.h.root, "01", execute=True,
                             approval="01", **kwargs)

    def test_tiny_fixed_request_and_no_arbitrary_tools(self):
        body = pilot.request_body()
        config = json.loads(body)
        self.assertLessEqual(len(body), pilot.MAX_REQUEST_BYTES)
        self.assertEqual(config["model"], "gpt-6-luna")
        self.assertEqual(config["max_output_tokens"], pilot.MAX_OUTPUT_TOKENS)
        self.assertEqual(config["tools"], [])
        self.assertEqual(config["tool_choice"], "none")
        self.assertFalse(config["store"])
        self.assertEqual(config["truncation"], "disabled")
        self.assertEqual(config["text"]["format"]["type"], "json_schema")

    def test_preview_is_read_only_and_fails_to_claim_without_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            preview = pilot.run(self.h.root, "01")
            self.assertEqual(preview["status"], "dry-run")
            self.assertFalse(preview["api_key_available"])
            with patch.object(pilot, "send_once") as external:
                with self.assertRaisesRegex(pilot.PilotError, "Missing valid OPENAI_API_KEY"):
                    pilot.run(self.h.root, "01", execute=True, approval="01")
                external.assert_not_called()
        self.assertFalse((Path(self.h.a) / "api-pilot").exists())

    def test_real_host_lifecycle_with_synthetic_http_response(self):
        with patch.object(pilot, "send_once", return_value=response()) as external:
            result = self.execute()
        self.assertEqual(result["status"], "ready-for-host-verification", result)
        self.assertTrue(result["model_invoked"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["tests_verified"])
        self.assertEqual(external.call_count, 1)
        self.assertEqual(self.h.state()["usageEvents"][0]["input"], 200)
        self.assertEqual(self.h.state()["usageEvents"][0]["output"], 42)
        self.assertEqual(self.h.state()["usageEvents"][0]["source"], "responses-api")
        record = json.loads((Path(self.h.a) / "api-pilot" / "01.json")
                            .read_text(encoding="utf-8"))
        self.assertNotIn("sk-", str(record))
        self.assertTrue(record["usage_recorded"])
        self.assertEqual(record["status"], "ready-for-host-verification")
        with patch.object(pilot, "send_once") as duplicate:
            with self.assertRaisesRegex(pilot.PilotError, "Prior API pilot"):
                self.execute()
            duplicate.assert_not_called()
        for action in ("verify", "finalize", "land", "accept", "release"):
            code, out = self.fixture.controller(
                "--suite", "test_core.py", "--advance")
            self.assertEqual(code, 0, (action, out))
            self.assertEqual(out["completed"]["action"], action)
        self.assertEqual(self.h.state()["tickets"][0]["status"], "done")
        self.assertEqual((Path(self.h.root) / pilot.SOURCE).read_text(encoding="utf-8"),
                         pilot.EXPECTED)

    def test_provider_incomplete_never_applies_or_retries(self):
        with patch.object(pilot, "send_once",
                          return_value=response(status="incomplete")) as external:
            result = self.execute()
        self.assertEqual(external.call_count, 1)
        self.assertEqual(result["status"], "blocked")
        self.assertTrue((Path(self.h.a) / "api-pilot" / "01.json").exists())
        target = Path(self.h.state()["tickets"][0]["worktree"]["cwd"])
        self.assertEqual((target / pilot.SOURCE).read_text(encoding="utf-8"),
                         pilot.BASELINE)
        self.assertEqual(self.h.state()["usageEvents"], [])
        with patch.object(pilot, "send_once") as second:
            with self.assertRaisesRegex(pilot.PilotError, "Prior API pilot"):
                self.execute()
            second.assert_not_called()

    def test_unapproved_source_is_not_applied(self):
        malicious = "def add(a, b):\n    __import__('os').system('echo surprise')\n"
        with patch.object(pilot, "send_once",
                          return_value=response(source=malicious)):
            result = self.execute()
        self.assertEqual(result["status"], "blocked")
        target = Path(self.h.state()["tickets"][0]["worktree"]["cwd"])
        self.assertEqual((target / pilot.SOURCE).read_text(encoding="utf-8"),
                         pilot.BASELINE)

    def test_network_timeout_is_uncertain_and_nonreplayable(self):
        with patch.object(pilot, "send_once", side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                self.execute()
        record = json.loads((Path(self.h.a) / "api-pilot" / "01.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "invocation-uncertain")
        with patch.object(pilot, "send_once") as repeated:
            with self.assertRaisesRegex(pilot.PilotError, "Prior API pilot"):
                self.execute()
            repeated.assert_not_called()

    def test_wrong_zone_and_consent_refuse_before_network(self):
        marker = Path(self.h.a) / "api-pilot-consent"
        marker.unlink()
        with patch.object(pilot, "send_once") as send:
            with self.assertRaisesRegex(pilot.PilotError, "consent"):
                self.execute()
            send.assert_not_called()
        marker.write_text(pilot.MARKER, encoding="utf-8")
        state = self.h.state()
        state["tickets"][0]["zone"] = ["src/bot/"]
        (Path(self.h.a) / "state.js").write_text(
            "window.STATE =\n" + json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(pilot.PilotError, "route"):
            pilot.run(self.h.root, "01")
        self.assertFalse((Path(self.h.a) / "api-pilot").exists())

    def test_no_unbounded_retries_or_non_temp_checkout(self):
        with self.assertRaises(pilot.PilotError):
            pilot.run(Path.cwd(), "01")
        with self.assertRaisesRegex(pilot.PilotError, "approve-pilot-ticket"):
            pilot.run(self.h.root, "01", execute=True, approval="02")
        self.assertFalse((Path(self.h.a) / "api-pilot").exists())

    def test_usage_outside_output_limit_rejected(self):
        with patch.object(pilot, "send_once",
                          return_value=response(output_tokens=999)):
            result = self.execute()
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.h.state()["usageEvents"], [])

if __name__ == "__main__":
    unittest.main()
