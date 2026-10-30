# Phase 4 — Plan

`ap.py stage plan`. Cut the spec into tickets, each built by its own subagent in a fresh context.

**Every ticket boundary is a cold start** — 60–80K tokens of context in a new repo, well over 100K in a large existing one, before a line is written, plus your own turns to launch and land it. **Fewer, denser tickets beat more, thinner ones** — but only down to what one context can hold. Measurements: `docs/autopilot/design.md`.

## Size — read from the volume of code, never from the length of the spec

**One executor builds about 3,000 changed lines, tests included** — past that its context gets heavy and every step costs more than the last.

**Estimate the volume first**, from the spec and, in existing code, from `notes.md`: screens, endpoints, tables, flows, and how much existing code each changes. One line to yourself — «~8K строк: чат ~3K, приглашения ~2K, лимиты ~1,5K, остальное ~1,5K» — then:

| Volume | Tickets | Tier |
|---|---|---|
| **up to ~3K lines** | **one** — one executor gets the whole spec and builds it in one fresh context. No waves, no point review | **T0** |
| ~3–6K | 2 | **T1** |
| ~6–18K | 3–6, one per ~3K | **T2** |
| ~18–36K | 7–12, one per ~3K | **T3** |
| more | **not allowed** — split into two runs | |

**T0 is the default for a list of edits in existing code** — eighteen fixes across a codebase are usually under 3K lines, however many files they touch; the whole-branch review checks the result. A `deep` spec for a landing page is still T0. State volume, tier and count in one line to the user; `ap.py set tier=T2`.

## How to cut

- **Each ticket is a narrow but complete path through every layer it touches** — data, logic, interface, tests. When it lands, something works end to end that did not before.
- **The shell, the schema, the shared primitives are ticket 01, alone.** Nothing parallelises with it.
- Groundwork that makes later tickets easy goes early. Tickets closing `R` go before tickets closing only `A`.
- Number from `01` in dependency order; each ticket names what it depends on.
- **The size test.** Merge neighbours that together stay under ~3K lines, even ones that would fly side by side — a little clock time for a whole cold start. Split only a ticket past ~3K lines, or one with a long debugging loop ahead (an unfamiliar integration).
- **The payback test:** its executor would spend more flying in than building → merge it into its neighbour. **The neighbour test:** under three acceptance criteria and the same files as an adjacent ticket → a checklist item there.
- **The merge pass**, mandatory, before any file is written: merge adjacent tickets on the same files, thin tickets with a natural parent, and chains where A alone demos nothing. 12 tickets for ~18K lines is T2 cut too thin. A wide change below is the one chain the merge pass leaves alone.

## A wide change — new beside old

In existing code a requirement can change **one shared thing that many zones use** — rename a field, change the money type, split a name, swap a library. A vertical slice never turns green on it (every untouched zone breaks), and one ticket for all of it overflows its executor. Cut it in three steps, each green on its own:

1. **Expand** — the new thing appears **next to** the old one, which keeps working: both fields, data copied and kept in sync; the new function, the old one delegating to it. `Ревью: да — фундамент`, `сильная`.
2. **Migrate** — one ticket per zone moves its callers to the new thing; unmoved zones stay green, and tickets on different zones fly in one wave. Criterion: «в `<зона>` не осталось обращений к `<старое>`».
3. **Contract** — once nothing calls the old thing, it is removed. Dropping a column with user data is `Ревью: да — удаление данных`.

Every ticket of the chain carries the same requirement. Use it only when the change crosses more zones than one ticket owns; a shared thing used in one zone is an ordinary ticket, and a new project never needs it.

## Waves and zones

**`wave = 1 + max(wave of what it depends on)`**, no dependencies → wave 1. Then **split each wave by zones**: two tickets writing the same files cannot fly together — the later one moves to the next wave. Every ticket names its **zone** — the directories and modules it owns, tests included. Waves are *discovered* in the dependency graph, never manufactured by splitting a ticket; a wave of one is normal. A written wave number is never renumbered — a real re-cut is told to the user in a line.

## Review and model — decided per ticket, here

**Review** — whether the ticket gets a point review after its commit (`phases/6-review.md`). It never holds up the build. **Every ticket is reviewed once at the end anyway** with the whole branch; a point review is only for what is worth catching earlier.

- `да — фундамент` — ticket 01 when later tickets build on it, and the expand step of a wide change. Nothing else.
- `да — <риск>` — a ticket whose **own code** is: sign-in, passwords, sessions, 2FA; keys and secrets; money; deleting or migrating user data. Only checking permissions inside an ordinary feature is not a risk ticket — marking all of those is how a run reviews 12 tickets of 15.
- `нет` — most tickets. **At T0 the one ticket is `нет` too**: the whole-branch review is its review.

