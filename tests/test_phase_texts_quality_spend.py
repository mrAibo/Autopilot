"""R04, R08, R05-R06: ключевые фразы в правленых фазах, выжимках и промпте исполнителя."""
import os
import unittest

SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "autopilot")

# (файл, фраза): без неё правка потеряна.
PHRASES = [
    ("phases/3-spec.md", "narrow questions"),
    ("phases/short/3-spec.md", "narrow questions"),
    ("phases/short/3-spec.md", "context-pack.md"),
    ("prompts/executor.md", "**первым**"),
    ("prompts/executor.md", "по необходимости дочитай сам"),
    ("phases/8-final.md", "**known**, not 🔴"),
    ("phases/short/8-final.md", "**known**"),
    ("phases/short/8-final.md", "no second round"),
    ("phases/4-plan.md", "Целевая проверка"),
    ("phases/short/4-plan.md", "Целевая проверка"),
    ("phases/5-subagents.md", "Целевая проверка"),
    ("phases/short/5-subagents.md", "Целевая проверка"),
]
FORBIDDEN = [("phases/3-spec.md", "study the whole project\n"), ("phases/short/3-spec.md", "explore the whole project")]


def read(rel):
    with open(os.path.join(SKILL, *rel.split("/")), encoding="utf-8") as f:
        return f.read()


class PhaseTexts(unittest.TestCase):
    def test_key_phrases_present(self):
        for rel, phrase in PHRASES:
            self.assertIn(phrase, read(rel), "%s: нет «%s»" % (rel, phrase))

    def test_no_whole_project_exploration(self):
        for rel, phrase in FORBIDDEN:
            self.assertNotIn(phrase, read(rel), rel)

    def test_blindness_untouched(self):
        # слепота: спека не показывается проверяющему
        self.assertIn("`spec.md`, `manifest.md`, tickets", read("phases/8-final.md"))


if __name__ == "__main__":
    unittest.main()
