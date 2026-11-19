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

NAME, ROTATED, FAIL = "run-log.jsonl", "run-log.1.jsonl", "run-log.fail"
ROTATE_BYTES = 1024 * 1024
VALUE_MAX = 120
SPEND_FIELDS = ("source", "origin", "role", "ticket", "agent", "agent_type", "model", "effort",
                "turns", "input", "output", "cache_read", "cache_write")
SPEND_KINDS = ("executor", "spend")
KINDS = {
    "phase": ("id", "act"),
    "ticket": ("id", "act", "cause", "class", "model", "effort"),
    "gate": ("g", "ok", "reason"),
    "tests": ("passed", "failed", "seconds", "source"),
    "reset": ("what", "id", "reason"),
    "wait": ("kind", "act"),
    # executor — историческое имя строки расхода; spend — то же для новых источников.
    "executor": SPEND_FIELDS,
    "spend": SPEND_FIELDS,
}
MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/]|/(?:home|Users|root)/", re.I)
ROLE = re.compile(r"autopilot-(executor|reviewer|explorer|acceptance)(?:-|$)")
TEXT_FIELDS = ("t", "run", "id", "act", "cause", "g", "reason", "what", "kind", "agent_type", "role",
               "source", "origin", "agent", "ticket", "class")


def role_of(agent_type):
    """Роль субагента по имени профиля `autopilot-<роль>` или `autopilot-<роль>-…` (ремонтный исполнитель — executor)."""
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
        _count_failure(autopilot_dir)
        return False


def _count_failure(autopilot_dir):
    """Число сбоев записи в run-log.fail: владелец видит, что журнал неполный. Не бросает."""
    try:
        path = os.path.join(autopilot_dir, FAIL)
        try:
            with open(path, encoding="utf-8") as f:
                count = int(f.read().strip() or 0)
        except (OSError, ValueError):
            count = 0
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(count + 1))
    except Exception:
        pass


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
            except (ValueError, RecursionError):
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
            except (ValueError, AttributeError, RecursionError):
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


def _moment(value):
    """ISO-время (с `Z` или без пояса — тогда UTC) → aware datetime; не разобрать → None."""
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
    try:
        m = dt.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return m if m.tzinfo else m.replace(tzinfo=dt.timezone.utc)


def usage_by_model(path, since, until=None):
    """Токены главной сессии по моделям из JSONL-журнала Claude Code: {модель: {turns, input,
    output, cache_read, cache_write}}. Читает построчно (журнал бывает десятки МБ); берёт ответы
    ассистента с `timestamp` в [since, until], без `isSidechain`, повтор `message.id` — последний.
    Текст сообщений не читается и не сохраняется. Нечитаемый файл → None."""
    lo, hi = _moment(since), _moment(until)
    seen = {}                                        # id ответа → (модель, usage)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f):
                try:
                    r = json.loads(line)
                    msg = r.get("message")
                    if r.get("isSidechain") is True or not isinstance(msg, dict) or msg.get("role") != "assistant" \
                            or not isinstance(msg.get("usage"), dict):
                        continue
                    at = _moment(r.get("timestamp"))
                    if at is None or (lo and at < lo) or (hi and at > hi):
                        continue
                    seen[msg.get("id") or "#%d" % n] = (msg.get("model") if isinstance(msg.get("model"), str)
                                                        and msg.get("model") else "unknown", msg["usage"])
                except (ValueError, AttributeError, RecursionError):
                    continue
    except OSError:
        return None
    num = lambda u, k: u[k] if isinstance(u.get(k), int) and not isinstance(u.get(k), bool) and u[k] > 0 else 0
    out = {}
    for model, u in seen.values():
        a = out.setdefault(model, dict.fromkeys(("turns", "input", "output", "cache_read", "cache_write"), 0))
        a["turns"] += 1
        for key, field in (("input", "input_tokens"), ("output", "output_tokens"),
                           ("cache_read", "cache_read_input_tokens"), ("cache_write", "cache_creation_input_tokens")):
            a[key] += num(u, field)
    return out


def usage_by_agent(folder, since, until=None):
    """Токены субагентов из `folder/agent-*.jsonl` (+ `.meta.json`): список по агентам
    {agent, agent_type, model, first_at, turns, input, output, cache_read, cache_write}.
    Берёт ответы ассистента с `timestamp` в [since, until]; повтор `message.id` — последний.
    Читаются только числа, модель, id, время и `agentType`; текст не читается и не сохраняется.
    Нет папки или она не читается → None; агентов нет → []."""
    lo, hi = _moment(since), _moment(until)
    try:
        names = sorted(n for n in os.listdir(folder) if re.fullmatch(r"agent-.+\.jsonl", n))
    except OSError:
        return None
    num = lambda u, k: u[k] if isinstance(u.get(k), int) and not isinstance(u.get(k), bool) and u[k] > 0 else 0
    out = []
    for name in names:
        seen, first = {}, None                       # id ответа → (модель, usage); самое раннее время
        try:
            with open(os.path.join(folder, name), encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f):
                    try:
                        r = json.loads(line)
                        m = r.get("message")
                        if not isinstance(m, dict) or m.get("role") != "assistant" or not isinstance(m.get("usage"), dict):
                            continue
                        at = _moment(r.get("timestamp"))
                        if at is None or (lo and at < lo) or (hi and at > hi):
                            continue
                        seen[m.get("id") or "#%d" % n] = (m["model"] if isinstance(m.get("model"), str) and m["model"]
                                                           else "unknown", m["usage"])
                        if first is None or at < first[0]:
                            first = (at, r["timestamp"])
                    except (ValueError, AttributeError, RecursionError):
                        continue
        except OSError:
            continue
        if not seen:
            continue
        agent_type = "agent"
        try:
            with open(os.path.join(folder, name[:-len(".jsonl")] + ".meta.json"), encoding="utf-8-sig") as f:
                t = json.load(f).get("agentType")
            if isinstance(t, str) and t:
                agent_type = t
        except (OSError, ValueError, AttributeError, RecursionError):
            pass
        usages = [u for _, u in seen.values()]
        out.append({"agent": name[len("agent-"):-len(".jsonl")], "agent_type": agent_type,
                    "model": list(seen.values())[-1][0], "first_at": first[1], "turns": len(seen),
                    "input": sum(num(u, "input_tokens") for u in usages),
                    "output": sum(num(u, "output_tokens") for u in usages),
                    "cache_read": sum(num(u, "cache_read_input_tokens") for u in usages),
                    "cache_write": sum(num(u, "cache_creation_input_tokens") for u in usages)})
    return out


