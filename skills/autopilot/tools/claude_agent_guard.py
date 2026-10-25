#!/usr/bin/env python3
"""Optional Claude Code PreToolUse guard for Autopilot strict subagent routes.

Install with a project-local hook matching Agent|Task. Claude's SubagentStart
hook cannot block a launch; this runs BEFORE tool execution instead.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from model_router import DEFAULT_POLICY


def read_state(root):
    path = Path(root) / ".autopilot" / "state.js"
    try:
        value = path.read_text(encoding="utf-8")
        if value.startswith("window.STATE"):
            value = value.split("=", 1)[1].strip().rstrip(";")
        state = json.loads(value)
        return state if isinstance(state, dict) else None
    except (OSError, ValueError, IndexError):
        return None


def parse_frontmatter(path):
    try:
        value = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not value.startswith("---\n"):
        return {}
    header = value.split("\n---", 1)[0]
    fields = {}
    for line in header.splitlines()[1:]:
        if ": " in line:
            key, val = line.split(": ", 1)
            fields[key] = val
    return fields


def decision(payload, root):
    if not isinstance(payload, dict):
        return False, "Malformed Claude hook payload"
    state = read_state(root)
    # Opt-in safeguard, active only during strict Autopilot flights.
    if not state or not state.get("strictRouting") or state.get("finishedAt"):
        return True, "No active strict run"
    if payload.get("tool_name") not in ("Agent", "Task"):
        return True, "Not an agent invocation"
    args = payload.get("tool_input")
    if not isinstance(args, dict):
        return False, "Missing subagent tool input"
    name = args.get("subagent_type")
    if not isinstance(name, str) or not re.fullmatch(
            r"autopilot-(executor|reviewer|explorer|acceptance)-[a-z0-9-]{1,58}", name):
        return False, "Only explicitly configured Autopilot agents are allowed"
    root = Path(root).resolve()
    agent = root / ".claude" / "agents" / (name + ".md")
    if not agent.is_file() or not str(agent.resolve()).startswith(str(root) + os.sep):
        return False, "Autopilot agent profile missing or outside project"
    fields = parse_frontmatter(agent)
    if fields.get("name") != name:
        return False, "Agent profile name mismatch"
    model, effort = fields.get("model"), fields.get("effort")
    if not model or not effort or model == "inherit":
        return False, "Agent model and effort must be pinned"
    premium = ("fable", "claude-fable", "opus", "claude-opus")
    if model.lower().startswith(premium):
        return False, "Premium subagents are blocked by strict policy"
    for key, field in (("model", model), ("effort", effort)):
        if args.get(key) is not None and args[key] != field:
            return False, "Explicit %s overrides pinned profile" % key
    caps_file = root / ".autopilot" / "model-capabilities.json"
    try:
        caps = json.loads(caps_file.read_text(encoding="utf-8"))
        if (caps.get("provider") != "anthropic"
                or caps.get("model_selection") is not True
                or effort not in caps.get("models", {}).get(model, [])):
            return False, "Host has not advertised this model/effort"
    except (OSError, ValueError, AttributeError, TypeError):
        return False, "Host capability advertisement missing/invalid"
    if name.startswith("autopilot-executor-"):
        known = [t.get("routing") or {} for t in state.get("tickets") or []]
        matching = [r for r in known if r.get("agentType") == name and
                    r.get("verified") and r.get("provider") == "anthropic" and
                    r.get("model") == model and r.get("effort") == effort]
        if len(matching) != 1:
            return False, "Executor does not match an approved Autopilot task"
        with agent.open("rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest != matching[0].get("profileSha"):
            return False, "Agent profile changed since route approval"
    return True, "Approved pinned profile"


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, TypeError):
        print("Autopilot guard: invalid hook JSON", file=sys.stderr)
        return 2
    ok, why = decision(payload, os.getcwd())
    if not ok:
        print("Autopilot guard: " + why, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
