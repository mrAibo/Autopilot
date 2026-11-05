#!/usr/bin/env python3
"""Optional Claude Code PreToolUse guard for Autopilot strict subagent routes.

Install with a project-local hook matching Agent|Task. Claude's SubagentStart
hook cannot block a launch; this runs BEFORE tool execution instead.
"""
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys

import gate_sign
import state_io
from model_router import is_allowed_subagent_model


def read_state(root):
    path = Path(root) / ".autopilot" / "state.js"
    try:
        return state_io.read_state_file(path)
    except state_io.StateError:
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


WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def is_protected(target, root):
    """Run files an executor must not rewrite: state, attestations, capabilities, Claude config."""
    real_root = os.path.normcase(os.path.realpath(root))
    path = os.path.normcase(os.path.realpath(os.path.join(root, target)))
    if os.path.commonpath((path, real_root)) != real_root:
        return False
    # casefold: .Autopilot and .AUTOPILOT are the same folder on macOS and Windows
    parts = path[len(real_root):].strip("\\/").replace("\\", "/").casefold().split("/")
    if parts[0] == ".autopilot":
        # top-level .py files are the verifiers themselves (ap, guard, gate_sign, ...)
        return len(parts) == 2 and (parts[1] in (
            "state.js", "attestations.jsonl", "model-capabilities.json")
            or parts[1].endswith(".py"))
    if parts[0] == ".claude" and len(parts) > 1:
        return (parts[1] == "agents" and len(parts) > 2) or (
            len(parts) == 2 and fnmatch.fnmatch(parts[1], "settings*.json"))
    return False


def forged_run(state, root):
    """Reason to deny when state.js disagrees with the signed record outside the project, else None.

    Checked before any "no active strict run" shortcut: a forged `strictRouting: false`
    or `finishedAt` is exactly how a downgrade would look.
    """
    if gate_sign.run_status(state, root) != "forged":
        return None
    if gate_sign.load_key() is None:
        return gate_sign.MISSING_KEY_MESSAGE
    return "Run signature marker missing or invalid"


def write_decision(payload, root):
    args = payload.get("tool_input")
    target = args.get("file_path") or args.get("notebook_path") if isinstance(args, dict) else None
    if not isinstance(target, str) or not target:
        return True, "No file target"
    try:
        protected = is_protected(target, root)
    except ValueError:  # other drive on Windows: certainly outside the project
        return True, "Outside project"
    if not protected:
        return True, "Not a protected file"
    if not (Path(root) / ".autopilot" / "state.js").exists():
        return True, "No Autopilot run"
    state = read_state(root)
    if state is None:
        return False, "Existing Autopilot state is unreadable or malformed"
    forged = forged_run(state, root)
    if forged:
        return False, forged
    if state.get("strictRouting") and not state.get("finishedAt"):
        return False, "Autopilot run files are protected in strict runs"
    return True, "No active strict run"


GIT_OPTS_WITH_VALUE = ("-C", "-c", "--git-dir", "--work-tree", "--namespace")


def split_unquoted(command):
    """Split on ; & | and newlines that sit outside '...' and "..." (a backslash escapes)."""
    parts, buf, quote, i = [], [], None, 0
    while i < len(command):
        c = command[i]
        if c == "\\" and quote != "'" and i + 1 < len(command):
            buf.append(command[i:i + 2])
            i += 2
            continue
        if quote:
            quote = None if c == quote else quote
        elif c == "#" and (not buf or buf[-1][-1] in " \t"):
            i = command.find("\n", i)  # comment: no quote opens inside it
            i = len(command) if i < 0 else i
            continue
        elif c in "'\"":
            quote = c
        elif c in ";&|\n":
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    return parts + ["".join(buf)]


def bash_decision(command):
    """Pure check of one Bash command: deny git stash / reset / checkout -- <paths>.

    Splits on ; && || | & and newlines outside quotes. shortcut: a command hidden in a script,
    `eval` or `$(...)` is not seen; documented in docs/autopilot/claude-code.md.
    """
    for part in split_unquoted(command if isinstance(command, str) else ""):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        if "git" not in words:
            continue
        rest = words[words.index("git") + 1:]
        while rest and rest[0].startswith("-"):
            rest = rest[2:] if rest[0] in GIT_OPTS_WITH_VALUE else rest[1:]
        sub = rest[0] if rest else ""
        if sub in ("stash", "reset") or (sub == "checkout" and "--" in rest):
            return False, "git %s is forbidden for Autopilot subagents (shared worktree index)" % sub
    return True, "Command allowed"


