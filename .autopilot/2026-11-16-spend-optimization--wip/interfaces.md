# Границы и правила проекта

## Правила проекта (из «Договорились» прошлой сборки — не пересматривать)
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`; на Windows ключ под DPAPI (блок `dpapi:`), на остальных ОС файл.
- Opus — только по подтверждению пользователя (`ap.py opus approve --by-user`); Fable не допускается ни под каким написанием.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя (`reset --by-user`, `finish --by-user`).
- Лого остаётся в шапке и рейке дашборда. «Классика» держит старые цвета, остальные темы — палитру макетов. Страница «Сейчас» по умолчанию; восемь старых тем под «Ещё».
- Принятые пробелы `bash_gate`: `>|`, `case…esac`, `find -exec sh -c`, `perl -pi`, heredoc, подстановки `$(...)` — не чинить.
- `state.js` читается и пишется только через `state_io.py`; файлы тасков ищутся через `ticket_files()`; тесты, копирующие `ap.py` в харнесс, копируют `state_io.py`, `process_containment.py` и `run_log.py`.
- Только стандартная библиотека Python. Правила проекта и команды — `AGENTS.md`.
## Границы, решённые в спецификации
Единицы и швы (имена на английском, как в коде):

| Единица | Владеет | Открывает | Прячет |
|---|---|---|---|
| `run_log.usage_by_model(path, since, until=None)` | построчным чтением журнала главной сессии | `-> dict[str, dict] | None`, ключ — модель; значения `turns, input, output, cache_read, cache_write` | формат строк Claude Code (`message.usage`, `isSidechain`, `timestamp`) |
| `ap.compute_spend(records, run)` | суммами на ключ | к `n, input, output, tokens` добавлены `cache_read, cache_write, hit` (`hit` — целые % или `None`); `tokens` по-прежнему вход+выход | дедуп строк `role=orchestrator` (последняя на модель) |
| `ap.py spend-orchestrator [--transcript PATH]` и шаг в `finish` | записью расхода оркестратора в `run-log.jsonl` | строки `k=executor, role=orchestrator`; одна печатная строка; не бросает исключений | поиск журнала сессии в `~/.claude/projects/<имя>/` |
| `run_log.render_report` | текстом `report-run` | новая таблица «Кэш по ролям» | — |
| шаблон `spendTable` | таблицами «Расход» | колонка «Кэш, %» | — |
| `prompts/executor.md` «Ритм проверок» | правилами исполнителя | правило тихого вывода | — |

Швы для тестов: `usage_by_model` и `compute_spend` — на фикстурных JSONL/списках строк во временной папке; `spend-orchestrator` — подпроцессом `ap.py` в харнессе (по образцу тестов `test_run_log*.py`) с `--transcript`; шаблон — jsdom-харнесс `test_dashboard_*.py`.

## Построено (из возврата таска 01, a0214b0)
- `run_log.usage_by_model(path, since, until=None) -> dict[str, {turns,input,output,cache_read,cache_write}] | None`
- `ap.compute_spend`: на каждом ключе ещё `cache_read`, `cache_write`, `hit` (целые % или `None`); строка оркестратора — последняя на модель
- `ap.py spend-orchestrator [--transcript PATH]`; `ap.spend_orchestrator(state, transcript=None) -> str` (не бросает); `ap.session_transcript() -> path | None`
- `run_log.render_report`: «## Кэш по ролям» и, без `--share`, «## Кэш по профилям»
- шаблон: `W.cCache` («Кэш, %» / «Cache, %»), четвёртая колонка `spendTable`
