# Заметки по коду (журнал прогона)

Все пути от корня репозитория. Модули инструментов лежат в `skills/autopilot/tools/`, в проекте их копии в `.autopilot/`.

- `ap.py:61-64` — `import run_log` в `try/except Exception`, при сбое `run_log = None` без слова. `mirror_run_log` (`ap.py:190`) при `None` молча выходит; `cmd_report_run` (`ap.py:2644`) при `None` читает `[]` и печатает «журнал прогона пуст: …» — не отличает «нет модуля» от «ещё нет записей».
- `run_log.py`: `KINDS` (схема строк; `executor`: agent_type, turns, input, output, cache_read, cache_write), `ROLE = re.compile(r"autopilot-(executor|reviewer|explorer|acceptance)-")` (используется только в `render_report` для `--share`), `append(autopilot_dir, kind, /, **fields)`, `read_all` (пропускает нечитаемые JSON-строки молча, возвращает только dict), `summarize(records, run=None)`, `render_report(summary, share)`.
- `summarize` строит словари `phases`/`tickets`/`open_waits` по ключам из строки журнала (`id`, `kind`) — нехэшируемое значение (список) роняет её; `cause` не строка ломает склейку.
- `ap.py:2650` — свод берёт `run=records[-1].get("run")`; если последняя запись без `run` (`claude_attest.log_usage` не прочитал `state.js`), `run=None` и `summarize` берёт все прогоны.
- `claude_attest.py:77 log_usage` пишет всегда `"executor"` с `agent_type` (имя профиля: `autopilot-<роль>-<слаг>`, ремонтный — `autopilot-executor-repair-<слаг>`).
- Тест списка копирования — `tests/test_state_io.py`, класс `InstrumentsCopyListTests`: читает `cp "${TPL%/phases/*}/tools/X.py"` из `skills/autopilot/phases/0-instruments.md`, проверяет, что каждый скопированный модуль и всё, что он импортирует из `tools/`, тоже скопировано. Не проверяет, что в списке есть вообще каждый модуль `tools/`, и нигде явно не названы модули, что запускаются только из навыка.
- Харнессы тестов, копирующие `ap.py` или `claude_attest.py`, копируют и `run_log.py` (в `tests/test_ap.py`, `test_claude_attest.py` и др. после прошлой сборки).
- Команда одного файла: `python -m unittest discover -s tests -p test_run_log.py`; полный прогон около 6 минут.
- Динамические импорты (`importlib`, `__import__`) AST-разбор тестом не видит — предел.
