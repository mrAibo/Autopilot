# Заметки разведки (ap.py, строки на момент 8d9af0a)

- `cmd_land` 3157–3259: проверка `code, out = run_shell(check, 1800)` (3221), `count_tests` (3224); красный: `tk["lastCheck"]` = последние 30 строк (до 3000 знаков), `red("проверка", "красная: код N, упало M", last_line(out))` (3225–3228). `red(step, why, hint)` печатает «land NN: стоп на шаге «…» — …» + строку-подсказку, `sys.exit(2)`.
- `full_check_command(state)` 2948 (регэксп по `interfaces.md`), `run_shell` 3001 → `(код|None, stdout+stderr)`, `count_tests` 3014, `last_line` 3032. Разбора `FAIL:`/`ERROR:` нигде нет.
- `cmd_stage` 1797 (порядок `ORDER` 148), `cmd_finish` 4171–4259: полную проверку не запускают; предупреждения `finish` — список `notes` со строками «! …» (4242), печать в main 5028–5029.
- Команд-таблицы нет: `main()` 4830 — цепочка `if cmd == "…"` / `elif cmd == …`; опции — `parse_args` 1442, читаются `opt.get("имя")`; справка — докстринг модуля.
- `blind`: `cmd_numbers(state, "blind", …)`, второй круг 3949–3972 (не менять). `phases/8-final.md` ст. 49–63, 75; `phases/short/8-final.md` ст. 13.
- Дашборд: строка «план: N из M» — `planOf` (1521), карточка `section.card.w > h3.wt` (2814–2815), условие `S.planFact && Number.isFinite(+S.planFact.total)`. `tools/check-dashboard-browser.py`: `fixture` 26, `design_ids` 94, `shoot_designs` 99, `finished_fixture` 135, `main` 194; ширины 1440×2600 и 400×3600; проверка — размер PNG; DOM-проверки нет.
- `context-pack`: `phases/3-spec.md` (ст. 5, 7), `short/3-spec.md` ст. 7, `5-subagents.md` ст. 24, `short/5-subagents.md` ст. 8, `prompts/executor.md` ст. 10.
- Тесты land: `tests/test_one_command.py` (`Project` 68, `Land(Project)` 199, `land(*args)` 210; `ap(*args)` → (код, вывод); `mode("green")`/`.autopilot/check.mode`), `tests/test_speed_lessons.py` (`BundleCmd`), `tests/test_work_kinds.py`.
- `CHANGELOG.md` «## Unreleased»; ADR последний `0034`, следующий `0035`.
