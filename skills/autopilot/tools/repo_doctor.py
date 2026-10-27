#!/usr/bin/env python3
"""Read-only Git preflight for any Autopilot project.

Never stages, commits, stashes, resets, initializes, launches a model or executes
project test code. Emits only aggregate Git status counts, not private filenames.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


class DoctorError(ValueError):
    pass


def git(root, *args, allow_failure=False):
    try:
        run = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                              "-C", str(root), *args],
                             capture_output=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DoctorError("Git unavailable or timed out") from exc
    if run.returncode and not allow_failure:
        raise DoctorError("Git preflight command failed")
    return run


def inspect(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise DoctorError("Project root does not exist")
    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.decode("utf-8", "replace").strip()).resolve() != root:
        raise DoctorError("Expected exact Git repository root")
    head = git(root, "rev-parse", "--verify", "HEAD^{commit}", allow_failure=True)
    baseline = head.stdout.decode("ascii", "replace").strip() if head.returncode == 0 else None
    result = {"status": "blocked", "read_only": True, "git_mutated": False,
              "base_commit": baseline, "source": {}, "blockers": [],
              "warnings": [], "test_runners": {"available": ["python-unittest"],
                                                 "other_frameworks": "not-attested"}}
    blockers = result["blockers"]
    if baseline is None:
        blockers.append("no-baseline-commit")
    status = git(root, "status", "--porcelain=v1", "-z",
                 "--untracked-files=all", "--", ".",
                 ":(exclude).autopilot")
    if status.returncode:
        raise DoctorError("Cannot inspect Git source status")
    # Porcelain -z uses NUL fields. Rename/copy entries carry an additional
    # path, so skip it without ever disclosing paths or their contents.
    entries = status.stdout.split(b"\0")
    counts = {"staged": 0, "unstaged": 0, "untracked": 0, "conflicted": 0}
    index = 0
    while index < len(entries):
        record = entries[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            raise DoctorError("Unexpected Git porcelain format")
        x, y = record[:1], record[1:2]
        if x == b"?" and y == b"?":
            counts["untracked"] += 1
        elif x == b"U" or y == b"U" or (x + y) in (b"AA", b"DD"):
            counts["conflicted"] += 1
        else:
            counts["staged"] += int(x not in (b" ", b"?"))
            counts["unstaged"] += int(y not in (b" ", b"?"))
        if x in (b"R", b"C") or y in (b"R", b"C"):
            if index >= len(entries) or not entries[index]:
                raise DoctorError("Malformed rename entry")
            index += 1
    result["source"] = counts
    if any(counts.values()):
        blockers.append("source-has-uncommitted-changes")
        result["warnings"].append(
            "Review scoped source changes manually; never auto-stage, stash, reset or clean.")
    for item in (root / ".autopilot", root / ".autopilot" / "worktrees",
                 root / ".autopilot" / "worktrees" / "T01"):
        if item.is_symlink() or (getattr(item, "is_junction", lambda: False)()):
            blockers.append("unsafe-worktree-path")
            break
    ignored = git(root, "check-ignore", "-q", ".autopilot/worktrees/T01", allow_failure=True)
    if ignored.returncode != 0:
        blockers.append("worktree-directory-not-ignored")
    if (root / "Cargo.toml").is_file():
        result["warnings"].append(
            "Rust/Cargo verifier is not yet accepted by the host evidence gate.")
    if (root / "package.json").is_file():
        result["warnings"].append(
            "Node/JS verifier is not yet accepted by the host evidence gate.")
    if (root / "go.mod").is_file():
        result["warnings"].append(
            "Go verifier is not yet accepted by the host evidence gate.")
    result["status"] = "ready" if not blockers else "blocked"
    result["can_prepare_worktree"] = not blockers
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        report = inspect(args.root)
    except (DoctorError, ValueError, OSError) as exc:
        report = {"status": "blocked", "read_only": True,
                  "git_mutated": False, "blockers": [str(exc)[:130]]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    sys.exit(main())
