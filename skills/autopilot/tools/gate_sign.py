#!/usr/bin/env python3
"""HMAC signing of strict-run gate records (routing, attestations, test evidence).

The key lives in the user's home (~/.autopilot/gate.key, or $AUTOPILOT_HOME),
outside the project, so editing project files cannot forge a signature. On Windows
the key is wrapped with DPAPI (`dpapi:` + base64), so the file alone is useless to
another user; elsewhere it is a 0600 file. Neither protects against a process that
runs as the same user and can read the home directory.

A `dpapi:` block is never treated as the key bytes themselves: a block that cannot
be unwrapped here (another account or machine, another OS) and a plain file that is
not a 32-byte key are reported as an unreadable key and never silently trusted.
"""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sys
import threading
import time

import state_io

MISSING_KEY_MESSAGE = ("нет ключа подписи, запусти init заново "
                       "или восстанови ~/.autopilot/gate.key")


def key_path():
    home = os.environ.get("AUTOPILOT_HOME", "").strip()
    return (Path(home) if home else Path.home() / ".autopilot") / "gate.key"


DPAPI_PREFIX = b"dpapi:"
KEY_UNREADABLE_MESSAGE = (
    "ключ подписи не читается: нет доступа, файл повреждён, защищён DPAPI другого пользователя "
    "или компьютера (блок dpapi: — не сам ключ), либо это не 32-байтный ключ; восстанови прежний "
    "~/.autopilot/gate.key, либо удали файл и запусти init заново "
    "(старые подписи этим ключом проверяться не будут)")
IS_WINDOWS = os.name == "nt"
_KEY_SIZE = 32
_warned = set()
_dpapi_lock = threading.Lock()


def _warn(text):
    """One warning line per distinct problem per process: a plain key keeps signing working."""
    if text not in _warned:
        _warned.add(text)
        print("gate_sign: " + text, file=sys.stderr)


def _dpapi(data, protect):
    """Windows DPAPI (CryptProtectData / CryptUnprotectData) for the current user; raises OSError."""
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    call = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    buf = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    src, out = Blob(len(data), buf), Blob()
    with _dpapi_lock:  # the prototypes below are shared by every thread and name this call's own Blob class
        call.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                         ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        call.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        if not call(ctypes.byref(src), None, None, None, None, 0, ctypes.byref(out)):
            raise ctypes.WinError()
        try:
            return ctypes.string_at(out.pbData, out.cbData)
        finally:
            kernel32.LocalFree(out.pbData)


