# What's new in Autopilot

The skill version comes from `metadata.version` in `skills/autopilot/SKILL.md`. The scoped Codex release is `2.3.0`; historical development evidence below may still refer to `2.3.0-dev`. When running from a Git checkout linked by Windows Junction, update the working branch using `git pull --ff-only` only after checking for local edits. The `npx` update command below applies only to installer-managed **released** versions, not this developer-linked checkout:

```bash
npx skills update autopilot -g
```

## 2.3.0 — Codex limited release (2026-10-26)

- **Claude guard fail-open fix:** `claude_agent_guard.py` resolves the project from `CLAUDE_PROJECT_DIR` (then payload `cwd`, then process cwd), so a hook started in a subdirectory or worktree no longer misses `.autopilot/state.js` and allows unapproved agents. `--install-hook` now writes an exec-form hook (absolute interpreter + `${CLAUDE_PROJECT_DIR}/.autopilot/claude_agent_guard.py`) with `onFailure: "block"` (Claude Code v2.1.295+) and replaces the legacy `python .autopilot/claude_agent_guard.py` entry. Re-run `--install-hook` to upgrade.

- **Claude attestation hook (new, opt-in):** `claude_attest.py` appends metadata-only evidence lines (`effort`, `resolved_model`, `models_used`, `status`) to `.autopilot/attestations.jsonl` from `PreToolUse` (inside Autopilot subagents), `PostToolUse` on `Agent` and `SubagentStop`. It never blocks (always exit 0, no `onFailure`) and never stores prompts, messages or tool inputs; `--install-hook --root .` adds the three exec-form hooks. Recording only, nothing gates on it yet.

- **Release scope:** supported Codex sequential host workflow only (one isolated ticket, independently re-run trusted Python unittest). Native GUI named children and exact runtime model/Effort or billing are not guaranteed; GUI→CLI/API execution remains disabled by spend guard. Claude Code profile/hook support is offline-tested only until the genuine CLI runtime and separate Claude subscription are verified. No provider model/API calls in release qualification.

- Phase 4 now supports **batch automatic model+reasoning-Effort selection per ticket** via `ap.py plan-models --provider openai|anthropic`, with deterministic risk-sensitive scoring and advisory blocked states if host capabilities are unavailable. `--capabilities ... --apply` prevalidates every proposed model/Effort and native agent file, refuses an unsupported or conflicting member without applying the partial batch, then pins all per-ticket profiles/routes for Phase 5. No models are invoked and no provider usage/cost or actual GUI model choice is asserted. Added negative real-Git tests and EN/RU/DE documentation. Sequential host mode deliberately rejects named-agent batch routing.

- Added explicit R03 `init --sequential-host` fallback (cannot combine with strict routing): exactly one prepared/active ticket, isolated worktree, **mandatory real baseline-tracked host unittest** at finalize/land/done/recover/blocker resolution. Denies fabricated `N/0`, changed code after verification, parallel schedules and synthetic named-agent route. Dashboard displays an explicit warning that **GUI model/Effort and cost are not attested**; no model is invoked by this mode. Disposable real-Git lifecycle regressions and EN/RU/DE user guidance added. This verifies file/Git/test safety, NOT native child execution or subscription billing; native GUI model/Effort guarantees remain out of scope for this limited release.

- Published [R01–R06 evidence-based release gate](docs/autopilot/release-readiness.md), cross-linked in English/Russian/German READMEs. Distinguishes real temporary-Git tests, synthetic headless browser checks, subscription login/catalog, negative native Codex GUI child-agent test, missing Claude Code CLI, and absent provider-level model/token savings proof. Native GUI named-agent and Claude Code live E2E remain NO-GO outside the limited Codex release. Corrected obsolete GUI→CLI instructions: the real `--execute` path is denied by `spend_guard`, and no positive token threshold or user approval overrides this guard; only read-only preview/doctor are currently supported. No models/API invoked.

