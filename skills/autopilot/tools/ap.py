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
    python3 .autopilot/ap.py ticket 03 retry --cause tests --escalate   # Haiku-таск после 1-го дозапроса -> Sonnet, один раз
    python3 .autopilot/ap.py ticket 03 reset --by-user "<цитата>"   # упавший таск — только по словам пользователя
    python3 .autopilot/ap.py git-check                  # может ли git писать здесь (до init и брифинга)
    python3 .autopilot/ap.py ticket 02 accept-edit --note "…"   # осознанная правка сданного таска
    python3 .autopilot/ap.py claude-version [--text "2.1.302"]  # версия Claude Code (до init)
    python3 .autopilot/ap.py opus propose               # где Opus уместен (только печать)
    python3 .autopilot/ap.py opus approve --tickets 03,05 --roles repair,reviewer --by-user "<цитата>"
    python3 .autopilot/ap.py opus status                # что пользователь подтвердил, подпись верна?
    python3 .autopilot/ap.py agent-for reviewer --diff-lines 3500   # какого агента звать: Opus или обычного
    python3 .autopilot/ap.py agent-for repair
    python3 .autopilot/ap.py plan-fact list | record --verdict "T02.1 | сделано | файл:строка" … | show   # план -> факт, «план: N из M»
    python3 .autopilot/ap.py check-review-report --file ФАЙЛ   # пункты чек-листа без ответа (код 1)
    python3 .autopilot/ap.py check-bypass [РЕВИЗИЯ..РЕВИЗИЯ]   # добавленные skip/xfail/--no-verify, удалённые assert
    python3 .autopilot/ap.py blocker confirm --id B01 --verdict confirmed|not-confirmed --quote "…"   # второй проход
    python3 .autopilot/ap.py agents install-user --by-user "<цитата>" | --decline   # лёгкие профили в папку настроек Claude Code (один раз)
    python3 .autopilot/ap.py agents prune [--apply]     # профили autopilot-* сданных прогонов: без --apply только список
    python3 .autopilot/ap.py chore test-count           # генератор из interfaces.md («Команды-генераторы»): запуск и коммит только его файлов
    python3 .autopilot/ap.py ticket 03 land --message "T03: приём заявки" --requirements R01,R02 [--zone a/,b/]   # вне зоны, полная проверка, коммит зоны, done
    python3 .autopilot/ap.py ticket 03 land --include a/x.py,b/   # land: дописать файлы вне зоны к коммиту (отдельно от --allow)
    python3 .autopilot/ap.py ticket 03 redproof --command "…"   # bug: красный тест до правки (код ≠ 0)
    python3 .autopilot/ap.py ticket 03 baseline --command "…"   # refactor: зелёные тесты до правок (код 0)
    python3 .autopilot/ap.py ticket 03 bundle           # сводка для исполнителя: упавшая проверка, блокеры, замечания
    python3 .autopilot/ap.py silence [--limit СЕК] [--transcript ПУТЬ]   # тихие агенты (код 3); нет журнала — код 1
    python3 .autopilot/ap.py lessons candidates | add … | show | drop N | check   # уроки сборок в .autopilot/lessons.md
    python3 .autopilot/ap.py profile refresh            # .autopilot/profile.md: команды проекта
    python3 .autopilot/ap.py init --kind quick|bug|task|refactor …   # вид работы (init --kind)
    python3 "<skillDir>/tools/ap.py" bootstrap --project .   # поставить инструменты и дашборд в .autopilot/ (из папки навыка); печатает skillDir
    python3 "<skillDir>/tools/ap.py" doctor             # git-check, версия Claude Code, advisorModel, repo_doctor — строка на проверку
    python3 .autopilot/ap.py url                        # адрес дашборда с токеном — только эта команда (в чат не вставлять)
    python3 .autopilot/ap.py upgrade-tools              # обновить .autopilot/*.py из навыка (init и stage делают сами)
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
    python3 .autopilot/ap.py finish --result "…" --by-user "<цитата>"   # сдать с оговорками — только словами пользователя
    python3 .autopilot/ap.py reopen                     # второй бриф в сданном прогоне
    python3 .autopilot/ap.py commits                    # коммиты сданных тасков ещё в истории?
    python3 .autopilot/ap.py report-run [--share]       # свод журнала прогона (run-log.jsonl)
    python3 .autopilot/ap.py spend-orchestrator [--transcript PATH]   # расход главной сессии в run-log.jsonl (finish делает сам)
    python3 .autopilot/ap.py spend-subagents [--transcript PATH]      # расход субагентов из журналов Claude Code (finish делает сам)
    python3 .autopilot/ap.py                            # просто синхронизировать

После каждой команды: updatedAt = сейчас (и метка в журнале beats), строка в ленте log,
счётчики и список требований — из manifest.md, гейты G1–G4 — из событий, которые их решают,
пройденные этапы закрыты, снимок вписан в dashboard.html, сервер жив. Время
ставит сам скрипт, с секундами и поясом, — агент его не пишет никогда.

Флаги: --check-update (сверить версию навыка с GitHub), --no-serve, --stop, --help.
Работает на macOS, Linux и Windows (в том числе из Git Bash).
"""

import datetime as dt
import hashlib
import importlib.util
import io
import contextlib
import glob
import hmac
import http.server
import json
import os
import posixpath
import re
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # соседние модули инструментов
import state_io  # noqa: E402
RUN_LOG_WARNING = None
try:
    import run_log  # noqa: E402
except Exception as _e:                              # журнал не обязателен для работы
    run_log = None
    RUN_LOG_WARNING = ("run_log.py не найден, журнал не пишется"
                       if isinstance(_e, ModuleNotFoundError) and _e.name == "run_log" else
                       "run_log.py не импортируется (%s), журнал не пишется" % type(_e).__name__)

for _s in (sys.stdout, sys.stderr):                       # cp1251-консоль Windows
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
if RUN_LOG_WARNING:
    print(RUN_LOG_WARNING, file=sys.stderr)

A = os.path.dirname(os.path.abspath(__file__))          # .autopilot этого проекта
ROOT = os.path.dirname(A)
STATE = os.path.join(A, "state.js")
PAGE = os.path.join(A, "dashboard.html")
README = os.path.join(A, "README.md")
PIDF = os.path.join(A, "serve.pid")
LOG = os.path.join(A, "serve.log")
TOKEN_FILE = "serve.token"
RUN_LOG_FAIL = os.path.join(A, "run-log.fail")
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
BLIND_ROUNDS = 2        # слепая приёмка: проверка и одна перепроверка после таска F2


def now():
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def die(msg):
    print("ошибка: " + msg)
    sys.exit(1)


# Формы секретов — те же, что в редакторе брифа (phases/1-manifest.md §1); сначала узкие, общая — последней.
_B64 = r"[A-Za-z0-9_-]"
SECRET_SHAPES = [(name, re.compile(rx)) for name, rx in (
    ("PRIVATE_KEY", r"-----BEGIN [A-Z ]*PRIVATE KEY-----(?:[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----|[\s\S]*$)"),
    ("DATABASE_URL", r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s:/@]+:[^\s@]+@\S+"),
    ("API_KEY", r"\b(?:sk|rk|pk)[-_]" + _B64 + r"{8,}"),
    ("GITHUB_TOKEN", r"\b(?:gh[pous]_" + _B64 + r"{20,}|github_pat_" + _B64 + r"{20,})"),
    ("AWS_ACCESS_KEY_ID", r"\b(?:AKIA|ASIA)[A-Z0-9]{12,}"),
    ("GOOGLE_API_KEY", r"\b(?:AIza" + _B64 + r"{20,}|ya29\." + _B64 + r"{20,})"),
    ("SLACK_TOKEN", r"\bxox[bpa]-[A-Za-z0-9-]{10,}"),
    ("TELEGRAM_BOT_TOKEN", r"\b\d{8,10}:" + _B64 + r"{35}\b"),
    ("JWT", r"\beyJ" + _B64 + r"{5,}\." + _B64 + r"{5,}(?:\." + _B64 + r"*)?"),
    ("SECRET", r"(?i)(?:key|token|secret|password|ключ\w*|токен\w*|пароль|доступ\w*)\W{1,12}[A-Za-z0-9+/=_-]{32,}"),
)]


def redact_secrets(text):
    """Текст без значений, похожих на секреты, и число вырезанных. Значение нигде не повторяется."""
    hits = 0
    for name, rx in SECRET_SHAPES:
        text, n = rx.subn("[REDACTED:%s]" % name, text)
        hits += n
    return text, hits


def clean_quote(raw):
    """`--by-user` → слова пользователя без секретов (R25) или None, если слов нет."""
    text = raw.strip() if isinstance(raw, str) else ""
    if not text:
        return None
    text, hits = redact_secrets(text)
    if hits:
        print("! в словах пользователя был ключ — я его не сохранил. Впиши его сам в `.env`, "
              "а этот лучше отзови и выпусти новый")
    return text


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
    if not os.path.exists(STATE):
        return None
    try:
        state = state_io.read_state_file(STATE)
        state_io.ensure_schema_version(state)
        return state
    except state_io.StateError as e:
        die("%s — перезапиши его командой init или поправь строку" % e)


def save(state):
    refresh_g1(state)                                  # G1 идёт за манифестом при каждой записи
    state["rev"] = (state.get("rev") or 0) + 1        # дашборд перерисовывается по нему
    try:
        state_io.ensure_schema_version(state)
        state_io.write_state_file(STATE, state, prefix="window.STATE =\n")
    except state_io.StateError as e:
        die(str(e))


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
    journal = kw.pop("journal", None) or {}           # поля только для run-log.jsonl
    entry = {"t": state["updatedAt"], "k": event}
    entry.update({k: v for k, v in kw.items() if v not in (None, "", [])})
    state.setdefault("log", []).append(entry)
    del state["log"][:-LOG_KEPT]
    try:
        mirror_run_log(state, event, kw, journal)
    except Exception:                                 # журнал только пишет и не блокирует
        pass


def mirror_run_log(state, event, kw, extra):
    """Событие ленты → строки run-log.jsonl (схема в run_log.KINDS)."""
    if run_log is None:
        return
    put = lambda row, **f: run_log.append(A, row, run=state.get("dir"), **f)
    if event == "stage":
        put("phase", id=kw.get("id"), act=kw.get("act"))
    elif event == "ticket":
        if kw.get("act") in ("start", "done", "retry", "fail", "repair", "review"):
            for i in kw.get("ids") or []:
                put("ticket", id=i, act=kw["act"], cause=extra.get("cause"), **(extra.get("routes") or {}).get(i, {}))
        if isinstance(kw.get("tests"), dict):
            put("tests", source="ticket", **kw["tests"])
    elif event == "gate":
        put("gate", g=kw.get("g"), ok=kw.get("ok"), reason=kw.get("reason"))
        if kw.get("reason"):
            put("reset", what="gate", id=kw.get("g"), reason=kw["reason"])
    elif event == "tests":
        put("tests", passed=kw.get("passed"), failed=kw.get("failed"),
            seconds=extra.get("seconds"), source="manual")
    elif event == "worktree" and kw.get("act") == "verify":
        put("tests", passed=kw.get("tests"), failed=0, seconds=extra.get("seconds"), source="host")
    elif event == "escalate":
        put("ticket", id=kw.get("id"), act="escalate", cause="tests")
    elif event == "ticket-reset":
        put("reset", what="ticket", id=kw.get("id"), reason=kw.get("reason"))
    elif event == "ask":
        put("wait", kind=kw.get("kind"), act="start")
    elif event == "answered":
        put("wait", kind=kw.get("kind"), act="end")


def set_gate(state, g, ok, **kw):
    """Гейт решается событием, которое его проверяет: G1 — открытием спецификации,
    G2 — coverage, G3 — check-plan, G4 — blind. Повторная проверка перезаписывает."""
    rec = {"ok": bool(ok), "at": state["updatedAt"]}
    rec.update({k: v for k, v in kw.items() if v is not None})
    state.setdefault("gates", {})[g] = rec
    log(state, "gate", g=g, ok=bool(ok), **kw)


def refresh_g1(state, create=False):
    """G1 равен манифесту: открытых строк (кроме D) нет. Гейта нет и create=False — выход.
    Гейт, сброшенный сменой плана (plan-changed), снимает только повторный `stage spec`."""
    cur = (state.get("gates") or {}).get("G1")
    if (cur is None and not create) or (cur or {}).get("reason") == "plan-changed":
        return
    rows = [r for r in manifest_table(state) or [] if not r["id"].startswith("D")]
    if not rows:
        return
    n = sum(1 for r in rows if r["status"] == "open")
    if cur and (cur.get("ok"), cur.get("open"), cur.get("total")) == (n == 0, n, len(rows)):
        return
    set_gate(state, "G1", n == 0, open=n, total=len(rows))


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


def ticket_files(state, pattern):
    """Файлы тасков прогона по шаблону имени — единственный glob по `tickets/`.
    Путь экранирован: `[`, `]` и `*` в папке проекта не читаются как шаблон."""
    return glob.glob(os.path.join(glob.escape(run_dir(state)), "tickets", pattern))


def artifact_present(state, art):
    """Файл-след этапа (`manifest.md`, `tickets/*.md`) лежит в папке прогона?"""
    if art.startswith("tickets/"):
        return bool(ticket_files(state, art[len("tickets/"):]))
    return os.path.exists(os.path.join(run_dir(state), art))


def fresh_state(a):
    t = now()
    return {
        "schemaVersion": state_io.SCHEMA_VERSION,
        "version": 2,
        "slug": a["slug"], "dir": "%s-%s--wip" % (t[:10], a["slug"]),
        "title": a.get("title") or a["slug"],
        "mode": a.get("mode") or "semi", "depth": a.get("depth") or "normal",
        "kind": a.get("kind") or "task",
        "tier": None, "strictRouting": bool(a.get("strict-routing")),
        "gateSigned": bool(a.get("strict-routing")),
        "sequentialHost": bool(a.get("sequential-host")),
        "spendLedger": [],
        "isolateTickets": bool(a.get("isolated-tickets") or a.get("sequential-host")),
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
        "additions": [], "coverage": None, "concerns": [], "blockingFindings": [],
        "blind": None, "beats": [t],
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


FIX_TICKET_FILE = re.compile(r"F\d+-.*\.md$")


def plan_contract_digest(state):
    """Bind G3 to requirement wording and the exact planned ticket files.

    Ticket acceptance legitimately changes manifest progress columns, but
    must not change requirement ID/text/rationale or silently remove/replace
    a planned ticket. Include D constraints and ticket file names and bytes.
    """
    rows = manifest_table(state)
    if not rows:
        return None
    contract = [[r["id"], r["text"], r["why"]] for r in rows]
    tickets = []
    for path in sorted(ticket_files(state, "*.md")):
        if FIX_TICKET_FILE.match(os.path.basename(path)):
            continue                      # fix-таски (F<n>-*.md) создаёт ревью ветки: контракт плана их не включает
        try:
            with open(path, "rb") as source:
                digest = hashlib.sha256(source.read()).hexdigest()
        except OSError:
            return None
        tickets.append([os.path.basename(path), digest])
    payload = json.dumps([contract, tickets], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def plan_validation_digest(state):
    """G3 input snapshot: include manifest statuses, unlike the finish contract.

    Status changes can affect whether an unassigned requirement needs a ticket.
    Accepting completed tickets may change statuses later, so this checksum is
    only a pre-dispatch check for the pending-ticket batch apply operation.
    """
    contract = plan_contract_digest(state)
    rows = manifest_rows(state)
    if contract is None or rows is None:
        return None
    payload = json.dumps([contract, rows], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
        "blockedBy": re.findall(r"[A-Za-z]*\d+[a-z]?", get("зависит от", "blocked by")),
        "wave": int(wave.group()) if wave else None,
        "zone": re.findall(r"`([^`]+)`", get("зона", "zone")),
        "review": get("ревью", "review") or None,
        "model": get("модель", "model") or None,
        "repro": get("вид", "kind").strip().lower() == "воспроизведение",
        "testsEdit": get("правка тестов", "tests edit") or None,
    }


def dep_id(ref, ids):
    """Ссылка из «Зависит от» → id таска. `2`, `02`, `T2` — это таск 02; ссылка, которая
    сама есть id таска (`F1`, `E34`), остаётся как есть; любая другая — тоже как есть,
    и check-plan назовёт её несуществующей. Цифры из чужой ссылки не вынимаются никогда."""
    if ref in ids:
        return ref
    m = re.match(r"^[Tt]?(\d+)$", ref)
    return m.group(1).zfill(2) if m else ref


# Те же шаблоны, что в tests/test_no_machine_data.py (не расширять сверх них).
MACHINE_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\Users\\(?!<|demo\\|user\\|example\\)[A-Za-z0-9_.-]+\\"),
    re.compile(r"/(?:home|Users)/(?!<|demo/|user/|example/)[a-z0-9_.-]+/", re.I),
]


def machine_path_hits(text):
    """Пути машины в тексте → [(номер строки, совпадение)]."""
    return [(n, m.group(0)) for n, line in enumerate(text.splitlines(), 1)
            for p in MACHINE_PATH_PATTERNS for m in p.finditer(line)]


def check_machine_paths(state, files):
    for p in files + [os.path.join(run_dir(state), "spec.md")]:
        try:
            with open(p, "rb") as f:
                text = f.read().decode("utf-8", errors="replace")
        except OSError:
            continue
        hits = machine_path_hits(text)
        if hits:
            die("путь машины в %s, строка %d: %s — замени на <repo> или <scratchpad>"
                % (os.path.relpath(p, A).replace(os.sep, "/"), hits[0][0], hits[0][1]))


def publish_tickets(state):
    files = sorted(ticket_files(state, "*.md"))
    if not files:
        return "в %s/tickets/ нет файлов" % state.get("dir")
    check_machine_paths(state, files)
    old = {t["id"]: t for t in state.get("tickets") or []}
    out = []
    for p in files:
        t = parse_ticket(p)
        with open(p, "rb") as stream:
            raw = stream.read()
        t["fingerprint"] = state_io.ticket_fingerprint(raw)
        prev = old.get(t["id"], {})
        if prev.get("fingerprint") and not state_io.fingerprint_matches(prev["fingerprint"], raw):
            if prev.get("status") == "done":
                if prev.get("acceptedFingerprint") != t["fingerprint"]:
                    die("сданный таск %s изменён; если правка осознанная: "
                        "`ap.py ticket %s accept-edit --note \"что и почему\"`" % (t["id"], t["id"]))
                if prev.get("worktree") and prev["worktree"].get("status") != "released":
                    die("таск %s изменён при существующем worktree: посадите его "
                        "(`ap.py worktree %s land`) или снимите (`ap.py worktree %s release`)"
                        % (t["id"], t["id"], t["id"]))
                prev = {k: v for k, v in prev.items() if k != "acceptedFingerprint"}
            elif prev.get("worktree") and prev["worktree"].get("status") not in ("released",):
                die("таск %s изменён при существующем worktree; завершите и освободите его вручную" % t["id"])
            else:
                if prev.get("status") not in (None, "pending"):
                    log(state, "ticket-reset", id=t["id"], reason="ticket-edited")
                prev = {}
        elif "acceptedFingerprint" in prev:
            prev = {k: v for k, v in prev.items() if k != "acceptedFingerprint"}
        for k in ("status", "startedAt", "finishedAt", "retries", "repairs", "repairFindings",
                  "tests", "commit", "concerns", "placeholders", "routing", "plannedRouting",
                  "worktree", "retryAdvice", "attestation", "attestFrom", "startHead", "redproof", "baseline"):
            if k in prev:
                t[k] = prev[k]
        t.setdefault("status", "pending")
        t.setdefault("retries", 0)
        t.setdefault("repairs", 0)
        out.append(t)
    known = {t["id"] for t in out}
    for t in out:
        t["blockedBy"] = [dep_id(b, known) for b in t["blockedBy"]]
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
    if len({rid for rid, _ in rows}) != len(rows):
        problems.append("повторяются ID требований в манифесте")
    named = {r for t in tickets for r in t["requirements"]}
    base = {r.split(".")[0] for r in named}
    for rid, st in rows:
        if st not in STATUS_KEY and st != "open":  # a typo would hide the row from every gate count
            problems.append("неизвестный статус «%s» у %s" % (st, rid))
        if st in ("in-spec", "in-ticket", "placeholder", "done") and not rid.startswith("D") and rid not in base:
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
    try:
        import model_router as router
    except ImportError:
        router = None
    for t in tickets if router else []:
        if t["id"].startswith("F"):               # fix-таск ветки идёт сильным по фазе 6, оценки планировщика у него нет
            continue
        files = ticket_files(state, "%s-*.md" % t["id"])
        if len(files) != 1:
            continue
        with open(files[0], encoding="utf-8") as stream:
            for why in router.plan_problems(stream.read()):
                problems.append("таск %s: %s" % (t["id"], why))
    try:
        import kinds
    except ImportError:
        kinds = None
    if kinds:
        problems += kinds.plan_problems(kinds.of_state(state), [t for t in tickets if not t["id"].startswith("F")],
                                        len(rows))
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


def stage_segments(s):
    """Отрезки работы этапа. Старый state.js без них: один отрезок из startedAt/finishedAt."""
    if "segments" not in s:
        s["segments"] = ([{"startedAt": s["startedAt"], "finishedAt": s.get("finishedAt")}]
                         if s.get("startedAt") else [])
    return s["segments"]


def segment_open(s, t):
    """Этап открыт (или возвращён): новый отрезок, если прежний уже закрыт."""
    segs = stage_segments(s)
    if not segs or segs[-1].get("finishedAt"):
        segs.append({"startedAt": t, "finishedAt": None})


def segment_close(s, t):
    segs = stage_segments(s)
    if not segs:
        segs.append({"startedAt": t, "finishedAt": t})     # этап закрыт, не открывшись
    elif not segs[-1].get("finishedAt"):
        segs[-1]["finishedAt"] = t


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
            segment_close(s, later[0])
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
        if artifact_present(state, art):
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
    i, j = page.find(BEGIN), page.rfind(END)      # END один в шаблоне; rfind лечит старые снимки с сырым END внутри
    if i < 0 or j < 0:
        return "страница без маркеров снимка — перекопируй dashboard.html из навыка"
    # `*\/` в JSON — тот же `*/`, но маркер снимка не закрывает
    payload = ("window.STATE=" + json.dumps(state, ensure_ascii=False).replace("</", "<\\/").replace("*/", "*\\/")
               + ";")
    new = page[: i + len(BEGIN)] + payload + page[j:]
    if new != page:
        tmp = PAGE + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(new)
            state_io.replace_with_retry(tmp, PAGE)
        except OSError as e:                          # страницу держит читатель: команда не падает
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            return "дашборд не обновлён (%s) — повтори команду" % e
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
    """Сервер этого проекта — и только он: наш `ap.py --serve <порт>` либо прежний
    `-m http.server` с ровно нашим --directory (его гасим: токена у него нет).
    Узко намеренно: широкая проверка уже убивала чужие серверы."""
    c = cmd.replace("\\", "/")
    c = c.lower() if WIN else c
    return is_guarded_server(cmd) or (bool(re.search(r"-m\s+http\.server\b", c)) and bool(_OURS.search(c)))


def is_guarded_server(cmd):
    """Сервер с проверкой Host и токена: ровно наш ap.py с флагом --serve."""
    c = cmd.replace("\\", "/")
    c = c.lower() if WIN else c
    return _norm(os.path.abspath(__file__)) in c and bool(re.search(r"\s--serve\s+\d+", c))


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


# ── сервер дашборда: Host, Origin и токен ───────────────────────────────────

OPEN_PAGES = ("/", "/dashboard.html", "/index.html")      # без токена: сама страница
STATIC_NAME = re.compile(r"/[\w.-]+\.(?:svg|png|ico|css|woff2|jpg|webp)", re.I)   # и статика верхнего уровня


def serve_token(directory=None):
    """Токен сервера лежит в `serve.token` и переживает перезапуск ap.py; нет файла — создаётся."""
    path = os.path.join(directory or A, TOKEN_FILE)
    try:
        with open(path, encoding="utf-8") as f:
            token = f.read().strip()
        if len(token) >= 16:
            return token
    except OSError:
        pass
    token = secrets.token_urlsafe(24)
    temp = "%s.%d.tmp" % (path, os.getpid())
    try:
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(token + "\n")
        try:
            os.link(temp, path)                       # целиком или никак: пустого файла токена никто не увидит
        except FileExistsError:                       # старый пустой или короткий файл — заменяем, живой — берём
            with open(path, encoding="utf-8") as f:
                other = f.read().strip()
            if len(other) >= 16:
                return other
            os.replace(temp, path)
        except OSError:
            os.replace(temp, path)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(temp)
    return token


PING_PATH = "/.ap-ping"        # вне OPEN_PAGES и без `?t=`: ответ не несёт токена, а Host/Origin/Sec-Fetch-Site проверены как везде


def ping_digest(token, port):
    """Ответ сервера на PING_PATH: hex hmac-sha256 с ключом-токеном от «autopilot-ping|<порт>». Токен по сети не уходит;
    порт внутри — чтобы ответ одного сервера не годился чужому на другом порту."""
    return hmac.new(token.encode(), ("autopilot-ping|%d" % port).encode(), hashlib.sha256).hexdigest()


def ping_reply(port):
    """Тело ответа PING_PATH или None: сервера нет, он старый (403/404) или это чужой процесс без такого пути."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d%s" % (port, PING_PATH), timeout=2) as r:
            return r.read(256).decode("utf-8", "replace").strip() if r.status == 200 else None
    except (urllib.error.URLError, OSError, ValueError):
        return None


