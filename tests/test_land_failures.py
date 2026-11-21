"""Красный `ticket NN land` печатает имена упавших тестов и хвост вывода (T01).

Запуск:  python -m unittest discover -s tests -p test_land_failures.py
"""

import unittest

import test_one_command as T

CHECK = r'''import os, sys
mode = open(os.path.join(os.path.dirname(__file__), "check.mode")).read().strip()
if mode == "unittest":
    print("ERROR: test_b (mod.Beta)\nTraceback x\nFAIL: test_a (mod.Alpha)\nFAIL: test_a (mod.Alpha)\n"
          "Ran 4 tests in 0.1s\n\nFAILED (failures=1, errors=1)", file=sys.stderr)
    sys.exit(1)
elif mode == "many":
    print("\n".join("FAIL: test_%d (m.C)" % n for n in range(23)) + "\nRan 30 tests in 1s\n\nFAILED (failures=23)")
    sys.exit(1)
elif mode == "plain":
    print("Ran 2 tests in 0.1s\n\nFAILED (failures=1)")
    sys.exit(1)
print("Ran 3 tests in 0.001s\n\nOK", file=sys.stderr)
'''


class LandFailures(T.Project):
    plan, land, work = T.Land.plan, T.Land.land, T.Land.work

    def setUp(self):
        super().setUp()
        self.put(".autopilot/check.py", CHECK)
        self.plan()
        self.work()

    def red(self, mode):
        self.mode(mode)
        head = self.head()
        code, out = self.land()
        self.assertEqual(code, 2, out)
        self.assertEqual(self.head(), head)
        return out.replace("\r\n", "\n")

    def test_names_and_tail_are_printed_once_in_output_order(self):
        out = self.red("unittest")
        self.assertIn("упавшие тесты (до 20):", out)
        self.assertIn("  - ERROR: test_b (mod.Beta)\n  - FAIL: test_a (mod.Alpha)\n", out)
        self.assertEqual(out.count("- FAIL: test_a (mod.Alpha)"), 1)
        self.assertIn("хвост вывода (последние 15 строк):", out)
        self.assertIn("  FAILED (failures=1, errors=1)", out)

    def test_more_than_twenty_names_are_cut(self):
        out = self.red("many")
        self.assertIn("  - FAIL: test_19 (m.C)", out)
        self.assertNotIn("  - FAIL: test_20 (m.C)", out)
        self.assertIn("… и ещё 3", out)

    def test_no_fail_lines_means_no_names_block_but_a_tail(self):
        out = self.red("plain")
        self.assertNotIn("упавшие тесты", out)
        self.assertIn("хвост вывода", out)
        self.assertIn("FAILED (failures=1)", out)

    def test_green_output_is_unchanged(self):
        code, out = self.land()
        self.assertEqual(code, 0, out)
        self.assertNotIn("хвост вывода", out)


if __name__ == "__main__":
    unittest.main()
