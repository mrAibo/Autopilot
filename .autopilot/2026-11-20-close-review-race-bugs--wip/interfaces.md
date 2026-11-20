# Интерфейсы и правила проекта

## Правила проекта (из «Договорились»)
- «R28 и R33–R35 не трогай»: не менять; ADR `0015` закреплён за R33, новые ADR — с `0029`.
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
- `ap.cmd_ticket`: условие зависимостей — по действию: `start` принимает статусы `done` и `review`; `done` — только `done`. `cmd_land` не меняется.
- `ap.commit_paths(paths, message, trailers)`: сигнатура прежняя; внутри добавляет исходные пути переименований из индекса.
- `gate_sign`/`tests/test_gate_sign.py`: публичные функции прежние.
