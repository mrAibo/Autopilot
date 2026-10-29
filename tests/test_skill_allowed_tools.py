"""SKILL.md must pre-approve only the ap.py bookkeeping CLI via allowed-tools."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "autopilot" / "SKILL.md"


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
                self.assertIn(".autopilot/ap.py", rule)

    def test_no_wildcard_bash_rule(self):
        self.assertNotIn("Bash(*)", self.rules())


if __name__ == "__main__":
    unittest.main()
