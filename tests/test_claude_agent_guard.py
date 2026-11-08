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
import gate_sign


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

    def write(self, path, tool="Write"):
        return guard.decision({"tool_name": tool, "tool_input": {"file_path": str(path)}}, self.root)

    def test_strict_run_blocks_writes_to_run_files(self):
        for rel in (".autopilot/state.js", ".autopilot/attestations.jsonl",
                    ".autopilot/model-capabilities.json", ".claude/settings.json",
                    ".claude/settings.local.json", ".claude/agents/x.md"):
            for tool in ("Write", "Edit", "MultiEdit"):
                self.assertFalse(self.write(self.root / rel, tool)[0], (rel, tool))
        ok, _ = guard.decision({"tool_name": "NotebookEdit", "tool_input": {
            "notebook_path": ".autopilot/state.js"}}, self.root)
        self.assertFalse(ok)
        self.assertFalse(self.write(self.root / "src" / ".." / ".autopilot" / "state.js")[0])

    def test_strict_run_blocks_writes_to_verifier_scripts(self):
        for name in ("gate_sign.py", "claude_agent_guard.py", "claude_attest.py",
                     "ap.py", "test_evidence.py"):
            self.assertFalse(self.write(self.root / ".autopilot" / name)[0], name)
        self.assertTrue(self.write(self.root / "src" / "ap.py")[0])

    def test_signed_run_downgrade_is_denied_by_guard(self):
        import gate_sign
        from unittest import mock
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        with mock.patch.dict(os.environ, {"AUTOPILOT_HOME": home.name}):
            gate_sign.ensure_key()
            gate_sign.write_run_record(self.root, self.state)  # init --strict-routing wrote it
            self.state["tickets"][0]["id"] = "01"  # strictRouting run, key exists, no marker
            self.save()
            ok, why = guard.decision(self.payload(), self.root)
            self.assertFalse(ok)
            self.assertIn("marker", why)

    def signed_run(self):
        """Key + record like a real `init --strict-routing`; returns the env patch to enter."""
        import gate_sign
        from unittest import mock
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        env = mock.patch.dict(os.environ, {"AUTOPILOT_HOME": home.name})
        env.start()
        self.addCleanup(env.stop)
        gate_sign.ensure_key()
        self.state.update(slug="s", startedAt="t0")
        self.state["gateMark"] = gate_sign.run_mark(self.state)
        gate_sign.write_run_record(self.root, self.state)
        route = self.state["tickets"][0]["routing"]
        self.state["tickets"][0]["id"] = "01"
        route["sig"] = gate_sign.sign(gate_sign.routing_payload("01", route))
        self.save()

    def test_record_mismatch_is_denied_before_the_no_active_run_shortcut(self):
        self.signed_run()
        self.assertTrue(guard.decision(self.payload(), self.root)[0])  # honest signed run
        for edit in ({"strictRouting": False}, {"finishedAt": "2026-11-03"}):
            with self.subTest(edit=edit):
                state = dict(self.state, **edit)
                (self.ap / "state.js").write_text("window.STATE = " + json.dumps(state), encoding="utf-8")
                ok, why = guard.decision(self.payload(), self.root)
                self.assertFalse(ok)
                self.assertIn("marker", why)
                ok, why = self.write(self.root / ".autopilot" / "state.js")
                self.assertFalse(ok)
                self.assertIn("marker", why)

    def test_is_protected_ignores_case_of_autopilot_and_claude_dirs(self):
        from unittest import mock
        # POSIX normcase keeps case; macOS and Windows file systems do not distinguish it.
        with mock.patch("os.path.normcase", side_effect=lambda p: p):
            for rel in (".Autopilot/state.js", ".AUTOPILOT/ATTESTATIONS.jsonl", ".Autopilot/AP.py",
                        ".CLAUDE/settings.json", ".Claude/Settings.local.json", ".claude/Agents/x.md"):
                with self.subTest(rel=rel):
                    self.assertTrue(guard.is_protected(rel, str(self.root)))
            self.assertFalse(guard.is_protected("src/.Autopilot/state.js", str(self.root)))

    def test_other_files_and_finished_or_non_strict_runs_are_writable(self):
        self.assertTrue(self.write(self.root / "src" / "app.py")[0])
        self.assertTrue(self.write(self.root / ".autopilot" / "notes.md")[0])
        self.state["finishedAt"] = "2026-01-01"
        self.save()
        self.assertTrue(self.write(self.root / ".autopilot" / "state.js")[0])
        self.state.update(finishedAt=None, strictRouting=False)
        self.save()
        self.assertTrue(self.write(self.root / ".autopilot" / "state.js")[0])

    def test_installer_adds_write_matcher_once(self):
        guard.install_hook(self.root)
        guard.install_hook(self.root)
        entries = json.loads((self.root / ".claude" / "settings.json").read_text(
            encoding="utf-8"))["hooks"]["PreToolUse"]
        self.assertEqual([e["matcher"] for e in entries],
                         ["Agent|Task", "Write|Edit|MultiEdit|NotebookEdit", "Bash"])

    def test_signed_run_requires_valid_route_signature(self):
        import gate_sign
        from unittest import mock
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        with mock.patch.dict(os.environ, {"AUTOPILOT_HOME": home.name}):
            self.state["gateMark"] = "placeholder"
            self.state["tickets"][0]["id"] = "01"
            self.save()
            self.assertEqual(guard.decision(self.payload(), self.root)[1], gate_sign.MISSING_KEY_MESSAGE)
            gate_sign.ensure_key()
            self.state["gateMark"] = gate_sign.run_mark(self.state)
            gate_sign.write_run_record(self.root, self.state)
            self.save()
            self.assertIn("signature", guard.decision(self.payload(), self.root)[1])  # no sig yet
            route = self.state["tickets"][0]["routing"]
            route["sig"] = gate_sign.sign(gate_sign.routing_payload("01", route))
            self.save()
            self.assertTrue(guard.decision(self.payload(), self.root)[0])
            route["score"] = 99  # forged field, old signature
            self.save()
            self.assertIn("signature", guard.decision(self.payload(), self.root)[1])
            del route["score"]
            self.save()
            os.remove(os.path.join(home.name, "gate.key"))
            self.assertEqual(guard.decision(self.payload(), self.root)[1], gate_sign.MISSING_KEY_MESSAGE)

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
        self.assertNotIn("opusApproval", self.state)  # no user approval: the default
        self.file.write_text(self.file.read_text(encoding="utf-8").replace("haiku", "fable"), encoding="utf-8")
        ok, why = guard.decision(self.payload(), self.root)
        self.assertFalse(ok)
        self.assertIn("Premium", why)

    def test_every_opus_spelling_is_denied_by_the_shared_allowlist(self):
        self.assertNotIn("opusApproval", self.state)  # without approval, stated explicitly
        original = self.file.read_text(encoding="utf-8")
        for model in ("us.anthropic.claude-opus-4-1-20250805-v1:0", "claude-3-opus-20240229",
                      "bedrock/anthropic.claude-opus-4-1", "Opus", "claude-fable-5", "gpt-6-luna"):
            with self.subTest(model=model):
                self.file.write_text(original.replace("haiku", model), encoding="utf-8")
                ok, why = guard.decision(self.payload(), self.root)
                self.assertFalse(ok)
                self.assertIn("Premium", why)

    def test_guard_has_no_private_premium_list(self):
        source = (Path(guard.__file__)).read_text(encoding="utf-8")
        self.assertNotIn("claude-opus", source)
        self.assertIn("is_allowed_subagent_model", source)

    # --- Opus: allowed only under the user's signed approval (opusApproval) ---

    def pin(self, path, model, effort="high"):
        """Rewrite model/effort in a profile; returns its new sha."""
        lines = [("model: " + model) if line.startswith("model: ")
                 else ("effort: " + effort) if line.startswith("effort: ") else line
                 for line in path.read_text(encoding="utf-8").split("\n")]
        path.write_text("\n".join(lines), encoding="utf-8")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def advertise(self, models):
        (self.ap / "model-capabilities.json").write_text(json.dumps({
            "provider": "anthropic", "model_selection": True, "models": models}), encoding="utf-8")

    def opus_executor(self, model="opus"):
        """Signed run: the ticket 01 executor profile and its route pinned to `model`, route re-signed."""
        route = self.state["tickets"][0]["routing"]
        route.update(model=model, effort="high", profileSha=self.pin(self.file, model))
        route["sig"] = gate_sign.sign(gate_sign.routing_payload("01", route))
        self.advertise({model: ["high"]})
        self.save()

    def add_profile(self, name, model="opus"):
        path = self.agents / (name + ".md")
        path.write_text("---\nname: %s\ndescription: Test\nmodel: %s\neffort: high\n---\nTask\n"
                        % (name, model), encoding="utf-8")
        self.advertise({model: ["high"]})
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def run_id(self):
        return "%s|%s" % (self.state["slug"], self.state["startedAt"])

    def approve(self, tickets=(), roles=()):
        """Signed like ap.py: sig over {tickets, roles, run}; agentsSig over {opusAgents, run} if any."""
        body = {"tickets": list(tickets), "roles": list(roles)}
        self.state["opusApproval"] = dict(
            body, quotes=[{"at": "2026-11-08T10:00:00", "quote": "да, Opus для 01"}],
            sig=gate_sign.sign(dict(body, run=self.run_id())))
        if "opusAgents" in self.state:
            self.state["opusApproval"]["agentsSig"] = gate_sign.sign(
                {"opusAgents": self.state["opusAgents"], "run": self.run_id()})
        self.save()

    def denied_as_premium(self, **args):
        ok, why = guard.decision(self.payload(**args), self.root)
        self.assertFalse(ok, why)
        self.assertIn("Premium", why)

    def test_opus_executor_is_denied_without_approval_even_in_a_signed_run(self):
        self.signed_run()
        self.opus_executor()
        self.assertNotIn("opusApproval", self.state)
        self.denied_as_premium()

    def test_opus_executor_runs_only_for_the_approved_ticket(self):
        self.signed_run()
        self.opus_executor()
        self.approve(tickets=["01"])
        ok, why = guard.decision(self.payload(), self.root)
        self.assertTrue(ok, why)
        self.approve(tickets=["02"])  # the approval names another ticket
        self.denied_as_premium()
        self.approve(tickets=[], roles=["reviewer", "repair"])  # roles do not cover a plain executor
        self.denied_as_premium()

    def test_forged_approval_is_denied(self):
        self.signed_run()
        self.opus_executor()
        self.approve(tickets=["01"])
        honest = self.state["opusApproval"]
        forgeries = {
            "garbage signature": dict(honest, sig="0" * 64),
            "no signature": dict(honest, sig=None),
            "signature of another approval": dict(honest, sig=gate_sign.sign({"tickets": ["02"], "roles": []})),
            "tickets widened after signing": dict(honest, tickets=["01", "02"]),
            "roles added after signing": dict(honest, roles=["reviewer"]),
            "tickets swapped after signing": dict(honest, tickets=["02"]),
            "lists replaced by strings": dict(honest, tickets="01"),
            "not a mapping": "yes",
        }
        for label, approval in forgeries.items():
            with self.subTest(label):
                self.state["opusApproval"] = approval
                self.save()
                self.denied_as_premium()
        self.state["opusApproval"] = honest  # the honest one still passes
        self.save()
        self.assertTrue(guard.decision(self.payload(), self.root)[0])

    def test_approval_without_a_signing_key_is_not_accepted(self):
        from unittest import mock
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        with mock.patch.dict(os.environ, {"AUTOPILOT_HOME": home.name}):  # no gate.key here
            route = self.state["tickets"][0]["routing"]
            self.state["tickets"][0]["id"] = "01"
            route.update(model="opus", effort="high", profileSha=self.pin(self.file, "opus"))
            self.advertise({"opus": ["high"]})
            for sig in (None, "0" * 64):
                with self.subTest(sig=sig):
                    self.state["opusApproval"] = {"tickets": ["01"], "roles": [], "quotes": [], "sig": sig}
                    self.save()
                    self.denied_as_premium()

    def test_opus_reviewer_needs_its_role_its_name_and_a_valid_signature(self):
        self.signed_run()
        reviewer = "autopilot-reviewer-opus-x"
        self.add_profile(reviewer)
        self.state["opusAgents"] = {"reviewer": reviewer, "repair": "autopilot-executor-repair-opus-x"}
        self.approve(roles=["reviewer"])
        ok, why = guard.decision(self.payload(agent=reviewer), self.root)
        self.assertTrue(ok, why)
        self.state["opusAgents"]["reviewer"] = "autopilot-reviewer-opus-y"  # not this run's opus reviewer
        self.approve(roles=["reviewer"])
        self.denied_as_premium(agent=reviewer)
        self.state["opusAgents"]["reviewer"] = reviewer
        for label, approval in {"repair role only": ([], ["repair"]), "task approval only": (["01"], [])}.items():
            with self.subTest(label):
                self.approve(*approval)
                self.denied_as_premium(agent=reviewer)
        self.approve(roles=["reviewer"])
        self.state["opusApproval"]["sig"] = "0" * 64
        self.save()
        self.denied_as_premium(agent=reviewer)
        explorer = "autopilot-explorer-opus-x"  # a role never stretches to another kind of agent
        self.add_profile(explorer)
        self.state["opusAgents"] = {"reviewer": explorer, "repair": reviewer}
        self.approve(roles=["reviewer", "repair"])
        self.denied_as_premium(agent=explorer)
        self.denied_as_premium(agent=reviewer)
        self.approve(roles=["reviewer"])
        del self.state["opusAgents"]  # no opus profiles registered for the run
        self.save()
        self.denied_as_premium(agent=reviewer)

    def test_opus_repair_executor_needs_the_repair_role_and_its_name(self):
        self.signed_run()
        name = "autopilot-executor-repair-opus-x"
        route = {"agentType": name, "provider": "anthropic", "model": "opus", "effort": "high",
                 "profileSha": self.add_profile(name), "verified": True}
        route["sig"] = gate_sign.sign(gate_sign.routing_payload("F1", route))
        self.state["tickets"].append({"id": "F1", "status": "repair", "routing": route})
        self.state["repairAgent"] = {"agentType": name}
        self.state["opusAgents"] = {"reviewer": "autopilot-reviewer-opus-x", "repair": name}
        self.approve(roles=["repair"])  # no task id: the role covers every fix ticket
        ok, why = guard.decision(self.payload(agent=name), self.root)
        self.assertTrue(ok, why)
        self.approve(roles=["reviewer"])
        self.denied_as_premium(agent=name)
        self.approve(roles=["repair"])
        self.state["opusAgents"]["repair"] = "autopilot-executor-repair-opus-y"
        self.save()
        self.denied_as_premium(agent=name)
        self.state["opusAgents"]["repair"] = name
        self.state["opusApproval"]["sig"] = "0" * 64
        self.save()
        self.denied_as_premium(agent=name)

    def test_approval_is_bound_to_the_run(self):
        self.signed_run()
        self.opus_executor()
        body = {"tickets": ["01"], "roles": []}
        for label, signed in {"signed without run": body,
                              "signed for another slug": dict(body, run="other|t0"),
                              "signed for another start": dict(body, run="s|t1")}.items():
            with self.subTest(label):
                self.approve(tickets=["01"])
                self.state["opusApproval"]["sig"] = gate_sign.sign(signed)
                self.save()
                self.denied_as_premium()
        self.approve(tickets=["01"])
        self.assertTrue(guard.decision(self.payload(), self.root)[0])

    def opus_reviewer_run(self):
        self.signed_run()
        reviewer = "autopilot-reviewer-opus-x"
        self.add_profile(reviewer)
        self.state["opusAgents"] = {"reviewer": reviewer, "repair": "autopilot-executor-repair-opus-x"}
        self.approve(roles=["reviewer"])
        return reviewer

    def test_opus_agents_name_needs_a_valid_agents_signature(self):
        reviewer = self.opus_reviewer_run()
        agents = self.state["opusAgents"]
        ok, why = guard.decision(self.payload(agent=reviewer), self.root)
        self.assertTrue(ok, why)
        swapped = dict(agents, reviewer="autopilot-reviewer-opus-y")
        cases = {
            "no agentsSig": None,
            "garbage agentsSig": "0" * 64,
            "agentsSig without run": gate_sign.sign({"opusAgents": agents}),
            "agentsSig of another run": gate_sign.sign({"opusAgents": agents, "run": "other|t0"}),
            "agentsSig over other names": gate_sign.sign({"opusAgents": swapped, "run": self.run_id()}),
            "agentsSig is sig": self.state["opusApproval"]["sig"],
        }
        for label, agents_sig in cases.items():
            with self.subTest(label):
                self.state["opusApproval"]["agentsSig"] = agents_sig
                self.save()
                self.denied_as_premium(agent=reviewer)
        # a name swapped into opusAgents after signing no longer matches the signature
        self.approve(roles=["reviewer"])
        self.state["opusAgents"]["reviewer"] = "autopilot-reviewer-opus-y"
        self.add_profile("autopilot-reviewer-opus-y")
        self.save()
        self.denied_as_premium(agent="autopilot-reviewer-opus-y")

    def test_ticket_route_needs_no_agents_signature(self):
        self.signed_run()
        self.opus_executor()
        self.state["opusAgents"] = {"reviewer": "autopilot-reviewer-opus-x",
                                    "repair": "autopilot-executor-repair-opus-x"}
        self.approve(tickets=["01"])
        del self.state["opusApproval"]["agentsSig"]
        self.save()
        ok, why = guard.decision(self.payload(), self.root)
        self.assertTrue(ok, why)
        self.state["opusApproval"]["sig"] = "0" * 64  # but the route still needs a valid sig
        self.save()
        self.denied_as_premium()

    def opus_repair_run(self, *tickets):
        """Signed run with the opus repair profile registered and `tickets` = [(id, status)] routed to it."""
        self.signed_run()
        name = "autopilot-executor-repair-opus-x"
        route = {"agentType": name, "provider": "anthropic", "model": "opus", "effort": "high",
                 "profileSha": self.add_profile(name), "verified": True}
        for tid, status in tickets:
            self.state["tickets"].append({"id": tid, "status": status, "routing": dict(
                route, sig=gate_sign.sign(gate_sign.routing_payload(tid, route)))})
        self.state["opusAgents"] = {"reviewer": "autopilot-reviewer-opus-x", "repair": name}
        self.approve(roles=["repair"])
        return name

    def test_opus_repair_runs_for_one_active_fix_ticket_without_repair_agent(self):
        for tickets in ([("F1", "in-progress")], [("F1", "done"), ("F2", "repair")]):
            with self.subTest(tickets=tickets):
                self.setUp()
                name = self.opus_repair_run(*tickets)  # opusAgents.repair alone stands for repairAgent
                self.assertNotIn("repairAgent", self.state)
                ok, why = guard.decision(self.payload(agent=name), self.root)
                self.assertTrue(ok, why)

    def test_opus_repair_is_denied_for_a_plain_or_a_second_active_ticket(self):
        for tickets in ([("02", "in-progress")], [("02", "repair")], [("F1", "pending")],
                        [("F1", "in-progress"), ("F2", "repair")], [("F1", "review")], []):
            with self.subTest(tickets=tickets):
                self.setUp()
                name = self.opus_repair_run(*tickets)
                ok, why = guard.decision(self.payload(agent=name), self.root)
                self.assertFalse(ok)
                self.assertIn("approved Autopilot task", why)

    def test_fable_is_denied_even_with_a_valid_approval(self):
        self.signed_run()
        reviewer = "autopilot-reviewer-opus-x"
        self.state["opusAgents"] = {"reviewer": reviewer, "repair": "autopilot-executor-repair-opus-x"}
        self.approve(tickets=["01"], roles=["reviewer", "repair"])
        for model in ("fable", "claude-fable-5", "us.anthropic.claude-fable-5-v1:0", "opusplan",
                      "claude-opus-4-1/haiku", "claude-fable-5/claude-opus-4"):
            with self.subTest(model=model):
                self.opus_executor(model)
                self.denied_as_premium()
                self.add_profile(reviewer, model)
                self.denied_as_premium(agent=reviewer)

    def test_every_opus_spelling_passes_the_shared_allowlist_under_approval(self):
        self.signed_run()
        self.approve(tickets=["01"])
        for model in ("us.anthropic.claude-opus-4-1-20250805-v1:0", "claude-3-opus-20240229",
                      "bedrock/anthropic.claude-opus-4-1", "Opus"):
            with self.subTest(model=model):
                self.opus_executor(model)
                ok, why = guard.decision(self.payload(), self.root)
                self.assertTrue(ok, why)

    def test_approval_of_one_ticket_does_not_cover_another_sharing_the_profile(self):
        self.signed_run()
        self.opus_executor()
        first = self.state["tickets"][0]["routing"]
        first["verified"] = False  # ticket 01 is approved but its route is not the verified one
        first["sig"] = gate_sign.sign(gate_sign.routing_payload("01", first))
        second = dict(first, verified=True)
        second["sig"] = gate_sign.sign(gate_sign.routing_payload("02", second))
        self.state["tickets"].append({"id": "02", "routing": second})
        self.approve(tickets=["01"])
        self.denied_as_premium()

    def test_approval_does_not_weaken_the_other_checks(self):
        self.signed_run()
        self.opus_executor()
        self.approve(tickets=["01"])
        self.assertTrue(guard.decision(self.payload(), self.root)[0])
        original = self.file.read_text(encoding="utf-8")
        self.file.write_text(original + "extra\n", encoding="utf-8")
        self.assertIn("changed since", guard.decision(self.payload(), self.root)[1])
        self.file.write_text(original, encoding="utf-8")
        self.advertise({"haiku": ["low"]})
        self.assertIn("advertised", guard.decision(self.payload(), self.root)[1])
        self.advertise({"opus": ["high"]})
        self.assertIn("overrides", guard.decision(self.payload(model="sonnet"), self.root)[1])
        self.state["tickets"][0]["routing"]["score"] = 99  # forged route field, old signature
        self.save()
        self.assertIn("signature", guard.decision(self.payload(), self.root)[1])

    def test_state_with_bom_and_trailing_semicolon_is_read(self):
        body = "window.STATE =\n" + json.dumps(self.state) + ";"
        (self.ap / "state.js").write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))
        ok, why = guard.decision(self.payload(), self.root)
        self.assertTrue(ok, why)

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
        self.assertEqual(len(content["hooks"]["PreToolUse"]), 3)  # Agent|Task + write tools + Bash

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
        self.assertEqual(len(guards), 3)
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

    def repair_run(self, *statuses):
        """Fix tickets F1, F2… share the run's pre-registered repair executor (T17)."""
        name = "autopilot-executor-repair-2026-10-30-run"
        profile = self.agents / (name + ".md")
        profile.write_text(self.file.read_text(encoding="utf-8").replace(self.name, name),
                           encoding="utf-8")
        route = {"agentType": name, "provider": "anthropic", "model": "haiku",
                 "effort": "low", "verified": True,
                 "profileSha": hashlib.sha256(profile.read_bytes()).hexdigest()}
        self.state["repairAgent"] = dict(route)
        self.state["tickets"] += [{"id": "F%d" % n, "status": status, "routing": dict(route)}
                                  for n, status in enumerate(statuses, 1)]
        self.save()
        return name

    def test_repair_executor_allowed_only_for_the_active_fix_ticket(self):
        for statuses in (("in-progress",), ("done", "in-progress"), ("repair",)):
            with self.subTest(statuses=statuses):
                self.setUp()
                ok, why = guard.decision(self.payload(agent=self.repair_run(*statuses)),
                                         self.root)
                self.assertTrue(ok, why)

    def test_repair_executor_denied_without_one_active_fix_ticket(self):
        for statuses in ((), ("pending",), ("done",), ("review",), ("failed", "pending"),
                         ("in-progress", "in-progress")):
            with self.subTest(statuses=statuses):
                self.setUp()
                ok, why = guard.decision(self.payload(agent=self.repair_run(*statuses)),
                                         self.root)
                self.assertFalse(ok)
                self.assertIn("approved Autopilot task", why)

    def test_shared_executor_without_repair_registration_stays_denied(self):
        name = self.repair_run("done", "in-progress")
        del self.state["repairAgent"]
        self.save()
        ok, why = guard.decision(self.payload(agent=name), self.root)
        self.assertFalse(ok)

    def test_real_hook_subprocess_allows_unrelated_project(self):
        (self.ap / "state.js").unlink()
        result = self.run_real_hook(self.payload(agent="Explore"))
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