- R01 review blocking findings: `ticket NN repair --note` now opens a durable B-numbered finding; ordinary ticket `done` and final `finish` fail closed on open blockers. Explicit whole-branch `blocker open` and reviewed `blocker resolve` record source ticket, approved commit, tests and reviewer verdict. All blockers (including whole-branch findings) require a new descendant fix commit rather than a preexisting/reviewed one; ticket acceptance must include resolved repair commits and rewritten Git history invalidates resolution. Old `repairFindings` without a matching ledger block final acceptance until reconciled. Ordinary report-only `concerns` remain nonblocking; CLI reviewer testimony/test totals are not signed third-party attestations. Disposable Git regression tests reproduce false success before fix. No AI calls.

- R01 final acceptance revalidates G3 and a saved SHA-256 snapshot of requirement wording, rationale and planned ticket file contents. Negative real-Git fixtures previously accepted newly-added already-`done` requirements, altered quoted user requirements, edited accepted tickets and missing redundant tickets; those releases now stop. Duplicate requirement IDs and orphaned `done` rows are also refused at `check-plan`. A fresh G3 over a changed plan revokes earlier G1/G2/G4 and blind acceptance; an unchanged re-check preserves them. Legacy in-progress 2.3-dev runs without a saved contract need to re-run `check-plan` and renew dependent gates. No model/API calls or new dependencies.

- R06 strict isolated test input integrity: reject ignored Python source, bytecode and importable archive/extension files anywhere in the worktree, including nested ignored directories and uppercase extensions, before fingerprinting. Strip inherited `PYTHON*` settings (especially `PYTHONPATH`/`PYTHONHOME`) before invoking the trusted host test runner; keep its fixed no-bytecode/no-user-site settings. Negative synthetic tests confirmed ignored `.py` and external `PYTHONPATH` were previously accepted, then passed after hardening. Ordinary ignored data remains outside this proof; no models or external paid calls.

- R06 strict-isolated host test evidence is no longer accepted merely from caller-controlled `state.js` fields and a reproducible Git fingerprint: on each `check`, rerun the baseline-tracked unittest module, compare real exit/pass totals and unchanged fingerprint/HEAD against the saved record. Preserve legacy 90-second timeout receipts, persist new approved timeouts and document additional verification run cost. Offline negative tests first demonstrated forged `999/0` accepted for an actually failing suite; the same attempts now fail closed. No model/API calls.

- R03 Claude Code hook fail-closed state integrity: an existing corrupted, unreadable, redirected or non-ledger Autopilot `state.js` no longer downgrades strict `Agent|Task` routing to permissive normal mode; malformed `strictRouting` also denies. Non-agent tools, projects without Autopilot state, and valid non-strict runs retain ordinary behavior. Offline unit and real Python hook subprocess tests added. Read-only Windows runtime qualification found Codex CLI `0.165.0-alpha.1` with `multi_agent` enabled and `multi_agent_v2` disabled, but no Claude Code CLI; no native GUI/Claude agent execution or paid calls were attempted. Host discovery is not child-runtime attestation.

- R04 keyboard and screen-reader navigation: add an EN/RU focus-revealed skip link to the main content landmark; preserve the focused language/filter/button, navigation link or focusable section target through Dashboard innerHTML rerenders caused by polling, live state changes and user actions, without stealing focus from outside the app. Respect reduced-motion preference for smooth scrolling. The real-browser four-layout matrix now asserts focused language click, subsequent rerender, skip link, desktop navigation link and main landmark. This is targeted browser DOM focus testing, not a complete keyboard/screen-reader accessibility certification. No model or API calls.

- Documentation localization and project recovery: rename the original repository requirements file from Cyrillic `бриф.md` to ASCII `brief.md` without changing content; repair EN/RU links and scope references. Add a comprehensive German `README.de.md` with language navigation, installation, normal use, **existing project modification** and **agent-led resume after interruption**. Clarify same three workflows in EN/RU README and bind the actual `SKILL.md` / `phases/0-resume.md` instructions to persisted state, Git/worktree checking, no duplicate writer, no auto-reinitialization or unsaved-work claims. Five CI-safe documentation consistency and link tests added; no app code or paid calls.

