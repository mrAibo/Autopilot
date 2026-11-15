# F3 — Калибровка роутера: «обычный» не уходит на Haiku, зона по целым сегментам

**Требования:** R07
**Зависит от:** —
**Зона:** `skills/autopilot/tools/model_router.py` · `skills/autopilot/phases/4-plan.md` · `docs/autopilot/model-routing.md` · `docs/adr/0007-planner-assessment-instead-of-regex.md` · `tests/test_followups_routing.py` · `tests/test_audit_routing.py` · `tests/test_model_router.py` · `tests/test_ap.py` · `tests/test_offline_supervisor.py` · `tests/test_host_loop.py`
**Волна:** 4
**Ревью:** нет
**Модель:** сильная
**Класс:** обычный
**Риск:** высокий
**Причина класса:** правка роутера моделей, около 60 строк с тестами; ошибка калибровки уводит обычные таски на дешёвую модель
**Объём:** 120

## Что должно заработать

После замены регулярных выражений оценкой планировщика обычный таск (с классом «обычный» или без класса) в кодовой зоне не уходит на Haiku/low: Haiku остаётся только за «механическим» классом, как описано в `phases/4-plan.md`. Чувствительная зона определяется по целым сегментам пути, а не по подстроке в имени.

## Из брифа, дословно

> «Надо бы выбирать модели более интеллигентно, а не по regular expression, есть там слово какое-то или нет. Это слишком ненадежно и грубо.»

## Критерии приёмки

Найдено слепой приёмкой, второй круг: таск «обычный» в зоне `src/ui/` получает `haiku/low, score 10`; зоны `src/author/` и `src/secretary/` получают `sonnet/high, риск высокий`.

- [ ] Таск с `**Класс:** обычный` и таск без заголовка класса в зоне, которая не docs-only, получают профиль не ниже `balanced` (Sonnet), а не `cheap`; класс `механический` по-прежнему даёт Haiku (`cheap_code`, haiku/high), `сложный` — `strong`; таск без класса в docs-only зоне остаётся как считается (риск 0, допустим `cheap`)
- [ ] Чувствительная зона определяется по целым сегментам пути (разбиение по `/`, `\`, `.`, `_`, `-`, пробелу, сравнение с нижним регистром) и по точным именам файлов (`claude_agent_guard`, `gate_sign`, `model_router`, `state_io`, `gate.key`), а не подстрокой: `src/author/`, `src/secretary/`, `src/tokenizer/`, `docs/token.md` не чувствительны; `src/auth/`, `src/auth_service.py`, `payments/`, `migrations/`, `.env`, `skills/autopilot/tools/gate_sign.py` чувствительны (`risk=10`)
- [ ] Тесты на оба поведения падают на текущем коде и проходят после правки; обновлённые старые тесты (`test_audit_routing`, `test_model_router`) не ослаблены, а переписаны под новую семантику; `phases/4-plan.md`, `docs/autopilot/model-routing.md` и ADR 0007 описывают это одинаково
- [ ] `python -m unittest discover -s tests -p test_followups_routing.py`, `-p test_audit_routing.py`, `-p test_model_router.py`, `-p test_audit_docs.py`, `-p test_agent_profiles.py` и `-p test_ap.py` зелёные
