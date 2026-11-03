# Заметки по коду (разведка, только чтение)

Инструменты — `skills/autopilot/tools/*.py`, тесты — `tests/*.py` (unittest, `python3 -m unittest discover -s tests`), CI — `.github/workflows/python-tests.yml` (ubuntu+windows × py3.11/3.13). Копии инструментов в `.autopilot/` git не отслеживает: **править только `skills/autopilot/tools/`**. Инструменты копируются в проект списком из `phases/0-instruments.md` — новый модуль нужно добавить в этот список.

## state.js
- `ap.py:64` STATE, `:66` LOCK; `:103 locked_state(timeout=10)` (только в `__main__` `:2342`; `--stop-now` идёт без неё); `:138 read_state()` (срезает `window.STATE =`, битый JSON → `die()`); `:151 save(state)` (rev++, пишет `.tmp`, `os.replace`, без повтора).
- `controller.py:27 read_state(root)` (ControllerError при symlink/нет префикса/нет tickets); `claude_agent_guard.py:17 read_state(root)` (None при любой ошибке → deny); `spend_guard.py:49 usage_summary` (свой разбор); `codex_dispatch.py:28 load_state` (его берёт `worker_outcome.py:31 inspect`).
- `offline_supervisor.py:74 replace_with_bounded_windows_retry(src,dst,*,windows=None)`: 12 попыток, повтор при WinError 5/32, пауза 0.01–0.05 с; сейчас только для receipt-файлов.
- Тесты: test_ap.py:201–243, test_controller.py:156, test_spend_guard.py:94, test_claude_agent_guard.py:255–293, test_offline_supervisor.py:28/55/71. `locked_state` без теста.

## init --force
- `ap.py:891 cmd_init`; `:899–901` старый state, без finishedAt и без `--force` → die; `:903–909` если папка `old["dir"]` есть — `git -C .autopilot mv -f state.js <dir>/state.js`, иначе `os.replace`; note «прошлый прогон убран в архив». Папки нет → архива нет, note нет, `save` `:917`.
- Тесты: test_ap.py:230, :236; `--force` на живом прогоне и без папки не покрыты.

## worktrees
- `worktrees.py:35 safe_target`, `:145 finalize(root,ticket,base,zones,passed,failed)` (зоны `:156–167`, набор путей = diff + diff --cached + ls-files --others `:185–190`, проверка зон `:196–202`), `:213 land(root,ticket,base)` (cherry-pick -x одного коммита, без проверки зон), `:111 find_landing`, `:234 remove`.
- `worker_outcome.py:27 inspect` — дубль логики путей/зон (`:64` три git-команды, `_safe_zone :13`).
- `ap.py:1664 cmd_worktree`, ветка land ~`:1800–1835`; `verified_host_required :1097` → `test_evidence.check`, иначе `tests_pair` (`:884`) по тексту `--tests N/M`.
- Тесты: test_worktrees.py:58/71/81/94/105/146; отдельного теста на worker_outcome нет.

## model_router / guard
- `model_router.py`: WEIGHTS `:14`, DEFAULT_POLICY `:22` (restricted: openai gpt-6-astra; anthropic fable, claude-fable-5; critical-тиры `:34`,`:40`), `assess_scores :116` (risk≥8 → минимум balanced `:126`; risk≥10 или algorithm≥20 → strong; оба → critical `:130–131`), `assess_ticket :135` (словари important `:143`, hard `:147`, vague `:150`), `choose_route :161`, префиксный запрет `:190–193` (anthropic: fable, claude-fable, opus, claude-opus).
- `claude_agent_guard.py:88–89` — дубль списка premium (fable, claude-fable, opus, claude-opus) + startswith. `:45 decision(payload, root)`; нет state.js → ok; битый → deny `:56`; strict и без finishedAt → проверки профиля, модели, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, capabilities, `routing.verified :133`, sha256 профиля == profileSha `:141`. `:156 install_hook` (PreToolUse matcher `Agent|Task`, onFailure block, deny `Agent(fork)`).
- `claude_attest.py:27 record` (строка в `.autopilot/attestations.jsonl`, без подписи), `:70 install_hook`.
- Тесты: test_model_router.py (RouterTests :14). **Дефект тестов:** одноимённые методы в одном классе затеняют первые копии — partial_profile_override (:117/:203), custom_restricted_list (:134/:220), policy_must_reject (:147/:233), default_policy_not_mutated (:170/:256), direct_policy_whitespace (:181/:267). test_claude_agent_guard.py:73 и др.

## retry_policy
- `retry_policy.py:30 classify` (casefold, срез `[:12000]` `:34`; порядок security → environment → dependency → requirements → tests → reasoning), `:41 decide`, `:62 main`. Тесты test_retry_policy.py:11–36; срез и порядок не покрыты.

## test_evidence / process_containment
- `test_evidence.py:197 run_cargo` (subprocess.run cargo test --frozen …), `:251 verify()` (`sys.executable -B -m unittest -q suite`), `:215 verify`, `:270 check`. Тесты test_test_evidence.py, test_cargo_evidence.py.
- `process_containment.py:70 OwnedJob`: Windows — Job Object; POSIX — ничего (`mode "posix-session-only"`, assign/terminate пустые; docstring обещает killpg, которого нет). Единственный вызов — `offline_supervisor.py:266`.

## dashboard_upgrade
- `dashboard_upgrade.py:75 upgrade`, `:82` бэкап в `tempfile.gettempdir()/autopilot-dashboard-backups` (mkdir без mode, без очистки), `:88–91` имя `<slug>-<UTC>-<sha12>.html`, режим "x". Тесты test_dashboard_upgrade.py:33/46/52/60.

## Документы и CI
- STATUS.md:1–8 («2.3 handoff», current v2.3.0); SKILL.md:8 = 2.6.0; CHANGELOG top = 2.6.0; test_documentation_locales.py:85 проверяет 2.6.0 и симметрию заголовков трёх README (одинаковое число ## и ###).
- README×3: строка ~31 `py -3.13 … execution sequential-host`, ~35 «2.3.0 — Codex limited release», ~72–73 dev-заметка про `<HOST>`/Junction.
- SKILL.md:6 allowed-tools: `Bash(python .autopilot/ap.py *)`, `python3`, `py -3`. Доки с `py -3.13`: worktrees.md:23–28/83–87, controller.md:13–15, README:31. test_skill_allowed_tools.py: правило есть, начинается с `Bash(`, содержит `.autopilot/ap.py`, нет `Bash(*)`.
- model-routing.md:55–62 — таблица без critical; текст «risk 10 forces strong» не отражает risk≥8 → balanced.
- CI `:24–25` Syntax check: `compileall -q skills/autopilot/tools tests`.
