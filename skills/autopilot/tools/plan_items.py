"""Пункты плана: критерии готовности из файлов тасков и вердикты ревью по ним (план -> факт).

Только стандартная библиотека. Состояние не трогает: `ap.py plan-fact` читает файлы, зовёт
`build_plan_fact` и сам пишет результат в `state["planFact"]`.
"""
import os
import re

DONE, PARTLY, NOT_DONE = "сделано", "частично", "не сделано"
STATUSES = (DONE, PARTLY, NOT_DONE)
HEADING = re.compile(r"^#{2,6}\s+(.*)$")
TITLE = re.compile(r"критери|приёмк|приемк|acceptance", re.I)
BULLET = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s*)?(.*\S)\s*$")


def parse_items(ticket_text):
    """Строки `- …` / `- [ ] …` из первого раздела (заголовки `##` и ниже) про критерии/приёмку/acceptance; нет раздела — []."""
    items, inside = [], False
    for line in ticket_text.splitlines():
        head = HEADING.match(line)
        if head:
            if inside:
                break
            inside = bool(TITLE.search(head.group(1)))
            continue
        if inside:
            m = BULLET.match(line)
            if m:
                items.append(m.group(1))
    return items


def parse_verdict(line):
    """`T02.1 | сделано | файл:строка` -> {id, status, evidence}; не по формату — None."""
    parts = [p.strip() for p in str(line).split("|", 2)]
    if len(parts) < 2 or not re.fullmatch(r"(?:T\w+|F\d+)\.\d+", parts[0]):
        return None
    return {"id": parts[0], "status": parts[1].lower(), "evidence": parts[2] if len(parts) > 2 else ""}


def item_prefix(ticket):
    """Id таска -> префикс пункта: `02` -> `T02`, fix-таск `F1` остаётся `F1`."""
    return ticket if re.fullmatch(r"F\d+", ticket) else "T" + ticket


EVIDENCE = re.compile(r"(?P<path>[^\s:|]+?)(?::\d+|::\w+)")


def _proved(evidence, root):
    """Доказательство `путь:строка` или `путь::имя`, где `путь` есть под root."""
    for m in EVIDENCE.finditer(evidence):
        full = os.path.realpath(os.path.join(root, m.group("path")))
        if os.path.exists(full) and os.path.commonpath([os.path.realpath(root), full]) == os.path.realpath(root):
            return True
    return False


def build_plan_fact(items_by_ticket, verdicts, root=None):
    """Факт плана: у каждого пункта статус и доказательство; нет вердикта, неизвестный статус
    или пустое доказательство — «не сделано». С `root` «сделано» требует `путь:строка`/`путь::имя`
    с существующим путём. `done` — число «сделано»."""
    given = {v.get("id"): v for v in verdicts if isinstance(v, dict)}
    items = []
    for ticket, texts in items_by_ticket.items():
        for n, text in enumerate(texts, 1):
            item_id = "%s.%d" % (item_prefix(ticket), n)
            v = given.get(item_id) or {}
            evidence = str(v.get("evidence") or "").strip()
            status = v.get("status") if v.get("status") in STATUSES and evidence else NOT_DONE
            if status == DONE and root is not None and not _proved(evidence, root):
                status = NOT_DONE
            items.append({"id": item_id, "ticket": ticket, "text": text, "status": status,
                          "evidence": evidence})
    return {"items": items, "done": sum(i["status"] == DONE for i in items), "total": len(items)}


def unknown_ids(items_by_ticket, verdicts):
    """Id вердиктов, которых нет среди пунктов."""
    known = {"%s.%d" % (item_prefix(t), n) for t, texts in items_by_ticket.items() for n in range(1, len(texts) + 1)}
    return [v["id"] for v in verdicts if v["id"] not in known]


def merge_verdicts(previous_items, new_verdicts):
    """Прежние вердикты (из `planFact.items`) с наложением новых по id."""
    merged = {i["id"]: {"id": i["id"], "status": i.get("status"), "evidence": i.get("evidence", "")}
              for i in previous_items or [] if isinstance(i, dict) and "id" in i}
    merged.update({v["id"]: v for v in new_verdicts})
    return list(merged.values())
