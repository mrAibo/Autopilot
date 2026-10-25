#!/usr/bin/env python3
"""Fail-closed Codex CLI executor for one already-approved Autopilot ticket.

Explicit --execute performs one model call in the verified ticket worktree.
Default is dry-run. Does not create a task, choose a model, or merge code.
"""
import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib


class DispatchError(ValueError):
    pass


def load_state(root):
    path = Path(root) / ".autopilot" / "state.js"
    content = path.read_text(encoding="utf-8")
    if content.startswith("window.STATE"):
        content = content.split("=", 1)[1]
    state = json.loads(content)
    if not isinstance(state, dict):
        raise DispatchError("Autopilot state is not an object")
    return state


def choose_binary(explicit=None):
    """Use native binary (not CMD wrappers, which can interpret shell characters)."""
    options = []
    if explicit is not None:
        options = [Path(explicit).expanduser()]
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@openai" / "codex" / "node_modules" / "@openai"
        options = sorted(base.glob("codex-win32-x64/vendor/**/codex.exe"))
    else:
        binary = shutil.which("codex")
        if binary:
            options = [Path(binary)]
    for binary in options:
        if binary.is_file() and (os.name != "nt" or binary.suffix.lower() == ".exe"):
            return str(binary.resolve())
    raise DispatchError("Native codex executable not found; install @openai/codex or pass --codex-exe")


def optimization_rules(mode):
    """Small explicit local policy, inspired by Ponytail, not the upstream plugin."""
    if mode == "off":
        return ""
    if mode != "lean":
        raise DispatchError("Optimization must be off or lean")
    return (
        "\nOptional optimization profile: first understand relevant code and its callers. "
        "Prefer existing code, built-in capabilities and the standard library over new dependencies. "
        "Implement only the requested behavior with the smallest maintainable diff. "
        "Never sacrifice validation, security, error handling, accessibility, tests, or any acceptance criterion. "
        "Do not skip tests to save tokens; explicitly report blockers.\n"
    )


def checked_dispatch(root, ticket_id, executable=None, mode="workspace-write", optimization="off"):
    root = Path(root).resolve()
    policy_prompt = optimization_rules(optimization)
    if mode not in ("read-only", "workspace-write"):
        raise DispatchError("Unsafe sandbox mode; only read-only or workspace-write accepted")
    if not re.fullmatch(r"[0-9]{2,4}", ticket_id):
        raise DispatchError("Invalid ticket ID")
    state = load_state(root)
    if state.get("finishedAt"):
        raise DispatchError("Run already finished")
    if state.get("isolateTickets") is not True or state.get("strictRouting") is not True:
        raise DispatchError("External dispatch requires both --isolated-tickets and --strict-routing")
    tickets = [t for t in state.get("tickets", []) if t.get("id") == ticket_id]
    if len(tickets) != 1 or tickets[0].get("status") != "in-progress":
        raise DispatchError("Ticket is missing, duplicated or not started")
    t = tickets[0]
    route = t.get("routing") or {}
    if route.get("provider") != "openai" or route.get("verified") is not True:
        raise DispatchError("Ticket lacks a verified OpenAI route")
    wt = t.get("worktree") or {}
    if wt.get("status") != "prepared":
        raise DispatchError("Worktree must be prepared and not landed")
    from worktrees import status as worktree_status
    actual = worktree_status(root, ticket_id)
    target = Path(actual.get("cwd", root)).resolve()
    if (actual.get("status") != "present" or actual.get("dirty")
            or actual.get("commit") != wt.get("baseCommit")
            or str(target) != str(Path(wt.get("cwd", root)).resolve())):
        raise DispatchError("Worktree is missing, changed or inconsistent with ledger")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", route.get("model", "")):
        raise DispatchError("Invalid route model")
    if route.get("effort") not in ("low", "medium", "high", "xhigh", "max"):
        raise DispatchError("Invalid route effort")
    profile_name = route.get("agentFile", "")
    if not isinstance(profile_name, str) or not re.fullmatch(
            r"\.codex/agents/autopilot-executor-[A-Za-z0-9-]+\.toml", profile_name):
        raise DispatchError("Invalid pinned Codex agent profile path")
    profile = (root / profile_name).resolve()
    if not profile.is_relative_to(root) or not profile.is_file():
        raise DispatchError("Pinned agent profile missing or redirected")
    if hashlib.sha256(profile.read_bytes()).hexdigest() != route.get("profileSha"):
        raise DispatchError("Pinned agent profile was edited")
    data = tomllib.loads(profile.read_text(encoding="utf-8"))
    if (data.get("model") != route["model"] or
            data.get("model_reasoning_effort") != route["effort"] or
            data.get("name") != route.get("agentType")):
        raise DispatchError("Pinned agent settings differ from approved route")
    # The runtime capabilities file is unauthenticated, but is still a fail-closed
    # availability advertisement, not proof of actual host execution.
    caps_path = root / ".autopilot" / "model-capabilities.json"
    caps = json.loads(caps_path.read_text(encoding="utf-8"))
    if (caps.get("provider") != "openai" or caps.get("model_selection") is not True
            or route["effort"] not in caps.get("models", {}).get(route["model"], [])):
        raise DispatchError("Approved model is not in host capability advertisement")
    budget = state.get("budgetTokens")
    used = sum(int(e["input"]) + int(e["output"]) for e in state.get("usageEvents", []))
    if budget is not None and used >= budget:
        raise DispatchError("Recorded token threshold exceeded")
    files = list((root / ".autopilot" / state["dir"] / "tickets").glob(ticket_id + "-*.md"))
    if len(files) != 1 or not files[0].is_file():
        raise DispatchError("Cannot resolve exact ticket brief")
    if hashlib.sha256(files[0].read_bytes()).hexdigest() != t.get("fingerprint"):
        raise DispatchError("Ticket brief changed since publication")
    binary = choose_binary(executable)
    cmd = [binary, "exec", "--cd", str(target), "--sandbox", mode,
           "--ephemeral", "--ignore-user-config",
           "--model", route["model"], "-c",
           'model_reasoning_effort="' + route["effort"] + '"', "--json"]
    # Windows Codex 0.152+ requires an explicit Windows sandbox backend when
    # --ignore-user-config is set. Keep the read-only/workspace-write boundary.
    # This is the OS sandbox backend selector, NOT --danger-full-access.
    if os.name == "nt":
        cmd.extend(["-c", 'windows.sandbox="elevated"'])
    prompt = (data.get("developer_instructions", "") + policy_prompt +
              "\nExecute the single task described below. Stay inside your declared file zone. "
              "Do not launch nested agents, change model settings, deploy or publish. "
              "Create exactly one Git commit of tested work, or report BLOCKED without inventing success.\n\n"
              + files[0].read_text(encoding="utf-8"))
    return {"command": cmd, "cwd": str(target), "model": route["model"],
            "effort": route["effort"], "ticket": ticket_id,
            "prompt": prompt, "binary": binary, "optimization": optimization}


