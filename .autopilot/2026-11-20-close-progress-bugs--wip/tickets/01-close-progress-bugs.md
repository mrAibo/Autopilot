# 01 — Закрыть баги и хвосты из PROGRESS.md

**Требования:** R01, R02, R03, R04, R05, R06, R07, R08, R09, R10, R11, R12
**Зависит от:** —
**Зона:** `skills/autopilot/tools/plan_items.py` · `skills/autopilot/tools/land_check.py` · `skills/autopilot/tools/ap.py` · `tests/` · `.github/workflows/python-tests.yml` · `AGENTS.md` · `CHANGELOG.md` · `docs/autopilot/measuring-cost.md` · `docs/adr/`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** точечные правки существующей логики в пяти местах, каждая с тестом; без новых протоколов

## Что должно заработать

Исправлены четыре группы багов из «Известные баги» `.autopilot/PROGRESS.md` (plan-fact record, land_check, blocker confirm и redproof), вердикт второго прохода хранится в блокере, а CI гоняет `python tools/run-tests.py`. Все границы и имена — в `interfaces.md` и `spec.md` (истории 1–12) папки прогона; `notes.md` — где что лежит.

## Из брифа, дословно

> «закрой из .autopilot/PROGRESS.md: баги plan-fact record, land_check, blocker confirm; хранение вердиктов второго прохода; CI на tools/run-tests.py. R28 и R33–R35 не трогай»

## Разделы спецификации

Истории 1–12, «Решения по реализации», `interfaces.md` («Границы, решённые в спецификации»).

## Критерии приёмки

- [ ] `plan-fact record` по части id не стирает вердикты остальных пунктов (тест: два вызова, оба вердикта в `planFact`)
- [ ] Вердикт «сделано» без доказательства `путь:строка`/`путь::имя` с существующим путём даёт `не сделано` и строку в `concerns` (тест)
- [ ] Вердикт на несуществующий id — отказ с перечнем id, `planFact` и `concerns` не тронуты (тест)
- [ ] Повторный одинаковый `plan-fact record` не удваивает `concerns` «план: …» (тест)
- [ ] `land_check.preflight` с `files`: соседний таск с общим префиксом зоны, но без общего вливаемого файла, отказа не даёт; `src/a` и `src/ab` не пересекаются (тест)
- [ ] Коммит с темой `T01: …` в зоне после старта таска 01 отказа не даёт, чужой коммит в вливаемом файле — даёт (тест)
- [ ] Проект в подпапке репозитория: чужой коммит в зоне даёт отказ, `unsupported` пуст (тест); старый тест про `unsupported` обновлён под «git не отвечает»
- [ ] Второй `blocker confirm` по блокеру с вердиктом — отказ, статус остаётся прежним (тест `confirmed` → `not-confirmed`)
- [ ] `blocker confirm` пишет `secondPass` (`verdict`, `quote`, `at`) и событие журнала с `verdict` (тест)
- [ ] `ticket NN redproof` отказывает при коде 127 и при выводе с `SyntaxError`, но принимает обычное падение теста (тест)
- [ ] В `python-tests.yml` шаг тестов — `python tools/run-tests.py`, `unittest discover` из workflow убран; матрица ОС и версий Python в workflow не изменена; в `AGENTS.md` исправлены фразы «CI запускает то же» (таблица команд) и «(CI не меняется)»/«CI остаётся на unittest discover» (подводные камни), в `docs/` — тоже (тест на файл workflow)
- [ ] `docs/autopilot/measuring-cost.md` объясняет, как считать долю снятых вторым проходом по `secondPass`; `CHANGELOG.md` («Unreleased») и `AGENTS.md` (строка про `plan-fact record`: больше не «заменяет целиком») обновлены; блокеры без `secondPass` читаются без ошибки (тест)
- [ ] Файлы R28 и R33–R35 не тронуты (`git diff --stat` не называет их); полная проверка `python tools/run-tests.py` зелёная
