<!-- autopilot:start -->
# Autopilot

Навык (skill) для Claude Code, Codex и Cursor: из надиктованной идеи собирает готовый проект.

## Команды

| Команда | Что делает |
|---------|------------|
| `—` | Установка не нужна: только стандартная библиотека Python |
| `python3 skills/autopilot/tools/ap.py` | Поднять дашборд, адрес без токена (в проектах — `.autopilot/ap.py`); адрес с токеном — `ap.py url` |
| `python3 skills/autopilot/tools/ap.py bootstrap --project .` | Из папки навыка поставить инструменты в `.autopilot/` проекта (до `init`, без `state.lock`) |
| `python3 .autopilot/ap.py doctor` | Предполётная проверка проекта: строка на проверку, код 2 — отказ `git-check` или версия ниже минимума |
| `python3 -m unittest discover -s tests` | Все тесты последовательно |
| `python tools/run-tests.py` | Все тесты параллельно, итог в формате unittest; CI запускает его на Python 3.11 и 3.13, Ubuntu и Windows |
| `python3 -m compileall -q skills/autopilot/tools tests` | Проверка синтаксиса |

## Как здесь работает Autopilot

Сборка ведётся навыком `/autopilot`. Требования, спецификация и таски — в `.autopilot/`.
Прогресс — `.autopilot/dashboard.html`. Требование из `manifest.md` может снять
(`dropped`) только пользователь; `finish --by-user` сдаёт сборку «с оговорками», строки остаются в своём статусе. Прерванную сборку продолжает «продолжи автопилот».

## Подводные камни