def parse_usage(lines):
    thread_id, usage, completed = None, None, False
    for line in lines.splitlines():
        if len(line) > 1024 * 1024:
            continue
        try:
            obj = json.loads(line)
        except (ValueError, TypeError):
            continue
        if obj.get("type") == "thread.started":
            thread_id = obj.get("thread_id")
        elif obj.get("type") == "turn.completed":
            usage = obj.get("usage")
            completed = True
    if not isinstance(usage, dict):
        return thread_id, None, completed
    try:
        counts = {k: int(usage.get(k, 0)) for k in
                  ("input_tokens", "output_tokens", "cached_input_tokens")}
    except (TypeError, ValueError):
        return thread_id, None, completed
    if any(v < 0 for v in counts.values()):
        return thread_id, None, completed
    return thread_id, counts, completed


@contextmanager
def single_flight(root, ticket):
    """OS-atomic create: no concurrent double-billing for the same ticket."""
    path = Path(root) / ".autopilot" / ("dispatch-" + ticket + ".lock")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise DispatchError("Existing dispatch lock; inspect old process before retry")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                       "ticket": ticket}, f)
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def verify_worker_commit(root, ticket):
    """True model-turn completion never implies a usable Git commit."""
    from worktrees import source_commit, WorktreeError
    from worktrees import git
    try:
        root = Path(root).resolve()
        state = load_state(root)
        task = next(t for t in state.get("tickets", []) if t.get("id") == ticket)
        base = task["worktree"]["baseCommit"]
        revision = source_commit(root, ticket, base)
        return revision, None
    except (StopIteration, KeyError, OSError, ValueError, WorktreeError):
        return None, "No clean single worker commit exists; read-only review is required"


def run_once(config, root, *, timeout=900):
    if not 20 <= timeout <= 1800:
        raise DispatchError("Timeout must be between 20 and 1800 seconds")
    with single_flight(root, config["ticket"]):
        result = subprocess.run(config["command"] + ["-"],
                                input=config["prompt"], text=True, encoding="utf-8",
                                errors="replace", capture_output=True, timeout=timeout)
        thread_id, usage, completed = parse_usage(result.stdout)
        recorded = False
        if usage and thread_id and (usage["input_tokens"] or usage["output_tokens"]):
            ap = Path(root) / ".autopilot" / "ap.py"
            subprocess.run([sys.executable, str(ap), "usage", config["ticket"],
                            "--call-id", "codex:" + thread_id,
                            "--input", str(usage["input_tokens"]),
                            "--output", str(usage["output_tokens"]),
                            "--cache-read", str(usage["cached_input_tokens"]),
                            "--source", "codex-jsonl", "--no-serve"],
                           cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30,
                           check=True)
            recorded = True
        commit, commit_issue = verify_worker_commit(root, config["ticket"])
        ok = result.returncode == 0 and completed
        return {"status": "ready-for-review" if ok and commit else
                ("incomplete" if ok else "failed"),
                "turn_completed": ok, "worker_commit": commit,
                "tests_verified": False, "accepted": False,
                "exit_code": result.returncode, "thread_id": thread_id,
                "usage_recorded": recorded, "usage": usage,
                "diagnostic": (commit_issue if ok and not commit else
                               "Codex CLI exited nonzero; inspect sanitized local host logs"
                               if not ok else "")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-exe", type=Path)
    parser.add_argument("--sandbox", default="workspace-write",
                        choices=["read-only", "workspace-write"])
    parser.add_argument("--optimization", default="off", choices=["off", "lean"],
                        help="Optional lean-code rules, off by default (NOT the upstream Ponytail plugin)")
    parser.add_argument("--execute", action="store_true",
                        help="Perform one real Codex model call (otherwise dry-run)")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    try:
        cfg = checked_dispatch(args.root, args.ticket, args.codex_exe, args.sandbox, args.optimization)
        if not args.execute:
            out = {key: value for key, value in cfg.items() if key != "prompt"}
            out["status"] = "dry-run"
        else:
            out = run_once(cfg, args.root, timeout=args.timeout)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out["status"] in ("dry-run", "ready-for-review") else 2
    except (DispatchError, OSError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(json.dumps({"status": "blocked", "error": str(e)[:500]},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
