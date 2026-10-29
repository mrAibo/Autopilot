#!/usr/bin/env python3
"""Claude Code attestation hook: record runtime model/effort evidence.

Appends metadata-only JSON lines to .autopilot/attestations.jsonl from
PreToolUse (inside a subagent), PostToolUse(Agent) and SubagentStop payloads.
Recording only: this hook never blocks (always exit 0). Gating is a separate step.
Prompts, messages and tool inputs are never written.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

from claude_agent_guard import project_root

# Same agent-name contract as claude_agent_guard.decision.
AGENT = re.compile(r"autopilot-(executor|reviewer|explorer|acceptance)-[a-z0-9-]{1,58}")
HOOKS = (("PreToolUse", "*"), ("PostToolUse", "Agent"), ("SubagentStop", "autopilot-.*"))


def _str(value):
    return value if isinstance(value, str) and value else None


def record(payload, root):
    """Append one evidence line; return it, or None if nothing applies."""
    if not isinstance(payload, dict):
        return None
    event = payload.get("hook_event_name")
    response = payload.get("tool_response")
    response = response if isinstance(response, dict) else {}
    line = {"event": event, "agent_type": None, "agent_id": _str(payload.get("agent_id")),
            "effort": None, "resolved_model": None, "models_used": None, "status": None}
    if event == "PreToolUse":
        effort = payload.get("effort")
        line["agent_type"] = _str(payload.get("agent_type"))
        line["effort"] = _str(effort.get("level")) if isinstance(effort, dict) else None
        if not line["agent_id"] or not line["effort"]:
            return None  # fired in the main session, not inside a subagent
    elif event == "PostToolUse" and payload.get("tool_name") == "Agent":
        args = payload.get("tool_input")
        line["agent_type"] = _str(args.get("subagent_type")) if isinstance(args, dict) else None
        line["agent_id"] = _str(response.get("agentId"))
        line["status"] = _str(response.get("status"))
        line["resolved_model"] = _str(response.get("resolvedModel"))
        used = response.get("modelsUsed")
        if isinstance(used, list):
            line["models_used"] = [m for m in used if isinstance(m, str)]
    elif event == "SubagentStop":
        line["agent_type"] = _str(payload.get("agent_type"))
    else:
        return None
    if not line["agent_type"] or not AGENT.fullmatch(line["agent_type"]):
        return None
    state = Path(root) / ".autopilot" / "state.js"
    log = state.with_name("attestations.jsonl")
    if state.is_symlink() or log.is_symlink() or not state.exists():
        return None
    line = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **line}
    with log.open("a", encoding="utf-8") as writer:
        writer.write(json.dumps(line, ensure_ascii=False) + "\n")
    return line


def install_hook(root):
    """Opt-in install: merge three project hooks, preserving unrelated settings.

    No onFailure: recording must never block work.
    """
    root = Path(root).resolve()
    settings = root / ".claude" / "settings.json"
    if not root.is_dir():
        raise ValueError("Project root missing")
    settings.parent.mkdir(parents=True, exist_ok=True)
    if not str(settings.resolve()).startswith(str(root) + os.sep):
        raise ValueError("Settings path escapes project")
    try:
        content = json.loads(settings.read_text(encoding="utf-8"))
    except FileNotFoundError:
        content = {}
    if not isinstance(content, dict):
        raise ValueError("settings.json must be an object")
    hooks = content.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks must be an object")
    args = ["${CLAUDE_PROJECT_DIR}/.autopilot/claude_attest.py"]
    command = str(Path(sys.executable).resolve())  # exec form: no shell, no PATH lookup
    changed = False
    for event, matcher in HOOKS:
        current = hooks.setdefault(event, [])
        if not isinstance(current, list):
            raise ValueError("hooks." + event + " must be a list")
        hook = {"matcher": matcher, "hooks": [
            {"type": "command", "command": command, "args": args}]}
        if hook in current:
            continue
        # Drop our own stale entry (e.g. another interpreter) before re-adding.
        current[:] = [e for e in current if not (
            isinstance(e, dict) and isinstance(e.get("hooks"), list) and any(
                isinstance(h, dict) and h.get("args") == args for h in e["hooks"]))]
        current.append(hook)
        changed = True
    if changed:
        temp = settings.with_suffix(".json.tmp")
        try:
            with temp.open("x", encoding="utf-8") as writer:
                json.dump(content, writer, ensure_ascii=False, indent=2)
                writer.write("\n")
            os.replace(temp, settings)
        finally:
            if temp.exists():
                temp.unlink()
    return settings, changed


def main():
    if "--install-hook" in sys.argv:
        try:
            project = Path(sys.argv[sys.argv.index("--root") + 1])
        except (IndexError, ValueError):
            project = Path.cwd()
        try:
            path, changed = install_hook(project)
        except (OSError, ValueError) as e:
            print("Autopilot attestation installation blocked: " + str(e), file=sys.stderr)
            return 2
        print(json.dumps({"hook": str(path), "installed": changed}, ensure_ascii=False))
        return 0
    try:
        payload = json.load(sys.stdin)
        record(payload, project_root(payload))
    except Exception as e:  # recording must never block work
        print("Autopilot attestation: " + str(e), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
