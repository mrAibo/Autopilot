# Границы и правила проекта

## Правила проекта
- Стек: Python 3.11+, только стандартная библиотека; запуск `python3` (в доках `py -3`).
- Проверка: `python3 -m compileall -q skills/autopilot/tools tests` и `python3 -m unittest discover -s tests` (~5 минут; один файл — `python3 -m unittest discover -s tests -p test_x.py`).
- Править `skills/autopilot/**`, `tests/**`, `docs/**`, `CHANGELOG.md`. Не править: `.autopilot/**` (копии и состояние), `skills/autopilot/phases/dashboard-template.html`, `.claude/**`, файлы вне зоны.
- `state.js` читать и писать только через `skills/autopilot/tools/state_io.py`.
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, и `process_containment.py`.
- Коммит: `git commit --only <файлы зоны>`, без `git stash`/`git reset`; перед коммитом `git diff --cached --stat`. Заголовок — что (`fix: …`), трейлер `--trailer "Requirements: R01"`.
- В файлах репозитория никаких путей машины (`C:\Users\<имя>\…`, `/home/<имя>/…`) — только `<repo>`, `<scratchpad>`.

## Договорились (из PROGRESS.md, дословно)
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), признак «прогон начат подписанным» — в `$AUTOPILOT_HOME/runs/` — R05, R17
- Opus и Fable не допускаются в субагенты ни под каким написанием — R06, R18

- Жёсткий минимум Claude Code 2.1.295; ниже 2.1.311 — предупреждение, не отказ — R06 (волна 1)

## Границы, решённые в спецификации

**`run_log.py`** (новый, только стандартная библиотека) — владеет файлом `.autopilot/run-log.jsonl` (+ одна ротация `run-log.1.jsonl` при размере больше 1 МБ), схемой строки и сводкой.
Открывает:
- `append(autopilot_dir: str, kind: str, **fields) -> bool` — дописывает одну строку `{"t", "run", "k", ...}`; **никогда не бросает исключение**, при любом сбое возвращает `False`; пропускает только известные поля, строки длиннее 120 символов обрезает, значение с путём машины заменяет на `"[path]"`;
- `read_all(autopilot_dir: str) -> list[dict]` — обе части журнала по порядку, битые строки молча пропускает;
- `usage_from_transcript(path: str, max_bytes: int = 5_000_000) -> dict | None` — `{"turns", "input", "output", "cache_read", "cache_write"}` из JSONL-транскрипта субагента; при любой ошибке `None`;
- `summarize(records: list[dict], run: str | None = None) -> dict` и `render_report(summary: dict, share: bool = False) -> str` — таблица Markdown: фазы, таски, повторы, простои, токены; `share=True` убирает имена прогона и таска, абсолютные времена и всё, кроме чисел и типов ролей.
Скрывает: формат файла, ротацию, фильтр полей, разбор транскрипта.

**Схема строки (`k`):** `phase` (`id`, `act`: start/done/skip/fail) · `ticket` (`id`, `act`: start/done/retry/fail/repair/review, `cause`) · `gate` (`g`, `ok`, `reason`) · `tests` (`passed`, `failed`, `seconds`, `source`: ticket/host/manual) · `reset` (`what`: ticket/gate, `id`, `reason`) · `wait` (`kind`, `act`: start/end) · `executor` (`agent_type`, `turns`, `input`, `output`, `cache_read`, `cache_write`).

**`ap.py`** — шов записи: `log(state, event, **kw)` (общая воронка) после своей работы зовёт `run_log.append`, обёрнутый в `try/except Exception`; новое событие `ticket-reset` (`id`, `reason`) при сбросе статуса в `publish_tickets`, `ticket NN reset` и перерасчёте; новая команда `report-run [--share]` — читает только журнал, не берёт блокировку состояния, работает и без `state.js`; `ensure_gitignore()` добавляет `.autopilot/run-log*.jsonl`. `ap.py tests N/M` принимает необязательный `--seconds S`; `worktree verify` кладёт измеренную длительность.
Открывает: `report-run`, `machine_path_hits` (как раньше).
Скрывает: сопоставление событий `log()` ↔ схема журнала.

**`claude_attest.py`** — на `SubagentStop` после записи в `attestations.jsonl` зовёт `usage_from_transcript(agent_transcript_path)` и `run_log.append(..., "executor", ...)`, всё в `try/except`: хук с журналом не должен падать и не должен менять ни код выхода, ни запись аттестации.

**`claude_agent_guard.py`** — `bash_decision(command) -> (bool, reason)` сохраняет сигнатуру. Новые формы: имя команды `git`, `git.exe`, `<путь>/git`, `<путь>/git.exe` (регистр не важен); оболочка `bash|sh|zsh|dash [-флаги] -c "<строка>"` — строка разбирается тем же правилом (глубина до 3); запрещены `stash`, `reset`, `checkout --`, `checkout .`, `restore .`, `clean` с флагом `-f`/`--force` (в любом кластере: `-fd`, `-df`, `-xdf`).
Скрывает: разбор команды, обход обёрток.

**Швы для тестов:** `run_log.append / read_all / summarize / render_report / usage_from_transcript`; `claude_agent_guard.bash_decision`; сквозные — `ap.py report-run`, `ap.py tickets` (R22c) в харнессе `tests/test_ap.py`.

**Харнессы:** любой тест, копирующий `ap.py` или `claude_attest.py` в временную папку, копирует и `run_log.py` — иначе `import run_log` не найдёт модуль (список файлов ставит таск 01, он же правит харнессы).
