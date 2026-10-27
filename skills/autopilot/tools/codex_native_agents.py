#!/usr/bin/env python3
"""Read-only, fail-closed Codex custom-agent capability and event verification.

A catalog and TOML profile do NOT prove that a GUI child was spawned with
that profile. Only native, independently recorded child runtime metadata may
attest actual model/effort. Never use an agent's free-form reply as proof.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

from codex_dispatch import choose_binary


class NativeAgentError(ValueError):
    pass


MODEL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,99}")
AGENT_ID = re.compile(r"[A-Za-z][A-Za-z0-9._-]{1,99}")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}


def resolved_catalog(binary, timeout=30):
    if not 5 <= timeout <= 60:
        raise NativeAgentError("Catalog timeout must be 5–60 seconds")
    try:
        result = subprocess.run([str(binary), "debug", "models"],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise NativeAgentError("Cannot retrieve native Codex model catalog") from exc
    if result.returncode:
        raise NativeAgentError("Native Codex model catalog query failed")
    try:
        data = json.loads(result.stdout)
    except ValueError as exc:
        raise NativeAgentError("Native Codex model catalog is invalid") from exc
    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        raise NativeAgentError("Native Codex model catalog lacks models")
    return data


def check_profile(profile_path, name, model, effort):
    if not AGENT_ID.fullmatch(name) or not MODEL_ID.fullmatch(model) or (
            effort is not None and effort not in EFFORTS):
        raise NativeAgentError("Unsafe native agent identifier, model or effort")
    target = Path(profile_path)
    if not target.is_file() or target.is_symlink() or target.suffix != ".toml":
        raise NativeAgentError("Missing or unsafe native TOML agent profile")
    try:
        profile = tomllib.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise NativeAgentError("Malformed native TOML agent profile") from exc
    expected = {"name": name, "model": model}
    if effort is not None:
        expected["model_reasoning_effort"] = effort
    elif "model_reasoning_effort" in profile:
        raise NativeAgentError("Advisory effort must not be pinned in native profile")
    for key, value in expected.items():
        if profile.get(key) != value:
            raise NativeAgentError("Native profile does not pin approved " + key)
    for field in ("description", "developer_instructions"):
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            raise NativeAgentError("Missing native profile field: " + field)
    return expected


def catalog_preflight(catalog, parent_model, agent_model, effort):
    for item in (parent_model, agent_model):
        if not isinstance(item, str) or not MODEL_ID.fullmatch(item):
            raise NativeAgentError("Invalid model ID")
    if effort is not None and effort not in EFFORTS:
        raise NativeAgentError("Invalid model effort")
    all_models = catalog.get("models") if isinstance(catalog, dict) else None
    if not isinstance(all_models, list):
        raise NativeAgentError("Missing resolved catalog models")
    models = {entry.get("slug"): entry for entry in all_models
              if isinstance(entry, dict) and isinstance(entry.get("slug"), str)}
    if parent_model not in models or agent_model not in models:
        return {"status": "blocked", "reason": "model-missing-from-host-catalog",
                "parent": parent_model, "child": agent_model}
    child = models[agent_model]
    supported = {entry.get("effort") for entry in child.get("supported_reasoning_levels", [])
                 if isinstance(entry, dict)}
    if effort is not None and effort not in supported:
        return {"status": "blocked", "reason": "child-effort-not-supported",
                "parent": parent_model, "child": agent_model}
    # Newer hosted GPT-6 V2 may expose only task_name/message/fork_turns;
    # this is not the same as explicitly selecting a named custom TOML agent.
    mode = models[parent_model].get("multi_agent_version")
    if mode != "v1":
        return {"status": "blocked", "reason": "custom-agent-type-not-exposed-by-parent",
                "parent": parent_model, "child": agent_model,
                "multi_agent_version": mode or "unknown"}
    return {"status": "candidate-only", "reason": "requires-native-spawn-and-child-evidence",
            "parent": parent_model, "child": agent_model,
            "multi_agent_version": mode}


def attested_events(lines, name, model, effort):
    """Require native child metadata, not completion text or claimed counts.

    A parent spawn event alone does not prove a child applied the requested
    model+effort. Both events must share a nonblank child id. Unknown schemas
    fail closed rather than guessing which version is running.
    """
    spawn_ids = set()
    child_ids = set()
    observed = 0
    for line in lines:
        try:
            event = json.loads(line) if isinstance(line, str) else line
        except (TypeError, ValueError):
            continue
        if not isinstance(event, dict):
            continue
        observed += 1
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if (item.get("type") == "collab_tool_call"
                and item.get("tool") == "spawn_agent"
                and item.get("agent_type") == name
                and isinstance(item.get("child_id"), str) and item["child_id"]):
            spawn_ids.add(item["child_id"])
        if (item.get("type") == "child_session_metadata"
                and item.get("agent_type") == name
                and item.get("model") == model
                and (effort is None or item.get("model_reasoning_effort") == effort)
                and isinstance(item.get("child_id"), str) and item["child_id"]):
            child_ids.add(item["child_id"])
    observed_pair = bool(spawn_ids & child_ids)
    # JSONL is caller-provided and not independently signed. Even matching
    # native-shaped events are *diagnostic*, never automatic authorization.
    return {"status": "trace-consistent" if observed_pair else "unverified",
            "reason": "matching-claimed-native-events-needs-host-approval" if observed_pair
                      else "native-child-execution-not-attested",
            "events": observed, "matching_children": len(spawn_ids & child_ids)}


def inspect(binary, profile, agent, parent_model, child_model, effort, event_path=None):
    check_profile(profile, agent, child_model, effort)
    catalog = resolved_catalog(binary)
    gate = catalog_preflight(catalog, parent_model, child_model, effort)
    gate["profile_valid"] = True
    gate["native_session_verified"] = False
    if gate["status"] == "blocked":
        return gate
    if event_path is not None:
        path = Path(event_path)
        if not path.is_file() or path.is_symlink():
            raise NativeAgentError("Native event file is missing or redirected")
        with path.open(encoding="utf-8", errors="replace") as data:
            evidence = attested_events(data, agent, child_model, effort)
        gate["evidence"] = evidence
        # Evidence copied from a GUI or CLI log is useful for diagnostics but
        # can be forged on disk; do not authorize any production spawn from it.
        gate["native_session_verified"] = False
        gate["status"] = "blocked"
        gate["reason"] = "requires-independent-native-session-attestation"
    return gate


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--codex-exe", type=Path)
    p.add_argument("--profile", required=True, type=Path)
    p.add_argument("--name", required=True)
    p.add_argument("--parent-model", required=True)
    p.add_argument("--child-model", required=True)
    p.add_argument("--effort", help="Optional enforced effort. Omit for model-only/advisory mode.")
    p.add_argument("--native-events", type=Path)
    args = p.parse_args(argv)
    try:
        result = inspect(choose_binary(args.codex_exe), args.profile, args.name,
                         args.parent_model, args.child_model, args.effort,
                         args.native_events)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        # Candidate is not an executed session, so never return success.
        return 0 if result["status"] == "verified" else 2
    except (NativeAgentError, OSError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
