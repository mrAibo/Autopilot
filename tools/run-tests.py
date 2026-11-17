#!/usr/bin/env python3
"""Параллельный запуск тестов репозитория (только стандартная библиотека).

    python tools/run-tests.py [-j N] [--list]

Тесты делятся между N процессами (по умолчанию — число ядер): файлы по классам, большие
классы — по кускам методов. Классы с атрибутом `serial = True` (или из SERIAL ниже) идут
отдельным процессом после параллельных. Итог — в формате unittest:
`Ran N tests in X.XXXs` и `OK (skipped=S)` либо `FAILED (failures=F, errors=E, skipped=S)`;
код выхода 1 при падении. `python -m unittest discover -s tests` остаётся основной командой CI.
"""
import argparse
import os
import re
import subprocess
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, "tests")

# Классы с общим ресурсом, где нельзя дописать `serial = True` (файл тестов чужой зоны):
# порт, взятый через bind(0) и отданный дочернему процессу, — гонка при параллельном прогоне.
SERIAL = {"test_ap_audit.Server", "test_otel_tools.SinkTests"}
# Файлы, где каждый тест несколько раз запускает ap.py отдельным процессом: вес выше.
HEAVY_FILES = {"test_ap", "test_ap_escalation", "test_one_command", "test_controller"}
HEAVY_WEIGHT = 10
CHUNK = 8  # больше тестов в одном классе — дробим на куски по методам


def _walk(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _walk(t)
        else:
            yield t


def collect(tests_dir=TESTS):
    """-> {"module.Class": ([method, ...], serial)}; ошибки импорта идут как класс _FailedTest."""
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    suite = unittest.defaultTestLoader.discover(tests_dir, top_level_dir=tests_dir)
    found = {}
    for t in _walk(suite):
        cls = type(t)
        key = "%s.%s" % (cls.__module__, cls.__name__)
        methods, _ = found.setdefault(key, ([], bool(getattr(cls, "serial", False)) or key in SERIAL))
        methods.append(t._testMethodName)
    return found


def make_units(found):
    """-> (parallel, serial): списки (weight, [test id, ...])."""
    parallel, serial = [], []
    for key, (methods, is_serial) in sorted(found.items()):
        w = HEAVY_WEIGHT if key.split(".")[0] in HEAVY_FILES else 1
        if is_serial:
            serial.append((w * len(methods), [key]))
        elif len(methods) > CHUNK:
            for i in range(0, len(methods), CHUNK):
                part = methods[i:i + CHUNK]
                parallel.append((w * len(part), ["%s.%s" % (key, m) for m in part]))
        else:
            parallel.append((w * len(methods), [key]))
    return parallel, serial


def plan(units, n):
    """Жадное деление: самый тяжёлый кусок — в самую лёгкую группу. -> список списков id."""
    groups = [[0, []] for _ in range(max(1, n))]
    for w, ids in sorted(units, key=lambda u: -u[0]):
        g = min(groups, key=lambda g: g[0])
        g[0] += w
        g[1].extend(ids)
    return [g[1] for g in groups if g[1]]


_RAN = re.compile(r"^Ran (\d+) tests? in", re.M)
_FAILED = re.compile(r"^FAILED \((.*)\)", re.M)
_OK = re.compile(r"^OK(?: \((.*)\))?$", re.M)


def parse_summary(text):
    """Вывод unittest -> {"ran", "failures", "errors", "skipped"} или None, если итога нет."""
    ran = _RAN.search(text)
    if not ran:
        return None
    res = {"ran": int(ran.group(1)), "failures": 0, "errors": 0, "skipped": 0}
    m = _FAILED.search(text) or _OK.search(text)
    for k, v in re.findall(r"(\w+)=(\d+)", m.group(1) or "" if m else ""):
        if k in res:
            res[k] = int(v)
    return res


def combine(results):
    """Складывает итоги процессов (None — процесс упал без итога: одна ошибка)."""
    total = {"ran": 0, "failures": 0, "errors": 0, "skipped": 0}
    for r in results:
        if r is None:
            total["errors"] += 1
            continue
        for k in total:
            total[k] += r[k]
    return total


def format_summary(total, seconds):
    out = "Ran %d tests in %.3fs\n\n" % (total["ran"], seconds)
    bad = total["failures"] + total["errors"]
    parts = []
    if bad:
        parts += ["failures=%d" % total["failures"], "errors=%d" % total["errors"]]
    if total["skipped"]:
        parts.append("skipped=%d" % total["skipped"])
    if bad:
        return out + "FAILED (%s)" % ", ".join(parts)
    return out + "OK" + (" (%s)" % ", ".join(parts) if parts else "")


def run_group(ids):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [TESTS, os.environ.get("PYTHONPATH")])))
    p = subprocess.run([sys.executable, "-m", "unittest", "-q"] + ids, cwd=ROOT, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       encoding="utf-8", errors="replace")
    return parse_summary(p.stdout), p.returncode, p.stdout


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-j", type=int, default=os.cpu_count() or 1, help="число процессов (по умолчанию — ядра)")
    ap.add_argument("--list", action="store_true", help="показать разбиение на группы и выйти")
    args = ap.parse_args(argv)
    parallel, serial = make_units(collect())
    groups = plan(parallel, args.j)
    if args.list:
        for i, g in enumerate(groups, 1):
            print("parallel %d: %d ids" % (i, len(g)))
        print("serial: %s" % (", ".join(i for _, ids in serial for i in ids) or "-"))
        return 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=len(groups) or 1) as pool:
        outs = list(pool.map(run_group, groups))
    if serial:
        outs.append(run_group([i for _, ids in serial for i in ids]))
    for summary, code, text in outs:
        if summary is None or code != 0:
            print(text, file=sys.stderr)
    total = combine(o[0] for o in outs)
    print("\n" + format_summary(total, time.time() - start), file=sys.stderr)
    return 1 if (total["failures"] or total["errors"] or any(o[1] for o in outs)) else 0


if __name__ == "__main__":
    sys.exit(main())
