#!/usr/bin/env python3
"""Safe one-step host-side lifecycle controller for strict isolated Autopilot.

Default: read-only plan. --advance applies ONE permitted state transition.
No model invocation: an executor must be deliberately launched separately
through the pinned, sandboxed codex_dispatch.py --execute path.

Never executes commands suggested by an agent, guesses test suites, retries
model calls, or fabricates completed-test/commit records.
"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys

import scheduler
import worktrees


class ControllerError(ValueError):
    pass


def read_state(root):
    state_file = root / ".autopilot" / "state.js"
    if state_file.is_symlink() or not state_file.is_file():
        raise ControllerError("Missing or redirected Autopilot state.js")
    raw = state_file.read_text(encoding="utf-8")
    if not raw.startswith("window.STATE"):
        raise ControllerError("Invalid state.js format")
    try:
        data = json.loads(raw.split("=", 1)[1].strip().rstrip(";"))
    except (ValueError, IndexError) as exc:
        raise ControllerError("Malformed Autopilot state.js") from exc
    if not isinstance(data, dict) or not isinstance(data.get("tickets"), list):
        raise ControllerError("Invalid Autopilot state")
    return data


def safe_zone_list(ticket):
    """Finalization accepts only exact, repo-relative paths and directories."""
    zones = ticket.get("zone")
    if not isinstance(zones, list) or not zones:
        return False
    for zone in zones:
        if not isinstance(zone, str):
            return False
        name = zone.replace(chr(92), "/")
        pieces = name.rstrip("/").split("/")
        if (not name or name.startswith("/") or
                any(p in ("", ".", "..") for p in pieces) or
                any(c in name for c in "*?[]:" + chr(0)) or
                name == ".git" or name.startswith(".git/") or
                name == ".autopilot" or name.startswith(".autopilot/")):
            return False
    return True


def verified_tests(ticket):
    record = ticket.get("testEvidence")
    if (not isinstance(record, dict) or record.get("status") != "verified"
            or record.get("runner") not in ("python-unittest", "cargo-test")
            or type(record.get("passed")) is not int
            or record["passed"] < 1 or record.get("failed") != 0):
        return None
    return record["passed"]


def decision(root, state, suite=None):
    """Choose a SINGLE safe next step; no mutation, no model calls."""
    if state.get("finishedAt"):
        return {"action": "blocked", "reason": "run-finished"}
    if state.get("isolateTickets") is not True or state.get("strictRouting") is not True:
        return {"action": "blocked", "reason": "strict-isolated-required"}
    tickets = state["tickets"]
    if not all(isinstance(t, dict) and isinstance(t.get("id"), str) for t in tickets):
        return {"action": "blocked", "reason": "invalid-ticket-list"}
    if len({t["id"] for t in tickets}) != len(tickets):
        return {"action": "blocked", "reason": "duplicate-ticket-id"}
    for t in tickets:
        if t.get("status") in ("pending", *scheduler.ACTIVE) and not safe_zone_list(t):
            return {"action": "blocked", "ticket": t["id"],
                    "reason": "unsafe-or-ambiguous-ticket-zone"}
    active = [t for t in tickets if t.get("status") in scheduler.ACTIVE]
    if len(active) > 1:
        return {"action": "blocked", "reason": "multiple-active-require-manual-review"}
    if active:
        t = active[0]
        tid = t["id"]
        wt = t.get("worktree") or {}
        stage = wt.get("status")
        if stage == "landed":
            accepted = verified_tests(t)
            if accepted is None or not wt.get("landedCommit"):
                return {"action": "blocked", "ticket": tid,
                        "reason": "landing-lacks-trusted-evidence"}
            return {"action": "accept", "ticket": tid, "tests": accepted,
                    "commit": wt["landedCommit"]}
        if stage != "prepared":
            return {"action": "blocked", "ticket": tid, "reason": "unexpected-worktree-stage"}
        actual = worktrees.status(root, tid)
        if actual.get("status") != "present":
            return {"action": "blocked", "ticket": tid, "reason": "missing-worker-worktree"}
        base = wt.get("baseCommit")
        if not isinstance(base, str) or not base:
            return {"action": "blocked", "ticket": tid, "reason": "missing-base-commit"}
        passed = verified_tests(t)
        if passed is not None:
            if actual.get("commit") == base:
                return {"action": "finalize", "ticket": tid, "tests": passed}
            return {"action": "land", "ticket": tid, "tests": passed}
        if actual.get("dirty") or actual.get("commit") != base:
            if suite is None:
                return {"action": "blocked", "ticket": tid, "reason": "trusted-suite-required"}
            return {"action": "verify", "ticket": tid, "suite": suite}
        return {"action": "blocked", "ticket": tid,
                "reason": "await-separately-approved-pinned-worker"}
    # Accept completed tickets' already-landed worktrees before new starts.
    for t in tickets:
        if t.get("status") == "done":
            stage = (t.get("worktree") or {}).get("status")
            if stage == "landed":
                return {"action": "release", "ticket": t["id"]}
            if stage not in ("released", None):
                return {"action": "blocked", "ticket": t["id"],
                        "reason": "done-ticket-worktree-inconsistent"}
    # Scheduling remains conservative even with disjoint zones: one host
    # transition at a time, never more than one pending executor.
    budget = state.get("budgetTokens")
    events = state.get("usageEvents") or []
    try:
        used = sum(event["input"] + event["output"] for event in events)
    except (KeyError, TypeError, ValueError):
        return {"action": "blocked", "reason": "invalid-usage-ledger"}
    if budget is not None and (type(budget) is not int or budget < 0):
        return {"action": "blocked", "reason": "invalid-token-budget"}
    plan = scheduler.schedule(
        tickets, 1, strict=True, isolated=True,
        budget_blocked=budget is not None and used >= budget)
    selected = plan.get("selected") or []
    if not selected:
        return {"action": "blocked", "reason": "no-safe-runnable-ticket",
                "blocked": plan.get("blocked", [])}
    action = selected[0]
    if action["action"] == "route":
        return {"action": "blocked", "ticket": action["ticket"],
                "reason": "verified-model-route-required"}
    if action["action"] not in ("prepare", "start"):
        return {"action": "blocked", "reason": "unexpected-scheduler-action"}
    return {"action": action["action"], "ticket": action["ticket"]}


@contextmanager
def controller_lock(root):
    """OS-owned interprocess lock; file stays permanently for Windows inode safety."""
    path = root / ".autopilot" / "controller.lock"
    with path.open("a+b") as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b"1")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ControllerError("Another controller owns the project") from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ControllerError("Another controller owns the project") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def command_for(step):
    tid = step.get("ticket")
    action = step["action"]
    if action == "prepare":
        return ["worktree", tid, "prepare"]
    if action == "start":
        return ["ticket", tid, "start"]
    if action == "verify":
        return ["worktree", tid, "verify", "--suite", step["suite"]]
    if action == "finalize":
        return ["worktree", tid, "finalize", "--tests", str(step["tests"]) + "/0"]
    if action == "land":
        return ["worktree", tid, "land", "--tests", str(step["tests"]) + "/0"]
    if action == "accept":
        return ["ticket", tid, "done", "--tests", str(step["tests"]) + "/0",
                "--commit", step["commit"]]
    if action == "release":
        return ["worktree", tid, "release"]
    raise ControllerError("Controller cannot execute " + action)


def advance(root, suite=None, *, execute=False):
    root = Path(root).resolve()
    if worktrees.repository(root) != root:
        raise ControllerError("Expected Git repository root")
    ap = root / ".autopilot" / "ap.py"
    if not ap.is_file() or ap.is_symlink():
        raise ControllerError("Project Autopilot ap.py missing or redirected")
    if not execute:
        # Truly read-only planning does not even create the controller lock.
        step = decision(root, read_state(root), suite)
        return {"status": "dry-run" if step["action"] != "blocked" else "blocked",
                "next": step, "model_invoked": False}
    with controller_lock(root):
        step = decision(root, read_state(root), suite)
        if step["action"] == "blocked":
            return {"status": "blocked", "next": step, "model_invoked": False}
        command = [sys.executable, str(ap), *command_for(step), "--no-serve"]
        try:
            result = subprocess.run(command, cwd=root, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=330)
        except subprocess.TimeoutExpired as exc:
            raise ControllerError("Host step timed out; inspect state before retry") from exc
        # No blind retry on failure; actions may have reached Git before state.
        if result.returncode:
            return {"status": "blocked", "next": step,
                    "reason": "host-transition-failed-inspect-ledger",
                    "exit_code": result.returncode, "model_invoked": False}
        return {"status": "advanced", "completed": step,
                "next": decision(root, read_state(root), suite),
                "model_invoked": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--suite", help="Operator-approved tracked unittest.py or cargo:integration-test name")
    p.add_argument("--advance", action="store_true",
                   help="Apply exactly one safe host step; never launch a model")
    args = p.parse_args(argv)
    try:
        output = advance(args.root, args.suite, execute=args.advance)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output["status"] in ("dry-run", "advanced") else 2
    except (ControllerError, worktrees.WorktreeError, OSError, TypeError,
            ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:300],
                          "model_invoked": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
