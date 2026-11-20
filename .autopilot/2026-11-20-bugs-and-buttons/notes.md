# Заметки по коду (разведка + прошлая сборка)

## Баги (R01–R03) — см. прошлый прогон `2026-11-20-close-weak-spots/notes.md` и `review-report.md`
- `scheduler.py` (`skills/autopilot/tools/`): `ACTIVE` держит `review`, `overlapping-zone` блокирует зависимого с пересекающейся зоной (строки ~13, ~103-109); зависимость в `review` пускается при `isolated=False` (стр. ~93).
- `ap.py` `commit_paths` (~2898-2921): `git diff --cached --name-status -M -z`, старый путь `R` добавляется, если новый путь покрыт `covers(paths, new)` и старый не покрыт; тесты — `tests/test_review_race_bugs.py` `CommitPathsRename`.
- `gate_sign.py`: `ensure_key` (~190-240), `_claim_empty`, `_retry_busy`; тесты — `tests/test_gate_sign.py` `KeyRaceTests`, `busy_claim(failures)`.

## Сервер дашборда (`skills/autopilot/tools/ap.py`)
- `make_server(directory, port, token)` 1025-1114; класс `Handler(SimpleHTTPRequestHandler)`: `allowed()` (1033: Host `127.0.0.1:<порт>`/`localhost:<порт>`; `Sec-Fetch-Site: cross-site` → отказ; Origin, если есть, = `http://<Host>`; пути `OPEN_PAGES`, `PING_PATH`, `STATIC_NAME` без токена; остальное — `?t=` через `hmac.compare_digest`; любой отказ `send_error(403)`), `tokenless_page` (1051), `do_GET` (1076), `do_HEAD`, `list_directory` (403), `log_message` (вырезает query), `end_headers` (`Referrer-Policy`, `Cache-Control: no-store`). `do_POST` нет, 405 нигде не выставляется, лимита тела нет.
- Сервер — тот же `ap.py --serve <порт>` (`run_server`), идёт без `state.lock` (4996-5009). `locked_state(timeout=10)` (196), `read_state()` 231, `save(state)` 242, `write_snapshot`.
- `serve_token()`, `serve.token`, `serve.log`, `serve.pid` — всё под `serve.*` в `.gitignore`.

## Ожидания
- `WAIT_KINDS = ("briefing","spec","plan","action","stop")` (133), `MOVES_ON` (136). `cmd_ask` (3787): `state["waiting"] = {"kind","since","note"}`, `log(state,"ask",kind=,note=)`. `answered` (4793) → `close_wait(state)` (333: `state["waits"]` += `{kind,from,to}`, `waiting=None`, `log(state,"answered",kind=)`). `log(state, k, **kw)` (263) пишет `{"t","k",…}`, хранит `LOG_KEPT=300`; поля `source` у `log` нет. `mirror_run_log` (277): `ask` → `wait act=start`, `answered` → `wait act=end`.
- Виды: `briefing` — раунд вопросов (`phases/2-briefing.md:23`), `spec` — ручной гейт (`3-spec.md:135`), `plan` — принять план (`4-plan.md:146`), `action` — да/нет перед необратимым (`0-modes.md:23`), `stop` — стоп (утёкший секрет и т.п.). Вида «принять сдачу» нет.
- CLI: `parse_args` (1305), `main` (4599): команды без state — `claude-version`, `git-check`, `agents`, `init`; печатающие без `save` — `url` (4672), `silence` (4693) и т.п.; `ask` — 4791, `answered` — 4793; под `with locked_state(): main()` (5008).

## Страница (`skills/autopilot/phases/dashboard-template.html`)
- `render(lang)` (2166): `waiting = S.waiting` (2173); плашка `askBar` (2899-2902), заголовок героя `L.waitH2[kind]` (1413 ru / 1568 en; ключи briefing, spec, plan, action, stop), событие ленты «Ждём тебя» (1485). Карточка `sNeed` («Нужно от вас», 1532/1682; `c.needCard`, `c.hasNeed`) — ключи, заглушки, допущения, не `waiting`.
- Шесть дизайнов: `DESIGNS` (1332), `DEFAULT_DESIGN='aurora'`, `applyDesign`; разметка одна, дизайн — `data-design` на `<html>`; `waiting` рисуется одной функцией для всех.
- `SERVED = /^https?:$/.test(location.protocol)` (2002), `stateUrl()` (2014: токен из `location.search`), `pullState` (2020, `<script>`); fetch/XHR/POST на странице нет. Потолок шаблона `TEMPLATE_CEILING = 450*1024` в `tests/test_dashboard_designs.py:378`.

## Тесты
- Сервер: `tests/test_ap_audit.py` (`make_server(self.dir, 0, TOKEN)` в потоке, `get(path, host=, method=, **headers)` на `http.client`), `tests/test_followups_token.py`. Шаблон: `tests/test_dashboard_designs.py` (`DesignRuns` через `NODE`/`HARNESS` из `tests/test_dashboard_views.py`, `DESIGN_IDS`), `test_dashboard_*.py`. Харнесс ap.py: `tests/test_ap.py` `Run.setUp` (57-79) копирует модули.
- ADR: свободен `0015` (пропуск между 0014 и 0016; закреплён за R33), следующий свободный 0030. `tests/test_text_split.py` держит размер обычного пути фаз.
