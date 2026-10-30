# Audit — read-only findings report

`/autopilot audit`, optionally with a focus: `/autopilot audit: security and performance`, «аудит», «Audit: Sicherheit». It replaces every other phase: no manifest, no spec, no tickets, no dashboard. The product is one verified report the owner can turn into a build later.

## The read-only contract

Binding on you and on every subagent; it beats any finding that «would take two lines to fix».

- **No edits, no commits, no stash, no installs, no network.** Reading the repository is the whole job. A finding is reported, never fixed.
- **Never run `ap.py`** — not `init`, not any other command. An audit creates no run, no `state.js`, no dashboard, no agent profiles, no hooks; the strict guard (`claude_agent_guard.py`) acts only during an unfinished strict run, so it never sees an audit.
- **The only file written** is the report, `.autopilot/audits/<YYYY-MM-DD>-audit.md` (create the folder; on a second audit the same day, `-2`). Nothing else: not `AGENTS.md`, not `PROGRESS.md`, not `.gitignore`, not memory.
- **Subagents get read-only tools:** Read, Grep, Glob, and Bash only for commands that change nothing — `git log`, `git show`, `git blame`, `git ls-files`, `ls`, `wc`. No package managers, no build, no `npm audit`/`pip-audit` (network), no test runs of their own.
- **Secrets:** a hard-coded key is a finding by file:line and kind (`STRIPE_SECRET_KEY`-style name), **never its value** — the redaction gate in `phases/1-manifest.md` runs over the report before it is written.

## 1. Before anything

Read `.autopilot/state.js` if it exists. `finishedAt` is `null`, or the file is unreadable → **an unfinished run is here: do not start.** One line: «Здесь незаконченная сборка Autopilot — аудит её не трогает. Напиши `/autopilot`, чтобы продолжить её, или закончи её сначала.» A finished run or no `state.js` → go on.

Record `git status --porcelain` (in a repository) — §6 compares against it.

Then one opening block, in the user's language, a hint and not a question:

```
Аудит: только чтение — ничего в проекте не меняю, не коммичу и не ставлю. Фокус: <фокус | весь проект>.
Отчёт будет в .autopilot/audits/<YYYY-MM-DD>-audit.md.
Основной расход — модель этого чата; для аудита хватает Sonnet (`/model`).
```

## 2. Recon — you, briefly