def _write_key_file(path, data):
    """Temp file + replace_with_retry: a crash never leaves a half-written key; a unique temp
    name keeps two concurrent inits from writing over each other's temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("%s.%d.%s.tmp" % (path.name, os.getpid(), secrets.token_hex(4)))
    try:
        fd = os.open(str(temp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        state_io.replace_with_retry(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _protected(key):
    """Key as stored on this OS: a DPAPI block that reads back as `key`, else the plain bytes.

    The round-trip check matters for the old-plain-key rewrite: a block that cannot be
    unwrapped here must not replace a key that still works.
    """
    if IS_WINDOWS:
        try:
            wrapped = DPAPI_PREFIX + base64.b64encode(_dpapi(key, True))
            if _dpapi(base64.b64decode(wrapped[len(DPAPI_PREFIX):]), False) != key:
                raise OSError("DPAPI: защищённый блок не читается обратно")
            return wrapped
        except Exception as exc:
            _warn("DPAPI недоступен (%s), ключ хранится обычным файлом" % type(exc).__name__)
    return key


def _retry_busy(action, attempts=100):
    """Run `action`; on Windows a reader holding the file for an instant is a PermissionError: retry, then raise."""
    for attempt in range(attempts):
        try:
            return action()
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.02)


def _create_key_atomically(path, data):
    """Full key in a temp file, then os.link: the key appears whole or not at all, a loser keeps the winner's."""
    temp = path.with_name("%s.%d.%s.tmp" % (path.name, os.getpid(), secrets.token_hex(4)))
    try:
        fd = os.open(str(temp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
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


def _claim_path(path):
    return path.with_name(path.name + ".claim")


def _claim_empty(path):
    """Remove an old empty key: exactly one racer gets True; the rest get False and leave the file alone.

    The claim is a hard link at a fixed name (atomic, never overwrites). A racer whose `size == 0` is stale
    finds the whole key behind its claim, drops it and moves nothing: the earlier rename-aside took such a
    key off the path for an instant, a third racer wrote its own key there and the first one was lost.
    """
    claim = _claim_path(path)
    try:
        _retry_busy(lambda: os.link(str(path), str(claim)))
    except (FileExistsError, FileNotFoundError):  # a claim is held, or there is no file left to claim
        return False
    try:
        if claim.stat().st_size:  # filled between our stat and the claim: it is the real key
            return False
        try:
            _retry_busy(path.unlink)
        except FileNotFoundError:
            pass
        return True
    finally:
        try:
            _retry_busy(lambda: claim.unlink(missing_ok=True))
        except PermissionError as exc:  # a reader kept the claim open for the whole retry: the key stays as it is
            raise OSError("не удалось удалить заявку %s: файл занят; если процесс, который её создал, убит, "
                          "удали её вручную" % claim) from exc


def _wait_for_key(path):
    """A loser of the race returns only once the winner's key is whole (32 bytes is the plain minimum)."""
    for _ in range(250):
        try:
            if path.stat().st_size >= _KEY_SIZE:
                return True
        except OSError:
            pass
        time.sleep(0.02)
    return False


def ensure_key():
    """Create the key (0600, DPAPI-wrapped on Windows) if absent; never replace a damaged one.

    Only `init --strict-routing` calls this. An old empty file is claimed by exactly one
    racer (see _claim_empty); a winner that dies before writing is retried. An existing
    key that does not read back (a foreign DPAPI block, a truncated plain file) is a
    clear OSError instead of a silent rewrite: rewriting would invalidate every signature.
    """
    path = key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            size = None
        if size == 0:  # an empty key would sign nothing; one racer swaps it
            if _claim_empty(path):
                size = None
            elif not _wait_for_key(path):
                continue  # the winner died between the claim and the write: retry
        if size is None:
            _create_key_atomically(path, _protected(secrets.token_bytes(_KEY_SIZE)))
            if not _wait_for_key(path):
                continue
        stored, key, problem = _stored_key()
        if problem == "missing":  # a racer removed the file: retry instead of returning no key
            continue
        if problem is not None:
            _warn(KEY_UNREADABLE_MESSAGE)
            raise OSError(KEY_UNREADABLE_MESSAGE)
        if IS_WINDOWS and not stored.startswith(DPAPI_PREFIX):
            # an old plain key: same bytes, now under DPAPI (this is the only place that rewrites
            # it; an unreadable block is never written over a working key, see _protected)
            wrapped = _protected(stored)
            if wrapped != stored:
                try:
                    _write_key_file(path, wrapped)
                except OSError as exc:
                    _warn("ключ не переписан под DPAPI (%s)" % type(exc).__name__)
        return path
    raise OSError("не удалось создать ключ подписи %s: файл остался пустым или занят; если рядом лежит %s "
                  "от убитого процесса, удали её" % (path, _claim_path(path)))


def _stored_key():
    """(stored bytes, raw key bytes or None, problem): problem is None, "missing" or "unreadable".

    A `dpapi:` block is never returned as the key, and a plain file must be exactly 32 bytes.
    """
    try:
        stored = key_path().read_bytes()
    except FileNotFoundError:
        return b"", None, "missing"
    except OSError:
        return b"", None, "unreadable"
    if not stored:
        return stored, None, "missing"
    if stored.startswith(DPAPI_PREFIX):
        if not IS_WINDOWS:
            return stored, None, "unreadable"
        try:
            raw = _dpapi(base64.b64decode(stored[len(DPAPI_PREFIX):]), False)
        except Exception:
            return stored, None, "unreadable"
        if len(raw) != _KEY_SIZE:
            return stored, None, "unreadable"
        return stored, raw, None
    if len(stored) != _KEY_SIZE:
        return stored, None, "unreadable"
    return stored, stored, None


def load_key():
    """The raw 32-byte key, or None. Read-only: only ensure_key rewrites the file."""
    _, key, problem = _stored_key()
    if problem == "unreadable":
        _warn(KEY_UNREADABLE_MESSAGE)
    return key


def sign(payload):
    """Hex HMAC-SHA256 over canonical JSON; a `sig` field is never part of the payload."""
    _, key, problem = _stored_key()
    if key is None:
        raise ValueError(KEY_UNREADABLE_MESSAGE if problem == "unreadable" else MISSING_KEY_MESSAGE)
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
