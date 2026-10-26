#!/usr/bin/env python3
"""One-shot *temporary fixture only* bounded OpenAI Responses API qualification.

Distinct from real Codex CLI dispatch and its fail-closed spend_guard. This
pilot uses a fixed toy task, a fixed API model, small request, server-side
max_output_tokens, zero tools, durable no-retry receipts and host-owned
test/commit acceptance. It is NOT a verified dollar hard cap or arbitrary
AI agent. No API key is written to disk or displayed.
"""
import argparse
from datetime import datetime, timezone
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
import tempfile

import controller
import worktrees

MODEL = "gpt-6-luna"
MAX_OUTPUT_TOKENS = 192
MAX_REQUEST_BYTES = 4096
MAX_RESPONSE_BYTES = 32768
MARKER = "AUTOPILOT_BOUNDED_API_PILOT_V1\n"
SOURCE = Path("src/core/calc.py")
BASELINE = "def add(a, b):\n    return a - b\n"
EXPECTED = "def add(a, b):\n    return a + b\n"
API_HOST = "api.openai.com"
API_PATH = "/v1/responses"


class PilotError(ValueError):
    pass


def stamp():
    return datetime.now(timezone.utc).isoformat()


def request_body():
    """Fixed, tiny text-only request: no agent tools, history or external files."""
    data = {
        "model": MODEL,
        "instructions": (
            "Return JSON containing exactly the corrected Python source in 'source'. "
            "Correct only the addition bug. No explanations. No extra code."),
        "input": [{
            "role": "user",
            "content": "Fix this add function so add(2,3)==5:\n" + BASELINE,
        }],
        "reasoning": {"effort": "low"},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "tools": [],
        "tool_choice": "none",
        "store": False,
        "truncation": "disabled",
        "text": {"format": {
            "type": "json_schema", "name": "fixed_add_source",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"source": {"type": "string"}},
                "required": ["source"], "additionalProperties": False
            }
        }},
    }
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    if len(payload) > MAX_REQUEST_BYTES:
        raise PilotError("Pilot input request exceeded fixed byte allowance")
    return payload


def receipt_path(root, ticket):
    if not re.fullmatch(r"[0-9]{2,4}", ticket):
        raise PilotError("Invalid ticket ID")
    folder = root / ".autopilot" / "api-pilot"
    if folder.is_symlink() or getattr(folder, "is_junction", lambda: False)():
        raise PilotError("Redirected API pilot receipt directory")
    path = folder / (ticket + ".json")
    if path.is_symlink():
        raise PilotError("Redirected API pilot receipt")
    return path


