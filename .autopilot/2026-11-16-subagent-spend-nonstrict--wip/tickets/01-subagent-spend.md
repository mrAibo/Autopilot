# 01 — Расход субагентов из журналов Claude Code, без хуков

**Требования:** R01, R02, R04i, R05i, G01
**Зависит от:** —
**Зона:** `skills/autopilot/tools/run_log.py` · `skills/autopilot/tools/ap.py` · `docs/autopilot/measuring-cost.md` · `AGENTS.md` · `tests/test_subagent_spend.py` · `tests/test_spend_accounting.py` · `tests/test_run_log.py`
**Волна:** 1
**Ревью:** нет
**Модель:** обычная
**Класс:** обычный
**Риск:** обычный
**Причина класса:** новый разбор формата журналов Claude Code и правка дедупа в двух читателях; логика не механическая, но в одном модуле
**Объём:** 500

## Что должно заработать

В обычном прогоне `ap.py spend-subagents [--transcript PATH]` (и `finish`) записывает в `run-log.jsonl` расход каждого субагента из `<журнал сессии без .jsonl>/subagents/agent-*.jsonl` (+ `.meta.json`): строки `k=executor` с полями `agent`, `agent_type`, `role`, `model`, `ticket`, `turns`, `input`, `output`, `cache_read`, `cache_write`. `report-run` и дашборд показывают их по ролям, моделям и таскам; повторный запуск не удваивает суммы.

Спецификация: `spec.md` истории 1–11; границы — `interfaces.md`. Читай `interfaces.md` первым.

## Из брифа, дословно

> «Сделай сборку по записи расхода субагентов в обычном режиме.»
> «ок» — читать только суммы токенов, имя модели и agentType; взять усечение длинных путей в `session_transcript`.

## Критерии приёмки

Формат: файл `agent-<id>.jsonl` — строки с `message.role=assistant`, `message.usage` (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`), `message.model`, `message.id`, `timestamp`; рядом `agent-<id>.meta.json` с `agentType`. Поведение сверяй с существующими `usage_by_model` и `spend_orchestrator`.

- [ ] `run_log.usage_by_agent(folder, since, until=None)` по интерфейсу; смотрит только `agent-*.jsonl`; `isSidechain` не фильтрует (в этих файлах он всегда true); повтор `message.id` — последний; битая строка и битый/отсутствующий meta не роняют (`agent_type` «agent»); в результат не попадает текст
- [ ] `KINDS["executor"]` получает `agent`, `ticket`; `ap.spend_subagents` и команда `spend-subagents`; `finish` зовёт её после оркестратора, сбой `finish` не роняет; печатная строка про субагентов, при отсутствии папки — «субагентов нет»
- [ ] Таск — единственный таск, в окне `startedAt…finishedAt` (или до «сейчас») которого лежит `first_at` агента; несколько или ни одного — поля `ticket` нет
- [ ] `compute_spend` и `run_log.summarize`: последняя строка на `agent`; `byTicket` берёт `ticket` из строки, иначе из имени профиля; при наличии строк хуков (без `agent`) строки журнала с `agent_type` вида `autopilot-…` отбрасываются
- [ ] `session_transcript` находит папку по общему префиксу, когда точной нет (shortcut-комментарий о неизвестном правиле усечения); точная папка приоритетна
- [ ] Тесты в `tests/test_subagent_spend.py` на истории 1–5, 7, 9–11 спецификации; ни один тест не берёт настоящую `~/.claude`; красный-до-правки для дедупа и окна таска
- [ ] `docs/autopilot/measuring-cost.md` — короткий раздел «Расход субагентов в обычном режиме»; `AGENTS.md` — строка про обычный режим исправлена (расход субагентов пишет и `spend-subagents`; хуки нужны только в строгом); счётчик тестов обновить `python skills/autopilot/tools/test_count.py --write` в конце
- [ ] `python -m unittest discover -s tests -p test_subagent_spend.py`, `-p test_spend_accounting.py`, `-p test_run_log*.py` зелёные; полный прогон не запускать
