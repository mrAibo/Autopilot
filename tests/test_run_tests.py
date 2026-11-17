"""Запускатель tools/run-tests.py: дробление на группы и сложение итогов (весь набор не гоняется)."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(HERE, "..", "tools", "run-tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


class Splitting(unittest.TestCase):
    FOUND = {
        "test_a.Big": ([f"test_{i}" for i in range(20)], False),
        "test_a.Small": (["test_x", "test_y"], False),
        "test_b.Port": (["test_p"], True),
    }

    def test_big_class_is_chunked_and_serial_class_is_kept_apart(self):
        parallel, serial = rt.make_units(self.FOUND)
        ids = [i for _, g in parallel for i in g]
        self.assertEqual(len([i for i in ids if i.startswith("test_a.Big.")]), 20)
        self.assertIn("test_a.Small", ids)
        self.assertEqual([g for _, g in serial], [["test_b.Port"]])
        self.assertNotIn("test_b.Port", ids)

    def test_plan_covers_every_id_once_in_at_most_n_groups(self):
        parallel, _ = rt.make_units(self.FOUND)
        groups = rt.plan(parallel, 3)
        flat = [i for g in groups for i in g]
        self.assertLessEqual(len(groups), 3)
        self.assertEqual(sorted(flat), sorted(i for _, g in parallel for i in g))

    def test_serial_attribute_on_a_real_class_is_read(self):
        class Marked(unittest.TestCase):
            serial = True

            def test_one(self):
                pass

        self.assertTrue(getattr(Marked, "serial", False))
        self.assertIn("test_ap_audit.Server", rt.SERIAL)  # порт bind(0) → дочернему процессу


class Summary(unittest.TestCase):
    def test_parse_ok_and_failed(self):
        self.assertEqual(rt.parse_summary("Ran 5 tests in 1.0s\n\nOK (skipped=2)\n"),
                         {"ran": 5, "failures": 0, "errors": 0, "skipped": 2, "unexpected": 0})
        self.assertEqual(rt.parse_summary("Ran 1 test in 0.1s\n\nFAILED (failures=1, errors=2)\n"),
                         {"ran": 1, "failures": 1, "errors": 2, "skipped": 0, "unexpected": 0})
        self.assertIsNone(rt.parse_summary("Traceback..."))

    def test_combine_sums_and_counts_a_crashed_process_as_error(self):
        a = {"ran": 5, "failures": 1, "errors": 0, "skipped": 2, "unexpected": 0}
        b = {"ran": 3, "failures": 0, "errors": 1, "skipped": 1, "unexpected": 1}
        self.assertEqual(rt.combine([a, b, None]), {"ran": 8, "failures": 1, "errors": 2, "skipped": 3, "unexpected": 1})

    def test_format_matches_unittest(self):
        ok = rt.format_summary({"ran": 9, "failures": 0, "errors": 0, "skipped": 5, "unexpected": 0}, 1.5)
        self.assertEqual(ok, "Ran 9 tests in 1.500s\n\nOK (skipped=5)")
        bad = rt.format_summary({"ran": 9, "failures": 1, "errors": 2, "skipped": 0, "unexpected": 0}, 1.5)
        self.assertTrue(bad.endswith("FAILED (failures=1, errors=2)"))


class WholeRun(unittest.TestCase):
    """Настоящий запуск на временной папке tests: сломанный импорт и «неожиданный успех» — падение."""

    def run_on(self, **modules):
        with tempfile.TemporaryDirectory() as tmp:
            for name, text in modules.items():
                with open(os.path.join(tmp, name + ".py"), "w", encoding="utf-8") as f:
                    f.write(text)
            return subprocess.run([sys.executable, os.path.join(HERE, "..", "tools", "run-tests.py"), "-j", "2", "--dir", tmp],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

    OK = "import unittest\nclass A(unittest.TestCase):\n    def test_a(self): pass\n"

    def test_module_that_fails_to_import_is_an_error_with_a_traceback(self):
        p = self.run_on(test_ok=self.OK, test_broken="import module_that_does_not_exist_xyz\n")
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertRegex(p.stderr, r"FAILED \(.*errors=[1-9]")
        self.assertIn("module_that_does_not_exist_xyz", p.stderr)
        self.assertIn("Traceback", p.stderr)

    def test_unexpected_success_fails_the_run_like_unittest(self):
        ux = "import unittest\nclass U(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_u(self): pass\n"
        p = self.run_on(test_ok=self.OK, test_ux=ux)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertTrue(p.stderr.rstrip().endswith("unexpected successes=1)"), p.stderr)   # итог запускателя, не вывод дочернего

    def test_a_clean_folder_is_ok(self):
        p = self.run_on(test_ok=self.OK)
        self.assertEqual((p.returncode, "OK" in p.stderr), (0, True), p.stderr)

    def test_summary_keeps_unexpected_successes(self):
        text = "Ran 2 tests in 0.1s\n\nFAILED (unexpected successes=1)\n"
        self.assertEqual(rt.parse_summary(text)["unexpected"], 1)


if __name__ == "__main__":
    unittest.main()
