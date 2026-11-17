# 01 — r13-model-names-latest

**Требования:** R13
**Зависит от:** —
**Зона:** `skills/autopilot/tools/model_router.py` · `tests/test_model_router.py` · `tests/test_claude_agent_guard.py` · `docs/autopilot/model-routing.md`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** одна правка регэкспа и таблица тестов на имена; зона чувствительная (`model_router`), поэтому маршрут не ниже сильного

## Что должно заработать

Имена семейства 5 покрыты тестами во всех написаниях; алиасы `-latest` у Haiku и Sonnet допустимы субагентам.

## Из брифа, дословно

> **R13. Имена моделей семейства 5**
> - Тесты `is_allowed_subagent_model`, `is_opus_model`, `is_premium_model` на написания `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-2`, с префиксами Bedrock и суффиксом даты: Haiku и Sonnet проходят, Opus только с подтверждением, Fable никогда.
> - Алиас `claude-3-5-haiku-latest` (и вообще `-latest` у Haiku и Sonnet): открытый пункт `PROGRESS.md`. Вопрос брифинга; моя рекомендация — разрешить, у Opus `-latest` уже разбирается.

Полный текст — раздел R13 и разделы 1, 4, 5 брифа (`2026-11-17-brief.md` в папке сборки); к сборке относятся только волны 4–6.

## Разделы спецификации

Истории: R13 (см. `spec.md`); «Решения по реализации»; «Вне рамок». Код и тесты — `notes.md` (раздел R13); границы — `interfaces.md`.

## Критерии приёмки

- [ ] `ALLOWED_SUBAGENT_RE` принимает `-latest` у Haiku и Sonnet (`claude-3-5-haiku-latest`, `claude-haiku-latest`, `claude-sonnet-4-latest`, `claude-sonnet-latest`); `claude-fable-*-latest` и любой Fable по-прежнему не проходит; Opus `-latest` разбирается как раньше
- [ ] Тесты `SubagentAllowlistTests`: `claude-haiku-5-5`, `claude-sonnet-5-5` (с префиксами `us.anthropic.`, `anthropic.`, `global.`, `eu.`, суффиксом даты и `-v1:0`) проходят; `claude-opus-5-5` — только с `premium_ok`; `claude-fable-5-2` — никогда; `is_opus_model`/`is_premium_model` на тех же именах
- [ ] Строки `-latest` у Haiku и Sonnet переехали из `DENIED` в `ALLOWED`; тесты `claude_agent_guard`, затронутые изменением, зелёные
- [ ] `docs/autopilot/model-routing.md`: абзац про разрешённые имена называет `-latest` у Haiku и Sonnet

## Возврат оркестратору

Список изменённых файлов, какие тесты запускал и результат, что не сделано и почему.
