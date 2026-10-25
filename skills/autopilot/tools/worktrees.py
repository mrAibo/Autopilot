#!/usr/bin/env python3
"""Conservative Git worktree isolation for parallel Autopilot executors.

One detached worktree per ticket, optional single-commit cherry-pick landing.
Never reset or force-remove a dirty worktree.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


class WorktreeError(RuntimeError):
    pass


def git(root, *args, check=True):
    run = subprocess.run(["git", "-C", str(root), *args],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and run.returncode:
        raise WorktreeError(run.stderr.strip() or "Git failed: " + " ".join(args))
    return run


def repository(root):
    root = Path(root).resolve()
    top = Path(git(root, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if top != root:
        raise WorktreeError("Root must be a Git worktree root (not a subdirectory)")
    return root


def safe_target(root, ticket):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}", ticket):
        raise WorktreeError("Ticket ID must be 1–32 safe characters")
    parent = root / ".autopilot" / "worktrees"
    target = parent / ("T" + ticket)
    # Do not compare resolve() to the raw Windows path: canonical casing and
    # drive normalization differ even for ordinary non-linked directories.
    for entry in (parent.parent, parent, target):
        if entry.is_symlink() or (getattr(entry, "is_junction", lambda: False)()):
            raise WorktreeError("Worktree path may not contain a symlink or junction")
    if parent.exists() and not parent.resolve().is_relative_to(Path(root).resolve()):
        raise WorktreeError("Worktree directory escapes repository")
    return target


def source_dirty(root):
    """Track user source modifications, excluding only the Autopilot runtime ledger."""
    return bool(git(root, "status", "--porcelain", "--untracked-files=all",
                    "--", ".", ":(exclude).autopilot").stdout.strip())


def create(root, ticket, base="HEAD"):
    root = repository(root)
    target = safe_target(root, ticket)
    if source_dirty(root):
        raise WorktreeError("Commit or restore source changes (including .gitignore) before preparing an isolated ticket")
    if target.exists():
        raise WorktreeError("Worktree already exists: " + str(target))
    if git(root, "check-ignore", "-q", str(target), check=False).returncode != 0:
        raise WorktreeError("Add .autopilot/worktrees/ to .gitignore before creating worktrees")
    if base != "HEAD" and not re.fullmatch(r"[0-9a-fA-F]{7,40}", base):
        raise WorktreeError("Base must be HEAD or a commit SHA")
    sha = git(root, "rev-parse", "--verify", base + "^{commit}").stdout.strip()
    target.parent.mkdir(parents=True, exist_ok=True)
    git(root, "worktree", "add", "--detach", str(target), sha)
    return {"ticket": ticket, "cwd": str(target), "baseCommit": sha,
            "status": "created", "landing": "not-applied"}


def status(root, ticket):
    root = repository(root)
    target = safe_target(root, ticket)
    if not target.is_dir():
        return {"ticket": ticket, "status": "missing"}
    head = git(target, "rev-parse", "HEAD").stdout.strip()
    return {"ticket": ticket, "cwd": str(target), "status": "present",
            "commit": head, "dirty": bool(git(target, "status", "--porcelain").stdout.strip())}


def source_commit(root, ticket, base):
    """Return the sole executor commit, rejecting diverged or dirty worktrees."""
    target = safe_target(root, ticket)
    if not target.is_dir():
        raise WorktreeError("Worktree missing")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", base):
        raise WorktreeError("A known base commit SHA is required")
    base_sha = git(root, "rev-parse", "--verify", base + "^{commit}").stdout.strip()
    head = git(target, "rev-parse", "HEAD").stdout.strip()
    if git(target, "status", "--porcelain").stdout.strip():
        raise WorktreeError("Executor worktree has uncommitted changes")
    count = git(root, "rev-list", "--count", base_sha + ".." + head).stdout.strip()
    if count != "1" or git(target, "rev-parse", head + "^").stdout.strip() != base_sha:
        raise WorktreeError("Executor must have exactly one commit directly on its base")
    return head


def patch_id(root, sha):
    diff = git(root, "show", "--pretty=format:", "--binary", sha).stdout
    result = subprocess.run(["git", "-C", str(root), "patch-id", "--stable"],
                            input=diff, capture_output=True, text=True, encoding="utf-8")
    if result.returncode or not result.stdout.strip():
        raise WorktreeError("Cannot compare source and integrated commit patches")
    return result.stdout.split()[0]


def find_landing(root, source):
    """Detect a previous cherry-pick after a crash, requiring matching Git patch."""
    marker = "(cherry picked from commit %s)" % source
    hits = git(root, "log", "HEAD", "--format=%H", "--fixed-strings",
               "--grep=" + marker, "--max-count=8").stdout.splitlines()
    valid = []
    for commit in hits:
        message = git(root, "show", "-s", "--format=%B", commit).stdout
        if marker not in message.splitlines():
            continue
        if patch_id(root, commit) == patch_id(root, source):
            valid.append(commit)
    if len(valid) > 1:
        raise WorktreeError("Ambiguous landing: multiple matching cherry-picks; inspect manually")
    return valid[0] if valid else None


def interrupted_cherry_pick(root):
    """Detect a Git sequencer left behind by abrupt termination."""
    return git(root, "rev-parse", "-q", "--verify", "CHERRY_PICK_HEAD",
               check=False).returncode == 0


def recover(root, ticket, base):
    """Read-only Git recovery: do not cherry-pick or amend anything."""
    root = repository(root)
    if interrupted_cherry_pick(root):
        raise WorktreeError("Git cherry-pick is interrupted; inspect Git status and decide --continue or --abort manually")
    source = source_commit(root, ticket, base)
    found = find_landing(root, source)
    return {"ticket": ticket, "status": "landed" if found else "not-landed",
            "sourceCommit": source, "landedCommit": found}


def finalize(root, ticket, base, zones, passed, failed):
    """Host-owned Git commit after independently confirmed tests.

    Designed for sandboxed model workers that cannot write shared .git/worktrees.
    Never stages a file outside declared zones, never deletes untracked files,
    never runs tests on behalf of the user, and never silently modifies main.
    """
    root = repository(root)
    target = safe_target(root, ticket)
    if type(passed) is not int or passed < 1 or type(failed) is not int or failed != 0:
        raise WorktreeError("Independent successful test results N/0 are required")
    if not isinstance(zones, list) or not zones:
        raise WorktreeError("Ticket must declare an exact code zone")
    allowed = []
    for zone in zones:
        if not isinstance(zone, str):
            raise WorktreeError("Invalid zone type")
        value = zone.replace("\\", "/")
        parts = value.rstrip("/").split("/")
        if (not value or value.startswith("/") or
                any(p in ("", ".", "..") for p in parts) or
                any(c in value for c in "*?[]:\0") or value.startswith(".git")):
            raise WorktreeError("Unsafe or wildcard code zone: " + zone)
        allowed.append((value.rstrip("/"), value.endswith("/")))
    if source_dirty(root):
        raise WorktreeError("Primary source checkout must be clean before finalization")
    if not target.is_dir() or target.is_symlink():
        raise WorktreeError("Executor worktree missing or redirected")
    expected = git(root, "rev-parse", "--verify", base + "^{commit}").stdout.strip()
    if git(target, "rev-parse", "HEAD").stdout.strip() != expected:
        raise WorktreeError("Executor HEAD already differs from planned base")
    if git(target, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0:
        raise WorktreeError("Worktree has an unresolved Git merge")
    if git(target, "diff", "--check").returncode:
        raise WorktreeError("Worker diff contains whitespace errors")
    commands = (("diff", "--name-only", "-z"),
                ("diff", "--cached", "--name-only", "-z"),
                ("ls-files", "--others", "--exclude-standard", "-z"))
    paths = sorted({name for cmd in commands for name in
                    git(target, *cmd).stdout.split("\0") if name})
    if not paths:
        raise WorktreeError("No changed worker files to finalize")
    for name in paths:
        normalized = name.replace("\\", "/")
        pieces = normalized.split("/")
        if (normalized.startswith("/") or
                any(p in ("", ".", "..") for p in pieces) or
                normalized == ".git" or normalized.startswith(".git/") or
                normalized == ".autopilot" or normalized.startswith(".autopilot/")):
            raise WorktreeError("Unsafe worker path: " + normalized)
        path = target / normalized
        if path.is_symlink() or (path.exists() and
                                not path.resolve().is_relative_to(target.resolve())):
            raise WorktreeError("Changed file escapes worktree")
        if not any(normalized == prefix or
                   (is_dir and normalized.startswith(prefix + "/"))
                   for prefix, is_dir in allowed):
            raise WorktreeError("Worker changed file outside declared zone: " + normalized)
    git(target, "add", "--", *paths)
    result = git(target, "commit", "-m", "Autopilot " + ticket + ": validated worker changes",
                 check=False)
    if result.returncode:
        raise WorktreeError("Git commit failed; staged changes preserved for inspection")
    source = source_commit(root, ticket, expected)
    return {"ticket": ticket, "status": "finalized", "sourceCommit": source,
            "files": paths, "tests": {"passed": passed, "failed": failed}}


def land(root, ticket, base):
    """Cherry-pick exactly one clean, detached commit; leave main unchanged on conflict."""
    root = repository(root)
    if interrupted_cherry_pick(root):
        raise WorktreeError("Git cherry-pick is interrupted; resolve or abort manually before landing")
    source = source_commit(root, ticket, base)
    existing = find_landing(root, source)
    if existing:
        return {"ticket": ticket, "status": "landed", "sourceCommit": source,
                "landedCommit": existing, "recovered": True}
    if source_dirty(root):
        raise WorktreeError("Main source checkout must be clean before landing")
    commit = git(root, "cherry-pick", "-x", source, check=False)
    if commit.returncode:
        git(root, "cherry-pick", "--abort", check=False)
        details = (commit.stderr or commit.stdout or "unknown Git error").strip()[:900]
        raise WorktreeError("Landing failed; cherry-pick aborted: " + details)
    return {"ticket": ticket, "status": "landed", "sourceCommit": source,
            "landedCommit": git(root, "rev-parse", "HEAD").stdout.strip(),
            "recovered": False}

def remove(root, ticket, acknowledge_loss=False):
    root = repository(root)
    target = safe_target(root, ticket)
    if not target.is_dir():
        raise WorktreeError("Worktree missing")
    if git(target, "status", "--porcelain").stdout.strip():
        raise WorktreeError("Refusing to remove a worktree with uncommitted files")
    head = git(target, "rev-parse", "HEAD").stdout.strip()
    if not acknowledge_loss and git(root, "merge-base", "--is-ancestor", head, "HEAD", check=False).returncode:
        raise WorktreeError("Worktree commit is not an ancestor of main; acknowledge lost refs explicitly")
    git(root, "worktree", "remove", str(target))
    return {"ticket": ticket, "status": "removed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "status", "land", "recover", "remove"])
    parser.add_argument("ticket")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base", default="HEAD",
                        help="Base commit. Required (as SHA) for land.")
    parser.add_argument("--acknowledge-loss", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "create":
            value = create(args.root, args.ticket, args.base)
        elif args.action == "status":
            value = status(args.root, args.ticket)
        elif args.action == "land":
            value = land(args.root, args.ticket, args.base)
        elif args.action == "recover":
            value = recover(args.root, args.ticket, args.base)
        else:
            value = remove(args.root, args.ticket, args.acknowledge_loss)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (WorktreeError, OSError) as e:
        print(json.dumps({"status": "blocked", "error": str(e)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
