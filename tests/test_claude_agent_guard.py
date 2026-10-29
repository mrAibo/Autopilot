"""Claude PreToolUse guard tests (no Claude subscription or process required)."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
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

    def test_worktree_isolation_in_call_is_denied(self):
        # T12 option B: Autopilot owns ticket worktrees; Claude's own isolation bypasses them.
        ok, why = guard.decision(self.payload(isolation="worktree"), self.root)
        self.assertFalse(ok)
        self.assertIn("isolation", why)

    def test_worktree_isolation_in_profile_is_denied(self):
        profile = self.root / ".claude" / "agents" / (self.name + ".md")
        text = profile.read_text(encoding="utf-8")
        profile.write_text(text.replace("---\n", "---\nisolation: worktree\n", 1), encoding="utf-8")
        ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("isolation", why)

    def test_premium_or_inherited_model_is_denied(self):
        self.file.write_text(self.file.read_text(encoding="utf-8").replace("haiku", "fable"), encoding="utf-8")
        ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("Premium", why)

    def test_override_of_pinned_effort_is_denied(self):
        ok, why = guard.decision(self.payload(effort="high"), self.root)
        self.assertFalse(ok)
        self.assertIn("overrides", why)

    def test_forced_global_model_is_denied_even_if_profile_matches(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {
                "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1",
                "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"}):
            ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("FORCE", why)

    def test_conflicting_global_effort_is_denied(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"CLAUDE_CODE_EFFORT_LEVEL": "high"}):
            ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("environment override", why)

    def test_matching_global_effort_does_not_break_route(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"CLAUDE_CODE_EFFORT_LEVEL": "low"}):
            ok, why = guard.decision(self.payload(), self.root)
        self.assertTrue(ok, why)

    def model_only(self):
        self.file.write_text(self.file.read_text(encoding="utf-8").replace(
            "effort: low" + chr(10), ""), encoding="utf-8")
        route = self.state["tickets"][0]["routing"]
        route["profileSha"] = hashlib.sha256(self.file.read_bytes()).hexdigest()
        route["effortEnforced"] = False
        self.save()
        (self.ap / "model-capabilities.json").write_text(json.dumps({
            "provider": "anthropic", "model_selection": True,
            "effort_selection": False, "models": {"haiku": []}}), encoding="utf-8")

    def test_model_only_allows_effort_override_but_not_model_override(self):
        from unittest.mock import patch
        self.model_only()
        with patch.dict("os.environ", {"CLAUDE_CODE_EFFORT_LEVEL": "high"}):
            ok, why = guard.decision(self.payload(effort="high"), self.root)
        self.assertTrue(ok, why)
        self.assertIn("unverified", why)
        ok, why = guard.decision(self.payload(model="sonnet"), self.root)
        self.assertFalse(ok)
        self.assertIn("model", why.lower())

    def test_model_only_still_denies_generic_and_forced_global_model(self):
        from unittest.mock import patch
        self.model_only()
        ok, _ = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        with patch.dict("os.environ", {"CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"}):
            ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("FORCE", why)

    def test_model_only_rejects_mismatched_route_capabilities(self):
        self.model_only()
        self.state["tickets"][0]["routing"]["effortEnforced"] = True
        self.save()
        self.assertFalse(guard.decision(self.payload(), self.root)[0])
        self.state["tickets"][0]["routing"]["effortEnforced"] = False
        self.save()
        self.file.write_text(self.file.read_text(encoding="utf-8").replace(
            "model: haiku", "model: sonnet"), encoding="utf-8")
        self.assertFalse(guard.decision(self.payload(), self.root)[0])

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

    def test_installer_preserves_existing_settings_and_is_idempotent(self):
        settings = self.root / ".claude" / "settings.json"
        settings.write_text(json.dumps({"permissions": {"allow": ["Read"]}}),
                            encoding="utf-8")
        _, installed = guard.install_hook(self.root)
        self.assertTrue(installed)
        content = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(content["permissions"]["allow"], ["Read"])
        self.assertEqual(content["hooks"]["PreToolUse"][0]["matcher"], "Agent|Task")
        _, installed = guard.install_hook(self.root)
        self.assertFalse(installed)
        content = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(len(content["hooks"]["PreToolUse"]), 1)

    def test_installer_writes_exec_form_fail_closed(self):
        guard.install_hook(self.root)
        settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        hook = settings["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertEqual(hook["command"], str(Path(sys.executable).resolve()))
        self.assertTrue(hook["args"][0].startswith("${CLAUDE_PROJECT_DIR}"))
        self.assertEqual(hook["onFailure"], "block")

    def test_installer_denies_claude_started_forks(self):
        settings = self.root / ".claude" / "settings.json"
        settings.write_text(json.dumps({"permissions": {"deny": ["Bash(rm *)"]}}),
                            encoding="utf-8")
        guard.install_hook(self.root)
        guard.install_hook(self.root)
        deny = json.loads(settings.read_text(encoding="utf-8"))["permissions"]["deny"]
        self.assertEqual(deny, ["Bash(rm *)", "Agent(fork)"])

    def test_installer_adds_fork_deny_to_existing_hook_install(self):
        guard.install_hook(self.root)
        settings = self.root / ".claude" / "settings.json"
        content = json.loads(settings.read_text(encoding="utf-8"))
        content["permissions"]["deny"].remove("Agent(fork)")
        settings.write_text(json.dumps(content), encoding="utf-8")
        _, installed = guard.install_hook(self.root)
        self.assertTrue(installed)
        self.assertIn("Agent(fork)",
                      json.loads(settings.read_text(encoding="utf-8"))["permissions"]["deny"])

    def test_installer_rejects_invalid_permissions_shape(self):
        settings = self.root / ".claude" / "settings.json"
        settings.write_text(json.dumps({"permissions": {"deny": "Agent(fork)"}}),
                            encoding="utf-8")
        with self.assertRaises(ValueError):
            guard.install_hook(self.root)

    def test_installer_replaces_legacy_relative_hook(self):
        settings = self.root / ".claude" / "settings.json"
        legacy = {"matcher": "Agent|Task", "hooks": [
            {"type": "command", "command": "python .autopilot/claude_agent_guard.py"}]}
        other = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}
        settings.write_text(json.dumps({"hooks": {"PreToolUse": [other, legacy]}}),
                            encoding="utf-8")
        _, installed = guard.install_hook(self.root)
        self.assertTrue(installed)
        entries = json.loads(settings.read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
        self.assertIn(other, entries)
        guards = [e for e in entries if "claude_agent_guard.py" in json.dumps(e)]
        self.assertEqual(len(guards), 1)
        self.assertEqual(guards[0]["hooks"][0]["onFailure"], "block")
        self.assertNotIn(legacy, entries)

    def test_root_from_claude_project_dir_env(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(self.root)}):
            self.assertEqual(guard.project_root({"cwd": "/somewhere/else"}), str(self.root))

    def test_root_falls_back_to_payload_cwd(self):
        from unittest.mock import patch
        with patch.dict("os.environ", {}):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            self.assertEqual(guard.project_root({"cwd": str(self.root)}), str(self.root))

    def test_installer_rejects_invalid_settings_shape(self):
        settings = self.root / ".claude" / "settings.json"
        settings.write_text("[]", encoding="utf-8")
        with self.assertRaises(ValueError):
            guard.install_hook(self.root)
        self.assertEqual(settings.read_text(encoding="utf-8"), "[]")

    def test_no_active_strict_autopilot_leaves_normal_claude_use_unaffected(self):
        self.state["strictRouting"] = False
        self.save()
        ok, _ = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertTrue(ok)

    def test_absent_autopilot_state_does_not_block_unrelated_claude(self):
        (self.ap / "state.js").unlink()
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertTrue(ok, why)

    def test_corrupt_existing_state_denies_generic_agent(self):
        (self.ap / "state.js").write_text("window.STATE = {not JSON}", encoding="utf-8")
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("malformed", why)

    def test_non_object_existing_state_denies_agent(self):
        (self.ap / "state.js").write_text("window.STATE = [];", encoding="utf-8")
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("malformed", why)

    def test_corrupt_strict_flag_is_not_permissive(self):
        self.state["strictRouting"] = "false"
        self.save()
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("strictRouting", why)

    def test_empty_state_object_is_not_an_opt_out(self):
        (self.ap / "state.js").write_text("window.STATE = {};", encoding="utf-8")
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("ticket ledger", why)

    def test_corrupt_ticket_ledger_is_not_an_opt_out(self):
        self.state["tickets"] = "invalid"
        self.state["strictRouting"] = False
        self.save()
        ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("ticket ledger", why)

    def test_corrupt_state_does_not_block_unrelated_tool(self):
        (self.ap / "state.js").write_text("corrupt", encoding="utf-8")
        ok, why = guard.decision({"tool_name": "Read", "tool_input": {}}, self.root)
        self.assertTrue(ok, why)

    def test_existing_state_read_error_denies_agent(self):
        from unittest.mock import patch
        with patch.object(guard, "read_state", return_value=None):
            ok, why = guard.decision(self.payload(agent="Explore"), self.root)
        self.assertFalse(ok)
        self.assertIn("unreadable", why)

    def run_real_hook(self, payload, cwd=None, project_dir=None):
        # Isolate from the caller's Claude session so cwd-only tests stay meaningful.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        if project_dir is not None:
            env["CLAUDE_PROJECT_DIR"] = str(project_dir)
        return subprocess.run(
            [sys.executable, str(guard.__file__)],
            cwd=cwd or self.root, input=json.dumps(payload), env=env,
            capture_output=True, text=True, encoding="utf-8", timeout=15)

    def test_strict_run_denied_when_hook_cwd_is_subdirectory(self):
        sub = self.root / "sub"
        sub.mkdir()
        result = self.run_real_hook(self.payload(agent="Explore"), cwd=sub,
                                    project_dir=self.root)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Only explicitly", result.stderr)

    def test_real_hook_subprocess_blocks_corrupt_state(self):
        state_path = self.ap / "state.js"
        state_path.write_text("window.STATE = {bad}", encoding="utf-8")
        old_bytes = state_path.read_bytes()
        result = self.run_real_hook(self.payload(agent="Explore"))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("malformed", result.stderr)
        self.assertEqual(state_path.read_bytes(), old_bytes)

    def test_real_hook_subprocess_accepts_pinned_executor(self):
        result = self.run_real_hook(self.payload())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_real_hook_subprocess_allows_unrelated_project(self):
        (self.ap / "state.js").unlink()
        result = self.run_real_hook(self.payload(agent="Explore"))
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
