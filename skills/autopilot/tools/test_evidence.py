#!/usr/bin/env python3
"""Host-owned Python unittest or offline Cargo evidence for isolated tickets.

Runs operator-approved, unchanged baseline-tracked Python unittest or
restricted frozen/offline Cargo integration tests in the exact
executor worktree and checks the checkout fingerprint before/after. It does
not trust the model's "N/0" text or execute arbitrary shell command strings.
Test binaries/code run as the host user and require independent operator trust.
"""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

import worktrees


class EvidenceError(ValueError):
    pass


SUITE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]{0,180}\.py$")
RAN = re.compile(r"(?m)^Ran (\d+) tests? in [\d.]+s\s*$")

CARGO_SUITE = re.compile(r"cargo:([a-zA-Z][a-zA-Z0-9_-]{0,63})\Z")
CARGO_RESULT = re.compile(
    r"(?m)^test result: ok\. (\d+) passed; (\d+) failed; "
    r"(\d+) ignored; (\d+) measured; (\d+) filtered out;")
IGNORED_RUST_PATTERNS = (
    ":(icase)*.rs", ":(icase)*.toml", ":(icase)*.lock",
    ":(icase).cargo/config", ":(icase).cargo/config.toml",
)


def git_bytes(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, timeout=20)
    if p.returncode:
        raise EvidenceError("Cannot determine tested checkout status")
    return p.stdout


# Ignored Python source, bytecode or importable extension modules are
# unreviewed executable inputs. They are absent from ordinary Git status and
# cannot be attested by hashing only tracked/nonignored files.
IGNORED_PYTHON_PATTERNS = tuple(
    ":(icase)*" + ext for ext in (
        ".py", ".pyw", ".pyc", ".pyo", ".pyd", ".so",
        ".pth", ".zip", ".egg", ".whl",
    )
)


def reject_ignored_python(target):
    ignored = git_bytes(
        target, "ls-files", "--others", "--ignored", "--exclude-standard",
        "-z", "--", *IGNORED_PYTHON_PATTERNS)
    if ignored.strip(b"\0"):
        # Avoid printing filenames: ignored paths may contain private names.
        raise EvidenceError("Ignored Python inputs in test worktree; "
                            "remove them or obtain independent operator review")


def reject_ignored_rust(target):
    ignored = git_bytes(
        target, "ls-files", "--others", "--ignored", "--exclude-standard",
        "-z", "--", *IGNORED_RUST_PATTERNS)
    if ignored.strip(b"\0"):
        raise EvidenceError(
            "Ignored Cargo/Rust inputs in test worktree; independent review required")


def fingerprint(target):
    """Hash tracked changes, index and exact untracked file bytes (including paths)."""
    target = Path(target).resolve()
    reject_ignored_python(target)
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


def checked_baseline_cargo(target, suite):
    """A single unchanged baseline-tracked Cargo integration test; no options."""
    match = CARGO_SUITE.fullmatch(suite) if isinstance(suite, str) else None
    if not match:
        raise EvidenceError("Cargo suite must be cargo:<integration-test-name>")
    name = match.group(1)
    # Cargo can execute project build scripts, dependencies and test code:
    # baseline selection is an operator trust decision, not a sandbox.
    for rel in ("Cargo.toml", "Cargo.lock", "tests/" + name + ".rs"):
        path = Path(target) / rel
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(
                Path(target).resolve()):
            raise EvidenceError("Cargo baseline manifest, lock or test missing/redirected")
        if subprocess.run(
                ["git", "-C", str(target), "cat-file", "-e", "HEAD:" + rel],
                capture_output=True, timeout=20).returncode:
            raise EvidenceError("Cargo manifest, lock and integration suite must be baseline-tracked")
        if subprocess.run(
                ["git", "-C", str(target), "diff", "--quiet", "HEAD", "--", rel],
                capture_output=True, timeout=20).returncode:
            raise EvidenceError("Modified Cargo manifest, lock or test suite needs independent review")
    for candidate in (".cargo/config", ".cargo/config.toml"):
        if (Path(target) / candidate).exists():
            raise EvidenceError("Cargo project config requires independent review")
    reject_ignored_rust(target)
    # Deliberately narrow initial host-backed adapter: dependency-free package,
    # no build scripts or Cargo workspace configuration. This keeps dependency
    # resolution, custom build-script execution and external source trees out of
    # the pilot. Broader operator-attested Cargo graphs need a separate review.
    try:
        with (Path(target) / "Cargo.toml").open("rb") as manifest_stream:
            manifest = tomllib.load(manifest_stream)
    except (OSError, ValueError) as exc:
        raise EvidenceError("Invalid baseline Cargo manifest") from exc
    package = manifest.get("package")
    if not isinstance(package, dict) or "workspace" in manifest:
        raise EvidenceError("Cargo verifier currently requires standalone crate")
    lib = manifest.get("lib") or {}
    if not isinstance(lib, dict):
        raise EvidenceError("Invalid Cargo library definition")
    if ((Path(target) / "build.rs").exists()
            or package.get("build") not in (None, False)
            or lib.get("proc-macro") is True):
        raise EvidenceError("Cargo build scripts/proc-macros require independent review")
    if any(key in manifest for key in (
            "dependencies", "dev-dependencies", "build-dependencies",
            "patch", "replace", "target", "workspace", "test", "bench")):
        raise EvidenceError("Cargo external dependencies require independent review")
    return name


