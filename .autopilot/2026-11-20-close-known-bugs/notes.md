# Заметки о коде
Всё в `skills/autopilot/tools/`; тесты — `tests/` (`test_work_kinds.py`: land_check, redproof, blocker; `test_review_accuracy.py`: plan-fact, blocker confirm). После правки — `ap.py upgrade-tools`.
- `plan_items.py`: `_proved` (регэксп EVIDENCE: `путь:N` | `путь::имя`), `build_plan_fact`, `merge_verdicts`.
- `ap.py`: `cmd_plan_fact` (~3576: строка со `state["concerns"] = [...startswith("план: ")]` — стирает всё), `blocker_confirm` (~3532, отказ «уже есть вердикт»), `cmd_blocker` (~3636), `cmd_proof` (~2964, регэксп с SyntaxError…; комментарий «ImportError законен»), `cmd_land` (~3020; `commit_paths(files, msg, trailers)`).
- `land_check.py`: `_own`, `_foreign_files` (git log `%H %s`, потом `git show --name-only` — у merge пусто).
