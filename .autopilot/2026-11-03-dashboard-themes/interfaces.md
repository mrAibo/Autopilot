# Интерфейсы и правила проекта

## Правила проекта (из «Договорились» прошлой сборки, дословно)
- Ключ подписи гейтов хранится вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/` — R05, R17
- Opus и Fable не допускаются в субагенты ни под каким написанием — R06, R18

Правила репозитория (AGENTS.md): только стандартная библиотека Python; `state.js` читается и пишется только через `skills/autopilot/tools/state_io.py`; полный прогон тестов ~5 минут, один файл — `python -m unittest discover -s tests -p test_x.py`; `py -3`, не `py -3.13`.

## Границы, решённые в спецификации

### Единица A — `skills/autopilot/phases/dashboard-template.html` (владеет всем дашбордом)
Экспортирует (имена в английском, внутри одного `<script>`):
- `const VIEW_KEY = 'autopilot-view'` — ключ `localStorage`.
- `const VIEW_IDS = ['overview','timeline','requirements','resources','summary','classic']` — порядок кнопок; первый — по умолчанию.
- `function storedView()` → id из `VIEW_IDS`, любое другое значение или ошибка хранилища → `'overview'`. Все обращения к `localStorage` в `try/catch`.
- `let VIEW = storedView()` — текущая тема.
- `const VIEWS = { <id>: (ctx) => '<html строка основного содержимого>' }` — по одной функции на тему; `ctx` — объект уже посчитанных в `render()` блоков (`hero`, `opsBlock`, `kpiRow`, `tiles`, `segs`, `buildCard`, `wordsCard`, `gatesCard`, `feedCard`, `resourceBlock`, `isolationBlock`, `leftCol`, `rightCol`, `activeWorkers`, `L`, `S`, `fin`, …). Функция не читает `STATE` сама и не пишет в DOM.
- `I18N.<lang>.views = {overview:'…', …}` и `I18N.<lang>.viewLabel` — названия тем и подпись группы кнопок, ключи одинаковы в `ru` и `en`.
- Кнопки: `<button type="button" data-view="<id>" aria-pressed="…">`; обработчик клика на `#app` ставит `VIEW`, пишет `localStorage` (в `try/catch`) и вызывает `render(CUR.lang)`. `'data-view'` добавлен в `focusAttrs`.
- Лого: символ `<symbol id="ap-mark">` в разметке страницы, класс `brandmark`; слово — `<span class="wordmark"><span>auto</span><b>pilot</b></span>`. Используется в `.top .brand` (оба заголовка, включая `bootFail`) и в `.rail-brand`. Не использовать `class="logo"` и `const LOGO =`.
- Сохраняются строки, которые проверяет `tests/test_brand_assets.py` (см. `notes.md`).

Скрывает: порядок и состав блоков внутри каждой темы; CSS-слои 3.0/3.1.

### Единица B — `skills/autopilot/tools/dashboard_upgrade.py`
- `read_project_state(path) -> dict` (D01: вместо `parse_project_state(data: str)`, см. манифест) — читает файл через `state_io.read_state_file`; `StateError` переводится в `UpgradeError("…not valid JSON…")` (текст сохраняет существующий тест). Тот же вход, что и раньше, плюс BOM и отсутствие префикса.
- Не меняет сигнатуру `upgrade(...)` и статусы `upgraded|unchanged|would-upgrade`.

### Швы для тестов
1. `tests/test_dashboard_upgrade.py` — состояние с BOM и без префикса через `parse_project_state`/`upgrade`.
2. `tests/test_dashboard_views.py` (новый) — строки шаблона + (при наличии `node`) исполнение извлечённого JS на фикстурах STATE: пустая, в работе, завершённая; во всех шести темах `VIEWS[id](ctx)` возвращает непустую строку и без исключений.
3. `tests/test_brand_assets.py` — существующий; расширяется проверкой `ap-mark` и отсутствия запрещённых строк.

## Что построили закрытые таски
(пусто — заполняется по мере сдачи)

### T01 — темы дашборда и логотип (сдан)
`VIEW_KEY='autopilot-view'`; `VIEW_IDS` (6 id); `storedView()`; `let VIEW`; `const VIEWS={id: c=>html}`; `I18N.{ru,en}.{viewLabel,views,vw}`; кнопки `data-view` с `aria-pressed`; `BRAND_SVG`/`BRAND_WORD`/`BRAND_MARK`; `<symbol id="ap-mark">`. Ссылки рейки `#tasks/#models/#quality` работают там, где в теме есть нужный блок. Тесты: `tests/test_dashboard_views.py` (11, часть через `node`).
