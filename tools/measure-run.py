#!/usr/bin/env python3
"""Замер прогона Autopilot по логам сессии Claude Code.

Отвечает на три вопроса, ради которых он написан:
  · во что обошёлся прогон и кто именно потратил;
  · насколько выросли контексты — единственная величина, которой можно управлять;
  · соблюдаются ли правила, которые нельзя проверить чтением скилла.

Использование:
    python3 tools/measure-run.py <путь к каталогу проекта>
    python3 tools/measure-run.py ~/Documents/VScode/EDU/share

Каталог логов вычисляется из пути проекта так же, как это делает Claude Code:
слэши заменяются дефисами внутри ~/.claude/projects/ (корень — $CLAUDE_CONFIG_DIR, если задан).

Вторым аргументом — id сессии или `all`: все сессии каталога, где есть субагенты; тогда печатаются
только две сводные таблицы — стартовый контекст по типам агентов и ходы оркестратора между субагентами.

Читаются только числа, время, id, имена инструментов, `subagent_type` и `agentType`; текст сообщений
и промптов не читается и не сохраняется (метка контекста — поле `description` из meta.json, как раньше).

«Шаг» — один вызов модели (уникальный message.id), а не строка лога.
До 2026-10-12 скрипт считал строки и завышал расход примерно вдвое.

Нормировка стоимости — относительно входного токена:
    output ×5 · cache_write ×1.25 · cache_read ×0.1
Это пропорции, а не деньги: они нужны, чтобы сравнивать прогоны между собой.
"""

import json
import os
import re
import sys
import glob
import statistics
from datetime import datetime
from collections import Counter

for _s in (sys.stdout, sys.stderr):                     # cp1251-консоль Windows
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

W_OUT, W_WRITE, W_READ = 5.0, 1.25, 0.1
IDLE_GAP_SEC = 300          # пауза длиннее — это простой, а не работа
CEILING_HINT = 120_000      # ориентир для колонки «перебор»: выше — контекст раздут
EXEC_LOW = 150_000          # таск на ~3K строк кончается около 300–400K; ниже половины — стоило слить с соседом
EXEC_HIGH = 450_000         # выше — таск вышел далеко за ~3K строк: его стоило поделить


# Роль субагента — по описанию, которое ему дал оркестратор. Порядок важен:
# «Ремонт по находкам ревью» — ремонт, а не ревью.
ROLES = [
    ("ревью", r"re-review|повторн\w* ревью"),
    ("ремонт", r"ремонт|дозапрос|правки|доработка|repair|\bfix"),
    ("ревью", r"ревью|review|рецензент|ремесл|craft"),
    ("приёмка", r"слеп|blind|покрыт|coverage|\bg2\b"),
    ("память", r"памят|memory|\badr\b|claude\.md|agents\.md"),
    ("разведка", r"развед|explor|notes"),
    ("исполнитель", r"таск|ticket|исполн|executor|^t?\d{2}\b"),
]


def role_of(label):
    if label == "Оркестратор":
        return "оркестратор"
    for name, rx in ROLES:
        if re.search(rx, label.lower()):
            return name
    return "прочее"


def logs_dir_for(project_path):
    p = os.path.abspath(os.path.expanduser(project_path))
    root = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(root, "projects", re.sub(r"[^A-Za-z0-9]", "-", p))


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def analyse(path, label):
    rows = load(path)
    ctx, tools = [], Counter()
    out = win = rin = cold = 0
    test_edits = code_edits = test_runs = 0
    stamps = []
    # Один ответ модели пишется в лог несколькими строками — мысли, текст, вызов
    # инструмента — с одним message.id и одним usage. Считать его надо один раз,
    # по последней строке: в ней итоговое число выходных токенов.
    usage = {}

    for r in rows:
        m = r.get("message") or {}
        ts = parse_ts(r.get("timestamp"))
        if ts:
            stamps.append(ts)
        if (m.get("role") or r.get("type")) != "assistant":
            continue
        if m.get("usage"):
            usage[m.get("id") or id(m)] = m["usage"]
        for c in m.get("content") or []:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            name, inp = c.get("name"), c.get("input", {})
            tools[name] += 1
            if name == "Bash":
                cmd = str(inp.get("command", ""))
                if any(k in cmd for k in ("pytest", "npm test", "go test", "cargo test", "unittest")):
                    test_runs += 1
            elif name in ("Edit", "Write", "NotebookEdit"):
                fp = str(inp.get("file_path", ""))
                base = os.path.basename(fp)
                if "/tests/" in fp or "/test/" in fp or base.startswith("test_") or ".test." in base:
                    test_edits += 1
                else:
                    code_edits += 1

    for u in usage.values():
        cr = u.get("cache_read_input_tokens", 0) or 0
        cw = u.get("cache_creation_input_tokens", 0) or 0
        ip = u.get("input_tokens", 0) or 0
        out += u.get("output_tokens", 0) or 0
        win += cw
        rin += cr
        if cw > 20_000:
            cold += 1
        if cr + cw + ip:
            ctx.append(cr + cw + ip)

    stamps.sort()
    active = idle = 0
    for a, b in zip(stamps, stamps[1:]):
        gap = (b - a).total_seconds()
        if gap <= IDLE_GAP_SEC:
            active += gap
        else:
            idle += gap

    return {
        "label": label, "steps": len(ctx),
        "start": ctx[0] if ctx else 0,          # контекст первого шага: стартовый
        "end": stamps[-1] if stamps else None,
        "avg_ctx": sum(ctx) / len(ctx) if ctx else 0,
        "max_ctx": max(ctx) if ctx else 0,
        "over": sum(1 for c in ctx if c > CEILING_HINT),
        "out": out, "write": win, "read": rin, "cold": cold,
        "norm": out * W_OUT + win * W_WRITE + rin * W_READ,
        "active": active, "idle": idle,
        "test_edits": test_edits, "code_edits": code_edits, "test_runs": test_runs,
    }


