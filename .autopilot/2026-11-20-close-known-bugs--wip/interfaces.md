# Интерфейсы и правила проекта

## Правила проекта (из «Договорились»)
- «R28 и R33–R35 не трогай» (2026-11-20): не менять; ADR `0015` закреплён за R33, новые ADR — с `0028`.
- Opus выключен, Fable не допускается; `dropped` ставит только пользователь; `main` в `origin` — только по слову.
- Исполнитель не коммитит (коммитит оркестратор через `ticket NN land`); `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md`, `BRIEF-2026-11-orchestrator-spend.md` не коммитить.
- Тесты, копирующие `ap.py` в харнесс, копируют и каждый импортируемый модуль.
- Каждый баг — с регрессионным тестом в `tests/` и строкой в `CHANGELOG.md` («Unreleased»).

Полная проверка: `python tools/run-tests.py`

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| tests-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Границы
- `plan_items._proved(evidence, root)` — теперь сверяет строку (`N` ≤ числа строк файла) и имя (`::имя` есть в тексте файла); сигнатура `build_plan_fact` прежняя.
- `ap.cmd_plan_fact`: удаляет из `concerns` только точные строки, записанные прежним `planFact`.
- `land_check`: `_own(subject, ticket, trailers="")`; `_foreign_files` читает `%H %P %s` и трейлеры `Autopilot-Ticket`; merge — через `diff --name-only -z --relative <sha>^1 <sha>`. `ap.cmd_land` добавляет трейлер `Autopilot-Ticket: <id>`.
- `ap.blocker_confirm(state, opt)`: опция `by-user` (поправка `confirmed` → `not-confirmed`); `secondPass.replaces` хранит прежний вердикт.
- `ap.cmd_proof`: отказ redproof и на `ImportError|ModuleNotFoundError|cannot import name` в выводе.