def save_receipt(path, rec):
    with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix="receipt-", suffix=".tmp",
            mode="w", encoding="utf-8", delete=False) as f:
        temp = Path(f.name)
        os.chmod(temp, 0o600)
        json.dump(rec, f, sort_keys=True, ensure_ascii=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def claim(root, ticket):
    path = receipt_path(root, ticket)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise PilotError("Prior API pilot receipt exists; NEVER replay") from exc
    rec = {"ticket": ticket, "status": "invocation-uncertain",
           "model_requested": MODEL, "model_invoked": "unknown",
           "created_at": stamp(), "provider_limit_output_tokens": MAX_OUTPUT_TOKENS,
           "max_request_bytes": MAX_REQUEST_BYTES,
           "accepted": False, "tests_verified": False,
           "note": "One exact temporary fixture call; no retry after any outcome"}
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(rec, f, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return path, rec


def preflight(root, ticket):
    root = Path(root).resolve()
    temp = Path(tempfile.gettempdir()).resolve()
    if root == temp or not root.is_relative_to(temp):
        raise PilotError("Only disposable Git projects inside OS temp directory")
    metadata = root / ".autopilot"
    if (metadata.is_symlink() or
            getattr(metadata, "is_junction", lambda: False)()):
        raise PilotError("Redirected Autopilot metadata directory")
    marker = metadata / "api-pilot-consent"
    if marker.is_symlink() or not marker.is_file() or (
            marker.read_text(encoding="utf-8") != MARKER):
        raise PilotError("Missing exact temporary API pilot consent marker")
    if receipt_path(root, ticket).exists():
        raise PilotError("Prior API pilot attempt; no replay")
    worktrees.repository(root)
    state = controller.read_state(root)
    if state.get("strictRouting") is not True or state.get("isolateTickets") is not True:
        raise PilotError("Strict isolated worktrees required")
    active = [t for t in state["tickets"] if t.get("status") == "in-progress"]
    if len(active) != 1 or active[0].get("id") != ticket:
        raise PilotError("Exactly one matching started ticket required")
    t = active[0]
    routing = t.get("routing") or {}
    if (routing.get("provider") != "openai" or routing.get("verified") is not True
            or routing.get("model") != MODEL or routing.get("effort") != "low"
            or t.get("zone") != ["src/core/"]):
        raise PilotError("Exact verified model/effort/zone route required")
    summary = worktrees.status(root, ticket)
    wt = t.get("worktree") or {}
    target = worktrees.safe_target(root, ticket)
    if (summary.get("status") != "present" or summary.get("dirty")
            or summary.get("commit") != wt.get("baseCommit")
            or Path(wt.get("cwd", root)).resolve() != target.resolve()
            or wt.get("status") != "prepared"):
        raise PilotError("Ticket worktree is not at clean planned base")
    file = target / SOURCE
    for part in ("src", "core", "calc.py"):
        current = target / "src" if part == "src" else (
            target / "src" / "core" if part == "core" else file)
        if (current.is_symlink() or
                getattr(current, "is_junction", lambda: False)()):
            raise PilotError("Redirected fixture source path")
    if not file.is_file():
        raise PilotError("Expected ordinary fixture source file")
    if file.read_text(encoding="utf-8") != BASELINE:
        raise PilotError("Expected exact unchanged synthetic baseline")
    suite = target / "test_core.py"
    if suite.is_symlink() or not suite.is_file():
        raise PilotError("Expected baseline trusted test suite")
    if subprocess.run(["git", "-C", str(target), "diff", "--quiet",
                       "HEAD", "--", "test_core.py"],
                      capture_output=True, timeout=15).returncode:
        raise PilotError("Trusted baseline test suite was modified")
    events = state.get("usageEvents")
    budget = state.get("budgetTokens")
    if type(budget) is not int or budget < MAX_REQUEST_BYTES + MAX_OUTPUT_TOKENS:
        raise PilotError("Missing conservative *soft* run budget allowance")
    if not isinstance(events, list):
        raise PilotError("Missing usage ledger")
    used = 0
    for e in events:
        if not isinstance(e, dict) or type(e.get("input")) is not int or type(e.get("output")) is not int:
            raise PilotError("Invalid usage ledger")
        used += e["input"] + e["output"]
    if used < 0 or budget - used < MAX_REQUEST_BYTES + MAX_OUTPUT_TOKENS:
        raise PilotError("Recorded soft run budget insufficient")
    return {"root": str(root), "ticket": ticket, "target": str(target),
            "model": MODEL, "request_bytes": len(request_body()),
            "max_request_bytes": MAX_REQUEST_BYTES,
            "server_max_output_tokens": MAX_OUTPUT_TOKENS,
            "provider_dollar_hard_cap": False,
            "model_invoked": False, "accepted": False}


def send_once(body, key):
    """Exactly one TLS POST to fixed host, no redirects, tools or auto retries."""
    conn = http.client.HTTPSConnection(API_HOST, timeout=25,
                                       context=ssl.create_default_context())
    try:
        conn.request("POST", API_PATH, body=body, headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json"})
        reply = conn.getresponse()
        raw = reply.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise PilotError("Provider response exceeded bounded size")
        if reply.status != 200:
            raise PilotError("Provider did not return HTTP 200; no retry")
        return json.loads(raw)
    finally:
        conn.close()


def extract(response):
    if (not isinstance(response, dict) or response.get("status") != "completed"
            or response.get("model") not in (MODEL,)
            or not isinstance(response.get("id"), str)
            or not re.fullmatch(r"resp_[A-Za-z0-9_-]{5,120}", response["id"])):
        raise PilotError("Response incomplete or unverified model/identity")
    usage = response.get("usage") or {}
    inp, out = usage.get("input_tokens"), usage.get("output_tokens")
    cache = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
    if (type(inp) is not int or type(out) is not int or type(cache) is not int
            or not 0 < inp <= MAX_REQUEST_BYTES or
            not 0 < out <= MAX_OUTPUT_TOKENS or not 0 <= cache <= inp):
        raise PilotError("Provider token usage unavailable or outside bounds")
    output = response.get("output")
    if not isinstance(output, list) or len(output) != 1:
        raise PilotError("Unexpected provider output item shape")
    msg = output[0]
    if (not isinstance(msg, dict) or msg.get("type") != "message"
            or msg.get("role") != "assistant"
            or msg.get("status") not in (None, "completed")):
        raise PilotError("Unexpected assistant output status")
    content = msg.get("content")
    if not isinstance(content, list) or len(content) != 1 or (
            not isinstance(content[0], dict) or content[0].get("type") != "output_text"):
        raise PilotError("Unexpected model content")
    try:
        result = json.loads(content[0].get("text"))
    except (TypeError, ValueError) as exc:
        raise PilotError("Invalid model JSON output") from exc
    if result != {"source": EXPECTED}:
        raise PilotError("Output is not the exact approved synthetic change")
    return {"response_id": response["id"], "model_reported": response["model"],
            "input_tokens": inp, "output_tokens": out, "cached_tokens": cache}


def ledger(root, ticket, report):
    proc = subprocess.run([
        sys.executable, str(root / ".autopilot" / "ap.py"),
        "usage", ticket, "--call-id", "api:" + report["response_id"],
        "--input", str(report["input_tokens"]),
        "--output", str(report["output_tokens"]),
        "--cache-read", str(report["cached_tokens"]),
        "--source", "responses-api", "--no-serve"],
        cwd=root, capture_output=True, text=True, timeout=20,
        encoding="utf-8", errors="replace")
    if proc.returncode:
        raise PilotError("Host token ledger rejected provider report")


def run(root, ticket, *, execute=False, approval=None):
    root = Path(root).resolve()
    if not execute:
        if approval is not None:
            raise PilotError("Approval only allowed on --execute")
        preview = preflight(root, ticket)
        return {"status": "dry-run", "preview": preview,
                "api_key_available": bool(os.environ.get("OPENAI_API_KEY")),
                "provider_dollar_hard_cap": False, "model_invoked": False}
    if approval != ticket:
        raise PilotError("Explicit --approve-pilot-ticket must match ticket")
    key = os.environ.get("OPENAI_API_KEY")
    if (not isinstance(key, str) or not key.startswith("sk-")
            or not 20 <= len(key) <= 250 or not key.isascii()):
        raise PilotError("Missing valid OPENAI_API_KEY; nothing sent or claimed")
    with controller.controller_lock(root):
        summary = preflight(root, ticket)
        body = request_body()
        path, record = claim(root, ticket)
        try:
            response = send_once(body, key)
            report = extract(response)
            record.update(report)
            record["model_invoked"] = True
            # Accounted before writing anything: if ledger fails, leave no edit.
            ledger(root, ticket, report)
            record["usage_recorded"] = True
            save_receipt(path, record)
            # Live recheck: no other host write should occur during the call.
            target = Path(summary["target"])
            if (worktrees.status(root, ticket).get("dirty") or
                    (target / SOURCE).read_text(encoding="utf-8") != BASELINE):
                raise PilotError("Source changed while response was pending")
            (target / SOURCE).write_text(EXPECTED, encoding="utf-8")
            record.update({"status": "ready-for-host-verification",
                           "changed_files": 1, "accepted": False,
                           "tests_verified": False,
                           "note": "Trusted host tests and scoped finalize REQUIRED"})
            save_receipt(path, record)
        except BaseException as exc:
            record["status"] = "invocation-uncertain"
            record["diagnostic"] = type(exc).__name__ + ": manual review; never replay"
            save_receipt(path, record)
            if isinstance(exc, PilotError):
                return {"status": "blocked", "reason": str(exc),
                        "receipt": str(path), "model_invoked": "unknown",
                        "accepted": False}
            raise
        return {"status": record["status"], "ticket": ticket,
                "receipt": str(path), "model_invoked": True,
                "usage_recorded": True, "accepted": False,
                "tests_verified": False, "input_tokens": report["input_tokens"],
                "output_tokens": report["output_tokens"],
                "provider_dollar_hard_cap": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--ticket", required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--approve-pilot-ticket")
    args = p.parse_args(argv)
    try:
        result = run(args.root, args.ticket,
                     execute=args.execute, approval=args.approve_pilot_ticket)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] in ("dry-run", "ready-for-host-verification") else 2
    except (PilotError, controller.ControllerError, worktrees.WorktreeError,
            ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:220],
                          "model_invoked": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