AGENT_TOOLS = ("Agent", "Task")
PROFILE_ROLES = (("autopilot-executor", "исполнитель"), ("autopilot-reviewer", "ревью"),
                 ("autopilot-acceptance", "приёмка"), ("autopilot-explorer", "разведка"))


def agent_role(label, agent_type):
    """Роль субагента: по метке, как всегда; не вышло — по имени профиля `autopilot-<роль>…`."""
    role = role_of(label) if label else "прочее"
    if role == "прочее":
        for prefix, name in PROFILE_ROLES:
            if str(agent_type).startswith(prefix):
                return name
    return role


def landings(rows, agents):
    """Ходы главной сессии на «посадку»: от возврата субагента до следующего запуска или возврата.

    rows — строки журнала главной сессии; agents — {agentId: {"end", "label", "type"}}. Фоновый
    субагент вернулся, когда записана последняя строка его журнала; обычный — в строке результата.
    В окно входит шаг, который запускает следующего субагента. Окно без следующего запуска или
    возврата (хвост сессии, итоговый отчёт) не считается. Читаются время, id, usage, имена
    инструментов, subagent_type и agentId; текст не читается."""
    steps, launches, results = {}, {}, {}
    for r in rows:
        m = r.get("message") or {}
        ts = parse_ts(r.get("timestamp"))
        content = m.get("content") if isinstance(m.get("content"), list) else []
        if (m.get("role") or r.get("type")) == "assistant" and ts:
            s = steps.setdefault(m.get("id") or id(m), {"at": ts, "usage": None, "tools": {}})
            s["at"] = ts
            s["usage"] = m.get("usage") or s["usage"]
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    s["tools"][c.get("id")] = c.get("name")
                    if c.get("name") in AGENT_TOOLS:
                        st = (c.get("input") or {}).get("subagent_type")
                        launches[c.get("id")] = (ts, st if isinstance(st, str) else "general-purpose")
        elif ts:
            tur = r.get("toolUseResult") if isinstance(r.get("toolUseResult"), dict) else {}
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    aid = tur.get("agentId")
                    results[c.get("tool_use_id")] = (
                        ts, aid if isinstance(aid, str) else None,
                        tur.get("isAsync") is True or tur.get("status") == "async_launched")
    returns = []
    for tid, (_, stype) in launches.items():
        if tid not in results:
            continue
        at, aid, is_async = results[tid]
        info = agents.get(aid) or {}
        at = info.get("end") if is_async else at
        if at:
            returns.append((at, agent_role(info.get("label", ""), info.get("type") or stype), info.get("type") or stype))
    returns.sort(key=lambda x: x[0])
    launch_times = sorted(t for t, _ in launches.values())
    out = []
    for at, role, atype in returns:
        later = [t for t in launch_times if t > at] + [t for t, _, _ in returns if t > at]
        if not later:
            continue
        end = min(later)
        picked = [s for s in steps.values() if at < s["at"] <= end]
        norm = 0.0
        for s in picked:
            u = s["usage"] or {}
            norm += (u.get("output_tokens", 0) or 0) * W_OUT + (u.get("cache_creation_input_tokens", 0) or 0) * W_WRITE \
                + (u.get("cache_read_input_tokens", 0) or 0) * W_READ
        out.append({"role": role, "type": atype, "steps": len(picked), "norm": norm,
                    "tools": Counter(n for s in picked for n in s["tools"].values())})
    return out


