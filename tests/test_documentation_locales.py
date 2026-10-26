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


if __name__ == "__main__":
    unittest.main()
