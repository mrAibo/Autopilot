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
    if parent.exists() and parent.resolve() != parent:
        # Parent may resolve elsewhere via symlink; refuse.
        raise WorktreeError("Worktree directory is a symlink")
    if target.is_symlink():
        raise WorktreeError("Worktree path may not be a symlink")
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


def land(root, ticket, base):
    """Cherry-pick exactly one clean, detached commit; leave main unchanged on conflict."""
    root = repository(root)
    target = safe_target(root, ticket)
    if not target.is_dir():
        raise WorktreeError("Worktree missing")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", base):
        raise WorktreeError("A known base commit SHA is required")
    base_sha = git(root, "rev-parse", "--verify", base + "^{commit}").stdout.strip()
    head = git(target, "rev-parse", "HEAD").stdout.strip()
    if git(target, "status", "--porcelain").stdout.strip():
        raise WorktreeError("Executor worktree has uncommitted changes")
    # Autopilot's own ledger is updated during every ticket. Never cherry-pick it;
    # check all user source paths while ignoring only that internal directory.
    if source_dirty(root):
        raise WorktreeError("Main source checkout must be clean before landing")
    count = git(root, "rev-list", "--count", base_sha + ".." + head).stdout.strip()
    if count != "1" or git(target, "rev-parse", head + "^").stdout.strip() != base_sha:
        raise WorktreeError("Executor must have exactly one commit directly on its base")
    if git(root, "rev-list", "--max-count=1", base_sha + ".." + head).stdout.strip() != head:
        raise WorktreeError("Head does not match a single commit after base")
    commit = git(root, "cherry-pick", head, check=False)
    if commit.returncode:
        git(root, "cherry-pick", "--abort", check=False)
        details = (commit.stderr or commit.stdout or "unknown Git error").strip()[:900]
        raise WorktreeError("Landing failed; cherry-pick aborted: " + details)
    return {"ticket": ticket, "status": "landed", "sourceCommit": head,
            "landedCommit": git(root, "rev-parse", "HEAD").stdout.strip()}


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
    parser.add_argument("action", choices=["create", "status", "land", "remove"])
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
        else:
            value = remove(args.root, args.ticket, args.acknowledge_loss)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (WorktreeError, OSError) as e:
        print(json.dumps({"status": "blocked", "error": str(e)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
