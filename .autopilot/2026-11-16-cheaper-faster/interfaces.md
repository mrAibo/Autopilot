# Границы и правила проекта

Каждый исполнитель читает этот файл первым, затем `notes.md` (где что лежит в коде, с номерами строк).

## Правила проекта (из «Договорились» прошлых сборок — не пересматривать)

- «пуш мэйн» (2026-11-16): `main` отправлен в `origin`; прежнее «не пушить» снято. В этой сборке исполнители не пушат.
- «ок» (2026-11-16): из журналов субагентов читать только суммы токенов, модель, `agentType`, id агента, `timestamp`; из журнала главной сессии — только суммы токенов. Текст сообщений, промпты и `description` не читаются и не сохраняются (кроме уже существующей метки в `tools/measure-run.py`, которую эта сборка не расширяет).
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/`; на Windows ключ под DPAPI.
- Opus — только по подтверждению пользователя (`ap.py opus approve --by-user "<цитата>"`); Fable не допускается ни под каким написанием. Правила Opus в этой сборке не меняются.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя (`reset --by-user`, `finish --by-user`); `dropped` ставит только пользователь.
- Лого остаётся в шапке и рейке дашборда; «Классика» держит старые цвета.
- Жёсткий минимум Claude Code 2.1.295; ниже 2.1.311 — предупреждение, не отказ.
- Принятые пробелы `bash_gate` (`>|`, `case…esac`, `find -exec sh -c`, `perl -pi`, heredoc, `$(...)`) — не чинить.
- Маршрут таска задаёт планировщик (`**Класс:**`, `**Риск:**`, `**Причина класса:**`); регулярных выражений по тексту таска нет; Haiku только за «механическим» классом.
- Адрес дашборда с токеном печатает только `ap.py url`; в чат и файлы не вставлять.
- `.claude/settings.json` и `ROADMAP-claude-code-2026-11.md` в корне — не трогать и не коммитить (отложено пользователем).
- Шлюзы G1–G4, слепота приёмки, подписи, guard, запрет Fable не ослабляются. При переносе текста навыка не теряется ни одно правило: перенос дословный.

## Как здесь работают

- Python, только стандартная библиотека. Исходники — `skills/autopilot/tools/*.py`, тексты навыка — `skills/autopilot/SKILL.md`, `phases/`, `prompts/`. Копии `.autopilot/*.py` и `.autopilot/dashboard.html` исполнитель не правит.
- `state.js` — только через `state_io.py`; файлы тасков — через `ticket_files(state, pattern)`.
- Новый модуль инструментов, который импортирует `ap.py`, добавляется в списки копий харнессов: `tests/test_ap.py` `setUp`, `test_ap_escalation.py`, `test_gui_bridge_e2e.py`, `test_subagent_spend.py`, `test_spend_accounting.py`. В этой сборке новых модулей не заводим: код идёт в существующие файлы.
- Новая команда `ap.py` вписывается и в docstring в начале файла, и в таблицу команд `phases/0-instruments.md` §4.
- В документах и командах `py -3`, не `py -3.13`. Коммит: `git commit --only -- <файлы зоны>`, без `git stash`, без `git add -A` по дереву.
- Тексты для пользователя — по-русски; имена в коде — по-английски.
- Один файл тестов: `python -m unittest discover -s tests -p test_x.py`. Синтаксис: `python -m compileall -q skills/autopilot/tools tests`.

Полная проверка: `python -m unittest discover -s tests`

(около 8 минут, 959 тестов до этой сборки, 5 пропущено; исполнитель гоняет свои файлы тестов, полный прогон — перед сдачей таска.)

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| test-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Границы, решённые в спецификации

| Единица | Владеет | Открывает | Прячет |
|---|---|---|---|
| `agent_profiles.permanent_profiles() -> list[(Path, str)]` и `agent_profiles.install_permanent(root) -> list[str]` | текстом и записью четырёх постоянных профилей | имена `autopilot-executor`, `autopilot-reviewer`, `autopilot-acceptance`, `autopilot-explorer`; `install_permanent` возвращает имена записанных (нет файла или текст отличается), остальное не трогает; не бросает наружу из `init` | frontmatter без `model`, `effort`, пути таска; `definition`/`prepare` строгого прогона не меняются |
| `run_log.role_of(agent_type)` и `ap.EXEC_TICKET` | разбором роли из имени профиля | `autopilot-executor` и `autopilot-executor-03-…` → `executor`; так же reviewer, explorer, acceptance | — |
| `ap.py agents install-user --by-user "<цитата>"` / `--decline` | записью в `$CLAUDE_CONFIG_DIR\|~/.claude` → `agents/` и ответом в `$AUTOPILOT_HOME/user-profiles` | `init` печатает строку `?`, пока ответа нет | без `--by-user` вне проекта ничего не пишет |
| `ap.last_context_tokens(transcript=None) -> int \| None` | чтением хвоста журнала главной сессии | вход + чтение кэша + запись кэша последнего ответа без `isSidechain`; `None` — журнала нет или не читается | читает только числа; порог — `AUTOPILOT_CONTEXT_HINT`, по умолчанию 150000, 0 выключает |
| `ap.commit_paths(paths, message, trailers) -> sha` | единственным местом, где `ap.py` коммитит | `git commit --only -- <пути>` с трейлерами; общий для `chore` и `ticket land` | — |
| `ap.interfaces_section(state, …)`: `full_check_command(state) -> str \| None`, `generators(state) -> {имя: (команда, [файлы])}` | разбором `interfaces.md` прогона | строка `Полная проверка: \`…\`` и таблица раздела «Команды-генераторы» | формат выше в этом файле — эталон |
| `ap.py chore <имя>` | запуском генератора и коммитом объявленных файлов | код 0 — закоммичено или «нечего коммитить»; код 2 — отказ, коммита нет | — |
| `ap.py ticket NN land [--zone …] --message "…" --requirements R..` | посадкой таска в обычном прогоне | шаги: вне зоны → полная проверка → коммит → `done`; успех ≤5 строк; красный шаг — 1–3 строки, код 2 | в `isolateTickets` или при `tk["worktree"]` отказывает с подсказкой |
| `ap.py bootstrap --project <путь>` | установкой инструментов в `<проект>/.autopilot/` | печатает `skillDir = …`; идемпотентна | не берёт `state.lock` в папке навыка |
| `ap.py doctor` | сводной предполётной проверкой проекта в текущей папке | по строке на проверку; код 2 только при отказе `git-check` или версии ниже минимума | отдельные `git-check`, `claude-version` не меняются |
| `ap.py ticket F<n> route --model … --effort … --reason "…"` (обычный прогон) | записью `tk["routing"]` без профиля | `{model, effort, reason, provider}`; строгая ветка не меняется | — |
| `run_log.collapse_agents(rows)` | сведением строк хуков и журнала | журнальная `autopilot-…` отбрасывается только при строке хука с тем же `agent_type` | — |
| `ap.py blind checked=N matched=M [--mismatch …]`, круг 2 | сведением двух кругов | `state["blind"] = {checked, matched, mismatches, rounds: [{checked, matched, mismatches}, …]}`; верхние поля — итог | круг 2: `checked ≤ len(расхождений круга 1) + 1` |

Швы для тестов: всё через подпроцесс `ap.py` в харнессе `tests/test_ap.py` (`self.ap(...)`, уже с `--no-serve`); журналы — фикстурные `.jsonl` во временной папке с `--transcript` или `CLAUDE_CONFIG_DIR`; `tools/measure-run.py` — подпроцессом на фикстурной папке; тексты фаз — чтением файлов, как в `tests/test_documentation_locales.py`.

## Что завершённые таски построили

- Таск 01: `agent_profiles.permanent_profiles() -> [(Path, str)]`; `agent_profiles.install_permanent(root, agents_dir=".claude/agents") -> [имена]`; `ap.last_context_tokens(transcript=None) -> int | None`; `ap.context_hint() -> str`; `ap.cmd_agents` (`agents install-user --by-user|--decline`); `tools/measure-run.py <проект> [id|all]` — колонки «стартовый контекст», тип агента, таблица ходов оркестратора. Тесты — `tests/test_light_profiles.py`.
- Таск 02 (`ap.py`): `full_check_command(state) -> str | None`; `generators(state) -> {имя: (команда, [файлы])}`; `commit_paths(paths, message, trailers) -> sha | None`; `count_tests(text) -> (прошло, упало) | None`; команды `chore <имя>`; `ticket NN land --message … [--zone a/,b/] [--requirements R01,R02] [--allow пути] [--placeholder R05]`; `bootstrap --project <путь>`; `doctor [--text <версия>]`; `state.blind` после круга 2 — `{checked, matched, mismatches, rounds: [{…}, {…}]}`. `upgrade-tools` и `init` доносят все новые `.py` навыка. Тесты — `tests/test_one_command.py`.
- Решение по R05 (замер таска 01: в среднем 8,2 шага оркестратора на посадку, медиана 3, 49 окон из 14 сессий): три и больше — R05 делается.