def bash_gate(payload, root):
    if not (payload.get("agent_id") or payload.get("agent_type")):
        return True, "Main session"
    if not (Path(root) / ".autopilot" / "state.js").exists():
        return True, "No Autopilot run"
    state = read_state(root)
    if state is None:
        return True, "No readable Autopilot state"
    forged = forged_run(state, root)
    if forged:
        return False, forged
    if not state.get("strictRouting") or state.get("finishedAt"):
        return True, "No active strict run"
    args = payload.get("tool_input")
    return bash_decision(args.get("command") if isinstance(args, dict) else "")


def decision(payload, root):
    if not isinstance(payload, dict):
        return False, "Malformed Claude hook payload"
    if payload.get("tool_name") in WRITE_TOOLS:
        return write_decision(payload, root)
    if payload.get("tool_name") == "Bash":
        return bash_gate(payload, root)
    if payload.get("tool_name") not in ("Agent", "Task"):
        return True, "Not an agent invocation"
    state_file = Path(root) / ".autopilot" / "state.js"
    if state_file.is_symlink():
        return False, "Autopilot state may not be redirected"
    # No run is a legitimate non-Autopilot Claude project. An existing but
    # unreadable/malformed run is NOT proof that strict routing is disabled.
    if not state_file.exists():
        return True, "No Autopilot run"
    state = read_state(root)
    if state is None:
        return False, "Existing Autopilot state is unreadable or malformed"
    if not isinstance(state.get("tickets"), list):
        return False, "Existing Autopilot state has no valid ticket ledger"
    strict = state.get("strictRouting")
    if strict is not None and not isinstance(strict, bool):
        return False, "Autopilot strictRouting flag is malformed"
    forged = forged_run(state, root)
    if forged:
        return False, forged
    # Opt-in safeguard, active only during strict Autopilot flights.
    if not strict or state.get("finishedAt"):
        return True, "No active strict run"
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
    # Autopilot owns ticket worktrees (T12 option B); Claude's isolation would bypass them.
    if fields.get("isolation") or args.get("isolation"):
        return False, "Claude worktree isolation is not allowed in strict runs"
    model, effort = fields.get("model"), fields.get("effort")
    if not model or model == "inherit":
        return False, "Agent model must be pinned"
    if not is_allowed_subagent_model(model):
        return False, "Premium or non-allowlisted subagent models are blocked by strict policy"
    # Claude Code resolves these variables after reading the profile.
    # In particular a forced model can silently ignore a pinned profile,
    # while the effort variable takes precedence over both frontmatter and
    # the per-invocation value. Refuse ambiguous strict routing.
    forced = os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE", "").strip().lower()
    if forced not in ("", "0", "false", "off"):
        return False, "Global Claude subagent model FORCE overrides pinned routes"
    if args.get("model") is not None and args["model"] != model:
        return False, "Explicit model overrides pinned profile"
    caps_file = root / ".autopilot" / "model-capabilities.json"
    try:
        caps = json.loads(caps_file.read_text(encoding="utf-8"))
        advertised = caps.get("models")
        if (caps.get("provider") != "anthropic"
                or caps.get("model_selection") is not True
                or type(caps.get("effort_selection", True)) is not bool
                or not isinstance(advertised, dict)
                or not isinstance(advertised.get(model), list)):
            return False, "Host has not advertised this model"
        effort_enforced = caps.get("effort_selection", True)
        if effort_enforced:
            if (not effort or effort not in advertised[model]):
                return False, "Host has not advertised this model/effort"
            env_effort = os.environ.get("CLAUDE_CODE_EFFORT_LEVEL", "").strip()
            if env_effort and env_effort != effort:
                return False, "Claude effort environment override conflicts with pinned route"
            if args.get("effort") is not None and args["effort"] != effort:
                return False, "Explicit effort overrides pinned profile"
        elif effort is not None:
            return False, "Advisory effort must not be pinned in profile"
    except (OSError, ValueError, AttributeError, TypeError):
        return False, "Host capability advertisement missing/invalid"
    if name.startswith("autopilot-executor-"):
        tickets = state.get("tickets") or []
        repair = state.get("repairAgent")
        if isinstance(repair, dict) and repair.get("agentType") == name:
            # The run's repair executor serves fix tickets one at a time: only the
            # one fix ticket being built or repaired right now may call it.
            tickets = [t for t in tickets if isinstance(t, dict)
                       and t.get("status") in ("in-progress", "repair")]
        known = [(t.get("id"), t.get("routing") or {}) for t in tickets]
        matching = [r for _, r in known if r.get("agentType") == name and
                    r.get("verified") and r.get("provider") == "anthropic" and
                    r.get("model") == model and
                    r.get("effortEnforced", True) is effort_enforced and
                    (not effort_enforced or r.get("effort") == effort)]
        if len(matching) != 1:
            return False, "Executor does not match an approved Autopilot task"
        status = gate_sign.run_status(state, root)
        if status != "unsigned":
            if gate_sign.load_key() is None:
                return False, gate_sign.MISSING_KEY_MESSAGE
            if status != "signed":
                return False, "Run signature marker missing or invalid"
            tid = next(i for i, r in known if r is matching[0])
            if not gate_sign.verify(gate_sign.routing_payload(tid, matching[0]),
                                    matching[0].get("sig")):
                return False, "Route signature missing or invalid"
        with agent.open("rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest != matching[0].get("profileSha"):
            return False, "Agent profile changed since route approval"
    return True, ("Approved pinned model and effort" if effort_enforced
                  else "Approved pinned model; effort unverified/advisory")


def project_root(payload):
    """Prefer Claude's project dir; never trust an arbitrary cwd silently."""
    env = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env:
        return env
    cwd = payload.get("cwd") if isinstance(payload, dict) else None
    return cwd if isinstance(cwd, str) and cwd else os.getcwd()


def install_hook(root):
    """Opt-in install: merge a project hook, preserving unrelated Claude settings."""
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
    current = hooks.setdefault("PreToolUse", [])
    if not isinstance(current, list):
        raise ValueError("hooks.PreToolUse must be a list")
    interpreter = str(Path(sys.executable).resolve())
    hook = {"matcher": "Agent|Task", "hooks": [{
        "type": "command",
        "command": interpreter,                      # exec form: no shell, no PATH lookup
        "args": ["${CLAUDE_PROJECT_DIR}/.autopilot/claude_agent_guard.py"],
        "onFailure": "block",                        # hook crash/timeout = deny (v2.1.295+)
    }]}
    permissions = content.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise ValueError("permissions must be an object")
    deny = permissions.setdefault("deny", [])
    if not isinstance(deny, list):
        raise ValueError("permissions.deny must be a list")
    # Settings-level layer for Claude-started forks, independent of this hook.
    fork_denied = "Agent(fork)" in deny
    write_hook = dict(hook, matcher="|".join(WRITE_TOOLS))
    bash_hook = dict(hook, matcher="Bash")
    if hook in current and write_hook in current and bash_hook in current and fork_denied:
        return settings, False
    if not fork_denied:
        deny.append("Agent(fork)")

    def outdated(entry):
        # Legacy relative/bare-python hook, or ours with another interpreter.
        inner = entry.get("hooks") if isinstance(entry, dict) else None
        return isinstance(inner, list) and any(
            isinstance(h, dict) and (
                h.get("command") == "python .autopilot/claude_agent_guard.py"
                or h.get("args") == hook["hooks"][0]["args"])
            for h in inner)
    current[:] = [e for e in current if not outdated(e)]
    current.extend((hook, write_hook, bash_hook))
    temp = settings.with_suffix(".json.tmp")
    try:
        with temp.open("x", encoding="utf-8") as writer:
            json.dump(content, writer, ensure_ascii=False, indent=2)
            writer.write("\n")
        os.replace(temp, settings)
    finally:
        if temp.exists():
            temp.unlink()
    return settings, True


def main():
    if "--install-hook" in sys.argv:
        try:
            ix = sys.argv.index("--root")
            project = Path(sys.argv[ix + 1])
        except (IndexError, ValueError):
            project = Path.cwd()
        try:
            path, changed = install_hook(project)
        except (OSError, ValueError) as e:
            print("Autopilot guard installation blocked: " + str(e), file=sys.stderr)
            return 2
        print(json.dumps({"hook": str(path), "installed": changed}, ensure_ascii=False))
        return 0
    try:
        payload = json.load(sys.stdin)
    except (ValueError, TypeError):
        print("Autopilot guard: invalid hook JSON", file=sys.stderr)
        return 2
    ok, why = decision(payload, project_root(payload))
    if not ok:
        print("Autopilot guard: " + why, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
