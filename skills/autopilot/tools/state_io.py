#!/usr/bin/env python3
"""Чтение и запись .autopilot/state.js — единственное место, знающее формат обёртки.

Файл — это `window.STATE = {…};`. Разбор терпим к BOM (Блокнот Windows), к отсутствию
префикса и к хвостовому `;`. Запись идёт через `.tmp` и замену с повтором: на Windows
дашборд читает файл раз в 10 с, и `os.replace` в этот момент может получить WinError 5/32.
Что делать с `StateError`, решает вызывающий: ap — die, controller — ControllerError,
guard — deny.
"""

import json
import os
import time
from pathlib import Path

WINDOWS = os.name == "nt"


class StateError(Exception):
    pass


def parse_state_text(text):
    """Текст state.js → dict. Пусто, мусор, не объект → StateError."""
    body = text.lstrip(chr(0xFEFF)).strip()  # BOM
    if not body:
        raise StateError("state.js пуст")
    if not body.startswith("{"):
        head, sep, body = body.partition("=")
        if not sep or "STATE" not in head:
            raise StateError("state.js: нет префикса window.STATE =")
    try:
        data = json.loads(body.strip().rstrip(";"))
    except ValueError as exc:
        line = getattr(exc, "lineno", "?")
        msg = getattr(exc, "msg", str(exc))
        raise StateError("state.js не разбирается (строка %s: %s)" % (line, msg)) from exc
    if not isinstance(data, dict):
        raise StateError("state.js: ожидался объект")
    return data


def read_state_file(path):
    """Читает и разбирает файл; нет файла или порча → StateError."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise StateError("state.js не прочитан: %s" % exc) from exc
    except UnicodeDecodeError as exc:
        raise StateError("state.js не в utf-8") from exc
    return parse_state_text(text)


def replace_with_retry(src, dst, *, windows=None, attempts=12):
    """os.replace с коротким ограниченным повтором при WinError 5/32 (читатель держит файл).

    Другие ошибки не повторяются; по исчерпании попыток исключение уходит наверх.
    """
    if windows is None:
        windows = WINDOWS
    for attempt in range(attempts):
        try:
            os.replace(src, dst)
            return
        except OSError as exc:
            if (not windows or getattr(exc, "winerror", None) not in (5, 32)
                    or attempt == attempts - 1):
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.05))


def write_state_file(path, state, *, prefix="window.STATE = "):
    """Атомарно пишет state; при провале `.tmp` удаляется, поднимается StateError."""
    path = os.fspath(path)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(prefix + json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        replace_with_retry(tmp, path)
    except OSError as exc:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise StateError("state.js не записан (файл занят?): %s — повтори команду" % exc) from exc
