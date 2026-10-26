#!/usr/bin/env python3
"""Учёт прогона Autopilot: состояние, дашборд, сервер — одной командой на событие.

Агент не правит .autopilot/state.js руками. Каждое событие прогона — один вызов:

    python3 .autopilot/ap.py init --slug S --title "…" --mode semi --depth normal \\
                                  --memory-file AGENTS.md --memory-owner autopilot --skill-dir /abs
    python3 .autopilot/ap.py stage spec                 # открыть этап (прошлые закроются сами)
    python3 .autopilot/ap.py stage briefing skip --note "полный автомат — самобрифинг"
    python3 .autopilot/ap.py set tier=T2 baseCommit=a1b2c3d
    python3 .autopilot/ap.py tickets                    # опубликовать таски из <dir>/tickets/*.md
    python3 .autopilot/ap.py check-plan                 # гейт G3: трасса манифест ↔ таски
    python3 .autopilot/ap.py ticket 02 03 start         # волна ушла
    python3 .autopilot/ap.py ticket 02 review
    python3 .autopilot/ap.py ticket 02 repair --note "пустой адрес проходит — R01.1"
    python3 .autopilot/ap.py ticket 02 done --tests 34/0 --commit a1b2c3d
    python3 .autopilot/ap.py ticket 03 retry | fail --note "…" | reset
    python3 .autopilot/ap.py stage build done | fail --note "…"
    python3 .autopilot/ap.py add concerns "src/notify.ts:40 — два формата даты"
    python3 .autopilot/ap.py add debt.emptyEnv TELEGRAM_BOT_TOKEN
    python3 .autopilot/ap.py coverage found=2 fixed=1 deferred=1 --item "R07 — отложено: …"
    python3 .autopilot/ap.py add report "Два формата даты в уведомлениях — оставлено"
    python3 .autopilot/ap.py blind checked=12 matched=11 --mismatch "R07 — статус не виден"
    python3 .autopilot/ap.py tests 34/0                 # последний полный прогон
    python3 .autopilot/ap.py ask briefing --note "три вопроса в чате"   # ждём пользователя
    python3 .autopilot/ap.py answered                   # ответил (stage/ticket закрывают сами)
    python3 .autopilot/ap.py finish --result "Бот принимает заявки и пишет их в таблицу"
    python3 .autopilot/ap.py reopen                     # второй бриф в сданном прогоне
    python3 .autopilot/ap.py commits                    # коммиты сданных тасков ещё в истории?
    python3 .autopilot/ap.py                            # просто синхронизировать

После каждой команды: updatedAt = сейчас (и метка в журнале beats), строка в ленте log,
счётчики и список требований — из manifest.md, гейты G1–G4 — из событий, которые их решают,
пройденные этапы закрыты, снимок вписан в dashboard.html, сервер жив. Время
ставит сам скрипт, с секундами и поясом, — агент его не пишет никогда.

Флаги: --check-update (сверить версию навыка с GitHub), --no-serve, --stop.
Работает на macOS, Linux и Windows (в том числе из Git Bash).
"""

import datetime as dt
import hashlib
import importlib.util
import contextlib
import glob
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

for _s in (sys.stdout, sys.stderr):                       # cp1251-консоль Windows
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

A = os.path.dirname(os.path.abspath(__file__))          # .autopilot этого проекта
ROOT = os.path.dirname(A)
STATE = os.path.join(A, "state.js")
PAGE = os.path.join(A, "dashboard.html")
README = os.path.join(A, "README.md")
PIDF = os.path.join(A, "serve.pid")
LOG = os.path.join(A, "serve.log")
LOCK = os.path.join(A, "state.lock")
BEGIN, END = "/*STATE-BEGIN*/", "/*STATE-END*/"
WIN = os.name == "nt"
REPO = "mrAibo/Autopilot"
REMOTE_SKILL = "https://raw.githubusercontent.com/%s/main/skills/autopilot/SKILL.md" % REPO
STOP_DELAY = 12
BEATS_KEPT = 2000
LOG_KEPT = 300
QUOTE_MAX = 240
WAIT_KINDS = ("briefing", "spec", "plan", "action", "stop")
# Команды, которые значат «работа пошла дальше»: ожидание пользователя ими закрывается,
# даже если `answered` забыли.
MOVES_ON = {"stage", "ticket", "tickets", "check-plan", "coverage", "blind", "tests", "finish", "reopen"}
ORDER = ["preflight", "manifest", "briefing", "spec", "plan", "build", "review", "final"]
# Этап, чей результат лежит на диске, пройден — даже если его забыли отметить.
ARTIFACT = {"manifest": "manifest.md", "spec": "spec.md", "plan": "tickets/*.md"}
TICKET_STATUSES = {"start": "in-progress", "review": "review", "repair": "repair",
                   "done": "done", "fail": "failed", "retry": "in-progress", "reset": "pending",
                   "route": "pending"}
LISTS = {"concerns", "additions", "report", "debt.placeholders", "debt.assumptions", "debt.emptyEnv"}


def now():
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def die(msg):
    print("ошибка: " + msg)
    sys.exit(1)


# ── состояние ───────────────────────────────────────────────────────────────

@contextlib.contextmanager
def locked_state(timeout=10):
    """Cross-platform exclusive process lock. Never delete the lock file."""
    with open(LOCK, "a+b") as f:
        f.seek(0)
        if not f.read(1):
            f.seek(0)
            f.write(b"1")
            f.flush()
        f.seek(0)
        deadline = time.monotonic() + timeout
        while True:
            try:
                if WIN:
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, BlockingIOError):
                if time.monotonic() >= deadline:
                    die("state.lock занят другой сессией; повтори команду позднее")
                time.sleep(.08)
        try:
            yield
        finally:
            if WIN:
                import msvcrt
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def read_state():
    try:
        raw = open(STATE, encoding="utf-8").read()
    except FileNotFoundError:
        return None
    body = raw.split("=", 1)[1] if "=" in raw.split("\n", 1)[0] else raw
    try:
        return json.loads(body.strip().rstrip(";"))
    except json.JSONDecodeError as e:
        die("state.js не разбирается (строка %d: %s) — перезапиши его командой init "
            "или поправь строку" % (e.lineno, e.msg))


def save(state):
    state["rev"] = (state.get("rev") or 0) + 1        # дашборд перерисовывается по нему
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("window.STATE =\n" + json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, STATE)


def beat(state):
    """Журнал пульса: каждое событие оставляет метку. updatedAt перезаписывается,
    и без журнала дашборд знал о прошлых событиях, только если сам их видел, —
    уснул экран или упал сервер, и рабочее время между редкими метками
    обрезалось как простой."""
    beats = state.setdefault("beats", [])
    if state["updatedAt"] not in beats:
        beats.append(state["updatedAt"])
    del beats[:-BEATS_KEPT]


def log(state, event, **kw):
    """Лента событий для дашборда: что случилось, словами страницы, а не агента.
    Пишет скрипт сам, по команде, — от агента ничего сверх обычного вызова не нужно."""
    entry = {"t": state["updatedAt"], "k": event}
    entry.update({k: v for k, v in kw.items() if v not in (None, "", [])})
    state.setdefault("log", []).append(entry)
    del state["log"][:-LOG_KEPT]


def set_gate(state, g, ok, **kw):
    """Гейт решается событием, которое его проверяет: G1 — открытием спецификации,
    G2 — coverage, G3 — check-plan, G4 — blind. Повторная проверка перезаписывает."""
    rec = {"ok": bool(ok), "at": state["updatedAt"]}
    rec.update({k: v for k, v in kw.items() if v is not None})
    state.setdefault("gates", {})[g] = rec
    log(state, "gate", g=g, ok=bool(ok), **kw)


def close_wait(state):
    """Ожидание пользователя кончилось: интервал уходит в waits — часы дашборда
    его не считают, это не работа сборки."""
    w = state.get("waiting")
    if not w:
        return
    state.setdefault("waits", []).append({"kind": w.get("kind"), "from": w.get("since"),
                                          "to": state["updatedAt"]})
    state["waiting"] = None
    log(state, "answered", kind=w.get("kind"))


def run_dir(state):
    name = state.get("dir") or ""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*(?:--wip)?", name):
        die("недопустимое имя папки прогона: %r" % name)
    return os.path.join(A, name)


