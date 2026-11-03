"""SKILL.md must pre-approve only the ap.py bookkeeping CLI via allowed-tools."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "autopilot" / "SKILL.md"
DOC_FILES = ("README.md", "README.ru.md", "README.de.md",
             "docs/autopilot/gui-clients.md", "docs/autopilot/worktrees.md",
             "docs/autopilot/controller.md", "docs/autopilot/model-routing.md")


def frontmatter_lines():
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md has no frontmatter"
    end = lines.index("---", 1)
    return lines[1:end]


class SkillAllowedToolsTests(unittest.TestCase):
    def setUp(self):
        self.lines = frontmatter_lines()
        self.value = None
        for line in self.lines:
            if line.startswith("allowed-tools:"):
                self.value = line.split(":", 1)[1].strip()
        self.assertIsNotNone(self.value, "allowed-tools key missing from SKILL.md frontmatter")

    def rules(self):
        parts = self.value.split(") ")
        return [p if p.endswith(")") else p + ")" for p in parts if p.strip()]

    def test_allowed_tools_has_at_least_one_rule(self):
        self.assertGreaterEqual(len(self.rules()), 1)

    def test_every_rule_is_bash_ap_py_only(self):
        for rule in self.rules():
            with self.subTest(rule=rule):
                self.assertTrue(rule.startswith("Bash("), rule)
                self.assertRegex(rule, r"\.autopilot/(ap|controller)\.py")

    def test_no_wildcard_bash_rule(self):
        self.assertNotIn("Bash(*)", self.rules())

    def test_every_documented_launch_is_covered_by_a_rule(self):
        rules = set(self.rules())
        # Both scripts under all three launchers must be pre-approved.
        for script in ("ap.py", "controller.py"):
            for launcher in ("python", "python3", "py -3"):
                self.assertIn("Bash(%s .autopilot/%s *)" % (launcher, script), rules)
        launch = re.compile(r"\b(python3?|py -3(?:\.\d+)?)\s+(\.autopilot/(?:ap|controller)\.py)\b")
        for name in DOC_FILES:
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("py -3.13", text, name)
            for launcher, script in launch.findall(text):
                with self.subTest(doc=name, launch=launcher + " " + script):
                    self.assertIn("Bash(%s %s *)" % (launcher, script), rules)


if __name__ == "__main__":
    unittest.main()
