# 01 — Одна страница вместо девяти раскладок

**Требования:** R30, R30a, R30b, R30c, R30d, R32b
**Зависит от:** —
**Зона:** `skills/autopilot/phases/dashboard-template.html` · `tests/test_dashboard_views.py` · `tests/test_dashboard_now.py` · `tests/test_dashboard_boards.py` · `tests/test_dashboard_details.py` · `tools/test-dashboard-render.js` · `tools/check-dashboard.py` · `tools/check-dashboard-browser.py`
**Волна:** 1
**Ревью:** да — фундамент
**Модель:** сильная
**Класс:** сложный
**Риск:** обычный
**Причина класса:** снос девяти раскладок и перепись тестов вокруг общего харнесса, много связей в одном файле

## Что должно заработать

Дашборд рисует одну страницу в раскладке A «Лента» (`mockups/dashboard-single-page/a-lenta.html`): шапка, герой, закреплённая полоса «ждёт ответа», затем секции `<details>`: маршрут этапов, требования, таски с Ганттом, проверки и тесты, расход и модели, гейты, лента. Вкладок и девяти раскладок нет; combobox выбора раскладки из шапки убирается (выбор дизайна добавит таск 02). Боковая рейка строится по якорям, которые есть на странице. Дизайн пока один — «Аврора» как сейчас. Тесты и инструменты переписаны под одну страницу.

## Из брифа, дословно

> «Основная страница одна, секциями сверху вниз, без вкладок: шапка и «Нужно от вас» вверху, герой, маршрут этапов, требования, таски с Ганттом, проверки и тесты, расход и модели, гейты, лента. Секции сворачиваются через `<details>`, а не вкладками.»
> «в основу ложится раскладка A «Лента» … одна колонка до ~1100 px по центру, шапка, герой с главным ответом, закреплённая полоса «ждёт ответа», затем секции в порядке важности.»
> «Девять прежних раскладок уходят из combobox и из шаблона. На ширине до 520 px страница сама сжимается в один столбец»
> «Прежние ссылки на `data-view` и `autopilot-view` в `localStorage` читаются без ошибки и игнорируются; пункты боковой рейки строятся по тем якорям, что есть на странице.»
> «тесты `test_dashboard_views.py` переписаны под одну страницу; старый `state.js` без `blind`, `debt`, `usageEvents`, `startedAt` по-прежнему рисует страницу целиком.»
> «Поведение шлюзов G1–G4, слепой приёмки, подписей, guard, правил Opus и запрета Fable не меняется.»

## Разделы спецификации

Истории 6–10 и 18; «Решения по реализации» (раскладка A как единственный `page`, `autopilot-boardmode` убирается, рейка); «Уточнения» (рейка без якоря); `interfaces.md` — «Страница».

## Критерии приёмки

- [ ] В `dashboard-template.html` нет `VIEWS`, `VIEW_IDS`, `VIEW_HOME`, `UI.tab`, `data-ntab`, ленты `class="tabs views"`, `data-views-more`; `storedView` не существует, а ключ `autopilot-view` и `autopilot-boardmode` в `localStorage` не читаются на отрисовку и не бросают ошибок (тест кладёт в хранилище `autopilot-view=classic`, `focus`, мусор — страница рисуется одинаково)
- [ ] Одна функция `page(c)` отдаёт секции `<details class="sec" id="mission|tasks|models|quality">` и остальные из списка брифа; каждая `summary` ≥44 px; закреплённая полоса «ждёт ответа» рисуется только при `state.waiting` (`role="status"`, sticky), и её нет без ожидания
- [ ] Колонка по центру `max-width` ~1100 px; на ширине до 520 px один столбец по правилу `@media(max-width:520px)` (последнее в CSS), без выбора вида
- [ ] Рейка `aside.cockpit-rail` рисует ссылку только на якорь, чей `id="…"` есть в HTML страницы; `skip-link`, `cockpit-content`, `cockpit-rail`, `planned-model-routes`, `sequential-host-notice`, `no child agent is created`, якорь `/*STATE-BEGIN*/…/*STATE-END*/` (ровно один) на месте
- [ ] Фикстуры `empty, running, finished, nodone, old, oldfin, notes, landed, opus, ask, returned, gated` и `state.js` без `blind`, `debt`, `usageEvents`, `startedAt` рисуются целиком на двух языках без исключения (`python -m unittest tests.test_dashboard_views` зелёный)
- [ ] `tests/test_dashboard_views.py`, `test_dashboard_now.py`, `test_dashboard_boards.py`, `test_dashboard_details.py` переписаны под одну страницу (без `VIEW_IDS`/`UI.tab`; тестовый модуль `test_dashboard_views` экспортирует временно `DESIGN_IDS = ['aurora']` вместо `VIEW_IDS`; таск 02 заменит это чтением реестра из шаблона); тест на «Нужно от вас»-полосу, секции и якоря есть; проверка `dashboard-views.md` по девяти id снята
- [ ] `tools/test-dashboard-render.js`, `tools/check-dashboard.py`, `tools/check-dashboard-browser.py` не ссылаются на девять id и `VIEW='classic'`; `python tools/check-dashboard.py` проходит
- [ ] `git diff` таска не содержит `ap.py`, `gate_sign.py`, `claude_agent_guard.py`, `model_router.py`, `state_io.py`
- [ ] `python -m unittest discover -s tests -p "test_dashboard_*.py"` и `python tools/run-tests.py` зелёные (число тестов может измениться)
