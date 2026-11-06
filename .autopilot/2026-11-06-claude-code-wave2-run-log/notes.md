# Заметки по коду (для R22, R22a–R22c)

Код навыка — `skills/autopilot/tools/`; `.autopilot/*.py` — копии (в живом проекте копируются по `phases/0-instruments.md`, править их руками нельзя).

**`ap.py` (2590 строк)**
- `log(state, event, **kw)` (стр. 171) — единая воронка событий дашборда: каждое `stage`, `gate`, `ticket`, `tests`, `worktree`, `answered` проходит через неё. Сюда же встаёт запись в журнал.
- `set_gate` (180) пишет `log(..., "gate", g, ok, **kw)`; при `check-plan` со сменой контракта гейты G1/G2/G4 сбрасываются с `reason="plan-changed"` (стр. ~2520).
- `cmd_stage` (1034) — начало и конец фазы (`stage`, `act`); `cmd_ticket` (1569): `start`, `done`, `retry`, `fail`, `repair`, `reset`, `review`; событие `log(state, "ticket", ids, act, tests, ...)` (~1834). Поле `tests` — пара `(passed, failed)` из `tests_pair`.
- `cmd_ticket ... accept-edit` → `cmd_accept_edit` (1549); `publish_tickets` (440): сброс статуса тасков — ветка `prev = {}` (изменённый таск не `done`) и ветка `done` с `acceptedFingerprint`; проверка worktree — строка `elif prev.get("worktree") and ... not in ("released",)` (~454) срабатывает только для не сданных тасков.
- `cmd_worktree` (1838): подкоманды `prepare, status, verify, finalize, land, release, recover`; `verify` запускает тесты хоста (источник длительности).
- `cmd_usage` (2051) — ручной `usage`, токены; `MOVES_ON` (86) — команды, двигающие дашборд.
- `machine_path_hits(text)` (421) — шаблоны путей машины, `check_machine_paths` (427).
- `main()` (2436) — диспетчер команд; команда `claude-version` — образец небольшой самостоятельной команды (2402–2436).
- `.gitignore` пополняет `ensure_gitignore()` (880).

**`claude_attest.py` (146 строк)** — хук `PreToolUse`/`PostToolUse`/`SubagentStop`, пишет `attestations.jsonl`; на `SubagentStop` кладёт `transcript_path` (`agent_transcript_path` из payload) — транскрипт субагента, JSONL; в нём — сообщения ассистента с `usage`.

**`claude_agent_guard.py` (392)** — `split_unquoted(command)` (107), `bash_decision(command) -> (bool, reason)` (134) с `GIT_OPTS_WITH_VALUE` (104): отклоняет слово `git` + `stash` / `reset` / `checkout --`; `install_hook(root)` (300). Слово `git` ищется ровно как `git`.

**Тесты** — `tests/`, `unittest`; `tests/test_ap.py` — харнесс с копией `ap.py`; харнессы (`test_ap.py`, `test_cargo_evidence.py`, `test_offline_supervisor.py`, `test_process_containment.py`, `test_test_evidence.py`) копируют `state_io.py` и `process_containment.py` рядом с `ap.py`; новый модуль, который `ap.py` импортирует, надо добавить в эти копии. Защита хука: `tests/test_wave1.py` (`BashGuard`), `tests/test_claude_agent_guard.py`. Тест R22p: `test_changed_ticket_resets_previous_acceptance` в `tests/test_ap.py` (~2414) проверяет, что сданный таск НЕ сбрасывается, а останавливает публикацию. Проверка путей машины: `tests/test_no_machine_data.py`.

**Проверка:** `python3 -m compileall -q skills/autopilot/tools tests`, `python3 -m unittest discover -s tests` (~5 мин; один файл — `-p test_x.py`).
