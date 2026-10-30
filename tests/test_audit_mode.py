"""Contract for the read-only `/autopilot audit` mode (docs-only feature)."""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "autopilot"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class AuditModeTests(unittest.TestCase):
    def setUp(self):
        self.phase = read("skills/autopilot/phases/audit.md")
        self.prompt = read("skills/autopilot/prompts/audit.md")

    def test_skill_routes_audit_to_its_phase(self):
        skill = read("skills/autopilot/SKILL.md")
        self.assertIn("[`phases/audit.md`](phases/audit.md)", skill)
        self.assertIn("instead of every phase below", skill)
        self.assertIn("| `phases/audit.md` — instead of all phases, on `/autopilot audit`", skill)
        self.assertIn("audit[: фокус]", skill.split("\n---", 1)[0])
        for word in ("«аудит»", "«Audit»"):
            self.assertIn(word, skill)
        self.assertIn("phases/audit.md", read("skills/autopilot/phases/0-modes.md"))

    def test_phase_states_read_only_contract_and_report_path(self):
        for needle in ("No edits, no commits", "no installs, no network",
                       ".autopilot/audits/<YYYY-MM-DD>-audit.md",
                       "The only file written", "Read, Grep, Glob",
                       "never its value", "git status --porcelain"):
            self.assertIn(needle, self.phase)
        self.assertIn("The report is not committed", self.phase)

    def test_phase_never_runs_ap_py(self):
        lines = [l for l in self.phase.splitlines() if "ap.py" in l]
        self.assertTrue(lines, "the phase must forbid ap.py explicitly")
        for line in lines:
            self.assertIn("never", line.lower(), line)
        self.assertIn("not `init`", self.phase)
        self.assertNotRegex(self.phase, r"ap\.py (init|stage|set|ticket)\b")

    def test_phase_refuses_with_unfinished_run(self):
        section = self.phase.split("## 1. Before anything", 1)[1].split("\n## ", 1)[0]
        self.assertIn(".autopilot/state.js", section)
        self.assertIn("`finishedAt` is `null`", section)
        self.assertIn("do not start", section)

    def test_cheap_explorers_and_one_strong_verifier(self):
        explorers = self.phase.split("## 3. Explorers", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`cheap` profile", explorers)
        self.assertIn("haiku", explorers)
        self.assertIn("at most 12 findings, 25 lines, 2,500 characters", explorers)
        verify = self.phase.split("## 4. Verification", 1)[1].split("\n## ", 1)[0]
        self.assertIn("**one fresh subagent**", verify)
        self.assertIn("`strong` profile", verify)
        self.assertIn("concrete failure scenario", verify)
        for role in ("## Разведчик", "## Проверяющий"):
            self.assertIn(role, self.prompt)
        self.assertIn("2 500 знаков", self.prompt)

    def test_test_suite_rule_and_no_network_tools_for_subagents(self):
        self.assertIn("run it once, yourself, only when all hold", self.phase)
        self.assertIn("never install them", self.phase)
        self.assertIn("pip-audit", self.prompt)
        self.assertIn("значение никогда", self.prompt)

    def test_report_template_has_ids_checkboxes_and_sections(self):
        template = self.phase.split("```markdown", 1)[1].split("```", 1)[0]
        self.assertRegex(template, r"(?m)^- \[ \] \*\*A01\*\* · `[^`]+:\d+`")
        self.assertRegex(template, r"(?m)^- \[ \] \*\*I01\*\*")
        for heading in ("## Сводка", "## Критично", "## Важно", "## Улучшения",
                        "## Идеи развития", "## Что не проверялось"):
            self.assertIn(heading, template)
        for field in ("Почему важно", "Сценарий", "Работа: S | M | L"):
            self.assertIn(field, template)

    def test_bridge_to_build_uses_only_ticked_items(self):
        self.assertIn("/autopilot .autopilot/audits/", self.phase)
        manifest = read("skills/autopilot/phases/1-manifest.md")
        self.assertIn("**only the ticked items**", manifest)
        self.assertIn("`- [x] **A##**`", manifest)
        self.assertIn("Unticked items are **out of scope**", manifest)
        self.assertIn("Nothing ticked → ask", manifest)

    def test_user_guide_exists_and_links_resolve(self):
        guide = read("docs/autopilot/audit.md")
        self.assertIn("/autopilot audit", guide)
        self.assertIn(".autopilot/audits/", guide)
        for link in re.findall(r"\]\((\.\./[^)]+)\)", guide):
            self.assertTrue((ROOT / "docs/autopilot" / link).resolve().is_file(), link)


if __name__ == "__main__":
    unittest.main()
