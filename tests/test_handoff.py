"""`ap.py handoff` (ADR 0034): после коммита плана — стоп ради нового чата, если контекст выше порога."""
import os
import unittest
from pathlib import Path

import test_ap


class Handoff(unittest.TestCase):
    def setUp(self):
        self.h = test_ap.Run("test_skip_needs_a_reason")
        self.h.setUp()
        self.addCleanup(self.h.tearDown)

    def planned(self):
        h = self.h
        h.plan()
        h.ap("tickets")
        open(os.path.join(h.root, "x.txt"), "w").close()
        h.git("add", "-A")
        h.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "план")
        h.ap("set", "baseCommit=" + h.git("rev-parse", "--short", "HEAD").stdout.strip())

    def test_stops_above_threshold_and_is_read_only(self):
        self.planned()
        code, out = self.h.ap("handoff", "--tokens", "200000")
        self.assertEqual(code, 3, out)
        self.assertIn("/autopilot", out)
        self.assertEqual([t["status"] for t in self.h.state()["tickets"]], ["pending", "pending"])

    def test_continues_below_threshold(self):
        self.planned()
        self.assertEqual(self.h.ap("handoff", "--tokens", "100000")[0], 0)

    def test_refuses_without_plan_commit(self):
        self.h.plan()
        self.h.ap("tickets")
        code, out = self.h.ap("handoff", "--tokens", "200000")
        self.assertEqual(code, 1, out)
        self.assertIn("baseCommit", out)

    def test_strict_run_keeps_its_own_step(self):
        self.planned()
        self.h.edit_state(strictRouting=True)
        self.assertEqual(self.h.ap("handoff", "--tokens", "200000")[0], 0)

    def test_dirty_autopilot_gives_code_1(self):
        self.planned()
        open(os.path.join(self.h.dir, "notes-late.md"), "w").close()
        code, out = self.h.ap("handoff", "--tokens", "200000")
        self.assertEqual(code, 1, out)
        self.assertIn("не закоммичено", out)

    def test_base_commit_not_ancestor_gives_code_1(self):
        self.planned()
        self.h.git("checkout", "-q", "--orphan", "other")
        self.h.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
        code, out = self.h.ap("handoff", "--tokens", "200000")
        self.assertEqual(code, 1, out)
        self.assertIn("не предок", out)

    def test_started_build_and_single_ticket_continue(self):
        self.planned()
        self.h.edit_state(tickets=[dict(t, status="done") for t in self.h.state()["tickets"]])
        self.assertEqual(self.h.ap("handoff", "--tokens", "200000")[0], 0)
        self.h.edit_state(tickets=self.h.state()["tickets"][:1])
        self.h.edit_state(tickets=[dict(t, status="pending") for t in self.h.state()["tickets"]])
        self.assertEqual(self.h.ap("handoff", "--tokens", "200000")[0], 0)

    def test_threshold_from_env_and_missing_value_is_refused(self):
        self.planned()
        from unittest import mock
        with mock.patch.dict(os.environ, {"AUTOPILOT_CONTEXT_HINT": "300000"}):
            self.assertEqual(self.h.ap("handoff", "--tokens", "200000")[0], 0)
        with mock.patch.dict(os.environ, {"AUTOPILOT_CONTEXT_HINT": "0"}):
            self.assertEqual(self.h.ap("handoff", "--tokens", "900000")[0], 0)
        self.assertNotEqual(self.h.ap("handoff", "--tokens")[0], 0)
        self.assertNotEqual(self.h.ap("handoff", "--tokens", "abc")[0], 0)

    def test_read_only_and_no_token_in_output_and_new_window_hint(self):
        self.planned()
        path = os.path.join(self.h.a, "state.js")
        before = Path(path).read_bytes()
        code, out = self.h.ap("handoff", "--tokens", "200000")
        self.assertEqual(Path(path).read_bytes(), before)
        self.assertNotIn("?t=", out)
        self.assertIn("продолжает новое окно", out)

    def test_phase_names_the_command(self):
        with open(os.path.join(test_ap.SKILL, "phases", "4-plan.md"), encoding="utf-8") as f:
            self.assertIn("ap.py handoff", f.read())


if __name__ == "__main__":
    unittest.main()
