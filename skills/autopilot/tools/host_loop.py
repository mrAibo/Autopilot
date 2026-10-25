#!/usr/bin/env python3
"""Bounded host-only Autopilot lifecycle loop for strict isolated tickets.

Read-only by default. --advance runs at most N controller transitions, without
calling a model, sending network requests, or retrying a failed transition.
Explicit per-ticket suites are never inferred from agent text.
"""
import argparse
import json
from pathlib import Path
import sys

import controller
import worktrees

MAX_STEPS = 32
AWAIT_WORKER = "await-separately-approved-pinned-worker"


def parse_suites(values):
    result = {}
    for value in values:
        tid, sep, suite = value.partition("=")
        if (not sep or not tid.isdigit() or not 1 <= len(tid) <= 4 or
                not suite or tid in result or "\x00" in suite):
            raise ValueError("Use unique --suite TICKET=baseline_test.py entries")
        result[tid] = suite
    return result


def peek(root, suites):
    """Never create a lock, write a receipt or execute an ap.py step."""
    result = controller.advance(root, execute=False)
    step = result["next"]
    tid = step.get("ticket")
    if step.get("reason") == "trusted-suite-required" and tid in suites:
        result = controller.advance(root, suite=suites[tid], execute=False)
        step = result["next"]
    return step


def loop(root, suites=None, *, execute=False, max_steps=8):
    """One explicit host run; always stop at a separate AI worker boundary."""
    if type(max_steps) is not int or not 1 <= max_steps <= MAX_STEPS:
        raise ValueError("max_steps must be between 1 and 32")
    suites = dict(suites or {})
    root = Path(root).resolve()
    steps = []
    while True:
        step = peek(root, suites)
        if step["action"] == "blocked":
            reason = step.get("reason", "")
            status = "paused" if reason == AWAIT_WORKER else "blocked"
            if reason == "no-safe-runnable-ticket":
                state = controller.read_state(root)
                tickets = state["tickets"]
                if tickets and all(t.get("status") == "done" and
                                   (t.get("worktree") or {}).get("status") == "released"
                                   for t in tickets):
                    # NOT Autopilot finish / blind acceptance / G1-G4.
                    status = "tickets-settled"
            return {"status": status, "next": step,
                    "completed": steps, "model_invoked": False}
        if not execute:
            return {"status": "dry-run", "next": step,
                    "completed": [], "model_invoked": False}
        if len(steps) == max_steps:
            return {"status": "limit-reached", "next": step,
                    "completed": steps, "model_invoked": False}
        # The controller takes the OS lock and revalidates live state/Git.
        # A concurrent update can change the selected action; do not continue
        # an orchestration run after that action has unexpectedly changed.
        result = controller.advance(
            root, suite=suites.get(step.get("ticket")), execute=True)
        if result["status"] != "advanced":
            return {"status": "blocked", "next": result.get("next", step),
                    "reason": result.get("reason", "controller-transition-blocked"),
                    "completed": steps, "model_invoked": False}
        completed = result["completed"]
        steps.append(completed)
        if (completed.get("action") != step["action"] or
                completed.get("ticket") != step.get("ticket")):
            return {"status": "blocked", "reason": "concurrent-state-shift",
                    "next": result["next"], "completed": steps,
                    "model_invoked": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--suite", action="append", default=[], metavar="TICKET=FILE",
                        help="Explicit baseline-tracked unittest per ticket")
    parser.add_argument("--advance", action="store_true",
                        help="Allow bounded trusted host Git/test/state transitions")
    parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args(argv)
    try:
        result = loop(args.root, parse_suites(args.suite),
                      execute=args.advance, max_steps=args.max_steps)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] in (
            "dry-run", "paused", "limit-reached", "tickets-settled") else 2
    except (ValueError, TypeError, OSError, controller.ControllerError,
            worktrees.WorktreeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:300],
                          "completed": [], "model_invoked": False},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
