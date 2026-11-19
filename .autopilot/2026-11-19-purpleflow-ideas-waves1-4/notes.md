# Заметки об исследовании кода

Снято разведчиком 2026-11-19 (чтение, без запуска тестов). Номера строк сдвигаются при правках: перед правкой искать по имени.

## Ревью и ремонт
- `phases/6-review.md`: точечное ревью (`Ревью: да`, после коммита) и ревью ветки (стадия `review`); оси Manifest/Spec/Craft; `FINDINGS` → `ap.py add concerns`; `BLOCKING` → `phases/5-repair.md`; общее ревью: вердикты `FIX NOW` / `REPORT` / `DROP`, `FIX NOW` → один таск `F1`; Opus-ревьюер только при подтверждённой роли и диффе > 3000 (`OPUS_REVIEW_DIFF`), выбор — `ap.py agent-for reviewer --diff-lines N`.
- `prompts/review.md`: три режима «таск» / «ремонт» / «ветка», форматы ответа (ветка ≤ 40 строк, 4000 знаков).
- `phases/5-repair.md`: счётчики `repairs`/`retries` (лимит 2), `ticket NN repair --note` открывает блокер `B##`; `blocker resolve --id B01 --commit SHA --tests N/0 --note`; повторное ревью — только по правке, один раз на таск.
- `concerns`: верхний список `state["concerns"]` (`ap.py add concerns`), `tickets[].concerns`. Блокеры: `state["blockingFindings"]`, `open_blocker`, `blocker_ledger`, `cmd_blocker` (ap.py).

## Приёмка и отчёт
- Слепой агент — текст в `phases/8-final.md`; видит только `*-brief.md` и репозиторий. Запись: `ap.py blind checked=N matched=M --mismatch "…"` (`cmd_numbers`; `state["blind"]`, `blindRounds`).
- `cmd_finish`: блокеры, `landing_problems`, G3, переименование `--wip`, `spend_*`. Отчёт собирается по таблице секций в `phases/8-final.md`.
- Список `LISTS` (ap.py) — допустимые ключи для `ap.py add`.

## ap.py (≈4600 строк; искать по имени)
- Диспетчер `main()`; `fresh_state(a)` — начальное состояние (`mode`, `depth`, без проверки значений); `cmd_set` — разрешённые ключи `tier, baseCommit, briefFile, memoryFile, memoryOwner, skillDir, mode, depth`.
- `cmd_ticket`: статусы `TICKET_STATUSES`; `done` проверяет блокеры, тесты, коммит в HEAD; `route` для `F<n>`.
- `cmd_land` (ticket NN land): зона `split_paths(opt["zone"]) or tk["zone"]`; `allowed = [".autopilot", ".env.example"] + flying + --allow`; `outside` → код 2; `full_check_command` из «Полная проверка: `…`» в `interfaces.md`; `run_shell(check, 1800)`; `count_tests`; `commit_paths(files, msg, trailers)`; затем `cmd_ticket([i,"done"])`.
- `commit_paths` — единственное место коммита; `ticket_files(state, pattern)`; `parse_ticket(path)` читает `требования, зависит от, волна, зона, ревью, модель` (регулярка `FIELD`); `**Класс:**`/`**Риск:**`/`**Причина класса:**` читает `model_router.py` (`CLASS_RE`, `RISK_HEADER_RE`, `WHY_RE`, `plan_problems`, `assess_ticket`). Раздел «Критерии готовности»/«Приёмка» кодом не разбирается.
- `check_plan(state)` (G3) пропускает `F*`-таски; `publish_tickets`; `cmd_agent_for` падает с «профиль роли … не зарегистрирован — plan-models --apply в строгом прогоне», если нет `state["roleAgents"]["reviewer"]` / `state["repairAgent"]`, которые пишет только `plan-models --apply`; `phases/6-review.md` обещает, что в обычном прогоне печатается обычный ревьюер — код этого не делает.
- Схема: `state_io.ensure_schema_version` в `read_state`/`save`; `docs/autopilot/state-schema.md`.

## Прочие инструменты (`skills/autopilot/tools/`)
- `state_io.py`: `read_state_file`, `write_state_file`, `parse_state_text`, `ticket_fingerprint`.
- `worktrees.py`: `create(root, ticket, base)` (`git worktree add --detach .autopilot/worktrees/T<id>`), `land(root, ticket, base, zones)` (cherry-pick одного коммита), `finalize`, `main` (`--zone` повторяемый). Зависимости (`node_modules`) не копируются нигде.
- `scheduler.py`: `ACTIVE`, `zones_of`, `intersect`, `schedule`. `model_router.py`: `is_allowed_subagent_model(name, premium_ok=…)`. `agent_profiles.py`: `PERMANENT_ROLES`, `install_permanent`. `run_log.py`: `append`, `role_of`.
- Сторожевого таймера агента (молчание) нигде нет; есть только таймауты процессов (`run_shell`, git).
- `test_count.py`: маркеры `<!-- tests:count -->` в `AGENTS.md`, `README*.md`.

## Дашборд
`skills/autopilot/phases/dashboard-template.html`: `render(lang)`, `page(c)` собирает секции `mission/reqs/tasks/quality/models`; `quality` = `nextCard + mismatchCard + verdictCard + blindView + reviewView + …`; `dxTicker` (массив `parts`) и `c.stageNote` — места для строки «план: N из M»; подписи в обеих ветках I18N (ru/en). Потолок шаблона 450 КБ.

## Тесты
- 58 файлов `tests/test_*.py`; харнессы, копирующие `ap.py`, копируют `state_io.py`, `process_containment.py`, `gate_sign.py`, `run_log.py`, `dashboard_upgrade.py` и др. (`tests/test_ap.py`, `test_one_command.py`, `test_ap_escalation.py`). Новый `.py` рядом с `ap.py`, который `ap.py` импортирует, — добавить в эти харнессы.
- `tests/test_text_split.py`: `NORMAL_PATH_LIMIT`, перечень `EXTRACTED`/`MOVED_LINES` с sha256; новые тексты видов, чек-листа, уроков класть в **новые файлы** `phases/`/`prompts/`, а в обычный путь — не более одной строки-ссылки; имя нового файла должно быть в `SKILL.md`.
- `tools/run-tests.py`: `SERIAL`; полный прогон ≈ 10 мин последовательно.

## Документы
`docs/adr/`: занято 0001–0014 и 0016–0019; **0015 закреплён за R33 («dashboard-actions»)** — ADR этой сборки берут 0020 и далее. `docs/autopilot/measuring-cost.md`, `docs/autopilot/state-schema.md`. `CHANGELOG.md`: раздел `## Unreleased`.

## Исполнитель
`prompts/executor.md`: полная проверка из `interfaces.md` в конце, по ходу — один файл тестов; фразы «запускает только тесты своих изменений» нет.
