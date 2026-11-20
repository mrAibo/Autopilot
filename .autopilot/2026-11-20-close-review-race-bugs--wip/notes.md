# Заметки по коду

- `skills/autopilot/tools/ap.py`:
  - `cmd_ticket` (~2483): для `start` и `done` строка `pending = [dep for dep in tk["blockedBy"] if known[dep].status != "done"]` → отказ «сначала заверши зависимости» (~2552–2556). Именно она не пускает зависимый `start`, пока зависимость в `review`.
  - `cmd_land` (~3029): `waiting` — то же условие для `land`; его менять не нужно (land = сдача, зависимость должна быть `done`).
  - `commit_paths(paths, message, trailers)` (~2896): `git add -- <пути>` → `git commit --only -- <пути>`; `--literal-pathspecs`. Если в индексе стоит переименование (`git mv old new`), а в `paths` только новый путь, удаление `old` остаётся в индексе после коммита.
- Точечное ревью идёт ПОСЛЕ коммита (`phases/6-review.md`, `phases/5-subagents.md`): код зависимости уже в `HEAD`, когда таск в `review`; «ждать ревью — не повод держать волну».
- `skills/autopilot/tools/gate_sign.py` + `tests/test_gate_sign.py` — ключ подписи гейтов; в тестах `KeyRaceTests` гонка за пустым `gate.key` (`_claim_empty`, `_create_key_atomically`, `ensure_key`); `AUTOPILOT_HOME` подменяется `mock.patch.dict` на каждый тест. Параллельный запуск — `tools/run-tests.py` (классы с `serial = True` идут отдельно).
- Тесты по теме: `tests/test_ap.py`, `tests/test_hardening_2026_11.py` (commit_paths), `tests/test_scheduler.py` (blockedBy).
