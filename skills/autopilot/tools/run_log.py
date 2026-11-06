#!/usr/bin/env python3
"""Журнал прогона: .autopilot/run-log.jsonl, одна строка на событие, только метаданные.

Журнал только пишет: `append` не бросает исключений, любой сбой — `False`. Он лежит вне
state.js, отпечатков и подписанных гейтов. При размере больше 1 МБ файл уходит в
run-log.1.jsonl (одна ротация, прежний файл затирается). Поля вне схемы отбрасываются,
строки длиннее 120 знаков обрезаются, значение с путём машины заменяется на "[path]".
"""
import datetime as dt
import json
import os
import re

NAME, ROTATED = "run-log.jsonl", "run-log.1.jsonl"
ROTATE_BYTES = 1024 * 1024
VALUE_MAX = 120
KINDS = {
    "phase": ("id", "act"),
    "ticket": ("id", "act", "cause"),
    "gate": ("g", "ok", "reason"),
    "tests": ("passed", "failed", "seconds", "source"),
    "reset": ("what", "id", "reason"),
    "wait": ("kind", "act"),
    "executor": ("agent_type", "role", "turns", "input", "output", "cache_read", "cache_write"),
}
MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/]|/(?:home|Users|root)/", re.I)
ROLE = re.compile(r"autopilot-(executor|reviewer|explorer|acceptance)-")
TEXT_FIELDS = ("t", "run", "id", "act", "cause", "g", "reason", "what", "kind", "agent_type", "role", "source")


def role_of(agent_type):
    """Роль субагента по имени профиля `autopilot-<роль>-…` (ремонтный исполнитель — executor)."""
    m = ROLE.match(agent_type) if isinstance(agent_type, str) else None
    return m.group(1) if m else "agent"


def _clean(value):
    if isinstance(value, str):
        if MACHINE_PATH.search(value):
            return "[path]"
        return value if len(value) <= VALUE_MAX else value[:VALUE_MAX - 1] + "…"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise TypeError("поле журнала: только строка, число или bool")


def append(autopilot_dir, kind, /, **fields):   # `kind` позиционный: у строки wait есть поле kind
    """Дописать одну строку; `run` — имя прогона. Никогда не бросает, при сбое → False."""
    try:
        if kind not in KINDS:
            return False
        row = {"t": dt.datetime.now().astimezone().replace(microsecond=0).isoformat(),
               "run": _clean(fields.pop("run", None)), "k": kind}
        row.update({k: _clean(v) for k, v in fields.items() if k in KINDS[kind] and v is not None})
        line = json.dumps(row, ensure_ascii=False) + "\n"
        path = os.path.join(autopilot_dir, NAME)
        try:
            big = os.path.getsize(path) > ROTATE_BYTES
        except OSError:
            big = False
        if big:
            os.replace(path, os.path.join(autopilot_dir, ROTATED))
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
        return True
    except Exception:
        return False


def read_all(autopilot_dir):
    """Обе части журнала по порядку; битые строки и нечитаемые файлы молча пропускаются."""
    return read_all_stats(autopilot_dir)[0]


def read_all_stats(autopilot_dir):
    """(строки-словари обеих частей журнала, число нечитаемых непустых строк)."""
    rows, skipped = [], 0
    for name in (ROTATED, NAME):
        try:
            with open(os.path.join(autopilot_dir, name), encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        for line in filter(str.strip, lines):
            try:
                row = json.loads(line)
            except ValueError:
                row = None
            if isinstance(row, dict):
                rows.append(row)
            else:
                skipped += 1
    return rows, skipped


def usage_from_transcript(path, max_bytes=5_000_000):
    """Сумма `message.usage` ответов ассистента в JSONL-транскрипте субагента; ошибка → None."""
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes + 1)
        lines = data.decode("utf-8", errors="replace").splitlines()
        if len(data) > max_bytes:
            lines = lines[:-1]                       # последняя строка могла оборваться
        seen = {}                                    # id сообщения → usage (потоковые дубли)
        for n, line in enumerate(lines):
            try:
                msg = json.loads(line).get("message")
            except (ValueError, AttributeError):
                continue
            if isinstance(msg, dict) and msg.get("role") == "assistant" \
                    and isinstance(msg.get("usage"), dict):
                seen[msg.get("id") or "#%d" % n] = msg["usage"]
        if not seen:
            return None
        num = lambda u, k: u[k] if isinstance(u.get(k), int) and not isinstance(u.get(k), bool) else 0
        return {"turns": len(seen),
                "input": sum(num(u, "input_tokens") for u in seen.values()),
                "output": sum(num(u, "output_tokens") for u in seen.values()),
                "cache_read": sum(num(u, "cache_read_input_tokens") for u in seen.values()),
                "cache_write": sum(num(u, "cache_creation_input_tokens") for u in seen.values())}
    except Exception:
        return None


def _seconds(a, b):
    try:
        return max(0, int((dt.datetime.fromisoformat(b) - dt.datetime.fromisoformat(a)).total_seconds()))
    except (TypeError, ValueError):
        return None


def _sound(r):
    """Строка вида из схемы, где текстовые поля — строки, а значений-списков и словарей нет."""
    return (isinstance(r, dict) and isinstance(r.get("k"), str) and r["k"] in KINDS
            and not any(isinstance(v, (list, dict)) for v in r.values())
            and all(isinstance(r.get(f), (str, type(None))) for f in TEXT_FIELDS))


