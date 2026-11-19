"""Молчание агента и долгая стадия: только чтение, агентов не останавливает (это делает оркестратор)."""
import datetime as dt
import glob
import os
import time

DEFAULT_LIMIT = 600


def limit_from_env():
    """Срок молчания в секундах из AUTOPILOT_SILENCE_SECONDS; не число или ≤ 0 — по умолчанию."""
    try:
        value = int(os.environ.get("AUTOPILOT_SILENCE_SECONDS", ""))
    except ValueError:
        return DEFAULT_LIMIT
    return value if value > 0 else DEFAULT_LIMIT


def silent_agents(subagents_dir, limit, now=None):
    """`agent-*.jsonl`, не менявшиеся дольше `limit` секунд → [{"file", "idle"}]."""
    now = time.time() if now is None else now
    found = []
    for path in sorted(glob.glob(os.path.join(glob.escape(subagents_dir), "agent-*.jsonl"))):
        try:
            idle = int(now - os.path.getmtime(path))
        except OSError:
            continue
        if idle > limit:
            found.append({"file": os.path.basename(path), "idle": idle})
    return found


def long_stages(stages, minutes=60, now=None):
    """Открытые стадии, идущие дольше `minutes` (по открытому отрезку, иначе по startedAt) → [(id, минут)]."""
    now = now or dt.datetime.now().astimezone()
    out = []
    for s in stages or []:
        if s.get("status") != "active":
            continue
        segs = s.get("segments") or []
        began = segs[-1].get("startedAt") if segs and not segs[-1].get("finishedAt") else (None if segs else s.get("startedAt"))
        try:
            mins = int((now - dt.datetime.fromisoformat(began)).total_seconds() // 60)
        except (TypeError, ValueError):
            continue
        if mins > minutes:
            out.append((s.get("id"), mins))
    return out
