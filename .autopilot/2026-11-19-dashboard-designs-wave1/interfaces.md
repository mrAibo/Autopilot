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

### Таск 01 (страница)
- `const page = c => html` — единственная раскладка; секции `<details class="sec" id="mission|reqs|tasks|quality|models|gates|feed">`; `UI.sec` (id→bool открыта), слушатель `toggle`; строки `I18N.<lang>.sec`.
- Тест-модуль `tests/test_dashboard_views.py`: временно `DESIGN_IDS=['aurora']`, `SECTIONS`; харнесс без `VIEW`.
- Палитровые селекторы теперь `:root[lang]:not([hidden])` (прежняя специфичность без `data-view`).
- Осталось мёртвым в CSS: `.nowh`, `.ov3`, `.tl2`, `.hero:before`-варианты раскладок — таск 02 чистит то, что не нужно странице; рейка без подсветки текущего пункта.

### Таск 02 (реестр)
- `DESIGNS`, `DESIGN_IDS`, `DESIGN_KEY`, `DEFAULT_DESIGN`, `designOf(id)`, `storedDesign()`, `applyDesign(id)`, `selectDesign(id)`, `comboList(q)`, `comboOpen(b)`, `comboKey(e)`, `comboSync()`, `railPick(tops,edge)`, `railSync()`; `UI.combo={open,q,i}`; разметка `data-dcombo`, `data-dcombo-input`, `data-dcombo-toggle`, `data-dopt`, `#dopt-<id>`.
- Незавершённые дизайны (editorial, brutal, terminal, blueprint, bento) берут токены «Авроры» через `html:is([data-design=…])` в четырёх блоках токенов; таски 03 и 04 убирают свой id из этого списка, когда пишут палитру.
- Дизайны с одной схемой ставят `data-theme` = своя схема; акцент дизайна — правило `html[data-design=X][lang]:not([hidden]):not([data-theme="none"])`.
- `data-narrow` и CSS `.ov3/.tl2/.nowh` остаются: их читают `test_dashboard_now.py:58` и `test_dashboard_boards.py:288` (вне зоны таска 02).

### Таск 03 (светлые дизайны, слоты)
- `dxStamp(c)`, `dxDim(c)`, `dxRing(c)` с `c={S,L}` — чистые функции, '' без данных; классы `.dx-stamp`, `.dx-dim`, `.dx-ring`, скрыты общим `.dx-stamp,.dx-dim,.dx-ring{display:none}`; Отчёт показывает штамп, Чертёж размерные линии, Аврора и Бенто кольцо.
- Блоки токенов `html[data-design="editorial|blueprint|bento"][data-theme="light"][lang]:not([hidden])`; id этих трёх убраны из списка `html:is([data-design=…])`. Остались на токенах «Авроры»: brutal, terminal.
- Старое кольцо требований `ringHTML('')` (класс `ring`) не тронуто (его требует `test_dashboard_views.py`, в том числе на фикстуре `empty`); в трёх новых дизайнах оно скрыто CSS.

### Таск 04 (тёмные дизайны, печать, пределы)
- `dxTicker({S,L})`, `dxAscii({S,L})` — '' без данных; классы `.dx-ticker`, `.dx-ticker-track`, `.dx-ascii`, `.dx-row`; скрыты общим правилом `.dx-ticker,.dx-ascii{display:none}`, показаны Пульту и Терминалу.
- `tools/check-dashboard-browser.py --designs [DIR]` снимает шесть дизайнов на 1440 и 400 px; `TEMPLATE_CEILING = 450*1024` в `tests/test_dashboard_designs.py`.
- Снимки (12 файлов, ~4,1 МБ) лежат в `.autopilot/2026-11-19-dashboard-designs-wave1--wip/shots/`, а не в `docs/` (больше 3 МБ).
- `@media print` стоит перед CSS досок (тест `test_dashboard_boards` запрещает hex-цвета после правила 520 px); тест 520 px сравнивает только правила по ширине.
- Все шесть дизайнов теперь имеют свои палитры (список `html:is([data-design=…])` пуст или удалён).
