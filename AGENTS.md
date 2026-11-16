<!-- autopilot:start -->
# Autopilot

Навык (skill) для Claude Code, Codex и Cursor: из надиктованной идеи собирает готовый проект.

## Команды

| Команда | Что делает |
|---------|------------|
| `—` | Установка не нужна: только стандартная библиотека Python |
| `python3 skills/autopilot/tools/ap.py` | Поднять дашборд, адрес без токена (в проектах — `.autopilot/ap.py`); адрес с токеном — `ap.py url` |
| `python3 -m unittest discover -s tests` | Все тесты (CI запускает то же на Python 3.11 и 3.13, Ubuntu и Windows) |
| `python3 -m compileall -q skills/autopilot/tools tests` | Проверка синтаксиса |

## Как здесь работает Autopilot

Сборка ведётся навыком `/autopilot`. Требования, спецификация и таски — в `.autopilot/`.
Прогресс — `.autopilot/dashboard.html`. Требование из `manifest.md` может снять
(`dropped`) только пользователь; `finish --by-user` сдаёт сборку «с оговорками», строки остаются в своём статусе. Прерванную сборку продолжает «продолжи автопилот».

## Подводные камни

- Полный прогон тестов идёт около 8 минут (<!-- tests:count -->942<!-- /tests:count --> тестов, 5 пропущены; число подставляет `skills/autopilot/tools/test_count.py --write`); один файл: `python -m unittest discover -s tests -p test_x.py`.
- `state.js` читается и пишется только через `skills/autopilot/tools/state_io.py` (BOM, префикс, повтор `os.replace` на Windows).
- Сервер дашборда (`ap.py`) отдаёт данные только с `?t=<токен>` из `.autopilot/serve.token` (страница без токена приходит с `window.STATE=null`); адрес с токеном печатает только `ap.py url` (голый `ap.py` и остальные команды печатают адрес без `?t=`); адрес с токеном не вставлять в чат и скриншоты; 403 на чужой Host/Origin и `Sec-Fetch-Site: cross-site`; `file://` токена не требует (`docs/adr/0001`).
- Файлы тасков искать только через `ticket_files(state, pattern)` в `ap.py` (там `glob.escape`): прямой glob по пути проекта ломается на `[`.
- Этап хранит `segments: [{startedAt, finishedAt|null}]`; минуты — сумма отрезков, нет `segments` — старый расчёт (`docs/adr/0006`).
- Маршрут таска задаёт оценка планировщика в файле таска: `**Класс:** механический|обычный|сложный`, `**Риск:** обычный|высокий`, `**Причина класса:**` (до 200 знаков; `check-plan` требует класс и причину); слов по тексту роутер не ищет (`docs/adr/0007`), зона остаётся нижней границей риска; профиль `cheap` разделён на `cheap_read` (haiku/low) и `cheap_code` (haiku/high); как старое имя `cheap` ведёт себя в сохранённых маршрутах, не проверено (`docs/adr/0002`, `0003`).
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, и `process_containment.py`.
- `worktrees.py land` требует `--zone`; в доках и командах `py -3`, не `py -3.13`.
- Ключ подписи гейтов — `~/.autopilot/gate.key` (или `$AUTOPILOT_HOME`), запись «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`; в strict-прогоне `.autopilot/*.py` закрыты от Write/Edit. На Windows `gate.key` хранит блок `dpapi:` (читать и писать только через `gate_sign.py`; старый открытый файл переписывается защищённым); на остальных ОС — файл. `bash_gate` запрещает субагенту запись, удаление, копирование и перенос в `.autopilot/`, `~/.autopilot/`, `.claude/agents/`; принятые пробелы: `>|`, `case…esac`, `find -exec sh -c`, `perl -pi`, heredoc, подстановки `$(...)`.
- Допустимые модели субагентов задаёт `model_router.is_allowed_subagent_model(name, premium_ok=…)`; Opus допускается только при подписанном подтверждении пользователя, Fable не проходит никогда.
- Подтверждение Opus — поле `opusApproval` в `state.js` (подпись `sig`); пишется только `ap.py opus approve --tickets 03,05 --roles repair,reviewer --by-user "<слова пользователя>"`, `opus propose` лишь печатает. Подписи (`sig`, `agentsSig`) привязаны к прогону (`run = slug|startedAt`), guard сверяет обе; Opus-ремонтник назначается `ticket F<n> route` при подтверждённой роли `repair` и допускается только на fix-таск в работе; профили зовут по `ap.py agent-for reviewer|repair`.
- Упавший таск возвращается только `ticket NN reset --by-user "<цитата>"` (на не упавшем счётчики не обнуляются); сдача с отказами — `finish --by-user`, жёсткие причины (блокер, подпись) цитатой не снимаются; `git-check` смотрит git из cwd.
- Темы дашборда — реестр `VIEWS` в `skills/autopilot/phases/dashboard-template.html` (`docs/autopilot/dashboard-views.md`); пункты рейки строятся по тем якорям `mission/tasks/models/quality`, что есть на странице темы (у «Обзора» нет `models`), `VIEW_HOME` задаёт пункт текущей темы; «Классика» держит старые цвета, остальные темы — палитру макетов. `.autopilot/dashboard.html` — копия шаблона: в живом проекте обновляй `dashboard_upgrade.py`, а не копированием.
- Отпечаток таска считается по нормализованному тексту (LF, без BOM и хвостовых пробелов): окончания строк не страшны. Правка смысла сданного таска останавливает `ap.py tickets` с командой `ticket NN accept-edit --note "..."`. Версию Claude Code проверяет `ap.py claude-version` до `init`. Исполнители коммитят `git commit --only <файлы зоны>`, без `git stash`.
- Журнал прогона — `.autopilot/run-log.jsonl` (только метаданные, пишет `run_log.py`, сбой записи глотается); свод — `ap.py report-run [--share]`; харнессы, копирующие `ap.py` или `claude_attest.py`, копируют и `run_log.py`.
- Единственная эскалация модели — `ticket NN retry --cause tests --escalate`: Haiku-таск после первого дозапроса уходит один раз на Sonnet-исполнителя `repairAgent`, в таск пишется `escalatedFrom`; остальные сбои модель не повышают (`docs/autopilot/retry-policy.md`).
- Расход: `compute_spend` считает ещё `cache_read`, `cache_write`, `hit`; расход главной сессии пишет `ap.py spend-orchestrator [--transcript PATH]` (и `finish`) строкой `role=orchestrator` — только числа и модель, по умолчанию самый свежий журнал папки проекта в `~/.claude/projects/` (`docs/autopilot/measuring-cost.md`).
- Что осталось после этой сборки — `.autopilot/PROGRESS.md`.
<!-- autopilot:end -->