def fresh_state(a):
    t = now()
    return {
        "version": 2,
        "slug": a["slug"], "dir": "%s-%s--wip" % (t[:10], a["slug"]),
        "title": a.get("title") or a["slug"],
        "mode": a.get("mode") or "semi", "depth": a.get("depth") or "normal",
        "tier": None, "strictRouting": bool(a.get("strict-routing")),
        "isolateTickets": bool(a.get("isolated-tickets")),
        "briefFile": a.get("brief-file"),
        "memoryFile": a.get("memory-file") or "AGENTS.md",
        "memoryOwner": a.get("memory-owner") or "autopilot",
        "skillDir": a.get("skill-dir"), "baseCommit": None,
        "startedAt": t, "updatedAt": t, "finishedAt": None,
        "stages": [{"id": "preflight", "status": "active", "startedAt": t}]
                  + [{"id": s, "status": "pending"} for s in ORDER[1:]],
        "requirements": {"total": 0, "done": 0, "inTicket": 0, "inSpec": 0,
                         "placeholder": 0, "deferred": 0, "dropped": 0},
        "tickets": [], "tests": None, "usageEvents": [], "budgetTokens": None,
        "debt": {"placeholders": [], "assumptions": [], "emptyEnv": []},
        "additions": [], "coverage": None, "concerns": [], "blind": None, "beats": [t],
        "rev": 0, "waiting": None, "waits": [], "log": [], "reqList": [], "gates": {}, "result": None,
    }


# ── манифест и таски ────────────────────────────────────────────────────────

ROW_ID = re.compile(r"^[RGD]\d+[a-z]?$")
PIPE = re.compile(r"(?<!\\)\|")          # «\|» внутри цитаты — не граница колонки


def cells_of(line):
    return PIPE.split(line.strip().strip("|"))
STATUS_KEY = {"done": "done", "in-ticket": "inTicket", "in-spec": "inSpec",
              "placeholder": "placeholder", "deferred": "deferred", "dropped": "dropped"}


def plain(cell):
    """Ячейка манифеста как текст для страницы: без разметки, «\\|» — обратно в «|»."""
    t = re.sub(r"\*+|`", "", cell.replace("\\|", "|")).strip()
    return t if len(t) <= QUOTE_MAX else t[:QUOTE_MAX - 1].rstrip() + "…"


def manifest_table(state):
    """Строки manifest.md: ID в первой колонке, цитата во второй, статус в третьей,
    основание в четвёртой."""
    try:
        text = open(os.path.join(run_dir(state), "manifest.md"), encoding="utf-8").read()
    except OSError:
        return None
    rows = []
    for line in text.splitlines():
        raw = cells_of(line)
        cells = [c.strip().strip("`*") for c in raw]
        if len(cells) >= 3 and ROW_ID.match(cells[0]):
            rows.append({"id": cells[0], "text": plain(raw[1]) if len(raw) > 1 else "",
                         "status": cells[2].split()[0].lower() if cells[2] else "open",
                         "why": plain(raw[3]) if len(raw) > 3 else ""})
    return rows


def manifest_rows(state):
    """[(id, status)] из таблицы manifest.md."""
    rows = manifest_table(state)
    return None if rows is None else [(r["id"], r["status"]) for r in rows]


def recount(state):
    table = manifest_table(state)
    if table is None:
        return
    # Список для страницы — слова пользователя и что с ними стало. Основание нужно
    # только там, где требование не сделано как написано.
    state["reqList"] = [dict({"id": r["id"], "text": r["text"], "status": r["status"]},
                             **({"why": r["why"]} if r["status"] in ("placeholder", "deferred", "dropped")
                                and r["why"] not in ("", "—", "-") else {}))
                        for r in table if not r["id"].startswith("D")]
    rows = [(r["id"], r["status"]) for r in table]
    rows = [(i, st) for i, st in rows if not i.startswith("D")]   # D## — ограничение, не требование
    r = {"total": len(rows), "done": 0, "inTicket": 0, "inSpec": 0,
         "placeholder": 0, "deferred": 0, "dropped": 0}
    for _, st in rows:
        if st in STATUS_KEY:
            r[STATUS_KEY[st]] += 1
    state["requirements"] = r


def manifest_update(state, changes):
    """Переписывает статус (третья колонка) и «Где» (пятая) у строк манифеста.
    changes: {id: (статус, добавка к «Где»)}. Возвращает список изменённых id."""
    path = os.path.join(run_dir(state), "manifest.md")
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except OSError:
        return []
    touched = []
    for n, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        cells = cells_of(line)
        rid = cells[0].strip().strip("`*") if cells else ""
        if rid not in changes or len(cells) < 3:
            continue
        status, where = changes[rid]
        cells[2] = " %s " % status
        if where and len(cells) >= 5:
            cur = cells[4].strip()
            cells[4] = " %s " % (where if cur in ("", "—", "-") else
                                 cur if where in cur else "%s → %s" % (cur, where))
        lines[n] = "|" + "|".join(cells) + "|"
        touched.append(rid)
    if touched:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    return touched


FIELD = re.compile(r"^\*\*([^*:]+):?\*\*:?\s*(.*)$")


def parse_ticket(path):
    text = open(path, encoding="utf-8").read()
    base = os.path.basename(path)
    tid = re.match(r"(\w+?)[-_.]", base)
    tid = tid.group(1) if tid else base[:2]
    title = ""
    f = {}
    for line in text.splitlines():
        s = line.strip()
        if not title and s.startswith("# "):
            title = re.sub(r"^#\s*\w+\s*[—–-]\s*", "", s).strip() or s[2:]
        m = FIELD.match(s)
        if m:
            f[m.group(1).strip().lower()] = m.group(2).strip()

    def ids(v):
        return [x for x in re.findall(r"[A-Za-z]*\d+[a-z]?(?:\.\d+)?", v or "")]

    def get(*names):
        for n in names:
            if n in f:
                return f[n]
        return ""
    wave = re.search(r"\d+", get("волна", "wave"))
    return {
        "id": tid, "title": title,
        "requirements": ids(get("требования", "requirements")),
        "blockedBy": [x.zfill(2) for x in re.findall(r"\d+", get("зависит от", "blocked by"))],
        "wave": int(wave.group()) if wave else None,
        "zone": re.findall(r"`([^`]+)`", get("зона", "zone")),
        "review": get("ревью", "review") or None,
        "model": get("модель", "model") or None,
    }


