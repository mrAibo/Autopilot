"""Запускатель tools/run-tests.py: дробление на группы и сложение итогов (весь набор не гоняется)."""
import importlib.util
import os
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
                         {"ran": 5, "failures": 0, "errors": 0, "skipped": 2})
        self.assertEqual(rt.parse_summary("Ran 1 test in 0.1s\n\nFAILED (failures=1, errors=2)\n"),
                         {"ran": 1, "failures": 1, "errors": 2, "skipped": 0})
        self.assertIsNone(rt.parse_summary("Traceback..."))

    def test_combine_sums_and_counts_a_crashed_process_as_error(self):
        a = {"ran": 5, "failures": 1, "errors": 0, "skipped": 2}
        b = {"ran": 3, "failures": 0, "errors": 1, "skipped": 1}
        self.assertEqual(rt.combine([a, b, None]), {"ran": 8, "failures": 1, "errors": 2, "skipped": 3})

    def test_format_matches_unittest(self):
        ok = rt.format_summary({"ran": 9, "failures": 0, "errors": 0, "skipped": 5}, 1.5)
        self.assertEqual(ok, "Ran 9 tests in 1.500s\n\nOK (skipped=5)")
        bad = rt.format_summary({"ran": 9, "failures": 1, "errors": 2, "skipped": 0}, 1.5)
        self.assertTrue(bad.endswith("FAILED (failures=1, errors=2)"))


if __name__ == "__main__":
    unittest.main()