def server_is_ours(port):
    """Сервер на порту — наш с текущим токеном: ответ сошёлся с hmac от `serve.token`. Без PowerShell/`ps`.
    Удалённый или переписанный `serve.token` даёт другой токен, ответ не сходится — вызывающий перезапускает сервер."""
    got = ping_reply(port)
    return got is not None and hmac.compare_digest(got.encode(), ping_digest(serve_token(), port).encode())


def make_server(directory, port, token):
    """HTTP-сервер каталога `directory` на 127.0.0.1. 403, если чужой Host/Origin,
    `Sec-Fetch-Site: cross-site`, либо запрошено не страница и не статика, а токена `?t=` нет."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kw):
            super().__init__(*args, directory=directory, **kw)

        def allowed(self):
            p = self.server.server_port
            hosts = ("127.0.0.1:%d" % p, "localhost:%d" % p)
            if (self.headers.get("Host") or "").lower() not in hosts:
                return False
            if (self.headers.get("Sec-Fetch-Site") or "").lower() == "cross-site":
                return False
            origin = (self.headers.get("Origin") or "").lower()
            if origin and origin not in ["http://" + h for h in hosts]:
                return False
            url = urllib.parse.urlsplit(self.path)
            path = urllib.parse.unquote(url.path)
            if path in OPEN_PAGES or path == PING_PATH or STATIC_NAME.fullmatch(path):
                return True
            given = (urllib.parse.parse_qs(url.query).get("t") or [""])[0]
            return (posixpath.basename(path) != TOKEN_FILE
                    and hmac.compare_digest(given.encode(), token.encode()))

        def tokenless_page(self):
            """Открытая страница без верного токена: тело с `window.STATE=null`; b"" — подмена не удалась
            (файл не отдаём, будет 403); None — иная страница или токен верный, отдаём как есть.
            PING_PATH тоже идёт этим путём: тело — подтверждение сервера, не страница."""
            url = urllib.parse.urlsplit(self.path)
            path = urllib.parse.unquote(url.path)
            if path == PING_PATH:
                return ping_digest(token, self.server.server_port).encode()
            if path not in OPEN_PAGES:
                return None
            given = (urllib.parse.parse_qs(url.query).get("t") or [""])[0]
            if hmac.compare_digest(given.encode(), token.encode()):
                return None
            try:
                with open(self.translate_path("/index.html" if path == "/" else path), "rb") as f:
                    page = f.read().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                return b""
            i, j = page.find(BEGIN), page.rfind(END)
            if i < 0 or j < i:
                return b""
            page = page[: i + len(BEGIN)] + "window.STATE=null;" + page[j:]
            # без токена state.js всё равно 403: тег убираем, чтобы в консоли не было лишней ошибки
            return page.replace('<script src="state.js"></script>', "").encode("utf-8")

        def do_GET(self):
            if not self.allowed():
                return self.send_error(403)
            body = self.tokenless_page()
            if body is None:
                return super().do_GET()
            self.send_page(body)

        def send_page(self, body, head=False):
            if not body:
                return self.send_error(403)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def do_HEAD(self):
            if not self.allowed():
                return self.send_error(403)
            body = self.tokenless_page()
            return super().do_HEAD() if body is None else self.send_page(body, head=True)

        def list_directory(self, path):
            self.send_error(403)                      # состав каталога не показываем
            return None

        def log_message(self, fmt, *args):
            # serve.log лежит рядом с проектом: query (`?t=<токен>`) в него не пишем
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(),
                                                   re.sub(r"\?\S*", "?", fmt % args)))

        def end_headers(self):
            self.send_header("Referrer-Policy", "no-referrer")   # токен в адресе не уходит дальше
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    return http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)


def run_server(port):
    make_server(A, port, serve_token()).serve_forever()


def page_url(port, with_token=True):
    """Адрес дашборда; токен — только для `ap.py url`."""
    base = "http://localhost:%d/dashboard.html" % port
    return base + "?t=" + serve_token() if with_token else base


def serve(state, with_token=False):
    port, pid = recorded()
    if state.get("finishedAt"):
        kill_orphans(keep=pid)
        return "прогон закрыт"
    if os.environ.get("SSH_CONNECTION") or os.environ.get("CI"):
        return "удалённая сессия — без сервера, дашборд: %s" % PAGE
    # Сошёлся ответ сервера — процессы не смотрим (PowerShell на Windows ≈ 0,56 с на команду). Ответ есть, но не
    # сошёлся (удалён serve.token) — не наш, перезапуск. Ответа нет (старый ap.py, чужой процесс) — прежняя проверка процесса.
    if port and pid and http_ok(port) and (server_is_ours(port) or (ping_reply(port) is None
                                                                    and is_guarded_server(cmdline(pid)))):
        return page_url(port, with_token)
    kill_orphans()
    port = free_port(port)
    if not port:
        return "порт не нашёлся — дашборд открывается файлом: %s" % PAGE
    try:
        with open(LOG, "a", encoding="utf-8") as log:
            srv = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--serve", str(port)],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=log, **_detached())
    except OSError as e:
        return "сервер не запустился (%s) — дашборд открывается файлом: %s" % (e, PAGE)
    for _ in range(10):
        if http_ok(port):
            with open(PIDF, "w", encoding="utf-8") as f:
                f.write("%d %d\n" % (port, srv.pid))
            return "сервер поднят: " + page_url(port, with_token)
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
    entries = [".autopilot/serve.*", ".autopilot/serve.token", ".autopilot/state.lock",
               ".autopilot/run-log.fail",
               ".autopilot/dispatch-*.lock", ".autopilot/controller.lock",
               ".autopilot/gui-dispatch/",
               ".autopilot/api-pilot/", ".autopilot/api-pilot-consent",
               ".autopilot/offline-worker/", ".autopilot/offline-test-consent",
               ".autopilot/__pycache__/", ".autopilot/run-log*.jsonl",
               ".autopilot/worktrees/", ".autopilot/model-capabilities.json",
               ".autopilot/history-cache.json",
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


def archive_old_state(old):
    """Старый state.js уходит в папку его прогона, а без неё — в .autopilot/archive/.
    Существующий файл не затирается: к имени добавляется -2, -3. Возвращает путь от .autopilot."""
    if old.get("dir") and os.path.isdir(os.path.join(A, old["dir"])):
        folder, name = old["dir"], "state.js"
    else:
        folder = "archive"
        name = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-state.js"
    os.makedirs(os.path.join(A, folder), exist_ok=True)
    stem, ext = os.path.splitext(name)
    dst, n = os.path.join(folder, name), 1
    while os.path.exists(os.path.join(A, dst)):
        n += 1
        dst = os.path.join(folder, "%s-%d%s" % (stem, n, ext))
    if subprocess.run(["git", "-C", A, "mv", "-f", "state.js", dst], capture_output=True).returncode:
        os.replace(STATE, os.path.join(A, dst))
    return dst.replace(os.sep, "/")


SELF_UPGRADE = []        # новая копия ap.py: подменяется в конце команды (main), а не посреди неё


def skill_pin_path():
    """Куда init кладёт skillDir подписанного прогона: рядом с признаком подписи, вне проекта."""
    return str(_gs().record_path(ROOT)) + ".skill"


def _skill_key(path):
    return os.path.normcase(os.path.realpath(path))


def write_skill_pin(state):
    """Подписанный прогон: зафиксировать skillDir при init (правка state.js источник не меняет)."""
    body = {"run": run_id(state), "skillDir": _skill_key(state.get("skillDir") or "")}
    body["sig"] = _gs().sign(body)
    try:
        with open(skill_pin_path(), "w", encoding="utf-8") as stream:
            json.dump(body, stream)
    except OSError as exc:
        die("не удалось записать skillDir прогона: %s" % exc)


def skill_dir_trusted(state):
    """Неподписанный прогон — всегда; подписанный — только если skillDir тот, что был при init."""
    try:
        if _gs().run_status(state, ROOT) == "unsigned":
            return True
        with open(skill_pin_path(), encoding="utf-8") as stream:
            pin = json.load(stream)
        return (isinstance(pin, dict) and _gs().verify({k: v for k, v in pin.items() if k != "sig"}, pin.get("sig"))
                and pin.get("run") == run_id(state) and pin.get("skillDir") == _skill_key(state.get("skillDir") or ""))
    except ImportError:  # харнесс без gate_sign подписанных прогонов не ведёт
        return True
    except (OSError, ValueError):
        return False


NOT_PINNED = ("skillDir не совпадает с зафиксированным при init (прогон подписан): инструменты из него не копирую; "
              "верни skillDir или сделай init заново")


def upgrade_tools(state, auto=False):
    """Копирует из `skillDir/tools/` в `.autopilot/` отличающиеся и новые `.py`; ap.py — в конце команды.
    Возвращает имена. Ручной вызов отказывает, пока таск в работе; auto (init, stage) молча пропускает.
    Подписанный прогон берёт только skillDir, зафиксированный при init; сбой записи не оставляет половину обновления."""
    src = os.path.join(state.get("skillDir") or "", "tools")
    busy = [t["id"] for t in state.get("tickets") or [] if t.get("status") in ACTIVE_EXECUTOR]
    if not state.get("skillDir") or not os.path.isfile(os.path.join(src, "ap.py")) or (
            os.path.realpath(src) == os.path.realpath(A)):
        if auto:
            return []
        die("upgrade-tools: нет skillDir/tools/ap.py (init без --skill-dir, навык убран) или это сама папка инструментов")
    if busy:
        if auto:
            return []
        die("upgrade-tools: таск в работе (%s) — обнови инструменты между тасками" % ", ".join(busy))
    if not skill_dir_trusted(state):
        raise UntrustedSkillDir(NOT_PINNED)
    todo, tmps = [], []
    try:
        for name in sorted(os.listdir(src)):
            old, new = os.path.join(A, name), os.path.join(src, name)
            if not name.endswith(".py") or not os.path.isfile(new):
                continue
            with open(new, "rb") as f2:
                data = f2.read()
            if os.path.isfile(old):                   # нового файла навыка в .autopilot/ ещё нет — он тоже доезжает
                with open(old, "rb") as f1:
                    if f1.read() == data:
                        continue
            if name != "ap.py":
                tmp = old + ".new"
                tmps.append(tmp)
                with open(tmp, "wb") as stream:
                    stream.write(data)
            todo.append((name, old, data))
        for name, old, data in todo:
            if name == "ap.py":
                SELF_UPGRADE.append(data)
            else:
                os.replace(old + ".new", old)
    except OSError:
        SELF_UPGRADE.clear()                  # ap.py и модули не должны разойтись по версиям
        for tmp in tmps:
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise
    return [name for name, _, _ in todo]


class UntrustedSkillDir(Exception):
    pass


def upgrade_note(state):
    """Автообновление в init/stage: строка для вывода или []. Сбой записи не валит команду."""
    try:
        done = upgrade_tools(state, auto=True)
    except UntrustedSkillDir:
        return ["! инструменты не обновлены: " + NOT_PINNED]
    except OSError as exc:
        return ["! инструменты не обновлены (%s): запусти `ap.py upgrade-tools`" % type(exc).__name__]
    return ["инструменты обновлены из навыка: " + ", ".join(done)] if done else []


def refresh_dashboard(state):
    """Копия `.autopilot/dashboard.html` отстала от шаблона навыка — обновить через dashboard_upgrade.upgrade.
    Возвращает одну строку для печати: что обновлено или почему нет; пусто — копия актуальна. Не исключение."""
    template = os.path.join(state.get("skillDir") or "", "phases", "dashboard-template.html")
    if not state.get("skillDir") or not os.path.isfile(template):
        return ""
    try:
        snapshot = re.compile(re.escape(BEGIN) + r"window\.STATE=.*?;" + re.escape(END), re.S)
        bare = lambda text: snapshot.sub("", text)
        with open(template, encoding="utf-8") as f, open(PAGE, encoding="utf-8") as g:
            if bare(f.read()) == bare(g.read()):
                return ""
        try:
            import dashboard_upgrade
        except ImportError:                       # в .autopilot/ нет dashboard_upgrade.py (харнесс, старая установка)
            if not skill_dir_trusted(state):
                return "! дашборд не обновлён из шаблона: " + NOT_PINNED
            spec = importlib.util.spec_from_file_location(
                "dashboard_upgrade", os.path.join(state["skillDir"], "tools", "dashboard_upgrade.py"))
            dashboard_upgrade = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dashboard_upgrade)
        done = dashboard_upgrade.upgrade(ROOT, template)
    except (OSError, ImportError, ValueError, SyntaxError) as exc:         # UpgradeError — это ValueError
        return "! дашборд не обновлён из шаблона (%s)" % type(exc).__name__
    return "дашборд обновлён из шаблона навыка" if done.get("status") == "upgraded" else ""


def finish_self_upgrade():
    """Конец команды: заменить свою копию ap.py (идущий процесс уже прочитал её целиком)."""
    while SELF_UPGRADE:
        tmp = os.path.join(A, "ap.py.new")
        with open(tmp, "wb") as stream:
            stream.write(SELF_UPGRADE.pop())
        os.replace(tmp, os.path.join(A, "ap.py"))


def light_profiles_notes():
    """Обычный прогон: четыре постоянных лёгких профиля в `.claude/agents/` и один вопрос про профили
    на уровне пользователя, пока нет ответа. Сбой записи — строка `!`, не падение `init`."""
    notes = []
    try:
        import agent_profiles
        written = agent_profiles.install_permanent(ROOT)
        if written:
            notes.append("лёгкие профили записаны в .claude/agents: " + ", ".join(written)
                         + " — Claude Code увидит их со следующего чата")
    except (OSError, ImportError, ValueError) as exc:
        notes.append("! лёгкие профили не записаны (%s): сборка пойдёт на general-purpose" % type(exc).__name__)
    if user_profiles_answer() is None:
        notes.append("? профили лёгких агентов можно поставить и на уровне пользователя (%s): сборка в любой "
                     "папке станет дешевле уже с первого чата. Спроси пользователя один раз: согласие — "
                     "`ap.py agents install-user --by-user \"<его слова>\"`, отказ — `ap.py agents install-user --decline`"
                     % os.path.join(claude_config_dir(), "agents"))
    return notes


def claude_config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def user_profiles_file():
    home = os.environ.get("AUTOPILOT_HOME", "").strip()
    return os.path.join(home or os.path.join(os.path.expanduser("~"), ".autopilot"), "user-profiles")


def user_profiles_answer():
    """`install` | `decline` — ответ пользователя про профили в папке настроек; None — не спрашивали."""
    try:
        with open(user_profiles_file(), encoding="utf-8") as f:
            word = f.read().strip()
    except OSError:
        return None
    return word if word in ("install", "decline") else None


def cmd_agents(pos, opt):
    """`agents install-user --by-user "<цитата>" | --decline`: запись вне проекта — только со словами пользователя."""
    usage = 'agents install-user --by-user "<слова пользователя>" | --decline'
    if pos == ["prune"]:
        return cmd_agents_prune(opt)
    if pos != ["install-user"]:
        die(usage)
    quote = opt.get("by-user")
    decline = opt.get("decline") is True
    if decline == (quote is not None):
        die(usage + ": нужно ровно одно из двух; без слов пользователя ничего не пишу вне проекта")
    if not decline and not (isinstance(quote, str) and clean_quote(quote)):
        die(usage + ": слова пользователя пусты")
    answer = "decline" if decline else "install"
    names = []
    if not decline:
        try:
            import agent_profiles
            names = agent_profiles.install_permanent(claude_config_dir(), "agents")
        except (OSError, ImportError) as exc:
            die("agents install-user: профили не записаны (%s)" % type(exc).__name__)
    try:
        os.makedirs(os.path.dirname(user_profiles_file()), exist_ok=True)
        with open(user_profiles_file(), "w", encoding="utf-8") as f:
            f.write(answer + "\n")
    except OSError as exc:
        print("! ответ не сохранён (%s): `init` спросит снова" % type(exc).__name__)
    print("профили в %s: %s" % (os.path.join(claude_config_dir(), "agents"), ", ".join(names) or
                               ("не записаны: отказ запомнен" if decline else "уже на месте")))
    return 0


def cmd_init(opt):
    if opt.get("sequential-host") and opt.get("strict-routing"):
        die("init: --sequential-host и --strict-routing несовместимы; "
            "нет подтверждения нативного субагента")
    if not opt.get("slug"):
        die("init требует --slug")
    if "kind" in opt:
        import kinds
        try:
            kinds.normalize(opt["kind"])
        except ValueError as exc:
            die("init: --kind: %s" % exc)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(opt["slug"])):
        die("slug: разрешены только a-z, 0-9 и одиночные дефисы")
    old = read_state()
    notes = []
    if opt.get("strict-routing"):
        try:
            _gs().ensure_key()
        except OSError as exc:
            die("init: не удалось создать ключ подписи %s (%s)" % (_gs().key_path(), type(exc).__name__))
    if old and not old.get("finishedAt") and not opt.get("force"):
        die("идёт прогон %s — это продолжение, а не новый прогон (или --force)" % old.get("dir"))
    if old:
        notes.append("прошлый прогон убран в архив: %s" % archive_old_state(old))
    state = fresh_state(opt)
    if state["gateSigned"]:
        state["gateMark"] = _gs().run_mark(state)
        write_run_record(state)
        write_skill_pin(state)
    else:
        drop_run_record()
    try:  # версия навыка для шапки дашборда; нечитаемый SKILL.md — просто без неё
        v = _version(open(os.path.join(state["skillDir"] or "", "SKILL.md"), encoding="utf-8").read())
        if v:
            state["skillVersion"] = ".".join(map(str, v))
    except OSError:
        pass
    log(state, "init")
    os.makedirs(os.path.join(run_dir(state), "tickets"), exist_ok=True)
    save(state)
    ensure_gitignore()
    register_row(state, "в работе", None)
    notes.append("папка прогона: .autopilot/%s" % state["dir"])
    if not opt.get("strict-routing"):
        notes += light_profiles_notes()
    return state, notes + upgrade_note(state)


def cmd_execution(state, pos, opt):
    """Opt in to sequential-host on an unfinished run before any worker work.

    Never reinterpret already launched tasks, approved model routes or existing
    worktrees as host-operated tickets. No re-init, branch edits or code writes.
    """
    if pos != ["sequential-host"] or set(opt) - {"no-serve"}:
        die("execution: используй `ap.py execution sequential-host`")
    if state.get("finishedAt"):
        die("execution: завершённый прогон нельзя переключить")
    if state.get("sequentialHost") and state.get("strictRouting") is False:
        return "уже выбран sequential-host; состояние не переинициализировано"
    if state.get("strictRouting") is not True or state.get("sequentialHost"):
        die("execution: переключение поддерживается только из активного strict-routing")
    tickets = state.get("tickets")
    if not isinstance(tickets, list):
        die("execution: повреждён список задач")
    for tk in tickets:
        if (not isinstance(tk, dict) or tk.get("status") != "pending"
                or any(tk.get(k) for k in
                       ("worktree", "routing", "plannedRouting", "commit",
                        "testEvidence", "tests", "startedAt", "finishedAt"))):
            die("execution: нельзя менять режим после маршрутизации или начала задач")
    if any(s.get("id") in ("build", "review", "final") and
           s.get("status") != "pending" for s in state.get("stages", [])):
        die("execution: этап исполнения уже начался")
    if any((e.get("k") == "worktree"
            or (e.get("k") == "plan-models" and e.get("applied") is True)
            or e.get("k") == "ticket")
           for e in state.get("log", [])):
        die("execution: обнаружена история работы исполнителя или модельного маршрута")
    worktree_dir = os.path.join(A, "worktrees")
    if os.path.isdir(worktree_dir) and os.listdir(worktree_dir):
        die("execution: существуют worktrees — сначала разберись с ними")
    state["strictRouting"] = False
    drop_run_record()
    state["sequentialHost"] = True
    state["isolateTickets"] = True
    if isinstance(state.get("waiting"), dict) and state["waiting"].get("kind") == "stop":
        close_wait(state)
    log(state, "execution", mode="sequential-host", previous="strict-routing")
    return ("переключён в sequential-host; план сохранён; один таск за раз. "
            "Перед worktree prepare проверь чистоту Git и подтверждённые тесты")


def cmd_stage(state, pos, opt):
    if not pos:
        die("stage <id> [done|skip|fail] [--note …]")
    sid, action = pos[0], (pos[1] if len(pos) > 1 else "start")
    if sid not in ORDER:
        die("этапы: " + ", ".join(ORDER))
    s = stage(state, sid)
    t = now()
    if action == "start":
        segment_open(s, t)                            # до pop: у старого state.js отрезок берётся из finishedAt
        s["status"] = "active"
        s.setdefault("startedAt", t)
        s.pop("finishedAt", None)
    elif action == "done":
        segment_close(s, t)
        s["status"] = "done"
        s.setdefault("startedAt", t)
        s["finishedAt"] = t
    elif action in ("skip", "fail"):
        if not opt.get("note"):
            die("%s требует --note с причиной" % action)
        segment_close(s, t)
        s["status"] = "skipped" if action == "skip" else "failed"
        s.setdefault("startedAt", t)
        s["finishedAt"] = t
    else:
        die("действие этапа: start | done | skip | fail")
    if isinstance(opt.get("note"), str):
        s["note"] = opt["note"]
    if sid == "spec" and action in ("start", "done"):
        g1 = (state.get("gates") or {}).get("G1")
        if g1:
            g1.pop("reason", None)                    # спецификацию открыли заново — plan-changed снят
        refresh_g1(state, create=True)
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


def commit_descends_from(child_rev, ancestor_rev):
    if not verified_commit(child_rev) or not verified_commit(ancestor_rev):
        return False
    try:
        return subprocess.run(
            ["git", "-C", ROOT, "merge-base", "--is-ancestor",
             ancestor_rev, child_rev], capture_output=True, timeout=10
        ).returncode == 0
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


def _gs():
    """gate_sign is needed only by strict runs; plain harnesses may not ship it."""
    import gate_sign
    return gate_sign


def write_run_record(state):
    """Record outside the project that this run started signed (see gate_sign.record_path)."""
    try:
        _gs().write_run_record(ROOT, state)
    except (ValueError, OSError) as exc:
        die("не удалось записать признак подписанного прогона: %s" % exc)


def drop_run_record():
    """A run that is not strict has nothing to protect; a stale record would read as forged."""
    try:
        _gs().remove_run_record(ROOT)
    except ImportError:  # plain harness without gate_sign: it never wrote a record
        pass
    except OSError as exc:
        die("не удалось убрать признак подписанного прогона: %s" % exc)


def sync_run_record(state):
    """finish/reopen of a signed run update its record; no record (old or moved run) means nothing to do."""
    if state.get("gateMark") is not None and os.path.exists(_gs().record_path(ROOT)):
        write_run_record(state)


def gate_signed(state):
    """True for a run started signed; a forged state (vs the record outside the project) stops, never warns."""
    if state.get("gateMark") is not None and _gs().load_key() is None:
        die(_gs().MISSING_KEY_MESSAGE)
    status = _gs().run_status(state, ROOT)
    if status == "forged":
        die("маркер подписи прогона отсутствует или неверен (state.js правили без ключа); "
            "запусти init заново или восстанови ~/.autopilot/gate.key")
    return status == "signed"


def require_key(state):
    """A signed run never continues without its key and never recreates it silently."""
    if gate_signed(state) and _gs().load_key() is None:
        die(_gs().MISSING_KEY_MESSAGE)


def sign_routing(state, ticket_id, routing):
    if gate_signed(state):
        require_key(state)
        routing["sig"] = _gs().sign(_gs().routing_payload(ticket_id, routing))


def routing_signature_ok(state, tk):
    if not gate_signed(state):
        return True
    require_key(state)
    route = tk.get("routing") or {}
    return _gs().verify(_gs().routing_payload(tk.get("id"), route), route.get("sig"))


def evidence_signature_ok(state, ident, evidence):
    if not gate_signed(state):
        return True
    require_key(state)
    return isinstance(evidence, dict) and _gs().verify(
        _gs().evidence_payload(ident, evidence), evidence.get("sig"))


def verified_host_required(state):
    """Host-side test evidence even without native named-agent routing."""
    return bool(state.get("isolateTickets") and (
        state.get("strictRouting") or state.get("sequentialHost")))


def check_claude_attestation(state, ticket, root):
    """Strict Claude run: hook evidence (claude_attest.py) must show the routed model/effort.

    Returns (ok, message). Not gated (ok) unless strictRouting and an anthropic route.
    On success stores ticket["attestation"] = {"model", "effort", "lines"}.
    """
    route = ticket.get("routing") or {}
    if state.get("strictRouting") is not True or route.get("provider") != "anthropic":
        return True, ""
    agent, model, effort = route.get("agentType"), route.get("model"), route.get("effort")
    if not all(isinstance(x, str) and x for x in (agent, model, effort)):
        return False, "в маршруте нет agentType/model/effort"
    signed = gate_signed(state)
    if signed and _gs().load_key() is None:
        return False, _gs().MISSING_KEY_MESSAGE
    path = os.path.join(root, ".autopilot", "attestations.jsonl")
    if os.path.islink(path) or os.path.islink(os.path.dirname(path)):
        return False, "attestations.jsonl не может быть ссылкой"
    try:
        with open(path, encoding="utf-8") as stream:
            raw = stream.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return False, "нет читаемого .autopilot/attestations.jsonl (%s)" % type(exc).__name__
    if agent in repair_agent_types(state):
        # Shared repair executor: count only lines appended since this ticket's start.
        start = ticket.get("attestFrom")
        if type(start) is not int or start < 0 or start > len(raw):
            return False, "нет отметки начала таска в attestations.jsonl (attestFrom)"
        raw = raw[start:]
    lines = []
    for text in raw:
        try:
            item = json.loads(text)
        except ValueError:
            continue  # a malformed line is not evidence
        if signed and not (isinstance(item, dict) and _gs().verify(item, item.get("sig"))):
            continue  # an unsigned or forged line is not evidence
        if isinstance(item, dict) and item.get("agent_type") == agent:
            lines.append(item)
    if not lines:
        return False, "в attestations.jsonl нет строк агента " + agent

    def fits(name):  # alias ("haiku") matches as substring, a full ID exactly
        return isinstance(name, str) and (name == model if "-" in model else model in name)

    seen = []
    for item in lines:
        used = item.get("models_used")
        if used is not None and not isinstance(used, list):
            return False, "повреждённое поле models_used"
        seen += [item.get("resolved_model")] if item.get("resolved_model") is not None else []
        seen += used or []
    resolved = [x["resolved_model"] for x in lines if fits(x.get("resolved_model"))]
    if not resolved:
        return False, "нет resolved_model, совпадающего с моделью маршрута " + model
    wrong = sorted(set(str(m) for m in seen if not fits(m)))
    if wrong:
        return False, "аттестована чужая модель: " + ", ".join(wrong)
    efforts = [x["effort"] for x in lines if x.get("effort") is not None]
    if route.get("effortEnforced") is not False:  # legacy routes without the flag enforced effort
        if effort not in efforts:
            return False, "нет строки с effort=" + effort
        other = sorted(set(str(e) for e in efforts) - {effort})
        if other:
            return False, "аттестован другой effort: " + ", ".join(other)
    ticket["attestation"] = {"model": resolved[-1],
                             "effort": efforts[-1] if efforts else None,
                             "lines": len(lines)}
    return True, ""


def sequential_occupied(state, ticket_id):
    """Block second prepared/running task in sequential fallback."""
    return any(t.get("id") != ticket_id and (
        t.get("status") in ("in-progress", "review", "repair")
        or (t.get("worktree") or {}).get("status") == "prepared")
        for t in state.get("tickets") or [])


# Fixed router inputs for the run-level Claude roles: reviewer strong (whole-branch
# review), blind acceptance balanced, read-only explorer cheap.
ROLE_SCORES = {
    "reviewer": {"algorithm": 20, "coupling": 0, "uncertainty": 0,
                 "context": 0, "testing": 0, "risk": 0},
    "acceptance": {"algorithm": 5, "coupling": 10, "uncertainty": 0,
                   "context": 10, "testing": 10, "risk": 0},
    "explorer": {"algorithm": 0, "coupling": 0, "uncertainty": 0,
                 "context": 0, "testing": 0, "risk": 0},
}
ROLE_BRIEF = """# Autopilot role agents of this run

