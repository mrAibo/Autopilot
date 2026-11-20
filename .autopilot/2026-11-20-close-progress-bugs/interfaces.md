# Интерфейсы и правила проекта

## Правила проекта (из «Договорились» прошлой сборки)

- «пуш мэйн»: `main` отправляется в `origin` — только по слову пользователя.
- R28 и R33–R35 не трогать («R28 и R33–R35 не трогай», 2026-11-20); ADR `0015` закреплён за R33, новые ADR этой сборки — с `0027`.
- Opus — только по подтверждению пользователя (выключен); Fable не допускается.
- Возврат упавшего таска и сдача с отказами — только цитатой; `dropped` ставит только пользователь.
- Тесты, копирующие `ap.py` в харнесс, копируют и каждый модуль, который он импортирует.
- Исполнители коммитят (если им велено) `git commit --only <файлы зоны>`, без `git stash`; обычно коммитит оркестратор через `ticket NN land`.
- `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md`, `BRIEF-2026-11-orchestrator-spend.md` в корне не коммитить.
- Каждый баг — с регрессионным тестом (в `tests/`), запись в `CHANGELOG.md` («Unreleased»).

Полная проверка: `python tools/run-tests.py`

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| tests-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Границы, решённые в спецификации

### `plan_items.py` (T01)
- `build_plan_fact(items_by_ticket, verdicts, root=None) -> dict` — прежняя форма результата; при `root` статус «сделано» требует доказательства `путь:строка` или `путь::имя` с существующим `путь` под `root`, иначе `не сделано`.
- `unknown_ids(items_by_ticket, verdicts) -> list[str]` — id вердиктов, которых нет среди пунктов.
- `merge_verdicts(previous_items, new_verdicts) -> list[dict]` — прежние вердикты (из `planFact.items`) с наложением новых по id.
`ap.py plan-fact record`: неизвестный id → отказ (`die`), в `state` ничего; `concerns` «план: …» перед записью заменяются актуальными (старые строки с префиксом `план: ` удаляются).

### `land_check.py` (T02)
- `preflight(root, start_head, base_commit, zone, ticket, active_zones, files=None) -> dict` — прежние ключи; `files` — вливаемые файлы (проектные пути): при заданных `neighbors` и `foreign_files` считаются только по ним; сравнение по целым сегментам пути; коммиты с темой, начинающейся с id таска (`T02:`, `T02 `, `F1:`), чужими не считаются; проект в подпапке — пути приводятся через `git rev-parse --show-prefix`, `unsupported` только когда git не отвечает.
`cmd_land` передаёт `files`; `worktrees.py land` — как раньше (без `files` — прежнее поведение).

### Блокеры и redproof (T03)
- Блокер получает `secondPass: {"verdict": "confirmed"|"not-confirmed", "quote": str, "at": ISO}`; `confirmQuote` остаётся. Второй `blocker confirm` по блокеру с `secondPass` — отказ. Событие журнала `blocker` с `act=confirmed|downgraded` получает `verdict`.
- `cmd_proof`: для `redproof` отказ при коде 126/127, при выводе с `SyntaxError`/`IndentationError`/`command not found`/`is not recognized`/`Ran 0 tests`/`no tests ran`/`collected 0 items` («тест не по-настоящему красный: …»).

### CI (T04)
- `.github/workflows/python-tests.yml`: шаг «Unit tests» — `python tools/run-tests.py`; `AGENTS.md` и `docs/` не называют `unittest discover` как то, что гоняет CI.
