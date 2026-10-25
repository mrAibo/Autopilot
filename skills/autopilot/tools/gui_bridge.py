#!/usr/bin/env python3
"""Explicit one-shot, fail-closed bridge from Codex/Claude GUI to pinned Codex CLI.

The GUI can invoke this local command (if host tools permit); no native
subagent is claimed. Default is READ-ONLY. Paid dispatch requires explicit
--execute --approve-ticket ID, a recorded positive token threshold, and
an unused durable attempt receipt. Any uncertain attempt is non-replayable.
Never trust arbitrary shell or model-supplied commands.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import subprocess
import tempfile

import codex_dispatch
import codex_capabilities
import controller
import worktrees


class BridgeError(ValueError):
    pass


def consent_preflight(root, ticket, executable=None, sandbox="workspace-write",
                      optimization="off", timeout=900):
    """Validate project, next host action, authenticated pinned route and budget."""
    root = Path(root).resolve()
    if not re.fullmatch(r"[0-9]{2,4}", ticket):
        raise BridgeError("Invalid ticket ID")
    if not 20 <= timeout <= 1800:
        raise BridgeError("Timeout must be 20-1800 seconds")
    if worktrees.repository(root) != root:
        raise BridgeError("Expected Git repository root")
    state = controller.read_state(root)
    next_step = controller.decision(root, state)
    if next_step != {"action": "blocked", "ticket": ticket,
                     "reason": "await-separately-approved-pinned-worker"}:
        raise BridgeError("Host controller is not waiting for this clean ticket worker")
    active = [t for t in state["tickets"] if t.get("status") in controller.scheduler.ACTIVE]
    if len(active) != 1 or active[0]["id"] != ticket:
        raise BridgeError("Expected exactly one active approved ticket")
    budget = state.get("budgetTokens")
    if type(budget) is not int or budget <= 0:
        raise BridgeError("Explicit positive recorded token threshold required")
    events = state.get("usageEvents")
    if not isinstance(events, list):
        raise BridgeError("Invalid usage ledger")
    total = 0
    for event in events:
        if (not isinstance(event, dict) or
                type(event.get("input")) is not int or
                type(event.get("output")) is not int or
                min(event["input"], event["output"]) < 0):
            raise BridgeError("Invalid usage event prevents budget check")
        total += event["input"] + event["output"]
    if total >= budget:
        raise BridgeError("Recorded token threshold exceeded")
    # Keep dispatch and its pinned profile/brief validation in ONE place.
    config = codex_dispatch.checked_dispatch(root, ticket, executable,
                                             sandbox, optimization)
    return config, {"ticket": ticket, "model": config["model"],
                    "effort": config["effort"], "sandbox": sandbox,
                    "timeout_seconds": timeout,
                    "recorded_used_tokens": total,
                    "recorded_budget_tokens": budget,
                    "recorded_remaining_tokens": budget-total,
                    "working_directory": config["cwd"],
                    "optimization": optimization}


def receipt_dir(root):
    base = Path(root) / ".autopilot"
    if not base.is_dir() or base.is_symlink():
        raise BridgeError("Unsafe project Autopilot directory")
    receipts = base / "gui-dispatch"
    if receipts.is_symlink():
        raise BridgeError("Refusing redirected dispatch receipts directory")
    if not receipts.exists():
        receipts.mkdir(mode=0o700)
    if not receipts.is_dir() or receipts.is_symlink():
        raise BridgeError("Unsafe dispatch receipts directory")
    return receipts


def receipt_path(root, ticket):
    return Path(root) / ".autopilot" / "gui-dispatch" / (ticket + ".json")


def receipt_status(root, ticket):
    if not re.fullmatch(r"[0-9]{2,4}", ticket):
        raise BridgeError("Invalid ticket ID")
    path = receipt_path(root, ticket)
    if path.is_symlink():
        raise BridgeError("Refusing redirected dispatch receipt")
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BridgeError("Dispatch receipt damaged; manual inspection required") from exc
    if not isinstance(value, dict) or value.get("ticket") != ticket:
        raise BridgeError("Dispatch receipt identity mismatch")
    return value


def atomic_json_replace(path, data):
    """Preserve a receipt on partial writes, even when model work has failed."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         prefix=path.name + "-", suffix=".tmp",
                                         dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            os.chmod(f.name, 0o600)
            json.dump(data, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def claim_attempt(root, ticket, config, summary):
    directory = receipt_dir(root)
    path = directory / (ticket + ".json")
    if path.exists() or path.is_symlink():
        raise BridgeError("Attempt already recorded; NEVER silently dispatch twice")
    created = dt.datetime.now(dt.timezone.utc).isoformat()
    record = {"ticket": ticket, "status": "invocation-uncertain",
              "claimed_at": created, "pid": os.getpid(),
              "dispatch_fingerprint": hashlib.sha256(config["prompt"].encode("utf-8")).hexdigest(),
              "approved": summary, "model_invoked": "unknown",
              "note": "Durable claim written before external process; no automatic replay"}
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise BridgeError("Attempt exists: inspect receipt and provider usage first") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Keep the possibly partial claim to forbid accidental repeated billing.
        raise
    return path, record


def bridge(root, ticket, *, execute=False, approval=None, executable=None,
           sandbox="workspace-write", optimization="off", timeout=900):
    """Dry-run is strictly read-only. Execution needs direct positive consent."""
    root = Path(root).resolve()
    if execute and approval != ticket:
        raise BridgeError("Paid execution needs --approve-ticket matching --ticket")
    if not execute and approval is not None:
        raise BridgeError("Approval may only accompany --execute")
    if not execute:
        config, summary = consent_preflight(root, ticket, executable, sandbox,
                                            optimization, timeout)
        prior = receipt_status(root, ticket)
        return {"status": "dry-run" if prior is None else "blocked",
                "reason": "previous-attempt-requires-reconciliation" if prior else "",
                "approved_invocation": False, "model_invoked": False,
                "ticket": ticket, "preview": summary,
                "next_action": ("run --execute --approve-ticket " + ticket
                                if prior is None else "inspect existing receipt")}
    with controller.controller_lock(root):
        # Re-check all invariants under the host lock, including receipt.
        existing = receipt_status(root, ticket)
        if existing is not None:
            return {"status": "blocked", "reason": "previous-attempt-requires-reconciliation",
                    "ticket": ticket, "receipt": str(receipt_path(root, ticket)),
                    "model_invoked": False}
        config, summary = consent_preflight(root, ticket, executable, sandbox,
                                            optimization, timeout)
        path, record = claim_attempt(root, ticket, config, summary)
        try:
            result = codex_dispatch.run_once(config, root, timeout=timeout)
            # Existing executor accounts actual JSONL input/cache/output through ap.py.
            # No child/GUI-native claim and no automatic finalize/land acceptance.
            record.update({"status": result["status"],
                           "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                           # Failed or incomplete CLI process does not prove
                           # the provider ever received the billable request.
                           "model_invoked": True if result["status"] == "ready-for-review"
                                            else "unknown",
                           "worker_commit": result.get("worker_commit"),
                           "turn_completed": result.get("turn_completed"),
                           "tests_verified": False,
                           "accepted": False,
                           "usage_recorded": result.get("usage_recorded"),
                           "usage": result.get("usage")})
        except Exception as exc:
            record.update({"status": "invocation-uncertain",
                           "model_invoked": "unknown",
                           "diagnostic": type(exc).__name__ +
                           ": check provider/account usage and worktree manually"})
        atomic_json_replace(path, record)
        return {"status": record["status"], "ticket": ticket,
                "model_invoked": record["model_invoked"],
                "receipt": str(path),
                "worker_commit": record.get("worker_commit"),
                "usage_recorded": record.get("usage_recorded", False),
                "tests_verified": False, "accepted": False,
                "next_action": ("Use controller --suite TEST --advance only after "
                                "independent trusted test verification; never replay paid call")}



def runtime_doctor(root, ticket, *, executable=None, sandbox="workspace-write",
                   optimization="off", timeout=900, catalog_timeout=25):
    """Read-only check of the ACTUAL CLI binary and fresh account catalog.

    Catalog visibility does not prove authentication at inference time or
    attest that a provider call used the model. This function never sends
    a prompt, creates an attempt receipt or writes the project ledger.
    """
    if not 5 <= catalog_timeout <= 60:
        raise BridgeError("Runtime catalog timeout must be 5-60 seconds")
    existing = bridge(root, ticket, executable=executable, sandbox=sandbox,
                      optimization=optimization, timeout=timeout)
    if existing["status"] != "dry-run":
        return {"status": "blocked", "reason": existing.get("reason", "previous attempt"),
                "ticket": ticket, "model_invoked": False}
    config, preflight = consent_preflight(root, ticket, executable, sandbox,
                                         optimization, timeout)
    binary = config["binary"]
    try:
        models = codex_capabilities.discover(binary, timeout=catalog_timeout)
    except (codex_capabilities.CatalogError, OSError, subprocess.TimeoutExpired) as exc:
        raise BridgeError("Native Codex runtime catalog check failed") from exc
    if config["effort"] not in models.get(config["model"], []):
        raise BridgeError("Pinned model/Effort not in the CURRENT Codex CLI catalog")
    try:
        version = subprocess.run([binary, "--version"], capture_output=True,
                                 text=True, encoding="utf-8", errors="replace",
                                 timeout=catalog_timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BridgeError("Native Codex CLI version check timed out or failed") from exc
    if version.returncode:
        raise BridgeError("Native Codex CLI version check failed")
    label = version.stdout.strip().splitlines()
    if not label or not label[0].startswith("codex-cli "):
        raise BridgeError("Native binary version is not a recognized Codex CLI")
    try:
        help_result = subprocess.run([binary, "exec", "--help"],
                                     capture_output=True, text=True,
                                     encoding="utf-8", errors="replace",
                                     timeout=catalog_timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BridgeError("Native Codex CLI exec help timed out or failed") from exc
    if help_result.returncode:
        raise BridgeError("Native Codex CLI exec help check failed")
    help_text = help_result.stdout + help_result.stderr
    required = ("--model", "--cd", "--sandbox", "--ephemeral",
                "--ignore-user-config", "--json")
    missing = [option for option in required if option not in help_text]
    if missing:
        raise BridgeError("Native Codex CLI is missing required exec switches")
    return {"status": "ready", "ticket": ticket,
            "binary": binary, "cli_version": label[0][:100],
            "model": config["model"], "effort": config["effort"],
            "current_catalog_model_effort": True,
            "required_exec_switches": list(required),
            "runtime_compatible": True,
            "verified_provider_execution": False,
            "model_invoked": False,
            "provider_budget_hard_cap": False,
            "preview": preflight}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--ticket", required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--check-runtime", action="store_true",
                   help="Read-only binary/version/switches/current-model check; no model call")
    p.add_argument("--approve-ticket", help="Explicit consent to one potentially billable call")
    p.add_argument("--codex-exe", type=Path)
    p.add_argument("--sandbox", choices=["workspace-write", "read-only"],
                   default="workspace-write")
    p.add_argument("--optimization", choices=["off", "lean"], default="off")
    p.add_argument("--timeout", type=int, default=900)
    args = p.parse_args(argv)
    try:
        if args.check_runtime:
            if args.execute or args.approve_ticket:
                raise BridgeError("Read-only --check-runtime cannot combine with paid approval")
            result = runtime_doctor(args.root, args.ticket, executable=args.codex_exe,
                                    sandbox=args.sandbox, optimization=args.optimization,
                                    timeout=args.timeout)
        else:
            result = bridge(args.root, args.ticket, execute=args.execute,
                            approval=args.approve_ticket, executable=args.codex_exe,
                            sandbox=args.sandbox, optimization=args.optimization,
                            timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in ("dry-run", "ready", "ready-for-review") else 2
    except (BridgeError, controller.ControllerError, codex_dispatch.DispatchError,
            worktrees.WorktreeError, OSError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)[:500],
                          "model_invoked": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
