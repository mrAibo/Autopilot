# Границы, решённые в спецификации

## Правила проекта (из «Договорились», кроме изменённого)
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`); признак «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`.
- Opus — только по подтверждению пользователя (`ap.py opus approve --by-user`), Fable закрыт ни под каким написанием.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя (`reset --by-user`, `finish --by-user`).
- Жёсткий минимум Claude Code 2.1.295; ниже 2.1.311 — предупреждение.
- `state.js` читается и пишется только через `state_io.py`; харнессы, копирующие `ap.py`, копируют `state_io.py`, `process_containment.py`, `run_log.py` (и `gate_sign.py`).

## Единицы

### Подписи (общий формат — читают и пишут ap.py и claude_agent_guard.py)
- `run_id(state) = "%s|%s" % (state["slug"], state["startedAt"])`
- `opusApproval.sig = gate_sign.sign({"tickets": [...], "roles": [...], "run": run_id})`
- `opusApproval.agentsSig = gate_sign.sign({"opusAgents": {"reviewer": str, "repair": str}, "run": run_id})`
Оба `null` без ключа. Порядок списков — как записан в `opusApproval`.

### ap.py (владеет состоянием прогона и командами)
Открывает: `ticket F<n> route` (Opus-ремонтник при подтверждённой роли `repair`), `agent-for reviewer|repair [--diff-lines N]`, `upgrade-tools`, функцию `run_id(state)`, `opus status` с проверкой подписи. Меняет: `opus_sig`/`opus_approval` (run в payload, проверка при наличии ключа в любом прогоне), `plan_contract_digest`/`plan_validation_digest` (без `F<n>-*.md`), `cmd_stage` и `cmd_init` (вызов обновления инструментов).
Поля state.js не добавляются.

### claude_agent_guard.py (владеет допуском запуска субагента)
`opus_approved(state, name)`: сверяет `sig` с `run`, при допуске по `opusAgents` сверяет ещё `agentsSig`. Профиль `opusAgents.repair` приравнен к `repairAgent` в отборе тасков по статусу. Своих списков моделей не заводит.

### Фазы и документы
Описывают команды выше; источник правды — `ap.py`.

## Швы для тестов
- `tests/test_ap.py` (`Run`): F-route на Opus при подтверждении и без; `agent-for`; подпись из другого прогона не проходит; `opus status`; `upgrade-tools` копирует только отличающееся и не работает при таске в работе; `check-plan` после F-таска не сбрасывает гейты, после правки обычного таска — сбрасывает.
- `tests/test_claude_agent_guard.py`: чужой `run` в sig → отказ; неверный `agentsSig` → отказ; repair-Opus допущен только для fix-таска в работе.
