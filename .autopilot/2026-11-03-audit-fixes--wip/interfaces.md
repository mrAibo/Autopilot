# Границы и правила проекта

## Правила проекта
- Только stdlib, Python 3.11+. Править только `skills/autopilot/tools/`, `tests/`, `docs/`, README×3, STATUS.md, `skills/autopilot/SKILL.md`, `skills/autopilot/phases/0-instruments.md`, `.github/workflows/`. Копии в `.autopilot/*.py` не трогать.
- Тесты — unittest, лежат в `tests/`; перед коммитом `python3 -m unittest discover -s tests` целиком зелёный.
- Имена в коде английские. Сообщения пользователю — по-русски, как в соседнем коде.
- Новый модуль инструментов → строка в списке копирования `phases/0-instruments.md`.
- Не коммитить ничего вне зон своего тикета.

## Границы, решённые в спецификации

**`tools/state_io.py`** (новый). Владеет: разбором и записью `state.js`. Открывает:
- `parse_state_text(text: str) -> dict` — BOM, префикс `window.STATE =`, `;` допустимы; пусто/мусор → `StateError`.
- `read_state_file(path) -> dict` — читает файл (utf-8-sig), `StateError` при отсутствии/порче.
- `write_state_file(path, state: dict, *, prefix="window.STATE = ") -> None` — `.tmp` + `replace_with_retry`; при провале удаляет `.tmp`, поднимает `StateError`.
- `replace_with_retry(src, dst, *, windows=None, attempts=12) -> None` — повтор только при WinError 5/32.
- `class StateError(Exception)`.
Скрывает: формат обёртки, политику повтора. Вызывающие сами решают, что делать с `StateError` (ap — `die`, controller — `ControllerError`, guard — deny).

**`tools/gate_sign.py`** (новый). Владеет: ключом и подписью.
- `key_path() -> Path` (`$AUTOPILOT_HOME` или `~/.autopilot` + `gate.key`); `ensure_key() -> Path` (создаёт 0600, только вызывается из `init --strict-routing`); `load_key() -> bytes | None`.
- `sign(payload: dict) -> str` — hex HMAC-SHA256 над каноническим JSON (sort_keys, separators), `sig` в payload не входит.
- `verify(payload: dict, sig: str) -> bool` — constant-time; нет ключа → `False`.
- `MISSING_KEY_MESSAGE` — готовая фраза для пользователя.

**`tools/process_containment.py`** (расширяется). `run_contained(cmd, *, timeout, env=None, cwd=None) -> subprocess.CompletedProcess` — по таймауту убивает всю группу/Job и поднимает `subprocess.TimeoutExpired` после очистки. `OwnedJob.terminate` на POSIX делает `killpg`.

**`tools/model_router.py`** (расширяется). `is_allowed_subagent_model(name: str, policy: dict | None = None) -> bool`; `normalize_model_name(name: str) -> str`. `claude_agent_guard` импортирует её (модули лежат рядом).

**`tools/worktrees.py`** (расширяется). `changed_paths(cwd) -> list[str]` (diff + diff --cached + ls-files --others, всё с `--no-renames`); `check_paths_in_zones(paths, zones) -> None` (поднимает существующий тип ошибки finalize); `land` вызывает проверку над путями коммита (`git diff-tree --no-commit-id --name-only -r --no-renames <sha>`). `worker_outcome.inspect` использует `changed_paths`.

**Швы для тестов:** `state_io` (чистые функции, tmp-каталог); `gate_sign` (через `AUTOPILOT_HOME` во временный каталог); `run_contained` (скрипт-внук); `is_allowed_subagent_model` (таблица имён); `land` (временный git-репозиторий, как в test_worktrees.py).