def run_cargo(target, suite, timeout):
    name = checked_baseline_cargo(target, suite)
    cargo = shutil.which("cargo")
    if not cargo:
        raise EvidenceError("Cargo binary unavailable on verified test host")
    # No user-provided command strings/flags. Frozen forbids network and lock
    # updates; private target and home prevent use of project target and
    # inherited Cargo configs. The Rust toolchain itself is host trusted.
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith(("CARGO_", "RUST", "RUSTUP_"))}
    env["CARGO_NET_OFFLINE"] = "true"
    env["CARGO_TERM_COLOR"] = "never"
    try:
        with tempfile.TemporaryDirectory(prefix="autopilot-cargo-") as build:
            env["CARGO_HOME"] = str(Path(build) / "cargo-home")
            env["CARGO_TARGET_DIR"] = str(Path(build) / "target")
            result = subprocess.run(
                [cargo, "test", "--frozen", "--quiet",
                 "--manifest-path", str(Path(target) / "Cargo.toml"),
                 "--test", name, "--", "--test-threads=1"],
                cwd=target, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout, env=env)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise EvidenceError("Cargo tests could not complete within host limits") from exc
    output = result.stdout + "\n" + result.stderr
    results = CARGO_RESULT.findall(output)
    if result.returncode or len(results) != 1:
        raise EvidenceError("Independent host Cargo integration test did not pass")
    passed, failed, ignored, measured, filtered = map(int, results[0])
    if passed < 1 or any((failed, ignored, measured, filtered)):
        raise EvidenceError("Cargo test gate requires positive, unfiltered, unignored N/0")
    return passed


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

    runner = "cargo-test" if isinstance(suite, str) and suite.startswith("cargo:") else "python-unittest"
    if runner == "cargo-test":
        checked_baseline_cargo(target, suite)
    else:
        checked_suite(target, suite)
    before = fingerprint(target)
    if runner == "cargo-test":
        passed = run_cargo(target, suite, timeout)
        after = fingerprint(target)
        reject_ignored_rust(target)
        if before != after:
            raise EvidenceError("Worktree changed while running tests; results invalidated")
        return {"status": "verified", "runner": runner, "suite": suite,
                "fingerprint": after, "baseCommit": base, "workerHead": head,
                "passed": passed, "failed": 0, "timeout": timeout,
                "verifiedAt": datetime.now(timezone.utc).isoformat()}
    # Avoid inheriting PYTHONPATH/PYTHONHOME/etc. from the controlling host.
    # Otherwise an external module can satisfy tests without being represented
    # in the ticket's worktree fingerprint. Preserve non-Python OS variables.
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith("PYTHON")}
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
            or evidence.get("runner") not in ("python-unittest", "cargo-test")
            or evidence.get("baseCommit") != base
            or type(evidence.get("passed")) is not int or evidence["passed"] < 1
            or evidence.get("failed") != 0):
        raise EvidenceError("Missing confirmed host test evidence")
    actual = worktrees.status(root, ticket)
    if actual.get("status") != "present":
        raise EvidenceError("Evidence checkout missing")
    if worktrees.git(actual["cwd"], "rev-parse", "HEAD").stdout.strip() != evidence.get("workerHead"):
        raise EvidenceError("Executor commit changed after verification")
    if evidence["runner"] == "cargo-test":
        checked_baseline_cargo(actual["cwd"], evidence.get("suite"))
    else:
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
    if observed["runner"] != evidence["runner"]:
        raise EvidenceError("Host test runner differs from approved receipt")
    if observed["passed"] != evidence["passed"]:
        raise EvidenceError("Claimed test count differs from independent host run")
    if (observed["fingerprint"] != evidence["fingerprint"]
            or observed["workerHead"] != evidence["workerHead"]):
        raise EvidenceError("Source changed during independent host verification")
    return {"passed": observed["passed"], "failed": 0}
