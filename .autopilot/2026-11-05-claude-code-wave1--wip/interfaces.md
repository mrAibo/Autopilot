# Границы и правила проекта

## Правила проекта
- Стек: Python 3.11+, только стандартная библиотека; запуск `python3` (в доках `py -3`).
- Проверка: `python3 -m compileall -q skills/autopilot/tools tests` и `python3 -m unittest discover -s tests` (~5 минут; один файл — `python3 -m unittest discover -s tests -p test_x.py`).
- Править `skills/autopilot/**`, `tests/**`, `docs/**`, `CHANGELOG.md`. Не править: `.autopilot/**` (копии и состояние), `skills/autopilot/phases/dashboard-template.html`, `.claude/**`, файлы вне зоны.
- `state.js` читать и писать только через `skills/autopilot/tools/state_io.py`.
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, и `process_containment.py`.
- Коммит: `git commit --only <файлы зоны>`, без `git stash`/`git reset`; перед коммитом `git diff --cached --stat`. Заголовок — что (`fix: …`), трейлер `--trailer "Requirements: R01"`.
- В файлах репозитория никаких путей машины (`C:\Users\<имя>\…`, `/home/<имя>/…`) — только `<repo>`, `<scratchpad>`.

## Договорились (из прошлой сборки, дословно из PROGRESS.md)
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/` — R05, R17
- Opus и Fable не допускаются в субагенты ни под каким написанием — R06, R18

## Границы, решённые в спецификации

**`state_io.py`** — владеет чтением/записью `state.js` и отпечатком таска.
Открывает: `ticket_fingerprint(raw: bytes) -> str`; `fingerprint_matches(stored: str | None, raw: bytes) -> bool`.
Скрывает: нормализацию (UTF-8, снять BOM, `\r\n`/`\r` → `\n`, снять пробелы и табы в конце строк), набор старых вариантов.

**`ap.py`** — владеет подкомандами и публикацией тасков.
Открывает: `machine_path_hits(text: str) -> list[tuple[int, str]]` (номер строки, совпадение); `parse_claude_version(text: str) -> tuple[int, int, int] | None`; `claude_version_report(version, min_version=(2,1,295), warn_below=(2,1,311)) -> tuple[str, list[str]]` (уровень `ok|warn|refuse|unknown`, строки сообщения); подкоманды `claude-version [--text S]`, `ticket NN accept-edit --note S`.
Скрывает: порядок проверок в `publish_tickets` (путь машины → отпечаток → перенос полей).

**`claude_agent_guard.py`** — владеет решением хука.
Открывает: `decision(payload, root)` для `Agent|Task`, записи и теперь `Bash`; `bash_decision(command: str) -> tuple[bool, str]` (чистая функция, шов для тестов); `install_hook(root)` с третьим хуком.
Скрывает: разбор команды git.

**Швы для тестов:** `state_io.fingerprint_matches`, `ap.machine_path_hits`, `ap.claude_version_report`, `claude_agent_guard.bash_decision`; сквозной — `ap.py tickets` / `ticket accept-edit` в харнессе из `tests/test_ap.py`.
