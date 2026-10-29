# Phase 5 — Build

`ap.py stage build`. Where the code gets written. **Identical in all four modes, and hands-free**: manual buys control over *what* gets built, not over each edit.

Then read `5-host-claude.md` if running in Claude Code, `5-host-codex.md` if in Codex.

## One ticket, one subagent, one fresh context

**Explicit R03 exception when native named agents are unsupported:** a new run with `--sequential-host` uses *one current host session and one Git-isolated task at a time*, without claiming a named subagent, fresh child context, pinned worker model or provider billing control. **The ordinary "you dispatch; you do not build" rule assumes a verified native subagent and does not apply as written to this declared fallback.** The host may edit the **approved worktree only**, after model and subscription conditions are independently confirmed and the operator authorized that work. The host must run `worktree verify` on an unchanged baseline-tracked Python unittest module before finalization, and never mark a task done from a stated test count. No parallel waves, no invented child ID, no real CLI `--execute`: see [sequential-host.md](../../docs/autopilot/sequential-host.md).

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
| `reference.md` | by path, when the ticket builds something the user will look at |
| the check command and how to run one test file | from `interfaces.md` |
| its zone, and what it must not touch | zones of tickets flying beside it included |
| credentials | variable **names**, never a value |

Never paste what it can read: that pays twice and stays in your context. Every rule the executor must follow travels in its prompt or in `prompts/executor.md` — a rule only in a phase file does not exist for the one writing the code.

**Strict isolated test evidence (mandatory):** after the sandboxed worker finishes editing, the **trusted host** runs `ap.py worktree NN verify --suite test_suite.py` against a baseline-tracked, unchanged Python unittest module in the prepared worktree. No arbitrary shell string is run. A verified test count and source fingerprint are recorded; strict `finalize`, `land` and `ticket done` reject invented `--tests` values or source changed after testing. Use `worktree NN finalize` (host-owned Git commit), then `worktree NN land` and `ticket NN done --commit SHA`. Where tests cannot be executed safely, **block acceptance** — never fall back to manually claimed N/0. See `docs/autopilot/worktrees.md`.

**Provider-neutral model routing (mandatory).** Phase 4 computed each ticket's model/Effort with `ap.py plan-models`; with host-advertised capabilities and `--apply` it pinned all allowed profiles. Verify these routes, profile hashes and live host selection again before EVERY executor spawn. For manual re-review or changed tickets: `python3 .autopilot/model_router.py <ticket-path> --provider openai|anthropic --capabilities .autopilot/model-capabilities.json`. The capabilities file must describe the actual running harness (models, effort, enforceable selection). A non-zero exit or `status=blocked` means **do not spawn**. If the host advertises `effort_selection:false` but reliably selects the exact **model** and named agent, the planner may omit effort from the native profile: `effortEnforced=false` means recommendations are advisory and runtime effort is **not verified**. Do not invent host capabilities, weaken model/profile enforcement, or claim this makes Codex V2 native custom agents available. `ap.py ticket NN route --provider ... --model ... --effort ... --reason ... --capabilities .autopilot/model-capabilities.json` creates a **pinned native project agent profile** and records its integrity hash. Pass the exact resulting `agentType` to the host's Agent/subagent call — **not** a generic `worker` or `Explore` — and do not override its model/effort. `ticket NN start` in strict routing mode checks the profile is unchanged. Existing sessions may need a restart to see new project agent files. Host-specific dispatch guards: `5-host-claude.md`, `5-host-codex.md`; details in `docs/autopilot/model-routing.md`. Legacy `Модель: сильная/обычная` is only a hint, not a dispatch instruction.

OpenAI default: Luna for cheap/balanced, Sol for strong; Anthropic default: Haiku for cheap, Sonnet for balanced/strong. Restricted Astra/Fable never spawn automatically; the main session's model must not leak into subagents. If this host cannot independently choose the model or provide verified capabilities, **stop delegation and report the blocker**. A retry on a stronger model needs a new approved route; missing dependencies, access or ambiguous requirements are not model-strength failures.

**Dependencies.** Ticket 01 installs everything the spec's «Решения по реализации» names. A later ticket needing something else returns `BLOCKED` with its name; if it fits a decision already made, add it to «Решения» and relaunch that ticket with permission to install exactly that — the manifest and lock files join its commit — and fly nothing else that installs meanwhile.

**Bounded safe host controller (available in Phase 0):** `python .autopilot/controller.py --root .` gives a read-only single-step plan; `--advance` makes one audited host transition. It consumes the scheduler's eligible task, does prepare/start only after verified routing and exact file-zone safety, then waits for an explicitly approved sandboxed executor. After a worker leaves changes, `--suite test_file.py` invokes trusted host tests; passing runs finalize/land/accept/release, one step per invocation. No automatic model invocation, shell commands from agent prompts, or blind retries. On crash use `worktree NN recover` after inspection. Limits: docs/autopilot/controller.md.

## Waves

**Before each wave, read the scheduler JSON:** `python .autopilot/ap.py schedule --max-parallel 2`. It weighs dependencies, zone overlaps, in-flight executors, checkout reservations, verified routing and the token threshold. Follow each `selected[]` object's `action` (route/prepare/start); never assume the scheduler spawned an agent. `selected[].cwd` is the required executor cwd for prepared isolated tasks. After an agent lands, call `schedule` again to refill only free capacity. Never launch a task whose `blocked[]` entry lists unresolved dependencies, overlaps or budget limits.

**Launch a whole wave in one message, one subagent call per ticket, in the background** — two calls in two messages run serially and throw the planned parallelism away.

