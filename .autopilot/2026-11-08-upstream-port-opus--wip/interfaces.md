# Границы, решённые в спецификации

## Правила проекта (из «Договорились», кроме изменённого)
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`); признак «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`.
- Fable закрыт ни под каким написанием. Opus — см. ниже, только с подтверждением (изменено пользователем 2026-11-08).
- Жёсткий минимум Claude Code 2.1.295; ниже 2.1.311 — предупреждение.
- `state.js` читается и пишется только через `state_io.py`; харнессы, копирующие `ap.py`, копируют `state_io.py`, `process_containment.py`, `run_log.py`.

## Единицы

### ap.py (владеет состоянием прогона)
Открывает: команды `ticket NN reset --by-user "<цитата>"`, `finish --result … [--by-user "<цитата>"]`, `git-check`, `opus propose|approve|status`; функции `refresh_g1(state, create=False)`, `landing_problems(state) -> (refuse: list[str], caveat: list[str])`, константу `BLIND_ROUNDS = 2`.
Поля state.js (новые, необязательные — старые прогоны читаются):
- `blindRounds: int` (0 по умолчанию; `reopen` → 0)
- `tickets[].reopenedByUser: list[str]`
- `landedWith: {"problems": list[str], "byUser": str|null}` — есть только у сданного с оговорками
- `opusApproval: {"tickets": [str], "roles": ["repair"|"reviewer"], "quotes": [{"at": iso, "quote": str}], "sig": str|null}`
- `opusAgents: {"reviewer": str, "repair": str}` — только если подтверждение непустое при `plan-models --apply`
Скрывает: порядок проверок `finish`, пересчёт G1.

### model_router.py (владеет политикой моделей)
Открывает: `is_opus_model(name) -> bool`, `is_allowed_subagent_model(name, premium_ok=False) -> bool`, `choose_route(..., premium=False)`, `premium_candidate(route_or_scores) -> bool`, ключ политики `providers.anthropic.premium`.
Инвариант: при `premium_ok=False`/`premium=False` результат тот же, что до этой сборки. Fable не допускается ни при каком флаге.

### claude_agent_guard.py (владеет допуском запуска субагента)
Использует `is_allowed_subagent_model(model, premium_ok=…)` и общий `gate_sign.verify`; читает из state `opusApproval`, `opusAgents`, `tickets[].routing`. Своего списка премиум-моделей не заводит.

### agent_profiles.py
`prepare(…, premium=False)` передаёт флаг в `choose_route`.

### dashboard-template.html (владеет показом)
Читает `S.landedWith` (шапка «Сдано с оговорками» + список) и `S.opusApproval` (строка в виде `models`). Новые строки RU/EN в словаре L. Ничего не пишет.

### Фазы и документы
Описывают команды выше; источник правды — `ap.py`.

## Швы для тестов
- `tests/test_ap.py` (`Run`): `ticket reset` failed/by-user; третий repair/retry; blind трижды; G1 после правки манифеста; `done` без commit; `finish` отказ/по `--by-user`/оговорка G4; `git-check` при занятом `.git/index.lock`; `opus propose|approve|status`; `plan-models --apply` с подтверждением и без.
- `tests/test_model_router.py`: `premium_ok`, `choose_route(premium=True)`, Fable закрыт при флаге.
- `tests/test_claude_agent_guard.py`: opus-профиль допущен только при верной подписи и при совпадении таск/роль; поддельная подпись → отказ.
- `tests/test_dashboard_views.py` или соседний: `landedWith` и `opusApproval` отрисованы.
