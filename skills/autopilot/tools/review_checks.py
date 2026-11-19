"""Проверки ревью: чек-лист рисков в отчёте и сигналы обхода замечаний в диффе.

Только стандартная библиотека; ничего не пишет и не запускает. Сигнал обхода — подсказка, не отказ.
"""
import re

CHECKLIST = ("инварианты", "токены и деньги", "статусы и переходы", "сбой посередине", "гонки", "права и подписи")

_SKIP = re.compile(r"@unittest\.skip|skipTest\(|pytest\.mark\.(skip|xfail)|--no-verify|#\s*noqa", re.I)
_ASSERT = re.compile(r"\bassert\b|self\.assert\w*\(")


def missing_checklist(report_text):
    """Пункты чек-листа, на которые в отчёте нет строки `<пункт>: <ответ>` (допустимы `-`, `*`, `**`)."""
    out = []
    for name in CHECKLIST:
        pat = re.compile(r"^[ \t]*(?:[-*][ \t]+)?\**%s\**[ \t]*:[ \t]*\**[ \t]*\S" % re.escape(name), re.I | re.M)
        if not pat.search(report_text):
            out.append(name)
    return out


def bypass_lines(diff_text):
    """Добавленные строки с skip/xfail/--no-verify/noqa и удалённые assert без добавленной замены."""
    out, added_asserts, removed = [], 0, []
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            body = line[1:]
            if _SKIP.search(body):
                out.append("добавлено: " + body.strip())
            if _ASSERT.search(body):
                added_asserts += 1
        elif line.startswith("-") and _ASSERT.search(line[1:]):
            removed.append(line[1:].strip())
    # shortcut: замена считается по числу строк assert, не по смыслу; точнее — только ручным ревью
    out += ["удалено: " + r for r in removed[added_asserts:]]
    return out
