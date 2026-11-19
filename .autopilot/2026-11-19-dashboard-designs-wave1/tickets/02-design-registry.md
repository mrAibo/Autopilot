# 02 — Реестр дизайнов, выбор и хранение

**Требования:** R29, R29a, R29b, R29c
**Зависит от:** 01
**Зона:** `skills/autopilot/phases/dashboard-template.html` · `tests/test_dashboard_designs.py` · `tests/test_dashboard_views.py`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** новая логика реестра, поиска и хранения поверх готового combobox

## Что должно заработать

В шапке combobox выбирает один из шести дизайнов (aurora, editorial, brutal, terminal, blueprint, bento): поиск по имени ru/en, номеру, id и тегам, клавиатура как у прежнего combobox. Выбор ставит `data-design` на `<html>` и живёт в `localStorage`. Пока все шесть дают токены «Авроры» плюс собственные акцент и `data-design`-селектор-заготовку; настоящие палитры добавят таски 03 и 04. Схема темы: кнопки светлая/тёмная видны только у дизайнов со `scheme:'both'`.

## Из брифа, дословно

> «В шаблоне появляется реестр `DESIGNS` (id, номер, имя ru/en, подпись, акцент, теги), по образцу `mockups/dashboard-2026/designs.js`: `aurora`, `editorial`, `brutal`, `terminal`, `blueprint`, `bento`.»
> «Дизайн включается атрибутом `<html data-design="…">`; он задаёт токены и декоративные правила для **тех же блоков**, а не отдельную разметку и не iframe.»
> «Combobox в шапке … выбирает дизайн; поиск идёт по имени на двух языках, номеру, id и тегам; стрелки, Enter, Esc, `aria-activedescendant` как сейчас.»
> «Выбор хранится в `localStorage` (`autopilot-design`); по умолчанию `aurora`. Неизвестное значение или ошибка хранилища — `aurora`.»

## Разделы спецификации

Истории 1–4; «Уточнения» (схемы, теги, акценты); `interfaces.md` — «Реестр дизайнов».

## Критерии приёмки

- [ ] `DESIGNS` в шаблоне: шесть записей в порядке aurora 01, editorial 02, brutal 03, terminal 04, blueprint 05, bento 06, у каждой `id, no, name.ru/en, tagline.ru/en, accent, scheme, tags`; схемы: aurora `both`, editorial/blueprint/bento/brutal `light`, terminal `dark`; акценты и теги как в `mockups/dashboard-2026/designs.js`; `DESIGN_IDS`, `DESIGN_KEY='autopilot-design'`, `DEFAULT_DESIGN='aurora'` определены
- [ ] `storedDesign()` возвращает `aurora` при пустом хранилище, неизвестном значении и при исключении `localStorage.getItem`; `selectDesign(id)` пишет `autopilot-design`, ставит `data-design` на `<html>` (и при первой отрисовке тоже) и перерисовывает; ошибка записи не роняет страницу
- [ ] `comboList(q)`: «чертёж», «blueprint», «05», «5», «mono», «light» дают ожидаемые дизайны, пустой запрос — все шесть по порядку, мусор — пустой список с сообщением «ничего не найдено» на двух языках; ArrowDown/Up/Enter/Escape, `aria-activedescendant`, `role="combobox"` работают как раньше (тесты на каждую клавишу)
- [ ] Кнопки темы (`button[data-theme]`) рисуются только при `scheme:'both'`; у остальных дизайнов `data-theme` не мешает: страница использует схему дизайна
- [ ] Каждый из шести дизайнов рендерит одни и те же секции и якоря на фикстурах (тест сравнивает набор `id="…"` секций между дизайнами)
- [ ] `tests/test_dashboard_views.py` экспортирует `DESIGN_IDS`, читая его из шаблона; харнесс принимает `design`; остальные `test_dashboard_*.py` зелёные; `tests/test_dashboard_designs.py` содержит тесты реестра, выбора, хранения и неизвестного значения
- [ ] `python -m unittest discover -s tests -p "test_dashboard_*.py"` зелёный
- [ ] Остатки таска 01 (замечания ревью): боковая рейка подсвечивает пункт текущей секции (`aria-current="page"` у ссылки секции, которая сейчас в зоне видимости; тест на правило и на атрибут при `scrollIntoView`/смене хэша без IntersectionObserver-заглушек хуже — допускается простой слушатель `scroll` с выбором ближайшей к верху секции); механизм `data-narrow` (JS-флаг 700 px) удалён вместе с мёртвым CSS `.ov3/.tl2`, если на них не ссылается тест вне зоны (`.nowh` оставить, пока его читает `test_followups_dashboard.py`); в `tests/test_dashboard_views.py` удалён дубль блока `PALETTE`/`SCOPE`/`DARK_*` с `data-view`

