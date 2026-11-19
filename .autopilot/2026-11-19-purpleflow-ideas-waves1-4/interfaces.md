# Интерфейсы и правила проекта

## Правила проекта (из «Договорились» прошлой сборки, дословно по сути)

- «пуш мэйн» (2026-11-16): `main` отправляется в `origin` — только по слову пользователя.
- Ключ подписи гейтов вне проекта (`~/.autopilot/gate.key`), на Windows под DPAPI.
- Opus — только по подтверждению пользователя (в этой сборке выключен); Fable не допускается ни под каким написанием.
- Возврат упавшего таска и сдача с отказами — только цитатой пользователя; `dropped` ставит только пользователь.
- Жёсткий минимум Claude Code 2.1.295; принятое ограничение `bash_gate` не чинить.
- Маршрут таска задаёт планировщик (`**Класс:**`, `**Риск:**`, `**Причина класса:**`).
- Адрес с токеном печатает только `ap.py url`; в чат не вставлять.
- `.claude/settings.json`, `ROADMAP-claude-code-2026-11.md`, `BRIEF-2026-11-orchestrator-spend.md` в корне не коммитить.
- ADR: `0015` закреплён за R33; новые ADR этой сборки — с `0020`.
- Тесты, копирующие `ap.py` в харнесс, копируют и `state_io.py`, `process_containment.py` (и `run_log.py`) — **и каждый новый модуль, который `ap.py` импортирует**.
- Исполнители коммитят `git commit --only <файлы зоны>`, без `git stash`.
- Новые тексты — в новые файлы `phases/`/`prompts/`; обычный путь (`test_text_split.NORMAL_PATH_LIMIT`) не растёт, имя нового файла добавлено в таблицу `SKILL.md`.

Полная проверка: `python -m unittest discover -s tests`

## Команды-генераторы

| Имя | Команда | Файлы |
|---|---|---|
| tests-count | `python skills/autopilot/tools/test_count.py --write` | `AGENTS.md`, `README.md`, `README.ru.md`, `README.de.md` |

## Границы, решённые в спецификации

Все модули — `skills/autopilot/tools/`, только стандартная библиотека, имена на английском, тексты и сообщения пользователю на русском.

### `plan_items.py` — пункты плана (T01)
Владеет: разбор файла таска и вердиктов плана → факт.
- `parse_items(ticket_text: str) -> list[str]` — строки `- …` из раздела «Критерии готовности»/«Приёмка»/«Acceptance» (первый найденный), без пустых; нет раздела → `[]`.
- `build_plan_fact(items_by_ticket: dict[str, list[str]], verdicts: list[dict]) -> dict` — `{"items": [{"id": "T02.1", "ticket": "02", "text": str, "status": "сделано"|"частично"|"не сделано", "evidence": str}], "done": N, "total": M}`; пункт без вердикта или с пустым `evidence` → `не сделано`.
- Скрывает: форматы заголовков.
Команда `ap.py plan-fact list` (печатает пункты с id) · `ap.py plan-fact record --verdict "T02.1 | сделано | файл:строка" …` (пишет `state["planFact"]`, `частично`/`не сделано` → `concerns` строкой `план: T02.1 — <статус> — <текст>`) · `ap.py plan-fact show` (`план: N из M`).

### `review_checks.py` — проверки ревью (T02)
- `CHECKLIST: tuple[str, ...]` — шесть пунктов: `инварианты`, `токены и деньги`, `статусы и переходы`, `сбой посередине`, `гонки`, `права и подписи`.
- `missing_checklist(report_text: str) -> list[str]` — пункты без строки-ответа `<пункт>: …`.
- `bypass_lines(diff_text: str) -> list[str]` — добавленные строки с `@unittest.skip`, `skipTest`, `pytest.mark.skip|xfail`, `--no-verify`, `# noqa` в новых местах, а также удалённые строки с `assert`/`self.assert*` без добавленных замен.
Команды: `ap.py check-review-report --file ФАЙЛ` (код 1, если есть пропуск) · `ap.py check-bypass [РЕВИЗИЯ..РЕВИЗИЯ]` (печатает, код 0; только сигнал) · `ap.py blocker confirm --id B01 --verdict confirmed|not-confirmed --quote "…"` (цитата обязательна; `not-confirmed` закрывает блокер состоянием `downgraded` и добавляет в `concerns` «не подтверждено вторым проходом: <условие>»).
`ap.py agent-for reviewer|repair` в обычном (не строгом) прогоне печатает `autopilot-reviewer`/`autopilot-executor` (профиль маршрута из `plan-models`, без `--apply`); Opus — по-прежнему только при подписанном подтверждении роли.

### `land_check.py` — проверка перед влитием (T03)
- `preflight(root: str, start_head: str|None, base_commit: str, zone: list[str], ticket: str, active_zones: dict[str, list[str]]) -> dict` — `{"ahead": int, "foreign_files": [..], "neighbors": [{"ticket": "03", "files": [..]}], "unsupported": str|None}`; не меняет репозиторий (`git rev-list --count`, `git diff --name-only`, пересечение путей).
- `problems(report: dict) -> list[str]` — готовые сообщения с командой «что делать».
- `ticket NN start` пишет `tk["startHead"]` (HEAD на момент старта).
`cmd_land` и `worktrees.py land` вызывают `preflight` до слияния; непустые `problems` → код 2. Проект в подпапке репозитория: `unsupported` непусто → предупреждение, не отказ. `--allow` без изменений; новое `--include a,b` = разрешить и закоммитить (новые/изменённые файлы вне зоны).

