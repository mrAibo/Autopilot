"""Журнал прогона: skills/autopilot/tools/run_log.py (метаданные, без исключений, ротация, сводка)."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "skills", "autopilot", "tools"))
import run_log  # noqa: E402


class RunLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.d = self.temp.name
        self.path = os.path.join(self.d, "run-log.jsonl")

    def rows(self):
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(x) for x in f.read().splitlines()]

    def test_append_writes_one_known_line(self):
        self.assertTrue(run_log.append(self.d, "ticket", run="r1", id="01", act="start",
                                       prompt="секретный промпт", note="заметка"))
        (row,) = self.rows()
        self.assertEqual((row["k"], row["run"], row["id"], row["act"]), ("ticket", "r1", "01", "start"))
        self.assertRegex(row["t"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertEqual(set(row), {"t", "run", "k", "id", "act"})   # чужие поля отброшены

    def test_wait_row_keeps_its_own_kind_field(self):
        self.assertTrue(run_log.append(self.d, "wait", kind="stop", act="start"))
        self.assertEqual((self.rows()[0]["k"], self.rows()[0]["kind"]), ("wait", "stop"))

    def test_long_value_is_cut_and_machine_path_is_replaced(self):
        run_log.append(self.d, "reset", what="ticket", id="01", reason="x" * 500)
        run_log.append(self.d, "reset", what="ticket", id="C:\\Users\\" + "ivan" + "\\proj\\a.py",
                       reason="/home/" + "ivan" + "/x")   # литерал пути не лежит в файле
        long_row, path_row = self.rows()
        self.assertEqual(len(long_row["reason"]), 120)
        self.assertEqual((path_row["id"], path_row["reason"]), ("[path]", "[path]"))

    def test_append_never_raises_and_returns_false(self):
        self.assertFalse(run_log.append(os.path.join(self.d, "нет-такой-папки"), "phase", id="spec"))
        self.assertFalse(run_log.append(self.d, "unknown-kind"))
        self.assertFalse(run_log.append(self.d, "phase", id=object()))      # не сериализуется
        os.mkdir(self.path)                                                  # журнал — каталог
        self.assertFalse(run_log.append(self.d, "phase", id="spec", act="start"))

    def test_rotation_keeps_both_parts_in_order_and_skips_broken_lines(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"k": "phase", "id": "old"}) + "\n" + "{битая строка\n"
                    + " " * run_log.ROTATE_BYTES + "\n")
        self.assertTrue(run_log.append(self.d, "phase", id="new", act="start"))
        self.assertTrue(os.path.exists(os.path.join(self.d, "run-log.1.jsonl")))
        self.assertEqual([r["id"] for r in self.rows()], ["new"])            # свежий файл
        self.assertEqual([r["id"] for r in run_log.read_all(self.d)], ["old", "new"])

    def transcript(self, *lines):
        p = os.path.join(self.d, "t.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return p

    def test_usage_sums_assistant_messages_once_per_message_id(self):
        def msg(i, role, **u):
            return json.dumps({"message": {"id": i, "role": role, "usage": u}})
        same = dict(input_tokens=10, output_tokens=5, cache_read_input_tokens=100,
                    cache_creation_input_tokens=7)
        p = self.transcript(msg("m1", "assistant", **same),
                            msg("m1", "assistant", **same),      # потоковый дубль того же ответа
                            "не json",
                            msg("m2", "assistant", input_tokens=1, output_tokens=2),
                            msg("u1", "user", input_tokens=999))
        self.assertEqual(run_log.usage_from_transcript(p),
                         {"turns": 2, "input": 11, "output": 7, "cache_read": 100, "cache_write": 7})

    def test_usage_is_none_on_missing_broken_or_empty_and_respects_max_bytes(self):
        self.assertIsNone(run_log.usage_from_transcript(os.path.join(self.d, "нет.jsonl")))
        self.assertIsNone(run_log.usage_from_transcript(self.transcript("{", "[]")))
        line = json.dumps({"message": {"id": "a", "role": "assistant", "usage": {"input_tokens": 1}}})
        p = self.transcript(line, line.replace('"a"', '"b"'))
        self.assertEqual(run_log.usage_from_transcript(p, max_bytes=len(line) + 5)["turns"], 1)

    def test_summary_and_share_report(self):
        run = "2026-01-01-secret-slug"
        t = lambda m: "2026-01-01T10:%02d:00+00:00" % m
        rows = [{"k": "phase", "run": run, "t": t(0), "id": "build", "act": "start"},
                {"k": "ticket", "run": run, "t": t(1), "id": "07", "act": "start"},
                {"k": "ticket", "run": run, "t": t(2), "id": "07", "act": "retry", "cause": "tests-failed"},
                {"k": "tests", "run": run, "t": t(3), "passed": 3, "failed": 0, "seconds": 12},
                {"k": "wait", "run": run, "t": t(4), "kind": "stop", "act": "start"},
                {"k": "wait", "run": run, "t": t(6), "kind": "stop", "act": "end"},
                {"k": "executor", "run": run, "t": t(7), "agent_type": "autopilot-executor-07-secret-slug",
                 "turns": 4, "input": 10, "output": 20},
                {"k": "phase", "run": run, "t": t(10), "id": "build", "act": "done"}]
        s = run_log.summarize(rows)
        self.assertEqual(s["phases"][0]["seconds"], 600)
        self.assertEqual((s["tickets"][0]["starts"], s["tickets"][0]["retries"]), (1, 1))
        self.assertEqual(s["waits"], {"count": 1, "seconds": 120})
        full = run_log.render_report(s)
        for word in ("Фазы", "Таски", "Простои", "Токены", run, "07"):
            self.assertIn(word, full)
        shared = run_log.render_report(s, share=True)
        for word in ("Фазы", "Таски", "Простои", "Токены", "executor"):
            self.assertIn(word, shared)
        for hidden in ("secret-slug", "2026-01-01", "07", "T10:", "tests-failed"):
            self.assertNotIn(hidden, shared)

class HardeningTests(unittest.TestCase):
    def test_role_of_maps_profile_names(self):
        for name, role in (("autopilot-executor-x", "executor"), ("autopilot-executor-repair-x", "executor"),
                           ("autopilot-reviewer-x", "reviewer"), ("autopilot-explorer-x", "explorer"),
                           ("autopilot-acceptance-x", "acceptance"), ("other-agent", "agent"), (None, "agent")):
            self.assertEqual(run_log.role_of(name), role, name)

    def test_read_all_stats_counts_unreadable_lines(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, run_log.NAME), "w", encoding="utf-8") as f:
            f.write('{"k": "phase", "run": "r"}\n{"k": "pha\n[1]\n\n{"k": "wait", "run": "r"}\n')
        rows, bad = run_log.read_all_stats(d)
        self.assertEqual((len(rows), bad), (2, 2))
        self.assertEqual(len(run_log.read_all(d)), 2)

    def test_deeply_nested_line_is_unreadable_not_fatal(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, run_log.NAME), "w", encoding="utf-8") as f:
            f.write('{"k": "phase", "run": "r"}\n' + "[" * 200000 + "\n")
        rows, bad = run_log.read_all_stats(d)
        self.assertEqual((len(rows), bad), (1, 1))
        s = run_log.summarize(rows, run="r", skipped=bad)
        self.assertIn("пропущено испорченных строк: 1", run_log.render_report(s))
        tr = os.path.join(d, "t.jsonl")
        with open(tr, "w", encoding="utf-8") as f:
            f.write("[" * 200000 + "\n")
        self.assertIsNone(run_log.usage_from_transcript(tr))

    def test_summarize_skips_malformed_rows_and_counts_them(self):
        rows = [{"k": "phase", "run": "r", "id": ["x"], "act": "start"},
                {"k": "ticket", "run": "r", "id": "01", "act": "fail", "cause": 5},
                {"k": "nope", "run": "r"}, {"k": ["phase"], "run": "r"},
                {"k": "ticket", "run": "r", "id": "02", "act": "start"}]
        s = run_log.summarize(rows, run="r", skipped=1)
        self.assertEqual(s["skipped"], 5)
        self.assertEqual([x["id"] for x in s["tickets"]], ["02"])
        for share in (False, True):
            self.assertIn("пропущено испорченных строк: 5", run_log.render_report(s, share=share))
        self.assertNotIn("пропущено", run_log.render_report(run_log.summarize([rows[-1]], run="r")))

    def test_report_has_role_column_and_old_rows_get_role_from_profile(self):
        rows = [{"k": "executor", "run": "r", "agent_type": "autopilot-reviewer-09-slug", "turns": 1},
                {"k": "executor", "run": "r", "agent_type": "autopilot-executor-09-slug", "role": "explorer"}]
        s = run_log.summarize(rows, run="r")
        self.assertEqual([t["role"] for t in s["tokens"]], ["reviewer", "explorer"])
        full, shared = run_log.render_report(s), run_log.render_report(s, share=True)
        self.assertIn("роль", full)
        self.assertIn("autopilot-reviewer-09-slug", full)
        self.assertIn("reviewer", shared)
        self.assertNotIn("slug", shared)


if __name__ == "__main__":
    unittest.main()
