# Границы и правила

## Проект
- Только стандартная библиотека Python. Проверка: `python3 -m unittest discover -s tests` (около 6 минут); один файл: `python -m unittest discover -s tests -p test_x.py`.
- Журнал только пишет и читает, никогда не блокирует; метаданные без путей машины и текстов. Тесты не содержат литералов путей машины (`test_no_machine_data`): собирай путь при выполнении.
- Харнессы, копирующие `ap.py` или `claude_attest.py`, копируют и `run_log.py`, `state_io.py`, `process_containment.py`.
- Коммит исполнителя: `git commit --only <файлы зоны>`, без `git stash`/`reset`.

## Договорились (из carried.md, не пересматривать)
- Ключ подписи гейтов вне проекта; Opus и Fable не допускаются в субагенты; жёсткий минимум Claude Code 2.1.295.
- Поведение шлюзов G1–G4, `claude_agent_guard`, `spend_guard`, `test_evidence` не ослабляется.

## Границы, решённые в спецификации
- `run_log.read_all_stats(autopilot_dir) -> tuple[list[dict], int]` — строки журнала и число нечитаемых JSON-строк; `read_all` остаётся.
- `run_log.summarize(records, run=None, skipped=0) -> dict` — добавляет ключ `skipped` (испорченные + переданные), не падает на строках неверной структуры.
- `run_log.render_report(summary, share=False) -> str` — выводит «пропущено испорченных строк: N» при N > 0; колонка «роль».
- `run_log.role_of(agent_type) -> str` — `executor|reviewer|explorer|acceptance|agent`.
- `KINDS["executor"]` получает поле `role`.
- `ap.cmd_report_run(argv)` — выбор прогона: последняя запись с непустым `run`.
- `ap.py` при сбое импорта `run_log` печатает одну строку в stderr; `run_log = None` как раньше.
- Тест списка копирования: `tests/test_state_io.py::InstrumentsCopyListTests` — явный список `RUN_FROM_SKILL`.

## Построено таском 01

- `run_log.role_of(agent_type) -> str`; `run_log.read_all_stats(autopilot_dir) -> (list[dict], int)`; `run_log.summarize(records, run=None, skipped=0)` (ключ `skipped`, `tokens[*]["role"]`); `KINDS["executor"]` + поле `role`.
- `render_report(summary, share=False)`: строка «пропущено испорченных строк: N», колонка «роль».
- `ap.RUN_LOG_WARNING`; `tests/test_state_io.py::InstrumentsCopyListTests.RUN_FROM_SKILL`.
