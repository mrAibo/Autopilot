"""Виды работы сборки: quick | bug | task | refactor. Только правила; запуск команд и состояние — в ap.py."""
import re

KINDS = ("quick", "bug", "task", "refactor")
DEFAULT_KIND = "task"
QUICK_MAX_TICKETS = 1
QUICK_MAX_REQUIREMENTS = 3
REPRO = "воспроизведение"
_TEST = re.compile(r"(^|/)(tests?|__tests__|spec)(/|$)|(^|/)test_[^/]*$|_test\.[^/]+$|\.(test|spec)\.[^/]+$")


def normalize(value):
    """None/пусто -> task; вне списка -> ValueError."""
    if value is None or value == "":
        return DEFAULT_KIND
    if not isinstance(value, str) or value not in KINDS:
        raise ValueError("вид работы: одно из %s" % ", ".join(KINDS))
    return value


def of_state(state):
    """Вид сборки из state.js; нет поля или мусор — task."""
    try:
        return normalize(state.get("kind"))
    except ValueError:
        return DEFAULT_KIND


def is_test_path(path):
    return bool(_TEST.search(path.replace("\\", "/")))


def plan_problems(kind, tickets, manifest_rows=None):
    """Отказы check-plan для вида; fix-таски `F…` вызывающий отфильтровывает."""
    out = []
    if kind == "quick":
        if len(tickets) > QUICK_MAX_TICKETS:
            out.append("quick: таск должен быть один (предел %d), а их %d" % (QUICK_MAX_TICKETS, len(tickets)))
        if manifest_rows is not None and manifest_rows > QUICK_MAX_REQUIREMENTS:
            out.append("quick: в манифесте %d строк при пределе %d — это не мелкая правка, вид task"
                       % (manifest_rows, QUICK_MAX_REQUIREMENTS))
    elif kind == "bug":
        repro = [t for t in tickets if t.get("repro")]
        if len(repro) != 1 or repro[0].get("blockedBy"):
            out.append("bug: нужен ровно один таск `**Вид:** воспроизведение` без зависимостей")
    elif kind == "refactor":
        for t in tickets:
            if not t.get("testsEdit") and any(is_test_path(z) for z in t.get("zone") or []):
                out.append("refactor: у таска %s зона в тестах без строки `**Правка тестов:** причина`" % t["id"])
    return out


def land_problems(kind, ticket, changed_files, tracked_tests, redproof, tickets=()):
    """Отказы `ticket NN land` для вида. bug — снимает `--by-user`; refactor — не снимается."""
    out = []
    if kind == "bug":
        if ticket.get("repro"):
            if not redproof:
                out.append("bug: нет красного доказательства — `ticket %s redproof --command \"<тест>\"` "
                           "(команда должна упасть)" % ticket["id"])
        else:
            repro = [t for t in tickets if t.get("repro")]
            if not any(t.get("status") == "done" for t in repro):
                out.append("bug: таск воспроизведения ещё не сдан (done) — сначала он")
    elif kind == "refactor":
        if not ticket.get("baseline"):
            out.append("refactor: нет baseline — `ticket %s baseline --command \"<тесты>\"` до правок" % ticket["id"])
        edited = sorted(set(changed_files) & set(tracked_tests))
        if edited and not ticket.get("testsEdit"):
            out.append("refactor: правка существующих тестов (%s) без строки `**Правка тестов:** причина` в файле таска"
                       % ", ".join(edited[:3]))
    return out