- Windows test reliability found during R04 qualification: concurrent read of a durable synthetic offline-worker receipt could cause atomic `os.replace` to fail with WinError 5/32. Receipt replacement now retries these exact temporary Windows sharing conditions briefly, preserves the old receipt on exhaustion, and fails closed for all other errors; three portable fault-injection tests added. The Node VM Dashboard test also has a bounded but less fragile 5-second limit for slower CI runners. No AI or API calls.

- R04 actual responsive browser qualification: fix falsely labeled narrow screenshots caused by Chrome's 500px minimum headless window. The browser smoke now uses 460/390 CSS-pixel frames, validates actual viewport width, horizontal overflow, controls/sections, RU/EN, light/dark and ≥4.5:1 contrast of secondary small labels against inset surfaces. Adjusted only muted/quiet foreground colors to improve small-text readability; no UI framework or service introduced.

- R06 offline benchmark: fixed deterministic 2.2.0 `25b5fbad` vs 2.3-dev measured host CLI/Git fixtures, paired five times per scenario with alternating order and 20 raw samples. The baseline wrongly accepted all five empty runs while current rejected all five; both accepted 5/5 two-ticket synthetic valid runs. Median host-only valid scenario 2475.37ms (2.2) vs 2011.82ms (2.3). This does **not** demonstrate real AI token savings, billing, autonomous coding correctness or general performance. Optional `lean` adds 414 prompt UTF-8 bytes; tokens unknown. No API calls.

- R04 Dashboard: escaped malformed/untrusted state values in test totals, task-wave headings/blockers, gate messages and live timer attributes; the boot error path now escapes its own message. Added a dependency-free Node VM rendered-state regression, automatically invoked by the existing Dashboard check on Linux and Windows. Preserves bilingual, responsive, no-CDN HTML.

- R03 routing: custom JSON policy now safely deep-merges partial model/Effort selections without deleting unrelated default tiers/providers or baseline restricted models; rejects malformed/unknown settings. Normal `ap.py ticket NN route --policy FILE` uses the same policy for selection and agent profile, records its SHA256 and refuses stale-policy strict task transitions. No model/API calls and no additional dependency.

- Scope correction toward the original R01–R06 brief: stop presenting optional paid-API experiments and process harnesses as a normal `/autopilot` prerequisite. Add `docs/autopilot/scope-and-labs.md` and refocus both README front pages.
- R01 final-acceptance regression: `ap.py finish` revalidates all accepted ticket commit ancestry against current HEAD. A real temporary Git `reset --soft` negative test demonstrates stale commits block a false final release while preserving run state.

- Add a separate **fixed synthetic-only** bounded Responses API pilot (no arbitrary code execution, no tool calls, max 4096 request bytes, server `max_output_tokens=192`, one durable no-replay receipt). Uses `gpt-6-luna`, requires temporary Git fixture, exact zone and approval, records reported token usage before applying only an approved toy change. Full host Git acceptance tested with fake provider JSON response. No OPENAI_API_KEY was present and no real paid call made. This is NOT a provider hard dollar cap; Codex CLI spend_guard remains unchanged.

- P0 host-verified worker outcome: the read-only zone-scoped worktree inspector recognizes completed but **uncommitted** worker edits (Windows sandbox can deny shared Git index.lock); `ready-for-host-verification` does not mean tests passed or work accepted. Existing trusted host tests/finalize/land/accept still own the code gate. A synthetic OS-worker no-commit full lifecycle and out-of-zone failure are tested. Real paid CLI remains blocked behind spend_guard.

- P0 hard-cap admission gate: real Codex paid calls are blocked from both GUI bridge and direct dispatcher pending independently verified provider-enforced per-call limits. Ledger token thresholds and timeout are explicitly soft. New `spend_guard.py` read-only audit reports input/cache/output tokens, prior attempts and budget overage without fabricating monetary billing. Strict offline mock tests cover fail-closed paths; no new paid calls.

