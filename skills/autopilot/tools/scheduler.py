#!/usr/bin/env python3
"""Deterministic Autopilot dispatch planner.

Chooses at most two new tasks by default, respecting dependencies, active zones,
prepared worktree reservations, verified routes and recorded-token thresholds.
This module NEVER spawns agents or modifies a checkout.
"""
import argparse
import json
from pathlib import Path
import sys

ACTIVE = {"in-progress", "review", "repair"}
MAX = 3


def zones_of(ticket):
    zones = ticket.get("zone") or []
    result = []
    for zone in zones:
        if not isinstance(zone, str) or not zone.strip():
            continue
        normalized = zone.replace("\\", "/").strip("./").rstrip("/")
        if normalized and not normalized.startswith(".."):
            result.append(normalized + "/")
    return result or ["/"]


def intersect(left, right):
    """Unknown or broad zones are treated as shared, not disjoint."""
    a, b = zones_of(left), zones_of(right)
    if "/" in a or "/" in b:
        return True
    return any(x.startswith(y) or y.startswith(x) for x in a for y in b)


def schedule(tickets, max_parallel=2, *, strict=False, isolated=False,
             budget_blocked=False, verified=None):
    if type(max_parallel) is not int or not 1 <= max_parallel <= MAX:
        raise ValueError("Max parallel workers must be 1..3")
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be an array")
    if not all(isinstance(t, dict) and isinstance(t.get("id"), str) for t in tickets):
        raise ValueError("Each ticket needs a string ID")
    if len({t["id"] for t in tickets}) != len(tickets):
        raise ValueError("Duplicate ticket IDs")
    index = {t["id"]: t for t in tickets}
    active = [t for t in tickets if t.get("status") in ACTIVE]
    reserved = [t for t in tickets if t.get("status") == "pending"
                and (t.get("worktree") or {}).get("status") == "prepared"]
    held = active + reserved
    if len(held) > max_parallel:
        return {"selected": [], "blocked": [{"ticket": "*", "reason": "parallel-capacity-exceeded"}],
                "capacity": max_parallel, "inFlight": len(active),
                "reserved": len(reserved), "automaticLaunch": False}
    available = max_parallel - len(held)
    selected = []
    blocked = []
    def eligible(t):
        return verified.get(t["id"], False) if verified is not None else (
            (t.get("routing") or {}).get("verified") is True)
    candidates = sorted(
        (t for t in tickets if t.get("status") == "pending"),
        key=lambda t: (t.get("wave") if type(t.get("wave")) is int else 999, t["id"]))
    for ticket in candidates:
        tid = ticket["id"]
        missing = [dep for dep in ticket.get("blockedBy") or []
                   if dep not in index or index[dep].get("status") != "done"]
        if missing:
            blocked.append({"ticket": tid, "reason": "dependencies", "ids": missing})
            continue
        if budget_blocked:
            blocked.append({"ticket": tid, "reason": "recorded-token-budget"})
            continue
        already_reserved = ticket in reserved
        if not already_reserved and available <= 0:
            blocked.append({"ticket": tid, "reason": "parallel-capacity"})
            continue
        conflicts = [t["id"] for t in held if t["id"] != tid and intersect(ticket, t)]
        conflicts += [e["ticket"] for e in selected if e["ticket"] != tid and
                      intersect(ticket, index[e["ticket"]])]
        if conflicts:
            blocked.append({"ticket": tid, "reason": "overlapping-zone",
                            "ids": sorted(set(conflicts))})
            continue
        if strict and not eligible(ticket):
            action = "route"
        elif isolated and not already_reserved:
            action = "prepare"
        elif isolated and (ticket.get("worktree") or {}).get("status") != "prepared":
            action = "prepare"
        else:
            action = "start"
        selected.append({"ticket": tid, "action": action,
                         "wave": ticket.get("wave"),
                         "cwd": (ticket.get("worktree") or {}).get("cwd") if action == "start" else None})
        if not already_reserved:
            available -= 1
    return {"selected": selected, "blocked": blocked, "capacity": max_parallel,
            "inFlight": len(active), "reserved": len(reserved),
            "automaticLaunch": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--max-parallel", type=int, default=2)
    args = parser.parse_args()
    try:
        raw = args.state.read_text(encoding="utf-8")
        if raw.startswith("window.STATE"):
            raw = raw.split("=", 1)[1]
        data = json.loads(raw)
        usage = data.get("usageEvents") or []
        budget = data.get("budgetTokens")
        exhausted = (isinstance(budget, int) and budget > 0 and
                     sum(e.get("input", 0) + e.get("output", 0) for e in usage) >= budget)
        result = schedule(data.get("tickets") or [], args.max_parallel,
                          strict=bool(data.get("strictRouting")),
                          isolated=bool(data.get("isolateTickets")), budget_blocked=exhausted)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