def collapse_agents(rows):
    """Строки расхода (`executor`) без повторов: последняя строка на `agent`; строки журнала Claude Code
    (с `agent`) профилей `autopilot-…` отбрасываются, только если хук записал строку с тем же `agent_type`:
    хук записал не всех агентов — расход остальных не теряется."""
    hooked = {r.get("agent_type") for r in rows if not r.get("agent") and r.get("role") != "orchestrator"}
    last, rest = {}, []
    for r in rows:
        a = r.get("agent")
        if not a:
            rest.append(r)
        elif not (str(r.get("agent_type") or "").startswith("autopilot-") and r.get("agent_type") in hooked):
            last[a] = r
    return rest + list(last.values())


def run_key(name):
    """Имя прогона без `--wip`: журнал мог писаться до переименования папки."""
    return str(name or "").removesuffix("--wip")


def is_spend(row):
    """Строка единого журнала расхода: старый `executor` или новый `spend`."""
    return isinstance(row, dict) and row.get("k") in SPEND_KINDS


def normalize_spend(row):
    """Приводит строку журнала к одному набору полей; мусорные числа — 0, не падает."""
    fields = KINDS.get(row.get("k"), SPEND_FIELDS)
    out = {key: row.get(key) for key in ("t", "run") + tuple(fields)}
    out["source"] = row.get("source") or "claude"
    out["role"] = row.get("role") or role_of(row.get("agent_type"))
    for key in ("turns", "input", "output", "cache_read", "cache_write"):
        v = row.get(key)
        out[key] = v if isinstance(v, int) and not isinstance(v, bool) and v > 0 else 0
    out["tokens"] = out["input"] + out["output"]
    den = out["input"] + out["cache_read"] + out["cache_write"]
    out["hit"] = round(100 * out["cache_read"] / den) if den else None
    return out


def spend_rows(records, run, collapse=True):
    """Единый журнал расхода одного прогона: нормализованные строки, без повторов агентов."""
    rows = [normalize_spend(r) for r in records
            if is_spend(r) and run_key(r.get("run")) == run_key(run)]
    return collapse_agents(rows) if collapse else rows


def spend_snapshot(records, run, limit=200):
    """Последние строки журнала для state.spendLedger: стабильный хронологический срез."""
    rows = sorted(spend_rows(records, run), key=lambda r: str(r.get("t") or ""))
    return rows[-max(0, int(limit)):]


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
    out["tokens"] = collapse_agents(out["tokens"])
    last = {}                                        # оркестратор: последняя строка на модель, как в compute_spend
    for e in out["tokens"]:
        if e["role"] == "orchestrator":
            last[e.get("model")] = e
    out["tokens"] = [e for e in out["tokens"] if e["role"] != "orchestrator"] + list(last.values())
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
    elif k in SPEND_KINDS:
        out["tokens"].append({key: r.get(key) for key in KINDS[k]})
        out["tokens"][-1]["role"] = r.get("role") or role_of(r.get("agent_type"))


def _cell(v):
    return "—" if v is None else str(v)


def _table(head, body):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    return lines + ["| " + " | ".join(_cell(c) for c in row) + " |" for row in body]


def _count(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v > 0 else 0


def _cache_table(head, entries, key):
    """Чтение и запись кэша и доля попаданий (читали / вход + читали + писали) по ключу `key(запись)`."""
    acc = {}
    for e in entries:
        a = acc.setdefault(key(e), [0, 0, 0])
        a[0] += _count(e.get("input"))
        a[1] += _count(e.get("cache_read"))
        a[2] += _count(e.get("cache_write"))
    return _table([head, "кэш чтение", "кэш запись", "доля попаданий"],
                  [[k, r, w, ("%d%%" % round(100 * r / (i + r + w))) if i + r + w else None]
                   for k, (i, r, w) in acc.items()])


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
    lines += ["", "## Кэш по ролям"] + _cache_table("роль", s["tokens"], lambda e: e.get("role") or role_of(e.get("agent_type")))
    if not share:
        lines += ["", "## Кэш по профилям"] + _cache_table("профиль", [e for e in s["tokens"] if e.get("agent_type")],
                                                           lambda e: e.get("agent_type"))
    return "\n".join(lines) + "\n"
