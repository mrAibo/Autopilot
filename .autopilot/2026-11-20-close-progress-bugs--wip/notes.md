# Заметки о коде (для исполнителей)

Всё в `skills/autopilot/tools/`; копии лежат в `.autopilot/` (после правки — `ap.py upgrade-tools`). Тесты — `tests/`.

- `plan_items.py`: `parse_items`, `parse_verdict`, `item_prefix`, `build_plan_fact(items_by_ticket, verdicts)`; статусы `DONE/PARTLY/NOT_DONE`. Пустое доказательство → `не сделано`.
- `ap.py`: `cmd_plan_fact(state, pos, multi)` (~стр. 3565): `record` собирает `verdicts` из `--verdict`, зовёт `build_plan_fact`, пишет `state["planFact"]`, на каждый не-DONE пункт `cmd_add(state, ["concerns", "план: <id> — <статус> — <текст>"])`. `plan_items_by_ticket(state)` — пункты по таскам.
- `ap.py`: `blocker_ledger`, `open_blocker`, `blocker_confirm(state, opt)` (~3530): `confirmQuote`, при `not-confirmed` статус `downgraded`; при `confirmed` статус остаётся `open` (отсюда баг повторного вердикта). `cmd_blocker` разбирает подкоманды.
- `ap.py`: `cmd_proof` (~2964) — `redproof` (код ≠ 0) и `baseline` (код 0), `run_shell(command, 1800)` → `(code, out)`, `last_line(out)`.
- `ap.py`: `cmd_land` (~3000) зовёт `land_check.preflight(ROOT, tk.get("startHead"), baseCommit, zone, i, active)` и `land_check.problems(report, i)`; `files` (вливаемые) считаются после preflight. `worktrees.py land` зовёт ту же проверку.
- `land_check.py`: `_git`, `_covers`, `_norm`, `_overlap(a, b)`, `preflight`, `problems`, `tracked_files`, `diff_text`. Тесты: `tests/test_work_kinds.py` (`LandCheckUnit`, `WorktreeLand`, `Repo` — временный репозиторий).
- Тесты на plan-fact/blocker — `grep -rn "plan-fact\|blocker confirm" tests/`.
- CI: `.github/workflows/python-tests.yml`, шаг «Unit tests». Запускатель: `tools/run-tests.py` (итог в формате unittest, код 1 при падении).
- Документация, которую надо держать в согласии: `AGENTS.md` (строки про `plan-fact record`, `blocker confirm`, CI, `run-tests`), `CHANGELOG.md` («Unreleased»), `docs/autopilot/measuring-cost.md` (замеры R23f/R26d), `.autopilot/PROGRESS.md` (пишет приёмка, не исполнители).