def summarize(records, run=None, skipped=0):
    """Строки журнала → сводка: фазы, таски, шлюзы, тесты, сбросы, простои, токены.
    `skipped` — сколько строк не прочитано ранее; испорченные по структуре прибавляются."""
    records = list(records)
    skipped += sum(1 for r in records if not _sound(r))
    rows = [r for r in records if _sound(r) and (run is None or r.get("run") == run)]
    out = {"run": run or (rows[-1].get("run") if rows else None), "skipped": skipped, "phases": [], "tickets": [],
           "gates": [], "tests": {"runs": 0, "seconds": 0, "passed": None, "failed": None},
           "resets": [], "waits": {"count": 0, "seconds": 0}, "tokens": []}
    phases, tickets, open_waits = {}, {}, {}
    for r in rows:
        try:
            _fold(r, out, phases, tickets, open_waits)
        except Exception:                                # отчёт не должен падать на одной строке
            out["skipped"] += 1
    for p in phases.values():
        p["seconds"] = _seconds(p["start"], p["end"]) if p["end"] else None
    out["phases"], out["tickets"] = list(phases.values()), list(tickets.values())
    return out


def _fold(r, out, phases, tickets, open_waits):
    k, t = r.get("k"), r.get("t")
    if k == "phase":
        p = phases.setdefault(r.get("id"), {"id": r.get("id"), "start": None, "end": None, "act": None})
        if r.get("act") == "start":
            p["start"] = p["start"] or t
        else:
            p["start"] = p["start"] or t
            p["end"], p["act"] = t, r.get("act")
    elif k == "ticket":
        x = tickets.setdefault(r.get("id"), {"id": r.get("id"), "starts": 0, "retries": 0,
                                             "repairs": 0, "fails": 0, "reviews": 0,
                                             "done": False, "causes": []})
        act = r.get("act")
        if act in ("start", "retry", "repair", "fail", "review"):
            x[{"start": "starts", "retry": "retries", "repair": "repairs",
               "fail": "fails", "review": "reviews"}[act]] += 1
        if act == "done":
            x["done"] = True
        if r.get("cause") and r["cause"] not in x["causes"]:
            x["causes"].append(r["cause"])
    elif k == "gate":
        out["gates"].append({"g": r.get("g"), "ok": r.get("ok"), "reason": r.get("reason")})
    elif k == "tests":
        s = out["tests"]
        s["runs"] += 1
        s["seconds"] += r["seconds"] if isinstance(r.get("seconds"), (int, float)) else 0
        s["passed"], s["failed"] = r.get("passed"), r.get("failed")
    elif k == "reset":
        out["resets"].append({"what": r.get("what"), "id": r.get("id"), "reason": r.get("reason")})
    elif k == "wait":
        if r.get("act") == "start":
            open_waits[r.get("kind")] = t
        elif r.get("kind") in open_waits:
            out["waits"]["count"] += 1
            out["waits"]["seconds"] += _seconds(open_waits.pop(r["kind"]), t) or 0
    elif k == "executor":
        out["tokens"].append({key: r.get(key) for key in KINDS["executor"]})
        out["tokens"][-1]["role"] = r.get("role") or role_of(r.get("agent_type"))


def _cell(v):
    return "—" if v is None else str(v)


def _table(head, body):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    return lines + ["| " + " | ".join(_cell(c) for c in row) + " |" for row in body]


def render_report(summary, share=False):
    """Сводка → Markdown. `share=True`: только числа и типы ролей — без имени прогона,
    названий тасков и профилей, абсолютных времён, причин."""
    s, lines = summary, []
    lines.append("# Журнал прогона" + ("" if share else ": %s" % _cell(s.get("run"))))
    if s.get("skipped"):
        lines += ["", "пропущено испорченных строк: %d" % s["skipped"]]
    lines += ["", "## Фазы"]
    lines += _table(["фаза", "секунды"] if share else ["фаза", "начало", "конец", "итог", "секунды"],
                    [[p["id"], p["seconds"]] if share else
                     [p["id"], p["start"], p["end"], p["act"], p["seconds"]] for p in s["phases"]])
    lines += ["", "## Таски (повторы)"]
    head = ["№" if share else "таск", "старты", "повторы", "ремонты", "падения", "готов"]
    rows = [[i if share else x["id"], x["starts"], x["retries"], x["repairs"], x["fails"],
             "да" if x["done"] else "нет"] + ([] if share else [", ".join(x["causes"]) or None])
            for i, x in enumerate(s["tickets"], 1)]
    lines += _table(head if share else head + ["причины"], rows)
    t = s["tests"]
    lines += ["", "## Тесты", "запусков: %d · секунд: %s · последний: %s/%s"
              % (t["runs"], t["seconds"], _cell(t["passed"]), _cell(t["failed"]))]
    lines += ["", "## Сбросы", "статусов и шлюзов: %d" % len(s["resets"])]
    if not share:
        lines += ["- %s %s: %s" % (r["what"], _cell(r["id"]), _cell(r["reason"])) for r in s["resets"]]
    lines += ["", "## Простои", "ожиданий пользователя: %d · секунд: %d"
              % (s["waits"]["count"], s["waits"]["seconds"])]
    lines += ["", "## Токены"]
    cols = ("turns", "input", "output", "cache_read", "cache_write")
    body = []
    for n, e in enumerate(s["tokens"], 1):
        role = e.get("role") or role_of(e.get("agent_type"))
        body.append(([role] if share else [e.get("agent_type"), role]) + [e.get(c) or 0 for c in cols])
    lines += _table((["роль"] if share else ["исполнитель", "роль"]) + ["ходы", "вход", "выход", "кэш чтение", "кэш запись"], body)
    return "\n".join(lines) + "\n"
