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
<!-- autopilot:end -->
