# 02 — `ask accept` только в manual, `::имя`, redproof, git-версия, chore

**Требования:** R02, R04, R05, R19, R21
**Зависит от:** —
**Зона:** `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/plan_items.py` · `tests/test_dashboard_actions.py` · `tests/test_review_accuracy.py` · `tests/test_work_kinds.py` · `tests/test_one_command.py` · `tests/test_git_version.py`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** пять небольших правок CLI с регресс-тестами, без нового протокола

## Что должно заработать

`ap.py ask accept` отказывает вне режима `manual`. `plan-fact record` с `::имя` не принимает подстроку. `redproof` не отказывает из-за слов «cannot import name» вне строки исключения. `doctor` печатает версию git и предупреждает ниже 2.22. Отказ `chore` называет грязный файл и что делать.

## Из брифа, дословно

> «ADR `0015`: `ask accept` ограничен режимом `manual` только текстом фаз, CLI пускает его везде»
> «`::имя` ищется подстрокой»
> ««cannot import name» в выводе даёт ложный отказ `redproof`»
> «трейлер `Autopilot-Ticket` нужен git ≥ 2.22»
> «`chore` не принимает грязный `AGENTS.md`, запускать до правок»

## Разделы спецификации

Решения R02, R04, R05, R19, R21; `interfaces.md` — «`ask accept`», «`::имя`», «`doctor`».

## Критерии приёмки

- [ ] `ask accept` в режиме semi/full/interview — код ≠ 0 и строка с текущим режимом; в `manual` — как раньше; тесты `test_dashboard_actions.py`, звавшие `ask accept` вне manual, переведены на manual и зелёные
- [ ] `plan-fact record --verdict "T.. | сделано | файл::run"` не принимается, когда в файле только `runtime`; принимается при целом слове `run`
- [ ] `redproof`: вывод с `ImportError: cannot import name X` в начале строки — отказ; вывод, где фраза только внутри текста (например в строке `assert "cannot import name" ...`), — принят; прежние признаки отказа сохранены, тесты `test_work_kinds.py` зелёные
- [ ] `doctor` печатает `git: версия N.N`; ниже 2.22 — предупреждение без кода 2; версию не прочитать — `git: версия не определена`, код как раньше; тест подменяет вывод `git --version`
- [ ] Отказ `chore` из-за грязного файла генератора называет файл и действие («закоммить или отмени правки в …»); файл пользователя не тронут; тест