- Windows process containment qualification: gated launch after successful Job Object assignment, kernel kill-on-job-close for parent crashes, claim-bound cancellation marker and acknowledged terminal receipts, plus read-only reconciliation. Windows parent-death test verified with a held native process handle. POSIX parent-death containment and production use remain unverified.
- One explicitly authorized real Codex CLI smoke (gpt-6-luna/low) completed a model turn but **did not produce a worker commit**: `incomplete`, not accepted, no replay. Account-reported 53,187 input (46,464 cached) and 341 output tokens exceeded the recorded 2,000-token threshold; it is not a hard per-call cap. Added sanitized CLI exit/diagnostic fields to future GUI dispatch receipts. No further paid probes until spending limits and failure diagnosis are addressed.

- Added a **test-only** offline subprocess supervisor with strict temporary Git fixture gating, an exclusive fsynced single-use receipt, explicit per-ticket offline consent, live-child cancellation marker, timeout and no replay on failure/crash. Its only child is a bundled deterministic Python fixture; no Codex/Claude, paid provider or invented usage events. This is a qualification harness, **not** production AI auto-dispatch.

- Added bounded `host_loop.py` on top of controller: side-effect-free preview;
  explicit `--advance` drives up to 32 trusted host/Git/test transitions with
  per-ticket baseline unittest suites, fail-closed pauses for separately approved
  AI workers, stop on failures/concurrent state changes, and distinct
  `tickets-settled` (not final acceptance) status. Real offline two-ticket
  worktrees with failed unittest and successful repair tested without model calls.

- Added read-only Codex CLI runtime doctor: current model/Effort catalog, version and required flags, verified on native Windows CLI without paid calls.

- Added two actual OS-process offline GUI bridge end-to-end tests: pinned route, real worktree commit, usage, host tests, Git landing/acceptance, anti-replay and failure. An incomplete/failed CLI process now reports unknown provider invocation status.

- Added a separately approved GUI-to-CLI bridge for strict isolated OpenAI tickets. Read-only preflight, one-shot explicit per-ticket consent, durable non-replayable attempt receipt, host-controller serialization, native sandboxed Codex dispatcher and independent test acceptance. Not a GUI-native subagent and no production live-billing E2E yet.

- Added a strict isolated host controller with read-only plan and one-step audited prepare/start/verify/finalize/land/accept/release, fail-closed concurrency, and no implicit model calls. Real two-ticket synthetic Git lifecycle verified, including test failure and recovery. Strengthened cross-platform scheduler zone checking.

- Guarded native Codex custom-agent routing against model-V2 spawn metadata omission and unverified child execution; do not interpret GUI skill discovery or agent prose as model pinning.

**Dashboard 3.1 command center and copied-dashboard upgrade (2026-10-25)**
- Rebuilt the Dashboard as a desktop mission-control experience with a dark navigation rail, a two-panel next-action view, color-coded KPIs, task execution, model/token/worktree and quality sections. Narrow and Codex split-screen layouts retain the information without a sidebar.
- Regenerated six real Chrome screenshots in EN and RU, with cache-busting Dashboard 3.1 filenames, and retired previous Dashboard 3.0 captures; regression tests assert the actual live layout.
- Added a standalone dashboard_upgrade.py tool for existing project Dashboard copies: back up the old HTML, check project slug, embed current state.js data and atomically swap the copied page without restarting a run or changing code.
- Validated safe upgrade against the existing WEG_HomeManager project (ledger rev 41 and two tickets); Chrome rendered the new page with preserved state.