One profile per role, shared by the whole run. The orchestrator's launch prompt
names the task, the files to read and the limits; follow it.

- reviewer: point review, repair re-review and whole-branch review. No edits.
- acceptance: blind acceptance against the brief files. No edits.
- explorer: read-only reading tasks (coverage reader, memory and ADR drafts);
  return text, write nothing.
"""
REPAIR_BRIEF = """# Autopilot repair executor of this run

One executor profile for every fix ticket (F1, F2, …) the whole-branch review
creates; registered in Phase 4 because Claude Code sees only agents that existed
at session start. The orchestrator's launch prompt names the fix ticket file:
read it and build exactly that ticket, inside its zone, with its checks.
"""
# Fix tickets are built strong (phases/6-review.md: `Модель: сильная`), like the branch review.
REPAIR_SCORES = ROLE_SCORES["reviewer"]
ACTIVE_EXECUTOR = ("in-progress", "review", "repair")


def repair_agent_type(state):
    entry = state.get("repairAgent")
    return entry.get("agentType") if isinstance(entry, dict) else None


def repair_agent_types(state):
    """Обычный и Opus-ремонтник — один пул: одновременно работает один fix-таск, общий attestations.jsonl."""
    agents = state.get("opusAgents")
    return {a for a in (repair_agent_type(state), agents.get("repair") if isinstance(agents, dict) else None) if a}


OPUS_ROLES = ("repair", "reviewer")
OPUS_USAGE = ("opus propose | opus approve [--tickets 03,05] [--roles repair,reviewer] "
              "--by-user \"<слова пользователя>\" | opus status")


def opus_propose(state):
    """Кандидаты на Opus среди pending-тасков: пометка `Модель: opus` или premium_candidate. Только печать."""
    try:
        import model_router as router
    except ImportError as exc:
        die("opus propose: " + str(exc))
    out = []
    for tk in state.get("tickets") or []:
        if tk.get("status") != "pending":
            continue
        why = []
        mark = (tk.get("model") or "").strip()
        if re.match(r"opus\b", mark, re.I):
            why.append("пометка в файле таска: «%s»" % mark)
        files = ticket_files(state, "%s-*.md" % tk["id"])
        text = ""
        if len(files) == 1:
            try:
                with open(files[0], encoding="utf-8") as stream:
                    text = stream.read()
            except (OSError, UnicodeDecodeError):
                pass
        if text and router.premium_candidate(router.assess_ticket(text)):
            why.append("высокий риск: так оценил планировщик (`**Риск:** высокий`) или так велит зона таска")
        if why:
            out += ["  %s · %s" % (tk["id"], tk.get("title") or ""), "    причина: " + "; ".join(why),
                    "    дороже Sonnet-таска, не измерено"]
    if not out:
        return ["Кандидатов на Opus нет: все таски идут как обычно"]
    return (["Opus можно включить для этих тасков; решает пользователь:"] + out +
            ["Его «да» — `opus approve --tickets <id,…> --by-user \"<его слова>\"`; «нет» — ничего не делать."])


def run_id(state):
    """Прогон, к которому привязаны подписи Opus: `slug|startedAt` (как gate_sign._run_id, его читает guard)."""
    return "%s|%s" % (state.get("slug"), state.get("startedAt"))


def opus_sig_state(state, cur):
    """ok | bad | nokey: сверка `sig` подтверждения {tickets, roles, run} с ключом из ~/.autopilot."""
    try:
        gs = _gs()
    except ImportError:                      # харнесс без gate_sign: сверять нечем
        return "nokey"
    if gs.load_key() is None:
        return "nokey"
    ok = gs.verify({"tickets": cur.get("tickets"), "roles": cur.get("roles"), "run": run_id(state)}, cur.get("sig"))
    return "ok" if ok else "bad"


def opus_profile(state, role):
    """Имя Opus-профиля роли `reviewer`/`repair`, если роль подтверждена, обе подписи верны и профиль есть, иначе None.
    Неверная `sig` останавливает команду (opus_approval); неверная `agentsSig` — просто закрывает Opus, как в guard."""
    cur = opus_approval(state)
    agents = state.get("opusAgents")
    name = agents.get(role) if isinstance(agents, dict) else None
    if role not in (cur.get("roles") or []) or not isinstance(name, str) or not name:
        return None
    if opus_sig_state(state, cur) != "ok":
        return None
    return name if _gs().verify({"opusAgents": agents, "run": run_id(state)}, cur.get("agentsSig")) else None


def opus_repair_entry(name):
    """Запись агента ремонта для Opus-профиля: модель и effort читаются из самого файла профиля."""
    if not name:
        return None
    rel = ".claude/agents/%s.md" % name
    try:
        with open(os.path.join(ROOT, rel), "rb") as stream:
            raw = stream.read()
    except OSError:
        return None
    head = raw.decode("utf-8", "replace").split("\n---", 1)[0]
    fields = dict(re.findall(r"(?m)^(model|effort): (\S+)\s*$", head))
    if "model" not in fields:
        return None
    # effort в файле нет, когда хост его не держит; политика премиума — high
    return {"agentType": name, "agentFile": rel, "model": fields["model"],
            "effort": fields.get("effort", "high"), "effortEnforced": "effort" in fields,
            "profileSha": hashlib.sha256(raw).hexdigest()}


OPUS_REVIEW_DIFF = 3000        # ревью ветки длиннее этого — на Opus-ревьюера, если роль подтверждена


def cmd_agent_for(state, pos, opt):
    """Имя агента, которого звать для `reviewer`/`repair`: Opus-профиль или обычный. Ничего не пишет."""
    if len(pos) != 1 or pos[0] not in OPUS_ROLES:
        die("agent-for reviewer|repair [--diff-lines N]")
    role = pos[0]
    lines = opt.get("diff-lines", 0)
    if not isinstance(lines, str) or not lines.isdigit():
        if "diff-lines" in opt:
            die("agent-for: --diff-lines — число строк диффа")
        lines = 0
    if role == "repair" or int(lines) > OPUS_REVIEW_DIFF:
        name = opus_profile(state, role)
        if name:
            return name
    plain = (state.get("repairAgent") if role == "repair" else (state.get("roleAgents") or {}).get("reviewer"))
    name = plain.get("agentType") if isinstance(plain, dict) else None
    if not name:
        if state.get("strictRouting") is True or state.get("gateMark") is not None:
            die("agent-for: профиль роли %s не зарегистрирован — `plan-models --apply` в строгом Claude-прогоне" % role)
        name = "autopilot-reviewer" if role == "reviewer" else "autopilot-executor"   # обычный прогон: постоянные профили
    return name


def opus_status(state):
    cur = state.get("opusApproval")
    if not isinstance(cur, dict) or not (cur.get("tickets") or cur.get("roles")):
        return ["Opus не включён"]
    verdict = {"ok": "верна", "bad": "НЕ СХОДИТСЯ (state.js правили без ключа или это другой прогон)",
               "nokey": "нет ключа (строгий допуск не примет)"}[opus_sig_state(state, cur)]
    out = ["Opus включён пользователем:",
           "  таски: " + (", ".join(cur.get("tickets") or []) or "—"),
           "  роли: " + (", ".join(cur.get("roles") or []) or "—"),
           "  подпись: " + verdict]
    if isinstance(state.get("opusAgents"), dict):
        out.append("  профили: " + ", ".join("%s=%s" % kv for kv in sorted(state["opusAgents"].items())))
    return out + ["  слова пользователя:"] + ["    %s — «%s»" % (q.get("at"), q.get("quote"))
                                             for q in cur.get("quotes") or []]


def opus_sig(state, tickets, roles):
    """sig, который примет claude_agent_guard.opus_approved: HMAC над {tickets, roles, run}.
    Строгий прогон без ключа — отказ; прогон без ключа — None (guard такое не примет)."""
    strict = state.get("strictRouting") is True or state.get("gateMark") is not None
    try:
        if strict:
            gate_signed(state)               # поддельный state.js и пропавший ключ останавливают
        if _gs().load_key() is not None:
            return _gs().sign({"tickets": tickets, "roles": roles, "run": run_id(state)})
    except ImportError:                      # харнесс без gate_sign: подписывать нечем
        pass
    if strict:
        die("строгий прогон не принимает Opus без подписи: нет ключа ~/.autopilot/gate.key "
            "(или gate_sign.py) — запусти init заново или восстанови ключ")
    return None


def opus_approve(state, opt):
    """Подтверждение пользователя: тексты — его слова (--by-user), ничего сверх них. Расширяет прежнее."""
    raw = opt.get("by-user")
    if not isinstance(raw, str) or not raw.strip():
        die("opus approve требует --by-user \"<слова пользователя>\": Opus включает только он")
    names = {}
    for key in ("tickets", "roles"):
        v = opt.get(key)
        if v is not None and not isinstance(v, str):
            die("opus approve: --%s — список через запятую" % key)
        names[key] = [x.strip() for x in (v or "").split(",") if x.strip()]
    if not names["tickets"] and not names["roles"]:
        die("opus approve требует --tickets 03,05 и/или --roles repair,reviewer")
    known = {t["id"] for t in state.get("tickets") or []}
    unknown = [x for x in names["tickets"] if x not in known]
    if unknown:
        die("opus approve: таска %s нет — сначала `ap.py tickets`" % ", ".join(unknown))
    bad = [x for x in names["roles"] if x not in OPUS_ROLES]
    if bad:
        die("opus approve: роль %s не бывает, допустимы %s" % (", ".join(bad), " и ".join(OPUS_ROLES)))
    quote = clean_quote(raw)
    cur = opus_approval(state)               # прежнее подтверждение сперва проверено: подпись не отмывает правку
    tickets = list(dict.fromkeys(list(cur.get("tickets") or []) + names["tickets"]))
    roles = list(dict.fromkeys(list(cur.get("roles") or []) + names["roles"]))
    state["opusApproval"] = dict(cur, tickets=tickets, roles=roles, sig=opus_sig(state, tickets, roles),
                                 quotes=list(cur.get("quotes") or []) + [{"at": state["updatedAt"], "quote": quote}])
    log(state, "opus-approve", tickets=tickets, roles=roles, quote=quote)
    late = [t["id"] for t in state.get("tickets") or [] if t["id"] in names["tickets"] and t.get("routing")]
    no_agents = ([] if not names["roles"] or isinstance(state.get("opusAgents"), dict) else
                 ["! профилей Opus для ролей нет (opusAgents пуст): они появятся при plan-models --apply, "
                  "а Claude Code увидит их только в новой сессии"])
    return (["Opus подтверждён: таски %s; роли %s" % (", ".join(tickets) or "—", ", ".join(roles) or "—")] +
            ["! таск %s уже получил маршрут: Opus на него не перейдёт (подтверждать надо до plan-models --apply)" % i
             for i in late] + no_agents)


def opus_approval(state):
    """Подтверждение Opus (plan-models и расширение в approve): {} если его нет.
    Неверная подпись (правка state.js, другой прогон) — остановка в любом прогоне, где есть ключ, чтобы
    законный approve не подписал чужую правку; строгий прогон без ключа тоже стоит."""
    cur = state.get("opusApproval")
    if not isinstance(cur, dict) or not (cur.get("tickets") or cur.get("roles")):
        return {}
    verdict = opus_sig_state(state, cur)
    if verdict == "bad" or (verdict == "nokey" and (
            state.get("strictRouting") is True or state.get("gateMark") is not None)):
        die("подпись подтверждения Opus отсутствует или неверна: state.js правили без ключа "
            "или подтверждение из другого прогона")
    return cur


def cmd_plan_models(state, opt):
    """Phase 4: plan all ticket models; --apply atomically installs profiles.

    A strict Claude Code apply also installs the run's reviewer, acceptance and
    explorer profiles: Claude Code loads agents at session start, so every
    profile the build needs must exist before the build session opens.
    """
    if state.get("sequentialHost"):
        die("plan-models: sequential-host не создаёт нативных субагентов")
    provider = opt.get("provider")
    if provider not in ("openai", "anthropic"):
        die("plan-models: требуется --provider openai|anthropic")
    if not state.get("tickets") or any(t.get("status") != "pending" for t in state["tickets"]):
        die("plan-models: сначала опубликуй pending таски через ap.py tickets")
    apply = opt.get("apply") is True
    if opt.get("apply") not in (None, True):
        die("plan-models: --apply не принимает аргумент")
    cap_arg = opt.get("capabilities")
    if apply and not isinstance(cap_arg, str):
        die("plan-models: --apply требует --capabilities из проверенного хоста")
    if apply and (state.get("gates", {}).get("G3", {}).get("ok") is not True
                  or not state.get("planContractDigest")
                  or state["planContractDigest"] != plan_contract_digest(state)
                  or not state.get("planValidationDigest")
                  or state["planValidationDigest"] != plan_validation_digest(state)):
        die("plan-models: --apply требует актуальный успешный ap.py check-plan (G3)")
    policy_arg = opt.get("policy")
    policy_path = None
    policy_relative = None
    policy_sha = None
    if policy_arg is not None:
        if not isinstance(policy_arg, str) or not policy_arg.strip():
            die("plan-models: неверный --policy")
        policy_path = os.path.realpath(os.path.join(ROOT, policy_arg))
        try:
            if os.path.commonpath((policy_path, os.path.realpath(ROOT))) != os.path.realpath(ROOT):
                die("plan-models: policy должна быть внутри проекта")
        except ValueError:
            die("plan-models: недопустимый путь policy")
        if not os.path.isfile(policy_path):
            die("plan-models: файл policy не найден")
        policy_relative = os.path.relpath(policy_path, ROOT).replace(chr(92), "/")
        with open(policy_path, "rb") as stream:
            policy_sha = hashlib.sha256(stream.read()).hexdigest()
    cap_path = os.path.realpath(os.path.join(ROOT, cap_arg)) if isinstance(cap_arg, str) else None
    if cap_path and not os.path.isfile(cap_path):
        die("plan-models: файл capabilities не найден")
    try:
        import model_router as router
        import agent_profiles
        policy = router.load_policy(policy_path)
        caps = router.load_json(cap_path) if cap_path else None
        approval = opus_approval(state)      # {} без подтверждения пользователя: тогда путь прежний
        plans = []
        for tk in state["tickets"]:
            tid = tk["id"]
            candidates = ticket_files(state, "%s-*.md" % tid)
            if len(candidates) != 1:
                die("plan-models: tickets отличаются от опубликованного плана: %s" % tid)
            with open(candidates[0], "rb") as stream:
                raw = stream.read()
            if not state_io.fingerprint_matches(tk.get("fingerprint"), raw):
                die("plan-models: tickets изменены; повтори ap.py tickets и check-plan")
            scores = router.assess_ticket(raw.decode("utf-8"))
            premium = tid in (approval.get("tickets") or [])     # пометка `Модель: opus` без подтверждения не считается
            route = router.choose_route(provider, scores, policy, caps, premium=premium,
                                        note=router.planner_note(raw.decode("utf-8")))
            proposal = {
                "ticket": tid, "provider": provider, "model": route["model"],
                "effort": route["effort"],
                "effortEnforced": route.get("effort_enforced"),
                "profile": route["profile"],
                "score": route["score"], "factors": scores,
                "reason": route["reason"], "requiresReview": route["requires_review"],
                "status": route["status"], "fingerprint": tk["fingerprint"],
                "hostExecutionVerified": False,
            }
            if route["status"] != "ready":
                proposal["error"] = route["error"]
            item = {"ticket": tk, "file": candidates[0], "scores": scores,
                    "route": route, "proposal": proposal, "premium": premium}
            if apply and route["status"] == "ready":
                profile = agent_profiles.prepare(ROOT, candidates[0], provider, cap_path,
                                                 "executor", policy_path, scores, False, premium=premium)
                relative = profile["agent_file"]
                path = os.path.join(ROOT, relative)
                target = os.path.realpath(path)
                if os.path.commonpath((target, os.path.realpath(ROOT))) != os.path.realpath(ROOT):
                    die("plan-models: профиль за пределами проекта")
                if os.path.islink(path) or os.path.islink(os.path.dirname(path)):
                    die("plan-models: ссылки профиля запрещены")
                expected_rel, expected_text = agent_profiles.definition(
                    provider, profile["agent_type"], "executor", route,
                    os.path.relpath(candidates[0], ROOT).replace(chr(92), "/"),
                    raw.decode("utf-8"))
                if expected_rel.as_posix() != relative:
                    die("plan-models: несовместимый профиль")
                if os.path.lexists(path):
                    with open(path, encoding="utf-8") as stream:
                        if stream.read() != expected_text:
                            die("plan-models: профиль существует с другим содержимым")
                item.update(profile=profile, profilePath=path)
            plans.append(item)
        blocked = [p for p in plans if p["route"]["status"] != "ready"]
        if apply and blocked:
            die("plan-models: blocked — " + "; ".join(
                p["ticket"]["id"] + ": " + p["route"]["error"] for p in blocked))
        roles = {}
        claude_roles = apply and provider == "anthropic" and state.get("strictRouting") is True
        if claude_roles:
            for role, scores in ROLE_SCORES.items():
                route = router.choose_route(provider, scores, policy, caps)
                if route["status"] != "ready":
                    die("plan-models: blocked — %s: %s" % (role, route["error"]))
            run_name = re.sub(r"--wip$", "", state["dir"])[:58].rstrip("-")
            role_brief = os.path.join(run_dir(state), "roles", run_name + ".md")
            repair_brief = os.path.join(run_dir(state), "roles",
                                        "repair-" + run_name[:51].rstrip("-") + ".md")
            # Names `autopilot-reviewer-opus-<run>` / `autopilot-executor-repair-opus-<run>`; the slug stays within 58.
            opus_reviewer_brief = os.path.join(run_dir(state), "roles", "opus-" + run_name[:53].rstrip("-") + ".md")
            opus_repair_brief = os.path.join(run_dir(state), "roles",
                                             "repair-opus-" + run_name[:46].rstrip("-") + ".md")
        opus_agents = {}
        if apply:
            created = []
            try:
                for p in plans:
                    existed = os.path.isfile(p["profilePath"])
                    agent_profiles.prepare(ROOT, p["file"], provider, cap_path,
                                           "executor", policy_path, p["scores"], True, premium=p["premium"])
                    if not existed:
                        created.append(p["profilePath"])
                if claude_roles:
                    os.makedirs(os.path.dirname(role_brief), exist_ok=True)
                    with open(role_brief, "w", encoding="utf-8", newline="\n") as stream:
                        stream.write(ROLE_BRIEF)
                    for role, scores in ROLE_SCORES.items():
                        profile = agent_profiles.prepare(ROOT, role_brief, provider, cap_path,
                                                         role, policy_path, scores, True)
                        path = os.path.join(ROOT, profile["agent_file"])
                        if profile["action"] == "created":
                            created.append(path)
                        with open(path, "rb") as stream:
                            digest = hashlib.sha256(stream.read()).hexdigest()
                        roles[role] = {"agentType": profile["agent_type"],
                                       "agentFile": profile["agent_file"],
                                       "model": profile["model"], "effort": profile["effort"],
                                       "effortEnforced": profile["effort_enforced"],
                                       "profileSha": digest}
                    with open(repair_brief, "w", encoding="utf-8", newline="\n") as stream:
                        stream.write(REPAIR_BRIEF)
                    profile = agent_profiles.prepare(ROOT, repair_brief, provider, cap_path,
                                                     "executor", policy_path, REPAIR_SCORES, True)
                    path = os.path.join(ROOT, profile["agent_file"])
                    if profile["action"] == "created":
                        created.append(path)
                    with open(path, "rb") as stream:
                        digest = hashlib.sha256(stream.read()).hexdigest()
                    repair = {"agentType": profile["agent_type"],
                              "agentFile": profile["agent_file"],
                              "model": profile["model"], "effort": profile["effort"],
                              "effortEnforced": profile["effort_enforced"],
                              "profileSha": digest}
                    if policy_relative is not None:
                        repair.update(policyFile=policy_relative, policySha=policy_sha)
                    if approval:
                        # Claude Code sees only agents that existed at session start, so the pinned
                        # opus profiles are made now; the guard admits them only by the signed approval.
                        for key, brief, body, role, scores in (
                                ("reviewer", opus_reviewer_brief, ROLE_BRIEF, "reviewer", ROLE_SCORES["reviewer"]),
                                ("repair", opus_repair_brief, REPAIR_BRIEF, "executor", REPAIR_SCORES)):
                            with open(brief, "w", encoding="utf-8", newline="\n") as stream:
                                stream.write(body)
                            profile = agent_profiles.prepare(ROOT, brief, provider, cap_path, role,
                                                             policy_path, scores, True, premium=True)
                            if profile["action"] == "created":
                                created.append(os.path.join(ROOT, profile["agent_file"]))
                            opus_agents[key] = profile["agent_type"]
            except (OSError, ValueError, TypeError) as exc:
                for path in created:
                    os.unlink(path)
                die("plan-models: создание профилей отменено: " + str(exc))
        for p in plans:
            tk = p["ticket"]
            tk["plannedRouting"] = dict(p["proposal"], applied=apply)
            if apply:
                profile = p["profile"]
                with open(p["profilePath"], "rb") as stream:
                    digest = hashlib.sha256(stream.read()).hexdigest()
                tk["routing"] = {
                    "provider": provider, "model": p["route"]["model"],
                    "effort": p["route"]["effort"],
                    "effortEnforced": p["route"]["effort_enforced"],
                    "score": p["route"]["score"],
                    "reason": p["route"]["reason"], "verified": True,
                    "agentType": profile["agent_type"],
                    "agentFile": profile["agent_file"], "profileSha": digest,
                }
                if policy_relative is not None:
                    tk["routing"].update(policyFile=policy_relative, policySha=policy_sha)
                sign_routing(state, tk["id"], tk["routing"])
        result = {"status": "applied" if apply else "advisory", "provider": provider,
                  "modelCalls": 0, "hostExecutionVerified": False,
                  "tickets": [p["proposal"] for p in plans]}
        if roles:
            state["roleAgents"] = result["roleAgents"] = roles
            state["repairAgent"] = result["repairAgent"] = repair
            if opus_agents:
                state["opusAgents"] = result["opusAgents"] = opus_agents
                # opusAgents is outside `sig`: its own signature, bound to this run; the guard checks it.
                approval["agentsSig"] = _gs().sign(
                    {"opusAgents": opus_agents, "run": run_id(state)}) if _gs().load_key() else None
            # Phase 4 ends here with a new-chat stop: the state must read plan done, build pending.
            cmd_stage(state, ["plan", "done"], {})
        log(state, "plan-models", provider=provider, applied=apply, tickets=len(plans),
            blocked=len(blocked))
        return result
    except (ValueError, OSError, TypeError, ImportError) as exc:
        die("plan-models: " + str(exc))


def cmd_accept_edit(state, ids, opt):
    """Запомнить текущий отпечаток сданного таска как осознанную правку."""
    note = opt.get("note")
    if not isinstance(note, str) or not note.strip():
        die("accept-edit требует --note \"что и почему изменено\"")
    if len(ids) != 1:
        die("ticket NN accept-edit --note \"…\" — один таск")
    tk = next((x for x in state.get("tickets") or [] if x["id"] == ids[0]), None)
    if tk is None:
        die("таска %s нет — сначала `ap.py tickets`" % ids[0])
    if tk.get("status") != "done":
        die("таск %s не сдан: accept-edit только для done" % ids[0])
    files = ticket_files(state, "%s-*.md" % ids[0])
    if len(files) != 1:
        die("файл таска %s не найден или не один" % ids[0])
    with open(files[0], "rb") as stream:
        tk["acceptedFingerprint"] = state_io.ticket_fingerprint(stream.read())
    log(state, "ticket-edit-accepted", id=ids[0], note=note)


def attest_mark():
    """Строк в attestations.jsonl сейчас: общий агент пишет в один файл, доказательства таска — после этой отметки."""
    try:
        with open(os.path.join(ROOT, ".autopilot", "attestations.jsonl"), encoding="utf-8") as stream:
            return len(stream.read().splitlines())
    except FileNotFoundError:
        return 0
    except (OSError, UnicodeDecodeError) as exc:
        die("attestations.jsonl не читается (%s)" % type(exc).__name__)


def escalate_ticket(state, tk, i, cause, attempts, t):
    """Единственная эскалация Haiku -> Sonnet: красные тесты, после первого дозапроса, один раз.

    Новый маршрут — зарегистрированный в фазе 4 Sonnet-исполнитель (`repairAgent`): профиль,
    созданный сейчас, Claude Code в этой сессии не увидел бы. Всё, что не подходит, — отказ."""
    route = tk.get("routing") or {}
    if "haiku" not in str(route.get("model") or "").casefold():
        die("таск %s: --escalate только для таска на Haiku (сейчас: %s)" % (i, route.get("model") or "модель не назначена"))
    import retry_policy
    if not retry_policy.escalation_allowed(route.get("model"), attempts, cause):
        die("таск %s: эскалация возможна только после первого дозапроса красной проверки "
            "(--cause tests, повторов ровно 1; сейчас: причина %s, повторов %s)" % (i, cause, attempts))
    repair = state.get("repairAgent")
    import model_router  # без premium_ok: Opus и Fable сюда не проходят
    if (not isinstance(repair, dict) or "sonnet" not in str(repair.get("model") or "").casefold()
            or not model_router.is_allowed_subagent_model(repair.get("model"))):
        die("таск %s: нет зарегистрированного Sonnet-исполнителя (repairAgent) — нечем эскалировать" % i)
    busy = [x["id"] for x in state.get("tickets") or [] if x.get("id") != i
            and x.get("status") in ACTIVE_EXECUTOR
            and (x.get("routing") or {}).get("agentType") == repair.get("agentType")]
    if busy:
        die("таск %s: Sonnet-исполнитель занят таском %s" % (i, ", ".join(busy)))
    new = dict({k: repair[k] for k in ("agentType", "agentFile", "model", "effort", "effortEnforced",
                                       "profileSha", "policyFile", "policySha") if k in repair},
               provider="anthropic", verified=True,
               reason="эскалация Haiku -> Sonnet: красные тесты после первого дозапроса")
    probe = dict(tk, routing=new)
    if not profile_ok(probe):
        die("таск %s: профиль Sonnet-исполнителя отсутствует или изменён" % i)
    tk["escalatedFrom"] = {"model": route.get("model"), "effort": route.get("effort"),
                           "agentType": route.get("agentType"), "at": t}
    tk["routing"] = new
    sign_routing(state, i, new)
    tk.pop("plannedRouting", None)
    tk["attestFrom"] = attest_mark()
    log(state, "escalate", id=i, **{"from": route.get("model"), "to": new.get("model")})


def route_fields(tk):
    """Класс, модель и усилие таска для строки журнала: из `routing`, иначе из `plannedRouting`."""
    r = tk.get("routing") or tk.get("plannedRouting") or {}
    m = re.search(r"class=([^;]+)", str(r.get("reason") or ""))
    return {"class": m.group(1).strip() if m else None, "model": r.get("model"), "effort": r.get("effort")}


def cmd_ticket(state, pos, opt):
    if "accept-edit" in pos:
        return cmd_accept_edit(state, [p for p in pos if p != "accept-edit"], opt)
    if "land" in pos:
        return cmd_land(state, [p for p in pos if p != "land"], opt)
    if "redproof" in pos or "baseline" in pos:
        return cmd_proof(state, pos, opt)
    acts =[p for p in pos if p in TICKET_STATUSES]
    ids = [p for p in pos if p not in TICKET_STATUSES]
    if len(acts) != 1 or not ids:
        die("ticket <id…> start|review|repair|done|fail|retry|reset")
    act = acts[0]
    if opt.get("escalate") and act != "retry":
        die("--escalate работает только с `ticket NN retry --cause tests`")
    known = {t["id"]: t for t in state.get("tickets") or []}
    t = now()
    for i in ids:
        tk = known.get(i)
        if tk is None:
            die("таска %s нет — сначала `ap.py tickets`" % i)
        if opt.get("escalate") and tk.get("escalatedFrom"):
            die("таск %s: уже эскалирован с Haiku на Sonnet — вторая эскалация не допускается; "
                "`ticket %s fail --note \"что блокирует\"` и вопрос пользователю" % (i, i))
        quote = None
        if act == "reset" and tk.get("status") == "failed":
            quote = opt.get("by-user")
            if not isinstance(quote, str) or not quote.strip():
                die("таск %s упал — дальше решает пользователь: спроси его и, если он велел "
                    "продолжать, повтори `ticket %s reset --by-user \"<его слова>\"`" % (i, i))
            quote = clean_quote(quote)
        if state.get("sequentialHost") and act == "route":
            die("таск %s: sequential-host не создаёт и не запускает нативных субагентов" % i)
        if state.get("sequentialHost") and act in ("start", "retry") and sequential_occupied(state, i):
            die("таск %s: sequential-host допускает только один активный таск" % i)
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
        shared = repair_agent_types(state)
        on_repair = (tk.get("routing") or {}).get("agentType") in shared
        if act in ("start", "retry") and on_repair:
            busy = [x["id"] for x in state.get("tickets") or [] if x.get("id") != i
                    and x.get("status") in ACTIVE_EXECUTOR
                    and (x.get("routing") or {}).get("agentType") in shared]
            if busy:
                die("таск %s: агент ремонта занят таском %s" % (i, ", ".join(busy)))
        if act == "start" and on_repair:
            # The agent is shared: only evidence appended after this start is this ticket's.
            tk["attestFrom"] = attest_mark()
        if act == "done" and (state.get("strictRouting") or state.get("gateMark")) and (
                not gate_signed(state)):
            print("предупреждение: прогон без подписи гейтов (начат до подписи); "
                  "маршрут, аттестации и тесты не защищены ключом")
        if act == "done" and (state.get("strictRouting") or state.get("gateMark")) and (
                not routing_signature_ok(state, tk)):
            die("таск %s: подпись маршрута отсутствует или неверна" % i)
        if act == "done" and verified_host_required(state):
            if not evidence_signature_ok(state, i, tk.get("testEvidence")):
                die("таск %s: подпись результатов тестов отсутствует или неверна" % i)
            recorded = tk.get("tests")
            evidence = tk.get("testEvidence")
            if (not isinstance(evidence, dict) or evidence.get("status") != "verified"
                    or recorded != {"passed": evidence.get("passed"), "failed": 0}):
                die("таск %s: строгий режим требует результатов тестов, проверенных на хосте" % i)
            if opt.get("tests") and tests_pair(opt["tests"]) != recorded:
                die("таск %s: переданные тесты не совпадают с проверенными" % i)
        if act == "done":
            pending_blockers = [b["id"] for b in blocker_ledger(state)
                                if b["status"] == "open" and b.get("ticket") == i]
            if pending_blockers:
                die("таск %s: не закрыты блокирующие замечания %s" %
                    (i, ", ".join(pending_blockers)))
            validation = tests_pair(opt["tests"]) if opt.get("tests") else tk.get("tests")
            repro_done = kinds_of(state) == "bug" and tk.get("repro") and tk.get("redproof")   # красный тест — цель
            if not repro_done and (not validation or validation["passed"] < 1 or validation["failed"] != 0):
                die("таск %s: нельзя принять без успешных тестов" % i)
            rev = opt.get("commit") or tk.get("commit")
            if not rev:
                die("таск %s: нет --commit и записанного коммита. Если git отказал в коммите — "
                    "это сбой машины, не ремонт: `ticket %s fail --note \"что отказал git\"` "
                    "и вопрос пользователю" % (i, i))
            if not verified_commit(rev):
                die("таск %s: требуется существующий коммит в HEAD" % i)
            resolved = [b for b in blocker_ledger(state)
                        if b.get("ticket") == i and b["status"] == "resolved"]
            if any(not commit_descends_from(rev, b.get("resolutionCommit"))
                   for b in resolved):
                die("таск %s: коммит сдачи не включает проверенное исправление блокера" % i)
            ok, why = check_claude_attestation(state, tk, ROOT)
            if not ok:
                print("ошибка: таск %s: строгий Claude-прогон требует аттестации — %s" % (i, why))
                sys.exit(2)
        if act == "retry" and state.get("isolateTickets") and not tk.get("worktree"):
            die("таск %s: сначала подготовь worktree для повтора" % i)
        if act in ("retry", "repair"):
            attempts = tk.get("retries", 0)
            repairs = tk.get("repairs", 0)
            if (act == "retry" and attempts >= 2) or (act == "repair" and repairs >= 2):
                die("таск %s: предел повторов/ремонтов достигнут (2). Не ходи по кругу: "
                    "`ticket %s fail --note \"что блокирует\"` и вопрос пользователю" % (i, i))
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
                if opt.get("escalate"):
                    escalate_ticket(state, tk, i, kind, attempts, t)
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
            repair = state.get("repairAgent")
            if (provider == "anthropic" and state.get("strictRouting") is True
                    and re.fullmatch(r"F\d+", i) and isinstance(repair, dict)):
                # A profile created now is invisible to this Claude session (T17):
                # fix tickets go to the repair executor registered in Phase 4
                # (the opus one when the user approved role `repair`: signed, profile present).
                repair = opus_repair_entry(opus_profile(state, "repair")) or repair
                if not isinstance(reason, str) or not reason.strip():
                    die("route требует --reason")
                if model not in (None, repair.get("model")) or effort not in (None, repair.get("effort")):
                    die("route: таск %s идёт на агента ремонта (%s/%s)" %
                        (i, repair.get("model"), repair.get("effort")))
                if len(ticket_files(state, "%s-*.md" % i)) != 1:
                    die("route: не удалось однозначно найти файл таска %s" % i)
                tk["routing"] = dict({k: repair[k] for k in (
                    "agentType", "agentFile", "model", "effort", "effortEnforced",
                    "profileSha", "policyFile", "policySha") if k in repair},
                    provider="anthropic", reason=reason, verified=True)
                sign_routing(state, i, tk["routing"])
                if not profile_ok(tk):
                    die("route: профиль агента ремонта отсутствует или изменён")
                tk.pop("plannedRouting", None)
                continue
            if not state.get("strictRouting") and re.fullmatch(r"F\d+", i) and provider in (None, "anthropic"):
                # Fix-таск обычного прогона: профиль, созданный сейчас, этой сессии не виден, поэтому маршрут
                # только записывается (модель берётся параметром вызова), без файла профиля и подписи.
                import model_router
                if not all(isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}", x.strip())
                           for x in (model, effort)) or not (isinstance(reason, str) and reason.strip()):
                    die("route: fix-таск %s требует --model --effort --reason" % i)
                if not model_router.is_allowed_subagent_model(
                        model, premium_ok=i in (opus_approval(state).get("tickets") or [])):
                    die("route: модель %s не допускается: Haiku и Sonnet без условий, Opus только по подтверждению "
                        "пользователя, Fable никогда" % model)
                tk["routing"] = {"provider": "anthropic", "model": model.strip(), "effort": effort.strip(),
                                 "reason": reason.strip()}
                continue
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
                candidates = ticket_files(state, "%s-*.md" % i)
                if len(candidates) != 1:
                    die("route: не удалось однозначно найти файл таска %s" % i)
                source = open(candidates[0], encoding="utf-8").read()
                scores = json.loads(opt["scores"]) if opt.get("scores") else router.assess_ticket(source)
                route = router.choose_route(
                    provider, scores, policy=router.load_policy(policy_path),
                    capabilities=router.load_json(cap), note=router.planner_note(source))
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
                             "effort": effort,
                             "effortEnforced": route["effort_enforced"],
                             "score": route["score"],
                             "reason": reason, "verified": True,
                             "agentType": profile["agent_type"],
                             "agentFile": filename, "profileSha": digest}
            # `routing` is authoritative; a Phase-4 advisory beside it only misleads (T16).
            tk.pop("plannedRouting", None)
            if policy_relative is not None:
                tk["routing"].update(policyFile=policy_relative,
                                     policySha=policy_digest)
            sign_routing(state, i, tk["routing"])
            continue
        tk["status"] = TICKET_STATUSES[act]
        if act == "start":
            tk.setdefault("startedAt", t)
            tk.pop("finishedAt", None)
            try:
                import land_check
                tk["startHead"] = land_check.head(ROOT)
            except ImportError:
                pass
        elif act == "retry":
            tk["retries"] = tk.get("retries", 0) + 1
            tk["startedAt"] = tk.get("startedAt") or t
        elif act == "repair":
            note = opt.get("note")
            if not isinstance(note, str) or not note.strip():
                die("таск %s: repair требует текст блокирующего условия --note" % i)
            tk["repairs"] = tk.get("repairs", 0) + 1
            tk.setdefault("repairFindings", []).append(note)
            open_blocker(state, note, tk)
        elif act in ("done", "fail"):
            tk.setdefault("startedAt", t)
            tk["finishedAt"] = t
            if act == "fail" and isinstance(opt.get("note"), str):
                tk.setdefault("concerns", []).append(opt["note"])
        elif act == "reset":
            for k in ("startedAt", "finishedAt"):
                tk.pop(k, None)
            if quote:                                 # упавший таск вернул пользователь
                tk.setdefault("reopenedByUser", []).append(quote)
                tk["repairs"] = tk["retries"] = 0
            log(state, "ticket-reset", id=i, reason="by-user" if quote else "manual", quote=quote)
        if act == "done":
            close_requirements(state, tk, opt, t)
        if opt.get("tests"):
            tk["tests"] = tests_pair(opt["tests"])
            state["tests"] = tk["tests"]
        if isinstance(opt.get("commit"), str):
            tk["commit"] = opt["commit"][:12]
    pair = tests_pair(opt["tests"]) if opt.get("tests") else None
    cause = opt.get("cause") if isinstance(opt.get("cause"), str) and re.fullmatch(
        r"[a-z0-9][a-z0-9-]{0,39}", opt["cause"]) else ("tests-failed" if pair and pair["failed"] else None)
    routes = {i: route_fields(known[i]) for i in ids} if act == "start" else {}
    log(state, "ticket", ids=ids, act=act, tests=pair, journal={"cause": cause, "routes": routes},
        note=opt["note"] if act in ("repair", "fail") and isinstance(opt.get("note"), str) else None)


# ── chore и ticket land: команды из interfaces.md, коммит только названных путей ──

def interfaces_text(state):
    try:
        with open(os.path.join(A, state.get("dir") or "", "interfaces.md"), encoding="utf-8-sig") as f:
            return f.read()
    except OSError:
        return ""


def full_check_command(state):
    """Команда из строки «Полная проверка: `…`» в interfaces.md прогона; нет строки — None."""
    m = re.search(r"(?m)^[ \t>*-]*Полная проверка:[ \t]*`([^`\n]+)`", interfaces_text(state))
    return m.group(1).strip() if m else None


def generators(state):
    """Таблица «Имя | Команда | Файлы» раздела «Команды-генераторы» → {имя: (команда, [файлы])}."""
    found, inside = {}, False
    for line in interfaces_text(state).splitlines():
        if line.startswith("#"):
            inside = line.lstrip("# ").strip().lower().startswith("команды-генераторы")
            continue
        if not inside or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) < 3 or cells[0].lower() == "имя" or set(cells[0]) <= set("-: "):
            continue
        files = [f.strip().strip("`").strip().replace("\\", "/") for f in cells[2].split(",")]
        found[cells[0].strip("`").strip()] = (cells[1].strip("`").strip(), [f for f in files if f])
    return found


def covers(paths, path):
    return any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") for p in paths)


def porcelain():
    """{путь: (XY, sha256 содержимого)} по `git status --porcelain`; None — git не ответил."""
    try:
        r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                           capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode:
        return None
    found, parts, n = {}, r.stdout.decode("utf-8", "replace").split("\0"), 0
    while n < len(parts):
        entry = parts[n]
        n += 1
        if len(entry) < 4:
            continue
        if entry[0] in "RC":
            n += 1                                    # следом идёт прежний путь
        try:
            with open(os.path.join(ROOT, entry[3:]), "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            digest = None
        found[entry[3:]] = (entry[:2], digest)
    return found


def run_shell(command, timeout):
    """→ (код, вывод); код None — таймаут (потомки убиты). Оболочка системы."""
    import process_containment
    try:
        r = process_containment.run_contained("cmd /c " + command if WIN else ["sh", "-c", command],
                                              timeout=timeout, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return None, ""
    except OSError as exc:
        return 127, str(exc)
    return r.returncode, (r.stdout or "") + "\n" + (r.stderr or "")


def count_tests(text):
    """Вывод проверки (unittest, cargo, pytest) → (прошло, упало); формат не узнан — None."""
    ran = re.findall(r"^Ran (\d+) tests? in", text, re.M)
    if ran:
        tail = text[text.rfind("Ran " + ran[-1]):]
        n = lambda key: sum(int(x) for x in re.findall(key + r"=(\d+)", tail))
        failed = n("failures") + n("errors")
        return int(ran[-1]) - failed - n("skipped"), failed
    cargo = re.findall(r"^test result: \w+\. (\d+) passed; (\d+) failed", text, re.M)
    if cargo:
        return sum(int(p) for p, _ in cargo), sum(int(f) for _, f in cargo)
    for line in reversed(text.splitlines()):
        if re.search(r"\b(?:passed|failed|errors?)\b", line) and re.search(r"\bin [\d.]+s", line):
            n = lambda word: sum(int(x) for x in re.findall(r"(\d+) " + word, line))
            return n("passed"), n("failed") + n("errors?")
    return None


def last_line(text):
    return next((x.strip()[:200] for x in reversed(text.splitlines()) if x.strip()), "")


def commit_paths(paths, message, trailers):
    """Единственное место, где ap.py коммитит: `git commit --only -- <пути>` с трейлерами → короткий SHA.
    Без `git add -A` и `git stash`; сбой git — OSError с его последней строкой; нечего коммитить — None."""
    def git(*args):
        r = subprocess.run(["git", "--literal-pathspecs", "-C", ROOT] + list(args), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        if r.returncode:
            raise OSError(last_line(r.stderr or r.stdout) or "git вернул код %d" % r.returncode)
        return r.stdout.strip()
    git("add", "--", *paths)
    if subprocess.run(["git", "--literal-pathspecs", "-C", ROOT, "diff", "--cached", "--quiet", "--"] + list(paths)).returncode == 0:
        return None                                   # после нормализации концов строк менять нечего
    git("commit", "-q", "--only", "-m", message, *["--trailer=" + t for t in trailers], "--", *paths)
    return git("rev-parse", "--short", "HEAD")


def cmd_chore(state, pos):
    """`chore <имя>`: объявленный генератор → коммит только его файлов. Код 0 — закоммичено или нечего;
    2 — отказ, коммита нет."""
    def refuse(*lines):
        print("\n".join("chore: " + x for x in lines))
        return 2
    known = generators(state)
    if len(pos) != 1 or pos[0] not in known:
        return refuse("нет генератора %s в разделе «Команды-генераторы» interfaces.md (есть: %s)"
                      % (" ".join(pos) or "—", ", ".join(known) or "ни одного"))
    name = pos[0]
    command, declared = known[name]
    before = porcelain()
    if before is None:
        return refuse("git не отвечает — коммита нет")
    dirty = [p for p in before if covers(declared, p)]
    if dirty:
        return refuse("%s: файлы генератора грязные до запуска (%s) — закоммить или убери, коммита нет"
                      % (name, ", ".join(dirty[:3])))
    code, out = run_shell(command, 600)
    if code is None:
        return refuse("%s: таймаут 600 с, коммита нет" % name)
    if code:
        return refuse("%s: команда вернула код %d, коммита нет" % (name, code), last_line(out))
    after = porcelain()
    if after is None:
        return refuse("git не отвечает — коммита нет")
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    extra = [p for p in changed if not covers(declared, p)]
    if extra:
        return refuse("%s: изменено лишнее — %s%s, коммита нет" % (
            name, ", ".join(extra[:3]), " и ещё %d" % (len(extra) - 3) if len(extra) > 3 else ""),
            "верни эти файлы и поправь «Файлы» генератора в interfaces.md")
    if not changed:
        print("chore %s: нечего коммитить — объявленные файлы не изменились" % name)
        return 0
    try:
        sha = commit_paths(changed, "chore: " + name, ["Autopilot-Run: " + run_key(state.get("dir"))])
    except OSError as exc:
        return refuse("%s: коммит не удался (%s)" % (name, exc))
    if sha is None:
        print("chore %s: нечего коммитить — объявленные файлы не изменились" % name)
        return 0
    print("chore %s: закоммичено %s, файлов %d" % (name, sha, len(changed)))
    return 0


def kinds_of(state):
    import kinds
    return kinds.of_state(state)


def cmd_proof(state, pos, opt):
    """`ticket NN redproof --command "…"` (bug: код ≠ 0) и `ticket NN baseline --command "…"` (refactor: код 0)."""
    act = "redproof" if "redproof" in pos else "baseline"
    ids = [p for p in pos if p != act]
    command = opt.get("command")
    if len(ids) != 1 or not isinstance(command, str) or not command.strip():
        die('ticket NN %s --command "<команда тестов>"' % act)
    tk = next((x for x in state.get("tickets") or [] if x["id"] == ids[0]), None)
    if tk is None:
        die("таска %s нет — сначала `ap.py tickets`" % ids[0])
    kind = kinds_of(state)
    if kind != ("bug" if act == "redproof" else "refactor"):
        die("%s работает только в сборке вида %s (сейчас %s)" % (act, "bug" if act == "redproof" else "refactor", kind))
    code, out = run_shell(command, 1800)
    if code is None:
        die("%s: таймаут 1800 с" % act)
    # shortcut: режем синтаксис, «команда не найдена», 126/127 и ноль тестов; ImportError законен (тест на ненаписанный код)
    if act == "redproof" and code != 0 and (code in (126, 127, 9009) or re.search(
            r"(?m:^\s*(?:SyntaxError|IndentationError)\b)|command not found|is not recognized|Ran 0 tests|no tests ran|collected 0 items", out)):
        die("redproof: тест не по-настоящему красный: %s" % last_line(out))
    if (act == "redproof") == (code == 0):
        die("redproof: тест не красный (код 0)" if act == "redproof" else
            "baseline: тесты красные до правок (код %d): %s" % (code, last_line(out)))
    tk[act] = {"command": command.strip(), "exit": code, "at": now()}
    log(state, "ticket-" + act, id=ids[0], code=code)
    return "таск %s: %s записан (код %d)" % (ids[0], act, code)


def split_paths(value):
    return [x.strip().replace("\\", "/") for x in re.split(r"[,;]", value) if x.strip()] if isinstance(value, str) else []


def review_signals(files, status):
    """Сигналы обхода (skip, xfail, --no-verify, удалённые assert) по диффу таска; только печать."""
    import review_checks
    import land_check
    untracked = [f for f in files if status.get(f, ("", ""))[0].strip() == "??"]
    return review_checks.bypass_lines(land_check.diff_text(ROOT, files, untracked))


def cmd_land(state, pos, opt):
    """`ticket NN land --message "…" [--zone a,b] [--requirements R01,R02] [--allow пути]`: вне зоны → полная
    проверка → коммит зоны с трейлерами → `ticket NN done`. Красный шаг — 1–3 строки, код 2, коммита нет."""
    if len(pos) != 1:
        die('ticket NN land --message "…" [--zone a,b] [--requirements R01,R02]')
    i = pos[0]
    tk = next((x for x in state.get("tickets") or [] if x["id"] == i), None)
    if tk is None:
        die("таска %s нет — сначала `ap.py tickets`" % i)
    message = opt.get("message")
    if not isinstance(message, str) or not message.strip():
        die('land: нужен --message "T%s: что сделано"' % i)

    def red(step, why, hint=None):
        print("land %s: стоп на шаге «%s» — %s" % (i, step, why))
        if hint:
            print("  " + hint)
        sys.exit(2)
    if state.get("isolateTickets") or tk.get("worktree"):
        red("режим", "изолированный прогон", "прежним путём: worktree %s verify → finalize → land, затем ticket %s done" % (i, i))
    if tk.get("status") == "done":
        red("таск", "уже сдан")
    by_id = {x["id"]: x for x in state.get("tickets") or []}
    waiting = [d for d in tk.get("blockedBy", []) if by_id.get(d, {}).get("status") != "done"]
    if waiting or any(b["status"] == "open" and b.get("ticket") == i for b in blocker_ledger(state)):
        red("таск", "не готовы зависимости или есть открытые блокеры", "заверши их: " + ", ".join(waiting or [i]))
    zone = split_paths(opt.get("zone")) or [z.replace("\\", "/") for z in tk.get("zone") or []]
    if not zone:
        red("зона", "у таска нет зоны", "дай --zone путь1,путь2")
    reqs = ", ".join(re.findall(r"[RGD]\d+[a-z]?(?:\.\d+)?", str(opt.get("requirements") or "")) or tk.get("requirements") or [])
    import kinds
    import land_check
    kind = kinds.of_state(state)
    repro = kind == "bug" and bool(tk.get("repro"))            # красный тест вливается без полной проверки
    check = full_check_command(state)
    if not check and not repro:
        red("проверка", "в interfaces.md нет строки «Полная проверка: `команда`»", "впиши её и повтори")
    include = split_paths(opt.get("include"))
    flying = [z for x in state.get("tickets") or [] if x["id"] != i and x.get("status") in ACTIVE_EXECUTOR
              for z in x.get("zone") or []]
    allowed = [".autopilot", ".env.example"] + flying + split_paths(opt.get("allow")) + include
    status = porcelain()
    if status is None:
        red("вне зоны", "git не отвечает")
    outside = [p for p in status if not covers(zone, p) and not covers(allowed, p)]
    if outside:
        red("вне зоны", "изменено %s%s" % (", ".join(outside[:3]), " и ещё %d" % (len(outside) - 3) if len(outside) > 3 else ""),
            "верни файл или назови причину (--allow путь — если он не от таска; --include путь — влить в коммит)")
    files = sorted(p for p in status if covers(zone, p) or p == ".env.example" or covers(include, p))
    active = {x["id"]: x.get("zone") or [] for x in state.get("tickets") or [] if x["id"] != i and x.get("status") in ACTIVE_EXECUTOR}
    report = land_check.preflight(ROOT, tk.get("startHead"), state.get("baseCommit") or tk.get("startHead"), zone, i, active, files)
    if report["unsupported"]:
        print("land %s: предупреждение — %s" % (i, report["unsupported"]))
    bad = land_check.problems(report, i)
    if bad:
        red("пересечения", bad[0], bad[1] if len(bad) > 1 else None)
    tests = {f for f in land_check.tracked_files(ROOT) if kinds.is_test_path(f)} if kind == "refactor" else set()
    kind_bad = kinds.land_problems(kind, tk, files, tests, tk.get("redproof"), state.get("tickets") or [])
    quote = clean_quote(opt.get("by-user")) if kind == "bug" else None
    if kind_bad and (not quote or repro):                      # красный тест слово пользователя не снимает
        red("вид «%s»" % kind, kind_bad[0], kind_bad[1] if len(kind_bad) > 1 else None)
    if kind_bad:
        tk.setdefault("concerns", []).append("land по слову пользователя вопреки виду bug: " + quote)
        log(state, "land-by-user", id=i, quote=quote)
    code, out = (0, "") if repro else run_shell(check, 1800)
    if code is None:
        red("проверка", "таймаут 1800 с")
    counts = (0, 0) if repro else count_tests(out)
    if code:
        tk["lastCheck"] = "\n".join(out.strip().splitlines()[-30:])[-3000:]      # хвост для `ticket NN bundle`
        save(state)
        red("проверка", "красная: код %d%s" % (code, ", упало %d" % counts[1] if counts else ""), last_line(out))
    tk.pop("lastCheck", None)
    if counts is None:
        red("проверка", "не смог посчитать тесты: вывод не unittest, pytest или cargo", "отдельно: ticket %s done --tests N/0 --commit SHA" % i)
    passed, failed = counts
    if not repro and (passed < 1 or failed):
        red("проверка", "ноль тестов" if passed < 1 else "упало %d" % failed)
    if not files:
        red("коммит", "в зоне нечего коммитить")
    for line in review_signals(files, status)[:3]:
        print("land %s: сигнал обхода — %s" % (i, line))
    try:
        sha = commit_paths(files, message.strip(), ["Autopilot-Run: " + run_key(state.get("dir")), "Requirements: " + reqs])
    except OSError as exc:
        red("коммит", "git отказал (%s)" % exc, "сбой машины, не кода: ticket %s fail --note \"git отказал\" и вопрос пользователю" % i)
    if sha is None:
        red("коммит", "в зоне нечего коммитить")
    done = {"commit": sha} if repro else {"tests": "%d/%d" % (passed, failed), "commit": sha}
    if isinstance(opt.get("placeholder"), str):
        done["placeholder"] = opt["placeholder"]
    try:
        cmd_ticket(state, [i, "done"], done)
    except SystemExit:
        tests_arg = " --tests %s" % done["tests"] if "tests" in done else ""    # у воспроизводящего таска тестов нет
        print("land %s: коммит %s сделан, но `ticket done` отказал — после исправления: ticket %s done%s --commit %s"
              % (i, sha, i, tests_arg, sha))
        raise
    if repro:
        return "таск %s посажен: коммит %s (красный тест, полная проверка не гонялась), файлов %d" % (i, sha, len(files))
    ahead = " · цель ушла на %d коммит." % report["ahead"] if report["ahead"] else ""
    return "таск %s посажен: коммит %s, тестов %d/0, файлов %d%s" % (i, sha, passed, len(files), ahead)


def cmd_bundle(state, pos):
    """`ticket NN bundle`: одно сообщение исполнителю — хвост упавшей проверки, открытые блокеры, замечания таска."""
    if len(pos) != 1:
        die("ticket NN bundle")
    tk = next((x for x in state.get("tickets") or [] if x["id"] == pos[0]), None)
    if tk is None:
        die("таск %s: нет" % pos[0])
    blockers = [b for b in blocker_ledger(state) if b["status"] == "open" and b.get("ticket") == tk["id"]]
    notes = [str(c) for c in tk.get("concerns") or []] + [str(c) for c in tk.get("repairFindings") or []]
    out = ["таск %s — сводка для исполнителя" % tk["id"], "", "Проверка:",
           tk.get("lastCheck") or "  нет упавшей проверки", "", "Открытые блокеры:"]
    out += ["  %s %s" % (b["id"], b["text"]) for b in blockers] or ["  нет"]
    out += ["", "Замечания таска:"] + (["  - " + n for n in notes] or ["  нет"])
    return "\n".join(out)


def cmd_silence(opt):
    """`silence [--limit СЕК] [--transcript ПУТЬ]`: тихие агенты → код 3; агента не останавливает."""
    import silence
    try:
        limit = int(opt["limit"]) if opt.get("limit") else silence.limit_from_env()
    except ValueError:
        die("silence: --limit — число секунд")
    path = opt["transcript"] if isinstance(opt.get("transcript"), str) else session_transcript()
    if not path:
        print("тишина: журнал не найден (путь задаёт --transcript)")
        return 1
    if not os.path.exists(path):
        print("тишина: журнал не найден: %s" % path)
        return 1
    quiet = silence.silent_agents(os.path.splitext(path)[0] + os.sep + "subagents", limit)
    for q in quiet:
        print("тихий агент %s: %d с без вывода (срок %d) — останови его TaskStop и пересоздай таск" % (q["file"], q["idle"], limit))
    if not quiet:
        print("тишина: все агенты подают признаки жизни (срок %d с)" % limit)
    return 3 if quiet else 0


def lessons_path():
    return os.path.join(A, "lessons.md")


def cmd_lessons(state, pos, opt):
    """`lessons candidates|add|show|drop|check` — только `.autopilot/lessons.md` (и `.seen` рядом)."""
    import lessons
    act, args = (pos[0] if pos else ""), pos[1:]
    path = lessons_path()
    if act == "candidates":
        try:
            n = int(opt.get("max", lessons.DEFAULT_MAX))
        except ValueError:
            die("lessons candidates: --max — число")
        print("\n".join("- " + c for c in lessons.candidates(state, n)) or "кандидатов нет")
        return 0
    if act == "add" and args:
        refused = lessons.add(path, args, int(opt["max"]) if str(opt.get("max", "")).isdigit() else lessons.DEFAULT_MAX)
        print("\n".join("отказ — " + r for r in refused) or "уроки записаны: .autopilot/lessons.md")
        return 1 if refused else 0
    if act == "show":
        print(lessons.render(path) or "уроков нет")
        return 0
    if act == "drop" and len(args) == 1 and args[0].isdigit():
        ok = lessons.drop(path, int(args[0]))
        print("урок удалён" if ok else "нет урока с таким номером")
        return 0 if ok else 1
    if act == "check":
        bad = []
        try:
            with open(path, encoding="utf-8") as f:
                bad = [(i, lessons.check_text(x.rstrip("\n"))) for i, x in enumerate(f, 1)]
        except OSError:
            pass
        bad = [(i, why) for i, why in bad if why]
        print("\n".join("строка %d: %s" % b for b in bad) or "уроки чистые")
        return 1 if bad else 0
    die("lessons candidates [--max N] | add \"текст\" … | show | drop N | check")


def cmd_profile(state, pos):
    import lessons
    if pos != ["refresh"]:
        die("profile refresh")
    try:
        changed = lessons.refresh_profile(ROOT, full_check_command(state))
    except OSError as exc:
        die("profile: не записан (%s)" % type(exc).__name__)
    print("профиль: записан .autopilot/profile.md" if changed else "профиль: без изменений")


def lessons_note():
    """Строка для `init`: сколько строк в уроках, если файл не пуст."""
    try:
        with open(lessons_path(), encoding="utf-8") as f:
            n = sum(1 for x in f if x.startswith("- "))
    except OSError:
        return None
    return "уроки: %d строк (.autopilot/lessons.md, читать вместе с profile.md)" % n if n else None


def cmd_worktree(state, pos, opt):
    """Plan-aware, explicit isolation lifecycle; no automatic agent spawning."""
    if len(pos) != 2 or pos[1] not in ("prepare", "status", "verify", "finalize", "land", "release", "recover"):
        die("worktree <ticket-id> prepare|status|verify|finalize|land|release|recover [--tests N/0]; verify --suite test.py|cargo:name")
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
            if verified_host_required(state):
                import test_evidence
                evidence = tk.get("testEvidence")
                if record.get("sourceCommit") == recovered["sourceCommit"]:
                    if not evidence or evidence.get("status") != "verified":
                        die("worktree: отсутствует подтверждение тестов после финализации")
                    if not evidence_signature_ok(state, ident, evidence):
                        die("worktree: подпись результатов тестов отсутствует или неверна")
                    check = {"passed": evidence["passed"], "failed": evidence["failed"]}
                else:
                    check = test_evidence.check(ROOT, ident, record["baseCommit"], evidence,
                                                gate_signed(state))
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
            if state.get("sequentialHost") and sequential_occupied(state, ident):
                die("worktree: sequential-host допускает только один подготовленный/активный таск")
            if tk.get("worktree"):
                die("worktree: для %s уже существует запись, проверь status" % ident)
            result = worktrees.create(ROOT, ident)
            tk["worktree"] = {"status": "prepared", "baseCommit": result["baseCommit"],
                              "cwd": result["cwd"]}
            log(state, "worktree", act="prepare", ticket=ident)
            try:
                deps = worktrees.link_deps(ROOT, result["cwd"])
            except Exception as exc:                  # копия зависимостей — удобство, prepare она не роняет
                deps = "skipped: %s" % type(exc).__name__
            return "worktree %s подготовлен: %s · зависимости: %s" % (ident, result["cwd"], deps)
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
            require_key(state)
            started = time.monotonic()
            result = test_evidence.verify(ROOT, ident, record["baseCommit"], suite,
                                          int(timeout), sign=gate_signed(state))
            seconds = round(time.monotonic() - started, 1)
            tk["testEvidence"] = result
            check = {"passed": result["passed"], "failed": 0}
            tk["tests"] = check
            state["tests"] = check
            log(state, "worktree", act="verify", ticket=ident,
                tests=result["passed"], suite=result["suite"], journal={"seconds": seconds})
            return "worktree %s: %d/%d тестов подтверждено на хосте" % (
                ident, result["passed"], result["failed"])
        if action == "finalize":
            record = tk.get("worktree") or {}
            if (record.get("status") != "prepared" or
                    tk.get("status") not in ("in-progress", "review", "repair")):
                die("worktree: для финализации требуется запущенная задача и prepared checkout")
            if verified_host_required(state):
                import test_evidence
                check = test_evidence.check(ROOT, ident, record["baseCommit"],
                                            tk.get("testEvidence"), gate_signed(state))
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
        if verified_host_required(state):
            import test_evidence
            evidence = tk.get("testEvidence")
            if record.get("sourceCommit"):
                # Host finalize consumed and committed the exact verified edit.
                if not evidence or evidence.get("status") != "verified":
                    die("worktree: нет подтверждения тестов на хосте")
                if not evidence_signature_ok(state, ident, evidence):
                    die("worktree: подпись результатов тестов отсутствует или неверна")
                if worktrees.source_commit(ROOT, ident, record["baseCommit"]) != record["sourceCommit"]:
                    die("worktree: коммит изменился после финализации")
                check = {"passed": evidence["passed"], "failed": evidence["failed"]}
            else:
                check = test_evidence.check(ROOT, ident, record["baseCommit"], evidence,
                                            gate_signed(state))
            if opt.get("tests") and tests_pair(opt["tests"]) != check:
                die("worktree: указанные тесты не совпадают с проверенными на хосте")
            source = "host"
        else:
            check = tests_pair(opt.get("tests") or "")
            # "host" only if the receipt is bound to the current HEAD and fingerprint.
            import test_evidence
            try:
                observed = test_evidence.check(ROOT, ident, record["baseCommit"],
                                               tk.get("testEvidence"))
            except test_evidence.EvidenceError:
                observed = None
            source = "host" if observed == check else "claimed"
        if check["passed"] < 1 or check["failed"] != 0:
            die("worktree: для интеграции нужны пройденные тесты N/0")
        result = worktrees.land(ROOT, ident, record["baseCommit"], tk.get("zone") or [],
                                active_zones={x["id"]: x.get("zone") or [] for x in known.values()
                                              if x["id"] != ident and x.get("status") in ACTIVE_EXECUTOR})
        tk["testsSource"] = source
        if source == "claimed":
            note = "тесты тикета %s не перепроверены хостом" % ident
            assumptions = state.setdefault("debt", {}).setdefault("assumptions", [])
            if note not in assumptions:
                assumptions.append(note)
            print("предупреждение: " + note + " (числа заявлены оркестратором)")
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
                   "memoryOwner", "skillDir", "mode", "depth", "kind"}
        if not _ or k not in allowed:
            die("set: разрешены только " + ", ".join(sorted(allowed)))
        if k == "kind":
            import kinds
            try:
                v = kinds.normalize(v if v != "null" else None)
            except ValueError as exc:
                die("set: kind: %s" % exc)
        state[k] = None if v in ("", "null") else v


def blocker_ledger(state):
    """Fail closed for corrupted blocker records, including old manual edits."""
    entries = state.get("blockingFindings", [])
    if not isinstance(entries, list):
        die("блокирующие замечания: повреждён журнал")
    ids = set()
    for entry in entries:
        if (not isinstance(entry, dict)
                or (entry.get("status") == "resolved"
                    and (not isinstance(entry.get("resolutionCommit"), str)
                         or not isinstance(entry.get("review"), str)
                         or not entry["review"].strip()
                         or not isinstance(entry.get("resolutionTests"), dict)
                         or not isinstance(entry["resolutionTests"].get("passed"), int)
                         or entry["resolutionTests"]["passed"] < 1
                         or entry["resolutionTests"].get("failed") != 0))
                or not isinstance(entry.get("id"), str)
                or not re.fullmatch(r"B[0-9]{2,6}", entry["id"])
                or entry["id"] in ids
                or not isinstance(entry.get("text"), str)
                or not entry["text"].strip()
                or entry.get("status") not in ("open", "resolved", "downgraded")
                or (entry.get("ticket") is not None
                    and not isinstance(entry.get("ticket"), str))):
            die("блокирующие замечания: повреждён журнал")
        ids.add(entry["id"])
    return entries


def open_blocker(state, text, ticket=None):
    if not isinstance(text, str) or not 3 <= len(text.strip()) <= 2000:
        die("блокирующее замечание требует --note (3–2000 символов)")
    entries = blocker_ledger(state)
    if len(entries) >= 1000:
        die("достигнут лимит блокирующих замечаний")
    n = 1 + max([int(e["id"][1:]) for e in entries] or [0])
    item = {"id": "B%02d" % n, "text": text.strip(),
            "ticket": ticket["id"] if ticket else None,
            "openedAt": state["updatedAt"], "status": "open"}
    # Anchor every blocker (including a whole-branch blocker) to the
    # commit at review time. A previously existing commit cannot close it.
    origin = _run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"]).strip()
    if not verified_commit(origin):
        die("blocker open: нельзя определить исходный Git-коммит")
    item["openedCommit"] = origin
    entries.append(item)
    log(state, "blocker", id=item["id"], act="open", ticket=item["ticket"])
    return item


def blocker_confirm(state, opt):
    """Второй проход по блокирующему: не подтверждено — блокер `downgraded`, условие уходит в concerns."""
    entry = next((b for b in blocker_ledger(state) if b["id"] == opt.get("id")), None)
    if entry is None or entry["status"] != "open":
        die("blocker: нет открытого замечания с этим ID")
    verdict, quote = opt.get("verdict"), opt.get("quote")
    if verdict not in ("confirmed", "not-confirmed"):
        die("blocker confirm: --verdict confirmed|not-confirmed")
    if not isinstance(quote, str) or not quote.strip():
        die("blocker confirm: нужна цитата второго прохода --quote (место кода и что в нём)")
    if entry.get("secondPass"):
        die("blocker confirm: у %s уже есть вердикт второго прохода (%s)" % (entry["id"], entry["secondPass"].get("verdict")))
    entry["confirmQuote"] = clean_quote(quote)
    entry["secondPass"] = {"verdict": verdict, "quote": entry["confirmQuote"], "at": now()}
    if verdict == "confirmed":
        log(state, "blocker", id=entry["id"], act="confirmed", ticket=entry.get("ticket"), verdict=verdict)
        return
    entry.update(status="downgraded", downgradedAt=state["updatedAt"])
    cmd_add(state, ["concerns", "не подтверждено вторым проходом: " + entry["text"]])
    log(state, "blocker", id=entry["id"], act="downgraded", ticket=entry.get("ticket"), verdict=verdict)


def plan_items_by_ticket(state):
    """Пункты плана по таскам прогона: {id таска: [текст…]} из файлов тасков (раздел критериев)."""
    import plan_items
    out = {}
    for tk in state.get("tickets") or []:
        files = ticket_files(state, "%s-*.md" % tk["id"])
        if len(files) != 1:
            continue
        with open(files[0], encoding="utf-8") as stream:
            items = plan_items.parse_items(stream.read())
        if items:
            out[tk["id"]] = items
    return out


def plan_line(state):
    fact = state.get("planFact") or {}
    return "план: %d из %d" % (fact.get("done", 0), fact.get("total", 0))


def cmd_plan_fact(state, pos, multi):
    """plan-fact list | record --verdict "T02.1 | сделано | файл:строка" … | show"""
    import plan_items
    if len(pos) != 1 or pos[0] not in ("list", "record", "show"):
        die("plan-fact list | plan-fact record --verdict \"T02.1 | сделано | файл:строка\" … | plan-fact show")
    if pos[0] == "show":
        return [plan_line(state)]
    by_ticket = plan_items_by_ticket(state)
    if pos[0] == "list":
        return ["%s.%d — %s" % (plan_items.item_prefix(t), n, text) for t, texts in by_ticket.items() for n, text in enumerate(texts, 1)]
    verdicts = [plan_items.parse_verdict(v) for v in multi.get("verdict", [])]
    if not verdicts or None in verdicts:
        die("plan-fact record: --verdict \"T02.1 | сделано|частично|не сделано | доказательство\" (по одному на пункт)")
    unknown = plan_items.unknown_ids(by_ticket, verdicts)
    if unknown:
        die("plan-fact record: нет пунктов с id %s — см. `plan-fact list`" % ", ".join(unknown))
    previous = (state.get("planFact") or {}).get("items")
    fact = state["planFact"] = plan_items.build_plan_fact(by_ticket, plan_items.merge_verdicts(previous, verdicts), ROOT)
    state["concerns"] = [c for c in state.get("concerns") or [] if not (isinstance(c, str) and c.startswith("план: "))]
    for item in fact["items"]:
        if item["status"] != plan_items.DONE:
            cmd_add(state, ["concerns", "план: %s — %s — %s" % (item["id"], item["status"], item["text"])])
    log(state, "plan-fact", done=fact["done"], total=fact["total"])
    asked = {v["id"] for v in verdicts if v.get("status") == plan_items.DONE}
    demoted = ["%s понижен до «не сделано»: для «сделано» нужно доказательство файл:строка или файл::имя с существующим путём" % i["id"]
               for i in fact["items"] if i["id"] in asked and i["status"] != plan_items.DONE]
    return [plan_line(state)] + demoted


def cmd_check_review_report(opt):
    import review_checks
    path = opt.get("file")
    if not isinstance(path, str):
        die("check-review-report --file ФАЙЛ")
    try:
        with open(path, encoding="utf-8") as stream:
            missing = review_checks.missing_checklist(stream.read())
    except (OSError, UnicodeDecodeError) as exc:
        die("check-review-report: %s" % exc)
    print("\n".join("в отчёте нет ответа по пункту: " + m for m in missing) or "чек-лист закрыт полностью")
    return 1 if missing else 0


def cmd_check_bypass(pos):
    """Печатает добавленные skip/xfail/--no-verify и удалённые assert; только сигнал, код 0."""
    import review_checks
    rev = pos[1] if len(pos) > 1 else "HEAD~1..HEAD"
    if len(pos) < 2 and subprocess.run(["git", "-C", ROOT, "rev-parse", "-q", "--verify", "HEAD~1"],
                                       capture_output=True).returncode:
        rev = "4b825dc642cb6eb9a060e54bf8d69288fbee4904..HEAD"  # единственный коммит: от пустого дерева
    if rev.startswith("-") or len(pos) > 2:
        die("check-bypass [РЕВИЗИЯ..РЕВИЗИЯ]")
    done = subprocess.run(["git", "-C", ROOT, "diff", "--no-color", rev, "--"], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if done.returncode:
        die("check-bypass: git diff %s не удался" % rev)
    print("\n".join(review_checks.bypass_lines(done.stdout)) or "обхода не видно")
    return 0


def cmd_blocker(state, pos, opt):
    if len(pos) != 1 or pos[0] not in ("open", "resolve", "confirm"):
        die("blocker open --note TEXT [--ticket NN] | blocker resolve --id BNN --commit SHA --tests N/0 --note REVIEW"
            " | blocker confirm --id BNN --verdict confirmed|not-confirmed --quote \"цитата кода\"")
    if pos[0] == "confirm":
        return blocker_confirm(state, opt)
    if pos[0] == "open":
        ticket = None
        if opt.get("ticket") is not None:
            ticket = next((t for t in state.get("tickets") or []
                           if t.get("id") == opt["ticket"]), None)
            if ticket is None:
                die("blocker: неизвестный таск")
        item = open_blocker(state, opt.get("note"), ticket)
        print("блокирующее замечание %s зарегистрировано" % item["id"])
        return
    entries = blocker_ledger(state)
    entry = next((b for b in entries if b["id"] == opt.get("id")), None)
    if entry is None or entry["status"] != "open":
        die("blocker: нет открытого замечания с этим ID")
    review = opt.get("note")
    if not isinstance(review, str) or len(review.strip()) < 12:
        die("blocker resolve: нужна конкретная запись результата повторного ревью --note")
    commit = opt.get("commit")
    if not verified_commit(commit):
        die("blocker resolve: нужен существующий проверенный коммит в HEAD")
    baseline = entry.get("openedCommit")
    if (baseline and (
            commit.lower().startswith(baseline.lower())
            or baseline.lower().startswith(commit.lower())
            or not commit_descends_from(commit, baseline))):
        die("blocker resolve: коммит исправления должен отличаться от исходного"
            " и быть его потомком")
    if not opt.get("tests"):
        die("blocker resolve: требуются свежие успешные тесты --tests N/0")
    result = tests_pair(opt["tests"])
    if result["passed"] < 1 or result["failed"]:
        die("blocker resolve: тесты не пройдены")
    if entry.get("ticket") and verified_host_required(state):
        ticket = next((t for t in state.get("tickets") or []
                       if t.get("id") == entry["ticket"]), None)
        evidence = ticket.get("testEvidence") if ticket else None
        if (not isinstance(evidence, dict) or evidence.get("status") != "verified"
                or result != {"passed": evidence.get("passed"), "failed": 0}):
            die("blocker resolve: в строгом изолированном режиме необходимы независимые тесты")
    entry.update(status="resolved", resolvedAt=state["updatedAt"],
                 resolutionCommit=commit.lower(), resolutionTests=result,
                 review=review.strip())
    log(state, "blocker", id=entry["id"], act="resolve", ticket=entry.get("ticket"))


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


NUMBERS = {"coverage": ("found", "fixed", "deferred"), "blind": ("checked", "matched")}


def cmd_numbers(state, name, pos, multi):
    """Гейт решают числа: без всех чисел ничего не пишем — пропавший счётчик не ноль."""
    keys = NUMBERS[name]
    usage = "%s %s" % (name, " ".join(k + "=N" for k in keys))
    d = {}
    for p in pos:
        k, eq, v = p.partition("=")
        if not eq or k not in keys or not v.isdigit():
            die("%s: не понял «%s» — пишется так: %s" % (name, p, usage))
        d[k] = int(v)
    missing = [k for k in keys if k not in d]
    if missing:
        die("%s: нет %s — пишется так: %s" % (name, ", ".join(missing), usage))
    if name == "blind":
        if d["matched"] > d["checked"]:
            die("blind: matched=%d больше checked=%d" % (d["matched"], d["checked"]))
        if (state.get("blindRounds") or 0) >= BLIND_ROUNDS:
            die("blind: уже %d круга слепой приёмки за прогон. Остаток расхождений — в отчёт: "
                "`add report \"что осталось\"`" % BLIND_ROUNDS)
        d["mismatches"] = multi.get("mismatch", [])
        first = state.get("blind") if state.get("blindRounds") == 1 else None
        round_ok = True
        if isinstance(first, dict) and isinstance(first.get("checked"), int):
            # Круг 2 проверяет расхождения круга 1 и основной сценарий; итог — как в круге 1, расхождения — оставшиеся.
            r1 = {"checked": first["checked"], "matched": first.get("matched"),
                  "mismatches": list(first.get("mismatches") or [])}
            floor = len(r1["mismatches"])
            if d["checked"] < floor:
                die("blind: круг 2 должен проверить каждое из %d расхождений круга 1 — checked не меньше %d; "
                    "закрытое — в matched, оставшееся — в --mismatch" % (floor, floor))
            cap = floor + 1
            if d["checked"] > cap:
                die("blind: круг 2 проверяет только расхождения круга 1 и основной сценарий — checked не больше %d" % cap)
            round_ok = d["checked"] - d["matched"] == len(d["mismatches"])
            d = {"checked": r1["checked"], "matched": max(0, r1["checked"] - len(d["mismatches"])),
                 "mismatches": d["mismatches"], "rounds": [r1, dict(d)]}
        state[name] = d
        state["blindRounds"] = (state.get("blindRounds") or 0) + 1
        valid = (round_ok and isinstance(d.get("checked"), int) and d["checked"] > 0
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


def landing_problems(state):
    """-> (refuse, caveat). refuse — отменяемые отказы finish (снимает только --by-user);
    caveat — оговорки, которые сдаче не мешают (G4 красный после BLIND_ROUNDS кругов)."""
    refuse, caveat = [], []
    done = [tk for tk in state.get("tickets") or [] if tk.get("status") == "done"]
    nocommit = [tk.get("id", "?") for tk in done if not tk.get("commit")]
    if nocommit:
        refuse.append("сданные таски без коммита: " + ", ".join(nocommit))
    # The run may have been reset/rebased after its tickets were accepted.
    # Reject stale Git ancestry *at the final gate*, not just at ticket done;
    # 'commits' remains a separate read-only diagnostic for manual recovery.
    stale = [tk.get("id", "?") for tk in done
             if tk.get("commit") and not verified_commit(tk["commit"])]
    if stale:
        refuse.append("коммиты сданных тасков отсутствуют в HEAD: " + ", ".join(stale))
    gates = state.get("gates") or {}
    missing = [g for g in ("G1", "G2", "G3", "G4") if not (gates.get(g) or {}).get("ok")]
    g4 = gates.get("G4") or {}
    if ("G4" in missing and (state.get("blindRounds") or 0) >= BLIND_ROUNDS
            and state.get("blind") and not g4.get("reason")):
        missing.remove("G4")
        caveat.append("слепая приёмка: расхождения остались после %d кругов (%d из %d)"
                      % (BLIND_ROUNDS, len((state["blind"] or {}).get("mismatches") or []),
                         (state["blind"] or {}).get("checked") or 0))
    if missing:
        refuse.append("проверки %s не пройдены" % ", ".join(missing))
    incomplete = [tk["id"] for tk in state.get("tickets") or [] if tk.get("status") != "done"]
    if incomplete or not state.get("tickets"):
        refuse.append("незавершённые таски: %s" %
                      (", ".join(incomplete) if incomplete else "нет опубликованных тасков"))
    test = state.get("tests") or {}
    if test.get("passed", 0) < 1 or test.get("failed") != 0:
        refuse.append("нет успешного полного прогона тестов")
    open_rows = [rid for rid, st in manifest_rows(state) or []
                 if not rid.startswith("D") and st in ("open", "in-spec", "in-ticket")]
    if open_rows:
        refuse.append("требования не закрыты: " + ", ".join(open_rows))
    return refuse, caveat


def archive_attestations(state):
    """`finish`: строки общего `.autopilot/attestations.jsonl` — в `<папка прогона>/attestations.jsonl` (дописью, как есть:
    подписи верны), общий файл начинается заново. Сбой — строка `!`, `finish` не падает."""
    src, dst_dir = os.path.join(A, "attestations.jsonl"), os.path.join(A, state.get("dir") or "")
    try:
        if not state.get("dir") or os.path.islink(src) or not os.path.isfile(src) or not os.path.isdir(dst_dir):
            return None
        with open(src, "rb") as f:
            data = f.read()
        if not data:
            return None
        with open(os.path.join(dst_dir, "attestations.jsonl"), "ab") as f:
            f.write(data)
        with open(src, "wb"):
            pass
        return "аттестации перенесены: %s/attestations.jsonl" % state["dir"]
    except OSError as exc:
        return "! аттестации не перенесены (%s)" % type(exc).__name__


PROFILE_DIRS = ((".claude/agents", ".md"), (".codex/agents", ".toml"))


def profile_refs(state):
    """Имена профилей, записанных в state.js прогона: routing и escalatedFrom тасков, roleAgents, repairAgent, opusAgents."""
    entries = []
    for tk in state.get("tickets") or []:
        if isinstance(tk, dict):
            entries += [tk.get("routing"), tk.get("escalatedFrom")]
    role_agents = state.get("roleAgents")
    entries += list(role_agents.values()) if isinstance(role_agents, dict) else []
    entries.append(state.get("repairAgent"))
    opus = state.get("opusAgents")
    entries += list(opus.values()) if isinstance(opus, dict) else []
    names = set()
    for entry in entries:
        values = [entry] if isinstance(entry, str) else (
            [entry.get("agentType"), os.path.splitext(os.path.basename(str(entry.get("agentFile") or "").replace("\\", "/")))[0]]
            if isinstance(entry, dict) else [])
        names.update(v for v in values if isinstance(v, str) and v)
    return names


def profile_files(names=None):
    """Файлы профилей `autopilot-<роль>-<имя>` в `.claude/agents` и `.codex/agents`: не ссылки, не четыре постоянных;
    `names` — только эти имена. Больше ничего не возвращается, значит, больше ничего и не удалят."""
    import agent_profiles
    permanent = {"autopilot-" + r for r in agent_profiles.PERMANENT_ROLES}
    found = []
    for rel, ext in PROFILE_DIRS:
        folder = os.path.join(ROOT, *rel.split("/"))
        try:
            if os.path.islink(folder):
                continue
            entries = sorted(os.scandir(folder), key=lambda e: e.name)
        except OSError:
            continue
        for e in entries:
            stem = e.name[:-len(ext)] if e.name.endswith(ext) else ""
            if (re.fullmatch(r"autopilot-(?:%s)-[A-Za-z0-9._-]+" % "|".join(agent_profiles.PERMANENT_ROLES), stem)
                    and stem.lower() not in permanent
                    and not e.is_symlink() and e.is_file(follow_symlinks=False)
                    and (names is None or stem in names)):
                found.append(e.path)
    return found


def unfinished_profile_refs(own):
    """Имена профилей незавершённых прогонов, кроме `own`: папки `*--wip` и архивы с пустым `finishedAt`.
    Второе значение — нечитаемые `--wip` папки: про них неизвестно, что они держат."""
    refs, unreadable = set(), []
    try:
        folders = sorted(n for n in os.listdir(A) if RUN_DIR_NAME.fullmatch(n) and run_key(n) != own)
    except OSError:
        return refs, unreadable
    for n in folders:
        try:
            old = state_io.read_state_file(os.path.join(A, n, "state.js"))
            if n.endswith("--wip") or old.get("finishedAt") is None:
                refs |= profile_refs(old)
        except (state_io.StateError, OSError, AttributeError):
            if n.endswith("--wip"):
                unreadable.append(n)
    return refs, unreadable


def delete_profiles(paths):
    """Удалить файлы; сбой одного не мешает остальным. Вернуть (удалённые, строки `!`)."""
    done, notes = [], []
    for path in paths:
        try:
            os.unlink(path)
            done.append(path)
        except OSError as exc:
            notes.append("! профиль не удалён: %s (%s)" % (os.path.relpath(path, ROOT), type(exc).__name__))
    return done, notes


def remove_run_profiles(state):
    """`finish`: убрать профили этого прогона; постоянные, чужие файлы и профили других незавершённых прогонов остаются."""
    try:
        others, unreadable = unfinished_profile_refs(run_key(state.get("dir")))
        if unreadable:
            return ["! профили не удалены: не читается state.js в " + ", ".join(unreadable)]
        done, notes = delete_profiles(profile_files(profile_refs(state) - others))
        return ["профили прогона удалены: %d" % len(done)] * bool(done) + notes
    except (OSError, ImportError) as exc:
        return ["! профили не удалены (%s)" % type(exc).__name__]


def cmd_agents_prune(opt):
    """`agents prune [--apply]`: профили `autopilot-*`, на которые не ссылается ни один незавершённый прогон."""
    state = read_state()
    own = run_key((state or {}).get("dir"))
    keep, unreadable = unfinished_profile_refs(own)
    if state and state.get("finishedAt") is None:
        keep |= profile_refs(state)
    if unreadable:
        die("agents prune: не читается state.js в %s — не знаю, что там держится" % ", ".join(unreadable))
    paths = [p for p in profile_files() if os.path.splitext(os.path.basename(p))[0] not in keep]
    if opt.get("apply") is not True:
        print("\n".join(["без --apply ничего не удаляю; бы удалил: %d" % len(paths)]
                        + ["  " + os.path.relpath(p, ROOT) for p in paths]))
        return 0
    done, notes = delete_profiles(paths)
    print("\n".join(["профили удалены: %d" % len(done)] + notes))
    return 1 if notes else 0


def cmd_finish(state, opt):
    if state.get("gateMark") is not None:
        gate_signed(state)  # never re-sign the record over a forged state
    pending_blockers = [b["id"] for b in blocker_ledger(state)
                        if b["status"] == "open"]
    if pending_blockers:
        die("finish заблокирован: незакрытые блокирующие замечания: "
            + ", ".join(pending_blockers))
    # Older 2.3-dev states may have review repair notes without the new
    # structured ledger. Do not silently treat those notes as resolved.
    ledger = blocker_ledger(state)
    for ticket in state.get("tickets") or []:
        notes = ticket.get("repairFindings") or []
        if (not isinstance(notes, list)
                or any(not isinstance(note, str) for note in notes)
                or any(not any(b.get("ticket") == ticket.get("id")
                               and b.get("text") == note for b in ledger)
                       for note in notes)):
            die("finish заблокирован: замечания старого ревью без записи закрытия; "
                "добавь blocker open --ticket NN и подтверди исправление")
    stale_resolution = [b["id"] for b in ledger if b["status"] == "resolved"
                        and not verified_commit(b.get("resolutionCommit"))]
    if stale_resolution:
        die("finish заблокирован: коммиты закрытия блокирующих замечаний отсутствуют в HEAD: "
            + ", ".join(stale_resolution))
    refresh_g1(state, create=True)
    refuse, caveat = landing_problems(state)
    hard = []                                         # неотменяемое: --by-user его не снимает
    saved_contract = state.get("planContractDigest")
    if (not isinstance(saved_contract, str)
            or saved_contract != plan_contract_digest(state)):
        hard.append("требования изменились после G3 или нет отпечатка старого прогона; "
                    "повтори check-plan и при необходимости G2/G4")
    else:
        hard += ["повторная G3 проверка плана не пройдена: " + p for p in check_plan(state)]
    by_user = clean_quote(opt.get("by-user"))
    if hard or (refuse and not by_user):
        lines = ["finish заблокирован:"] + ["  - " + x for x in hard + refuse]
        if refuse and not hard:
            lines.append("Сдать как есть можно только словами пользователя: "
                         "finish --result \"…\" --by-user \"<его цитата>\"")
        die("\n".join(lines))
    t = now()
    notes = []
    for s in state.get("stages") or []:
        if s.get("status") in ("active", "pending") and s.get("id") == "final":
            if s.get("status") == "active":
                segment_close(s, t)
            s["status"], s["finishedAt"] = "done", t
            s.setdefault("startedAt", t)
        elif s.get("status") == "active":
            segment_close(s, t)
            s["status"], s["finishedAt"] = "done", t
        elif s.get("status") == "pending":
            s["status"], s["note"], s["finishedAt"] = "skipped", s.get("note") or "не понадобился", t
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
    problems = refuse + caveat
    if problems:
        state["landedWith"] = {"problems": problems, "byUser": by_user}
        notes.append("! сдано с оговоркой — " + "; ".join(problems))
    else:
        state.pop("landedWith", None)
    register_row(state, "сдан с оговорками" if problems else "сдан", state["result"])
    sync_run_record(state)
    log(state, "finish", result=state["result"], problems=len(problems))
    notes += [n for n in [archive_attestations(state)] if n]
    notes += remove_run_profiles(state)
    notes.append(spend_orchestrator(state))
    notes.append(spend_subagents(state))
    try:
        import lessons
        if lessons.refresh_profile(ROOT, full_check_command(state)):
            notes.append("профиль проекта обновлён: .autopilot/profile.md")
    except OSError:
        pass
    notes.append("уроки: запусти лёгкого агента по phases/9-lessons.md (ap.py lessons candidates)")
    return notes


def cmd_reopen(state):
    """Второй бриф в сданном прогоне: фазы 1–8 идут заново, прежние таски остаются."""
    if state.get("gateMark") is not None:
        gate_signed(state)
    if any(t.get("worktree") and t["worktree"].get("status") != "released"
           for t in state.get("tickets") or []):
        die("reopen заблокирован: незавершённые или неосвобождённые worktrees")
    d = state.get("dir") or ""
    if not d.endswith("--wip") and git_mv(d, d + "--wip"):
        state["dir"] = d + "--wip"
    state["finishedAt"] = None
    state["blind"] = None
    state["blindRounds"] = 0
    state.pop("landedWith", None)
    for s in state.get("stages") or []:
        if s.get("id") != "preflight":
            for k in ("startedAt", "finishedAt", "note", "segments"):
                s.pop(k, None)
            s["status"] = "pending"
    stage(state, "manifest").update(status="active", startedAt=now())
    state["result"] = None
    state["gates"] = {}
    sync_run_record(state)
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


CLAUDE_MIN_VERSION = (2, 1, 295)
CLAUDE_WARN_BELOW = (2, 1, 311)
CLAUDE_KNOWN_ISSUES = [
    "2.1.305 (Windows): на части томов отказ любого вызова инструмента; пути scratchpad растут с длиной пути проекта (лимит 260)",
    "2.1.310 (Windows): PreToolUse-хук пропускал вызов без Git Bash, если команда хука — только строки в кавычках",
]


def parse_claude_version(text):
    """`2.1.302 (Claude Code)` → (2, 1, 302); не разобрано → None."""
    m = re.search(r"(?<![\d.])(\d+)\.(\d+)\.(\d+)(?![\d.])", text or "")
    return tuple(int(x) for x in m.groups()) if m else None


def claude_version_report(version, min_version=CLAUDE_MIN_VERSION, warn_below=CLAUDE_WARN_BELOW):
    """→ (уровень ok|warn|refuse|unknown, строки сообщения)."""
    if version is None:
        return "unknown", ["версия Claude Code не определена (настольное приложение несёт свою) — проверка пропущена"]
    v = ".".join(map(str, version))
    if version < min_version:
        return "refuse", ["Claude Code %s ниже минимума %s — обнови" % (v, ".".join(map(str, min_version)))]
    if version < warn_below:
        return "warn", ["Claude Code %s ниже %s; известные проблемы:" % (v, ".".join(map(str, warn_below)))] \
            + ["  - " + x for x in CLAUDE_KNOWN_ISSUES]
    return "ok", ["Claude Code %s — ok" % v]


def cmd_git_check():
    """Может ли git писать здесь — до брифинга, а не на первом таске. Как `git add`, берём и
    снимаем index.lock, не трогая ни индекс, ни файлы; state.js не нужен. (`update-index
    --refresh` для этого не годится: без изменений он молча терпит занятый замок.)"""
    err = None
    try:
        # git смотрим из cwd: preflight запускает копию из tools/ навыка, она лежит вне репозитория пользователя
        r = subprocess.run(["git", "rev-parse", "--git-path", "index.lock"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if r.returncode:
            err = next((x.strip() for x in r.stderr.splitlines() if x.strip()), "git вернул код %d" % r.returncode)
        else:
            lock = os.path.join(os.getcwd(), r.stdout.strip())
            try:
                os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                os.remove(lock)
            except OSError as exc:
                err = "%s: %s" % (lock, exc.strerror or exc)
    except (OSError, subprocess.SubprocessError) as exc:
        err = "%s: %s" % (type(exc).__name__, exc)
    if err is None:
        print("git: запись разрешена")
        return 0
    print("git не может писать здесь: %s. Это сбой машины, не кода" % err)
    return 2


def claude_version_text(opt):
    text = opt.get("text")
    if text is None:
        try:
            text = subprocess.run(["claude", "--version"], capture_output=True, text=True,
                                  timeout=20).stdout
        except (OSError, subprocess.SubprocessError):
            text = ""
    return text


def cmd_claude_version(opt):
    text = claude_version_text(opt)
    level, lines = claude_version_report(parse_claude_version(text if isinstance(text, str) else ""))
    if level == "ok":
        return 0
    print("\n".join(lines))
    return 2 if level == "refuse" else 0


def cmd_doctor(opt):
    """`doctor`: git-check, версия Claude Code, advisorModel, сводка repo_doctor — по строке на проверку,
    проект — текущая папка. Код 2 только там, где сборку останавливали и раньше: Git не пишет, версия ниже минимума."""
    def git():
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cmd_git_check()
        return out.getvalue().strip(), code

    def version():
        level, lines = claude_version_report(parse_claude_version(str(claude_version_text(opt))))
        return "claude: " + lines[0].rstrip(":"), 2 if level == "refuse" else 0

    def advisor():
        spots = [os.path.join(claude_config_dir(), "settings.json"),
                 os.path.join(os.getcwd(), ".claude", "settings.json"),
                 os.path.join(os.getcwd(), ".claude", "settings.local.json")]
        found = []
        for path in spots:
            try:
                with open(path, encoding="utf-8-sig") as f:
                    if "advisorModel" in json.load(f):
                        found.append(path)
            except (OSError, ValueError, TypeError):
                pass
        if not found:
            return "advisorModel: не задан", 0
        return ("advisorModel: задан в %s — для строгого прогона поставь CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1"
                % ", ".join(found)), 0

    def repo():
        import repo_doctor
        try:
            report = repo_doctor.inspect(os.getcwd())
        except repo_doctor.DoctorError as exc:
            return "repo_doctor: %s" % exc, 0
        return ("repo_doctor: готов" if report["status"] == "ready"
                else "repo_doctor: блокеры — " + ", ".join(report["blockers"])), 0
    worst = 0
    for check in (git, version, advisor, repo):
        try:
            line, code = check()
        except Exception as exc:                      # сбой одной проверки не мешает остальным
            line, code = "%s: проверка не выполнилась (%s)" % (check.__name__, type(exc).__name__), 0
        print(line)
        worst = max(worst, code)
    return worst


def cmd_bootstrap(opt):
    """`bootstrap [--project .]` из папки навыка: все `.py` из tools/ и дашборд -> `<проект>/.autopilot/`, `index.html`;
    печатает skillDir. Идемпотентна, `state.lock` не берёт. Подписанный прогон с другим skillDir и таск в работе — отказ."""
    global A, ROOT, PAGE
    tools = os.path.dirname(os.path.abspath(__file__))
    skill = os.path.dirname(tools)
    template = os.path.join(skill, "phases", "dashboard-template.html")
    if not (os.path.isfile(os.path.join(skill, "SKILL.md")) and os.path.isfile(template)):
        die('bootstrap запускается из папки навыка: python3 "<skillDir>/tools/ap.py" bootstrap --project .')
    project = os.path.abspath(opt["project"] if isinstance(opt.get("project"), str) else ".")
    if not os.path.isdir(project):
        die("bootstrap: нет папки проекта " + project)
    dest = os.path.join(project, ".autopilot")
    A, ROOT, PAGE = dest, project, os.path.join(dest, "dashboard.html")
    state = None
    if os.path.isfile(os.path.join(dest, "state.js")):
        try:
            state = state_io.read_state_file(os.path.join(dest, "state.js"))
        except state_io.StateError as exc:
            die("bootstrap: %s" % exc)
    ours = dict(state or {}, skillDir=skill)
    if state and not state.get("finishedAt"):
        busy = [t["id"] for t in state.get("tickets") or [] if t.get("status") in ACTIVE_EXECUTOR]
        if busy:
            die("bootstrap: таск в работе (%s) — ставь инструменты между тасками" % ", ".join(busy))
        if not skill_dir_trusted(ours):
            die("bootstrap: " + NOT_PINNED)
    copied, note = [], ""
    try:
        os.makedirs(dest, exist_ok=True)
        for name in sorted(os.listdir(tools)):
            src, target = os.path.join(tools, name), os.path.join(dest, name)
            if not name.endswith(".py") or not os.path.isfile(src):
                continue
            with open(src, "rb") as f:
                data = f.read()
            if os.path.isfile(target):
                with open(target, "rb") as f:
                    if f.read() == data:
                        continue
            with open(target + ".new", "wb") as f:
                f.write(data)
            os.replace(target + ".new", target)
            copied.append(name)
        with open(template, "rb") as f:
            page = f.read()
        if state is not None and os.path.isfile(PAGE):
            note = refresh_dashboard(ours)                # через dashboard_upgrade.py, снимок не затирается
        elif not os.path.isfile(PAGE) or open(PAGE, "rb").read() != page:
            with open(PAGE, "wb") as f:
                f.write(page)
            note = "дашборд скопирован"
        index = os.path.join(dest, "index.html")
        if not os.path.lexists(index):
            try:
                os.symlink("dashboard.html", index)
            except (OSError, NotImplementedError):        # ссылки недоступны — копия-перенаправление
                with open(index, "w", encoding="utf-8") as f:
                    f.write('<!doctype html><meta charset="utf-8">'
                            '<meta http-equiv="refresh" content="0; url=dashboard.html">'
                            '<a href="dashboard.html">dashboard</a>\n')
    except OSError as exc:
        die("bootstrap: не записано (%s)" % exc)
    print("инструменты: %s" % (("скопировано %d" % len(copied)) if copied else "уже на месте"))
    if note:
        print(note)
    print("skillDir = " + skill)
    return 0


# ── данные для дашборда: расход, прошлые сборки, сбои журнала ────────────────

HISTORY_KEPT = 20
HISTORY_CACHE = "history-cache.json"
UNKNOWN_MODEL = "не указана"
RUN_DIR_NAME = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*(?:--wip)?")
EXEC_TICKET = re.compile(r"autopilot-executor-(?:(\d+)|f(\d+))-")


def run_key(name):
    """Имя прогона без `--wip`: журнал мог писаться до переименования папки."""
    return str(name or "").removesuffix("--wip")


def executor_ticket(agent_type):
    """Номер таска из имени профиля `autopilot-executor-<NN|F<n>>-…`; у ремонтника и ревьюера его нет."""
    m = EXEC_TICKET.match(agent_type) if isinstance(agent_type, str) else None
    return (m.group(1) or "F" + m.group(2)) if m else None


def _tokens(row, key):
    v = row.get(key)
    return v if isinstance(v, int) and not isinstance(v, bool) and v > 0 else 0


def row_ticket(r):
    """Таск строки расхода: поле `ticket` (из журнала Claude Code), иначе из имени профиля."""
    t = r.get("ticket")
    return t if isinstance(t, str) and t else executor_ticket(r.get("agent_type"))


def executor_rows(records, run):
    """Строки единого журнала расхода одного прогона; без повторов по `agent`."""
    if run_log:
        return run_log.spend_rows(records, run)
    rows = [r for r in records if isinstance(r, dict) and r.get("k") in ("executor", "spend")
            and run_key(r.get("run")) == run_key(run)]
    return rows


def compute_spend(records, run):
    """{byRole, byModel, byTicket}: на ключ — число запусков, токены (вход + выход), кэш (чтение, запись)
    и доля попаданий `hit` (целые %, `None` без знаменателя). Строка без модели — «не указана»;
    без таска в имени профиля — только в byRole и byModel. Оркестратор (`role=orchestrator`) —
    последняя строка на модель, в byTicket его нет."""
    out = {"byRole": {}, "byModel": {}, "byTicket": {}}
    rows, last_orch = [], {}
    for r in executor_rows(records, run):
        if r.get("role") == "orchestrator":
            last_orch[r.get("model") if isinstance(r.get("model"), str) and r.get("model") else UNKNOWN_MODEL] = r
        else:
            rows.append(r)
    for r in rows + list(last_orch.values()):
        tokens = {"n": 1, "input": _tokens(r, "input"), "output": _tokens(r, "output"),
                  "cache_read": _tokens(r, "cache_read"), "cache_write": _tokens(r, "cache_write")}
        role = r.get("role") if isinstance(r.get("role"), str) and r.get("role") else (
            run_log.role_of(r.get("agent_type")) if run_log else "agent")
        model = r.get("model") if isinstance(r.get("model"), str) and r.get("model") else UNKNOWN_MODEL
        for bucket, key in (("byRole", role), ("byModel", model),
                            ("byTicket", None if role == "orchestrator" else row_ticket(r))):
            if key is None:
                continue
            acc = out[bucket].setdefault(key, dict.fromkeys(tokens, 0))
            for k, v in tokens.items():
                acc[k] += v
    for bucket in out.values():
        for acc in bucket.values():
            acc["tokens"] = acc["input"] + acc["output"]
            den = acc["input"] + acc["cache_read"] + acc["cache_write"]
            acc["hit"] = round(100 * acc["cache_read"] / den) if den else None
    return out


def session_transcript():
    """Самый свежий журнал сессии проекта: <CLAUDE_CONFIG_DIR|~/.claude>/projects/<путь с «-»>/*.jsonl или None.
    Нет точной папки (Claude Code усекает длинные имена) — папка с самым длинным общим префиксом ≥100 знаков."""
    root = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    projects = os.path.join(root, "projects")
    want = re.sub(r"[^A-Za-z0-9]", "-", os.path.dirname(A))
    newest = lambda d: glob.glob(os.path.join(glob.escape(os.path.join(projects, d)), "*.jsonl"))
    files = newest(want)
    if not files:
        # shortcut: правило усечения Claude Code не документировано и не проверено — берём общий префикс,
        # апгрейд — когда правило станет известно
        try:
            names = os.listdir(projects)
        except OSError:
            names = []
        scored = [(len(os.path.commonprefix([want, n])), max(os.path.getmtime(f) for f in fs), fs)
                  for n in names for fs in [newest(n)] if fs]
        scored = [x for x in scored if x[0] >= 100]
        files = max(scored, key=lambda x: x[:2])[2] if scored else []
    return max(files, key=os.path.getmtime) if files else None


CONTEXT_HINT = 150_000
CONTEXT_TAIL = 1_000_000          # байт с конца журнала: он бывает в десятки МБ, а нужен последний ответ


def last_context_tokens(transcript=None):
    """Размер контекста последнего ответа главной сессии: вход + чтение кэша + запись кэша.
    Читается только хвост журнала; оборванная строка и ответы субагентов (`isSidechain`) пропускаются,
    текст сообщений не читается. Журнала нет, он не читается или в хвосте нет ответа — None."""
    try:
        path = transcript or session_transcript()
        if not path:
            return None
        with open(path, "rb") as f:
            size = f.seek(0, os.SEEK_END)
            f.seek(max(0, size - CONTEXT_TAIL))
            lines = f.read().decode("utf-8", errors="replace").splitlines()
        if size > CONTEXT_TAIL:
            lines = lines[1:]                        # первая строка хвоста могла начаться посередине
        for line in reversed(lines):
            try:
                r = json.loads(line)
                msg = r.get("message")
                if r.get("isSidechain") is True or not isinstance(msg, dict) or msg.get("role") != "assistant" \
                        or not isinstance(msg.get("usage"), dict):
                    continue
            except (ValueError, AttributeError, RecursionError):
                continue                             # оборванная последняя строка
            u = msg["usage"]
            return sum(u[k] for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
                       if isinstance(u.get(k), int) and not isinstance(u.get(k), bool) and u[k] > 0)
    except Exception:
        pass
    return None


def context_hint():
    """Одна строка `↑`, если контекст главной сессии выше порога (`AUTOPILOT_CONTEXT_HINT`, по умолчанию
    150000, 0 выключает); иначе пустая строка. Подсказка, не вопрос: журнала нет — строки нет."""
    raw = os.environ.get("AUTOPILOT_CONTEXT_HINT", "").strip()
    limit = int(raw) if re.fullmatch(r"[0-9]+", raw) else CONTEXT_HINT
    n = last_context_tokens() if limit > 0 else None
    if n is None or n <= limit:
        return ""
    return ("↑ контекст этого чата %d тыс. токенов: каждый шаг его перечитывает. `/autopilot` в новом чате "
            "продолжит сборку с этого места, это дешевле" % round(n / 1000))


def spend_orchestrator(state, transcript=None):
    """Расход главной сессии за время прогона → строки `executor`/`role=orchestrator` в run-log.jsonl
    (числа и модель, без текста). Возвращает одну печатную строку; не бросает исключений."""
    miss = lambda why: "расход оркестратора не найден: " + why
    try:
        if run_log is None:
            return miss("журнал прогона недоступен")
        path = transcript or session_transcript()
        if not path:
            return miss("нет журнала сессии в ~/.claude/projects (путь задаёт --transcript)")
        by_model = run_log.usage_by_model(path, state.get("startedAt"), dt.datetime.now(dt.timezone.utc))
        if by_model is None:
            return miss("журнал сессии не читается")
        if not by_model:
            return miss("в журнале сессии нет ответов за время прогона")
        saved = [run_log.append(A, "executor", run=state.get("dir"), role="orchestrator",
                                source="orchestrator", origin="claude-transcript", model=model, **u)
                 for model, u in sorted(by_model.items())]
        if not all(saved):
            return "расход оркестратора не записан: журнал прогона недоступен для записи"
        return "расход оркестратора: %s ток. вход+выход, кэш чтение %s, моделей %d" % (
            sum(u["input"] + u["output"] for u in by_model.values()),
            sum(u["cache_read"] for u in by_model.values()), len(by_model))
    except Exception as exc:
        return "расход оркестратора не найден: " + type(exc).__name__


def _ticket_at(state, first_at):
    """Единственный таск, в окне startedAt…finishedAt (или до «сейчас») которого лежит `first_at`; иначе None."""
    at, now, hit = run_log._moment(first_at), dt.datetime.now(dt.timezone.utc), []
    for t in state.get("tickets") or []:
        lo, hi = run_log._moment(t.get("startedAt")), run_log._moment(t.get("finishedAt")) or now
        if at and lo and lo <= at <= hi and isinstance(t.get("id"), str):
            hit.append(t["id"])
    return hit[0] if len(hit) == 1 else None


def spend_subagents(state, transcript=None):
    """Расход субагентов за время прогона из `<журнал сессии без .jsonl>/subagents/` → строки расхода
    по агентам (числа, модель, agent_type, id агента, таск; без текста). Таск берётся из имени профиля,
    а по времени — только для исполнителей и general-purpose: ревьюеру чужой таск не приписывается.
    Повторный вызов не удваивает расход: читатели берут последнюю строку на `agent`."""
    miss = lambda why: "расход субагентов не найден: " + why
    try:
        if run_log is None:
            return miss("журнал прогона недоступен")
        path = transcript or session_transcript()
        if not path:
            return miss("нет журнала сессии в ~/.claude/projects (путь задаёт --transcript)")
        agents = run_log.usage_by_agent(os.path.splitext(path)[0] + os.sep + "subagents",
                                        state.get("startedAt"), dt.datetime.now(dt.timezone.utc))
        if not agents:
            return "расход субагентов: субагентов нет"
        def ticket_of(agent):
            role = run_log.role_of(agent.get("agent_type"))
            from_profile = executor_ticket(agent.get("agent_type"))
            if from_profile:
                return from_profile
            return _ticket_at(state, agent["first_at"]) if role in ("executor", "agent") else None
        saved = [run_log.append(A, "executor", run=state.get("dir"), role=run_log.role_of(a["agent_type"]),
                                source="subagent", origin="claude-subagents",
                                ticket=ticket_of(a),
                                **{k: v for k, v in a.items() if k != "first_at"}) for a in agents]
        if not all(saved):
            return "расход субагентов не записан: журнал прогона недоступен для записи"
        return "расход субагентов: %s ток. вход+выход, кэш чтение %s, агентов %d" % (
            sum(a["input"] + a["output"] for a in agents), sum(a["cache_read"] for a in agents), len(agents))
    except Exception as exc:
        return miss(type(exc).__name__)


def _minutes(start, end, waits=()):
    try:
        secs = (dt.datetime.fromisoformat(end) - dt.datetime.fromisoformat(start)).total_seconds()
        for w in waits:
            secs -= (dt.datetime.fromisoformat(w["to"]) - dt.datetime.fromisoformat(w["from"])).total_seconds()
    except (TypeError, ValueError, KeyError):
        return None
    return max(0, round(secs / 60))


def compute_history(records, current):
    """Прошлые сборки из архивных state.js своих папок: до 20, свежие первыми; битый файл пропущен.
    Токены — из журнала по имени прогона."""
    try:
        names = sorted(n for n in os.listdir(A) if RUN_DIR_NAME.fullmatch(n) and run_key(n) != run_key(current))
    except OSError:
        return []
    cache_path = os.path.join(A, HISTORY_CACHE)
    try:                                               # битый, чужой или отсутствующий кэш — пересчёт молча
        with open(cache_path, encoding="utf-8") as f:
            cached = json.load(f)
        cached = cached["items"] if cached["v"] == 1 and isinstance(cached["items"], dict) else {}
    except (OSError, ValueError, KeyError, TypeError):
        cached = {}
    items, found = {}, []
    for name in names:
        try:
            st = os.stat(os.path.join(A, name, "state.js"))
            key = [st.st_mtime_ns, st.st_size]
            hit = cached.get(name)
            if (isinstance(hit, dict) and hit.get("key") == key and isinstance(hit.get("row"), dict)
                    and hit["row"].get("dir") == name
                    and all(k in hit["row"] for k in ("title", "startedAt", "finishedAt", "minutes", "tickets",
                                                      "repairs", "result"))
                    and isinstance(hit["row"].get("title"), str)
                    and isinstance(hit["row"].get("tickets"), int)
                    and isinstance(hit["row"].get("repairs"), int)):   # неполная строка кэша — пересчёт
                row = hit["row"]
            else:
                old = state_io.read_state_file(os.path.join(A, name, "state.js"))
                tickets = [t for t in old.get("tickets") or [] if isinstance(t, dict)]
                row = {"dir": name, "title": str(old.get("title") or name),
                       "startedAt": old.get("startedAt"), "finishedAt": old.get("finishedAt"),
                       "minutes": _minutes(old["startedAt"], old["finishedAt"], old.get("waits") or [])
                       if old.get("startedAt") and old.get("finishedAt") else None,
                       "tickets": len(tickets),
                       "repairs": sum(t["repairs"] for t in tickets if isinstance(t.get("repairs"), int)),
                       "result": old.get("result")}
            items[name] = {"key": key, "row": row}
            tokens = sum(a["tokens"] for a in compute_spend(records, name)["byRole"].values())
            found.append(dict(row, tokens=tokens))
        except (state_io.StateError, OSError, TypeError, ValueError, AttributeError, KeyError):
            continue                                   # битый архив не мешает остальным
    if items != cached:
        tmp = "%s.%d.tmp" % (cache_path, os.getpid())
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"v": 1, "items": items}, f)
            os.replace(tmp, cache_path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    found.sort(key=lambda h: (str(h["startedAt"] or ""), h["dir"]), reverse=True)
    return found[:HISTORY_KEPT]


def log_failures():
    """Сколько строк журнала не записано: число в `.autopilot/run-log.fail`, нет файла — 0."""
    try:
        with open(RUN_LOG_FAIL, encoding="utf-8") as f:
            return max(0, int(f.read().strip()))
    except (OSError, ValueError):
        return 0


def refresh_audit(state):
    """state.spend, state.history, state.logFailures — для «Подробностей» дашборда."""
    records = run_log.read_all(A) if run_log else []
    try:
        state["spend"] = compute_spend(records, state.get("dir"))
        state["history"] = compute_history(records, state.get("dir"))
        state["spendLedger"] = run_log.spend_snapshot(records, state.get("dir")) if run_log else []
    except Exception:                                  # расход не должен ронять команду
        state["spend"], state["history"], state["spendLedger"] = {"byRole": {}, "byModel": {}, "byTicket": {}}, [], []
    state["logFailures"] = log_failures()


def main():
    argv = sys.argv[1:]
    # Справка ничего не трогает: ни state.js, ни гейты, ни сервер.
    if "--help" in argv or "-h" in argv or argv[:1] == ["help"]:
        print(__doc__.strip())
        return
    if "--stop-now" in argv:
        i = argv.index("--stop-now")
        if len(argv) <= i + 2:
            die("stop-now требует ожидаемые PID и порт")
        stop_now(int(argv[i + 1]), int(argv[i + 2]))
        return
    pos, opt, multi = parse_args(argv)
    cmd = pos[0] if pos else ""
    if cmd == "claude-version":
        sys.exit(cmd_claude_version(opt))
    if cmd == "git-check":
        sys.exit(cmd_git_check())
    if cmd == "agents":
        sys.exit(cmd_agents(pos[1:], opt))
    notes, landed = [], None
    if cmd == "init":
        state, notes = cmd_init(opt)
        notes += [n for n in [lessons_note()] if n]
    else:
        state = read_state()
        if state is None:
            die("state.js ещё нет — начни с `ap.py init`")
        rest = pos[1:]
        if cmd == "plan-models":
            if rest:
                die("plan-models: лишние аргументы")
            state["updatedAt"] = now()
            payload = cmd_plan_models(state, opt)
            records = run_log.read_all(A) if run_log else []
            advice, guess = history_advice(records), forecast(records, state["tickets"])
            if advice:
                payload["advice"] = advice                 # только совет: маршрут не меняется
            if guess:
                payload["forecast"] = guess
            beat(state)
            save(state)
            write_snapshot(state)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        if cmd == "schedule":
            if rest:
                die("schedule: лишние аргументы")
            raw_limit = str(opt.get("max-parallel", "1" if state.get("sequentialHost") else "2"))
            if not re.fullmatch(r"[1-3]", raw_limit):
                die("schedule: --max-parallel допускает 1, 2 или 3")
            if state.get("sequentialHost") and raw_limit != "1":
                die("schedule: sequential-host допускает только --max-parallel 1")
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
        if cmd == "opus" and rest != ["approve"]:
            if rest not in (["propose"], ["status"]):
                die(OPUS_USAGE)
            print("\n".join(opus_propose(state) if rest == ["propose"] else opus_status(state)))
            return                                    # только печать: state.js не трогаем
        if cmd == "url":
            if rest:
                die("url: лишние аргументы")
            port, _ = recorded()
            if not port or (not server_is_ours(port) and ping_reply(port) is not None):   # токен сменился — сервер поднимется заново
                serve(state)
                port, _ = recorded()
            print(page_url(port) if port else "сервера нет — дашборд открывается файлом: %s" % PAGE)
            return                                    # только печать: state.js не трогаем
        if cmd == "spend-orchestrator":
            print(spend_orchestrator(state, opt["transcript"] if isinstance(opt.get("transcript"), str) else None))
            return                                    # только журнал расхода: state.js не трогаем
        if cmd == "spend-subagents":
            print(spend_subagents(state, opt["transcript"] if isinstance(opt.get("transcript"), str) else None))
            return                                    # только журнал расхода: state.js не трогаем
        if cmd == "agent-for":
            print(cmd_agent_for(state, rest, opt))
            return                                    # только печать: state.js не трогаем
        if cmd == "ticket" and rest[-1:] == ["bundle"]:
            print(cmd_bundle(state, rest[:-1]))
            return                                        # только печать
        if cmd == "silence":
            sys.exit(cmd_silence(opt))                    # только чтение: state.js не трогаем
        if cmd == "lessons":
            sys.exit(cmd_lessons(state, rest, opt))       # state.js не трогаем
        if cmd == "profile":
            cmd_profile(state, rest)
            return
        if cmd == "check-review-report":
            sys.exit(cmd_check_review_report(opt))        # только чтение файла: state.js не трогаем
        if cmd == "check-bypass":
            sys.exit(cmd_check_bypass(pos))               # только печать: state.js не трогаем
        if cmd == "plan-fact" and rest[:1] != ["record"]:
            print("\n".join(cmd_plan_fact(state, rest, multi)))
            return                                        # list и show только печатают
        if cmd == "chore":
            sys.exit(cmd_chore(state, rest))              # коммитит сам; state.js не трогаем
        if cmd == "upgrade-tools":
            if rest:
                die("upgrade-tools: лишние аргументы")
            try:
                done = upgrade_tools(state)
            except UntrustedSkillDir as exc:
                die("upgrade-tools: %s" % exc)
            except OSError as exc:
                die("upgrade-tools: инструменты не обновлены (%s)" % exc)
            finish_self_upgrade()
            print("обновлено: " + ", ".join(done) if done else "инструменты в .autopilot/ уже совпадают с навыком")
            return                                    # state.js не трогаем
        if cmd not in ("", "sync", "commits"):
            # Время события ставится до команды: ей самой и ленте нужна одна метка.
            state["updatedAt"] = now()
            beat(state)
        if cmd in MOVES_ON:
            close_wait(state)
        if cmd == "execution":
            notes.append(cmd_execution(state, rest, opt))
        elif cmd == "stage":
            notes += upgrade_note(state)
            cmd_stage(state, rest, opt)
            import silence
            notes += ["! стадия %s идёт %d мин — проверь, не завис ли агент (`ap.py silence`)" % x
                      for x in silence.long_stages(state.get("stages"), 60)]
        elif cmd == "ticket":
            landed = cmd_ticket(state, rest, opt)
        elif cmd == "tickets":
            notes.append(publish_tickets(state))
            log(state, "tickets", n=len(state.get("tickets") or []))
        elif cmd == "check-plan":
            previous_contract = state.get("planContractDigest")
            was_g3_accepted = state.get("gates", {}).get("G3", {}).get("ok") is True
            problems = check_plan(state)
            notes += ["! " + p for p in problems] or ["G3: трасса сходится"]
            current_contract = plan_contract_digest(state) if not problems else None
            set_gate(state, "G3", not problems, problems=len(problems))
            if ((previous_contract is not None or was_g3_accepted)
                    and previous_contract != current_contract):
                # Replacing a verified plan also invalidates earlier spec,
                # coverage and blind acceptance, not only the G3 snapshot.
                # Legacy 2.3-dev runs with G3 true but no contract requalify.
                for gate in ("G1", "G2", "G4"):
                    set_gate(state, gate, False, reason="plan-changed")
                state["blind"] = None
            if not problems:
                state["planContractDigest"] = current_contract
                state["planValidationDigest"] = plan_validation_digest(state)
            else:
                state.pop("planContractDigest", None)
                state.pop("planValidationDigest", None)
        elif cmd == "opus":
            notes += opus_approve(state, opt)
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
        elif cmd == "blocker":
            cmd_blocker(state, rest, opt)
        elif cmd == "plan-fact":
            notes += cmd_plan_fact(state, rest, multi)
        elif cmd in ("coverage", "blind"):
            cmd_numbers(state, cmd, rest, multi)
        elif cmd == "tests":
            state["tests"] = tests_pair(rest[0] if rest else "")
            seconds = opt.get("seconds")
            if seconds is not None:
                try:
                    seconds = float(seconds)
                except (TypeError, ValueError):
                    die("--seconds — число секунд, например 42.5")
                seconds = int(seconds) if seconds.is_integer() else round(seconds, 1)
            log(state, "tests", journal={"seconds": seconds}, **state["tests"])
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
    refresh_audit(state)
    save(state)
    snap = write_snapshot(state)
    if cmd in ("init", "stage", "finish"):
        note = refresh_dashboard(state)
        if note:
            notes.append(note)
    if cmd == "finish" or opt.get("stop"):
        srv = stop_later()
    elif opt.get("no-serve"):
        srv = "сервер не проверялся"
    else:
        srv = serve(state)
    if cmd == "init" or (cmd == "stage" and pos[1:2] in (["build"], ["review"], ["final"]) and pos[2:3] in ([], ["start"])):
        hint = context_hint()
        if hint:
            notes.append(hint)
    r = state.get("requirements") or {}
    lines = ["%s · %s · требований %s, готово %s" % (snap, srv, r.get("total", 0), r.get("done", 0))]
    lines += ["  " + (line if line[:1] in ("!", "?", "↑") else "· " + line) for line in notes]
    lines += ["  ! " + line for line in audit(state)[:5]]
    if "land" in pos[1:] and isinstance(landed, str):
        lines.insert(1, "  · " + landed)
    print("\n".join(lines[:5] if cmd == "ticket" and "land" in pos[1:] else lines))     # посадка таска — не длиннее пяти строк
    try:
        finish_self_upgrade()
    except OSError as exc:
        print("  ! ap.py не обновлён (%s): запусти `ap.py upgrade-tools`" % type(exc).__name__)
    if cmd == "check-plan" and problems:
        sys.exit(2)
    if opt.get("check-update"):
        note = check_update(state)
        if note:
            print("  ↑ " + note)


def compute_model_report(records, run):
    """По каждой модели: таски, доля сданных с первого раза, починки, токены на таск.
    Модель таска — у его последнего запуска исполнителя (эскалация Haiku → Sonnet — на Sonnet);
    нет строки расхода или в ней нет модели — «не указана»."""
    tickets, usage = {}, {}
    for r in records:
        if not (isinstance(r, dict) and r.get("k") == "ticket" and run_key(r.get("run")) == run_key(run)):
            continue
        tid = r.get("id")
        if not isinstance(tid, str):
            continue
        t = tickets.setdefault(tid, {"done": False, "again": False, "repairs": 0})
        if r.get("act") == "done":
            t["done"] = True
        elif r.get("act") == "repair":
            t["repairs"] += 1
            t["again"] = True
        elif r.get("act") in ("retry", "fail"):
            t["again"] = True
    model = {}
    for r in executor_rows(records, run):
        tid = row_ticket(r)
        if tid in tickets:
            model[tid] = r.get("model") if isinstance(r.get("model"), str) and r.get("model") else UNKNOWN_MODEL
            usage[tid] = usage.get(tid, 0) + _tokens(r, "input") + _tokens(r, "output")
    rows = {}
    for tid, t in tickets.items():
        m = rows.setdefault(model.get(tid, UNKNOWN_MODEL),
                            {"model": model.get(tid, UNKNOWN_MODEL), "tickets": 0, "first": 0, "repairs": 0, "tokens": 0})
        m["tickets"] += 1
        m["first"] += 1 if t["done"] and not t["again"] else 0
        m["repairs"] += t["repairs"]
        m["tokens"] += usage.get(tid, 0)
    return sorted(rows.values(), key=lambda m: m["model"])


def render_model_report(rows):
    lines = ["", "## Модели", "| модель | тасков | сдано с первого раза | починок | токенов на таск |",
             "|---|---|---|---|---|"]
    lines += ["| %s | %d | %d%% | %d | %d |" % (m["model"], m["tickets"], round(100 * m["first"] / m["tickets"]),
                                                  m["repairs"], round(m["tokens"] / m["tickets"])) for m in rows]
    return lines if rows else lines + ["| — | 0 | — | 0 | — |"]


def model_family(name):
    """`claude-sonnet-5-5` и `sonnet` → `sonnet`; haiku/sonnet/opus, иначе имя как есть; нет → «не указан»."""
    if not isinstance(name, str) or not name:
        return "не указан"
    low = name.casefold()
    return next((f for f in ("haiku", "sonnet", "opus") if f in low), low)


def compute_class_report(records):
    """Класс × модель × усилие по всему журналу (все прогоны): таски, с первого раза, дозапросы,
    эскалации Haiku → Sonnet, токены. Таск — пара (прогон, номер); сочетание берётся из его строки
    `start` (строки без полей — «не указан»); токены — по строкам расхода таска."""
    tickets = {}
    for r in records:
        if isinstance(r, dict) and r.get("k") == "ticket" and isinstance(r.get("id"), str):
            t = tickets.setdefault((run_key(r.get("run")), r["id"]), {"combo": None, "done": False, "again": False,
                                                                       "retries": 0, "esc": 0, "tokens": 0})
            act = r.get("act")
            if act == "start" and (t["combo"] is None or r.get("class") or r.get("model") or r.get("effort")):
                t["combo"] = (r.get("class") or "не указан", model_family(r.get("model")), r.get("effort") or "не указано")
            t["done"] = t["done"] or act == "done"
            t["again"] = t["again"] or act in ("retry", "fail", "repair")
            t["retries"] += act == "retry"
            t["esc"] += act == "escalate"
    for run in {k[0] for k in tickets}:
        for r in executor_rows(records, run):
            t = tickets.get((run, row_ticket(r)))
            if t:
                t["tokens"] += _tokens(r, "input") + _tokens(r, "output")
    rows = {}
    for t in tickets.values():
        c = t["combo"] or ("не указан", "не указан", "не указано")
        a = rows.setdefault(c, dict(zip(("class", "model", "effort"), c), tickets=0, first=0, retries=0, esc=0, tokens=0))
        a["tickets"] += 1
        a["first"] += t["done"] and not t["again"]
        a["retries"] += t["retries"]
        a["esc"] += t["esc"]
        a["tokens"] += t["tokens"]
    return sorted(rows.values(), key=lambda a: (a["class"], a["model"], a["effort"]))


def render_class_report(rows):
    """Блок «Класс × модель × усилие»; нет тасков — нет блока. Названий тасков в нём нет."""
    if not rows:
        return []
    lines = ["", "## Класс × модель × усилие",
             "| класс | модель | усилие | тасков | сдано с первого раза | дозапросов | эскалаций Haiku → Sonnet | токенов на таск |",
             "|---|---|---|---|---|---|---|---|"]
    return lines + ["| %s | %s | %s | %d | %d%% | %d | %d | %d |" % (
        a["class"], a["model"], a["effort"], a["tickets"], round(100 * a["first"] / a["tickets"]),
        a["retries"], a["esc"], round(a["tokens"] / a["tickets"])) for a in rows]


def history_advice(records):
    """Одна строка совета из истории или None: сколько механических тасков на Haiku эскалировано."""
    rows = [a for a in compute_class_report(records) if a["class"] == "механический" and a["model"] == "haiku"]
    n = sum(a["tickets"] for a in rows)
    return ("история: механических тасков на Haiku %d, эскалировано на Sonnet %d; совет не меняет маршрут"
            % (n, sum(a["esc"] for a in rows))) if n else None


def forecast(records, tickets):
    """Одна строка оценки плана или None: по классам тасков плана (`route_fields`) берёт средние токены и
    минуты (от первого `start` до последнего `done`) из журнала. Класса в истории нет — таск не считается."""
    tok, mins, span = {}, {}, {}
    for a in compute_class_report(records):
        n, s = tok.get(a["class"], (0, 0))
        tok[a["class"]] = (n + a["tickets"], s + a["tokens"])
    for r in records:
        if isinstance(r, dict) and r.get("k") == "ticket" and isinstance(r.get("id"), str):
            s = span.setdefault((run_key(r.get("run")), r["id"]), {})
            if r.get("act") == "start":
                s.setdefault("start", r.get("t"))
                s["class"] = r.get("class") or s.get("class")
            elif r.get("act") == "done":
                s["end"] = r.get("t")
    for s in span.values():
        m = _minutes(s.get("start"), s.get("end")) if s.get("class") and s.get("start") and s.get("end") else None
        if m is not None:
            n, total = mins.get(s["class"], (0, 0))
            mins[s["class"]] = (n + 1, total + m)
    known = [c for c in (route_fields(tk)["class"] for tk in tickets) if tok.get(c, (0, 0))[1] > 0]
    if not known:
        return None
    tokens = sum(tok[c][1] / tok[c][0] for c in known)
    minutes = sum(mins[c][1] / mins[c][0] for c in known if c in mins)
    return ("оценка по истории (не обещание): %d тасков, ≈%d токенов%s; оценено %d из %d"
            % (len(tickets), round(tokens), ", ≈%d минут" % round(minutes) if minutes else "", len(known), len(tickets)))


def cmd_report_run(argv):
    """Свод журнала: читает только run-log.jsonl, без блокировки и без state.js."""
    if run_log is None:
        print("журнал недоступен: " + RUN_LOG_WARNING)
        return 0
    records, unreadable = run_log.read_all_stats(A)
    if not records:
        print("журнал прогона пуст: .autopilot/run-log.jsonl ещё не создан")
        return 0
    runs = [r["run"] for r in records if isinstance(r.get("run"), str) and r["run"]]
    if not runs:
        print("в журнале нет записей с номером прогона")
        return 0
    summary = run_log.summarize(records, run=runs[-1], skipped=unreadable)
    print(run_log.render_report(summary, share="--share" in argv), end="")
    print("\n".join(render_model_report(compute_model_report(records, runs[-1]))
                     + render_class_report(compute_class_report(records))))
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--serve"] and len(sys.argv) == 3 and sys.argv[2].isdigit():
        run_server(int(sys.argv[2]))                  # без state.lock: сервер живёт долго
    elif "--stop-now" in sys.argv:
        main()
    elif sys.argv[1:2] == ["report-run"]:
        sys.exit(cmd_report_run(sys.argv[2:]))
    elif sys.argv[1:2] in (["bootstrap"], ["doctor"]) and "--help" not in sys.argv:
        # из папки навыка: без state.lock (иначе он появится в tools/ навыка) и без state.js проекта
        _opt = parse_args(sys.argv[2:])[1]
        sys.exit(cmd_bootstrap(_opt) if sys.argv[1] == "bootstrap" else cmd_doctor(_opt))
    else:
        with locked_state():
            main()