def collect(main_log):
    """(результаты по контекстам, окна посадки) одной сессии; битый или нечитаемый meta.json пропускается."""
    sub_dir = main_log[:-6]
    metas = {}
    for mf in glob.glob(os.path.join(sub_dir, "subagents", "*.meta.json")):
        try:
            with open(mf, encoding="utf-8-sig") as f:     # BOM в meta.json встречается
                meta = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(meta, dict):
            metas[os.path.basename(mf)[:-10]] = meta
    results = [analyse(main_log, "Оркестратор")]
    results[0]["type"] = "—"
    agents = {}
    for jf in sorted(glob.glob(os.path.join(sub_dir, "subagents", "*.jsonl"))):
        key = os.path.basename(jf)[:-6]
        meta = metas.get(key, {})
        r = analyse(jf, meta.get("description", key) if isinstance(meta.get("description", key), str) else key)
        r["type"] = meta.get("agentType") if isinstance(meta.get("agentType"), str) and meta["agentType"] else "—"
        results.append(r)
        agents[key[len("agent-"):]] = {"end": r["end"], "label": r["label"], "type": r["type"]}
    return results, landings(load(main_log), agents)


def type_family(agent_type):
    """`autopilot-executor-03-имя` и `autopilot-executor-repair-прогон` — одно семейство `autopilot-executor-*`."""
    return re.sub(r"^(autopilot-(?:executor|reviewer|explorer|acceptance))-.+$", r"\1-*", agent_type)


def print_start_by_type(results):
    """Стартовый контекст (первый шаг) по типу агента: сколько контекстов, наименьший, медиана, наибольший."""
    by = {}
    for r in results:
        if r["label"] != "Оркестратор" and r["steps"]:
            by.setdefault(type_family(r["type"]), []).append(r["start"])
    print("Стартовый контекст по типам агентов (первый шаг; тип — agentType из meta.json)")
    print(f"  {'тип агента':<44}{'конт.':>6}{'мин':>8}{'медиана':>9}{'макс':>8}")
    for t, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f"  {t[:43]:<44}{len(v):>6}{min(v)/1000:>7.0f}K{statistics.median(v)/1000:>8.0f}K{max(v)/1000:>7.0f}K")
    print()


def print_landings(windows):
    """Ходы оркестратора между субагентами: по роли вернувшегося — окон, шагов, среднее, норм. единицы."""
    print("Ходы оркестратора между субагентами (шаги главной сессии от возврата субагента "
          "до следующего запуска или возврата)")
    print(f"  {'после кого':<14}{'окон':>6}{'шагов':>7}{'ср.шагов':>10}{'норм.ед':>10}{'ср.норм.ед':>12}  инструменты")
    by = {}
    for w in windows:
        by.setdefault(w["role"], []).append(w)
    for role, ws in sorted(by.items(), key=lambda kv: -len(kv[1])):
        n, st, nu = len(ws), sum(w["steps"] for w in ws), sum(w["norm"] for w in ws)
        tools = sum((w["tools"] for w in ws), Counter())
        top = ", ".join(f"{name}×{c}" for name, c in tools.most_common(4))
        print(f"  {role:<14}{n:>6}{st:>7}{st/n:>10.1f}{nu/1e6:>9.2f}M{nu/n/1e6:>11.3f}M  {top}")
    ex = by.get("исполнитель", [])
    print(f"  посадка таска (окна после исполнителя): {len(ex)}"
          + (f", в среднем {sum(w['steps'] for w in ex)/len(ex):.1f} шага, медиана {statistics.median(w['steps'] for w in ex):g}" if ex else "")
          + "; один таск может дать несколько окон (повтор, ремонт), хвост сессии не считан")
    print()


