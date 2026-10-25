"""Host controller must never silently launch a model or accept fake tests."""
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                        "skills" / "autopilot" / "tools"))
import controller


def task(tid, status="pending", zone=None, deps=None, wt=None, evidence=None):
    d = {"id": tid, "status": status, "zone": zone or ["src/" + tid + ".py"],
         "wave": 1, "blockedBy": deps or [],
         "routing": {"verified": True}}
    if wt is not None:
        d["worktree"] = wt
    if evidence is not None:
        d["testEvidence"] = evidence
    return d


def ledger(*tickets, **fields):
    state = {"tickets": list(tickets), "isolateTickets": True,
             "strictRouting": True, "usageEvents": []}
    state.update(fields)
    return state


def evidence(n=2):
    return {"status": "verified", "runner": "python-unittest",
            "passed": n, "failed": 0}


def wt(status="prepared"):
    return {"status": status, "baseCommit": "abc123",
            "cwd": "/tmp/check"}


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("C:/fake-project")

    def test_requires_strict_isolation(self):
        s = ledger(task("01"))
        s["strictRouting"] = False
        self.assertEqual(controller.decision(self.root, s)["reason"],
                         "strict-isolated-required")
        s["strictRouting"] = True
        s["isolateTickets"] = False
        self.assertEqual(controller.decision(self.root, s)["action"], "blocked")

    def test_unsafe_zones_block_before_preparing(self):
        for zones in (["C:/Users/demo/secret.py"], ["src/*.py"],
                      ["src/../secret.py"], [], ["../src/"], ["./src"],
                      ["src/ok/", "src/./bad.py"]):
            with self.subTest(zones=zones):
                s = ledger(task("01", zone=zones))
                s["tickets"][0]["zone"] = zones
                self.assertEqual(controller.decision(self.root, s)["reason"],
                                 "unsafe-or-ambiguous-ticket-zone")

    def test_no_automatic_model_route(self):
        s = ledger(task("01"))
        s["tickets"][0]["routing"]["verified"] = False
        choice = controller.decision(self.root, s)
        self.assertEqual(choice["action"], "blocked")
        self.assertEqual(choice["reason"], "verified-model-route-required")

    def test_two_independent_tickets_only_one_host_step(self):
        s = ledger(task("01"), task("02"))
        self.assertEqual(controller.decision(self.root, s),
                         {"action": "prepare", "ticket": "01"})
        self.assertEqual(s["tickets"][0]["status"], "pending")

    def test_prepared_task_starts(self):
        s = ledger(task("01", wt=wt()))
        self.assertEqual(controller.decision(self.root, s),
                         {"action": "start", "ticket": "01"})

    def test_dependencies_remain_blocked(self):
        s = ledger(task("01", deps=["02"]), task("02", deps=["01"]))
        d = controller.decision(self.root, s)
        self.assertEqual(d["reason"], "no-safe-runnable-ticket")

    def test_budget_blocks_new_tasks(self):
        s = ledger(task("01"), budgetTokens=10,
                   usageEvents=[{"input": 8, "output": 3}])
        self.assertEqual(controller.decision(self.root, s)["action"], "blocked")

    def test_ambiguous_multiple_active_blocks(self):
        s = ledger(task("01", "in-progress", wt=wt()),
                   task("02", "in-progress", wt=wt()))
        self.assertEqual(controller.decision(self.root, s)["reason"],
                         "multiple-active-require-manual-review")

    @patch.object(controller.worktrees, "status")
    def test_unmodified_worker_is_waiting(self, status):
        status.return_value = {"status": "present", "commit": "abc123", "dirty": False}
        d = controller.decision(self.root, ledger(task("01", "in-progress", wt=wt())))
        self.assertEqual(d["reason"], "await-separately-approved-pinned-worker")

    @patch.object(controller.worktrees, "status")
    def test_changed_worker_requires_explicit_suite(self, status):
        status.return_value = {"status": "present", "commit": "abc123", "dirty": True}
        s = ledger(task("01", "in-progress", wt=wt()))
        self.assertEqual(controller.decision(self.root, s)["reason"],
                         "trusted-suite-required")
        self.assertEqual(controller.decision(self.root, s, "test_calc.py"),
                         {"action": "verify", "ticket": "01", "suite": "test_calc.py"})

    @patch.object(controller.worktrees, "status")
    def test_verified_dirty_changes_need_host_finalization(self, status):
        status.return_value = {"status": "present", "commit": "abc123", "dirty": True}
        d = controller.decision(self.root, ledger(task("01", "in-progress",
                                                     wt=wt(), evidence=evidence())))
        self.assertEqual(d["action"], "finalize")

    @patch.object(controller.worktrees, "status")
    def test_committed_changes_are_verified_before_landing(self, status):
        status.return_value = {"status": "present", "commit": "deadbeef", "dirty": False}
        s = ledger(task("01", "in-progress", wt=wt(), evidence=evidence()))
        d = controller.decision(self.root, s)
        self.assertEqual(d, {"action": "land", "ticket": "01", "tests": 2})

    def test_unverified_landed_ticket_not_accepted(self):
        s = ledger(task("01", "in-progress", wt={**wt("landed"),
                                                "landedCommit": "cafed00d"}))
        self.assertEqual(controller.decision(self.root, s)["reason"],
                         "landing-lacks-trusted-evidence")

    def test_verified_landed_ticket_accept_then_release(self):
        t = task("01", "in-progress", wt={**wt("landed"),
                                        "landedCommit": "cafed00d"},
                 evidence=evidence(3))
        d = controller.decision(self.root, ledger(t))
        self.assertEqual(d, {"action": "accept", "ticket": "01",
                             "tests": 3, "commit": "cafed00d"})
        self.assertEqual(controller.command_for(d),
                         ["ticket", "01", "done", "--tests", "3/0",
                          "--commit", "cafed00d"])
        t["status"] = "done"
        self.assertEqual(controller.decision(self.root, ledger(t))["action"], "release")
        t["worktree"]["status"] = "released"
        self.assertEqual(controller.decision(self.root, ledger(t))["action"], "blocked")

    def test_done_ticket_released_before_next_pending(self):
        s = ledger(task("01", "done", wt={**wt("landed"),
                                         "landedCommit": "cafed00d"}),
                   task("02", "pending", deps=["01"]))
        self.assertEqual(controller.decision(self.root, s)["action"], "release")

    def test_stale_or_bad_ledger_is_blocked(self):
        s = ledger(task("01"), task("01"))
        self.assertEqual(controller.decision(self.root, s)["reason"], "duplicate-ticket-id")
        s = ledger(task("01"), usageEvents=[{"input": "bad", "output": 5}])
        self.assertEqual(controller.decision(self.root, s)["reason"], "invalid-usage-ledger")
        s = ledger(task("01"), budgetTokens=-1)
        self.assertEqual(controller.decision(self.root, s)["reason"], "invalid-token-budget")

    def test_read_only_default_never_calls_ap(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            apdir = root / ".autopilot"
            apdir.mkdir()
            (apdir / "ap.py").write_text("print('NO EXECUTE')", encoding="utf-8")
            (apdir / "state.js").write_text(
                "window.STATE = " + json.dumps(ledger(task("01"))), encoding="utf-8")
            with patch.object(controller.worktrees, "repository", return_value=root), \
                    patch.object(controller.subprocess, "run") as spawn:
                d = controller.advance(root, execute=False)
                self.assertEqual(d["status"], "dry-run")
                self.assertEqual(d["next"]["action"], "prepare")
                spawn.assert_not_called()
                self.assertFalse((apdir / "controller.lock").exists())

    def test_advance_invokes_one_exact_ap_step_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            apdir = root / ".autopilot"
            apdir.mkdir()
            (apdir / "ap.py").write_text("# approved harness", encoding="utf-8")
            (apdir / "state.js").write_text(
                "window.STATE = " + json.dumps(ledger(task("01"))), encoding="utf-8")
            result = Mock(returncode=0)
            with patch.object(controller.worktrees, "repository", return_value=root), \
                    patch.object(controller.subprocess, "run", return_value=result) as spawn:
                d = controller.advance(root, execute=True)
                self.assertEqual(d["status"], "advanced")
                self.assertFalse(d["model_invoked"])
                self.assertEqual(spawn.call_count, 1)
                args = spawn.call_args.args[0]
                self.assertEqual(args[-4:], ["worktree", "01", "prepare", "--no-serve"])

    def test_host_failure_does_not_retry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            apdir = root / ".autopilot"
            apdir.mkdir()
            (apdir / "ap.py").write_text("# approved harness", encoding="utf-8")
            (apdir / "state.js").write_text(
                "window.STATE = " + json.dumps(ledger(task("01"))), encoding="utf-8")
            with patch.object(controller.worktrees, "repository", return_value=root), \
                    patch.object(controller.subprocess, "run", return_value=Mock(returncode=2)) as spawn:
                d = controller.advance(root, execute=True)
                self.assertEqual(d["status"], "blocked")
                self.assertEqual(spawn.call_count, 1)


if __name__ == "__main__":
    unittest.main()
