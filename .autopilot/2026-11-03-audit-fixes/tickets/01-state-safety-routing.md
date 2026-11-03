# 01 — Состояние, безопасность путей и выбор моделей

**Требования:** R16, R01, R07, R08, R09, R02, R03, R04, R06, R18, R10
**Зависит от:** —
**Зона:** `skills/autopilot/tools/state_io.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/controller.py` · `skills/autopilot/tools/spend_guard.py` · `skills/autopilot/tools/codex_dispatch.py` · `skills/autopilot/tools/retry_policy.py` · `skills/autopilot/tools/worktrees.py` · `skills/autopilot/tools/worker_outcome.py` · `skills/autopilot/tools/process_containment.py` · `skills/autopilot/tools/test_evidence.py` · `skills/autopilot/tools/model_router.py` · `skills/autopilot/tools/claude_agent_guard.py` · `skills/autopilot/phases/0-instruments.md` · `tests/test_state_io.py` · `tests/test_ap.py` · `tests/test_controller.py` · `tests/test_spend_guard.py` · `tests/test_codex_dispatch.py` · `tests/test_retry_policy.py` · `tests/test_worktrees.py` · `tests/test_worker_outcome.py` · `tests/test_process_containment.py` · `tests/test_test_evidence.py` · `tests/test_cargo_evidence.py` · `tests/test_model_router.py` · `tests/test_claude_agent_guard.py`
**Волна:** 1
**Ревью:** да — фундамент
**Модель:** сильная

## Что должно заработать

`state.js` читается и пишется одним модулем, переживает BOM и занятый файл на Windows; в main не уходят коммиты вне зоны тикета и переименования вне зоны; рискованные таски (токены, вебхуки, секреты, deploy) не получают самую дешёвую модель; Opus/Fable не проходят ни под каким написанием имени; `init --force` не теряет журнал; security-маркер в хвосте длинного лога не теряется; таймаут проверки тестов убивает всю группу процессов.

## Из брифа, дословно

> «A01: `save()` делает `os.replace` без повтора» — на Windows дашборд читает `state.js` раз в 10 с, и замена файла падает с `PermissionError`; в этом же репозитории уже есть повтор для такого случая (`offline_supervisor.py:77-86`).
> «A02: `land()` не проверяет зоны и пути; тесты берутся из текста `--tests N/0`»
> «A03: `git diff --cached --name-only` без `--no-renames`»
> «A04: риск тикета считается только по словарю слов»
> «A06: запрет премиум-моделей по префиксу строки»
> «A07: четыре разборщика `state.js` с разной терпимостью»
> «A08: `init --force` теряет журнал»
> «A09: `classify` смотрит только первые 12 000 символов»
> «A10: trusted-раннер не использует `OwnedJob`»
> «I01: общий модуль чтения/записи `state.js` (BOM, префикс, повтор replace) — закрывает A01 и A07 разом»
> «I03: точный allowlist моделей в роутере вместо префиксов + тесты на Bedrock-ID и `claude-3-opus`»

## Разделы спецификации

Истории 1–9, 14–16 (+5.1), «Решения по реализации». Сигнатуры — `interfaces.md` (state_io, process_containment.run_contained, model_router.is_allowed_subagent_model, worktrees.changed_paths / check_paths_in_zones). Заметки о точных местах — `notes.md`.

## Критерии приёмки

- [ ] `state_io` читает `state.js` с BOM, без префикса `window.STATE =`, с хвостовым `;`; пустой и битый JSON дают `StateError`
- [ ] `ap.save()` пишет через `state_io`; при имитации WinError 5 два раза подряд замена проходит; при постоянном отказе — понятная ошибка и нет `state.js.tmp`
- [ ] `ap.py`, `controller.py`, `claude_agent_guard.py`, `spend_guard.py`, `codex_dispatch.py` читают `state.js` через `state_io`; guard по-прежнему отказывает на битом файле, controller — `ControllerError`
- [ ] `land()` отклоняет коммит с путями вне зон, из `.autopilot/`, `.claude/`, `.git`; обычный коммит проходит
- [ ] `land --tests N/0` без `verify` в изолированном режиме записывает источник `claimed` и строку в `debt.assumptions`; с `verify` — `host`
- [ ] `git mv вне_зоны/x зона/x` в `finalize` и `worker_outcome.inspect` даёт оба пути и отклоняется; обе функции берут список из `worktrees.changed_paths` (`--no-renames`)
- [ ] «Проверка токена webhook-подписи» не получает cheap; русские и английские слова риска покрыты тестами
- [ ] `is_allowed_subagent_model` отклоняет `us.anthropic.claude-opus-*`, `claude-3-opus-*`, `bedrock/anthropic.claude-opus-*`, fable; пропускает haiku/sonnet; guard использует её, его собственный список удалён
- [ ] одноимённые методы `RouterTests` переименованы, выполняются обе копии
- [ ] `init --force`: папка прогона есть / нет / архив уже лежит — старый `state.js` никогда не теряется, note говорит куда; без `--force` отказ на живом прогоне остаётся
- [ ] лог 20 КБ с `AssertionError` в начале и «secret leaked» после 12 000 символов → security
- [ ] `run_contained` по таймауту убивает внука процесса (POSIX-тест; на Windows `skipUnless`); `test_evidence` (unittest и cargo) работает через неё
- [ ] новые модули `state_io.py` в списке копирования `phases/0-instruments.md`; тест проверяет, что каждый импортируемый sibling-модуль инструментов там есть
- [ ] `python3 -m unittest discover -s tests` целиком зелёный
