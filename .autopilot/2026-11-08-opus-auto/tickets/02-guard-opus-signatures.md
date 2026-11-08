# 02 — guard: проверка подписей Opus и ремонтник

**Требования:** R01, R02, R03, R04, R05, R08
**Зависит от:** —
**Зона:** `skills/autopilot/tools/claude_agent_guard.py` · `tests/test_claude_agent_guard.py`
**Волна:** 1
**Ревью:** да — риск: допуск дорогой модели
**Модель:** сильная

## Что должно заработать

Guard допускает Opus-профиль только при подписях, привязанных к прогону, и пускает Opus-ремонтника только на fix-таск в работе. Спецификация: §2.1, §2.2.

## Из брифа, дословно

> «Давай доработаем.» — R01
> «Все должно работать в автоматическом режиме.» — R02
> «Без вмешательства пользователя.» — R03
> «Opus-ремонт и ревью ветки» — R04
> «Подпись opusAgents в guard» — R05
> «Оставить (Recommended)» — R08: без подтверждения Opus закрыт по-прежнему

## Разделы спецификации

Решения по реализации §1, §2, §8; `interfaces.md` (Подписи, claude_agent_guard, швы для тестов). Формат подписей — единый с `ap.py` (таск 01 пишет их, этот читает): `sig` над `{"tickets","roles","run"}`, `agentsSig` над `{"opusAgents","run"}`, `run = "<slug>|<startedAt>"`.

## Критерии приёмки

- [ ] `opus_approved` отказывает, если `sig` подписан без `run` или с чужим `run` (другой slug/startedAt в state)
- [ ] допуск по имени из `opusAgents` требует верный `agentsSig` над `{opusAgents, run}`; подмена имени в `opusAgents` или отсутствие/неверный `agentsSig` → отказ (тест на каждый случай)
- [ ] допуск executor-профиля по ticket-маршруту (все таски с этим agentType в `opusApproval.tickets`) не требует `agentsSig` и по-прежнему требует верный `sig`
- [ ] профиль `opusAgents.repair` приравнен к `repairAgent`: допускается только если ровно один fix-таск (`F<n>`) в `in-progress`/`repair` маршрутизирован на него; обычный таск на repair-Opus → отказ
- [ ] без `opusApproval` или без ключа guard отклоняет Opus-профиль, как раньше; Fable отклоняется всегда (тесты прошлой сборки остаются зелёными)
- [ ] в guard нет собственного списка премиум-моделей (`test_guard_has_no_private_premium_list` проходит)
- [ ] `python -m unittest discover -s tests -p test_claude_agent_guard.py` зелёный
