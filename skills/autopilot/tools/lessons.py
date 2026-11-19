"""Уроки сборки (`.autopilot/lessons.md`) и профиль проекта (`.autopilot/profile.md`).
Пишет только в `.autopilot/`; урок без секретов, абсолютных путей и переводов строки."""
import datetime as dt
import hashlib
import json
import os
import re

LESSONS_LIMIT_BYTES = 2048
DEFAULT_MAX = 5
SECRET = re.compile(
    r"\b(?:sk|rk|pk)[-_](?:live_|test_)?[A-Za-z0-9_-]{10,}|\bgh[pos]_[A-Za-z0-9]{20,}|\bgithub_pat_\w{20,}"
    r"|\b(?:AKIA|ASIA)[0-9A-Z]{12,}|\bAIza[\w-]{20,}|\bya29\.[\w.-]{10,}|\bxox[bpa]-[\w-]{10,}"
    r"|\b\d{8,10}:[A-Za-z0-9_-]{35}\b|\beyJ[\w-]{5,}\.[\w-]{5,}|\w+://[^\s/:@]+:[^\s/@]+@\S+"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:key|token|secret|password|ключ|токен|пароль|доступ)\W{0,3}[A-Za-z0-9+/=]{32,}")
ABS_PATH = re.compile(r"(?<![\w.])(?:[A-Za-z]:[/\x5c]|/(?:Users|home)/)")


def check_text(text):
    """Причина отказа или None."""
    if "\n" in text or "\r" in text:
        return "урок в одну строку"
    if SECRET.search(text):
        return "похоже на секрет"
    if ABS_PATH.search(text):
        return "абсолютный путь вне проекта"
    return None


def _lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [x.rstrip("\n") for x in f if x.startswith("- ")]
    except OSError:
        return []


def _digest(text):
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()


def add(path, items, max_items=DEFAULT_MAX):
    """Дописывает `- ДАТА — текст`; → причины отказа (секрет, путь, уже было). Удалённый урок не возвращается:
    хеши записанного лежат рядом в `<файл>.seen`."""
    seen_path = path + ".seen"
    try:
        with open(seen_path, encoding="utf-8") as f:
            seen = set(f.read().split())
    except OSError:
        seen = set()
    refused, fresh = [], []
    for text in items:
        text = text.strip()
        why = check_text(text) or ("уже было" if _digest(text) in seen else None)
        if why:
            refused.append("%s (урок %d)" % (why, len(refused) + len(fresh) + 1))   # текст не печатаем: в нём может быть секрет
        elif len(fresh) < max_items:
            fresh.append(text)
    if fresh:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        today = dt.date.today().isoformat()
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write("".join("- %s — %s\n" % (today, t) for t in fresh))
        with open(seen_path, "a", encoding="utf-8", newline="\n") as f:
            f.write("".join(_digest(t) + "\n" for t in fresh))
    return refused


def render(path, limit=LESSONS_LIMIT_BYTES):
    """Новые первыми, целиком влезающие в `limit` байт; старое выпадает; нет файла — пусто."""
    out, size = [], 0
    for line in reversed(_lines(path)):
        size += len(line.encode("utf-8")) + 1
        if size > limit:
            break
        out.append(line)
    return "\n".join(out)


def drop(path, n):
    """Удаляет n-ю строку (1 — самая новая)."""
    try:
        with open(path, encoding="utf-8") as f:
            rows = f.read().splitlines()
    except OSError:
        return False
    idx = [i for i, x in enumerate(rows) if x.startswith("- ")]
    if not 1 <= n <= len(idx):
        return False
    del rows[idx[-n]]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(x + "\n" for x in rows))
    return True


def candidates(state, max_items=DEFAULT_MAX):
    """Сырьё для уроков: замечания, таски с повторами или починками, не подтверждённые блокеры."""
    out = [str(c) for c in state.get("concerns") or []]
    for tk in state.get("tickets") or []:
        if (tk.get("retries") or 0) > 0 or (tk.get("repairs") or 0) > 0:
            out.append("таск %s «%s»: повторов %s, починок %s" % (tk.get("id"), tk.get("title", ""),
                                                                tk.get("retries") or 0, tk.get("repairs") or 0))
    out += ["не подтверждено: " + b.get("text", "") for b in state.get("blockingFindings") or []
            if b.get("status") == "downgraded"]
    return out[:max_items]


def _section(text, title, rows):
    body, inside = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            inside = line.lstrip("# ").strip().lower().startswith(title)
            continue
        if inside and line.strip():
            body.append(line)
    return body[:rows]


def profile_text(root, check=None):
    """Страница профиля: команды, стек, подводные камни (до 15 строк)."""
    try:
        with open(os.path.join(root, "AGENTS.md"), encoding="utf-8") as f:
            agents = f.read()
    except OSError:
        agents = ""
    rows = ["# Профиль проекта", "", "## Команды"]
    if check:
        rows.append("- полная проверка: `%s`" % check)
    rows += [x for x in _section(agents, "команды", 15) if x.startswith("|") and not x.startswith("|--")]
    try:
        with open(os.path.join(root, "package.json"), encoding="utf-8") as f:
            scripts = json.load(f).get("scripts") or {}
    except (OSError, ValueError, AttributeError):
        scripts = {}
    for name, cmd in (("build", "npm run build"), ("test", "npm test")):
        if isinstance(scripts.get(name), str):
            rows.append("- `%s` (%s)" % (cmd, scripts[name]))
    stack = [n for n in ("pyproject.toml", "package.json", "go.mod", "Cargo.toml") if os.path.isfile(os.path.join(root, n))]
    rows += ["", "## Стек", ", ".join(stack) or "не определён", "", "## Подводные камни"]
    rows += _section(agents, "подводные", 15) or ["—"]
    return "\n".join(rows) + "\n"


def refresh_profile(root, check=None):
    """Пишет `.autopilot/profile.md`, только если текст изменился → записано ли."""
    path = os.path.join(root, ".autopilot", "profile.md")
    text = profile_text(root, check)
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == text:
                return False
    except OSError:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True
