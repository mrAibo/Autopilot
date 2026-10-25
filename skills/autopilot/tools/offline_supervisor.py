#!/usr/bin/env python3
"""Offline P0 worker supervisor; never dispatches paid model or arbitrary commands.

Only pre-reviewed synthetic fixtures in an isolated Git repo beneath the OS
temp directory can execute. A durable single-use receipt is claimed *before*
subprocess launch. Cancellation is cooperative with this live supervisor:
a second CLI request writes a cancellation marker, and the original supervisor
terminates its own child by process handle. A crashed supervisor is uncertain;
NEVER silently replay the ticket.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import secrets
import signal
import subprocess
import sys
import tempfile
import time

import controller
import process_containment
import worktrees

MARKER = "AUTOPILOT_OFFLINE_TEMP_FIXTURE_V1\n"
OPERATIONS = {
    "calc-add": "src/core/",
    "calc-mul": "src/bot/",
}


class OfflineError(ValueError):
    pass


def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def folder(root):
    base = Path(root) / ".autopilot"
    path = base / "offline-worker"
    if not base.is_dir() or base.is_symlink():
        raise OfflineError("Missing or redirected Autopilot metadata")
    if path.is_symlink():
        raise OfflineError("Redirected offline receipt directory")
    return path


def receipt_path(root, ticket):
    if not re.fullmatch(r"[0-9]{2,4}", ticket):
        raise OfflineError("Invalid ticket ID")
    return folder(root) / (ticket + ".json")


def read_receipt(root, ticket):
    path = receipt_path(root, ticket)
    if path.is_symlink():
        raise OfflineError("Redirected offline receipt")
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OfflineError("Unreadable offline receipt: inspect manually") from exc
    if not isinstance(data, dict) or data.get("ticket") != ticket:
        raise OfflineError("Offline receipt identity mismatch")
    return data


def persist(path, content):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, prefix=path.name + "-",
                                         suffix=".tmp", delete=False) as out:
            tmp = Path(out.name)
            os.chmod(tmp, 0o600)
            json.dump(content, out, ensure_ascii=False, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def claim(root, ticket, summary):
    directory = folder(root)
    directory.mkdir(mode=0o700, exist_ok=True)
    path = directory / (ticket + ".json")
    if path.is_symlink():
        raise OfflineError("Redirected offline receipt")
    # Non-replayable even if the launcher crashes after this atomic claim.
    try:
        handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise OfflineError("Previous attempt exists; inspect and never replay") from exc
    rec = {"ticket": ticket, "status": "invocation-uncertain",
           "claimed_at": utcnow(), "supervisor_pid": os.getpid(),
           "claim_id": secrets.token_hex(16),
           "fixture": summary["fixture"], "model_invoked": False,
           "cwd": summary["cwd"],
           "note": "Synthetic local process only. Receipt forbids replay."}
    with os.fdopen(handle, "w", encoding="utf-8") as out:
        json.dump(rec, out, sort_keys=True)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    return path, rec


def preflight(root, ticket, fixture, *, delay=0, fail=False, timeout=30):
    root = Path(root).resolve()
    temp = Path(tempfile.gettempdir()).resolve()
    if root == temp or not root.is_relative_to(temp):
        raise OfflineError("Offline fixture runs ONLY under the OS temp directory")
    if fixture not in OPERATIONS:
        raise OfflineError("Unknown offline fixture")
    if type(delay) not in (float, int) or not 0 <= delay <= 20:
        raise OfflineError("Offline delay must be 0-20 seconds")
    if type(timeout) is not int or not 2 <= timeout <= 60:
        raise OfflineError("Offline timeout must be 2-60 seconds")
    marker = root / ".autopilot" / "offline-test-consent"
    if marker.is_symlink() or not marker.is_file() or (
            marker.read_text(encoding="utf-8") != MARKER):
        raise OfflineError("Missing explicit offline-only fixture marker")
    if worktrees.repository(root) != root:
        raise OfflineError("Expected temporary Git repository root")
    state = controller.read_state(root)
    step = controller.decision(root, state)
    if step != {"action": "blocked", "ticket": ticket,
                "reason": "await-separately-approved-pinned-worker"}:
        raise OfflineError("Trusted host not waiting for this exact clean ticket")
    active = [t for t in state["tickets"] if t.get("status") == "in-progress"]
    if len(active) != 1 or active[0]["id"] != ticket:
        raise OfflineError("Expected one active ticket")
    task = active[0]
    if task.get("zone") != [OPERATIONS[fixture]]:
        raise OfflineError("Fixture source zone must exactly match ticket")
    wt = task.get("worktree") or {}
    target = Path(wt.get("cwd", root)).resolve()
    if not target.is_relative_to(root):
        raise OfflineError("Worker checkout escapes temporary root")
    stub = Path(__file__).resolve().parent / "offline_fixture_worker.py"
    if stub.is_symlink() or not stub.is_file():
        raise OfflineError("Missing trusted offline fixture executable")
    gate = Path(__file__).resolve().parent / "process_gate.py"
    if gate.is_symlink() or not gate.is_file():
        raise OfflineError("Missing trusted process start gate")
    if read_receipt(root, ticket) is not None:
        raise OfflineError("Previous attempt exists; never replay")
    return {"ticket": ticket, "fixture": fixture, "cwd": str(target),
            "timeout": timeout, "delay": delay, "fail": bool(fail),
            "stub": str(stub), "gate": str(gate), "model_invoked": False}


def cancel_request(root, ticket):
    root = Path(root).resolve()
    rec = read_receipt(root, ticket)
    if rec is None:
        raise OfflineError("No offline dispatch receipt to cancel")
    if rec.get("status") not in ("invocation-uncertain", "running"):
        return {"status": "no-active-worker", "ticket": ticket,
                "recorded_status": rec.get("status"), "model_invoked": False}
    marker = folder(root) / (ticket + ".cancel")
    if marker.is_symlink():
        raise OfflineError("Redirected cancellation marker")
    request = {"ticket": ticket, "claim_id": rec.get("claim_id"),
               "requested_at": utcnow()}
    if not isinstance(request["claim_id"], str) or len(request["claim_id"]) != 32:
        raise OfflineError("Cannot identify worker claim for cancellation")
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(request, out, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    except FileExistsError:
        try:
            existing = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise OfflineError("Malformed cancel marker; inspect manually") from exc
        if (existing.get("ticket") != ticket or
                existing.get("claim_id") != request["claim_id"]):
            raise OfflineError("Cancel request targets a different claim")
    return {"status": "cancel-requested", "ticket": ticket,
            "claim_id": request["claim_id"],
            "note": "Await terminal receipt acknowledgement; never kill a saved PID",
            "model_invoked": False}


def stop_child(process, job=None):
    """Only the owner terminates its live child; never trust persisted PIDs."""
    if process.poll() is not None:
        return
    if os.name == "nt" and job is not None:
        job.terminate()
    elif os.name != "nt":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        raise OfflineError("Windows child lacks Job Object; refuse unsafe fallback")
    if process.poll() is None:
        process.kill()


def launch(root, ticket, fixture, *, execute=False, approval=None,
           delay=0, fail=False, timeout=30):
    root = Path(root).resolve()
    if not execute and approval is not None:
        raise OfflineError("Approval requires --execute")
    if execute and approval != ticket:
        raise OfflineError("Use --approve-offline-ticket matching --ticket")
    if not execute:
        summary = preflight(root, ticket, fixture, delay=delay,
                            fail=fail, timeout=timeout)
        return {"status": "dry-run", "preview": summary,
                "model_invoked": False}
    # Hold controller lock across the child lifetime. This blocks host Git
    # transitions while the worktree is being written, not cancel requests.
    with controller.controller_lock(root):
        summary = preflight(root, ticket, fixture, delay=delay,
                            fail=fail, timeout=timeout)
        path, record = claim(root, ticket, summary)
        flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        # First launch a gated wrapper. It cannot start the fixture until the
        # owner assigns it to the Windows KILL_ON_JOB_CLOSE kernel object.
        args = [sys.executable, "-B", summary["gate"], summary["stub"],
                "--worktree", summary["cwd"], "--fixture", fixture,
                "--delay", str(delay)]
        if fail:
            args.append("--fail")
        child = None
        job = None
        began = time.monotonic()
        try:
            job = process_containment.OwnedJob()
            child = subprocess.Popen(
                args, cwd=summary["cwd"], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                creationflags=flags, start_new_session=(os.name != "nt"))
            # Failed containment assignment means NO worker action: the
            # wrapper remains blocked on stdin and is terminated on close.
            job.assign(child)
            record["containment"] = job.mode
            record.update({"status": "running", "child_pid": child.pid,
                           "started_at": utcnow()})
            child.stdin.write("START\n")
            child.stdin.flush()
            child.stdin.close()
            child.stdin = None
            persist(path, record)
            marker = folder(root) / (ticket + ".cancel")
            reason = None
            while True:
                if marker.is_symlink():
                    reason = "unsafe-cancel-marker"
                    break
                if marker.exists():
                    try:
                        request = json.loads(marker.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        reason = "unsafe-cancel-marker"
                        break
                    if (not isinstance(request, dict) or
                            request.get("ticket") != ticket or
                            request.get("claim_id") != record["claim_id"]):
                        reason = "unsafe-cancel-marker"
                    else:
                        reason = "cancelled"
                        record["cancel_acknowledged_at"] = utcnow()
                        record["cancel_requested_at"] = request["requested_at"]
                    break
                if time.monotonic() - began >= timeout:
                    reason = "timed-out"
                    break
                if child.poll() is not None:
                    break
                time.sleep(0.05)
            if reason is not None:
                stop_child(child, job)
            try:
                out, err = child.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                stop_child(child, job)
                out, err = child.communicate(timeout=5)
                reason = reason or "timed-out"
            status = reason or ("completed" if child.returncode == 0 else "failed")
            record.update({"status": status, "completed_at": utcnow(),
                           "exit_code": child.returncode,
                           "stdout_tail": out[-400:],
                           "stderr_tail": err[-400:],
                           "model_invoked": False})
        except BaseException:
            if child is not None:
                stop_child(child, job)
            record.update({"status": "invocation-uncertain",
                           "model_invoked": False,
                           "diagnostic": "Supervisor interrupted; inspect Git/process"})
            persist(path, record)
            raise
        finally:
            if job is not None:
                job.close()
        persist(path, record)
        return {"status": record["status"], "ticket": ticket,
                "receipt": str(path), "model_invoked": False,
                "exit_code": record.get("exit_code")}


def inspect(root, ticket):
    """Read-only receipt report; never infer liveness from a PID on disk."""
    receipt = read_receipt(Path(root).resolve(), ticket)
    if receipt is None:
        return {"status": "no-attempt", "ticket": ticket,
                "model_invoked": False}
    terminal = receipt.get("status") in (
        "completed", "failed", "cancelled", "timed-out", "unsafe-cancel-marker")
    return {"status": "recorded", "ticket": ticket,
            "recorded_status": receipt.get("status"),
            "claim_id": receipt.get("claim_id"),
            "containment": receipt.get("containment"),
            "cancel_acknowledged": bool(receipt.get("cancel_acknowledged_at")),
            "manual_reconciliation_required": not terminal,
            "note": "Recorded receipt does not attest a live process; no automatic retry",
            "model_invoked": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--fixture", choices=sorted(OPERATIONS))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-offline-ticket")
    parser.add_argument("--cancel", action="store_true",
                        help="Create a cancel marker; never kill a saved PID")
    parser.add_argument("--status", action="store_true",
                        help="Read the durable receipt without trusting a saved PID")
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.status:
            if args.cancel or args.execute or args.approve_offline_ticket or args.fixture:
                raise OfflineError("Status is strictly read-only")
            result = inspect(args.root, args.ticket)
        elif args.cancel:
            if args.execute or args.approve_offline_ticket or args.fixture:
                raise OfflineError("Cancel cannot be combined with launch flags")
            result = cancel_request(args.root, args.ticket)
        else:
            if args.fixture is None:
                raise OfflineError("--fixture required")
            result = launch(args.root, args.ticket, args.fixture,
                            execute=args.execute,
                            approval=args.approve_offline_ticket,
                            delay=args.delay, fail=args.fail,
                            timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in ("dry-run", "completed",
                "cancelled", "cancel-requested", "no-active-worker",
                "recorded", "no-attempt") else 2
    except (OfflineError, controller.ControllerError, worktrees.WorktreeError,
            ValueError, TypeError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:300],
                          "model_invoked": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
