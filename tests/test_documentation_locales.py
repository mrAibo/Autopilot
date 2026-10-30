"""Offline documentation contract for three localized README files and recovery."""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("README.md", "README.ru.md", "README.de.md")
LEGACY_BRIEF = "\u0431\u0440\u0438\u0444.md"


class DocumentationLocalesTests(unittest.TestCase):
    def test_original_brief_uses_latin_filename_without_losing_file(self):
        self.assertTrue((ROOT / "brief.md").is_file())
        self.assertFalse((ROOT / LEGACY_BRIEF).exists())
        self.assertGreater((ROOT / "brief.md").stat().st_size, 2000)
        for name in (*LOCALES, "docs/autopilot/scope-and-labs.md"):
            with self.subTest(name=name):
                content = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn("brief.md", content)
                self.assertNotIn(LEGACY_BRIEF, content)

    def test_three_way_language_navigation(self):
        for name in LOCALES:
            page = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("English", page)
                self.assertIn("Русский", page)
                self.assertIn("Deutsch", page)
                for sibling in LOCALES:
                    if sibling != name:
                        self.assertIn(sibling, page)

    def test_existing_project_and_interrupted_run_steps_are_translated(self):
        required = ("/autopilot", "brief.md", ".autopilot/state.js",
                    "AGENTS.md", "CLAUDE.md", "PROGRESS.md",
                    "git status", "ap.py commits", "init",
                    "0-resume.md", "reopen")
        for name in LOCALES:
            text = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                for term in required:
                    self.assertIn(term, text, (name, term))
                self.assertIn("git reset --hard", text)
        self.assertIn("## Ein vorhandenes Projekt weiterentwickeln",
                      (ROOT / "README.de.md").read_text(encoding="utf-8"))
        self.assertIn("## Как агент возобновляет работу после обрыва",
                      (ROOT / "README.ru.md").read_text(encoding="utf-8"))
        self.assertIn("## Resume when an agent or chat is interrupted",
                      (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_readmes_have_same_heading_structure(self):
        counts = {}
        for name in LOCALES:
            text = (ROOT / name).read_text(encoding="utf-8")
            counts[name] = (len(re.findall(r"(?m)^## ", text)),
                            len(re.findall(r"(?m)^### ", text)))
        self.assertEqual(len(set(counts.values())), 1, counts)

    def test_local_german_links_refer_to_actual_files(self):
        text = (ROOT / "README.de.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", text)
        local_links = [x.split("#", 1)[0] for x in links
                       if x and not x.startswith(("http:", "https:", "#"))]
        self.assertGreaterEqual(len(local_links), 14)
        for path in local_links:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), "Broken local link: " + path)

    def test_agent_recovers_by_saved_state_not_chat_or_reset(self):
        resume = (ROOT / "skills/autopilot/phases/0-resume.md").read_text(
            encoding="utf-8")
        skill = (ROOT / "skills/autopilot/SKILL.md").read_text(
            encoding="utf-8")
        for word in (".autopilot/state.js", "commits", "git status",
                     "no other active writer", "Do not", "reopen",
                     "PROGRESS.md"):
            self.assertIn(word, resume)
        self.assertIn("An unfinished", skill)
        self.assertIn("0-resume.md", skill)
        self.assertIn("<YYYY-MM-DD>-brief.md", skill)

    def test_230_scoped_codex_release_and_claude_limits(self):
        skill = (ROOT / "skills/autopilot/SKILL.md").read_text(encoding="utf-8")
        claude = (ROOT / "docs/autopilot/claude-code.md").read_text(encoding="utf-8")
        self.assertIn('version: "2.5.0"', skill)
        for name in LOCALES:
            page = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("2.4.0", page)
            self.assertIn("docs/autopilot/claude-code.md", page)
        for claim in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE",
                      "CLAUDE_CODE_EFFORT_LEVEL", "live-qualified",
                      "subscription", "model-capabilities.json"):
            self.assertIn(claim, claude)
        self.assertIn("limited sequential-host",
                      (ROOT / "docs/autopilot/release-readiness.md").read_text(encoding="utf-8"))

    def test_release_readiness_matrix_evidence_links_and_locales(self):
        path = ROOT / "docs/autopilot/release-readiness.md"
        self.assertTrue(path.is_file())
        page = path.read_text(encoding="utf-8")
        for req in ("R01", "R02", "R03", "R04", "R05", "R06"):
            self.assertIn(req, page)
        for claim in ("NO-GO", "BLOCKED", "ChatGPT", "multi_agent_v2=false",
                      "Краткий вывод", "Kurzfazit"):
            self.assertIn(claim, page)
        # The regression count advances as tests are added; require a
        # concrete measured total without freezing a stale release snapshot.
        self.assertRegex(page, r"full local Windows Python 3\.13 regression \*\*\d+/\d+\*\*")
        for target in re.findall(r"\]\(([^)]+)\)", page):
            if not target or target.startswith(("http:", "https:", "#")):
                continue
            rel = target.split("#", 1)[0]
            with self.subTest(target=target):
                self.assertTrue((path.parent / rel).is_file(),
                                "Broken release evidence link: " + target)
        for name in LOCALES:
            with self.subTest(name=name):
                self.assertIn("docs/autopilot/release-readiness.md",
                              (ROOT / name).read_text(encoding="utf-8"))

    def test_automatic_model_and_effort_plan_docs_are_explicit(self):
        phase = (ROOT / "skills/autopilot/phases/4-plan.md").read_text(
            encoding="utf-8")
        guide = (ROOT / "docs/autopilot/model-routing.md").read_text(
            encoding="utf-8")
        dashboard = (ROOT / "skills/autopilot/phases/dashboard-template.html").read_text(
            encoding="utf-8")
        for text in (phase, guide):
            self.assertIn("plan-models", text)
            self.assertIn("--apply", text)
            self.assertIn("Effort", text)
            self.assertIn("Phase 4", text)
        self.assertIn("plannedRouting", guide)
        self.assertIn("No verified host capabilities", guide)
        self.assertIn("planned-model-routes", dashboard)
        for language in LOCALES:
            page = (ROOT / language).read_text(encoding="utf-8")
            self.assertIn("plan-models", page)
            self.assertIn("docs/autopilot/model-routing.md", page)

    def test_sequential_host_docs_show_limits_in_all_locales(self):
        doc_path = ROOT / "docs/autopilot/sequential-host.md"
        self.assertTrue(doc_path.is_file())
        page = doc_path.read_text(encoding="utf-8")
        for claim in ("--sequential-host", "--max-parallel 1", "worktree 01 verify",
                      "No provider model is invoked", "effort", "spend_guard"):
            self.assertIn(claim.lower(), page.lower())
        self.assertNotIn("gui_bridge.py --root . --ticket 01 --execute", page)
        for name in LOCALES:
            self.assertIn("docs/autopilot/sequential-host.md",
                          (ROOT / name).read_text(encoding="utf-8"))
        phase = "".join((ROOT / "skills/autopilot/phases" / n).read_text(
            encoding="utf-8") for n in ("5-subagents.md", "5-host-codex.md"))
        self.assertIn("unconditionally", phase)
        self.assertNotRegex(phase, r"(?m)^\\?`?python .autopilot/gui_bridge.py.*--execute")
        dashboard = (ROOT / "skills/autopilot/phases/dashboard-template.html").read_text(
            encoding="utf-8")
        self.assertIn("sequential-host-notice", dashboard)
        self.assertIn("no child agent is created", dashboard)

    def test_gui_bridge_docs_do_not_offer_disabled_paid_command(self):
        guide = (ROOT / "docs/autopilot/gui-cli-bridge.md").read_text(
            encoding="utf-8")
        guard = (ROOT / "docs/autopilot/spend-guard.md").read_text(
            encoding="utf-8")
        clients = (ROOT / "docs/autopilot/gui-clients.md").read_text(
            encoding="utf-8")
        for term in ("execution is presently disabled", "assert_enforced_cap",
                     "read-only"):
            self.assertIn(term.lower(), guide.lower())
        self.assertIn("refuse all real provider model invocations", guard)
        self.assertIn("disabled by the", clients)
        # Live execution may be mentioned as explicitly denied, but must not
        # appear as a runnable PowerShell code line in the usage example.
        self.assertNotRegex(guide, r"(?m)^py -3\.13 .*--execute")

    def test_phase5_routes_to_host_files(self):
        shared = (ROOT / "skills/autopilot/phases/5-subagents.md").read_text(encoding="utf-8")
        self.assertIn("Then read `5-host-claude.md` if running in Claude Code, "
                      "`5-host-codex.md` if in Codex.", shared)
        for name in ("5-host-claude.md", "5-host-codex.md"):
            self.assertTrue((ROOT / "skills/autopilot/phases" / name).is_file(), name)

    def test_phase5_claude_host_rules(self):
        text = (ROOT / "skills/autopilot/phases/5-host-claude.md").read_text(encoding="utf-8")
        for needle in ("claude_agent_guard.py", "claude_attest.py", "/subtask"):
            self.assertIn(needle, text)

    def test_plan_then_new_chat_handoff(self):
        phases = ROOT / "skills/autopilot/phases"
        plan = (phases / "4-plan.md").read_text(encoding="utf-8")
        self.assertIn("fresh chat", plan)
        self.assertIn("/autopilot", plan)
        self.assertIn("never a new stop", plan)
        resume = (phases / "0-resume.md").read_text(encoding="utf-8")
        self.assertIn("Plan approved, build not started", resume)
        self.assertIn("stage build", resume)
        for name in LOCALES:
            self.assertIn("claude --model sonnet",
                          (ROOT / name).read_text(encoding="utf-8"), name)
        self.assertIn("never at T0", plan)

    def test_strict_claude_registers_agents_then_requires_new_chat(self):
        # T16: agents created mid-session are "Agent type not found" in Claude Code.
        phases = ROOT / "skills/autopilot/phases"
        plan = (phases / "4-plan.md").read_text(encoding="utf-8")
        section = plan.split("## Strict Claude Code run", 1)[1].split("\n## ", 1)[0]
        for needle in ("plan-models --provider anthropic", "--apply",
                       "claude_agent_guard.py --install-hook", "claude_attest.py --install-hook",
                       "roleAgents", "ask stop", "required", "new session",
                       "/autopilot", "general-purpose", "full"):
            self.assertIn(needle, section)
        resume = (phases / "0-resume.md").read_text(encoding="utf-8")
        for needle in ("Strict Claude Code run", "roleAgents", "Agent type not found",
                       "general-purpose", "ticket NN reset"):
            self.assertIn(needle, resume)
        host = (phases / "5-host-claude.md").read_text(encoding="utf-8")
        for role in ("roleAgents.reviewer", "roleAgents.acceptance", "roleAgents.explorer"):
            self.assertIn(role, host)
        for name in ("6-review.md", "8-final.md"):
            self.assertIn("roleAgents", (phases / name).read_text(encoding="utf-8"), name)
        guide = (ROOT / "docs/autopilot/claude-code.md").read_text(encoding="utf-8")
        self.assertIn("session start", guide)
        for name in LOCALES:
            self.assertIn("/autopilot", (ROOT / name).read_text(encoding="utf-8"))
        self.assertIn("required", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
