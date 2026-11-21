"""`ap.py handoff` (ADR 0034): после коммита плана — стоп ради нового чата, если контекст выше порога."""
import os
import unittest

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

    def test_phase_names_the_command(self):
        with open(os.path.join(test_ap.SKILL, "phases", "4-plan.md"), encoding="utf-8") as f:
            self.assertIn("ap.py handoff", f.read())


if __name__ == "__main__":
    unittest.main()
