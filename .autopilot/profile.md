# Профиль проекта

## Команды
- полная проверка: `python tools/run-tests.py`
| Команда | Что делает |
| `—` | Установка не нужна: только стандартная библиотека Python |
| `python3 skills/autopilot/tools/ap.py` | Поднять дашборд, адрес без токена (в проектах — `.autopilot/ap.py`); адрес с токеном — `ap.py url` |
| `python3 skills/autopilot/tools/ap.py bootstrap --project .` | Из папки навыка поставить инструменты в `.autopilot/` проекта (до `init`, без `state.lock`) |
| `python3 .autopilot/ap.py doctor` | Предполётная проверка проекта: строка на проверку, код 2 — отказ `git-check` или версия ниже минимума |
| `python3 -m unittest discover -s tests` | Все тесты последовательно |
| `python tools/run-tests.py` | Все тесты параллельно, итог в формате unittest; CI запускает его на Python 3.11 и 3.13, Ubuntu и Windows |
| `python3 -m compileall -q skills/autopilot/tools tests` | Проверка синтаксиса |

## Стек
не определён

## Подводные камни
- Полный прогон тестов идёт около 10 минут (<!-- tests:count -->1238<!-- /tests:count --> тестов, 5 пропущены; число подставляет `skills/autopilot/tools/test_count.py --write`); один файл: `python -m unittest discover -s tests -p test_x.py`.
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
