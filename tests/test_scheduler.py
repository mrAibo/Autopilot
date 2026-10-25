"""Deterministic scheduler respects dependencies, worktree reservations and zones."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "autopilot" / "tools"))
import scheduler


def ticket(id, zone, wave=1, status="pending", deps=None, worktree=None, verified=False):
    t = {"id": id, "zone": zone, "wave": wave, "status": status,
         "blockedBy": deps or [], "routing": {"verified": verified}}
    if worktree:
        t["worktree"] = worktree
    return t


class SchedulerTests(unittest.TestCase):
    def test_selects_two_independent_zones_not_more(self):
        ts = [ticket("01", ["app/a"]), ticket("02", ["app/b"]),
              ticket("03", ["app/c"])]
        p = scheduler.schedule(ts)
        self.assertEqual([x["ticket"] for x in p["selected"]], ["01", "02"])
        self.assertEqual(p["blocked"][0]["reason"], "parallel-capacity")
        self.assertFalse(p["automaticLaunch"])

    def test_conflicting_zones_serialize(self):
        ts = [ticket("01", ["src/"]), ticket("02", ["src/api"]),
              ticket("03", ["tests/"])]
        p = scheduler.schedule(ts)
        self.assertEqual([x["ticket"] for x in p["selected"]], ["01", "03"])
        self.assertIn("overlapping-zone", [x["reason"] for x in p["blocked"]])

    def test_waits_for_dependencies_even_if_slot_is_free(self):
        ts = [ticket("01", ["app/"], status="in-progress"),
              ticket("02", ["lib/"], deps=["01"])]
        p = scheduler.schedule(ts)
        self.assertFalse(p["selected"])
        self.assertEqual(p["blocked"][0]["reason"], "dependencies")

    def test_inflight_and_prepared_reservations_use_capacity(self):
        ts = [ticket("01", ["src/a"], status="in-progress"),
              ticket("02", ["src/b"], worktree={"status": "prepared", "cwd": "/fake"}),
              ticket("03", ["src/c"])]
        p = scheduler.schedule(ts, isolated=True)
        self.assertEqual([x["ticket"] for x in p["selected"]], ["02"])
        self.assertEqual((p["inFlight"], p["reserved"]), (1, 1))
        self.assertEqual(p["blocked"][0]["reason"], "parallel-capacity")

    def test_strict_without_verified_profile_requests_route(self):
        p = scheduler.schedule([ticket("01", ["docs/"])], strict=True, isolated=True,
                               verified={"01": False})
        self.assertEqual(p["selected"][0]["action"], "route")

    def test_strict_approved_profile_requests_preparation(self):
        p = scheduler.schedule([ticket("01", ["docs/"])], strict=True, isolated=True,
                               verified={"01": True})
        self.assertEqual(p["selected"][0]["action"], "prepare")

    def test_unknown_absolute_or_wildcard_zones_block_conflicts(self):
        absolute = [ticket("01", ["/etc/unsafe"]), ticket("02", ["src"])]
        p = scheduler.schedule(absolute)
        self.assertEqual(len(p["selected"]), 1)
        self.assertEqual(p["blocked"][0]["reason"], "overlapping-zone")
        wildcard = [ticket("01", ["src/*"]), ticket("02", ["src/api"])]
        p = scheduler.schedule(wildcard)
        self.assertEqual(len(p["selected"]), 1)
        self.assertEqual(p["blocked"][0]["reason"], "overlapping-zone")

    def test_budget_blocks_all_new_dispatches(self):
        ts = [ticket("01", ["src/a"]), ticket("02", ["src/b"])]
        p = scheduler.schedule(ts, budget_blocked=True)
        self.assertFalse(p["selected"])
        self.assertTrue(all(x["reason"] == "recorded-token-budget" for x in p["blocked"]))

    def test_overcapacity_is_fail_closed(self):
        ts = [ticket("01", ["a"], status="in-progress"),
              ticket("02", ["b"], status="in-progress"),
              ticket("03", ["c"], status="in-progress")]
        p = scheduler.schedule(ts)
        self.assertFalse(p["selected"])
        self.assertIn("parallel-capacity-exceeded", p["blocked"][0]["reason"])

    def test_duplicate_ticket_ids_are_not_accepted(self):
        with self.assertRaises(ValueError):
            scheduler.schedule([ticket("01", ["a"]), ticket("01", ["b"])])

    def test_requested_capacity_above_three_is_rejected(self):
        with self.assertRaises(ValueError):
            scheduler.schedule([], max_parallel=4)


if __name__ == "__main__":
    unittest.main()
