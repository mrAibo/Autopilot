# Phase 5 — Build

`ap.py stage build`. Where the code gets written. **Identical in all four modes, and hands-free**: manual buys control over *what* gets built, not over each edit.

Then read `5-host-claude.md` if running in Claude Code, `5-host-codex.md` if in Codex.

## One ticket, one subagent, one fresh context

**Without native named agents (`--sequential-host`):** read `5-sequential-host.md`; the "you dispatch" rule below does not apply as written there.

Never two tickets in one context — accumulated context is what breaks long sessions. At T0 the one ticket goes to one executor like any other.

**You dispatch; you do not build.** Your keyboard reaches `.autopilot/**`, the memory files, `.gitignore`, `.env.example`, and git (`add`, `commit`, `status`, `--stat` — never the diff). Every other file is written by someone whose context dies with the ticket. This is rule 5, and it beats «тут две строки» and «исполнитель не смог, доделаю сам»: a diff you read at ticket 02 is still in your never-refreshed context at ticket 08.

## What an executor gets — paths, not contents

| | |
|---|---|
| `prompts/executor.md` | by path (`skillDir` in `state.js`), **required reading before the first edit** — the testing contract, what is never allowed, the return format |
| its ticket | by path; it carries the verbatim brief quotes |
| the spec sections the ticket names | `spec.md` by path **and section headings** — not the whole spec, not pasted |
| `interfaces.md` | by path, read first |
| `notes.md` | by path, in an existing codebase |
| `context-pack.md` | by path, when the scout wrote one (`phases/3-spec.md`); the executor reads it first and reads the source itself for anything it skips |
| `reference.md` | by path, when the ticket builds something the user will look at |
| the check command and how to run one test file | from `interfaces.md` |
| its zone, and what it must not touch | zones of tickets flying beside it included |
| credentials | variable **names**, never a value |

**Ordinary Claude Code run: the executor is `autopilot-executor`**, with the ticket's `model` and `effort` passed in the call every time — the profile carries neither, and without them it takes the main session's model. «Agent type not found» → `general-purpose`, one line to the user, never a stop (`5-host-claude.md`).

Never paste what it can read: that pays twice and stays in your context. Every rule the executor must follow travels in its prompt or in `prompts/executor.md` — a rule only in a phase file does not exist for the one writing the code.

**Strict routing, isolated tickets, host controller:** read `5-strict.md` before the first ticket — test evidence, route and profile checks before every spawn, controller, worktree lifecycle. An ordinary run takes each ticket's model and effort from `plan-models` (Phase 4).

OpenAI default: Luna for cheap/balanced, Sol for strong; Anthropic default: Haiku for cheap, Sonnet for balanced/strong. Restricted Astra/Fable never spawn automatically; the main session's model must not leak into subagents. If this host cannot independently choose the model or provide verified capabilities, **stop delegation and report the blocker**. A retry on a stronger model needs a new approved route — the one exception is a Haiku ticket back with red tests after its first retry: `ap.py ticket NN retry --cause tests --escalate` moves it once to the registered Sonnet executor (`docs/autopilot/retry-policy.md`); missing dependencies, access or ambiguous requirements are not model-strength failures.

**Dependencies.** Ticket 01 installs everything the spec's «Решения по реализации» names. A later ticket needing something else returns `BLOCKED` with its name; if it fits a decision already made, add it to «Решения» and relaunch that ticket with permission to install exactly that — the manifest and lock files join its commit — and fly nothing else that installs meanwhile.


## Waves

**Before each wave, read the scheduler JSON:** `python .autopilot/ap.py schedule --max-parallel 2`. It weighs dependencies, zone overlaps, in-flight executors, checkout reservations, verified routing and the token threshold. Follow each `selected[]` object's `action` (route/prepare/start); never assume the scheduler spawned an agent. `selected[].cwd` is the required executor cwd for prepared isolated tasks. After an agent lands, call `schedule` again to refill only free capacity. Never launch a task whose `blocked[]` entry lists unresolved dependencies, overlaps or budget limits.

**Launch a whole wave in one message, one subagent call per ticket, in the background** — two calls in two messages run serially and throw the planned parallelism away.