The inspection of `phases/0-preflight.md` §1, read-only: the stack (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`), the size (`git ls-files | wc -l`, lines of source roughly), the tests and how they run, `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`/`docs/adr/`, `git log --oneline -20` and the most-changed files (`git log --format= --name-only -200 | sort | uniq -c | sort -rn | head`). Ten lines of notes, kept in your context; no file.

**The existing test suite — run it once, yourself, only when all hold:** the command is documented by the project (`AGENTS.md`, `README`, a `test` script, a `Makefile` target); its dependencies are already installed (`node_modules/`, a venv, a built target — never install them); it needs no network, database, container or credential (no `docker compose`, no `DATABASE_URL`, no e2e against a URL); it does not deploy, migrate, seed or write outside ignored caches. Any doubt → do not run it, and say so under «Что не проверялось». Run it with the output to a temporary file outside the project; keep the result line (passed/failed/skipped). The explorers never run it.

## 3. Explorers — cheap, parallel, one lens each

Lenses: **correctness & edge cases** · **security** · **performance under real load** · **tests** (risky code with no test that could fail) · **dead & duplicate code** · **docs drift** (README/AGENTS.md vs the code) · **dependencies** (unused, duplicated, unpinned, a lock file out of step — from the repo only; a «known vulnerable version» from memory goes to «Что не проверялось» as a command for the owner to run).

**Scale to the project** — calibration, not a target: small (under ~5k lines) → 3 explorers with merged lenses (correctness+security · tests+performance · dead code+docs+dependencies); medium → 5; large (over ~50k) → 7, one lens each, each told which top-level zones matter most. A **focus** keeps only the lenses it names (plus correctness, which every audit needs); the rest go to «Что не проверялось».

**Route on the cheap tier**, never the main session's model: the `cheap` profile of `tools/model_router.py` (Anthropic `haiku`/`low`, OpenAI `gpt-6-luna`/`low`; restricted models never). Claude Code: the `Explore` agent (no Edit/Write tools) with `model` and `effort` set explicitly, all in **one message, in the background**; no `autopilot-…` profiles, no `isolation`. Codex: the cheap route with a read-only sandbox where the host offers one. If the host cannot select the cheap model for a subagent, do not let the workers inherit an expensive model quietly: say so in one line and work the lenses yourself, one at a time, at the small-project scale.

Each explorer gets, by path: **`prompts/audit.md`** (`skillDir` = this skill's folder), section «Разведчик», required reading; its lens(es) and the focus; your recon lines and the test result line, pasted; the zones to start from. Its return is capped there: **at most 12 findings, 25 lines, 2,500 characters** — a longer block is not read, ask again in one line.

## 4. Verification — one reviewer, strong tier

When every explorer is back: **one fresh subagent** on the `strong` profile (Anthropic `sonnet`/`high`, OpenAI `gpt-6.1-sol`/`high`), Claude Code `Explore` with `model` and `effort` explicit. It gets `prompts/audit.md`, section «Проверяющий», and every explorer finding pasted verbatim, numbered. It opens each cited place, **drops what the code does not confirm**, merges duplicates, and keeps a finding only with a **concrete failure scenario** — what input, from whom, what goes wrong. It returns at most 60 lines and 8,000 characters. Nothing it dropped reaches the report; nothing it did not see is added by you.

## 5. The report

Write `.autopilot/audits/<YYYY-MM-DD>-audit.md` from the verifier's return, in the user's language. Ids and checkbox lines exactly as below — the build reads `- [x] **A01**` (`phases/1-manifest.md`). Findings `A01…` numbered through all priorities; ideas `I01…`; every item a `- [ ]`.

```markdown
# Аудит <проект> — <YYYY-MM-DD>

> Только чтение: в проекте ничего не менялось. Фокус: <фокус | весь проект>.
> Разведчиков: <N> (<линзы>), находок: <M>, подтверждено проверяющим: <K>. Тесты: <результат | не запускались — почему>.
> Чтобы починить: отметь `[x]` то, что чинить, и напиши `/autopilot .autopilot/audits/<файл>`. Неотмеченное в сборку не попадёт.

## Сводка

<3–6 строк простыми словами: в каком состоянии проект, главный риск, с чего начать>

## Критично

- [ ] **A01** · `src/auth/session.py:42` — <что не так, одной фразой>
  - Почему важно: <последствие для владельца>
  - Сценарий: <какой вход, от кого, что получается>
  - Работа: S | M | L

## Важно

## Улучшения

## Идеи развития

- [ ] **I01** — <идея, одной фразой> — <зачем>

## Что не проверялось

- <линза, зона или команда, которую стоит запустить самому — почему не здесь>
```

A priority with nothing in it says «нет». **Critical** — data loss, a security hole, a crash on a normal path; **important** — wrong under realistic conditions, or a risk without a test; **improvement** — debt that slows the next change. Effort: S under an hour, M a day, L more.

## 6. Check, then hand over

`git status --porcelain` again: the only difference from §1 is the report. Anything else changed → say what, plainly, and do not delete or revert it yourself.

Then one short message: the counts per priority, the top one or two findings in a line each, the report path, and the bridge:

«Отметь `[x]` находки, которые чинить, и напиши `/autopilot .autopilot/audits/<файл>` — сборка возьмёт в работу только отмеченное. Для экономии: план на сильной модели, сборка — в новом чате на Sonnet (обычные два прохода).»

The report is not committed — it is the owner's to tick; the build's plan commit carries it.
