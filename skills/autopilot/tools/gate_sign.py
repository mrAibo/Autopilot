#!/usr/bin/env python3
"""HMAC signing of strict-run gate records (routing, attestations, test evidence).

The key lives in the user's home (~/.autopilot/gate.key, or $AUTOPILOT_HOME),
outside the project, so editing project files cannot forge a signature. It does
not protect against a process that can read the home directory.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets

MISSING_KEY_MESSAGE = ("нет ключа подписи, запусти init заново "
                       "или восстанови ~/.autopilot/gate.key")


def key_path():
    home = os.environ.get("AUTOPILOT_HOME", "").strip()
    return (Path(home) if home else Path.home() / ".autopilot") / "gate.key"


def ensure_key():
    """Create the key (0600) if absent. Only `init --strict-routing` calls this."""
    path = key_path()
    if not path.exists() or path.stat().st_size == 0:  # an empty key would sign nothing
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
        try:
            fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return path
        with os.fdopen(fd, "wb") as stream:
            stream.write(secrets.token_bytes(32))
    return path


def load_key():
    try:
        key = key_path().read_bytes()
    except OSError:
        return None
    return key or None


def sign(payload):
    """Hex HMAC-SHA256 over canonical JSON; a `sig` field is never part of the payload."""
    key = load_key()
    if key is None:
        raise ValueError(MISSING_KEY_MESSAGE)
    body = {k: v for k, v in payload.items() if k != "sig"}
    data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def verify(payload, sig):
    if not isinstance(sig, str) or load_key() is None:
        return False
    return hmac.compare_digest(sign(payload), sig)


def routing_payload(ticket_id, routing):
    """What a ticket's route signature covers (profileSha included)."""
    return {"ticket": ticket_id, "routing": {k: v for k, v in routing.items() if k != "sig"}}


def evidence_payload(ticket_id, evidence):
    return {"ticket": ticket_id, "evidence": {k: v for k, v in evidence.items() if k != "sig"}}


def _run_id(state):
    # No `dir`: finish renames it (drops --wip) and that must not break the mark.
    return "%s|%s" % (state.get("slug"), state.get("startedAt"))


def run_mark(state):
    """Signed marker that this run was started signed (stored as state["gateMark"])."""
    return sign({"run": _run_id(state)})


def record_path(root):
    """Out-of-project record that a run was started signed: <home>/runs/<hash of the real root>.

    A moved or renamed project hashes differently: its record is not found and the
    run reads as unsigned (never forged); the owner re-inits to sign again.
    """
    real = os.path.normcase(os.path.realpath(root))
    return key_path().parent / "runs" / hashlib.sha256(real.encode("utf-8")).hexdigest()


def write_run_record(root, state):
    """Record (or update) `slug|startedAt` and finished-ness for a signed run. Needs the key."""
    path = record_path(root)
    body = {"run": _run_id(state), "finished": bool(state.get("finishedAt"))}
    body["sig"] = sign(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body), encoding="utf-8")  # shortcut: not atomic, a torn file reads as forged


def remove_run_record(root):
    record_path(root).unlink(missing_ok=True)


def run_status(state, root=None):
    """signed | unsigned | forged.

    With `root` the record outside the project decides: no record is unsigned; a record
    the state disagrees with (strict off, mark missing/wrong, other run, finished without
    a finish record) is forged. Without `root` (or without a key) only the in-state
    mark counts.
    """
    mark = state.get("gateMark")
    mark_ok = mark is not None and verify({"run": _run_id(state)}, mark)
    if root is None or load_key() is None:
        return "unsigned" if mark is None else ("signed" if mark_ok else "forged")
    try:
        record = json.loads(record_path(root).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "unsigned"
    except (OSError, ValueError):
        return "forged"
    if not isinstance(record, dict) or not verify(record, record.get("sig")):
        return "forged"
    agrees = (state.get("strictRouting") is True and mark_ok
              and record.get("run") == _run_id(state)
              and record.get("finished") is bool(state.get("finishedAt")))
    return "signed" if agrees else "forged"