- **At most two in flight by default**; three only if explicitly permitted by the verified policy and truly independent. A wave of five normally goes out as two, two, one. A point reviewer writes nothing and does not count.
- **Zones disjoint** — rechecked at launch; same files → serialise. When in doubt, serialise.
- **A wave is not a barrier.** When a ticket returns, first launch the next ticket whose dependencies are all committed, then process the one that landed.
- **A dependent never launches on an uncommitted parent.** A parent in `review` is committed (only its review is running): `ticket MM start` passes; `ticket MM done` still waits until the parent is `done`.
- `ap.py ticket 02 03 start` goes **before** the launch — one call for the whole wave, **in the same message as the Agent calls**: Bash first, the launches after it.
- **One event, one message.** Every call re-reads your whole context (at 200K, about a small subagent's first steps). The `ap.py` mark, the commit, the next launch and the line to the user go out together — never a call that only marks, then one that only launches.
- **Waiting is ending your turn** — a background subagent wakes you. Never spawn an agent or loop just to wait.

**Legacy shared-tree mode (sequential strongly preferred).** Parallel executors share the checkout, each touching only its zone (and `.env.example`); you commit by zone. A check failing **only in files of zones still being written** is a neighbour's unfinished work: the ticket may land on its own tests green, and the full check reruns when the neighbour lands.

## The return contract

Required in the prompt, not suggested — without it you cannot update anything. The exact format is «Что вернуть» in `prompts/executor.md`: `STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`, then `FILES`, `TESTS` (check → result, count before), `REDPROOF`, `INTERFACES`, `REQUIREMENTS` (`R01 done | R01.1 placeholder`), `COMMIT`, `CONCERNS`, `BLOCKERS`.

**Hard cap: 15 lines and 1,200 characters — no code, no diffs, no file dumps, no account of the work**; details stay in files and commits. A longer block is not read: ask for it again in one line — an essay stays in your context for every remaining turn.

## After each ticket

In this order:

1. **Read the contract and its status.** No block → the ticket is not finished; ask for it. `BLOCKED` or `NEEDS_CONTEXT` → `phases/5-repair.md` now. A `CONCERNS` line saying the plan does not hold — a data model, an interface, two requirements colliding — goes to `phases/5-repair.md` too. Two `NEEDS_CONTEXT` in one run mean the tickets are too thin across the board.
2. **Append its `INTERFACES` to `interfaces.md`** — you, never the executors. Two returns claiming one interface is a plan defect: keep the one that fits, re-cut the other.
3. **Land it — one call:**

   ```bash
   python3 .autopilot/ap.py ticket 03 land --message "T03: приём заявки" --requirements R01,R02
   ```

   In order: nothing changed outside the ticket's zone (`.autopilot/`, `.env.example` and zones still in flight excepted; `--allow path` for a file that is not the ticket's), the full check from `interfaces.md` («Полная проверка») with its tests counted, one commit of only the zone with the `Autopilot-Run` and `Requirements` trailers, then `ticket 03 done --tests N/F --commit SHA`. One commit per ticket is the user's rollback points; the trailers make history searchable (`git log --grep="R02"`; `Autopilot-Run` is the run folder without `--wip`). `--zone a/,b/` replaces the zone of the ticket file; `--placeholder R05` for each row reported as a stub. Success is up to five lines; compare its count with the contract — a `DONE` that added criteria and no tests is a дозапрос. A red step — a file outside the zone, a red check, zero tests, an output it cannot count, nothing to commit — is one to three lines, exit code 2 and no commit: a stray file is a дозапрос (put it back or say why), red goes to `phases/5-repair.md` and nothing is repaired by you. An isolated run refuses: it keeps `worktree NN verify`, `finalize`, `land`, then `ticket NN done`.
4. **Point review, if the ticket says `Ревью: да`**, or the contract reports one of its requirements as not done: `ap.py ticket NN review`, the reviewer in the background, and straight on to the next step and wave (`phases/6-review.md`). Its `BLOCKING` lines go to `phases/5-repair.md`.
5. **The ledger.** Each stub → `ap.py add debt.placeholders`; each new variable → `add debt.emptyEnv NAME`; each `A##` that reached the code → `add additions`; each craft `CONCERNS` line → `add concerns`. Project memory only if something was discovered (`phases/9-memory.md`, Moment 2) — most tickets add nothing.
6. **One plain line to the user**: «Бот принимает заявки — 3 из 8 готово».

**Two tickets returning together are processed one at a time**, each through the whole list — one commit and one check each, or a red has two possible authors.

## When the build is over

Every ticket is `done`, or `failed` with its dependents named to the user as waiting — point reviews included: none running, every repair they asked for landed. Then `ap.py stage review` and `phases/6-review.md` — the whole-branch review.