- Полный прогон тестов идёт около 10 минут (<!-- tests:count -->1258<!-- /tests:count --> тестов, 5 пропущены; число подставляет `skills/autopilot/tools/test_count.py --write`); один файл: `python -m unittest discover -s tests -p test_x.py`.
- `ticket MM start` пускает таск, чья зависимость в `review` (код закоммичен); `done` и `land` ждут `done` зависимости. `commit_paths` подхватывает старый путь переименования из индекса; ключ `gate.key` при пустом файле занимается жёсткой ссылкой `gate.key.claim` (брошенную заявку удалить руками, `docs/adr/0029`).
- Параллельный прогон: `python tools/run-tests.py [-j N] [--list]` (итог в формате unittest; классы с `serial = True` или из `SERIAL` в запускателе идут после параллельных); CI запускает именно его. Замер 2026-11-17, Windows, 32 процесса: последовательно 632 с, параллельно 77–90 с (1047 тестов, 5 пропущено, числа те же).
- `state.js` читается и пишется только через `skills/autopilot/tools/state_io.py` (BOM, префикс, повтор `os.replace` на Windows).
- Сервер дашборда (`ap.py`) отдаёт данные только с `?t=<токен>` из `.autopilot/serve.token` (страница без токена приходит с `window.STATE=null`); адрес с токеном печатает только `ap.py url` (голый `ap.py` и остальные команды печатают адрес без `?t=`); адрес с токеном не вставлять в чат и скриншоты; 403 на чужой Host/Origin и `Sec-Fetch-Site: cross-site`; `file://` токена не требует (`docs/adr/0001`).
- Ответ `/.ap-ping` (hmac от `serve.token` и порта) подтверждает свой сервер без PowerShell; не сошёлся — сервер перезапускается, нет ответа — прежняя проверка процесса (`docs/adr/0013`).
- `.autopilot/history-cache.json` — кэш сводки по архивам прогонов, ключ `(папка, mtime_ns, size)`; `tokens` в него не входит, битый файл молча пересчитывается (`docs/adr/0014`).
- `finish` переносит `.autopilot/attestations.jsonl` в папку прогона и удаляет профили прогона `autopilot-<роль>-<slug>`; то же и для старых — `ap.py agents prune [--apply]` (без `--apply` только список; четыре постоянных и чужие незавершённые прогоны не трогаются).
- В JSON `plan-models` есть ключи `forecast` и `advice` — только когда в журнале есть история; маршрут они не меняют (`docs/adr/0014`).
- Файлы тасков искать только через `ticket_files(state, pattern)` в `ap.py` (там `glob.escape`): прямой glob по пути проекта ломается на `[`.
- Этап хранит `segments: [{startedAt, finishedAt|null}]`; минуты — сумма отрезков, нет `segments` — старый расчёт (`docs/adr/0006`).
- Маршрут таска задаёт оценка планировщика в файле таска: `**Класс:** механический|обычный|сложный`, `**Риск:** обычный|высокий`, `**Причина класса:**` (до 200 знаков; `check-plan` требует класс и причину); слов по тексту роутер не ищет (`docs/adr/0007`), зона остаётся нижней границей риска; профиль `cheap` разделён на `cheap_read` (haiku/low) и `cheap_code` (haiku/high); как старое имя `cheap` ведёт себя в сохранённых маршрутах, не проверено (`docs/adr/0002`, `0003`).
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, и `process_containment.py`.
- `worktrees.py land` требует `--zone`; в доках и командах `py -3`, не `py -3.13`.
- Ключ подписи гейтов — `~/.autopilot/gate.key` (или `$AUTOPILOT_HOME`), запись «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`; в strict-прогоне `.autopilot/*.py` закрыты от Write/Edit. На Windows `gate.key` хранит блок `dpapi:` (читать и писать только через `gate_sign.py`; старый открытый файл переписывается защищённым); на остальных ОС — файл. `bash_gate` запрещает субагенту запись, удаление, копирование и перенос в `.autopilot/`, `~/.autopilot/`, `.claude/agents/`; принятые пробелы: `>|`, `case…esac`, `find -exec sh -c`, `perl -pi`, heredoc, подстановки `$(...)`.
- Допустимые модели субагентов задаёт `model_router.is_allowed_subagent_model(name, premium_ok=…)`; Opus допускается только при подписанном подтверждении пользователя, Fable не проходит никогда.
- Подтверждение Opus — поле `opusApproval` в `state.js` (подпись `sig`); пишется только `ap.py opus approve --tickets 03,05 --roles repair,reviewer --by-user "<слова пользователя>"`, `opus propose` лишь печатает. Подписи (`sig`, `agentsSig`) привязаны к прогону (`run = slug|startedAt`), guard сверяет обе; Opus-ремонтник назначается `ticket F<n> route` при подтверждённой роли `repair` и допускается только на fix-таск в работе; профили зовут по `ap.py agent-for reviewer|repair`.
- Упавший таск возвращается только `ticket NN reset --by-user "<цитата>"` (на не упавшем счётчики не обнуляются); сдача с отказами — `finish --by-user`, жёсткие причины (блокер, подпись) цитатой не снимаются; `git-check` смотрит git из cwd.
- Дизайны дашборда — реестр `DESIGNS` (шесть, по умолчанию `aurora`) в `skills/autopilot/phases/dashboard-template.html` (`docs/autopilot/dashboard-views.md`); страница одна, дизайн — `data-design` на `<html>`, выбор в `localStorage['autopilot-design']`; светлая/тёмная тема только у `aurora`; пункты рейки строятся по якорям `mission/tasks/models/quality`, что есть на странице; особые элементы — слоты `dxTicker/dxAscii/dxDim/dxStamp/dxRing`; потолок шаблона 450 КБ. `.autopilot/dashboard.html` — копия шаблона: в живом проекте обновляй `dashboard_upgrade.py`, а не копированием.
- Отпечаток таска считается по нормализованному тексту (LF, без BOM и хвостовых пробелов): окончания строк не страшны. Правка смысла сданного таска останавливает `ap.py tickets` с командой `ticket NN accept-edit --note "..."`. Версию Claude Code проверяет `ap.py claude-version` до `init`. Исполнители коммитят `git commit --only <файлы зоны>`, без `git stash`.
- Журнал прогона — `.autopilot/run-log.jsonl` (только метаданные, пишет `run_log.py`, сбой записи глотается); свод — `ap.py report-run [--share]`; харнессы, копирующие `ap.py` или `claude_attest.py`, копируют и `run_log.py`.
- Единственная эскалация модели — `ticket NN retry --cause tests --escalate`: Haiku-таск после первого дозапроса уходит один раз на Sonnet-исполнителя `repairAgent`, в таск пишется `escalatedFrom`; остальные сбои модель не повышают (`docs/autopilot/retry-policy.md`).
- Расход: `compute_spend` считает ещё `cache_read`, `cache_write`, `hit`; расход главной сессии пишет `ap.py spend-orchestrator [--transcript PATH]` (и `finish`) строкой `role=orchestrator` — только числа и модель, по умолчанию самый свежий журнал папки проекта в `~/.claude/projects/` (`docs/autopilot/measuring-cost.md`).
- Расход субагентов пишут хуки `claude_attest` (строгий прогон) и `ap.py spend-subagents [--transcript PATH]` (и `finish`) из `<журнал сессии>/subagents/agent-*.jsonl` — в обычном прогоне тоже; читатели берут последнюю строку на `agent`, при строках хуков журнальные `autopilot-…` отбрасываются (`docs/autopilot/measuring-cost.md`).
- Постоянные профили `autopilot-executor|reviewer|acceptance|explorer` без `model`/`effort` (модель и усилие — параметром вызова): `init` обычного прогона пишет их в `.claude/agents/` через `agent_profiles.install_permanent` (файлы под `.gitignore`); `ap.py agents install-user --by-user "<цитата>" | --decline` — в профили пользователя; `run_log.role_of` берёт роль из имени, в том числе из `autopilot-executor-03-…` (`docs/adr/0008`, `tests/test_light_profiles.py`).
- Подсказка `↑` о размере контекста главной сессии — на `init` и `stage build|review|final` (`ap.context_hint`, `last_context_tokens`); порог `AUTOPILOT_CONTEXT_HINT`, по умолчанию 150000, `0` выключает (`docs/adr/0009`); замеры по журналам — `tools/measure-run.py`.
- `ap.py` коммитит только через `commit_paths` (`git commit --only -- <пути>`) (`docs/adr/0010`): `ap.py chore <имя>` гоняет генератор из таблицы «Команды-генераторы» в `interfaces.md` прогона; `ap.py ticket NN land --message … --requirements R..` (`--zone a/,b/` через запятую, `--allow` — файлы, грязные до таска) берёт проверку из строки `Полная проверка: \`…\`` там же; в `isolateTickets` и при `tk["worktree"]` отказывает.
- `bootstrap` и `doctor` работают до `init` и без `state.lock` (`docs/adr/0011`); масок `allowed-tools` для них нет — будет запрос разрешения; `upgrade-tools` и `init` копируют и новые `.py` навыка.
- `ticket F<n> route --model --effort --reason` в обычном прогоне пишет `tk["routing"]` без профиля; строгая ветка прежняя.
- `blind` второго круга сводит круги в `state.blind.rounds`, верхние поля — итог; `checked` круга 2 — от числа расхождений круга 1 до него же плюс один (`docs/adr/0012`).
- Тексты чужих режимов лежат в `phases/4-plan-strict.md`, `4-plan-opus.md`, `5-strict.md`, `5-sequential-host.md`; `tests/test_text_split.py` держит размер обычного пути и дословность переноса.
- `plan-fact record --verdict "T02.1 | сделано | файл:строка" …` накладывает вердикты по id на прежние (`planFact.items`), чужие пункты не стирает; «сделано» требует `путь:строка` или `путь::имя` с существующим путём, неизвестный id — отказ, строки «план: …» в `concerns` заменяются; пункты с id — `plan-fact list` (`plan_items.py`, `phases/8-plan-fact.md`).
- `check-review-report --file ФАЙЛ` — код 1, если пункт чек-листа без ответа (`review_checks.py`); `check-bypass [A..B]` только печатает сигналы.
- `blocker confirm --id B01 --verdict confirmed|not-confirmed --quote "…"` — `not-confirmed` ставит `downgraded`; вердикт хранится в блокере (`secondPass`), второй `confirm` по тому же блокеру — отказ (`docs/adr/0027`).
- `ticket NN redproof|baseline --command "…"` — проверка до правки для `bug`/`refactor`; `ticket NN bundle` — сводка для исполнителя.
- `ticket NN land --include a,b` коммитит файлы вне зоны; `--allow` не коммитит (`land_check.py`, `docs/adr/0025`, `0026`).
- `init --kind …`: справка пишет `feature`, код знает `quick|bug|task|refactor` (`kinds.KINDS`); сценарии — `phases/kind-*.md`, `docs/adr/0020`.
- `silence [--limit СЕК]` — код 3, если есть тихие агенты; останавливает их оркестратор (TaskStop), не `ap.py` (`silence.py`, `docs/adr/0022`).
- `lessons candidates|add|show|drop N|check` и `profile refresh` — уроки в `.autopilot/lessons.md`, профиль в `.autopilot/profile.md` (`lessons.py`, `docs/adr/0024`).
- После правки `ap.py` или модуля из `skills/autopilot/tools/` — `ap.py upgrade-tools` обновляет копии в `.autopilot/`.
- Что осталось после этой сборки — `.autopilot/PROGRESS.md`.
<!-- autopilot:end -->
