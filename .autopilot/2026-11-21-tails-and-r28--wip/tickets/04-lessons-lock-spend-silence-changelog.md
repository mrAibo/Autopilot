# 04 — Уроки под замком, расход без дублей и чужих папок, тест без `~/.claude`

**Требования:** R06, R07, R08
**Зависит от:** 03
**Зона:** `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/lessons.py` · `skills/autopilot/tools/run_log.py` · `tests/test_lessons.py` · `tests/test_subagent_spend.py` · `tests/test_review_accuracy.py` · `CHANGELOG.md`
**Волна:** 3
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** три независимые правки по образцу соседнего кода, с регресс-тестами

## Что должно заработать

Проверка путей в уроках ловит больше форм абсолютных путей; запись `lessons.md`, `lessons.md.seen`, `profile.md` идёт под замком. Поиск журнала сессии по префиксу не берёт соседний проект; повторный `spend-*` с теми же числами не дописывает строк. Тест на `silence` не читает реальный `~/.claude`. В `CHANGELOG.md` («Unreleased») записаны все пункты прогона.

## Из брифа, дословно

> «`lessons`: проверка путей ловит только `X:\`, `/Users/`, `/home/`; `lessons.md`, `drop`, `profile refresh` пишут без замка»
> «`test_silence_without_any_transcript_is_not_all_alive` читает реальный `~/.claude`»
> «Расход: поиск папки субагентов по префиксу может взять соседний проект; повторный `spend-orchestrator` дописывает строки»

## Разделы спецификации

Решения R06, R07, R08; `interfaces.md` — «Расход (T04)»; `notes.md` — «lessons», «Тест silence», «Расход».

## Критерии приёмки

- [ ] `lessons add` отказывает на тексте с `~/`, `C:/…`, `\\сервер\…`, `/root/`, `/private/`, `/var/folders/` (по тесту на каждую форму), прежние формы тоже
- [ ] `lessons add`, `drop`, `profile refresh` выполняются под `locked_state` (как остальные записывающие команды); тест: два параллельных `add` дают обе строки без порчи файла
- [ ] `test_silence_without_any_transcript_is_not_all_alive` ставит `CLAUDE_CONFIG_DIR` на пустую временную папку и проходит при наличии реального `~/.claude` с журналами
- [ ] `session_transcript`: запасной поиск по префиксу не принимает папку соседнего проекта (тест: две папки, одна — префикс пути другого проекта); нет однозначной — журнала нет
- [ ] Повторный `spend-orchestrator` и `spend-subagents` с теми же числами не добавляют строку в `run-log.jsonl`; с новыми числами — добавляют (тесты)
- [ ] `CHANGELOG.md` («Unreleased») получил по строке на: кнопки (подпись, `ask accept`), сервер (nonce, перезапуск, лог), `::имя`, `redproof`, git-версию, `chore`, уроки, расход, тест silence, мёртвый CSS, `shots.py` и ADR `0030`–`0033`
