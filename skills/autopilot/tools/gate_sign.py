#!/usr/bin/env python3
"""HMAC signing of strict-run gate records (routing, attestations, test evidence).

The key lives in the user's home (~/.autopilot/gate.key, or $AUTOPILOT_HOME),
outside the project, so editing project files cannot forge a signature. On Windows
the key is wrapped with DPAPI (`dpapi:` + base64), so the file alone is useless to
another user; elsewhere it is a 0600 file. Neither protects against a process that
runs as the same user and can read the home directory.
"""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sys

import state_io

MISSING_KEY_MESSAGE = ("нет ключа подписи, запусти init заново "
                       "или восстанови ~/.autopilot/gate.key")


def key_path():
    home = os.environ.get("AUTOPILOT_HOME", "").strip()
    return (Path(home) if home else Path.home() / ".autopilot") / "gate.key"


DPAPI_PREFIX = b"dpapi:"
_warned = False


def _warn(text):
    """One warning line per process: the key stays a plain file, signing keeps working."""
    global _warned
    if not _warned:
        _warned = True
        print("gate_sign: " + text, file=sys.stderr)


def _dpapi(data, protect):
    """Windows DPAPI (CryptProtectData / CryptUnprotectData) for the current user; raises OSError."""
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    call = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    call.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                     ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    call.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    buf = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    src, out = Blob(len(data), buf), Blob()
    if not call(ctypes.byref(src), None, None, None, None, 0, ctypes.byref(out)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        kernel32.LocalFree(out.pbData)


def _write_key_file(path, data):
    """Temp file + replace_with_retry: a crash never leaves a half-written key."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    try:
        fd = os.open(str(temp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        state_io.replace_with_retry(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _protected(key):
    """Key as stored on this OS: DPAPI block on Windows (plain bytes if DPAPI fails), else as is."""
    if os.name == "nt":
        try:
            return DPAPI_PREFIX + base64.b64encode(_dpapi(key, True))
        except Exception as exc:
            _warn("DPAPI недоступен (%s), ключ хранится обычным файлом" % type(exc).__name__)
    return key


def _create_key_atomically(path, data, replace_empty):
    """Full key in a temp file, then os.link: the key appears whole or not at all, a loser keeps the winner's."""
    temp = path.with_name("%s.%d.%s.tmp" % (path.name, os.getpid(), secrets.token_hex(4)))
    try:
        fd = os.open(str(temp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        if replace_empty:  # an old empty file: nothing worth keeping, swap it for the full key
            state_io.replace_with_retry(temp, path)
            return
        try:
            os.link(str(temp), str(path))
        except FileExistsError:
            return
        except (OSError, NotImplementedError, AttributeError):
            # shortcut: volumes without hard links get O_EXCL create + write, a reader may see the file empty
            # for an instant; upgrade when such a volume matters
            try:
                fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                return
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
    finally:
        temp.unlink(missing_ok=True)


def ensure_key():
    """Create the key (0600, DPAPI-wrapped on Windows) if absent. Only `init --strict-routing` calls this."""
    path = key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        size = None
    if size is None or size == 0:  # an empty key would sign nothing
        _create_key_atomically(path, _protected(secrets.token_bytes(32)), size == 0)
    elif os.name == "nt" and not path.read_bytes().startswith(DPAPI_PREFIX):
        # an old plain key: same bytes, now under DPAPI (this is the only place that rewrites it;
        # tools copies from before this change cannot read the block, so upgrade them together)
        plain = path.read_bytes()
        wrapped = _protected(plain)
        if wrapped != plain:
            try:
                _write_key_file(path, wrapped)
            except OSError as exc:
                _warn("ключ не переписан под DPAPI (%s)" % type(exc).__name__)
    return path


def load_key():
    """The raw key bytes (plain or DPAPI block), or None. Read-only: only ensure_key rewrites the file."""
    try:
        stored = key_path().read_bytes()
    except OSError:
        return None
    if stored.startswith(DPAPI_PREFIX):
        try:
            return _dpapi(base64.b64decode(stored[len(DPAPI_PREFIX):]), False) or None
        except Exception:
            return None
    return stored or None


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
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_text(json.dumps(body), encoding="utf-8")
        state_io.replace_with_retry(temp, path)  # a crash between the two leaves the old record whole
    finally:
        temp.unlink(missing_ok=True)


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
