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
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
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


def run_mark(state):
    """Signed marker that this run was started signed (stored as state["gateMark"])."""
    return sign({"run": state.get("dir"), "startedAt": state.get("startedAt")})


def run_status(state):
    """signed | unsigned (pre-signing run, no key on this machine) | forged | downgraded.

    A key on this machine plus a strict run without a valid marker is a downgrade
    (someone removed it from state.js), never a pre-signing run.
    """
    mark = state.get("gateMark")
    if mark is None:
        return "downgraded" if state.get("strictRouting") and load_key() else "unsigned"
    ok = verify({"run": state.get("dir"), "startedAt": state.get("startedAt")}, mark)
    return "signed" if ok else "forged"
