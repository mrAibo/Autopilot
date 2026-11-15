#!/usr/bin/env python3
"""Число тестов unittest и его подстановка в документы.

    python3 skills/autopilot/tools/test_count.py            # напечатать число
    python3 skills/autopilot/tools/test_count.py --write    # подставить между маркерами
    python3 skills/autopilot/tools/test_count.py --check    # код 1, если в документах другое число

Маркеры: <!-- tests:count -->N<!-- /tests:count --> в AGENTS.md и трёх README. Файл без маркеров
не меняется. Тесты только собираются (countTestCases), не запускаются: пропущенные входят в число.
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FILES = ("AGENTS.md", "README.md", "README.ru.md", "README.de.md")
MARKERS = re.compile(r"(<!-- tests:count -->)(.*?)(<!-- /tests:count -->)", re.S)


def count(root=ROOT):
    """Сколько тестов соберёт `unittest discover -s tests` в корне проекта."""
    start = os.path.join(root, "tests")
    return unittest.defaultTestLoader.discover(start).countTestCases()


def substitute(text, number):
    """-> (новый текст, число найденных маркеров); без маркеров текст тот же."""
    return MARKERS.subn(lambda m: "%s%d%s" % (m.group(1), number, m.group(3)), text)


def stale(root, number):
    """Файлы, где маркеров нет или число в них другое."""
    bad = []
    for name in FILES:
        with open(os.path.join(root, name), encoding="utf-8", newline="") as stream:
            found = MARKERS.findall(stream.read())
        if not found or any(m[1] != str(number) for m in found):
            bad.append(name)
    return bad


def write(root, number):
    """Подставить число; -> {файл: сколько маркеров обновлено}. Файл без маркеров не переписывается."""
    done = {}
    for name in FILES:
        path = os.path.join(root, name)
        with open(path, encoding="utf-8", newline="") as stream:   # newline="": окончания строк сохраняются
            text = stream.read()
        new, hits = substitute(text, number)
        done[name] = hits
        if hits and new != text:
            with open(path, "w", encoding="utf-8", newline="") as stream:
                stream.write(new)
    return done


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    number = count()
    if "--write" in argv:
        for name, hits in write(ROOT, number).items():
            print("%s: %s" % (name, "%d маркер(ов)" % hits if hits else "маркеров нет, файл не тронут"))
    elif "--check" in argv:
        bad = stale(ROOT, number)
        if bad:
            print("число тестов %d не совпадает или нет маркеров: %s" % (number, ", ".join(bad)))
            return 1
    print(number)
    return 0


if __name__ == "__main__":
    sys.exit(main())