- Added a project brief (`бриф.md`) and a dedicated development branch.
- Hard-stop acceptance gates in `ap.py`: incomplete tickets, unverified commits, failing tests, missing gates block `finish`. Reopen/review paths reconcile requirement statuses. Empty manifest/plan fail G3.
- Introduced OS-level locking for `state.js` writes, validated run identifiers, and protected the dashboard server against stale delayed-stop requests.
- Added a provider-neutral model router with OpenAI Luna/Sol and Anthropic Haiku/Sonnet defaults. Restricted high-cost subagents do not launch. Selection requires actual host capabilities.
- Dashboard 3.0 visual refresh, next-action and quality overview, per-task model decisions and explicit unknown-cost state. Separate attributed input/output/cache token counters and recorded-token threshold.
- Project-scoped native Claude Code `.md` and Codex `.toml` subagent profiles; strict start validates their hash, optional Claude Code `PreToolUse` hook denies unapproved spawns.
- Conservative Git worktree helper for per-task isolation and safe, clean single-commit cherry-pick landing. Opt-in `--isolated-tickets` now integrates prepare, start, land, done and release with validated Git SHA and negative tests.
- Crash-safe Git integration via source-annotated `cherry-pick -x`, independent patch checks and explicit `worktree recover` for interrupted ledger writes.
- Real Codex CLI account-visible catalog importer (`codex_capabilities.py`) validates model/Effort pairs via `codex debug models`; no bundled catalog fallback.
- Strict isolated `worktree NN verify --suite test_file.py` runs baseline-tracked Python unittest in the actual worktree and records source fingerprint, test count and result; `finalize/land/done/recover` reject unverified or conflicting N/0. Legacy non-strict mode remains compatible.
- Host-side `worktree finalize --tests N/0` safely stages only declared-zone changes and commits after independently reported passing tests; permits Windows Codex sandboxed editing without shared Git index access.
- Corrected Codex success semantics: a model turn alone is not task completion; missing clean worker commit is `incomplete`. Explicit Windows sandbox backend preserves workspace-write/read-only boundaries.
- Opt-in `--optimization lean` rules are Ponytail-inspired but are **not** a bundled upstream plugin; requires real A/B acceptance and token benchmarks before claims.
- Opt-in Codex CLI external worker adapter with strict ticket/route/sha/worktree/budget preflight, named model and effort flags, isolated `codex exec --json`, and token usage recording; dry-run by default.
- Deterministic JSON `ap.py schedule` planner: dependency, zone, capacity, prepared checkout and budget gating. This is a planner, **not** an external agent launcher.
- Deterministic retry triage (`retry_policy.py`), explicit causes, hard attempt limits, no escalation for environment/dependency failures.
- Replaced all outdated 2.2 dashboard captures in English/Russian READMEs with genuine Chrome screenshots of Dashboard 3.0 using labeled synthetic fixture data; retired 14 old screenshot assets.
- Removed inherited upstream installer lock from the repository, replaced promotional author text with a short `Inspired by` credit and preserved the MIT copyright notice in `LICENSE`. Local development uses one shared skill checkout via Windows Junctions.
- Added regression tests and Linux/Windows CI, expanded setup and safety documentation.
- Pending: verified in-harness dispatch adapters, worktree isolation, actual billing telemetry, visual/browser regression, real-run benchmark.

## 2.2.0 — 2026-10-21

**Size by volume, review without waiting**
- A build is now sized by the volume of code, not by the kind of product: one agent per ~3,000 changed lines, tests included. Up to ~3K lines is one task — one agent builds the whole spec in one fresh context, like a plain dialogue; a list of edits to an existing project usually lands here. ~3–6K is two tasks, ~6–18K three to six, ~18–36K seven to twelve; more is two runs. This replaces "fill each agent to 200–250K", which real runs on a large codebase never hit: their agents ended at 300–420K.
- Code review of a single task only for the first task the rest build on and for tasks whose own code is sign-in, keys, money or deleting data. "Touches access rights" no longer counts: in one product it marked 12 tasks of 15.
- That review runs after the task's commit, alongside the next tasks, and never holds the build; a fix is a second commit. At most one re-check of a fix, then what is still open goes to the final review.
- The review of the whole build at the end stays, always.
- The orchestrator handles one event in one message — the `ap.py` mark, the commit, the next launch together — instead of a call that only marks followed by one that only launches: about 10 calls fewer per T2 run, each re-reading a context near 200K.

**Memory between builds**
- `.autopilot/PROGRESS.md` — what a finished build left: what you settled ("no SMS"), what is not done, known bugs. Rewritten at every landing.
- Small fixes without a new build: `AGENTS.md` now tells a plain session what to read first (the progress file and the commits since the last build) and what to write back after the fix.
- `AGENTS.md` also gets a "git history" section: which slice of the log answers which question (since the last build, by requirement, by file, by code fragment, by line), never the whole log, and how to word a commit so the next build can trace it.
- The next build reads the progress file and the history since the last landing before anything else. It offers the leftovers in the first briefing round, never takes them on its own, and passes what you settled to every executor as project rules.
- Commits carry `Autopilot-Run` and `Requirements` trailers, so `git log --grep="R02"` finds everything a requirement ever caused.
- `ap.py commits` — on resume, flags finished tickets whose commit is no longer in the history (a reset or a rebase), so they are rebuilt instead of trusted.

