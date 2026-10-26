#!/usr/bin/env python3
"""Host-owned Python unittest evidence for strict isolated Autopilot tickets.

This module runs a baseline-tracked, unchanged unittest module in the exact
executor worktree and checks the checkout fingerprint before/after. It does
not trust the model's "N/0" text or execute arbitrary shell command strings.
Unit tests themselves execute Python code and must be trusted by the operator.
"""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys

import worktrees


class EvidenceError(ValueError):
    pass


SUITE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]{0,180}\.py$")
RAN = re.compile(r"(?m)^Ran (\d+) tests? in [\d.]+s\s*$")


def git_bytes(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, timeout=20)
    if p.returncode:
        raise EvidenceError("Cannot determine tested checkout status")
    return p.stdout


def fingerprint(target):
    """Hash tracked changes, index and exact untracked file bytes (including paths)."""
    target = Path(target).resolve()
    digest = hashlib.sha256()
    digest.update(git_bytes(target, "rev-parse", "HEAD"))
    digest.update(git_bytes(target, "diff", "--binary", "HEAD", "--"))
    other = git_bytes(target, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    for raw in sorted(x for x in other if x):
        name = os.fsdecode(raw)
        path = target / name
        if (path.is_symlink() or not path.is_file()
                or not path.resolve().is_relative_to(target)):
            raise EvidenceError("Unsafe untracked file in test worktree")
        if path.stat().st_size > 25_000_000:
            raise EvidenceError("Untracked file exceeds safe evidence size")
        digest.update(raw)
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def checked_suite(target, suite):
    if not isinstance(suite, str) or not SUITE.fullmatch(suite):
        raise EvidenceError("Use one baseline-tracked .py test module, e.g. test_calc.py")
    parts = suite.replace("\\", "/").split("/")
    if any(part in (".", "..", "") for part in parts):
        raise EvidenceError("Test module path may not escape worktree")
    if parts[0] in (".git", ".autopilot"):
        raise EvidenceError("Internal metadata cannot be a test suite")
    test_path = Path(target) / suite
    if (not test_path.is_file() or test_path.is_symlink()
            or not test_path.resolve().is_relative_to(Path(target).resolve())):
        raise EvidenceError("Test file missing or redirected")
    if subprocess.run(["git", "-C", str(target), "cat-file", "-e", "HEAD:" + suite],
                      capture_output=True, timeout=20).returncode:
        raise EvidenceError("Test suite must exist unchanged in base commit")
    if subprocess.run(["git", "-C", str(target), "diff", "--quiet", "HEAD", "--", suite],
                      capture_output=True, timeout=20).returncode:
        raise EvidenceError("Modified test suite needs independent operator review")
    return test_path


def verify(root, ticket, base, suite, timeout=90):
    if type(timeout) is not int or not 10 <= timeout <= 300:
        raise EvidenceError("Test timeout must be 10–300 seconds")
    root = worktrees.repository(root)
    actual = worktrees.status(root, ticket)
    if actual.get("status") != "present":
        raise EvidenceError("Test checkout does not exist")
    target = Path(actual["cwd"]).resolve()
    head = worktrees.git(target, "rev-parse", "HEAD").stdout.strip()
    if head != base:
        worktrees.source_commit(root, ticket, base)  # one clean committed executor diff

    checked_suite(target, suite)
    before = fingerprint(target)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    try:
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", suite],
                                cwd=target, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        raise EvidenceError("Tests exceeded the host timeout") from exc
    after = fingerprint(target)
    if before != after:
        raise EvidenceError("Worktree changed while running tests; results invalidated")
    logs = (result.stdout + "\n" + result.stderr)[-30000:]
    matches = RAN.findall(logs)
    passed = int(matches[-1]) if matches else 0
    if result.returncode != 0 or not re.search(r"(?m)^OK(?:\s|$)", logs) or passed < 1:
        raise EvidenceError("Independent host tests did not pass")
    return {"status": "verified", "runner": "python-unittest", "suite": suite,
            "fingerprint": after, "baseCommit": base, "workerHead": head,
            "passed": passed, "failed": 0, "timeout": timeout,
            "verifiedAt": datetime.now(timezone.utc).isoformat()}


def check(root, ticket, base, evidence):
    if (not isinstance(evidence, dict) or evidence.get("status") != "verified"
            or evidence.get("runner") != "python-unittest"
            or evidence.get("baseCommit") != base
            or type(evidence.get("passed")) is not int or evidence["passed"] < 1
            or evidence.get("failed") != 0):
        raise EvidenceError("Missing confirmed host test evidence")
    actual = worktrees.status(root, ticket)
    if actual.get("status") != "present":
        raise EvidenceError("Evidence checkout missing")
    if worktrees.git(actual["cwd"], "rev-parse", "HEAD").stdout.strip() != evidence.get("workerHead"):
        raise EvidenceError("Executor commit changed after verification")
    checked_suite(actual["cwd"], evidence.get("suite"))
    if fingerprint(actual["cwd"]) != evidence.get("fingerprint"):
        raise EvidenceError("Source changed after tests; rerun verification")
    # state.js is project data, not a host-signed test receipt. A matching
    # Git fingerprint can be calculated without running tests, so a caller
    # could fabricate '999/0' even when the real suite fails. Re-run the
    # approved baseline-tracked suite in the same worktree before accepting
    # the serialized proof. This also checks for concurrent source changes.
    timeout = evidence.get("timeout", 90)  # legacy 2.3 receipts
    observed = verify(root, ticket, base, evidence["suite"], timeout=timeout)
    if observed["passed"] != evidence["passed"]:
        raise EvidenceError("Claimed test count differs from independent host run")
    if (observed["fingerprint"] != evidence["fingerprint"]
            or observed["workerHead"] != evidence["workerHead"]):
        raise EvidenceError("Source changed during independent host verification")
    return {"passed": observed["passed"], "failed": 0}
