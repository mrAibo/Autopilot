# 01 — Закрыть три слабых места: schedule и review, commit_paths и каталог, занятая заявка gate_sign

**Требования:** R01, R02, R03, R04
**Зависит от:** —
**Зона:** `skills/autopilot/tools/scheduler.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/tools/gate_sign.py` · `skills/autopilot/phases/` · `tests/` · `CHANGELOG.md` · `docs/adr/`
**Волна:** 1
**Ревью:** нет
**Модель:** сильная
**Класс:** обычный
**Риск:** высокий
**Причина класса:** правка кода подписи ключа (`gate_sign`) и коммита (`commit_paths`); остальное — небольшие правки по образцу

## Что должно заработать

Три слабых места из «Известные баги» `.autopilot/PROGRESS.md` закрыты (решения — `spec.md`, границы — `interfaces.md`, где что лежит — `notes.md` папки прогона). Файлы R28 и R33–R35 не трогать. Не коммитить (коммитит оркестратор).

## Из брифа, дословно

> «`ap.py schedule` не предлагает таск с зависимостью в `review`, хотя `ticket start` его пускает»
> «`commit_paths`: старый путь переименования подхватывается только при дословном совпадении пути, каталог зоны не работает»
> «`gate_sign`: при стойко занятой заявке `gate.key.claim` `ensure_key` падает `OSError` даже над целым ключом»
> «R28 и R33–R35 не трогай»

## Разделы спецификации

Таблица «Решение» (R01–R04), «Решения по реализации», «Уточнения».

## Критерии приёмки

- [ ] R01: `scheduler.schedule` при `isolated=False` предлагает pending-таск, чья зависимость в `review` (`action` `start`); зависимость в `in-progress`, `repair`, `failed`, `pending` и неизвестный id — по-прежнему `dependencies` (тест в `tests/test_scheduler.py`); при `isolated=True` зависимость в `review` по-прежнему блокирует (тест)
- [ ] R02: `commit_paths(["dir/"])` и `commit_paths(["dir"])` после `git mv dir/old.txt dir/new.txt` кладут старый путь в тот же коммит (в HEAD `D dir/old.txt`, индекс чист); переименование из каталога вне `paths` в каталог из `paths` — тоже; чужое индексное переименование не попадает в коммит; прежние тесты `CommitPathsRename` зелёные (тесты в `tests/test_review_race_bugs.py`)
- [ ] R03: когда `_claim_empty` бросает `OSError` из-за занятой заявки, а `gate.key` за это время стал целым, `ensure_key()` возвращает ключ и не падает, байты ключа не изменились (тест); если ключ пуст, `OSError` прежний и называет `gate.key.claim` (прежний тест остаётся зелёным)
- [ ] Запись в `CHANGELOG.md` («Unreleased») на каждый из трёх пунктов; в `docs/adr/0029-review-start-rename-key-race.md` — строка о дополнении; фразы в `phases/` не противоречат R01
- [ ] Полная проверка `python tools/run-tests.py` зелёная
