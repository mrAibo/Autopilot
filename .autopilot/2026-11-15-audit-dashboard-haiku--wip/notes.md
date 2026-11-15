# Заметки по коду (разведка перед спецификацией)

Составлено оркестратором по отчёту аудита и точечному чтению: в строгой сборке профили субагентов появляются только после плана и нового чата, так что разведчика в этой сессии нет. Всё ниже — отправные точки для исполнителей; точные строки сверять по коду.

## Где что лежит
- `skills/autopilot/tools/` — инструменты; в проекте их копии лежат в `.autopilot/*.py` (копирует `init`/`stage`/`upgrade-tools`). Править только `skills/autopilot/tools/`.
- `ap.py` (3193 строки): `run_dir(state)` (:310) путь прогона; `glob.glob(os.path.join(run_dir(state), …))` на строках 402, 555, 700, 1615, 1848, 2024, 2222, 2243; `serve(state)` (:850) сервер дашборда; `cmd_stage` (:1270) этапы и их `startedAt/finishedAt`; снимок дашборда пишется около :734 голым `os.replace`; запись гейтов/ленты около :270–278 и :3091.
- `model_router.py`: `RISK_RE` (:200), `assess_ticket(text)` (:208) — риск по словам текста; `assess_scores`, `choose_route(provider, scores, policy, capabilities, premium)`; `DEFAULT_POLICY` — профили `cheap|balanced|strong|critical|premium`; cheap сейчас `haiku/low` для всех ролей.
- `run_log.py`: `KINDS` (:19) — схема строк журнала; у `executor`: `agent_type, role, turns, input, output, cache_read, cache_write` (нет model/effort); `role_of`, `append` (никогда не бросает).
- `claude_attest.py`: `log_usage(line, root)` пишет строку расхода из SubagentStop; аттестация содержит `resolvedModel`.
- `gate_sign.py` (:98): запись «прогон начат подписанным» — не атомарная; ключ `~/.autopilot/gate.key`, `$AUTOPILOT_HOME`.
- `state_io.py`: `replace_with_retry` — повтор `os.replace` на Windows; единственная точка чтения/записи `state.js`.
- `claude_agent_guard.py`: PreToolUse-хук субагентов, `bash_gate`; профили, подписи Opus.
- `retry_policy.py` и `docs/autopilot/retry-policy.md` — «не повышать модель из-за упавшей команды».
- `phases/dashboard-template.html` (2614 строк): `VIEW_IDS` (:1022), `VIEW_HOME` (:1025), реестр `VIEWS` (:1569) — функции `ctx => html`; `render()` собирает блоки и рейку (:2415–2470); ленты гейтов (:1137, :1265, :1912); минуты этапов (:1683, :2214); «обновлено N назад» (:2460); счётчик повторов в Классике (:1820); полоса этапов `role="list"` (:1764, :2120); заголовок вкладки при вопросе (:2502). Копия шаблона в живом проекте — `.autopilot/dashboard.html`, обновлять `dashboard_upgrade.py`.
- `phases/4-plan.md:55` — правило «пометку планировщика считать только описанием»; `ap.py plan-models` считает маршруты.
- `tests/` — unittest, 750 тестов, ~7 минут; один файл — `python -m unittest discover -s tests -p test_x.py`. Харнессы, копирующие `ap.py`, копируют также `state_io.py`, `process_containment.py`, `run_log.py`, `claude_attest.py`.
- `AGENTS.md`, три README (рус/англ/нем.) — число тестов («730»).

## Формы данных
- `state.js`: `window.STATE = {...}`; `stages[]` с `id,status,startedAt,finishedAt,note`; `tickets[]`; `blind`, `coverage`, `gates`, лента событий; маршруты; `debt`.
- Прошлые прогоны: каждая папка `.autopilot/<дата>-<slug>/` содержит свой архивный `state.js`.
- `run-log.jsonl` — одна строка на событие; `report-run` свод.