**Model AND reasoning effort are automatically calculated for EVERY ticket in Phase 4 (planning), not guessed by the executor at launch.** The legacy header `**Модель:** сильная/обычная` is descriptive only and must not override it. The provider (`openai` for Codex, `anthropic` for Claude Code) comes from the actual host, not from the orchestrator's model.

After `ap.py tickets` and `ap.py check-plan`, compute the whole ticket matrix **with one command**:

```bash
# Advisory plan, no model calls, no native profiles or host entitlement claims:
python3 .autopilot/ap.py plan-models --provider openai

# Only after host capability discovery genuinely supports model + Effort selection:
python3 .autopilot/ap.py plan-models --provider openai \
  --capabilities .autopilot/model-capabilities.json --apply
```

- The deterministic `model_router.py` scores algorithm (25), coupling (20), uncertainty (15), context (15), tests (15), risk (10), picks `cheap`/`balanced`/`strong` and the **exact model + reasoning Effort** from the provider policy; critical risk can force `strong`. See [adaptive routing](../../../docs/autopilot/model-routing.md).
- `plan-models` saves `plannedRouting` on each ticket and returns JSON: ticket, category, score, model, Effort, reason, `ready/blocked`. Without capabilities it is **advisory only**: no agent launched, no false host verification. With `--apply`, **all** tickets must be supported **and the latest G3 `check-plan` snapshot must match the current requirement contract, ticket bytes and manifest statuses**; a missing, failed or stale G3 blocks application before any profile is created. Re-run `tickets` / `check-plan` and inspect changes — never bypass the guard.
- The applied route is an authorized **configuration**, not evidence of an actual child/model/Effort; Phase 5 still checks profile hashes, runtime dispatch capabilities and the exact selected agent. On an unsupported GUI, **do not use `--apply` as a workaround**; use [`--sequential-host`](../../../docs/autopilot/sequential-host.md) and do not claim named subagents.
- No automatic Astra/Fable/Opus, no inheriting the expensive parent model, no model call or paid API tokens during the plan. Changed tasks require republishing tickets, rechecking G3 and recalculating routes; retries with changed risk/complexity require reapproval.
- Rebalance independent ticket sizes against cold-start cost; one ticket does not imply several reviewers.

## The ticket file

`.autopilot/<dir>/tickets/NN-<slug>.md`. `ap.py` reads the header lines — keep their names:

```markdown
# 03 — Приём заявки от клиента

**Требования:** R01, R01.1, A01
**Зависит от:** 01, 02
**Зона:** `src/bot/` · `tests/bot/`
**Волна:** 2
**Ревью:** нет
**Модель:** обычная

## Что должно заработать

Клиент пишет боту, отвечает на три вопроса — что сломалось, адрес, телефон —
и получает подтверждение с номером заявки.

## Из брифа, дословно

> «принимает заявки на ремонт техники»

## Разделы спецификации

Истории 1–5, Решения §2 и §4.

## Критерии приёмки

- [ ] Диалог из трёх шагов доходит до подтверждения
- [ ] Номер заявки уникален и виден клиенту
- [ ] Незаполненный телефон даёт понятную ошибку, а не падение
```

- **The verbatim brief quotes are load-bearing** — they guard a fresh context against reinterpretation, and the point reviewer judges the Manifest axis from them.
- **Every criterion is checkable and false at the commit the executor starts from** — the executor proves each one red before building it (`prompts/executor.md`).
- No file paths or code snippets except a structure prose states worse — a schema, a state machine.
- `Зависит от` lists ticket numbers only — `01, 02`, or `—`.

## Before the first ticket flies

**`interfaces.md` carries more than Phase 3's boundaries.** Add the project rules an executor cannot derive: stack and versions; how to install, run, and **one check command** — tests, types and lint together — plus how to run a single test file (ticket 01 creates the check command if the project has none); what must not be touched. **Ticket 01 installs every dependency «Решения по реализации» names**; any other comes back as `BLOCKED` (`phases/5-repair.md`).

## Gate G3, publishing, and the plan commit

