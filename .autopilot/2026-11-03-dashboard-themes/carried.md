# Что оставила прошлая сборка (копия PROGRESS.md на старте)

Последняя сборка: `.autopilot/2026-11-03-audit-fixes/`.

## Договорились
- Ключ подписи гейтов хранится вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/` — R05, R17
- Opus и Fable не допускаются в субагенты ни под каким написанием — R06, R18

## Не доделано
- `scheduler.py:135` и `dashboard_upgrade.py:28` разбирают `state.js` вручную: BOM ломает scheduler CLI и обновление дашборда
- Алиас `claude-3-5-haiku-latest` роутер отклоняет (fail-closed)
- `.autopilot/__pycache__/*.pyc` глубины 3 не закрыт от Write-хука

## Известные баги
- Запись в `state.js` через Bash хук не ловит (только Write/Edit)
- `execution sequential-host` стирает запись подписи, но оставляет `gateMark` — `ap.py:985,1586`
- Запись подписи не атомарна — `ap.py:2286,2311`
- Тест `test_timeout_kills_the_grandchild_too` на Windows пропускается

## Изменено после сборки
Ничего: коммитов после «Autopilot: сборка сдана» нет.
