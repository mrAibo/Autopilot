#!/usr/bin/env python3
"""Read-only eligibility check for host-side finalization of uncommitted work.

No Git mutations, tests, shell instructions, worker tokens or model calls.
This is only a preliminary handoff gate: the existing independently verified
host tests, immutable evidence and worktrees.finalize recheck all invariants.
"""
from pathlib import Path

import worktrees


def _safe_zone(zone):
    if not isinstance(zone, str) or not zone:
        return None
    normalized = zone.replace("\\", "/")
    pieces = normalized.rstrip("/").split("/")
    if (normalized.startswith("/") or
            any(x in ("", ".", "..") for x in pieces) or
            any(ch in normalized for ch in "*?[]:\0") or
            normalized == ".git" or normalized.startswith(".git/") or
            normalized == ".autopilot" or normalized.startswith(".autopilot/")):
        return None
    return normalized.rstrip("/"), normalized.endswith("/")


def inspect(root, ticket):
    """Return a safe coarse status and count; never leak paths or model text."""
    root = Path(root).resolve()
    try:
        state_path = root / ".autopilot" / "state.js"
        if state_path.is_symlink() or not state_path.is_file():
            return {"eligible": False, "reason": "state-unavailable"}
        import codex_dispatch
        state = codex_dispatch.load_state(root)
        found = [t for t in state.get("tickets", [])
                 if isinstance(t, dict) and t.get("id") == ticket]
        if len(found) != 1:
            return {"eligible": False, "reason": "ticket-identity-unverified"}
        task = found[0]
        wt = task.get("worktree") or {}
        if (task.get("status") != "in-progress" or
                wt.get("status") != "prepared" or
                not isinstance(wt.get("baseCommit"), str)):
            return {"eligible": False, "reason": "ticket-not-active"}
        zones = task.get("zone")
        if not isinstance(zones, list) or not zones:
            return {"eligible": False, "reason": "zones-not-verified"}
        allowed = [_safe_zone(x) for x in zones]
        if any(z is None for z in allowed):
            return {"eligible": False, "reason": "zones-not-verified"}
        worktrees.repository(root)
        target = worktrees.safe_target(root, ticket)
        if not target.is_dir() or target.is_symlink():
            return {"eligible": False, "reason": "worktree-missing"}
        if (Path(wt.get("cwd", root)).resolve() != target.resolve()
                or worktrees.git(target, "rev-parse", "HEAD").stdout.strip()
                != wt["baseCommit"]):
            return {"eligible": False, "reason": "worktree-base-changed"}
        if (worktrees.git(target, "diff", "--check", check=False).returncode or
                worktrees.git(target, "diff", "--cached", "--check",
                              check=False).returncode):
            return {"eligible": False, "reason": "unsafe-diff"}
        operations = (("diff", "--name-only", "-z"),
                      ("diff", "--cached", "--name-only", "-z"),
                      ("ls-files", "--others", "--exclude-standard", "-z"))
        names = sorted(set(name for cmd in operations
                           for name in worktrees.git(target, *cmd).stdout.split("\0")
                           if name))
        if not names:
            return {"eligible": False, "reason": "no-changes", "changed_files": 0}
        for name in names:
            normalized = name.replace("\\", "/")
            pieces = normalized.split("/")
            if (not normalized or normalized.startswith("/") or
                    any(p in ("", ".", "..") for p in pieces) or
                    normalized == ".git" or normalized.startswith(".git/") or
                    normalized == ".autopilot" or normalized.startswith(".autopilot/")):
                return {"eligible": False, "reason": "unsafe-change-path"}
            candidate = target / normalized
            # Check intermediate components too, not just final target.
            current = target
            for part in pieces:
                current = current / part
                if (current.is_symlink() or
                        getattr(current, "is_junction", lambda: False)()):
                    return {"eligible": False, "reason": "redirected-change-path"}
            if candidate.exists() and not candidate.resolve().is_relative_to(target.resolve()):
                return {"eligible": False, "reason": "escaped-change-path"}
            if not any(normalized == prefix or
                       (directory and normalized.startswith(prefix + "/"))
                       for prefix, directory in allowed):
                return {"eligible": False, "reason": "change-outside-zone"}
        return {"eligible": True, "reason": "zone-scoped-uncommitted-changes",
                "changed_files": len(names),
                "next_gate": "independent-host-tests-before-finalize"}
    except (OSError, TypeError, ValueError, KeyError, worktrees.WorktreeError):
        return {"eligible": False, "reason": "git-or-state-unavailable"}

def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ticket", required=True)
    args = parser.parse_args(argv)
    status = inspect(args.root, args.ticket)
    print(json.dumps({"status": "read-only-inspection", "ticket": args.ticket,
                      "candidate": status, "model_invoked": False,
                      "accepted": False}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