`python3 .autopilot/ap.py tickets` publishes every ticket to the dashboard and moves their manifest rows to `in-ticket`; `python3 .autopilot/ap.py check-plan` is the gate. It checks both directions — every live requirement in some ticket, every ticket tracing to a requirement — and that every ticket has a zone and a wave, waves respect dependencies, and no two tickets in one wave write the same zone. Each `!` line is a plan defect: fix the ticket files and run both again. A passing G3 binds the exact wording/rationale of manifest requirements and every planned ticket file; if they change afterwards, a fresh `check-plan` invalidates earlier G1/G2/G4 approvals: inspect the changed specification, redo coverage and blind acceptance — a renewed G3 alone is **not** permission to finish.

**Then the plan commit** — the run's first, the base every later diff is measured from. Run the redaction gate over `.autopilot/` (`phases/1-manifest.md`), then commit exactly the files this skill wrote so far — never anything else in the tree:

```bash
git add -A -- .autopilot .gitignore AGENTS.md CLAUDE.md .env.example && git commit -qm "Autopilot: план сборки" --trailer "Autopilot-Run: <папка>" -- .autopilot .gitignore AGENTS.md CLAUDE.md .env.example \
  && python3 .autopilot/ap.py set baseCommit="$(git rev-parse --short HEAD)"
```

Omit from both lists any missing file, and the memory file if it is the user's own. `<папка>` is `dir` without `--wip`, the same in every commit of the run.

A ticket that exists only in the dialogue is not a ticket — the user sees a summary of files already on disk.

## Showing the plan

**Parallelism gets one line, and only if true**: «6 тасков в 4 волны, часть пойдёт параллельно».

- **semi, interview** — one screen, one plain line per ticket saying what the user can do when it lands, then «Показываю план и начинаю. Скажи "стоп", если что-то не так» — and start. Never promise a countdown you cannot hold.
- **full** — the same screen as a notification.
- **manual** — a gate: `ap.py ask plan`, then technical detail, granularity and order discussed, an explicit «ок» before Phase 5.

## Strict Claude Code run — register the agents, then a new chat

Claude Code reads `.claude/agents/` and the project hooks at session start; a profile created later in the same session answers «Agent type not found», and strict routing allows no fallback (T16). So a run with `strictRouting` on Claude Code (provider `anthropic`) ends Phase 4 here, once the plan stands (manual: after the «ок»; semi: instead of «и начинаю»):

1. Write `.autopilot/model-capabilities.json` from what this host really offers (`docs/autopilot/claude-code.md`), then **one** call creates every profile the run will use — an executor per ticket plus the run's reviewer, blind-acceptance and read-only explorer (`state.js` → `roleAgents`) and one repair executor for the fix tickets the whole-branch review may create (`state.js` → `repairAgent`): `python3 .autopilot/ap.py plan-models --provider anthropic --capabilities .autopilot/model-capabilities.json --apply`. It also marks the `plan` stage done. A blocked route is a stop, not a reason to skip a role.
2. Both hooks: `python3 .autopilot/claude_agent_guard.py --install-hook --root .` and `python3 .autopilot/claude_attest.py --install-hook --root .`.
3. No new commit — `.claude/` and the role brief stay out of the plan commit. `ap.py ask stop --note "новый чат: агенты зарегистрированы"`, then, in the user's language, as a **required** step that replaces the cost hint below:

   «Агенты сборки зарегистрированы, но Claude Code видит их только в новой сессии. Открой новый чат в этой папке (дешевле на Sonnet) и напиши `/autopilot` — сборка продолжится с этого места. Здесь сборка не пойдёт.» / "The build agents are registered, but Claude Code only sees them in a new session. Open a new chat in this folder (Sonnet is cheaper) and type `/autopilot` — the build resumes from here. It cannot run in this chat."

In every mode, full included, this is a stop: without the new session the build cannot dispatch a single agent — say so plainly, never carry on with `general-purpose`, a built-in agent, another ticket's profile or `--sequential-host`.

**Cost hint — plan here, build in a fresh chat (only on a strong model, never at T0, never in a strict Claude Code run).** At T0 — one ticket — there is no hint at all, not even a mention of a new chat; a strict Claude Code run gets the required step above instead. One line after the plan screen, in the user's language. **manual** (offer, answered by the «ок»): «План готов. Дешевле собрать в новом чате на Sonnet в этой же папке — выбери модель, напиши `/autopilot`, сборка продолжится с этого места. Или продолжим здесь.» / "Plan ready. Cheaper: open a new chat in this folder on Sonnet and type `/autopilot` — it resumes at the build. Or continue here." **semi, interview, full** (information only, never a new stop or wait): «Дешевле собрать на Sonnet: скажи «стоп», открой новый чат в этой папке на Sonnet и напиши `/autopilot`.» If the user takes it, this chat stays idle — one writer per run (`phases/0-resume.md`).
