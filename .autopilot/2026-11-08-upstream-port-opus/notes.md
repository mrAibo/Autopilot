# Заметки о коде (разведка, 2026-11-08)

Пути от корня; инструменты — `skills/autopilot/tools/`.

## Уже есть в коде (не переписывать, только проверить тестом)
- `ap.py` `cmd_ticket` (≈1739-1755): `retry` при `retries>=2` и `repair` при `repairs>=2` → `die("предел повторов/ремонтов достигнут")`; `retry_policy.decide(kind, attempts, repairs)` отсекает причины, не лечащиеся повтором; `--cause` обязателен в strict.
- `cmd_ticket` done (≈1722-1727): без успешных тестов и без `verified_commit(rev)` (`rev = --commit или tk.commit`, коммит должен быть предком HEAD) → `die`. Работает во всех режимах, не только strict.
- `cmd_finish` (2322-2407): уже отказывает при: подделке записи гейтов, открытых `blockingFindings`, старых repairFindings без записи, resolved-блокерах с коммитом вне HEAD, done-тасках с коммитом вне HEAD, G1–G4 не ok, смене `planContractDigest`, красном `check_plan`; затем stages, незавершённые таски/пустой план, тесты `passed>=1,failed==0`, открытые строки манифеста, rename `--wip`, `register_row(state,"сдан",...)`.

## Чего нет
- `reset` упавшего таска не требует ничего (≈1876-1879: снимает startedAt/finishedAt, пишет `ticket-reset reason=manual`). `landedWith`, `blindRounds`, `reopenedByUser`, `opusApproval` нигде нет.
- G1 считается только в `cmd_stage` для `stage spec start|done` (≈1112-1116: `open==0`, строки без `D`) и сбрасывается при `check-plan` со сменой контракта (≈2578). Правка манифеста после спецификации G1 не обновляет.
- `cmd_numbers blind` (≈2287-2297): без ограничения числа записей; G4 ok = `valid and not mismatches`.
- `cmd_reopen` (2410-2432): `blind=None`, `gates={}`, stages → pending, `register_row "в работе"`.
- Git-проверки записи в preflight нет (`repo_doctor.py` только читает).

## Имена
- `ap.py`: `TICKET_STATUSES` (101-103), `die`, `set_gate` (226-232), `manifest_table` (300-315, колонка 3 — статус), `recount`, `check_plan` (540-595), `blocker_ledger` (2159), `verified_commit` (1156), `register_row` (902-919), `gate_signed` (1245), `sign_routing/routing_signature_ok` (1262-1273), `check_claude_attestation` (1290-1358), `plan-models` (1406-1599; пишет `roleAgents`, `repairAgent` на 1590-1591), `parse_ticket` (415-447; поле `Модель:` → `tk["model"]`, в маршрут не идёт), `fresh_state` (254-279).
- `model_router.py`: `PREMIUM_FAMILIES=("opus","fable")` (50), `is_premium_model` (69-72), `is_allowed_subagent_model` (75-88), `normalize_model_name` (57-66), `DEFAULT_POLICY` (22-43; anthropic: cheap haiku/low, balanced sonnet/medium, strong sonnet/high, critical sonnet/xhigh; restricted: fable), `assess_scores` (157-173), `assess_ticket` (185-208), `choose_route` (211-281; restricted-ошибка на 243-244; `requires_review` на 253).
- `claude_agent_guard.py`: решение для Agent/Task (226-341); премиум отсекается на 276-277 (`is_allowed_subagent_model(model)`); читает state (`tickets`, `strictRouting`, `finishedAt`, `repairAgent`), `.claude/agents/<name>.md`, `model-capabilities.json`; `roleAgents` НЕ читает; рядом есть тест «в guard нет приватного списка премиум-моделей».
- `claude_attest.py`: премиум не проверяет; проверка `resolvedModel` — `ap.py check_claude_attestation`.
- `agent_profiles.py`: `prepare(root, ticket, provider, capabilities, role, policy, scores, install)` (114-171), `definition()` (49-111); allowlist только через `choose_route`.
- `gate_sign.py`: `sign`, `verify`, `routing_payload`, `evidence_payload`, `run_mark`.
- `phases/dashboard-template.html`: шапка `buildH2/buildAllDone/doneState` (≈1068-1078), `fin = !!S.finishedAt`, `heroCls='won'`, `h2 = esc(S.result||L.doneDefault)` (1703-1707); маршруты — `routed`, `mchip` (≈2311), `routesCard` (≈2165), вид `models`. `landedWith` там нет.

## Тесты (имена для правки/опоры)
- `tests/test_ap.py` класс `Run`: `test_ticket_lifecycle_counters`, `test_finish_*`, `test_gates_follow_the_events_that_decide_them`, `test_reopen_puts_wip_back`.
- «Opus/Fable не проходят», менять осторожно: `test_model_router.py`: `test_strong_anthropic_uses_sonnet_not_opus_or_fable`, `test_restricted_models_are_denied_even_when_advertised`, `test_premium_alias_cannot_bypass_restrictions`, `test_premium_and_unknown_names_are_refused_in_every_spelling`, `test_route_refuses_opus_hidden_before_a_slash`, `test_route_refuses_bedrock_style_opus`; `test_claude_agent_guard.py`: `test_premium_or_inherited_model_is_denied`, `test_every_opus_spelling_is_denied_by_the_shared_allowlist`, `test_guard_has_no_private_premium_list`; `test_agent_profiles.py`: `test_premium_rejected_even_if_host_advertises`; `test_ap.py`: `test_route_rejects_unapproved_model_even_with_host_advertisement`.

## Куда вписывать в фазах (skills/autopilot/)
- `SKILL.md`: «Model routing» ≈134-137; «Reading this skill» ≈35 (перечитывание после сжатия).
- `phases/0-preflight.md`: «2. Git» ≈27-33.
- `phases/4-plan.md`: «Review and model — decided per ticket» ≈47-73; «Showing the plan» ≈133; «How to cut» ≈23.
- `phases/5-repair.md`: «When a ticket fails» ≈51-55; рядом «BLOCKED» ≈47.
- `phases/6-review.md`: «The whole-branch review» ≈47.
- `phases/8-final.md`: «1. Blind acceptance» ≈13-58; «5. Landing» ≈160.