- **At most two in flight by default**; three only if explicitly permitted by the verified policy and truly independent. A wave of five normally goes out as two, two, one. A point reviewer writes nothing and does not count.
- **Zones disjoint** — rechecked at launch; same files → serialise. When in doubt, serialise.
- **A wave is not a barrier.** When a ticket returns, first launch the next ticket whose dependencies are all committed, then process the one that landed.
- **A dependent never launches on an uncommitted parent.**
- `ap.py ticket 02 03 start` goes **before** the launch — one call for the whole wave, **in the same message as the Agent calls**: Bash first, the launches after it.
- **One event, one message.** Every call re-reads your whole context (at 200K, about a small subagent's first steps). The `ap.py` mark, the commit, the next launch and the line to the user go out together — never a call that only marks, then one that only launches.
- **Waiting is ending your turn** — a background subagent wakes you. Never spawn an agent or loop just to wait.

**Isolated checkout lifecycle (opt-in, enforced):** start the run with `ap.py init ... --isolated-tickets`. Commit setup changes (particularly `.gitignore`) before preparing the first ticket. Per dependency-ready task: `ap.py worktree NN prepare` for its dedicated `cwd`; `ap.py ticket NN start`; launch the executor **in that exact cwd** and have it create ONE commit; verify, then `ap.py worktree NN land --tests 34/0` (serial, clean primary checkout) and `ap.py ticket NN done --commit <landedCommit>`. The ledger verifies dependencies, preparation, test results and landed SHA. It does **not** launch any model agent: if the harness cannot honor the returned cwd, **run executors sequentially**. See `docs/autopilot/worktrees.md`.

**Legacy shared-tree mode (sequential strongly preferred).** Parallel executors share the checkout, each touching only its zone (and `.env.example`); you commit by zone. A check failing **only in files of zones still being written** is a neighbour's unfinished work: the ticket may land on its own tests green, and the full check reruns when the neighbour lands.

## The return contract

Required in the prompt, not suggested — without it you cannot update anything. The exact format is «Что вернуть» in `prompts/executor.md`: `STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`, then `FILES`, `TESTS` (check → result, count before), `REDPROOF`, `INTERFACES`, `REQUIREMENTS` (`R01 done | R01.1 placeholder`), `COMMIT`, `CONCERNS`, `BLOCKERS`.

**Hard cap: 15 lines and 1,200 characters — no code, no diffs, no file dumps, no account of the work**; details stay in files and commits. A longer block is not read: ask for it again in one line — an essay stays in your context for every remaining turn.

## After each ticket

In this order:

1. **Read the contract and its status.** No block → the ticket is not finished; ask for it. `BLOCKED` or `NEEDS_CONTEXT` → `phases/5-repair.md` now. A `CONCERNS` line saying the plan does not hold — a data model, an interface, two requirements colliding — goes to `phases/5-repair.md` too. Two `NEEDS_CONTEXT` in one run mean the tickets are too thin across the board.
2. **Nothing outside the zone.** `git status --porcelain`: a changed file outside this ticket's zone, `.env.example` and the zones still in flight is a дозапрос — put it back or say why it had to change.
3. **Append its `INTERFACES` to `interfaces.md`** — you, never the executors. Two returns claiming one interface is a plan defect: keep the one that fits, re-cut the other.
4. **Run the check**, full, truncated: `<check> > /tmp/autopilot-check.log 2>&1; rc=$?; tail -30 /tmp/autopilot-check.log; test "$rc" -eq 0`, **and read it before anything else** — green or red, what failed, the count. Compare with the contract: a `DONE` that added criteria and no tests is a дозапрос; a suite reporting zero tests is red however it exits.
5. **Red → `phases/5-repair.md`.** Nothing is committed on red, and nothing is repaired by you.
6. **Commit and record — one call, only its zone:**

   ```bash
   git add -A -- src/bot/ tests/bot/ .env.example && git commit -qm "T03: приём заявки" \
     --trailer "Autopilot-Run: 2026-10-10-repair-bot" --trailer "Requirements: R01, R02" -- src/bot/ tests/bot/ .env.example \
     && python3 .autopilot/ap.py ticket 03 done --tests 34/0 --commit "$(git rev-parse --short HEAD)"
   ```

   Paths: every existing path of its zone, plus `.env.example` if changed (git refuses a path matching nothing). `--tests` is what step 4 printed; `--placeholder R05` for each row reported as a stub. One commit per ticket — the user's rollback points. Trailers keep history searchable: `Autopilot-Run` is `dir` without `--wip` (ticket numbers restart every run), `Requirements` the ticket's rows, so `git log --grep="R02"` finds every change a requirement caused.
7. **Point review, if the ticket says `Ревью: да`**, or the contract reports one of its requirements as not done: `ap.py ticket NN review`, the reviewer in the background, and straight on to the next step and wave (`phases/6-review.md`). Its `BLOCKING` lines go to `phases/5-repair.md`.
8. **The ledger.** Each stub → `ap.py add debt.placeholders`; each new variable → `add debt.emptyEnv NAME`; each `A##` that reached the code → `add additions`; each craft `CONCERNS` line → `add concerns`. Project memory only if something was discovered (`phases/9-memory.md`, Moment 2) — most tickets add nothing.
9. **One plain line to the user**: «Бот принимает заявки — 3 из 8 готово».

**Two tickets returning together are processed one at a time**, each through the whole list — one commit and one check each, or a red has two possible authors.

## When the build is over

Every ticket is `done`, or `failed` with its dependents named to the user as waiting — point reviews included: none running, every repair they asked for landed. Then `ap.py stage review` and `phases/6-review.md` — the whole-branch review.