**Measuring runs**
- `tools/measure-run.py` counted every model call two or three times — Claude Code logs one call as several lines (thinking, text, tool call) with the same usage — so every measured total was about 1.8–1.9× too high. A step is now one call. Comparisons between old runs still hold; absolute numbers in `docs/` are marked.
- It now recognises tasks named `T03 …` as executors and judges them against the new size: under 150K — should have been merged, over 450K — should have been split.

**Docs**
- README, this changelog and `docs/` are now in English; the Russian README lives on as [README.ru.md](README.ru.md). At the time of 2.2, screenshots documented its English-language dashboard. Those captures were retired from the 2.3 README and replaced by current Dashboard 3.0 synthetic demo captures.
- Dashboard: in English, ticket titles in the header are quoted “like this” instead of «like this».

## 2.1.0 — 2026-10-10

**New dashboard**
- The header color tells you what is going on: blue means the build is running, orange means it is waiting for you, green means done, red means a stage failed. Below it are one plain sentence ("2 of 6 tickets done, 3 more in progress") and the eight stages as a strip.
- **"Waiting for you".** When the agent asks you something — the briefing, an "ok" on the spec or the plan in manual mode, a decision before an irreversible step — the header turns orange, the browser tab reads "● Waiting for you", and the build clock stops: the time you take to answer no longer counts as work.
- Tasks are back as bright bars, with a color for each state: done, writing, in review, in repair, failed, waiting. Under a repair bar you see exactly what the review sent back; under a review bar, why the task is being reviewed on its own.
- **"Your words".** Every requirement from the brief, quoted in your words, with what became of it; deferred ones and placeholders show the reason. Filter by status.
- **Checks G1–G4** in plain sight: the brief is fully read, the spec lost nothing, the plan covers every requirement, blind acceptance.
- **Feed** — what happened, in words: task done, sent to review, back for repair.
- The "left" estimate now includes code review and acceptance. On real runs that is almost half the time, yet the estimate used to end along with development.
- A finished build is a report: what came out, what you need to provide before running it (keys, placeholders), blind acceptance disagreements, open questions and review notes. Review notes and report items used to be collected but never reached the screen.
- In a narrow panel next to the chat, the dashboard is denser: the same blocks without the huge numbers.
- The real logo as a single image — the page is ~25 KB lighter.
- Removed from the main screen: the duplicate task table, four different percentages, the ring, "tier" and "critical path".

**Under the hood**
- `ap.py ask <briefing|spec|plan|action|stop> --note "…"` and `ap.py answered` — the build is waiting for the user. A forgotten `answered` is closed by the next stage transition or task event.
- `ap.py` now keeps the event feed itself (`log`), marks gates (`gates`) from the events that decide them, and puts the list of quoted requirements (`reqList`) and the build outcome (`result`) into the state.
- The page re-renders on the `rev` counter, so a sync without an event still reaches the screen.

## 2.0.1 — 2026-10-02

**Dashboard**
- Working time is no longer lost when the computer sleeps or the dashboard server crashes: every build event is now written to the state, not only to wherever an open page happened to see it.
- A crashed server comes back on the same address, and an open tab comes back to life by itself — no reload needed. It used to be able to move to another port, leaving the tab dead.
- If the connection drops, the dashboard says so at the top and suggests what to tell the agent.
- The circular arrow at the top now refreshes the dashboard right away. It used to be an auto-refresh toggle: clicking it silently stopped updates.

## 2.0.0 — 2026-10-01

The first numbered version. Everything before it counts as 1.x. For its first hour after release it was called 1.1.0 — that is the same version.

**Launch**
- Autopilot starts only with the `/autopilot` command. It used to be able to start on its own on phrases like "build it turnkey" — and immediately create a repository and commit. To resume an interrupted build, run `/autopilot` with no arguments.

