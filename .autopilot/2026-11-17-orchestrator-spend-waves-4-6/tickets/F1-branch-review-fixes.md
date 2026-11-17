# F1 — правки по код-ревью ветки

**Требования:** R14, R15, R17, R18, R20, R11
**Зависит от:** —
**Зона:** `tools/run-tests.py` · `tests/test_run_tests.py` · `skills/autopilot/tools/ap.py` · `skills/autopilot/phases/dashboard-template.html` · `tests/test_ap.py` · `tests/test_ap_audit.py` · `tests/test_followups_dashboard.py` · `tests/test_dashboard_views.py`
**Волна:** 6
**Ревью:** да — ремонт ветки
**Модель:** сильная

## Что должно заработать

Пять замечаний ревью ветки закрыты, каждое с красным тестом до правки.

## Критерии приёмки

- [ ] `tools/run-tests.py`: модуль тестов, упавший на импорте (`unittest.loader._FailedTest`), даёт ошибку в итоге — `FAILED (errors>=1)`, код выхода 1 и показанный traceback — на Python 3.11 и 3.13 (не полагайся на то, что `python -m unittest unittest.loader._FailedTest` что-то загрузит: запускай такой модуль по его имени файла/модуля или считай ошибкой сам); тест запускателя на временной папке `tests` со сломанным модулем; «unexpected successes» попадают в итог (код 1 при них — как у unittest)
- [ ] `agents prune` и удаление на `finish` трогают только имена вида `autopilot-<executor|reviewer|acceptance|explorer>-<slug>` (`.md`/`.toml`) и `autopilot-…-opus-…`-профили, которые строит `agent_profiles`; файл `autopilot-mine.md` пользователя остаётся; фикстура `profiles_fixture` в `tests/test_ap.py` содержит такой файл и тест это проверяет
- [ ] Дашборд: при остановке опроса по неверному токену (`tokenStop`) плашка `#link` («Связь с дашбордом пропала…») скрыта — подсказка про токен и «сервер умер» не показываются вместе; тест node-vm проверяет и `#link`, не только `#app`
- [ ] `compute_history`: строка кэша принимается, только если `row.get("dir") == имя` и есть `startedAt`; иначе пересчёт этого архива; тест с кэшем `{"v":1,"items":{"<имя>":{"key":[mtime,size],"row":{}}}}` не падает с `KeyError`
- [ ] Тест через настоящий `ap.py plan-models`: при истории эскалаций Haiku в JSON есть `advice`, без истории ключа нет
- [ ] Полный `python tools/run-tests.py` зелёный; `python tools/check-dashboard.py` чисто

## Из брифа, дословно

> «`ap.py agents prune` удаляет профили `autopilot-*` с именем прогона, на которые не ссылается ни один незавершённый прогон; без `--apply` только печатает список.»
> «Неверный или отсутствующий `?t=`: страница один раз показывает подсказку про `ap.py url` и перестаёт опрашивать сервер.»
> «Битый или отсутствующий кэш пересчитывается молча.»
> «`plan-models` печатает одну строку совета из истории, когда она есть… Истории нет — строки нет.»
> «Обычная команда `python3 -m unittest discover -s tests` остаётся рабочей».

## Возврат оркестратору

Список файлов, красное до правки по каждому пункту, итог полного прогона.