def main_all(d, sessions):
    """Сводные таблицы по всем сессиям каталога, где есть субагенты."""
    results, windows, used = [], [], 0
    for p in sessions:
        if glob.glob(os.path.join(p[:-6], "subagents", "*.jsonl")):
            r, w = collect(p)
            results += r
            windows += w
            used += 1
    print(f"\nСессий с субагентами: {used} из {len(sessions)}; контекстов: {len(results)}\n")
    print_start_by_type(results)
    print_landings(windows)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = logs_dir_for(sys.argv[1])
    if not os.path.isdir(d):
        sys.exit(f"нет логов: {d}")

    sessions = glob.glob(os.path.join(d, "*.jsonl"))
    if not sessions:
        sys.exit(f"в {d} нет .jsonl")

    def weight(p):
        """Прогон Autopilot узнаётся по субагентам, а не по свежести:
        последняя по времени сессия — обычно та, в которой смотрят результат."""
        n = len(glob.glob(os.path.join(p[:-6], "subagents", "*.jsonl")))
        return (n, os.path.getsize(p))

    if sys.argv[2:3] == ["all"]:
        return main_all(d, sessions)
    if len(sys.argv) > 2:                       # явный выбор: id сессии
        picked = [p for p in sessions if sys.argv[2] in os.path.basename(p)]
        if not picked:
            sys.exit(f"сессия {sys.argv[2]} не найдена в {d}")
        main_log = picked[0]
    else:
        main_log = max(sessions, key=weight)

    if len(sessions) > 1:
        print(f"\nСессий в каталоге: {len(sessions)}. Взята {os.path.basename(main_log)[:8]}"
              f" ({len(glob.glob(os.path.join(main_log[:-6], 'subagents', '*.jsonl')))} субагентов)."
              f"\nДругую — вторым аргументом: measure-run.py <проект> <id сессии>")
    results, windows = collect(main_log)
    results.sort(key=lambda r: -r["norm"])

    total = sum(r["norm"] for r in results) or 1
    print(f"\nПрогон: {sys.argv[1]}   контекстов: {len(results)}\n")
    print(f"{'контекст':<38}{'шагов':>7}{'старт':>8}{'ср.ctx':>9}{'макс':>9}{'>120K':>7}{'норм.ед':>11}{'доля':>7}  тип агента")
    print("-" * 110)
    for r in results:
        print(f"{r['label'][:37]:<38}{r['steps']:>7}{r['start']/1000:>7.0f}K{r['avg_ctx']/1000:>8.0f}K"
              f"{r['max_ctx']/1000:>8.0f}K{r['over']:>7}{r['norm']/1e6:>10.2f}M"
              f"{r['norm']/total*100:>6.1f}%  {r['type']}")
    print("-" * 110)

    o = sum(r["out"] for r in results)
    w = sum(r["write"] for r in results)
    rd = sum(r["read"] for r in results)
    steps = sum(r["steps"] for r in results)
    print(f"{'ИТОГО':<38}{steps:>7}{'':>8}{'':>9}{'':>9}{'':>7}{total/1e6:>10.2f}M\n")
    print_start_by_type(results)
    print_landings(windows)

    print("По ролям")
    by = {}
    for r in results:
        by.setdefault(role_of(r["label"]), [0, 0.0])
        by[role_of(r["label"])][0] += 1
        by[role_of(r["label"])][1] += r["norm"]
    for name, (n, val) in sorted(by.items(), key=lambda kv: -kv[1][1]):
        print(f"  {name:<14}{n:>3} конт.{val/1e6:>9.2f}M{val/total*100:>6.1f}%")
    print()

    print("Структура расхода")
    for name, val in (("чтение кэша", rd * W_READ), ("запись кэша", w * W_WRITE), ("генерация", o * W_OUT)):
        bar = "█" * round(val / total * 46)
        print(f"  {name:<14}{val/total*100:>5.1f}%  {bar}")
    print(f"\n  прочитано на каждый написанный токен: {(rd + w) / o:.0f}:1" if o else "")

    print("\nСоблюдение правил")
    hot = [r for r in results if r["avg_ctx"] > CEILING_HINT * 1.5]
    print(f"  контекстов выше полуторного потолка: {len(hot)}"
          + (f" — {', '.join(r['label'][:24] for r in hot[:4])}" if hot else " — нет"))
    te = sum(r["test_edits"] for r in results)
    ce = sum(r["code_edits"] for r in results)
    print(f"  правки тестов к правкам кода: {te}/{ce}"
          + (f" ({te/(te+ce)*100:.0f}%)" if te + ce else ""))
    print(f"  прогонов тестов: {sum(r['test_runs'] for r in results)}")
    cold_agents = [r for r in results if r["read"] and r["write"] / r["read"] > 0.10]
    print(f"  контекстов с протухшим кэшем (запись/чтение > 10%): {len(cold_agents)}"
          + (f" — {', '.join(r['label'][:24] for r in cold_agents[:4])}" if cold_agents else " — нет"))

    execs = [r for r in results if role_of(r["label"]) == "исполнитель" and r["steps"]]
    if execs:
        print("\nНагрузка исполнителей (цель — ~3K строк на таск, обычно 300–400K контекста)")
        low = [r for r in execs if r["max_ctx"] < EXEC_LOW]
        high = [r for r in execs if r["max_ctx"] > EXEC_HIGH]
        print(f"  недогружены, макс. < {EXEC_LOW//1000}K — кандидаты на слияние: {len(low)}"
              + (f" — {', '.join(r['label'][:24] for r in low)}" if low else " — нет"))
        print(f"  перегружены, макс. > {EXEC_HIGH//1000}K — стоило поделить: {len(high)}"
              + (f" — {', '.join(r['label'][:24] for r in high)}" if high else " — нет"))

    act = sum(r["active"] for r in results)
    idl = sum(r["idle"] for r in results)
    print(f"\nВремя по всем контекстам: активно {act/60:.0f} мин · простой {idl/60:.0f} мин"
          f" ({act/(act+idl)*100:.0f}% активного)" if act + idl else "")


if __name__ == "__main__":
    main()
