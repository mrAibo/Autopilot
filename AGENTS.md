<!-- autopilot:start -->
# Autopilot

Навык (skill) для Claude Code, Codex и Cursor: из надиктованной идеи собирает готовый проект.

## Команды

| Команда | Что делает |
|---------|------------|
| `—` | Установка не нужна: только стандартная библиотека Python |
| `python3 skills/autopilot/tools/ap.py` | Поднять дашборд (в проектах — `.autopilot/ap.py`) |
| `python3 -m unittest discover -s tests` | Все тесты (CI запускает то же на Python 3.11 и 3.13, Ubuntu и Windows) |
| `python3 -m compileall -q skills/autopilot/tools tests` | Проверка синтаксиса |

## Как здесь работает Autopilot

Сборка ведётся навыком `/autopilot`. Требования, спецификация и таски — в `.autopilot/`.
Прогресс — `.autopilot/dashboard.html`. Требование из `manifest.md` может снять
только пользователь. Прерванную сборку продолжает «продолжи автопилот».

## Подводные камни

- Полный прогон тестов идёт около 5 минут; один файл: `python -m unittest discover -s tests -p test_x.py`.
- `state.js` читается и пишется только через `skills/autopilot/tools/state_io.py` (BOM, префикс, повтор `os.replace` на Windows).
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, и `process_containment.py`.
- `worktrees.py land` требует `--zone`; в доках и командах `py -3`, не `py -3.13`.
- Ключ подписи гейтов — `~/.autopilot/gate.key` (или `$AUTOPILOT_HOME`), запись «прогон начат подписанным» — `$AUTOPILOT_HOME/runs/`; в strict-прогоне `.autopilot/*.py` закрыты от Write/Edit.
- Допустимые модели субагентов задаёт `model_router.is_allowed_subagent_model`; Opus и Fable не проходят ни в каком написании.
- Темы дашборда — реестр `VIEWS` в `skills/autopilot/phases/dashboard-template.html` (`docs/autopilot/dashboard-views.md`); пункты рейки строятся по тем якорям `mission/tasks/models/quality`, что есть на странице темы (у «Обзора» нет `models`), `VIEW_HOME` задаёт пункт текущей темы; «Классика» держит старые цвета, остальные темы — палитру макетов. `.autopilot/dashboard.html` — копия шаблона: в живом проекте обновляй `dashboard_upgrade.py`, а не копированием.
- Отпечаток таска считается по нормализованному тексту (LF, без BOM и хвостовых пробелов): окончания строк не страшны. Правка смысла сданного таска останавливает `ap.py tickets` с командой `ticket NN accept-edit --note "..."`. Версию Claude Code проверяет `ap.py claude-version` до `init`. Исполнители коммитят `git commit --only <файлы зоны>`, без `git stash`.
- Журнал прогона — `.autopilot/run-log.jsonl` (только метаданные, пишет `run_log.py`, сбой записи глотается); свод — `ap.py report-run [--share]`; харнессы, копирующие `ap.py` или `claude_attest.py`, копируют и `run_log.py`.
- Что осталось после этой сборки — `.autopilot/PROGRESS.md`.
<!-- autopilot:end -->