**Cheaper and faster — the main point of this version**
- Review no longer runs after every task. Before commit, only the foundation (scaffold, schema, shared modules) and risky tasks are reviewed — login and permissions, money, data deletion, secrets, messages to third parties. At the end there is one review of the whole build, security included; everything worth fixing is done by a single executor. On real runs, reviews and repairs ate 13–47% of the spend.
- Only what the reviewer marked as blocking goes to repair — verbatim.
- Routine tasks are built by a lighter model; the foundation and risky tasks by a strong one.
- Briefing questions come in rounds: several at once, each with a recommended answer, and "ok" accepts them all.
- `ap.py` keeps the build's books: one command per event instead of hand-editing `state.js`. The script sets the times, and it also handles requirement statuses in the manifest and gate G3.
- The instructions the agent keeps in mind before development starts shrank from 188 to 75 KB: the rationale moved to `docs/autopilot/design.md`, rare branches to separate files.

**Quality**
- Acceptance installs the project from scratch in a clean copy of the repository, which catches unrecorded dependencies and uncommitted files.
- The executor proves the new test failed before the code was written (the `REDPROOF` line), and verification is a single command: tests, types, linter.
- Every acceptance criterion is false at the start of the task.
- In an existing codebase, one agent first writes notes on the project — the exact names of entities for every executor.
- Subagents do not call other skills or launch their own agents.
- Your references (example sites) go to the executors of UI tasks right away.
- Even the smallest project is built by a separate executor — the orchestrator never writes code.
- Autopilot commits only its own files: code by the task's zone, everything else by an explicit list. Your uncommitted work in the tree does not slip into its commits.
- The executor and acceptance never do anything external: no `git push`, no deploys, no real emails or payments.
- Names in code are in English, no transliteration: `order`, not `zakaz`. In someone else's code, that code's convention applies.
- A wide change in existing code — renaming a field, changing the money type, replacing a library — is split into three steps: the new alongside the old, migration zone by zone, removal of the old. Such a task used to be unable to go green.

**Removed**
- `polish` mode (refining to match a reference) — in eight real runs it was never turned on.
- Handing a task over between contexts based on a call counter — in ~60 tasks it fired once.

**Project memory**
- A new project gets `AGENTS.md` and a one-line `CLAUDE.md` that points to it, so Claude Code, Codex and Cursor all read the file.
- If the project already has its own `CLAUDE.md` or `AGENTS.md`, Autopilot leaves it alone and at the end suggests what to add and asks you.
- Memory holds pointers and pitfalls, not a retelling of the code; the architecture of large projects goes in `docs/architecture.md`.
- In large projects, a `CONTEXT.md` glossary appears at the end of the build: the project's own words ("request", "shift", "booking"), what each one means and which synonyms not to use for it. The next build in the same repository reads it first and writes the spec in the same words. Terms used to land in a separate decision record (ADR), and the exact names from the code notes were lost along with the build. The format follows Matt Pocock's `domain-modeling`, only without questions to the user: the glossary is written by the same agent that writes the ADR, at no extra cost.
- Autopilot keeps its own glossary up to date rather than only appending to it: if a build changed the meaning of a word, the definition is rewritten; if it removed a concept, the term is deleted. Words the build did not touch are left alone. Autopilot recognizes its own glossary by a marker in the first line.
- Your own glossary (`CONTEXT.md` or `GLOSSARY.md` without the marker) Autopilot only appends to: it does not change existing definitions and raises conflicts as questions in the report. In a repository with several areas (`CONTEXT-MAP.md`), no glossary is written.
- When the glossary has more than forty terms, the report suggests splitting it into areas. Autopilot does not split it itself.

**Update notifications**
- At the start of a build, a line if a new version is out. Without internet the check stays silent; turn it off with the `AUTOPILOT_NO_UPDATE_CHECK=1` variable.

**Windows and the dashboard**
- The dashboard no longer spawns multiple servers on Windows and shuts its server down at the end on every OS.
- A stage whose file is already on disk is marked as passed automatically.
- Requirements in the task table are color-coded: done / partial.
