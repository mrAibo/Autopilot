# Границы и правила проекта

Каждый исполнитель читает этот файл первым, затем `notes.md` (где что лежит в коде, номера строк на HEAD 0c07e30; сверяй по именам функций).

## Правила проекта (из «Договорились» прошлых сборок — не пересматривать)

- «ок» (2026-11-16): из журналов субагентов читать только суммы токенов, модель, `agentType`, id агента, `timestamp`; из журнала главной сессии — только суммы токенов. Текст сообщений, промпты и `description` не читаются и не сохраняются.
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/`; на Windows ключ под DPAPI.
- Opus — только по подтверждению пользователя (`ap.py opus approve --by-user "<цитата>"`); Fable не допускается ни под каким написанием. Правила Opus не меняются.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя; `dropped` ставит только пользователь.
- Лого остаётся в шапке и рейке дашборда; «Классика» держит старые цвета.
- Жёсткий минимум Claude Code 2.1.295; ниже 2.1.311 — предупреждение, не отказ.
- Принятые пробелы `bash_gate` — не чинить.
- Маршрут таска задаёт планировщик (`**Класс:**`, `**Риск:**`, `**Причина класса:**`); регулярных выражений по тексту таска нет; Haiku только за «механическим» классом. Поведение роутера не меняется.
- Адрес дашборда с токеном печатает только `ap.py url`; в чат и файлы не вставлять.
- `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md` и `BRIEF-2026-11-orchestrator-spend.md` в корне — не трогать и не коммитить.
- R06 прошлой сборки: текст навыка ради цифры не резать; порог обычного пути в `tests/test_text_split.py` (193 114 б, запас ≈ 9 КБ) — не поднимать без причины, новый текст в `phases/` минимален.
- Профили `autopilot-executor|reviewer|acceptance|explorer` постоянные: ни `finish`, ни `agents prune` их не удаляют.
- Шлюзы G1–G4, слепота приёмки, подписи, guard, запрет Fable не ослабляются.

## Как здесь работают

- Python, только стандартная библиотека. Исходники — `skills/autopilot/tools/*.py`, тексты навыка — `skills/autopilot/SKILL.md`, `phases/`, `prompts/`. Копии `.autopilot/*.py` и `.autopilot/dashboard.html` не правятся.
- `state.js` — только через `state_io.py`; файлы тасков — через `ticket_files(state, pattern)`.
- Новый модуль инструментов, который импортирует `ap.py`, добавляется в списки копий харнессов (`tests/test_ap.py` `setUp`, `test_ap_escalation.py`, `test_gui_bridge_e2e.py`, `test_subagent_spend.py`, `test_spend_accounting.py`). В этой сборке новых модулей `tools/` навыка не заводим; `tools/run-tests.py` (корень репозитория) — не модуль навыка.
- Новая команда `ap.py` вписывается и в docstring в начале файла, и в таблицу команд `phases/0-instruments.md` §4 (экономно: текст обычного пути).
- Коммит: `git commit --only -- <файлы зоны>`, без `git stash`, без `git add -A`, не пушить. Таски на `ap.py` в этой сборке идут по очереди; параллельно только таски с непересекающимися файлами.
- Тексты для пользователя — по-русски; имена в коде — по-английски. В документах `py -3`.
- Исполнитель гоняет только свои файлы тестов (`python -m unittest discover -s tests -p test_x.py`) и `python -m compileall -q skills/autopilot/tools tests tools`; полный прогон (≈ 9 мин) делает оркестратор в `ticket NN land`.
- Новый тест с общим числом тестов не требует правки счётчика руками: его пересчитывает `chore test-count` в конце.

Полная проверка: `python -m unittest discover -s tests`

(около 9 минут; исполнитель полный прогон не гоняет.)

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| test-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Границы, решённые в спецификации

| Единица | Владеет | Открывает | Прячет |
|---|---|---|---|
| `run_log.KINDS["ticket"]` + `ap.mirror_run_log` | схемой строки журнала | к полям `id, act, cause` добавляются `class`, `effort`, `model` (строки; `—`/пусто допустимы), пишутся при `act=start` из `tk["routing"]`/`tk["plannedRouting"]` (`class` — из `reason`, `class=…`) | старые строки без полей читаются как «не указан» |
| `ap.compute_class_report(records) -> list[dict]` / `render_class_report(rows) -> str` | сводом «класс × модель × усилие» по всем прогонам журнала | строки: `class, model_family, effort, tasks, first_try, retries, escalations, tokens_per_task`; блок печатается в `report-run` после «## Модели», в `--share` без названий тасков | `compute_model_report`/`render_model_report` не меняются |
| `ap.history_advice(records) -> str \| None`, `ap.forecast(records, tickets) -> str \| None` | советом и прогнозом из той же истории | строка или `None`; в `plan-models` ключи `advice` и `forecast` только если не `None` | не влияют на маршрут |
| `model_router.ALLOWED_SUBAGENT_RE` | допустимыми подагентскими моделями | принимает `-latest` у Haiku и Sonnet; Opus и Fable — как прежде | — |
| `ap.ping_digest(token, port) -> str`, `ap.server_is_ours(port) -> bool`; путь сервера `/.ap-ping` | подтверждением своего сервера по HTTP | `hmac-sha256(token, "autopilot-ping\|<порт>")` hex; путь вне `OPEN_PAGES`, без `?t=`, под теми же проверками Host/Origin/`Sec-Fetch-Site`; `serve()` и `ap.py url` зовут `server_is_ours` до `cmdline`; не совпало — прежний путь (`is_guarded_server(cmdline(pid))`) и перезапуск | токен по сети не уходит |
| `ap.history_cache` (файл `.autopilot/history-cache.json`, в `.gitignore` от `init`) | кэшем сводки по архивам | ключ `(папка, st_mtime_ns, st_size)`; битый/нет файла — молча пересчёт; `tokens` в кэш не входит | запись через временный файл и `os.replace` |
| `ap.archive_attestations(state) -> str \| None` (в `cmd_finish`) | переносом `.autopilot/attestations.jsonl` в `<папка прогона>/attestations.jsonl` | дописывает при повторе; строки не меняются (подписи верны); сбой — строка `!` в notes, `finish` не падает | незавершённый прогон не трогает |
| `ap.remove_run_profiles(state) -> list[str]` (в `cmd_finish`), `ap.py agents prune [--apply]` | удалением профилей `autopilot-*` с именем прогона | удаляет по `agentFile`/имени внутри `.claude/agents` и `.codex/agents`; не удаляет четыре постоянных, чужие файлы, профили других незавершённых прогонов (`*--wip`, `finishedAt is None`) и символические ссылки; `prune` без `--apply` печатает список | сбой удаления — `!`, не срыв |
| `tools/run-tests.py [-j N] [--list]` (корень репозитория) | параллельным запуском тестов | итог `Ran N tests in …s` + `OK (skipped=S)` / `FAILED (failures=F, errors=E, skipped=S)`, код 1 при падении; помеченные последовательные (атрибут класса `serial = True` или список в запускателе) идут после параллельных | `unittest discover` и CI не меняются |
| дашборд `humanRoute(route, L)` | словами о маршруте | разбирает `class=`, `risk=`, `why=` из `reason`; `score` — только в подробностях | старые фразы тестов сохраняются там, где не меняется смысл |
| дашборд: ошибка токена | подсказкой при неверном `?t=` | один раз `tokenHint()` и остановка опроса; кнопка «обновить» возобновляет | «сервер умер» (`lost`) остаётся отдельным сообщением |
