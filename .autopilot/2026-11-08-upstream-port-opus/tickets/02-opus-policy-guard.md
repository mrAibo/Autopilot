# 02 — Opus: политика роутера, допуск guard и профили

**Требования:** R16, R18, R20, R21, R23, R26, R27, R29, R30
**Зависит от:** —
**Зона:** `skills/autopilot/tools/model_router.py` · `skills/autopilot/tools/claude_agent_guard.py` · `skills/autopilot/tools/agent_profiles.py` · `tests/test_model_router.py` · `tests/test_claude_agent_guard.py` · `tests/test_agent_profiles.py`
**Волна:** 1
**Ревью:** да — риск: допуск дорогой модели в строгом прогоне

## Что должно заработать

Роутер, guard и генератор профилей получают исключительный маршрут Opus, который работает только при подтверждении пользователя; без подтверждения всё ведёт себя как до этого таска, Fable закрыт всегда. Спецификация: §4.7 (model_router, guard, agent_profiles).

## Из брифа, дословно

> «C1. По умолчанию ничего не меняется: Opus выключен, поведение и тесты «Opus не проходит» остаются, пока нет подтверждения.» — R16
> «C3. В роутере отдельный уровень выше «сильной». Выбирается только для тасков с высоким риском (безопасность, конкурентность, миграции данных) или с явной пометкой в файле таска, и только при подтверждении по C2.» — R18
> «C5. Нужно согласовать с `claude_agent_guard.py`, `claude_attest.py` и закреплёнными профилями в `.claude/agents/`: что в attest считается допустимой моделью, как guard проверяет подтверждение.» — R20
> «C6. Тесты переписываются из «Opus не проходит» в «Opus не проходит без подтверждения, и проходит только для помеченного таска при подписанном подтверждении». Отдельный тест на поддельное подтверждение.» — R21
> «Все 669 тестов остаются зелёными, добавленные тесты идут вместе с кодом.» — R23
> «Поведение по умолчанию (без `--by-user`, без подтверждения Opus) в рабочих прогонах не меняется, кроме новых отказов из A1, A3, B2 и B3: они и есть смысл брифа.» — R26
> «`state.js` пишется только через `state_io.py`; харнессы, копирующие `ap.py`, копируют `state_io.py`, `process_containment.py`, `run_log.py`.» — R27
> «`python3 -m unittest discover -s tests` зелёный на 3.11 и 3.13.» — R29
> «По одному регрессионному тесту на каждый пункт A1–A3, B1–B5 и C6.» — R30

## Разделы спецификации

Истории 16, 18, 20, 21; Решения §4.7; `interfaces.md` (model_router, claude_agent_guard, agent_profiles).

## Критерии приёмки

- [ ] `is_allowed_subagent_model(name)` без флага даёт те же результаты, что раньше, для всех случаев существующих тестов; `is_allowed_subagent_model(name, premium_ok=True)` допускает любое написание семейства opus (как в `test_every_opus_spelling_is_denied_by_the_shared_allowlist`) и по-прежнему отклоняет fable, astra и неизвестные имена
- [ ] `is_opus_model` истинна для opus во всех написаниях (в том числе bedrock-стиль, обёртки, `@дата`) и ложна для fable, sonnet и haiku
- [ ] `choose_route(..., premium=True)` для anthropic возвращает `model` семейства opus со `status` как у обычного маршрута и не бросает «restricted»; `premium=False` — как раньше; для openai `premium=True` не открывает Astra
- [ ] `premium_candidate` истинна при `risk >= 10` или профиле `critical` и ложна иначе
- [ ] guard пропускает запуск агента с `model: opus` только если в state есть `opusApproval` с верной подписью (`gate_sign.verify`) и: executor — id таска маршрута в `opusApproval.tickets`; либо имя равно `opusAgents.reviewer` и `reviewer` в `roles`; либо имя равно `opusAgents.repair` и `repair` в `roles`; иначе отказ с прежним текстом (тест на каждую ветку и на поддельную подпись)
- [ ] без `opusApproval` guard отклоняет opus-профиль так же, как раньше; профиль fable отклоняется всегда, даже с подтверждением
- [ ] `agent_profiles.prepare(..., premium=True)` создаёт закреплённый профиль с `model: opus`; без флага opus по-прежнему не создаётся (`test_premium_rejected_even_if_host_advertises` остаётся верным для вызова без флага)
- [ ] в `claude_agent_guard.py` нет собственного списка премиум-моделей (`test_guard_has_no_private_premium_list` проходит)
- [ ] перечисленные в `notes.md` тесты «Opus не проходит» переписаны так, что вызов без подтверждения явный; добавлены тесты с подтверждением; все остальные тесты проходят
