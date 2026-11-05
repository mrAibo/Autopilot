# Заметки по коду (разведка шаблона дашборда)

Единственный источник: `skills/autopilot/phases/dashboard-template.html` (1729 строк). `.autopilot/dashboard.html` — его копия; `skillDir` этого репозитория = сам репозиторий.

## Шаблон
- CSS: один `<style>` 7–565, слоями: базовый → «Dashboard 3.0» (332–439) → «3.1 command-center» (440–565, перекрывает). Тёмные переменные: `@media (prefers-color-scheme:dark){:root:not([data-theme])}` и `:root[data-theme="dark"]`.
- JS 585–1728. `STAGE_IDS` 587, `POLL_MS` 588, `IC`/`ic()` иконки 593/613, тема 615–628 (`storedTheme`, `applyTheme`, ключ `autopilot-theme`), `I18N = {ru, en}` 639–839 (ключи `themeLabel`, `langLabel`, `gates`, `stages`, `wave`… — обе локали обязаны иметь одинаковые ключи), `CUR` 842, `UI = {filter:'all', open:{}}` 856.
- Время: `MARKS`, `WAITS`, `activeMs` 917, `timerHTML` 949, `tick` 968 (раз в секунду обновляет только таймеры).
- `render(lang)` 1098 строит блоки-строки и в конце одним `app.innerHTML` (1593) собирает страницу: `rail` (1573), шапка `.top` с кнопками `data-theme` и `data-lang` (1597–1609), заголовок, `#mission.spotlight` (`hero` + `opsBlock`), плитки (`tileReq tileTk tileTests tile4`), `#tasks.pipeline` (`buildCard`, скрыт при `fin`), `#models.intelligence` (`resourceBlock` + `isolationBlock`), `#quality.cols` (`leftCol`/`rightCol` — массивы карточек), футер.
- Готовые блоки: `segs` (трек этапов 1211), `buildCard` (волны/таски 1273), `wordsCard` (требования с фильтрами 1340), `gatesCard` (1373), `feedCard` (лента 1399), `needCard asmCard reportCard concernsCard addCard blindCard`, `resourceBlock`/`proposalItems` (маршруты моделей, токены 1435–1491), `isolationBlock` (1539), `activeWorkers`/`nextTitle`/`okGates` (1404–1420).
- Клик-делегирование на `#app` (1662–1680): `data-lang` → запись в localStorage + `render`; `data-theme` → запись + `applyTheme` без перерисовки; `data-filter`, `data-more`, `data-refresh`.
- Фокус при перерисовке: `focusAttrs = ['data-focus-key','data-lang','data-theme','data-filter','data-more','data-refresh']` (1566) — новый атрибут переключателя вида надо добавить сюда. `focusId` — для `mission tasks models quality`.
- Другие ключи localStorage: `autopilot-lang`, `autopilot-beats:<slug>:<startedAt>`.
- Перерисовка при опросе: `applyState` → `render(CUR.lang)` только если изменился `stampOf(S)`; при `finishedAt` опрос останавливается.

## Состояние (`window.STATE`)
Верхний уровень: title, result, mode, depth, tier, dir, slug, skillVersion, rev, updatedAt, startedAt, finishedAt, waiting, waits, beats, stages[], tickets[], requirements{total,dropped,done,inTicket,inSpec,placeholder,deferred}, reqList[{id,text,why,status}], debt{emptyEnv,placeholders,assumptions}, report, concerns, additions, blind, gates{G1..G4}, coverage, tests{passed,failed}, log[], usageEvents[], budgetTokens, sequentialHost.
Таск: id, title, status (pending|in-progress|review|repair|done|failed), wave, blockedBy, startedAt, finishedAt, review, repairFindings, repairs, retries, concerns, tests, routing{model,provider,effort,score,reason,agentType}, plannedRouting{…}, worktree{status}, retryAdvice.

## `dashboard_upgrade.py`
`parse_project_state` (27–36) требует `data.startswith("window.STATE")` и режет по `=`; читает `state_path.read_text(encoding="utf-8")` (58) → BOM даёт «unexpected format». Ошибки — `UpgradeError(ValueError)`. Замена: `state_io.parse_state_text(text)` / `read_state_file(path)` (утф-8-sig, терпит отсутствие префикса и `;`, бросает `StateError`). Проверки шаблона: `"cockpit-rail"` в шаблоне (66–67), `"cockpit-content"` в результате (70). Снимок в странице: regex `SNAPSHOT` (24), `/*STATE-BEGIN*/window.STATE=…/*STATE-END*/`.

## Тесты, которые можно сломать
- `tests/test_brand_assets.py`: в шаблоне нет `const LOGO =` и `class="logo"`; `<div class="brand"` ровно 2; есть `class="cockpit-rail"`, `class="cockpit-content"`, `class="spotlight"`, `href="#models"`, строка `.cockpit-rail{display:none}`; нет `2.3 DEV`; есть `class="brand-version" id="brand-version"` и `bv.textContent = typeof v === 'string'`. Логотипы проекта: `assets/autopilot-logo-light.svg|dark.svg` (знак одинаковый, различаются цвета надписи).
- `tests/test_dashboard_upgrade.py` (6 тестов: апгрейд сохраняет прогон, права, 5 бэкапов, dry-run, чужой slug/плохой JSON, битый маркер снимка).
- `tests/test_ap.py:226` — `window.STATE={` в странице; остальное проверяет форму STATE, не разметку.
- Команды: `python -m unittest discover -s tests -p test_dashboard_upgrade.py`, `… -p test_brand_assets.py`, полный `python -m unittest discover -s tests` (~5 мин). Node 24 есть на машине, но тесты репозитория — только стандартная библиотека Python.