def publish_tickets(state):
    files = sorted(glob.glob(os.path.join(run_dir(state), "tickets", "*.md")))
    if not files:
        return "в %s/tickets/ нет файлов" % state.get("dir")
    old = {t["id"]: t for t in state.get("tickets") or []}
    out = []
    for p in files:
        t = parse_ticket(p)
        t["fingerprint"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        prev = old.get(t["id"], {})
        if prev.get("fingerprint") and prev["fingerprint"] != t["fingerprint"]:
            if prev.get("worktree") and prev["worktree"].get("status") not in ("released",):
                die("таск %s изменён при существующем worktree; завершите и освободите его вручную" % t["id"])
            prev = {}
        for k in ("status", "startedAt", "finishedAt", "retries", "repairs", "repairFindings",
                  "tests", "commit", "concerns", "placeholders", "routing", "worktree", "retryAdvice"):
            if k in prev:
                t[k] = prev[k]
        t.setdefault("status", "pending")
        t.setdefault("retries", 0)
        t.setdefault("repairs", 0)
        out.append(t)
    state["tickets"] = out
    rows = dict(manifest_rows(state) or [])
    where = {}
    for t in out:
        for r in {x.split(".")[0] for x in t["requirements"]}:
            where.setdefault(r, []).append("T" + t["id"])
    moved = manifest_update(state, {r: ("in-ticket", ", ".join(w)) for r, w in where.items()
                                    if rows.get(r) == "in-spec"})
    return "тасков опубликовано: %d%s" % (len(out), (" · в манифесте in-ticket: %d" % len(moved)) if moved else "")


def check_plan(state):
    """G3 механически: каждое живое требование — в таске, каждый таск — от требования,
    у каждого таска зона и волна, в одной волне зоны не пересекаются."""
    problems = []
    rows = manifest_rows(state)
    if not rows:
        problems.append("манифест отсутствует или пуст")
    publish_tickets(state)
    tickets = state.get("tickets") or []
    if not tickets:
        problems.append("план пуст: нет ни одного таска")
    rows = rows or []
    if len({t["id"] for t in tickets}) != len(tickets):
        problems.append("повторяются номера тасков")
    named = {r for t in tickets for r in t["requirements"]}
    base = {r.split(".")[0] for r in named}
    for rid, st in rows:
        if st in ("in-spec", "in-ticket", "placeholder") and not rid.startswith("D") and rid not in base:
            problems.append("требование %s (%s) не попало ни в один таск" % (rid, st))
    known = {rid for rid, _ in rows}
    ids = {t["id"] for t in tickets}
    for t in tickets:
        own = [r for r in t["requirements"] if r.split(".")[0][:1] in "RGD"]
        if not t["requirements"]:
            problems.append("таск %s ни к чему не привязан — работа, которую никто не заказывал" % t["id"])
        for r in own:
            if r.split(".")[0] not in known:
                problems.append("таск %s ссылается на %s, которого нет в манифесте" % (t["id"], r))
        if not t["zone"]:
            problems.append("у таска %s нет зоны" % t["id"])
        if t["wave"] is None or t["wave"] < 1:
            problems.append("у таска %s нет допустимой волны" % t["id"])
        for b in t["blockedBy"]:
            if b not in ids:
                problems.append("таск %s зависит от несуществующего %s" % (t["id"], b))
    wave_of = {t["id"]: t["wave"] for t in tickets}
    for t in tickets:
        need = 1 + max([wave_of.get(b) or 0 for b in t["blockedBy"]] or [0])
        if t["wave"] is not None and t["wave"] < need:
            problems.append("таск %s в волне %s, но его зависимости позволяют не раньше %d"
                            % (t["id"], t["wave"], need))
    for i, a in enumerate(tickets):
        for b in tickets[i + 1:]:
            if a["wave"] is None or a["wave"] != b["wave"]:
                continue
            for za in a["zone"]:
                for zb in b["zone"]:
                    x, y = za.rstrip("/") + "/", zb.rstrip("/") + "/"
                    if x.startswith(y) or y.startswith(x):
                        problems.append("таски %s и %s в одной волне пишут в %s"
                                        % (a["id"], b["id"], za if len(za) >= len(zb) else zb))
    return problems


# ── этапы ───────────────────────────────────────────────────────────────────

def stage(state, sid):
    for s in state.get("stages") or []:
        if s.get("id") == sid:
            return s
    s = {"id": sid, "status": "pending"}
    state.setdefault("stages", []).append(s)
    return s


def close_passed(state):
    """Инвариант: раньше открытого этапа не бывает другого открытого. Прошлый
    закрывается временем открытия ближайшего следующего. Этап, который прогон
    проскочил, не отметив, закрывается, если его файл лежит на диске.
    skipped и failed — осознанные состояния, их не трогаем."""
    rank = {v: i for i, v in enumerate(ORDER)}
    stages = [s for s in state.get("stages") or [] if s.get("id") in rank]
    live = [s for s in stages if s.get("status") == "active"]
    closed = []
    for s in live:
        later = sorted(o["startedAt"] for o in live
                       if rank[o["id"]] > rank[s["id"]] and o.get("startedAt"))
        if later:
            s["status"], s["finishedAt"] = "done", later[0]
            closed.append("%s закрыт (%s)" % (s["id"], later[0][11:19]))
    reached = [rank[s["id"]] for s in stages if s.get("status") in ("active", "done")]
    if not reached:
        return closed
    edge = max(reached)
    for s in stages:
        art = ARTIFACT.get(s["id"])
        if s.get("status") != "pending" or rank[s["id"]] >= edge or not art or not state.get("dir"):
            continue
        if glob.glob(os.path.join(run_dir(state), art)):
            nxt = [o["startedAt"] for o in stages if rank[o["id"]] > rank[s["id"]] and o.get("startedAt")]
            when = min(nxt) if nxt else state.get("updatedAt")
            s["status"], s["startedAt"], s["finishedAt"] = "done", s.get("startedAt") or when, when
            closed.append("%s отмечен пройденным по файлу %s" % (s["id"], art))
    return closed


def audit(state):
    out = []
    rank = {v: i for i, v in enumerate(ORDER)}
    stages = state.get("stages") or []
    live = [rank[s["id"]] for s in stages if s.get("status") == "active" and s.get("id") in rank]
    if live:
        for s in stages:
            if s.get("status") == "pending" and rank.get(s.get("id"), 99) < max(live):
                out.append("этап %s пропущен в учёте: был — `stage %s done`, не было — `stage %s skip "
                           "--note причина`. Это бухгалтерия, не расследуй" % ((s["id"],) * 3))
    return out


# ── страница и сервер ───────────────────────────────────────────────────────

def write_snapshot(state):
    try:
        page = open(PAGE, encoding="utf-8").read()
    except FileNotFoundError:
        return "страницы нет — перекопируй dashboard.html из навыка"
    i, j = page.find(BEGIN), page.find(END)
    if i < 0 or j < 0:
        return "страница без маркеров снимка — перекопируй dashboard.html из навыка"
    payload = "window.STATE=" + json.dumps(state, ensure_ascii=False).replace("</", "<\\/") + ";"
    new = page[: i + len(BEGIN)] + payload + page[j:]
    if new != page:
        tmp = PAGE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, PAGE)
    return "дашборд обновлён"


def _run(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=10,
                              encoding="utf-8", errors="replace").stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _ps(script):
    return _run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script])


def cmdline(pid):
    if WIN:
        return _ps("(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CommandLine" % int(pid)).strip()
    return _run(["ps", "-p", str(pid), "-o", "command="]).strip()


def processes():
    out = []
    if WIN:
        text = _ps("Get-CimInstance Win32_Process -Filter \"Name LIKE 'python%'\" | "
                   "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }")
        for line in text.splitlines():
            num, _, cmd = line.partition("\t")
            if num.strip().isdigit():
                out.append((int(num), cmd))
    else:
        for line in _run(["ps", "-Ao", "pid=,command="]).splitlines():
            num, _, cmd = line.strip().partition(" ")
            if num.isdigit():
                out.append((int(num), cmd))
    return out


def _norm(path):
    return os.path.normcase(os.path.normpath(path)).replace("\\", "/")


_OURS = re.compile(r"--directory\s+\"?" + re.escape(_norm(A)) + r"\"?(?=\s|$)")


def is_ours(cmd):
    """Сервер этого проекта — и только он: `-m http.server` и ровно наш --directory.
    Узко намеренно: широкая проверка уже убивала чужие серверы."""
    c = cmd.replace("\\", "/")
    c = c.lower() if WIN else c
    return bool(re.search(r"-m\s+http\.server\b", c)) and bool(_OURS.search(c))


def kill(pid):
    try:
        os.kill(int(pid), 15)
    except (OSError, ValueError):
        pass


def recorded():
    try:
        port, pid = open(PIDF, encoding="utf-8").read().split()
        return int(port), int(pid)
    except (OSError, ValueError):
        return None, None


def http_ok(port):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/dashboard.html" % port, timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def free_port(prefer):
    """Прежний порт — в первую очередь: открытая вкладка опрашивает именно его и
    оживает сама, когда сервер вернулся. Убитый сервер оставляет порт в TIME_WAIT,
    и без SO_REUSEADDR проверка считала его занятым — сервер уезжал на новый порт,
    а вкладка оставалась мёртвой. http.server сам ставит этот флаг, так что порт
    ему достанется. На Windows флаг значит другое (захват чужого порта) — там без него."""
    for p in ([prefer] if prefer else []) + [0]:
        s = socket.socket()
        if not WIN:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", p))
            return s.getsockname()[1]
        except OSError:
            continue
        finally:
            s.close()
    return None


def kill_orphans(keep=None):
    n = 0
    for pid, cmd in processes():
        if pid not in (keep, os.getpid()) and is_ours(cmd):
            kill(pid)
            n += 1
    return n


def _detached():
    if WIN:
        return {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                | getattr(subprocess, "CREATE_NO_WINDOW", 0)}
    return {"start_new_session": True}


def serve(state):
    port, pid = recorded()
    if state.get("finishedAt"):
        kill_orphans(keep=pid)
        return "прогон закрыт"
    if os.environ.get("SSH_CONNECTION") or os.environ.get("CI"):
        return "удалённая сессия — без сервера, дашборд: %s" % PAGE
    if port and pid and http_ok(port) and is_ours(cmdline(pid)):
        return "http://localhost:%d/dashboard.html" % port
    kill_orphans()
    port = free_port(port)
    if not port:
        return "порт не нашёлся — дашборд открывается файлом: %s" % PAGE
    try:
        with open(LOG, "a", encoding="utf-8") as log:
            srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port),
                                    "--bind", "127.0.0.1", "--directory", A],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=log, **_detached())
    except OSError as e:
        return "сервер не запустился (%s) — дашборд открывается файлом: %s" % (e, PAGE)
    for _ in range(10):
        if http_ok(port):
            with open(PIDF, "w", encoding="utf-8") as f:
                f.write("%d %d\n" % (port, srv.pid))
            return "сервер поднят: http://localhost:%d/dashboard.html" % port
        try:
            srv.wait(timeout=0.5)
            break
        except subprocess.TimeoutExpired:
            continue
    srv.terminate()
    return "сервер не ответил — дашборд открывается файлом: %s" % PAGE


def stop_now(expected_pid, expected_port):
    time.sleep(STOP_DELAY)
    port, pid = recorded()
    state = read_state()
    if (state and state.get("finishedAt") and pid == expected_pid
            and port == expected_port and is_ours(cmdline(pid))):
        kill(pid)
        for f in (PIDF, LOG):
            try:
                os.remove(f)
            except OSError:
                pass


