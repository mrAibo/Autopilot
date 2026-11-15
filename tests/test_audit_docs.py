"""Документы аудита 2026-11-15: фазы 3-5, промпт исполнителя, docs/autopilot и счётчик тестов."""

import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, "skills", "autopilot")
sys.path.insert(0, os.path.join(SKILL, "tools"))
import test_count  # noqa: E402


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as stream:
        return stream.read()


class PhaseDocs(unittest.TestCase):
    def test_plan_no_longer_calls_the_planner_class_a_mere_description(self):
        plan = read("skills", "autopilot", "phases", "4-plan.md")
        self.assertNotIn("только описанием", plan)
        self.assertNotIn("descriptive only", plan)

    def test_plan_describes_class_lines_haiku_signs_and_cold_start(self):
        plan = read("skills", "autopilot", "phases", "4-plan.md")
        for needle in ("**Класс:**", "**Причина класса:**", "механический|обычный|сложный",
                       "one zone", "~150", "interfaces.md", "Cold-start threshold", "cheap_code"):
            self.assertIn(needle, plan)

    def test_context_pack_is_written_by_the_scout_and_read_first_by_the_executor(self):
        self.assertIn("context-pack.md", read("skills", "autopilot", "phases", "3-spec.md"))
        self.assertIn("context-pack.md", read("skills", "autopilot", "phases", "5-subagents.md"))
        executor = read("skills", "autopilot", "prompts", "executor.md")
        self.assertRegex(executor, r"context-pack\.md[^\n]*первым")
        self.assertIn("дочитай сам", executor)

    def test_retry_policy_has_one_escalation_and_keeps_the_general_rule(self):
        text = read("docs", "autopilot", "retry-policy.md")
        self.assertIn("Never upgrade a model merely because a command failed", text)
        self.assertIn("ticket 03 retry --cause tests --escalate", text)
        self.assertIn("escalatedFrom", text)

    def test_routing_and_claude_code_docs_cover_profiles_class_dpapi_and_bash_gate(self):
        routing = read("docs", "autopilot", "model-routing.md")
        for needle in ("cheap_read", "cheap_code", "**Класс:**"):
            self.assertIn(needle, routing)
        claude = read("docs", "autopilot", "claude-code.md")
        for needle in ("DPAPI", "dpapi:", "bash_gate", ".claude/agents/"):
            self.assertIn(needle, claude)
        self.assertIn("escalate", read("docs", "autopilot", "run-log.md"))


class TestCount(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-count-")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def put(self, name, text):
        with open(os.path.join(self.root, name), "w", encoding="utf-8", newline="") as stream:
            stream.write(text)

    def get(self, name):
        with open(os.path.join(self.root, name), encoding="utf-8", newline="") as stream:
            return stream.read()

    def test_substitute_replaces_only_the_number_between_markers(self):
        new, hits = test_count.substitute("a <!-- tests:count -->1<!-- /tests:count --> b "
                                          "<!-- tests:count -->old<!-- /tests:count -->", 42)
        self.assertEqual((new, hits), ("a <!-- tests:count -->42<!-- /tests:count --> b "
                                       "<!-- tests:count -->42<!-- /tests:count -->", 2))

    def test_write_updates_marked_files_and_leaves_unmarked_ones_untouched(self):
        marked = "Тестов: <!-- tests:count -->7<!-- /tests:count -->.\r\n"
        plain = "Тестов: 730, без маркеров.\n"
        for name in test_count.FILES:
            self.put(name, plain if name == "README.de.md" else marked)
        done = test_count.write(self.root, 845)
        self.assertEqual(done, {"AGENTS.md": 1, "README.md": 1, "README.ru.md": 1, "README.de.md": 0})
        self.assertEqual(self.get("README.md"), "Тестов: <!-- tests:count -->845<!-- /tests:count -->.\r\n")
        self.assertEqual(self.get("README.de.md"), plain)

    def test_stale_names_files_with_a_wrong_number_or_no_markers(self):
        for name in test_count.FILES:
            self.put(name, "<!-- tests:count -->10<!-- /tests:count -->")
        self.put("README.ru.md", "без маркеров")
        self.put("README.md", "<!-- tests:count -->9<!-- /tests:count -->")
        self.assertEqual(test_count.stale(self.root, 10), ["README.md", "README.ru.md"])

    def test_project_documents_carry_markers_with_a_number(self):
        for name in test_count.FILES:
            self.assertRegex(read(name), r"<!-- tests:count -->\d+<!-- /tests:count -->", name)
        self.assertNotIn("730", read("AGENTS.md"))


if __name__ == "__main__":
    unittest.main()
