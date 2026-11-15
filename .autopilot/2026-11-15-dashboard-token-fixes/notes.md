# Заметки разведки (код как есть, 2026-11-15)

AP = skills/autopilot/tools/ap.py · TPL = skills/autopilot/phases/dashboard-template.html

## Сервер и печать адреса
- `make_server(directory, port, token)` AP:933; `allowed()` AP:941-957 (Host, `Sec-Fetch-Site`, Origin, токен `hmac.compare_digest`); `OPEN_PAGES=("/","/dashboard.html","/index.html")` AP:912 — без токена; `STATIC_NAME` AP:913.
- Сервер статический: снимок `window.STATE` пишет `write_snapshot(state)` AP:770-790 прямо в `.autopilot/dashboard.html` между `/*STATE-BEGIN*/`…`/*STATE-END*/`; по HTTP страница уходит вместе со снимком.
- `serve_token()` AP:916 (`secrets.token_urlsafe(24)`, `os.open(O_WRONLY|O_CREAT|O_TRUNC, 0o600)`); `page_url(port)` AP:986 -> `http://localhost:P/dashboard.html?t=TOKEN`.
- Строка после каждой команды: `main()` AP:3445-3454 `print("%s · %s · требований %s, готово %s" % (snap, srv, …))`; `serve(state)` AP:990-1021 возвращает `page_url(port)` / `"сервер поднят: " + page_url(port)`; запасные ветки печатают путь файла.
- Клиент: `stateUrl()` TPL:1673 читает `t` из `location.search`; `SERVED` TPL:1661.
- Тесты: tests/test_ap_audit.py `Server`, `Snapshot`; tests/test_dashboard_now.py `test_state_js_is_asked_with_the_token_from_the_page_address`; tests/test_dashboard_views.py:128. Подпроцессы тестов ходят с `--no-serve`; печатаемую строку ни один тест не проверяет.

## gate_sign.py
- `ensure_key()` :89-112: `path.unlink(missing_ok=True)` -> `os.open(O_EXCL)` -> `write`. Окно: файл есть и пуст до `write`; параллельный `ensure_key` видит `st_size==0` и удаляет чужой ключ; `load_key()` в этом окне читает пусто. `_write_key_file` :66 (temp + `replace_with_retry`) уже есть, `_protected` :79, `_dpapi` :42, `load_key` :115.
- Тесты: tests/test_gate_sign.py `GateSignTests`, `DpapiKeyTests` (в т. ч. `test_empty_key_file_counts_as_missing_and_is_recreated`).

## Манифест и finish
- Фразы «снимает только пользователь»: phases/1-manifest.md:56,77,81; phases/0-memory.md; AGENTS.md:18; старый spec 2026-11-08-upstream-port-opus R24: «`--by-user` фиксирует слова пользователя, но не снимает строки манифеста».
- Код: `landing_problems` AP:2946-2983 (открытые строки `open|in-spec|in-ticket` -> refuse); `cmd_finish` AP:2986-3060: с `--by-user` отказы пропускаются, строки НЕ переписываются, `state["landedWith"]` и «сдан с оговорками» пишутся. Цитата не проверяется (`clean_quote` AP:160).
- Вывод: код и R24 не расходятся; расходятся формулировки («снимаются `finish --by-user`»). Правится текст и добавляется тест «строки остались как были».

## model_router.py
- `RISK_RE` :216, `WORD_RISK_RE` :224, `SENSITIVE_ZONE_RE` :229, `CLASS_RE` :232, `docs_only` :235, `assess_ticket(text)` :241-277 (риск и «hard/vague» считаются regex по телу таска), `assess_scores` :196-212, `choose_route` :295, `CODE_MIN_SCORE=10`, `MECHANICAL` :193.
- `**Причина класса:**` нигде не разбирается. Вызовы: AP:1766, 1998-2045 (`cmd_plan_models`), 2439-2440 (`ticket NN route`), agent_profiles.py:126-134 (копия regex Объёма :41).
- Тесты: tests/test_audit_routing.py (`RiskByZoneTests`, `TicketClassTests`, `CheapProfilesTests`), tests/test_model_router.py (`RiskWordTests`, `RouterTests`, `PremiumRouteTests`), tests/test_audit_docs.py:30,48-49, tests/test_agent_profiles.py, tests/test_ap.py (`plan-models`, `route`, `check-plan`).
- Доки: phases/4-plan.md:55,74,91-92; docs/autopilot/model-routing.md:72; docs/adr/0002, 0003.

## Шаблон дашборда
- `VIEW_IDS` TPL:1089, `VIEW_HOME` TPL:1092, `VIEWS` TPL:1758-1801; «Сейчас» `VIEWS.now` TPL:1763-1780 (вкладки now/req/sum/det, `c.nowTabs` TPL:2760).
- Герой: `ovHero` TPL:2464 (`.card.ovh`, `ringHTML`, `.ovh-main` h2 + lead, `.ovh-side` `.kvs`), при сдаче `sumHero` TPL:2511 (`.kcards`); CSS `.ring`, `.ring.sm` TPL:665-672.
- Доска требований: `reqBoard` TPL:2720, `reqBoardBody` TPL:2714 (5 колонок `data-rcol=read|plan|doing|check|ok`, `BD.rcols` TPL:1233; полосы `ph|def|drop`), `reqCard` TPL:2711, `reqCol`, `reqPlaced`, `reqIn`. Все карточки рендерятся без ограничения. Готовый приём свёртки: `rowsList(key, arr, n)` ≈TPL:2065 (`data-more`, `L.more(n)`, `L.collapse`, `L.showAll(n)` TPL:1176). CSS `.bd-cols.r5` TPL:963-972, `.rcard` TPL:995-997, узкие TPL:1007-1008.
- Тесты: tests/test_dashboard_boards.py, test_dashboard_now.py, test_dashboard_views.py (`test_overview_has_ring_forecast_route_and_gantt`), test_dashboard_details.py, test_dashboard_upgrade.py.

## Обновление копии страницы
- `ap.py` шаблон не копирует: `finish`, `reopen`, `init` страницу не трогают; `upgrade_tools` AP:1255-1297 (зовётся из `init` и `stage` через `upgrade_note` AP:1300) копирует только `*.py`. HTML обновляет только `dashboard_upgrade.py` (`upgrade(project, template, backup_dir, dry_run)`): проверяет slug, `ANCHOR`, `cockpit-rail`, не идёт по symlink, делает копию в tmp (5 последних).
- Тесты: tests/test_dashboard_upgrade.py `DashboardUpgradeTest`, tests/test_ap.py (около :3416-3431 `upgrade-tools`).