def stop_later():
    """Гасит сервер через STOP_DELAY секунд из отдельного процесса: страница
    опрашивает state.js раз в 10 секунд и должна успеть забрать финал."""
    port, pid = recorded()
    if not port or not pid:
        return "сервер уже остановлен"
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--stop-now", str(pid), str(port)],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, **_detached())
    return "сервер погаснет через %d с" % STOP_DELAY


# ── версия навыка ───────────────────────────────────────────────────────────

_VER = re.compile(r"^\s*version:\s*[\"']?(\d+(?:\.\d+)*)", re.M)


def _version(text):
    m = _VER.search(text.split("\n---", 1)[0] if text.startswith("---") else "")
    return tuple(int(x) for x in m.group(1).split(".")) if m else None


def check_update(state):
    """Строка, если на GitHub навык новее. Без сети — молчит.
    AUTOPILOT_NO_UPDATE_CHECK=1 выключает."""
    if os.environ.get("AUTOPILOT_NO_UPDATE_CHECK"):
        return None
    skill = state.get("skillDir") or ""
    try:
        local = _version(open(os.path.join(skill, "SKILL.md"), encoding="utf-8").read())
    except OSError:
        return None
    try:
        with urllib.request.urlopen(REMOTE_SKILL, timeout=3) as r:
            remote = _version(r.read(65536).decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError):
        return None
    if not remote or (local and remote <= local):
        return None
    home = _norm(os.path.expanduser("~"))
    flag = " -g" if _norm(skill).startswith(home + "/.") else ""
    v = lambda t: ".".join(map(str, t))
    return ("вышла версия Autopilot %s (у тебя %s): npx skills update autopilot%s · "
            "что нового — github.com/%s/blob/main/CHANGELOG.md"
            % (v(remote), v(local) if local else "без номера", flag, REPO))


# ── реестр прогонов (.autopilot/README.md) ──────────────────────────────────

README_TEXT = """# Как читать эту папку

- `dashboard.html` — открывается сам в начале сборки; можно и двойным кликом.
  Этапы, прогресс, время, что осталось. Обновляется сам, пока сборка идёт.
  `index.html` рядом — тот же файл под другим именем, открывать его не нужно.
- `<дата>-<проект>/` — папка одной сборки. Дата — день, когда сборка началась.
  Суффикс `--wip` значит «ещё делается»; когда сборка сдана, он снимается. Внутри:
  - `<дата>-brief.md` — твоя задача слово в слово и «Дополнения» — всё, что ты сказал позже.
  - `manifest.md` — список требований и что с каждым стало.
  - `spec.md` — спецификация. `tickets/` — таски, на которые разбита сборка.
- `PROGRESS.md` — что осталось после последней сборки: не доделано, известные баги,
  о чём договорились. Мелкие правки без автопилота дописываются сюда же.

Если сборка прервалась — скажи агенту «продолжи автопилот», он поднимет состояние отсюда.

## Прогоны

| Начат | Папка | Статус | Итог |
|---|---|---|---|
"""


