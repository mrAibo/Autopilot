# 03 — Фазы и документы

**Требования:** R01, R02, R03, R04, R05, R06, R07, R08
**Зависит от:** 01, 02
**Зона:** `skills/autopilot/phases/` · `skills/autopilot/SKILL.md` · `docs/autopilot/` · `CHANGELOG.md` · `tests/test_dashboard_views.py`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Фазы и документы описывают то, что делает `ap.py` после таксков 01 и 02. Источник правды — `ap.py`. Правятся только места, где поведение изменилось.

## Из брифа, дословно

> «Давай доработаем.» — R01
> «Все должно работать в автоматическом режиме.» — R02
> «Без вмешательства пользователя.» — R03
> «Opus-ремонт и ревью ветки» — R04
> «Подпись opusAgents в guard» — R05
> «Автообновление .autopilot/*.py» — R06
> «Гейты не сбрасываются зря» — R07
> «Оставить (Recommended)» — R08

## Разделы спецификации

Решения по реализации §3–§8; `interfaces.md` (Фазы и документы).

## Критерии приёмки

- [ ] `phases/5-repair.md` и `CHANGELOG.md` больше не называют Opus-ремонт нерабочим: `ticket F<n> route` сам назначает Opus-ремонтника при подтверждённой роли `repair`
- [ ] `phases/6-review.md` и `phases/5-host-claude.md`: ревьюера ветки и ремонтника зовут по `ap.py agent-for reviewer|repair --diff-lines N`
- [ ] `phases/0-instruments.md` и `phases/0-resume.md`: копирование инструментов — `ap.py upgrade-tools` (само при `init` и `stage`), ручной `cp` остаётся только как запасной путь до первого `init`
- [ ] `phases/4-plan.md` и `phases/8-final.md`: fix-таски не входят в контракт плана, `check-plan` после них гейты не сбрасывает; сдача с оговорками — только `--by-user`, как раньше
- [ ] `docs/autopilot/model-routing.md` и `claude-code.md`: формат подписей (`run`), `agentsSig`, `agent-for`; подтверждение Opus и `--by-user` по-прежнему от пользователя
- [ ] `CHANGELOG.md`: запись об этой доработке, честная пометка, что экономия Opus-субагентов не измерена; `tests/test_dashboard_views.py` и `test_documentation_locales.py` зелёные
