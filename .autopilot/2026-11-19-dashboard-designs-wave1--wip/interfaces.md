# Границы и правила проекта

## Правила проекта («Договорились», дословно из carried.md)
- Opus — только по подтверждению пользователя; Fable не допускается ни под каким написанием.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя; `dropped` ставит только пользователь.
- Адрес с токеном печатает только `ap.py url`; в чат не вставлять.
- `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md`, `BRIEF-2026-11-orchestrator-spend.md` в корне не коммитить.
- Принятое ограничение `bash_gate` — не чинить.
- Нет внешних запросов, шрифтов и CDN в шаблоне дашборда; только стандартная библиотека Python в инструментах.
- В тексте реестра/страницы шаблона не появляется слово `STATE` вне блока `/*STATE-BEGIN*/…/*STATE-END*/` и функций чтения (держит тест).
- Якорь `/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/` встречается в шаблоне ровно один раз; строки `cockpit-rail`, `cockpit-content`, `planned-model-routes`, `sequential-host-notice`, `no child agent is created` остаются (читают `dashboard_upgrade.py` и тесты).
- Строка «Классика держит старые цвета, Сейчас по умолчанию» заменена брифом 2026-11-19 (девять раскладок уходят, по умолчанию дизайн `aurora`); пользователю сказано.

## Команды-генераторы
| Имя | Команда | Файлы |
|---|---|---|
| — | генераторов в этой сборке нет | — |

Полная проверка: `python tools/run-tests.py`

## Границы, решённые в спецификации

Единственный изменяемый файл кода дашборда — `skills/autopilot/phases/dashboard-template.html` (T). Внутри T границы такие.

**Реестр дизайнов (владеет: список дизайнов и их выбор).** Раскрывает:
- `DESIGNS` — массив `{id, no, name:{ru,en}, tagline:{ru,en}, accent:'#rrggbb', scheme:'dark'|'light'|'both', tags:[...]}`; порядок: aurora 01, editorial 02, brutal 03, terminal 04, blueprint 05, bento 06.
- `DESIGN_IDS` — `DESIGNS.map(d=>d.id)`; `DESIGN_KEY='autopilot-design'`; `DEFAULT_DESIGN='aurora'`.
- `storedDesign()` → id (никогда не бросает; неизвестное → `aurora`); `applyDesign(id)` ставит `document.documentElement.dataset.design`; `selectDesign(id)` сохраняет, применяет, `render(CUR.lang)`.
- `comboList(q)` ищет по `id`, `no` (в т. ч. «05» и «5»), `name.ru/en`, `tags`; пустой запрос — все шесть в порядке реестра. `comboKey`, `comboOpen`, `comboSync` — прежняя клавиатурная схема.
- Скрывает: способ хранения и разбор `localStorage`.

**Страница (владеет: порядок секций).** `page(c)` — единственная функция раскладки; возвращает `askPin + hero + sections`. Секции — `<details class="sec" id="mission|tasks|models|quality|…">`, у каждой `summary` ≥44 px. Якоря рейки `#mission #tasks #models #quality` рисуются все (на странице есть всё). Бывшие раскладки и `UI.tab` не существуют.

**Слоты особых элементов.** `dxTicker(c)`, `dxAscii(c)`, `dxDim(c)`, `dxStamp(c)`, `ringHTML(...)` — чистые функции от данных состояния, возвращают `''`, если данных нет. Классы: `.dx-ticker`, `.dx-ascii`, `.dx-dim`, `.dx-stamp`. Общий CSS скрывает слоты (`display:none`), каждый дизайн показывает свои.

**CSS-дизайны.** Токены — только внутри `html[data-design="<id>"]` (светлая и тёмная половины для `scheme:'both'`); общие правила структуры не называют дизайнов. Общие токены: `--bg --card --inset --soft --line --line2 --tx --tx2 --mut --quiet --hero --done* --now* --rev* --fix* --bad* --idle --accent --on-done --on-rev --on-bad --on-fix --warn-*`; новый дизайн обязан задать все.

**Тесты (швы).** `tests/test_dashboard_views.py` экспортирует `HARNESS`, `NODE`, `TEMPLATE`, `DESIGN_IDS` (читается из шаблона), `_fixtures`, `GX_CASES`; харнесс принимает `design` вместо `VIEW`. `tests/test_dashboard_designs.py` — реестр, выбор, хранение, контраст, ограничения (внешние ссылки, размер ≤450 КБ, `prefers-reduced-motion`, `@media print`, ≥44 px).

Что готовые таски добавили — ниже, по мере сдачи.

## Что построили сданные таски
(пока ничего)