def register_row(state, status, result):
    d = state.get("dir") or ""
    base = re.sub(r"--wip$", "", d)
    try:
        text = open(README, encoding="utf-8").read()
    except OSError:
        text = README_TEXT
    if "## Прогоны" not in text:
        text = text.rstrip("\n") + "\n\n## Прогоны\n\n| Начат | Папка | Статус | Итог |\n|---|---|---|---|\n"
    row = "| %s | `%s` | %s | %s |" % (d[:10], d, status, result or "—")
    lines = text.splitlines()
    hit = [i for i, l in enumerate(lines) if l.startswith("|") and ("`%s`" % base in l or "`%s--wip`" % base in l)]
    if hit:
        lines[hit[-1]] = row
    else:
        lines.append(row)
    with open(README, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def git_mv(src, dst):
    if subprocess.run(["git", "-C", A, "mv", src, dst], capture_output=True).returncode == 0:
        return True
    try:
        os.rename(os.path.join(A, src), os.path.join(A, dst))
        return True
    except OSError:
        return False


def ensure_gitignore():
    g = os.path.join(ROOT, ".gitignore")
    try:
        text = open(g, encoding="utf-8").read()
    except OSError:
        text = ""
    entries = [".autopilot/serve.*", ".autopilot/state.lock",
               ".autopilot/dispatch-*.lock", ".autopilot/controller.lock",
               ".autopilot/gui-dispatch/",
               ".autopilot/api-pilot/", ".autopilot/api-pilot-consent",
               ".autopilot/offline-worker/", ".autopilot/offline-test-consent",
               ".autopilot/__pycache__/",
               ".autopilot/worktrees/", ".autopilot/model-capabilities.json",
               ".claude/agents/autopilot-*.md", ".codex/agents/autopilot-*.toml"]
    existing = {line.strip() for line in text.splitlines()}
    missing = [entry for entry in entries if entry not in existing]
    if not missing:
        return
    with open(g, "a", encoding="utf-8") as f:
        f.write(("" if not text or text.endswith("\n") else "\n")
                + "\n".join(missing) + "\n")

# ── команды ─────────────────────────────────────────────────────────────────

def parse_args(argv):
    pos, opt, multi = [], {}, {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            key = a[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                opt[key] = argv[i + 1]
                multi.setdefault(key, []).append(argv[i + 1])
                i += 2
                continue
            opt[key] = True
        else:
            pos.append(a)
        i += 1
    return pos, opt, multi


def tests_pair(v):
    m = re.match(r"^\s*(\d+)\s*(?:/\s*(\d+))?\s*$", str(v))
    if not m:
        die("тесты пишутся как ПРОШЛО/УПАЛО, например 34/0")
    return {"passed": int(m.group(1)), "failed": int(m.group(2) or 0)}


def cmd_init(opt):
    if not opt.get("slug"):
        die("init требует --slug")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(opt["slug"])):
        die("slug: разрешены только a-z, 0-9 и одиночные дефисы")
    old = read_state()
    notes = []
    if old and not old.get("finishedAt") and not opt.get("force"):
        die("идёт прогон %s — это продолжение, а не новый прогон (или --force)" % old.get("dir"))
    if old and old.get("dir") and os.path.isdir(os.path.join(A, old["dir"])):
        dst = os.path.join(old["dir"], "state.js")
        if subprocess.run(["git", "-C", A, "mv", "-f", "state.js", dst], capture_output=True).returncode:
            os.replace(STATE, os.path.join(A, dst))
        notes.append("прошлый прогон убран в архив: %s" % dst)
    state = fresh_state(opt)
    log(state, "init")
    os.makedirs(os.path.join(run_dir(state), "tickets"), exist_ok=True)
    save(state)
    ensure_gitignore()
    register_row(state, "в работе", None)
    notes.append("папка прогона: .autopilot/%s" % state["dir"])
    return state, notes


def cmd_stage(state, pos, opt):
    if not pos:
        die("stage <id> [done|skip|fail] [--note …]")
    sid, action = pos[0], (pos[1] if len(pos) > 1 else "start")
    if sid not in ORDER:
        die("этапы: " + ", ".join(ORDER))
    s = stage(state, sid)
    t = now()
    if action == "start":
        s["status"] = "active"
        s.setdefault("startedAt", t)
        s.pop("finishedAt", None)
    elif action == "done":
        s["status"] = "done"
        s.setdefault("startedAt", t)
        s["finishedAt"] = t
    elif action in ("skip", "fail"):
        if not opt.get("note"):
            die("%s требует --note с причиной" % action)
        s["status"] = "skipped" if action == "skip" else "failed"
        s.setdefault("startedAt", t)
        s["finishedAt"] = t
    else:
        die("действие этапа: start | done | skip | fail")
    if isinstance(opt.get("note"), str):
        s["note"] = opt["note"]
    if sid == "spec" and action in ("start", "done"):
        rows = [r for r in manifest_table(state) or [] if not r["id"].startswith("D")]
        if rows:
            n = sum(1 for r in rows if r["status"] == "open")
            set_gate(state, "G1", n == 0, open=n, total=len(rows))
    log(state, "stage", id=sid, act=action,
        note=opt["note"] if action in ("skip", "fail") and isinstance(opt.get("note"), str) else None)


def close_requirements(state, tk, opt, t):
    """Требование закрыто, когда закрыты все таски, где оно названо. --placeholder R05
    помечает его заглушкой вместо done: там стоит видимая метка вместо данных пользователя."""
    ph = set(re.findall(r"[RGD]\d+[a-z]?", str(opt.get("placeholder") or "")))
    ph |= set(tk.get("placeholders") or [])
    tk["placeholders"] = sorted(ph)
    rows = dict(manifest_rows(state) or [])
    tickets = state.get("tickets") or []
    changes = {}
    for r in {x.split(".")[0] for x in tk.get("requirements", [])}:
        if rows.get(r) not in ("in-ticket", "in-spec", "open"):
            continue
        holders = [x for x in tickets if r in {y.split(".")[0] for y in x.get("requirements", [])}]
        if all(x is tk or x.get("status") == "done" for x in holders):
            changes[r] = ("placeholder" if r in ph else "done",
                          (opt.get("commit")[:7] if isinstance(opt.get("commit"), str) else None))
    manifest_update(state, changes)


def reconcile_requirements(state):
    """Требование не может быть done, когда хотя бы один его таск снова открыт."""
    rows = dict(manifest_rows(state) or [])
    groups = {}
    for ticket in state.get("tickets") or []:
        for req in ticket.get("requirements", []):
            groups.setdefault(req.split(".")[0], []).append(ticket)
    changes = {}
    for req, holders in groups.items():
        if rows.get(req) in ("done", "placeholder") and any(
                t.get("status") != "done" for t in holders):
            changes[req] = ("in-ticket", "")
    if changes:
        manifest_update(state, changes)


def verified_commit(rev):
    if not isinstance(rev, str) or not re.fullmatch(r"[0-9a-fA-F]{7,40}", rev):
        return False
    try:
        result = subprocess.run(
            ["git", "-C", ROOT, "merge-base", "--is-ancestor", rev, "HEAD"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def profile_ok(tk):
    """Refuse stale/edited native agent definitions before strict dispatch."""
    route = tk.get("routing") or {}
    if not route.get("verified") or not route.get("agentFile") or not route.get("profileSha"):
        return False
    relative = route["agentFile"]
    if not isinstance(relative, str) or os.path.isabs(relative):
        return False
    expected_prefix = (".claude/agents/" if route.get("provider") == "anthropic"
                       else ".codex/agents/")
    if not relative.replace("\\", "/").startswith(expected_prefix):
        return False
    path = os.path.realpath(os.path.join(ROOT, relative))
    root = os.path.realpath(ROOT)
    try:
        if os.path.commonpath((path, root)) != root:
            return False
        policy_file = route.get("policyFile")
        if policy_file is not None:
            if (not isinstance(policy_file, str) or
                    not isinstance(route.get("policySha"), str) or
                    os.path.isabs(policy_file)):
                return False
            policy_path = os.path.realpath(os.path.join(ROOT, policy_file))
            if os.path.commonpath((policy_path, root)) != root:
                return False
            with open(policy_path, "rb") as policy_stream:
                if hashlib.sha256(policy_stream.read()).hexdigest() != route["policySha"]:
                    return False
        with open(path, "rb") as stream:
            return hashlib.sha256(stream.read()).hexdigest() == route["profileSha"]
    except (OSError, ValueError):
        return False


def cmd_ticket(state, pos, opt):
    acts = [p for p in pos if p in TICKET_STATUSES]
    ids = [p for p in pos if p not in TICKET_STATUSES]
    if len(acts) != 1 or not ids:
        die("ticket <id…> start|review|repair|done|fail|retry|reset")
    act = acts[0]
    known = {t["id"]: t for t in state.get("tickets") or []}
    t = now()
    for i in ids:
        tk = known.get(i)
        if tk is None:
            die("таска %s нет — сначала `ap.py tickets`" % i)
        if act == "start" and tk.get("status") != "pending":
            die("таск %s: start разрешён только из pending (уже запущен или завершён)" % i)
        if act == "start" and (state.get("isolateTickets") or tk.get("worktree")):
            wt = tk.get("worktree") or {}
            if wt.get("status") != "prepared":
                die("таск %s: подготовь worktree командой worktree %s prepare" % (i, i))
            try:
                import worktrees
                actual = worktrees.status(ROOT, i)
                if (actual.get("status") != "present" or actual.get("dirty") or
                        actual.get("commit") != wt.get("baseCommit")):
                    die("таск %s: worktree изменён до старта или отсутствует" % i)
            except (OSError, ValueError, ImportError, worktrees.WorktreeError) as exc:
                die("таск %s: не удалось проверить worktree: %s" % (i, exc))
        if act == "reset" and tk.get("worktree"):
            if tk["worktree"].get("status") != "released":
                die("таск %s: сначала закончи и освободи worktree; сброс не удаляет изменения" % i)
            tk.pop("worktree", None)
        if act == "done" and state.get("isolateTickets") and not tk.get("worktree"):
            die("таск %s: изолированный режим требует интеграции worktree" % i)
        if act == "done" and tk.get("worktree"):
            wt = tk["worktree"]
            if wt.get("status") != "landed" or not wt.get("landedCommit"):
                die("таск %s: сначала интегрируй worktree командой worktree %s land" % (i, i))
            candidate = opt.get("commit") or tk.get("commit")
            if not isinstance(candidate, str) or not re.fullmatch(r"[0-9a-fA-F]{7,40}", candidate):
                die("таск %s: укажи интегрированный коммит" % i)
            if not wt["landedCommit"].lower().startswith(candidate.lower()):
                die("таск %s: коммит не совпадает с интегрированным worktree" % i)
        if act == "start" and state.get("budgetTokens") is not None:
            consumed = sum(x["input"] + x["output"]
                           for x in state.get("usageEvents") or [])
            if consumed >= state["budgetTokens"]:
                die("таск %s: лимит известных токенов достигнут (%d/%d)" %
                    (i, consumed, state["budgetTokens"]))
        if act in ("start", "done"):
            pending = [dep for dep in tk.get("blockedBy", [])
                       if known.get(dep, {}).get("status") != "done"]
            if pending:
                die("таск %s: сначала заверши зависимости %s" % (i, ", ".join(pending)))
        if act in ("start", "done", "retry") and state.get("strictRouting") and not profile_ok(tk):
            die("таск %s: строгая маршрутизация требует подтверждённой модели" % i)
        if act == "done" and state.get("strictRouting") and state.get("isolateTickets"):
            recorded = tk.get("tests")
            evidence = tk.get("testEvidence")
            if (not isinstance(evidence, dict) or evidence.get("status") != "verified"
                    or recorded != {"passed": evidence.get("passed"), "failed": 0}):
                die("таск %s: строгий режим требует результатов тестов, проверенных на хосте" % i)
            if opt.get("tests") and tests_pair(opt["tests"]) != recorded:
                die("таск %s: переданные тесты не совпадают с проверенными" % i)
        if act == "done":
            validation = tests_pair(opt["tests"]) if opt.get("tests") else tk.get("tests")
            if not validation or validation["passed"] < 1 or validation["failed"] != 0:
                die("таск %s: нельзя принять без успешных тестов" % i)
            rev = opt.get("commit") or tk.get("commit")
            if not verified_commit(rev):
                die("таск %s: требуется существующий коммит в HEAD" % i)
        if act == "retry" and state.get("isolateTickets") and not tk.get("worktree"):
            die("таск %s: сначала подготовь worktree для повтора" % i)
        if act in ("retry", "repair"):
            attempts = tk.get("retries", 0)
            repairs = tk.get("repairs", 0)
            if (act == "retry" and attempts >= 2) or (act == "repair" and repairs >= 2):
                die("таск %s: предел повторов/ремонтов достигнут; нужна диагностика" % i)
            if act == "retry":
                kind = opt.get("cause") or "unknown"
                if state.get("strictRouting") and not opt.get("cause"):
                    die("таск %s: --cause обязателен для безопасного повтора" % i)
                try:
                    from retry_policy import decide
                    advice = decide(kind, attempts, repairs)
                except (ValueError, ImportError) as exc:
                    die("retry: %s" % exc)
                if advice["action"] not in ("repair", "investigate"):
                    die("таск %s: повтор не разрешён (%s): %s" %
                        (i, advice["action"], advice["why"]))
                if tk.get("worktree"):
                    import worktrees
                    actual = worktrees.status(ROOT, i)
                    if actual.get("status") != "present" or tk["worktree"].get("status") != "prepared":
                        die("таск %s: рабочая копия не готова к повтору" % i)
                tk["retryAdvice"] = advice
        if act == "route":
            provider = opt.get("provider")
            model = opt.get("model")
            effort = opt.get("effort")
            reason = opt.get("reason")
            cap = opt.get("capabilities") or os.path.join(A, "model-capabilities.json")
            policy_arg = opt.get("policy")
            policy_path = None
            policy_relative = None
            policy_digest = None
            if policy_arg is not None:
                if not isinstance(policy_arg, str) or not policy_arg.strip():
                    die("route: --policy требует файл JSON внутри проекта")
                policy_path = os.path.realpath(os.path.join(ROOT, policy_arg))
                root_path = os.path.realpath(ROOT)
                try:
                    if os.path.commonpath((policy_path, root_path)) != root_path:
                        die("route: policy должна находиться внутри проекта")
                except ValueError:
                    die("route: недопустимый путь policy")
                if not os.path.isfile(policy_path):
                    die("route: policy файл отсутствует")
                policy_relative = os.path.relpath(policy_path, root_path).replace("\\", "/")
                with open(policy_path, "rb") as policy_stream:
                    policy_digest = hashlib.sha256(policy_stream.read()).hexdigest()
            if provider not in ("openai", "anthropic") or not all(
                    isinstance(x, str) and x.strip() for x in (model, effort, reason)):
                die("route требует --provider --model --effort --reason")
            module_path = os.path.join(A, "model_router.py")
            if not os.path.isfile(module_path) or not os.path.isfile(cap):
                die("route: требуется model_router.py и проверенный файл возможностей harness")
            try:
                spec = importlib.util.spec_from_file_location("model_router", module_path)
                router = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(router)
                candidates = glob.glob(os.path.join(run_dir(state), "tickets", "%s-*.md" % i))
                if len(candidates) != 1:
                    die("route: не удалось однозначно найти файл таска %s" % i)
                source = open(candidates[0], encoding="utf-8").read()
                scores = json.loads(opt["scores"]) if opt.get("scores") else router.assess_ticket(source)
                route = router.choose_route(
                    provider, scores, policy=router.load_policy(policy_path),
                    capabilities=router.load_json(cap))
            except (ValueError, OSError, TypeError) as err:
                die("route: %s" % err)
            if (route["status"] != "ready" or route["model"] != model
                    or route["effort"] != effort):
                die("route: заданная модель или effort не одобрены: %s" % route.get("error", "несовпадение"))
            try:
                import agent_profiles
                profile = agent_profiles.prepare(
                    ROOT, candidates[0], provider, cap, "executor",
                    policy=policy_path, scores=scores, install=True)
                if profile["model"] != model or profile["effort"] != effort:
                    die("route: профиль агента не совпадает с одобренной моделью")
                filename = profile["agent_file"]
                with open(os.path.join(ROOT, filename), "rb") as stream:
                    digest = hashlib.sha256(stream.read()).hexdigest()
            except (ValueError, OSError, ImportError, TypeError) as err:
                die("route: не удалось создать нативный профиль субагента: %s" % err)
            tk["routing"] = {"provider": provider, "model": model,
                             "effort": effort, "score": route["score"],
                             "reason": reason, "verified": True,
                             "agentType": profile["agent_type"],
                             "agentFile": filename, "profileSha": digest}
            if policy_relative is not None:
                tk["routing"].update(policyFile=policy_relative,
                                     policySha=policy_digest)
            continue
        tk["status"] = TICKET_STATUSES[act]
        if act == "start":
            tk.setdefault("startedAt", t)
            tk.pop("finishedAt", None)
        elif act == "retry":
            tk["retries"] = tk.get("retries", 0) + 1
            tk["startedAt"] = tk.get("startedAt") or t
        elif act == "repair":
            tk["repairs"] = tk.get("repairs", 0) + 1
            if isinstance(opt.get("note"), str):
                tk.setdefault("repairFindings", []).append(opt["note"])
        elif act in ("done", "fail"):
            tk.setdefault("startedAt", t)
            tk["finishedAt"] = t
            if act == "fail" and isinstance(opt.get("note"), str):
                tk.setdefault("concerns", []).append(opt["note"])
        elif act == "reset":
            for k in ("startedAt", "finishedAt"):
                tk.pop(k, None)
        if act == "done":
            close_requirements(state, tk, opt, t)
        if opt.get("tests"):
            tk["tests"] = tests_pair(opt["tests"])
            state["tests"] = tk["tests"]
        if isinstance(opt.get("commit"), str):
            tk["commit"] = opt["commit"][:12]
    log(state, "ticket", ids=ids, act=act, tests=tests_pair(opt["tests"]) if opt.get("tests") else None,
        note=opt["note"] if act in ("repair", "fail") and isinstance(opt.get("note"), str) else None)


def cmd_worktree(state, pos, opt):
    """Plan-aware, explicit isolation lifecycle; no automatic agent spawning."""
    if len(pos) != 2 or pos[1] not in ("prepare", "status", "verify", "finalize", "land", "release", "recover"):
        die("worktree <ticket-id> prepare|status|verify|finalize|land|release|recover [--tests N/0]")
    ident, action = pos
    known = {t["id"]: t for t in state.get("tickets") or []}
    tk = known.get(ident)
    if not tk:
        die("worktree: неизвестный таск " + ident)
    try:
        import worktrees
        if action == "status":
            info = worktrees.status(ROOT, ident)
            return "worktree %s: %s%s" % (ident, info.get("status"),
                    " · dirty" if info.get("dirty") else "")
        if action == "recover":
            record = tk.get("worktree") or {}
            actual = worktrees.status(ROOT, ident)
            if not record:
                # Crash after git worktree add but before ap.py persisted state.
                if (tk.get("status") != "pending" or actual.get("status") != "present"
                        or actual.get("dirty")):
                    die("worktree: нельзя безопасно восстановить неподтверждённую подготовку")
                head = worktrees.git(ROOT, "rev-parse", "HEAD").stdout.strip()
                if actual.get("commit") != head:
                    die("worktree: базовый коммит расходится; ручная проверка обязательна")
                tk["worktree"] = {"status": "prepared", "baseCommit": head,
                                  "cwd": actual["cwd"]}
                log(state, "worktree", act="recover-prepare", ticket=ident)
                return "worktree %s: восстановлено состояние prepared" % ident
            if record.get("status") == "landed":
                if not verified_commit(record.get("landedCommit")):
                    die("worktree: сохранённый коммит недоступен в текущей истории")
                if actual.get("status") == "missing" and tk.get("status") == "done":
                    # Crash after Git worktree remove but before the state write.
                    record["status"] = "released"
                    log(state, "worktree", act="recover-release", ticket=ident)
                    return "worktree %s: восстановлено состояние released" % ident
                return "worktree %s: интеграция уже зарегистрирована"
            if record.get("status") == "released":
                return "worktree %s: уже освобождён" % ident
            if record.get("status") != "prepared":
                die("worktree: неизвестный этап восстановления")
            if actual.get("status") != "present":
                die("worktree: рабочая копия пропала; проверить вручную")
            if actual.get("dirty"):
                die("worktree: незакоммиченные изменения; восстановление не изменяет их")
            if actual.get("commit") == record.get("baseCommit"):
                return "worktree %s: подготовлен, исполнитель ещё не создал коммит" % ident
            recovered = worktrees.recover(ROOT, ident, record["baseCommit"])
            if recovered["status"] == "not-landed":
                return "worktree %s: коммит исполнителя есть, ещё не интегрирован" % ident
            if state.get("strictRouting") and state.get("isolateTickets"):
                import test_evidence
                evidence = tk.get("testEvidence")
                if record.get("sourceCommit") == recovered["sourceCommit"]:
                    if not evidence or evidence.get("status") != "verified":
                        die("worktree: отсутствует подтверждение тестов после финализации")
                    check = {"passed": evidence["passed"], "failed": evidence["failed"]}
                else:
                    check = test_evidence.check(ROOT, ident, record["baseCommit"], evidence)
                if opt.get("tests") and tests_pair(opt["tests"]) != check:
                    die("worktree: числа тестов не совпадают с результатом хоста")
            else:
                check = tests_pair(opt.get("tests") or "")
            if check["passed"] < 1 or check["failed"] != 0:
                die("worktree: подтверждение интеграции требует пройденных тестов N/0")
            record.update(status="landed", sourceCommit=recovered["sourceCommit"],
                          landedCommit=recovered["landedCommit"])
            tk["commit"] = recovered["landedCommit"][:12]
            tk["tests"] = check
            state["tests"] = check
            log(state, "worktree", act="recover-land", ticket=ident)
            return "worktree %s: восстановлена уже выполненная интеграция" % ident
        if action == "release":
            record = tk.get("worktree") or {}
            if record.get("status") == "released":
                return "worktree %s: уже освобождён" % ident
            if (record.get("status") != "landed" or tk.get("status") != "done"
                    or not verified_commit(record.get("landedCommit"))):
                die("worktree: освобождение требует принятого таска и интегрированного коммита")
            result = worktrees.remove(ROOT, ident, acknowledge_loss=True)
            record["status"] = "released"
            log(state, "worktree", act="release", ticket=ident)
            return "worktree %s освобождён" % ident
        if action == "prepare":
            if tk.get("status") != "pending":
                die("worktree: сначала переведи таск %s в pending" % ident)
            if any(known.get(dep, {}).get("status") != "done" for dep in tk.get("blockedBy", [])):
                die("worktree: зависимости таска %s не закрыты" % ident)
            if state.get("strictRouting") and not profile_ok(tk):
                die("worktree: сначала подтверди модель таска %s" % ident)
            if tk.get("worktree"):
                die("worktree: для %s уже существует запись, проверь status" % ident)
            result = worktrees.create(ROOT, ident)
            tk["worktree"] = {"status": "prepared", "baseCommit": result["baseCommit"],
                              "cwd": result["cwd"]}
            log(state, "worktree", act="prepare", ticket=ident)
            return "worktree %s подготовлен: %s" % (ident, result["cwd"])
        if action == "verify":
            record = tk.get("worktree") or {}
            if (record.get("status") != "prepared" or
                    tk.get("status") not in ("in-progress", "review", "repair")):
                die("worktree: тесты требуют работающую задачу и prepared checkout")
            suite = opt.get("suite")
            timeout = opt.get("timeout") or "90"
            if not isinstance(timeout, str) or not re.fullmatch(r"\d{1,3}", timeout):
                die("worktree: --timeout должен быть целым числом секунд")
            import test_evidence
            result = test_evidence.verify(ROOT, ident, record["baseCommit"], suite,
                                          int(timeout))
            tk["testEvidence"] = result
            check = {"passed": result["passed"], "failed": 0}
            tk["tests"] = check
            state["tests"] = check
            log(state, "worktree", act="verify", ticket=ident,
                tests=result["passed"], suite=result["suite"])
            return "worktree %s: %d/%d тестов подтверждено на хосте" % (
                ident, result["passed"], result["failed"])
        if action == "finalize":
            record = tk.get("worktree") or {}
            if (record.get("status") != "prepared" or
                    tk.get("status") not in ("in-progress", "review", "repair")):
                die("worktree: для финализации требуется запущенная задача и prepared checkout")
            if state.get("strictRouting") and state.get("isolateTickets"):
                import test_evidence
                check = test_evidence.check(ROOT, ident, record["baseCommit"],
                                            tk.get("testEvidence"))
                if opt.get("tests") and tests_pair(opt["tests"]) != check:
                    die("worktree: указанные тесты не совпадают с проверенными на хосте")
            else:
                check = tests_pair(opt.get("tests") or "")
            if check["passed"] < 1 or check["failed"] != 0:
                die("worktree: сначала независимо проверь тесты N/0")
            result = worktrees.finalize(ROOT, ident, record["baseCommit"],
                                        tk.get("zone") or [], check["passed"], check["failed"])
            record["sourceCommit"] = result["sourceCommit"]
            tk["tests"] = check
            state["tests"] = check
            log(state, "worktree", act="finalize", ticket=ident)
            return "worktree %s: подготовлен проверенный коммит %s" % (
                ident, result["sourceCommit"][:12])
        record = tk.get("worktree") or {}
        if record.get("status") != "prepared" or tk.get("status") not in ("in-progress", "review", "repair"):
            die("worktree: %s не запущен в подготовленной рабочей копии" % ident)
        if state.get("strictRouting") and state.get("isolateTickets"):
            import test_evidence
            evidence = tk.get("testEvidence")
            if record.get("sourceCommit"):
                # Host finalize consumed and committed the exact verified edit.
                if not evidence or evidence.get("status") != "verified":
                    die("worktree: нет подтверждения тестов на хосте")
                if worktrees.source_commit(ROOT, ident, record["baseCommit"]) != record["sourceCommit"]:
                    die("worktree: коммит изменился после финализации")
                check = {"passed": evidence["passed"], "failed": evidence["failed"]}
            else:
                check = test_evidence.check(ROOT, ident, record["baseCommit"], evidence)
            if opt.get("tests") and tests_pair(opt["tests"]) != check:
                die("worktree: указанные тесты не совпадают с проверенными на хосте")
        else:
            check = tests_pair(opt.get("tests") or "")
        if check["passed"] < 1 or check["failed"] != 0:
            die("worktree: для интеграции нужны пройденные тесты N/0")
        result = worktrees.land(ROOT, ident, record["baseCommit"])
        record.update(status="landed", sourceCommit=result["sourceCommit"],
                      landedCommit=result["landedCommit"])
        tk["commit"] = result["landedCommit"][:12]
        tk["tests"] = check
        state["tests"] = check
        log(state, "worktree", act="land", ticket=ident)
        return "worktree %s интегрирован: %s" % (ident, tk["commit"])
    except (worktrees.WorktreeError, OSError, ImportError, ValueError) as exc:
        die("worktree %s: %s" % (ident, exc))


def positive_int_option(opt, name, default=None):
    v = opt.get(name, default)
    if isinstance(v, int):
        value = v
    elif isinstance(v, str) and re.fullmatch(r"\d{1,15}", v):
        value = int(v)
    else:
        die("usage: --%s должен быть целым неотрицательным числом" % name)
    if value < 0 or value > 10**12:
        die("usage: --%s вне допустимого диапазона" % name)
    return value


def cmd_usage(state, pos, opt):
    """Append an attributed, de-duplicated token report; never invent pricing."""
    if len(pos) != 1 or pos[0] not in {t["id"] for t in state.get("tickets") or []}:
        die("usage <known-ticket-id> --call-id ID --input N --output N --source SOURCE")
    call_id = opt.get("call-id")
    source = opt.get("source")
    if (not isinstance(call_id, str) or not re.fullmatch(r"[a-zA-Z0-9._:-]{4,128}", call_id)
            or source not in ("claude-jsonl", "codex-jsonl", "responses-api", "host-reported", "manual")):
        die("usage требует допустимые --call-id и --source")
    counts = {k: positive_int_option(opt, k, "0") for k in
              ("input", "output", "cache-read", "cache-write")}
    if not counts["input"] and not counts["output"] and not counts["cache-read"] and not counts["cache-write"]:
        die("usage: нельзя записать все нулевые счётчики")
    events = state.setdefault("usageEvents", [])
    existing = next((e for e in events if e["callId"] == call_id), None)
    event = {"callId": call_id, "ticket": pos[0], "source": source,
             "input": counts["input"], "output": counts["output"],
             "cacheRead": counts["cache-read"], "cacheWrite": counts["cache-write"]}
    if existing:
        match = {k: existing.get(k) for k in event} == event
        if not match:
            die("usage: call-id уже существует с другими параметрами")
        return
    if len(events) >= 2000:
        die("usage: журнал достиг лимита 2000 событий; нужен экспорт/архивирование")
    event["at"] = state["updatedAt"]
    events.append(event)
    log(state, "usage", ticket=pos[0])


def cmd_budget(state, pos, opt):
    if not opt.get("tokens") or pos:
        die("budget --tokens N")
    limit = positive_int_option(opt, "tokens")
    if not limit:
        die("budget: лимит должен быть больше нуля")
    state["budgetTokens"] = limit
    log(state, "budget", tokens=limit)


def cmd_set(state, pos):
    for p in pos:
        k, _, v = p.partition("=")
        allowed = {"tier", "baseCommit", "briefFile", "memoryFile",
                   "memoryOwner", "skillDir", "mode", "depth"}
        if not _ or k not in allowed:
            die("set: разрешены только " + ", ".join(sorted(allowed)))
        state[k] = None if v in ("", "null") else v


def cmd_add(state, pos):
    if len(pos) < 2 or pos[0] not in LISTS:
        die("add <%s> \"текст\"" % "|".join(sorted(LISTS)))
    key, vals = pos[0], pos[1:]
    if key.startswith("debt."):
        tgt = state.setdefault("debt", {}).setdefault(key[5:], [])
    else:
        tgt = state.setdefault(key, [])
    fresh = [v for v in vals if v not in tgt]
    tgt.extend(dict.fromkeys(fresh))
    if fresh:
        log(state, "add", key=key, n=len(fresh))


def cmd_numbers(state, name, pos, multi):
    d = {}
    for p in pos:
        k, _, v = p.partition("=")
        d[k] = int(v) if v.isdigit() else v
    if name == "blind":
        d["mismatches"] = multi.get("mismatch", [])
        state[name] = d
        valid = (isinstance(d.get("checked"), int) and d["checked"] > 0
                 and isinstance(d.get("matched"), int)
                 and 0 <= d["matched"] <= d["checked"]
                 and d["checked"] - d["matched"] == len(d["mismatches"]))
        set_gate(state, "G4", valid and not d["mismatches"],
                 checked=d.get("checked"), matched=d.get("matched"))
    else:
        d["items"] = multi.get("item", [])
        state[name] = d
        num = lambda k: d.get(k) if isinstance(d.get(k), int) else 0
        set_gate(state, "G2", all(isinstance(d.get(k), int) and d[k] >= 0
                                  for k in ("found", "fixed", "deferred"))
                 and num("found") == num("fixed") + num("deferred"),
                 found=num("found"), fixed=num("fixed"), deferred=num("deferred"))


def cmd_ask(state, pos, opt):
    """Сборка ждёт пользователя: раунд брифинга, ручной гейт, вопрос перед необратимым."""
    kind = pos[0] if pos else ""
    if kind not in WAIT_KINDS:
        die("ask <%s> --note \"что ждём, одной строкой\"" % "|".join(WAIT_KINDS))
    w = state.get("waiting")
    if w and w.get("kind") != kind:
        close_wait(state)
        w = None
    note = opt.get("note") if isinstance(opt.get("note"), str) else None
    state["waiting"] = {"kind": kind, "since": w["since"] if w else state["updatedAt"], "note": note}
    log(state, "ask", kind=kind, note=note)


def cmd_finish(state, opt):
    # The run may have been reset/rebased after its tickets were accepted.
    # Reject stale Git ancestry *at the final gate*, not just at ticket done;
    # 'commits' remains a separate read-only diagnostic for manual recovery.
    stale = [tk.get("id", "?") for tk in state.get("tickets") or []
             if tk.get("status") == "done"
             and not verified_commit(tk.get("commit"))]
    if stale:
        die("finish заблокирован: коммиты сданных тасков отсутствуют в HEAD: %s"
            % ", ".join(stale))
    t = now()
    notes = []
    for s in state.get("stages") or []:
        if s.get("status") in ("active", "pending") and s.get("id") == "final":
            s["status"], s["finishedAt"] = "done", t
            s.setdefault("startedAt", t)
        elif s.get("status") == "active":
            s["status"], s["finishedAt"] = "done", t
        elif s.get("status") == "pending":
            s["status"], s["note"], s["finishedAt"] = "skipped", s.get("note") or "не понадобился", t
    incomplete = [tk["id"] for tk in state.get("tickets") or []
                  if tk.get("status") != "done"]
    if incomplete or not state.get("tickets"):
        die("finish заблокирован: незавершённые таски: %s" %
            (", ".join(incomplete) if incomplete else "нет опубликованных тасков"))
    test = state.get("tests") or {}
    if test.get("passed", 0) < 1 or test.get("failed") != 0:
        die("finish заблокирован: нет успешного полного прогона тестов")
    missing = [g for g in ("G1", "G2", "G3", "G4")
               if not state.get("gates", {}).get(g, {}).get("ok")]
    if missing:
        die("finish заблокирован: проверки %s не пройдены" % ", ".join(missing))
    open_rows = [rid for rid, st in manifest_rows(state) or []
                 if not rid.startswith("D") and st in ("open", "in-spec", "in-ticket")]
    if open_rows:
        die("finish заблокирован: требования не закрыты: %s" % ", ".join(open_rows))
    d = state.get("dir") or ""
    if d.endswith("--wip"):
        new = d[: -len("--wip")]
        if os.path.exists(os.path.join(A, new)):
            notes.append("! папка %s уже есть — оставляю %s" % (new, d))
        elif git_mv(d, new):
            state["dir"] = new
            notes.append("папка прогона: .autopilot/%s" % new)
        else:
            notes.append("! не смог переименовать %s — оставляю как есть" % d)
    state["finishedAt"] = t
    state["result"] = opt.get("result") if isinstance(opt.get("result"), str) else None
    register_row(state, "сдан", state["result"])
    log(state, "finish", result=state["result"])
    return notes


def cmd_reopen(state):
    """Второй бриф в сданном прогоне: фазы 1–8 идут заново, прежние таски остаются."""
    if any(t.get("worktree") and t["worktree"].get("status") != "released"
           for t in state.get("tickets") or []):
        die("reopen заблокирован: незавершённые или неосвобождённые worktrees")
    d = state.get("dir") or ""
    if not d.endswith("--wip") and git_mv(d, d + "--wip"):
        state["dir"] = d + "--wip"
    state["finishedAt"] = None
    state["blind"] = None
    for s in state.get("stages") or []:
        if s.get("id") != "preflight":
            for k in ("startedAt", "finishedAt", "note"):
                s.pop(k, None)
            s["status"] = "pending"
    stage(state, "manifest").update(status="active", startedAt=now())
    state["result"] = None
    state["gates"] = {}
    register_row(state, "в работе", None)
    log(state, "reopen")


def cmd_commits(state):
    """Возобновление верит state.js, а история могла уйти из-под него: reset, rebase,
    другая ветка. Сданный таск, чьего коммита нет в HEAD, — строка «!»; сбрасывает
    его оркестратор, потому что код после rebase может лежать на месте под другим sha."""
    notes = []
    for tk in state.get("tickets") or []:
        c = tk.get("commit")
        if tk.get("status") != "done" or not c:
            continue
        r = subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", c, "HEAD"],
                           capture_output=True)
        if r.returncode:
            notes.append("! таск %s: коммита %s нет в истории — `ap.py ticket %s reset`"
                         % (tk["id"], c, tk["id"]))
    return notes or ["коммиты сданных тасков на месте"]


def main():
    argv = sys.argv[1:]
    if "--stop-now" in argv:
        i = argv.index("--stop-now")
        if len(argv) <= i + 2:
            die("stop-now требует ожидаемые PID и порт")
        stop_now(int(argv[i + 1]), int(argv[i + 2]))
        return
    pos, opt, multi = parse_args(argv)
    cmd = pos[0] if pos else ""
    notes = []
    if cmd == "init":
        state, notes = cmd_init(opt)
    else:
        state = read_state()
        if state is None:
            die("state.js ещё нет — начни с `ap.py init`")
        rest = pos[1:]
        if cmd == "schedule":
            if rest:
                die("schedule: лишние аргументы")
            raw_limit = str(opt.get("max-parallel", "2"))
            if not re.fullmatch(r"[1-3]", raw_limit):
                die("schedule: --max-parallel допускает 1, 2 или 3")
            try:
                from scheduler import schedule
                budget = state.get("budgetTokens")
                spent = sum(e.get("input", 0) + e.get("output", 0)
                            for e in state.get("usageEvents") or [])
                checked = {t["id"]: profile_ok(t) for t in state.get("tickets") or []}
                payload = schedule(state.get("tickets") or [], int(raw_limit),
                                   strict=bool(state.get("strictRouting")),
                                   isolated=bool(state.get("isolateTickets")),
                                   budget_blocked=(budget is not None and spent >= budget),
                                   verified=checked)
            except (ValueError, OSError, ImportError) as exc:
                die("schedule: %s" % exc)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        if cmd not in ("", "sync", "commits"):
            # Время события ставится до команды: ей самой и ленте нужна одна метка.
            state["updatedAt"] = now()
            beat(state)
        if cmd in MOVES_ON:
            close_wait(state)
        if cmd == "stage":
            cmd_stage(state, rest, opt)
        elif cmd == "ticket":
            cmd_ticket(state, rest, opt)
        elif cmd == "tickets":
            notes.append(publish_tickets(state))
            log(state, "tickets", n=len(state.get("tickets") or []))
        elif cmd == "check-plan":
            problems = check_plan(state)
            notes += ["! " + p for p in problems] or ["G3: трасса сходится"]
            set_gate(state, "G3", not problems, problems=len(problems))
        elif cmd == "worktree":
            notes.append(cmd_worktree(state, rest, opt))
        elif cmd == "usage":
            cmd_usage(state, rest, opt)
        elif cmd == "budget":
            cmd_budget(state, rest, opt)
        elif cmd == "set":
            cmd_set(state, rest)
            if any(p.startswith("tier=") for p in rest):
                log(state, "tier", v=state.get("tier"))
        elif cmd == "add":
            cmd_add(state, rest)
        elif cmd in ("coverage", "blind"):
            cmd_numbers(state, cmd, rest, multi)
        elif cmd == "tests":
            state["tests"] = tests_pair(rest[0] if rest else "")
            log(state, "tests", **state["tests"])
        elif cmd == "ask":
            cmd_ask(state, rest, opt)
        elif cmd == "answered":
            close_wait(state)
        elif cmd == "finish":
            notes = cmd_finish(state, opt)
        elif cmd == "reopen":
            cmd_reopen(state)
        elif cmd == "commits":
            notes = cmd_commits(state)
        elif cmd not in ("", "sync"):
            die("неизвестная команда %s — список в начале ap.py" % cmd)
    reconcile_requirements(state)
    recount(state)
    notes = close_passed(state) + notes
    save(state)
    snap = write_snapshot(state)
    if cmd == "finish" or opt.get("stop"):
        srv = stop_later()
    elif opt.get("no-serve"):
        srv = "сервер не проверялся"
    else:
        srv = serve(state)
    r = state.get("requirements") or {}
    print("%s · %s · требований %s, готово %s" % (snap, srv, r.get("total", 0), r.get("done", 0)))
    for line in notes:
        print("  " + (line if line.startswith("!") else "· " + line))
    for line in audit(state)[:5]:
        print("  ! " + line)
    if cmd == "check-plan" and problems:
        sys.exit(2)
    if opt.get("check-update"):
        note = check_update(state)
        if note:
            print("  ↑ " + note)


if __name__ == "__main__":
    if "--stop-now" in sys.argv:
        main()
    else:
        with locked_state():
            main()