### `kinds.py` — виды работы (T04)
- `KINDS = ("quick", "bug", "task", "refactor")`, `DEFAULT_KIND = "task"`, `QUICK_MAX_TICKETS = 1`, `QUICK_MAX_REQUIREMENTS = 3`.
- `normalize(value: str|None) -> str` — `None`/пусто → `task`, вне списка → `ValueError`.
- `plan_problems(kind, tickets) -> list[str]` — для `check-plan`: `quick` > 1 таска; `bug` без ровно одного таска `**Вид:** воспроизведение` без зависимостей; `refactor` с зоной таска в тестах без `**Правка тестов:**`.
- `land_problems(kind, ticket, changed_files, tracked_tests, redproof) -> list[str]`.
Команды: `ap.py init --kind …`, `ap.py set kind=…`, `ap.py ticket NN redproof --command "…"` (запуск через `run_shell`; код 0 → отказ «тест не красный»; иначе пишет `tk["redproof"]`).
`ap.py ticket NN baseline --command "…"` (для `refactor`: код 0 обязателен, пишет `tk["baseline"]`; `land` в `refactor` без него отказывает).
`ap.py ... --by-user "<цитата>"` снимает отказ `land` по `bug`, остальные отказы цитатой не снимаются. `model_router` от `kind` не зависит.

### `silence.py` — молчание агента (T05)
- `silent_agents(subagents_dir: str, limit: int, now: float|None = None) -> list[dict]` — `{"file": str, "idle": int}` для `agent-*.jsonl`, не менявшихся дольше `limit`.
- `DEFAULT_LIMIT = 600`, `limit_from_env()` читает `AUTOPILOT_SILENCE_SECONDS`.
Команда `ap.py silence [--limit СЕК] [--transcript ПУТЬ]` — печатает тихих (код 3, если есть); `ap.py` сам агента не останавливает: останавливает оркестратор (`TaskStop`). `ap.py stage` печатает предупреждение, если стадия идёт дольше 60 минут.
`ap.py ticket NN bundle` — одно сообщение: хвост упавшей проверки (`tk["lastCheck"]`, пишется в `land` при красной проверке), открытые блокеры таска, замечания таска.

### `worktrees.link_deps(root, worktree) -> str` (T05)
Копирует `node_modules`, если он есть в `root`, lock-файлы (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`) побайтно совпали и ОС не Windows (`cp -c` на macOS, `cp --reflink=auto -r` на Linux); возвращает `copied` | `skipped: <причина>`; ошибка копирования — `skipped`, прежний путь.

### `lessons.py` — уроки и профиль (T06)
- `LESSONS_LIMIT_BYTES = 2048`, `DEFAULT_MAX = 5`.
- `check_text(text) -> str|None` — причина отказа: секрет (шаблоны из `phases/1-manifest.md`), абсолютный путь вне проекта (`C:\…`, `/Users/…`, `/home/…`), перевод строки.
- `add(path, items, max_items=5) -> list[str]` — дописывает `- ДАТА — текст`, отброшенные `check_text` возвращаются списком причин.
- `render(path, limit=2048) -> str` — новые первыми, влезает в лимит, старое выпадает; нет файла — пусто.
- `drop(path, n) -> bool` — удаляет n-ю строку (1 — самая новая).
- `candidates(state, max_items) -> list[str]` — из `concerns`, тасков с `retries`/`repairs` > 0 и закрытых как `downgraded`/не подтверждённых.
- `profile_text(root) -> str`, `refresh_profile(root) -> bool` — `.autopilot/profile.md` (команды из «Полная проверка» и таблицы «Команды» в `AGENTS.md`, стек по `pyproject.toml|package.json|go.mod|Cargo.toml`, «Подводные камни» — до 15 строк); пишет, только если текст изменился.
Команды: `ap.py lessons check` (код 1, если в файле есть секрет или путь) · `ap.py lessons candidates [--max N]` · `lessons add "…" …` · `lessons show` · `lessons drop N` · `profile refresh`. `finish` вызывает `profile refresh` и печатает подсказку про `phases/9-lessons.md`; `init` печатает `уроки: N строк` и путь, когда файл не пуст; `prompts/executor.md` велит читать `.autopilot/lessons.md` и `profile.md`.

## Что построили закрытые таски

—

### Построено таском 01
`plan_items.parse_items/parse_verdict/build_plan_fact`; `review_checks.CHECKLIST/missing_checklist/bypass_lines`; команды `plan-fact list|record|show`, `check-review-report --file`, `check-bypass [A..B]`, `blocker confirm --id --verdict --quote` (статус блокера `downgraded`); тексты `prompts/review-checklist.md`, `prompts/confirm.md`, `phases/8-plan-fact.md`. Не сделано: `ticket NN land` не печатает сигналы обхода — переносится в таск 02.

### Построено таском 02
`land_check.preflight/problems/head/tracked_files/diff_text`; `kinds.normalize/of_state/is_test_path/plan_problems/land_problems`; `worktrees.land(..., start_head, active_zones)`; `ap`: `init --kind`, `set kind=`, `ticket NN redproof|baseline --command`, `land --include`; поля тасков `startHead`, `redproof`, `baseline`, `repro`, `testsEdit`; тексты `phases/kind-{bug,refactor,quick,auto}.md`; `docs/adr/0020-work-kinds.md`.

### Построено таском 03
`silence.silent_agents/limit_from_env/long_stages`; `worktrees.link_deps`; `lessons.check_text/add/render/drop/candidates/profile_text/refresh_profile`; команды `ticket NN bundle`, `silence`, `lessons candidates|add|show|drop|check`, `profile refresh`; тексты `phases/5-parallel.md`, `phases/9-lessons.md`. Удалённый вручную урок не возвращается за счёт `.autopilot/lessons.md.seen` (хеши).
