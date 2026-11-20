# Интерфейсы и правила проекта

Полная проверка: `python tools/run-tests.py`

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| tests-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Правила проекта (из «Договорились»)
- R28 не трогать; всё из раздела «Чего в этом брифе нет» (шлюзы, подписи, guard, слепая приёмка, Opus/Fable, дифф и «план → факт» на странице) не трогать. ADR `0015` — за R33 (этот прогон его пишет), прочие новые — с `0030`.
- Opus выключен, Fable не допускается; `dropped` ставит только пользователь; `main` в `origin` — только по слову.
- Исполнитель не коммитит (коммитит оркестратор через `ticket NN land`). `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md`, `BRIEF-2026-11-orchestrator-spend.md` не коммитить.
- Тесты, копирующие `ap.py` в харнесс, копируют каждый импортируемый модуль.
- Каждый баг — регресс-тест; `CHANGELOG.md` («Unreleased») ведёт **только таск 03** (записи на все шесть пунктов: R01–R03 и R33–R35); таски 01 и 02 в нём ничего не правят.
- Страница дашборда: одна разметка, шесть дизайнов; без внешних запросов (кроме `POST` на свой `/.ap-act`); потолок шаблона 450 КБ.

## Границы, решённые в спецификации

**Контракт `POST /.ap-act` (серверу и странице одинаково)**
- URL `/.ap-act?t=<токен>`; заголовки `Content-Type: application/json`, `Origin: http://<Host>` обязательны; тело ≤ 8192 байт.
- Тело: `{"kind": "briefing|spec|plan|accept", "since": "<waiting.since из state>", "answer": "<текст>"}`; `answer` обязателен и не пуст (1..2000 знаков) только для `briefing`; для остальных вида — не нужен.
- Ответы: 200 `{"ok": true, "kind": …}`; 400 `{"ok": false, "error": "bad-request"}`; 403 (без разбора тела) — токен/Host/Origin/`Sec-Fetch-Site`/запрещённый `kind`; 405 — любой другой `POST`-путь; 409 `{"ok": false, "error": "no-wait|other-kind|stale"}`; 413 тело велико; 503 `{"ok": false, "error": "busy"}`.
- `ALLOWED_ACTIONS = ("briefing", "spec", "plan", "accept")` — модульная константа в `ap.py` (рядом с `WAIT_KINDS`), её же перечисляет тест.

**Состояние и файлы**
- `WAIT_KINDS` получает `accept` (стоит после `plan`); текст ожидания на странице — `L.waitH2.accept` (ru «Принять сдачу», en «Accept the delivery»).
- Ответ кладётся в `.autopilot/serve.answer.json`: `{"kind","since","answer","source":"dashboard","at"}`, атомарно; `ap.py ask` и `ap.py answered` его удаляют.
- Журнал: `log(state, "answered", kind=…, source="dashboard")` (для CLI `source` не пишется); в `state.js` текст ответа не попадает.
- Команда `ap.py await [--timeout N]`: ждёт, пока ожидание закроется; код 0 — закрыто (печатает одну строку JSON `{"answered": true, "kind", "source": "dashboard|chat", "answer": "…"}`; `answer` есть только из дашборда), код 3 — срок вышел (`нет ответа`), код 4 — ожидания нет; `--timeout` по умолчанию 300, максимум 3500; обрабатывается вне `state.lock`.

**Страница**
- Кнопки появляются, только если `SERVED` и в `location.search` есть токен и `S.waiting.kind` в списке `ALLOWED_ACTIONS` (список дублируется в шаблоне константой `ACT_KINDS`); иначе — одна строка про `ap.py url` (без токена) или ничего (нет ожидания).
- Нажатие: первый клик меняет подпись («Точно? нажми ещё раз»), второй шлёт `fetch('/.ap-act'+location.search, {method:'POST', …})`; ответ не 200 — кнопка возвращается, показывается причина.
- Команды со словами пользователя (`ticket NN reset --by-user "<цитата>"`, `finish --by-user "<цитата>"`, `opus approve --by-user "<цитата>"`, пометка `dropped` в `manifest.md`) выводятся блоком с кнопкой «скопировать».

## Что построили тикеты
—
