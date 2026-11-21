"""`ap.py doc-check` (T04): имена ap.py <cmd> и --flag из CHANGELOG/ADR есть в ap.py.

Запуск:  python -m unittest discover -s tests -p test_doc_check.py
"""
import os
import shutil
import sys
import tempfile
import unittest

import test_ap
import test_one_command as T

sys.path.insert(0, T.TOOLS)
import doc_check  # noqa: E402

AP = os.path.join(T.TOOLS, "ap.py")
BAD = "## Unreleased\n\n- Новое: `ap.py nosuch` и `ap.py doc-check --nosuchflag`.\n"
GOOD = "## Unreleased\n\n- Новое: `ap.py doc-check` и `ap.py ticket --note`.\n"


class Units(unittest.TestCase):
    def test_claimed_takes_only_backticked_names(self):
        text = ("ap.py plain --plain; `ap.py lessons add` и `--zone a/`;\n"
                "`git log --stat`; `ap.py x --y-z`")
        self.assertEqual(doc_check.claimed(text), {"ap.py lessons", "--zone", "ap.py x", "--y-z"})

    def test_absence_statement_is_not_a_claim(self):
        self.assertEqual(doc_check.claimed("Команды `ap.py preset` нет."), set())

    def test_known_reads_commands_and_flags_from_source(self):
        src = 'if cmd == "aaa":\n  x = opt.get("bbb")\nif cmd in ("c-c", "d"):\n  y = opt["e"]\n  z = "--ff"\n'
        self.assertEqual(doc_check.known(src), ({"aaa", "c-c", "d"}, {"--bbb", "--e", "--ff"}))

    def test_real_ap_knows_doc_check_itself(self):
        with open(AP, encoding="utf-8") as f:
            cmds, flags = doc_check.known(f.read())
        self.assertIn("doc-check", cmds)
        self.assertIn("--result", flags)


class OnDisk(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ap-dc-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def put(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path) or self.root, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_invented_names_are_reported(self):
        self.put("CHANGELOG.md", BAD)
        got = doc_check.check(self.root, AP, ["CHANGELOG.md"])
        self.assertEqual(got, ["CHANGELOG.md: --nosuchflag — такого флага нет",
                               "CHANGELOG.md: ap.py nosuch — такой команды нет"])

    def test_real_names_and_files_without_mentions_pass(self):
        self.put("CHANGELOG.md", GOOD)
        self.put("docs/adr/0001-x.md", "# Ничего про команды\n")
        self.assertEqual(doc_check.check(self.root, AP, ["CHANGELOG.md", "docs/adr/0001-x.md"]), [])

    def test_only_the_unreleased_section_of_the_changelog_counts(self):
        self.put("CHANGELOG.md", "## Unreleased\n\n- ок\n\n## 1.0\n\n- старое `ap.py nosuch`\n")
        self.assertEqual(doc_check.check(self.root, AP, ["CHANGELOG.md"]), [])


class Cli(T.Project):
    def test_command_exit_codes(self):
        self.init()
        self.put("CHANGELOG.md", BAD)
        code, out = self.ap("doc-check", "--no-serve")
        self.assertEqual(code, 1, out)
        self.assertIn("ap.py nosuch — такой команды нет", out)
        self.put("CHANGELOG.md", GOOD)
        self.assertEqual(self.ap("doc-check", "--no-serve")[0], 0)

    def test_upgrade_tools_ships_the_module(self):
        self.assertTrue(os.path.exists(os.path.join(T.TOOLS, "doc_check.py")))
        self.assertTrue(os.path.exists(os.path.join(self.a, "doc_check.py")))


class FinishWarning(unittest.TestCase):
    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)
        shutil.copy(os.path.join(T.TOOLS, "doc_check.py"), os.path.join(self.h.a, "doc_check.py"))
        self.h.ready_to_finish()

    def finish(self, changelog):
        with open(os.path.join(self.h.root, "CHANGELOG.md"), "w", encoding="utf-8") as f:
            f.write(changelog)
        return self.h.ap("finish", "--result", "готово")

    def test_finish_warns_but_still_lands(self):
        code, out = self.finish(BAD)
        self.assertEqual(code, 0, out)
        self.assertIn("! doc-check: 2 расхождений", out)
        self.assertTrue(self.h.state()["finishedAt"])

    def test_finish_is_quiet_when_names_match(self):
        code, out = self.finish(GOOD)
        self.assertEqual(code, 0, out)
        self.assertNotIn("doc-check", out)

    def test_broken_module_does_not_break_finish(self):
        with open(os.path.join(self.h.a, "doc_check.py"), "w", encoding="utf-8") as f:
            f.write("raise ValueError('boom')\n")
        code, out = self.finish(BAD)
        self.assertEqual(code, 0, out)
        self.assertNotIn("doc-check", out)


if __name__ == "__main__":
    unittest.main()
