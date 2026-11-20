# Заметки по коду (разведка)

## scheduler.py (`skills/autopilot/tools/scheduler.py`)
- `schedule(tickets, max_parallel=2, *, strict=False, isolated=False, budget_blocked=False, verified=None)` (стр. 61). Кандидаты — `status == "pending"`, цикл с 89.
- Правило зависимостей 91-95: `missing = [dep for dep in ticket.get("blockedBy") or [] if dep not in index or index[dep].get("status") != "done"]` → `blocked.append({"ticket": tid, "reason": "dependencies", "ids": missing})`. Пускает только `done`.
- `ap.py` `cmd_ticket` стр. 2554: `ready = ("done", "review") if act == "start" else ("done",)`; тексты отказа стр. 2558.
- Вызывают: `ap.py` команда `schedule` (4644-4665), `controller.py` (19, 138). Тесты: `tests/test_scheduler.py` (`SchedulerTests`, `UnsafeZoneRegression`), `tests/test_ap.py` (копирует scheduler.py в харнесс).
- Расхождение: `ticket start` пускает зависимость в `review`, `schedule` — нет.

## commit_paths (`skills/autopilot/tools/ap.py` 2898-2921)
- `git add -- paths`; `git diff --cached --name-status -M -z`; цикл по тройкам `R`: старый путь добавляется, если `parts[n] == "R" and parts[n+2] in paths and parts[n+1] not in paths` (точное совпадение — каталог `x/` не совпадёт).
- `covers(zone, path)` (стр. 2833-2834): `path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/")`.
- Вызывающие передают файлы: `ticket NN land` (3064, 3099), `chore` (2951, 2961).
- Тесты: `tests/test_review_race_bugs.py`, класс `CommitPathsRename` (77-133), хелперы `setUp` (82-93), `git`, `put`, `changed_by_head`.

## gate_sign (`skills/autopilot/tools/gate_sign.py`)
- `_retry_busy(action, attempts=100)` (111-119), `_claim_path` (146), `_claim_empty(path) -> bool` (150-175): `os.link` под `_retry_busy` (PermissionError наружу сырой); `finally` снимает заявку через `_retry_busy`, при стойком `PermissionError` бросает `OSError("не удалось удалить заявку … ")` — оно перекрывает `return`.
- `ensure_key()` (190-231): `stat`; при `size == 0` → `_claim_empty(path)` (206) без try; `_stored_key()` читается только с 214. Единственный вызов из `ap.py` 1581-1585: `except OSError` → `die(...)`.
- Итог: ключ может быть уже целым (устаревший `stat` нулевой размер), а `ensure_key` всё равно падает `OSError` из-за заявки.
- Тесты: `tests/test_gate_sign.py`, `KeyRaceTests` (152-315): `busy_claim(failures)` (238-248), тесты стойко занятой заявки (257-273), брошенной заявки (275-285).
