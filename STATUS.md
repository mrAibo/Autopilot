# STATUS.md — Autopilot 2.3 handoff

**Updated:** 2026-10-26 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Active branch:** `main` (PR #22 merged; local checkout clean after fast-forward)
**P0 Codex native-agent guard:** [PR #2 merged](https://github.com/mrAibo/Autopilot/pull/2); `main` now contains verified fail-closed V1/V2/TOML checks. This is not native GUI E2E.
**Merged:** [PR #1](https://github.com/mrAibo/Autopilot/pull/1), squash commit `00600107be80fdb54015611647c767954aa096be` on 2026-10-25. Owner explicitly approved promotion to main after confirming the skill appears in Codex GUI.
**Development history:** `feat/autopilot-2.3-adaptive-router-dashboard` (192 commits retained; do not rely on it as the current deployment branch).
**Version:** `metadata.version = 2.3.0-dev`. This is a **main-branch development snapshot**, NOT a final 2.3.0 release. No stable release tag. Do not confuse publishing to main with feature-complete GUI runtime support.
**Specification:** `brief.md`. Read this STATUS first when resuming work; update it after every milestone.

## Verified QA / source

- Feature HEAD `b3dee4d319a4145c8c8a9f74bde6335237347993` passed [Actions #40199093084](https://github.com/mrAibo/Autopilot/actions/runs/40199093084): **4/4 jobs green** (Ubuntu and Windows / Python 3.11 and 3.13), **144 Python tests** on Ubuntu 3.13, JavaScript syntax and headless Chrome dashboard smoke (desktop/narrow).
- GitHub reports **PR #1 merged** into `main` via a single squash commit. Re-check the post-merge `main` CI after this STATUS update; do not claim it green without observing its result.
- User confirmed `autopilot` is visible in the graphical Codex skill selector. **This verifies discovery only**, not GUI child-agent model/effort/cwd, writable sandbox or accepted end-to-end GUI task.
- Earlier Windows host targeted tests: 13 worktree and 13 Codex adapter tests; strict isolated host verification integration passed. Live account Codex catalog import worked, and standalone Luna/Low read-only requests returned `CODEX_OK` (5s; input 19718, cached 12672, output 7) and `CONFIG_ISOLATED_OK` (4s; input 16643, cached 11776, output 9).
- Live synthetic Windows model task: Codex Luna/Low actually changed `calc.py` in `%TEMP%\autopilot-23-codex-e2e-20261025`; trusted host ran **2/2 tests**, committed only the approved edit (`262b83e`), landed in synthetic checkout (`e7e1975`), accepted the ticket and released its worktree. The now-implemented host `worktree finalize` command was independently validated in tests, not in that live paid task.
- The initial Windows CLI hang resulted from unclosed stdin in the remote test; prompt sent via stdin+EOF fixed it. The Windows Codex sandbox backend needed explicit `windows.sandbox="elevated"` while preserving `--sandbox read-only|workspace-write`; it could edit source but not access shared Git `index.lock` or `python` inside the sandbox. **Never disable sandboxing to make the test pass.**

## Current installation on owner's Windows PC

- Repo: `C:\Users\crown\Downloads\Projects\Autopilot`. After merging, fetch/switch or fast-forward to `main` **only if clean**. Global skills are Junctions to `...\Autopilot\skills\autopilot`; the directory must remain intact during branch change.
- Verified global directories `%USERPROFILE%\.agents\skills\autopilot`, `%USERPROFILE%\.claude\skills\autopilot`, `%USERPROFILE%\.codex\skills\autopilot`: each is a Windows **Junction** to the SAME checked-out skill folder and each reported `metadata.version=2.3.0-dev`. No duplicate skill installation.
- The old globally installed 2.2 skill directory was removed with owner approval. Its obsolete `nick-vels/skills` entry was removed from the **user's** installer lock; other skills were left untouched. Do not run `npx skills update autopilot -g` while working from the Junction-linked dev checkout or it may replace these links.
- Installed official Codex CLI `0.165.0-alpha.1` via npm and logged in with ChatGPT, GUI Codex app installed. VPN off resolved HTTP provider availability (doctor 21 ok, 0 fail). Claude general desktop app is present; actual Claude Code CLI and GUI-native agents remain unverified.
- Isolated GUI test folder `%TEMP%\autopilot-gui-skill-smoke-20261025` also has project-level Junctions to the same source; safe to reuse for validation.

## Implemented in 2.3.0-dev

1. Spec/requirement ledger; G1–G4 hard acceptance gates; strict task state, commit/test checks, state locking and bounded retry diagnosis.
2. OpenAI/Anthropic model+effort routing with fail-closed account capability verification; SHA-pinned native `.codex/agents/*.toml` and `.claude/agents/*.md`. Restricted expensive model tiers excluded by default. Optional Claude Code `PreToolUse` guard; runtime model inheritance still subject to host behavior.
3. Detached Git worktrees with safe `prepare → start → finalize → land → done → release`, source-linked cherry-pick and conflict recovery. Host `finalize` only stages exact approved zones, not unknown or symlink files.
4. Strict isolated `worktree NN verify --suite test_file.py` invokes an **unchanged baseline-tracked Python unittest** on trusted host, records genuine test count + source fingerprint, and denies fake N/0 or source changes at finalize/land/acceptance. This is not tamperproof against editing `state.js` or ignored files; other test runners are not yet supported.
5. Standalone Codex CLI worker with isolated sandbox/cwd and JSON token usage; **completed model turn without clean worker commit = `incomplete`, never accepted**. Scheduler `ap.py schedule --max-parallel 2` produces a read-only plan, it **does not dispatch agents automatically**.
6. Dashboard 3.0 (model assignments, worktree/recovery state, gates, recorded tokens and threshold), responsive Chrome smoke. Optional `codex_dispatch.py --optimization lean` instructions inspired by Ponytail (OFF by default; original Ponytail plugin NOT installed or benchmarked).
7. English/Russian READMEs display 4 **actual current Dashboard 3.0 Chrome screenshots** generated from synthetic state (desktop/narrow). Retired 14 obsolete 2.2 screenshots and imported old `skills-lock.json`. README only credits *Inspired by*; required original MIT copyright remains in `LICENSE`. No old Telegram-channel promotion observed. See `docs/autopilot/gui-clients.md`, `worktrees.md`, `codex-cli.md`, `optimization.md`, `model-routing.md`.

## Current presentation and GitHub upstream status (2026-10-25)

- User noticed earlier README images still displayed inherited original branding. Fixed the *actual dashboard template*, not just screenshot names: removed the embedded old PNG logo, replaced both headers (including error state) with text-only \`Autopilot / 2.3 DEV\`. Removed the two inherited README logo PNG assets and header references.
- Generated six fresh, actual Chrome captures from the updated Dashboard 3.0 implementation and the existing synthetic CI fixture: wide, narrow and an enlarged crop emphasizing model/effort selection, token reports and worktree state, for EN and RU galleries. They are clearly labeled synthetic demonstrations, not claims of a successful real user deployment. Confirm screenshot build, visual review, README links, smoke CI on \`main\`.
- The GitHub API explicitly reports \`fork: true\`, \`parent: nick-vels/skills\` for \`mrAibo/Autopilot\`. GitHub's “This branch is N commits ahead of ...” is a **fork network comparison**, not installed Autopilot version or incorrect active code. Rebranding cannot change GitHub fork metadata. GitHub supports **Settings → General → Danger Zone → Leave fork network** for eligible public forks; it is irreversible and can lose PR/issues/comments/stars/fork metadata. **Do not detach or recreate without explicit informed consent**. Keep original MIT copyright and appropriate \`Inspired by\` reference even if later detached.
- Owner confirmed the Autopilot skill appears in graphical Codex. Native child agent model/effort and working directory still require separate GUI execution validation; do not conflate skill discovery with full runtime verification.

## Dashboard 3.1 — owner-requested genuine visual redesign

- User pointed out that earlier Dashboard 3.0 screenshots and author/logo changes did
  not change the overall visual layout. They were correct: the previous interface
  still resembled the 2.2 design despite additional model and worktree cards.
- Actual single-file dashboard-template.html now renders a distinct command center:
  persistent dark navigation rail (wide screens), four functional anchor links,
  live active-agent and quality-gate counters; split live-execution/next-action
  spotlight; four color-coded metric cards; separately numbered Tasks, Models /
  Tokens / Worktrees, and Quality sections. At <=1150px the rail collapses;
  small screen and Codex split-pane layouts keep content accessible at 480px.
- Model routing, actual reported token totals, tests, requirements and Git status
  still derive from existing state fields; no fabricated usage or claims of
  successfully executing a graphical agent. RU/EN language toggles, theme
  switching, polling, safety notices and responsive behavior retained.
- Six new REAL Chrome screenshot files use cache-busting 3.1 filenames:
  assets/dashboard-31-{desktop,narrow,models}.png and assets/ru equivalents.
  Both README galleries point at these, with SYNTHETIC demo-state disclosure.
  Old 3.0 screenshots retired. Added source-level brand/design checks and
  extended headless Chrome DOM smoke to verify the new navigation and sections.
- **Verified final implementation checkpoint:** GitHub Actions [#40203272189](https://github.com/mrAibo/Autopilot/actions/runs/40203272189) passed **4/4** Python 3.11/3.13 Linux/Windows jobs, 151 unit tests, and dashboard browser checks on commit `fc135ea`. The new screenshots and GitHub image paths were also checked. Fork
  relationship to nick-vels/skills is separate GitHub metadata and is left
  untouched pending explicit informed consent for potentially destructive
  fork-network detachment.

## Real WEG_HomeManager Dashboard refreshed in place

- The user's live WEG_HomeManager project contained an older copied .autopilot/dashboard.html with no 3.0/3.1 features, explaining why updates to the global skill appeared invisible in that project.
- The new dashboard_upgrade.py safe updater validated that its embedded slug matched the authoritative state.js and atomically replaced ONLY the local HTML, preserving active run slug weg-homemanager, revision 41 and two tickets. A backup was written under the current Windows user's temporary autopilot-dashboard-backups directory. It did not touch WEG application source, task state or tracked changes.
- Direct Chrome --dump-dom on the upgraded WEG file confirmed new mission, models and quality sections and the existing project title. Reload existing Dashboard browser tabs to use the new DOM and CSS.
- Added four unit tests for safe upgrading, dry-run, wrong slugs and invalid snapshots; documented the upgrade procedure in phase 0, GUI integration guide and both READMEs. Future projects should refresh their copied Dashboard explicitly, not reinitialize active runs.

## P0 checkpoint: Codex native runtime incompatibility (2026-10-25)

- Native Codex Desktop EXE 0.164.0-alpha.11.1, standalone CLI
  0.165.0-alpha.1; both resolved catalogs expose 9 models. GPT-6
  Sol/Luna models indicate multi_agent_version=v2 (even if the local
  multi_agent_v2 feature flag reports false); GPT-5.6 Luna is V1.
- Created disposable read-only synthetic Git probe under
  TEMP/autopilot-native-gui-agent-smoke-20261025 with pinned
  .codex/agents/autopilot-explorer-smoke.toml set to GPT-6 Luna / Low.
- Native Desktop-bundled binary run via read-only codex exec with
  GPT-6 Sol / Low returned exit 0 but NAMED_AGENT_UNAVAILABLE and no
  child spawn event; 18,729 input / 12,928 cached / 78 output tokens;
  6.3 seconds. A GPT-5.6 Luna / Low V1 parent also had no child event;
  16,838 input / 11,392 cached / 54 output; 4.7 seconds.
- This was a native executable invoked in CLI mode, NOT mouse/keyboard
  GUI interaction. No personal project modified; full GUI E2E and
  per-child model/Effort/cwd remain UNVERIFIED.
- Added tools/codex_native_agents.py which validates resolved model
  V1/V2 metadata, profile model/Effort and available native events.
  It never authorizes execution from caller-supplied JSONL or from
  the agent's text. Ten new negative tests added. Phase 0 copies
  guard; Phase 5 requires it before strict named GUI OpenAI agents.
  Fallback: sequential GUI or separately validated, sandboxed pinned
  Codex CLI worker with trusted host tests, no forced inheritance.
- Claude Desktop installed but no claude executable located; no
  authenticated Claude Code GUI/CLI proof yet. Version remains 2.3.0-dev.
- **Merged** via [PR #2](https://github.com/mrAibo/Autopilot/pull/2) on 2026-10-25: `262387adc9bbbd79c4c611967ed573e9abf85374` (squash) into `main`, preserving feature branch history. [CI #40205859815](https://github.com/mrAibo/Autopilot/actions/runs/40205859815) on the feature commit passed all four Windows/Linux, Python 3.11/3.13 jobs, **161 Python tests**, JS syntax and Chrome desktop/narrow smoke. This `STATUS.md` update advances `main`, so check its own CI when resuming. Read docs/autopilot/gui-clients.md.

## P0 host controller milestone — in feature branch (2026-10-25)

- New `skills/autopilot/tools/controller.py` coordinates exactly **one**
  strict isolated host transition per invocation. Default only plans; explicit
  `--advance` runs prepare/start, trusted verify, finalize, land, accept or
  release. It never invokes a model, chooses a new model, fabricates success,
  or automatically retries interrupted Git operations. Uses an OS-owned
  persistent lock file and rereads state after each step.
- Before any new task, validates strict isolation, verified scheduler route,
  dependency and recorded-token budget, exact file zones, and disallows
  multiple active tasks. No autonomous parallel waves yet. Worker dispatch
  intentionally stays separate and explicitly opted-in through the pinned,
  sandboxed Codex CLI path. GUI child execution remains unverified.
- Supports actual host-run, baseline-tracked Python unittest suites:
  a red test blocks and preserves files for repair, only verified evidence
  permits finalization and acceptance. Existing read-only worktree recovery
  applies after crashes; no destructive cleanup or silent replay.
- New tests: isolated controller unit test suite covering blocked cases,
  malformed zones, duplicate starts, lock semantics, budget, no hidden model
  calls; an additional genuine two-ticket synthetic integration test exercises
  Git worktree creation, independent tests, commit/land/accept/release,
  a deliberate red test then corrected rerun and second successful landing.
- Scheduler treats malformed Windows drive/UNC paths, parent escapes,
  wildcards, unknown zone types and case differences as overlapping.
  Runtime-only controller lock and __pycache__ are ignored by new projects.
- **Merged** by [PR #3](https://github.com/mrAibo/Autopilot/pull/3) into `main` on 2026-10-25, squash commit `541c0549db5a548fb2c7f74cda2260466bbc9870`. Feature commit `3741bd2e9d7c69a2bc88670a19e199449f7773cd` passed [CI #40208179320](https://github.com/mrAibo/Autopilot/actions/runs/40208179320): **4/4** Windows/Linux Python 3.11/3.13 jobs green, **185 Python tests**, JS syntax and Chrome wide/narrow smoke. This STATUS-only commit starts another main CI; confirm its result separately.
- This is an explicitly invoked host-transition controller, **NOT** an unattended multi-agent execution daemon. Never say autonomous agent dispatch or GUI/Claude E2E is verified.

## NEW owner-provided Codex graphical app capability test (2026-10-25)

- The owner actually ran the disposable read-only `autopilot-explorer-smoke`
  request **inside a graphical Codex chat**, not merely via Codex CLI.
  Screenshot shows that Codex could not select the named child role from
  `.codex/agents/` in that session. It explicitly stopped and reported:
  child created **No**, profile applied **No**, runtime child model
  **unconfirmed**, reasoning effort **unconfirmed**, `EXPECTED_PROBE_WORD`
  **not obtained**. Approximate displayed duration: **23 seconds**.
- Codex reported no substitute agent launched and no files changed;
  these are its UI-reported results, not an independent filesystem audit.
- This is a **confirmed negative GUI capability test in the user's current
  session**; it does not prove all Codex desktop versions lack the capability.
  Do not record GUI native named-agent E2E as passed. Investigate conditional
  `agent_type` schema exposure, runtime flags and supported host versions
  separately and safely. Keep `codex_native_agents.py` fail-closed.
- Approved implementation direction: GUI remains the user interface; on
  unsupported native custom-agent sessions use the independently verified,
  model/Effort-pinned and sandboxed Codex CLI worker plus trusted host test,
  worktree and budget acceptance gates, or sequential GUI execution.
  Never silently substitute a generic child inheriting a costly parent.
- Record in `docs/autopilot/gui-clients.md` as a tested capability outcome;
  **Claude Code still needs independent runtime verification**. Version
  stays `2.3.0-dev`, no stable release claim.

## New P0 checkpoint — GUI to pinned CLI one-shot bridge (2026-10-25)

- Feature branch `feat/gui-cli-approved-dispatch-20261025` adds
  `skills/autopilot/tools/gui_bridge.py` and
  `docs/autopilot/gui-cli-bridge.md`, copied by Phase 0. This is an
  **explicit local terminal tool invocation from a GUI workflow**,
  not a Codex GUI-native subagent. Claude Code as a GUI host is still
  unverified. Existing pinned Codex CLI worker is reused unchanged.
- Default preview runs trusted controller and Codex dispatcher
  preflights with **no writes, subprocess model call or receipt**.
  Confirms strict isolated ticket, only one in-progress worker,
  known verified OpenAI model/Effort, SHA-pinned profile and brief,
  clean actual worktree and positive recorded token threshold.
- Explicit per-ticket `--execute --approve-ticket NN` creates a
  **persistent exclusive receipt before any provider call**. Later
  executions of the same ticket refuse even after timeout, crash,
  partial record, missing usage or failed/incomplete turn. There is
  NO force/reset/retry bypass. A controller OS lock serializes with
  other host transitions. The receipt contains only route/cwd/usage
  summary, digest, timestamps and status, never the full prompt.
- Existing `codex_dispatch.run_once` invokes pinned Codex CLI under
  sandbox with bounded wall-clock timeout and accounts JSONL usage
  when available. Recorded token threshold is NOT a hard provider
  cost cap, and user-supplied flag is NOT cryptographic human consent.
  The bridge never finalizes/lands/accepts automatically; trusted
  host tests remain mandatory. Do not infer paid execution from
  dry-run tests.
- New negative tests prove read-only default, explicit approval,
  duplicate/orphaned/partial receipt blocking, crash ambiguity,
  locked/invalid budget, dirty worker refusal and no silent test
  acceptance. Tests use mock model calls on synthetic Git fixtures.
- **Merged:** [PR #4](https://github.com/mrAibo/Autopilot/pull/4)
  squash commit `7c7fdd5e3f30c551dfc26dcd2f72c2930a7368ea` on 2026-10-25.
  [CI #40221255682](https://github.com/mrAibo/Autopilot/actions/runs/40221255682)
  passed **4/4** Linux/Windows Python 3.11/3.13 jobs, **199 tests** on
  Ubuntu 3.13, dashboard JavaScript and desktop/narrow browser smoke.
  A status-only commit advances main; check the corresponding new CI.
- **Still missing:** real GUI-terminal availability and owner-approved
  paid GUI→CLI→independently accepted code E2E. All new test-model calls were
  mocked. No hard provider budget enforcement; recorded usage threshold only.
  Remain `2.3.0-dev`, no release tag.

## P0 qualification — subprocess GUI-bridge E2E offline (2026-10-25)

- Branch `feat/bridge-process-e2e-validation` adds two actual OS process
  end-to-end tests for GUI-to-CLI fallback. The only substituted component
  is the external model executable; a local Python CLI shim replaces paid
  inference in the **temporary** test Git repository.
- First test uses a real strict isolated Autopilot run and model route
  pinned to GPT-6 Luna / Low; a real OS child writes one worktree commit,
  emits synthetic Codex JSONL, and actual ap.py usage records token counts.
  A duplicate GUI bridge invocation is blocked, then independent trusted
  baseline unittest, cherry-pick landing, ticket acceptance and worktree
  release are performed by the actual host controller.
- Second test exercises a nonzero OS subprocess exit with no usage;
  persistent receipt forbids retry and preserves the in-progress ticket.
  Failed/incomplete bridge status now reports model_invoked=unknown rather
  than claiming the provider actually received the billable request.
- Local Codex CLI 0.165.0-alpha.1 supports its required flags
  --cd, --sandbox, --model, --ephemeral, --ignore-user-config, --json.
  No real paid provider calls, GUI-host terminal interaction or Claude
  Code execution were run during this qualification.
- **Merged into `main`:** [PR #5](https://github.com/mrAibo/Autopilot/pull/5)
  squash commit `4e53182e27d247cb0ddcd13a519dbcdf231855c7`.
  [CI #40224575703](https://github.com/mrAibo/Autopilot/actions/runs/40224575703)
  passed **4/4** Linux/Windows Python 3.11/3.13 checks, including
  **201 Python tests**, JS syntax, and Dashboard browser smoke. The
  original Windows 3.13 fail was fixed by explicit UTF-8 stdin decoding
  in the **synthetic CLI test**. Current branch main contains the fix.
  This STATUS-only update advances main and requires its own CI check.
- No real paid provider invocation, graphical Codex terminal bridge E2E
  or Claude Code execution has yet been attested. Do not call native
  GUI subagents or billing hard limits verified.

## Disposable real-Codex smoke ticket prepared (2026-10-25)

- An isolated synthetic test repository is ready on Windows at
  `%TEMP%\autopilot-gui-cli-live-smoke-20261025`. It is separate from
  the Autopilot development checkout and all user application projects.
- Strict isolated ticket `01` has status **in-progress** with one clean
  prepared Git worktree. Approved route `gpt-6-luna / low`, pinned
  profile and host-resolved account capability advertisement passed
  `gui_bridge.py --root ROOT --ticket 01 --timeout 90` dry-run.
  Recorded token threshold is **2,000**, used **0**. Baseline source:
  `src/core/calc.py` intentionally subtracts instead of adding;
  trusted host test: `test_core.py`.
- **No paid model execution occurred**, no dispatch receipt was created,
  and no GUI terminal interaction was performed. Only an explicitly
  approved *specific ticket-01* potentially billable invocation can
  proceed. This threshold is recorded-accounting protection, NOT a
  hard cap on provider spend; timeout does not prevent all token use.
- Do not touch/reuse the fixture for another task or execute
  `--execute --approve-ticket 01` without the owner's specific informed
  consent. If approved, call once, inspect receipt + actual usage, run
  independent host test and controller land/accept/release as applicable.
  On a crash do NOT retry the paid call automatically. Do not mistake
  this CLI route for native GUI named subagents or a Claude Code test.

## P0 CLI runtime doctor — tested with actual native executable (2026-10-25)

- Branch `feat/bridge-readonly-runtime-doctor` implements
  `gui_bridge.py --check-runtime`, a read-only CLI/capability diagnostic.
  It uses existing preflight, checks actual native Codex model/Effort
  availability against the fresh resolved account catalog, version
  string and required CLI exec switches. Unknown versions, missing
  efforts or conflicting paid-execution flags block without a receipt.
- On the Windows host it passed with Codex CLI `0.165.0-alpha.1`,
  approved synthetic ticket `01` routed to GPT-6 Luna / Low, clean
  worktree and 2,000 recorded unused tokens. Verified no model call,
  no attempt receipt and no modified source.
- Four new tests cover nominal read-only, stale model catalog, invalid
  binary/version and mutually exclusive paid flags.
- This establishes CLI metadata compatibility, **NOT** provider
  execution, paid model identity, true hard budget limits or native
  GUI/Claude Code session execution. Keep the actual synthetic ticket
  untouched until a separately authorized potentially billable call.
- **Merged:** [PR #6](https://github.com/mrAibo/Autopilot/pull/6) as squash commit `ae8e2471332a6f0e72079c4ceba4a5020e8166bb` on 2026-10-25. Final PR [CI #40228772621](https://github.com/mrAibo/Autopilot/actions/runs/40228772621) passed **4/4** Ubuntu/Windows Python 3.11/3.13 checks with **205 Python tests** and Dashboard JS/browser smoke. Initial Linux 3.11 red test was due to Python executable symlink-string comparison in the synthetic fixture; canonical path test now passes everywhere.
- This STATUS.md update creates its own main commit and corresponding CI; check it independently.

## P0 host-only bounded orchestration loop (2026-10-25)

- **Merged to `main`:** [PR #7](https://github.com/mrAibo/Autopilot/pull/7) squash commit `372cdd89f35b60670ab08c4f5982bd5905864380` on 2026-10-25. Feature branch `feat/p0-host-orchestration-loop-20261025` was based on `fe0911ff`. Owner requested continued P0 work and persistent handoff; no paid model execution was authorized.
- Added `skills/autopilot/tools/host_loop.py`: default read-only; `--advance` makes at most 1–32 controller-managed trusted host transitions, with exact per-ticket `--suite 01=test_core.py` mapping; every transition uses existing controller OS lock, Git and test revalidation. No direct AI launch or provider call from the loop (`model_invoked=false`); trusted host-test modules can themselves have side effects and require independent offline review.
- Safe pauses at the independently approved worker boundary; test failures, ambiguous state and unexpected concurrent plan changes stop the loop without replay. `tickets-settled` indicates only accepted tickets and released worktrees; it does NOT mean `ap.py finish`, independent blind acceptance or G1–G4 completed.
- Added `tests/test_host_loop.py` with seven cases, including a **real temporary two-ticket Git worktree integration**: trusted source baseline, intentional offline source fixes, genuine host-run unittest, finalize/cherry-pick/accept/release, an intentional red test on ticket 02, hard stop, repair and restart. Targeted Windows Python 3.13 **7/7 passed** (prior to full suite).
- Phase 0 installer copies new instrument; bilingual README, CHANGELOG and `docs/autopilot/host-loop.md` explain approval boundaries, supported statuses and limitations. This is host lifecycle automation only; **there is no model worker auto-dispatch or true multi-agent parallelism**.
- **Verified final QA:** local Windows Python 3.13 **212/212 tests green**; Dashboard JavaScript syntax passed. [PR CI #40234255934](https://github.com/mrAibo/Autopilot/actions/runs/40234255934) **4/4** jobs green (Ubuntu/Windows, Python 3.11/3.13), with Linux dashboard browser smoke. No paid provider requests during these tests. `main` checked out locally with a clean fast-forward to `372cdd89`. This status-only checkpoint will produce another main commit and CI, verify it separately.
- Next step: explicit model-call authorisation for one disposable Codex CLI GUI→bridge smoke if wanted, or continue offline P0 with cancellation and bounded dispatch tests. Do not reuse the owner's paid smoke fixture or infer permission from the general continuation instruction. The existing Codex GUI named-agent negative result remains valid for the tested session.

## P0 development checkpoint — offline subprocess supervisor (2026-10-25)

- **Merged to `main`:** [PR #8](https://github.com/mrAibo/Autopilot/pull/8) squash commit `fd7cbaeb620b6984c8e5945dea64a1b813b6f26e` on 2026-10-25. Feature branch `feat/p0-offline-worker-supervisor-20261025` was based on `fea0a847`. Work is restricted to offline synthetic Git fixtures; no paid AI/model requests were authorized or performed.
- Added `skills/autopilot/tools/offline_supervisor.py` and `offline_fixture_worker.py`: explicit `--approve-offline-ticket NN`, strictly temporary Git root and marker validation, exact `src/core/` or `src/bot/` file zones, verified active ticket and clean isolated worktree. Only two bundled deterministic synthetic workers can launch. CLI cannot accept an arbitrary executable or dispatch Codex/Claude.
- A per-ticket exclusive, fsynced `.autopilot/offline-worker/NN.json` receipt is created **before** child spawn. Every completed/failed/cancelled/timed-out/uncertain attempt is non-replayable. Cancellation from another process writes a marker; only the **live** supervisor signals/kills its owned process, never a stale saved PID. Existing controller OS lock is held throughout the worker run to prevent racing Git host transitions.
- **Limit:** if supervisor crashes, child cleanup is not proven on every OS. Persisted receipt blocks replay; a cancel marker cannot stop a child if its owning supervisor died. Cancellation is best-effort when completion races. Do not describe this as production worker cancellation or recovery. No billable model identity, provider spend, GUI-native agents or parallel AI workers verified.
- Added `tests/test_offline_supervisor.py` (six real Windows 3.13 tests) and `docs/autopilot/offline-supervisor.md`. Synthetic first ticket is dispatched by an actual OS process and independently host-verified/landed/accepted; delayed second ticket is cancelled. Also verified failure, timeout, crash-after-claim, refusal without marker or with wrong zone, and no replay. **6/6 targeted tests green**. Additional .gitignore entries prevent local fixture receipts/marker from Git commit.
- **Verified QA:** local Windows Python 3.13 **218/218 tests green**, Dashboard JavaScript syntax passed. [PR CI #40236471621](https://github.com/mrAibo/Autopilot/actions/runs/40236471621) **4/4 jobs green** (Ubuntu/Windows, Python 3.11/3.13), with Linux browser smoke. The Windows checkout fast-forwarded cleanly to `fd7cbaeb` on `main`. This STATUS-only commit will trigger a separate `main` CI, which must be checked independently. Version stays `2.3.0-dev`.
- **Next P0:** separately design production-grade process containment/identity, acknowledged cancellation and durable result reconciliation, then explicit per-ticket real Codex CLI dispatch after specific informed paid-call consent. Keep native Codex GUI and Claude Code E2E unsupported until genuinely verified.

## P0 Windows crash containment + authorized real CLI smoke (2026-10-25)

- **Merged to `main`:** [PR #9](https://github.com/mrAibo/Autopilot/pull/9), squash commit `7adb11d13bc4995b5d88f5f437d1b522d94e4bab` on 2026-10-25; branch `feat/p0-windows-job-containment-20261025` based on `a438d1d5`. User **explicitly authorized paid token tests**; this does not provide a provider-side hard spending cap. No retries.
- Added `process_containment.py` with Windows Job Object `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and `process_gate.py` that cannot start its fixed synthetic fixture before successful Job assignment/START signal. The Job handle is owned by the supervisor, and Windows kernel kills its contained child tree if parent terminates; assignment failure blocks execution. POSIX retains session isolation only, **no parent-death guarantee**.
- The offline supervisor now uses a claim-specific 128-bit identifier in each cancellation marker, records `cancel_acknowledged_at` only when observed, and offers read-only `--status` without trusting saved PIDs. A Windows test held a real process handle, killed its supervisor, and confirmed that the gate terminated while the worktree stayed unchanged and retry remained blocked. Offline fixture-only constraints and standalone non-production designation are unchanged.
- **One authorized real CLI invocation performed:** existing disposable `%TEMP%\\autopilot-gui-cli-live-smoke-20261025`, ticket 01. Read-only CLI doctor confirmed Codex CLI `0.165.0-alpha.1`, `gpt-6-luna` / `low` exposed by account. Explicit one-shot `gui_bridge.py --execute --approve-ticket 01 --timeout 120` created `.autopilot/gui-dispatch/01.json`; result **`incomplete`**, `turn_completed=true`, **no worker commit**, source remains unfixed, no independent tests or acceptance, ticket remains `in-progress`. **Do not replay that ticket**. The receipt says `model_invoked=unknown` under strict bridge semantics, though its completed turn and usage event substantiate an actual call; no independently attested model identity from paid provider telemetry.
- CLI JSONL reported **53,187 input tokens (46,464 cached), 341 output**; one usage event was recorded. This exceeded the recorded positive **2,000-token threshold**: that threshold is a preflight ledger gate, **NOT a per-call hard cost cap**. No monetary cost was established, and subscription/CLI billing should not be equated with an API invoice. **Stop further paid calls** until an enforced provider-side cap and stronger diagnostic evidence exist.
- Future GUI bridge receipts now include sanitized CLI exit code, presence of a thread id, and diagnostic reason for incomplete/failed status, without exposing raw prompts or logs. This earlier historical receipt cannot be backfilled from absent CLI output.
- **Verified QA:** local Windows Python 3.13 targeted **8/8** offline supervisor and **2/2** GUI bridge tests; full regression **220/220** green and Dashboard JavaScript syntax passed. [PR #9 GitHub CI #40239212363](https://github.com/mrAibo/Autopilot/actions/runs/40239212363) **4/4 green** (Ubuntu/Windows; Python 3.11/3.13). Local Windows checkout fast-forwarded cleanly to `7adb11d1` on `main`. This status-only checkpoint generates its own main CI; verify separately. Version remains `2.3.0-dev`. Next P0: cross-platform parent-death containment, cancellation/process identity attestation, provider-enforced per-call budget and no false production auto-orchestration claims.

## P0 fail-closed real-provider budget gate and token audit (2026-10-25)

- **Merged to `main`:** [PR #10](https://github.com/mrAibo/Autopilot/pull/10), squash commit `a428e3b5747a88bc3f3dfc078a87f38eb3dfed0a` on 2026-10-25; feature branch `feat/p0-fail-closed-paid-budget-20261025` based on `ecdc366`. User permitted paid tests; none were made in this phase because the observed route lacked a provider hard cap.
- The user's explicit authorization for paid testing remains on record. **No additional paid Codex/Claude call** was made in this phase: the earlier real Codex CLI smoke used **53,187 input (46,464 cached) + 341 output = 53,528** tokens, exceeding a recorded 2,000-token threshold by **51,528**. That threshold is a **soft ledger admission gate, not a provider-enforced per-call cap**; no monetary invoice/actual price is established. The historical ticket receipt is non-replayable, incomplete, and unaccepted.
- Added `skills/autopilot/tools/spend_guard.py`: `assert_enforced_cap` unconditionally fails closed because there is currently no independently verified provider-enforced per-call hard budget. Both `gui_bridge.py --execute` and the lower-level direct `codex_dispatch.py --execute` refuse before the external model subprocess; GUI refuses before a new attempt receipt, and the direct CLI refuses before its dispatch lock. No CLI/config/env bypass. Synthetic offline unit/E2E tests patch only the guard in their test process when using mocked/stub executors.
- Read-only `spend_guard.py --root . --ticket 01` audits recorded input/output/cached subset, overage, receipt status and recorded commit/acceptance evidence; **no invoice, cost, independent model attestation or provider hard cap inferred**. Phase 0 now copies the guard alongside both dispatchers; previous already-installed `.autopilot` copies must be refreshed, not left unguarded. Read-only `gui_bridge.py --check-runtime` reports `execution_permitted=false`.
- Added `tests/test_spend_guard.py` for denial in both paid entrypoints and strict accounting, plus process-local mock adaptations; bilingual README, CHANGELOG, `docs/autopilot/spend-guard.md` and Codex CLI docs updated. Targeted tests **7 spend guard + 18 GUI bridge + 13 dispatch + 2 offline process E2E passed**. Full local Windows Python 3.13 **227/227 green**, Dashboard JS syntax passed; [PR #10 CI #40241254426](https://github.com/mrAibo/Autopilot/actions/runs/40241254426) **4/4 green** Ubuntu/Windows Python 3.11/3.13. Local Windows checkout cleanly fast-forwarded to merged `a428e3b5`. This status-only checkpoint will trigger its own main CI to verify separately.
- **Next P0:** provider-side verifiable request/account hard cap (or a clearly bounded alternative with explicit user-facing risk, without claiming hard enforcement), accurate spend reconciliation, sanitized diagnosis of missing worker commits, and independently successful model-driven worker acceptance. Preserve Windows Job Object proof from PR #9 and POSIX containment limitations. Keep `2.3.0-dev`.

## P0 host-verifiable uncommitted-worker handoff (2026-10-26)

- **Merged to `main`:** [PR #11](https://github.com/mrAibo/Autopilot/pull/11), squash commit `530d5808d5ce4f6b319353e24d38bdff0508a2d8` on 2026-10-26. Branch `feat/p0-worker-outcome-diagnostics-20261026` based on `dad300a`; no new paid model calls.
- **Known failure mode addressed (not proven to be the historical attempt's cause):** Codex Windows sandbox may edit permitted source but be unable to create a commit inside Git's shared `.git/worktrees` metadata. `codex_dispatch.py` now tells executors they may leave scoped edits uncommitted for independent host tests and commit. New `worker_outcome.py` inspects the existing Git checkout **read-only**, verifies active single ticket/base, exact allowed file zone, tracked/staged/untracked edits, clean diffs, and refuses redirects, unsafe paths or out-of-zone changes.
- A **completed** CLI turn with no worker commit but an eligible strictly scoped diff now returns `ready-for-host-verification` with **`accepted=false`** / **`tests_verified=false`**. It does not make a commit, land, claim test success, or retry AI. Only the existing trusted `controller.py` / `test_evidence.py` / `worktrees.finalize` may independently test, create a host-owned commit, land and accept. Out-of-zone changes, unchanged files and unsuccessful turns remain `incomplete` or `failed`.
- Real offline OS-process integration: synthetic Codex-like child made a valid `src/core/calc.py` edit **without committing** → read-only eligible handoff → trusted baseline Python tests → host finalize/land/accept/release. Negative OS subprocess tried to edit out-of-zone `test_core.py` → `incomplete` without acceptance. No paid provider calls.
- **Historical real 2026-10-25 paid CLI attempt inspected without replay:** temporary Git fixture was refreshed with local `worker_outcome.py` and `codex_dispatch.py`. Read-only `worker_outcome.py --root ... --ticket 01` reports **`eligible=false, reason=no-changes, changed_files=0`**. Thus this particular historical attempt produced **no retained source edits**, and cannot be recovered by host-finalizing an existing diff. Its recorded 53,528 token usage and non-replayable incomplete receipt remain unchanged.
- The verified provider-hard-cap gate from PR #10 **remains active** in both paid entrypoints. No confirmed provider-side per-call cap was found in the official Codex subscription usage guidance; plan limits/credits and their dashboards are not an enforceable per-request token ceiling. User's earlier paid-test consent remains valid, but no paid test in this stage. Preserve `2.3.0-dev` and no real production claim.
- **Verified:** local Windows Python 3.13 full **229/229 tests passed**, Dashboard JS syntax passed (2 inline scripts); [PR #11 CI #40245176985](https://github.com/mrAibo/Autopilot/actions/runs/40245176985) **4/4 passed** Ubuntu/Windows Python 3.11/3.13. Windows checkout cleanly fast-forwarded to merged `530d5808` on `main`. This STATUS-only checkpoint will trigger its own independent main CI, to be checked separately. Next P0: verifiable provider-side spend enforcement or clearly bounded alternative, privacy-safe diagnosis of real CLI tool failures, POSIX process containment and true parallel dispatch.

## P0 synthetic bounded Responses API qualification (2026-10-26)

- **Merged to `main`:** [PR #12](https://github.com/mrAibo/Autopilot/pull/12), squash commit `dd95fd11106fcfc2734b840efd4bd44e21d8acd2` on 2026-10-26. Branch `feat/p0-capped-api-pilot-20261026` based on `3afb1406`. No paid requests issued this stage.
- **Credential availability on connected Windows Aibo:** checked `OPENAI_API_KEY`, `OPENAI_PROJECT_ID`, `OPENAI_ORG_ID`, `CODEX_API_KEY` in process/user environment on 2026-10-26: none configured. The Python OpenAI SDK also absent. Do not infer API credentials from ChatGPT subscription or authenticated Codex CLI session. Consequently **no real Responses API request was attempted**, despite prior explicit user consent to paid token tests. Do not ask users to paste API keys in chat.
- Official GPT-6 Luna API model / current published pricing and Responses API output limit rechecked: `gpt-6-luna` supports Responses and structured outputs, `reasoning.effort=low`. Current standard short-context published token rates are $0.10/M input and $0.50/M output. These are not actual charges for this session and can change.
- Added isolated **test-only** `skills/autopilot/tools/bounded_api_pilot.py`: fixed `src/core/calc.py` addition bug under a disposable OS-temp strict Git project; exact user/test/zone/model/effort and consent marker; fixed `api.openai.com/v1/responses` TLS POST, **≤4096 serialized request bytes**, server-side `max_output_tokens=192`, no tools, no prior history, no auto retry, fixed strict JSON schema, explicit per-ticket approval. API key read only from process environment, never stored. No arbitrary app/project dispatch, no user-controlled URL. Critically, this **is not a provider-enforced monetary cap**, and the prior unrestricted Codex CLI paths still fail closed via `spend_guard.py`.
- One-shot fsynced receipt precedes HTTPS. A non-completed/error/timeout response blocks, never retries; only exact approved synthetic output and valid provider usage can be accepted. Reported usage is reconciled into Autopilot via `ap.py usage --source responses-api` **before** writing the single expected toy file, then the host must separately perform trusted Python tests, scoped commit, Git landing and acceptance. No AI process can mark accepted or execute model-supplied arbitrary code.
- **Verified:** 9/9 targeted `tests/test_bounded_api_pilot.py` passed with mocked HTTPS reply but real temporary Git worktrees/state/test execution/commit/landing. Negative cases include missing API key, wrong marker/zone, exceeded token report, incomplete/malicious response, timeout non-replayable receipt and no side effects. Full local Windows Python 3.13 **238/238 tests green**, Dashboard JS syntax passed. [PR #12 CI #40247616196](https://github.com/mrAibo/Autopilot/actions/runs/40247616196) **4/4 green** Ubuntu/Windows Python 3.11/3.13. Windows checkout fast-forwarded cleanly to merged `dd95fd1` on `main`. This STATUS-only checkpoint will independently trigger main CI and must be checked.
- Docs: `docs/autopilot/bounded-api-pilot.md`, English/Russian README and CHANGELOG; normal `ap.py` .gitignore now excludes temporary API pilot receipts and marker. This file is intentionally **not** deployed by Phase 0 into arbitrary application projects; it remains a deliberately narrow development-only qualification harness.
- **Next P0:** connect legitimate independent API credential using the machine's secure environment only after user provisions it and verifies account billing controls; then, with explicit one-shot ticket approval, consider a single tiny API request. Provider currency cap still not proven; keep previous `spend_guard` on Codex CLI. After actual model verification, investigate stronger process cancellation for POSIX and production-safe parallel orchestration.

## Return to original Autopilot 2.3 scope (2026-10-26)

- **Merged to `main`:** [PR #13](https://github.com/mrAibo/Autopilot/pull/13), squash commit `18f4cc0628518ec86fae82cc44bff3e0da867081` on 2026-10-26. Feature branch `fix/brief-scope-finish-ancestry-20261026` based on `ea07d19`. Version remains `2.3.0-dev`.
- The owner correctly observed scope creep. The original `brief.md` explicitly says **no wholesale rewrite, preserve the existing CLI and no paid API tests**. The required product is R01–R06: objective finish/gates, safe locking, economical model routing, responsive Dashboard, documentation and real regressions. The normal `/autopilot` should not require a new paid API key, background supervisor or an experimental worker.
- **R01 production bug fixed:** `ap.py finish` previously trusted `status=done` even if an accepted ticket's Git commit had disappeared from HEAD after a reset/rebase. It now rechecks every accepted ticket commit against current HEAD before stage mutation or final acceptance. A real temporary Git negative regression uses `reset --soft` to rewrite ancestry while preserving state, demonstrates `finish` refuses false success and does not change stages, result or project run directory.
- **Product clarity:** `docs/autopilot/scope-and-labs.md` categorizes core R01–R06 versus optional experiments. `SKILL.md` explicitly states that `bounded_api_pilot.py`, offline subprocess harnesses and API credentials are not prerequisites of the normal skill. Both READMEs now put the actual user journey before a short, transparent limitations summary; verbose experimental adapter explanations remain reachable through their existing specialist docs and status. No experimental modules removed, promoted or integrated into the default workflow.
- **Verified:** local Windows Python 3.13 **239/239 tests passed**, Dashboard JS syntax (2 inline scripts) passed, [PR #13 CI #40249998379](https://github.com/mrAibo/Autopilot/actions/runs/40249998379) **4/4 passed** Ubuntu/Windows Python 3.11/3.13. Local Windows worktree fast-forwarded cleanly to merge `18f4cc0` on `main`. This documentation-only checkpoint triggers another main CI, whose result must be verified separately. No new live/paid model calls and no changes to the owner's other projects.
- **Remaining core priorities:** verify supported Codex/Claude runtime routing honestly (a native named subagent was unavailable in the user-tested GUI), finish R01–R06 acceptance review, matched benchmarks and remaining Dashboard UX. Resist further API harness/dispatcher expansion unless an original requirement genuinely needs it.

## R03 original-brief model policy integration (2026-10-26)

- **Merged to `main`:** [PR #14](https://github.com/mrAibo/Autopilot/pull/14), squash commit `f7f6322cf49aee04207a3d5db6f3cac83affc7cb` on 2026-10-26. Feature branch `fix/r03-policy-merge-20261026` based on `4e7f817`.
- The final `main` CI for the preceding scope/finish correction ([#40250432426](https://github.com/mrAibo/Autopilot/actions/runs/40250432426)) **4/4 passed** Ubuntu/Windows Python 3.11/3.13.
- **R03 bug:** `model_router.load_policy()` previously shallow-overwrote the entire provider map when the user changed one model/Effort tier, dropping the other tiers/providers. `ap.py ticket NN route` did not accept custom policy at all even though `model_router.py` and `agent_profiles.py` supported one. This directly breaks the brief's configurable economical-routing policy.
- Fix: deep-copy and merge only explicit policy overrides, preserve built-in restricted deny lists when custom lists are supplied, validate unknown fields and exact names, and reject malformed settings fail-closed. The normal `ticket NN route --policy FILE` now uses one checked local project file for both model choice and native agent-profile rendering. Its SHA256 is recorded and required to remain current before strict `start`/`retry`/`done`. No independent API key, new worker, billing call or GUI capability claim.
- **Verified:** `test_model_router.py` 16/16, targeted `test_ap.py` policy cases passed; Windows Python 3.13 full suite **246/246 green**, Dashboard JS syntax passed. [PR #14 CI #40251787940](https://github.com/mrAibo/Autopilot/actions/runs/40251787940) **4/4 green on attempt 2**. On attempt 1, Windows Python 3.11 failed an **unrelated intermittent test** `test_real_offline_dispatch_accept_and_cancel_second` (`Supervisor exited before cancellation`); that specific job was rerun and passed. Do not omit this first-attempt failure; follow up if it repeats. Local Windows checkout cleanly fast-forwarded to merged `f7f6322` on `main`. This checkpoint-only commit triggers another main CI which must be checked separately. Docs: `docs/autopilot/model-routing.md`, CHANGELOG.
- Next: evaluate other R01–R06 gaps and regression tests, avoid adding unrelated research components. Version remains `2.3.0-dev`.

## R04 Dashboard state-to-HTML safety regression (2026-10-26)

- **Merged to `main`:** [PR #15](https://github.com/mrAibo/Autopilot/pull/15), squash commit `e601841d415af2bc253945133b57e29c6d12ca25` on 2026-10-26. Branch `fix/r04-dashboard-escape-rendered-state-20261026` based on `3ff2cda`. Local Windows checkout cleanly fast-forwarded to the merged source commit.
- **Verified preceding main CI:** [#40252664249](https://github.com/mrAibo/Autopilot/actions/runs/40252664249) **4/4 passed** Ubuntu/Windows Python 3.11/3.13.
- **R04 defect:** several state-driven values were inserted into HTML templates without `esc()` even though most user-supplied brief/ticket text was already escaped: `tests.passed`, error test counts, ticket wave labels/dependency text, G1/G3 gate details, the `data-from` attribute for live timers and boot error text. A malformed or manipulated state could inject markup in these paths; normal numeric states hid the problem.
- **Minimal fix:** escape only the above HTML boundaries, preserve existing visual styles, themes, languages, layout and 10-second refresh. No React/CDN, no external model calls, no new runtime dependencies.
- **Verified:** the new dependency-free `tools/test-dashboard-render.js` runs the actual Dashboard inline JavaScript in a Node VM: **7 hostile state fields + 1 English route + 1 boot error + 1 normal render** passed. The suite failed on the old template and passed after escaping the HTML boundaries. `tools/check-dashboard.py` runs both JS syntax and rendered-state checks. Local Windows Python 3.13 full **246/246 tests** passed; [PR #15 CI #40254233597](https://github.com/mrAibo/Autopilot/actions/runs/40254233597) **4/4 passed first attempt** Ubuntu/Windows Python 3.11/3.13, including Linux browser smoke and screenshot artifact. This STATUS-only checkpoint will trigger a separate main CI, which must be checked independently.
- Remaining brief: run actual browser screenshot smoke for narrow/wide, contrast and usability R04; quantify R06 benchmark on matched conditions. Optional API pilots are not on the default product path. Version remains `2.3.0-dev`.

## R06 paired offline benchmark — real host measurements, no AI cost claim (2026-10-26)

- **Merged to `main`:** [PR #16](https://github.com/mrAibo/Autopilot/pull/16), squash SHA `562ce5124a16db9723a20cb945e5e12c99e268c4` on 2026-10-26. Branch `feat/r06-matched-offline-benchmark-20261026` based on `38272a3c`. Preceding main CI [#40254675178](https://github.com/mrAibo/Autopilot/actions/runs/40254675178) 4/4 successful. No paid provider calls.
- Added `tools/benchmark-r06.py` for **matched offline host-only** comparison: reads immutable original 2.2.0 commit `25b5fbada50742f1b6a900a5a92800759e5c74d4` and 2.3-dev candidate `3eb5ecbfc05524d0095c6b53044c5d1e3f105560`, prepares clean temp Git repos for identical two predetermined workflows, alternates execution order, five repetitions each (20 samples). Collects `ap.py` invocations, Git commits, correct acceptance/rejection, and `perf_counter_ns` host durations. No LLM/model/subagent calls. Added `tests/test_r06_benchmark.py` with 5 deterministic, CI-safe contract tests that require no historical Git fetch or external APIs.
- **Observed host results (Windows Python 3.13):** empty invalid finish: 2.2 incorrectly accepted **5/5**, 2.3 correctly refused **5/5**; valid synthetic two-ticket finish: both accepted **5/5**, with **12 ap.py calls and 3 Git commits** each. Median valid host-only runtime: **2475.37ms vs 2011.82ms** (2.3 ~18.7% lower in this small local scenario; no general speed/cost claim). `off` optimization rules add **0 UTF-8 bytes**, `lean` adds **414 UTF-8 bytes**. **Actual input/output/cache tokens, billed money, model-based acceptance = unavailable (null)**, not zero.
- Raw results `docs/autopilot/benchmarks/r06-20261026-offline.json`; methodology `docs/autopilot/r06-offline-benchmark.md`; historical non-matched 1.x/2.0 distinguished. **Verified:** five dedicated R06 contract tests, Windows Python 3.13 full **251/251 Python tests**, Dashboard JS syntax and rendered-state injection checks. [PR #16 CI #40256338834](https://github.com/mrAibo/Autopilot/actions/runs/40256338834) **4/4 passed first attempt**, Ubuntu/Windows Python 3.11/3.13. Windows local clean fast-forwarded to merged `562ce51` on `main`. This STATUS-only checkpoint has its own main CI to verify separately.
- **Next R06 gap:** meaningful provider-token/cost-per-**accepted AI task** A/B still requires authorized real matching models/effort, real usage and accepted code, and is **not measured** here (original brief forbids paid API tests). Further work should target remaining original R01–R06 verification and Dashboard usability rather than adding more execution backends.

## R04 Dashboard real narrow viewport and label contrast (2026-10-26)

- **Merged to `main`:** [PR #17](https://github.com/mrAibo/Autopilot/pull/17), squash commit `b906ca2f8ab132a6b8d4eae8e5a740de7fac68ba` on 2026-10-26. Feature branch `fix/r04-browser-viewport-matrix-20261026` from clean `main` `5e047e3`; locally fast-forwarded cleanly to merge. No AI/API calls or new dependencies.
- **Identified false prior evidence:** Chromium headless silently clamps `--window-size=460,2100` and `390,2100` to **500 CSS px**: previous screenshots claimed a 460px test but actually exercised 500px CSS media queries.
- Repaired `tools/check-dashboard-browser.py`: headless browser opens same-origin iframe at exact **460 and 390 CSS px**; asserts actual `innerWidth` and `clientWidth`, no horizontal page overflow, correct navigation collapse, visible Dashboard sections/models/recovery text, labeled buttons, RU/EN and light/dark CSS. Four combinations: desktop RU/light, 460 RU/dark, 390 EN/light and 390 EN/dark.
- **Contrast improvement:** original light `--mut:#71819A` and `--quiet:#8391A4` were around **3.55:1 and 2.88:1** on inset #EFF3F9; below 4.5:1 for ordinary small labels. Dashboard 3.1 now uses light `--mut:#54657D`, `--quiet:#607084` and dark `--quiet:#899CB7`, including system-dark fallback. Actual headless browser reported contrast ≥ **4.53:1** for both secondary variables on all tested inset panels. This tests selected foreground/background pairs, not comprehensive WCAG conformance or screen-reader operation.
- Existing standalone HTML, 10s refresh, UI component tree and functional model logic preserved; Chrome/Edge testing in CI still runs with synthetic state. Screenshots include mobile at real CSS width and are uploaded as the Linux browser artifact.
- **R02 Windows race discovered during this PR:** the pre-fix local full **251-test** run and PR #17 first CI ([#40278022709](https://github.com/mrAibo/Autopilot/actions/runs/40278022709), Windows/Python 3.11) failed in old `test_windows_parent_kill_terminates_child_tree` before Job Object assignment. Adding exit diagnostics exposed reproducible `WinError 5: Access denied` from `os.replace(temporary_receipt, NN.json)` while the test's read-only poll opened the old receipt. `offline_supervisor.persist()` now retries only recognized temporary Windows WinError 5/32 with 12 bounded attempts and keeps old receipt on exhaustion; no paid execution/automatic worker retry. Added three portable negative/positive fault injection tests and fixed subprocess-pipe cleanup. Eight existing offline-supervisor integration tests and four extra isolated parent-kill repetitions passed locally before the real root cause was identified.
- **Second CI attempt [#40278659734](https://github.com/mrAibo/Autopilot/actions/runs/40278659734):** Ubuntu passed while Windows/Python 3.13 failed an unrelated existing Node VM Dashboard safety test with overly tight per-evaluation `timeout:1500ms` on a loaded runner. Raised bounded Node VM timeout to 5000ms (boot error 2000ms); model/runtime execution unchanged. Failed initial attempts remain documented.
- **Verified final:** full local Windows Python 3.13 suite **254/254 tests green** (saved diagnostic log), 11/11 offline-supervisor tests (8 existing + 3 new), Node JS syntax/injection probe, real local headless browser layouts/screenshots. [PR #17 CI #40279584601](https://github.com/mrAibo/Autopilot/actions/runs/40279584601) **4/4 green** Ubuntu/Windows Python 3.11/3.13 on fixed head `127f4ffa`. This STATUS-only checkpoint triggers a separate final main CI, which must be checked independently. No security limits disabled, no real model execution.
- Remaining original R01–R06 release blockers: authenticated host-native named agents in actual Codex GUI/Claude Code runtime not fully verified; independent per-accepted-real-AI-task cost A/B not measured; keyboard navigation end-to-end/a full accessibility audit is beyond this small browser smoke. Version remains `2.3.0-dev`.

## Documentation: three languages, existing projects, and agent-owned recovery (2026-10-26)

- **Merged to `main`:** [PR #18](https://github.com/mrAibo/Autopilot/pull/18), squash SHA `4825ed58ebe35d339af3762b469828d1d241a57a` on 2026-10-26. Feature branch `docs/trilingual-existing-project-recovery-20261026` based on `db33148`. No new model/API calls; version remains `2.3.0-dev`.
- The actual original root requirements file was named Cyrillic `бриф.md`. **Git-renamed it to `brief.md`** preserving its contents; repaired README EN/RU and `docs/autopilot/scope-and-labs.md` links. Run-created historic project files `<YYYY-MM-DD>-brief.md` retain their existing names; no application project's saved state/files were renamed.
- Added complete `README.de.md` with German installation, core stages, modes, security and transparency regarding unverified GUI agent support; language links now cross-reference English/Russian/German READMEs. Dashboard itself still only has RU/EN localization (explicitly stated).
- Added user-and-agent-facing **existing project continuation** (new requested feature on an existing codebase with no reinitialization, respecting dirty Git and user docs), **unfinished run resumption** (open same project dir in a new session, invoke bare `/autopilot`, agent reads `.autopilot/state.js`, memory, manifest, dated brief, tests/Git/worktrees and keeps completed work), and **new feature/reopen after a completed run**. No background self-restart, no two concurrent writers and no claim that unsaved model output can be recovered. The agent owns the steps, not the user; no auto `git reset --hard` or manual edits to `state.js`.
- Reinforced actual skill instructions in `SKILL.md` and `phases/0-resume.md` so this is not merely a README promise. Changed English phase file date placeholders to `<YYYY-MM-DD>-brief.md`, without altering the naming used on disk. Added `tests/test_documentation_locales.py` to verify all 3 languages, original brief rename, cross-links and the restart contract. Five targeted documentation tests passed; full local Windows Python 3.13 **259/259 tests passed**, Dashboard JavaScript syntax and injection-safety checks passed. [PR #18 CI #40285907776](https://github.com/mrAibo/Autopilot/actions/runs/40285907776) **4/4 green first attempt** (Ubuntu/Windows Python 3.11 and 3.13). Local checkout fast-forwarded cleanly to merged `4825ed5` on `main`. This status-only checkpoint triggers new `main` CI, which must be checked independently.
- This is a documentation / agent instruction improvement, **not an independently validated native host subagent crash/restart E2E**. No claim of automatic process resurrection; restart requires a new user-invoked agent session. Revisit R01–R06 requirements for 2.3 stable release only after real host capabilities have been demonstrated.

## R04 keyboard-focus / main-landmark hardening (2026-10-26)

- **Merged to `main`:** [PR #19](https://github.com/mrAibo/Autopilot/pull/19), squash SHA `b1c9bf2f9dd64b7ccc2255d520b8b76880b2cbae` on 2026-10-26. Feature branch `fix/r04-dashboard-keyboard-focus-20261026` started from clean local `main` HEAD `2bee5e8e4cc2d41b3531856a6fe985bf0ba15ad4`, finished at `dbf10d1c41ea1ac388d0288995dc7ddff0fc69e4`. Previous `main` [CI #40286602266](https://github.com/mrAibo/Autopilot/actions/runs/40286602266) passed. Both remote and local Git were checked before edits; initial worktree clean. Base Windows Python 3.13 suite: **259/259 passed**. Local Windows checkout subsequently fast-forwarded cleanly to merged `main`.
- **R04 defect:** `render()` replaces all of `#app.innerHTML` on language/filter interactions and refreshed live state. Focus on a button or rail anchor was lost even though a global focus-visible outline existed; keyboard users restart navigation. The project lacked a skip link and explicit HTML main landmark.
- **Targeted patch:** capture only a focused application's stable locally generated action identifier, restore its replacement by exact tag/attribute match after render with `focus({preventScroll:true})`; leave focus outside the app alone. Add RU/EN focus-revealed skip link to `#mission`, focusable section targets and restoration after jumping to a section, semantic `<main>` landmark, stable rail anchor keys and reduced-motion scroll preference. Keep the independent English/Russian toggle, theme, state snapshot, 10-second refresh, standalone HTML and no CDN.
- **Real browser regression:** existing headless Chrome four-layout matrix (desktop RU/light, 460 RU/dark, 390 EN/light and 390 EN/dark) asserts keyboard-focus retention after a genuine language button click, a subsequent rerender, skip-link and desktop nav focus, proper label and landmark. Desktop and the three exact-width layouts passed locally; Node VM escaped-state tests and JS syntax also passed. This checks programmatic DOM focus retention, **not** physical Tab-key traversal, screen-reader use, or full WCAG certification.
- **Validation:** local Windows Python 3.13 full **259/259 passed** (baseline before edits also 259/259); JS syntax (2 inline scripts), Node rendered-state injection, Chrome/Edge actual layout/focus four cases and `git diff --check` all passed. Browser assertions also prove re-render does not steal focus from an external element. Final [PR #19 CI #40288846093](https://github.com/mrAibo/Autopilot/actions/runs/40288846093) passed **4/4 jobs** (Ubuntu/Windows, Python 3.11/3.13) on exact feature HEAD `dbf10d1`. This STATUS-only commit will start separate `main` CI; verify independently. No new model/subagent execution, paid API calls, dependencies, or other application edits. Version stays `2.3.0-dev`; do not claim full screen-reader or physical keyboard E2E.

## R03 Claude Code strict hook integrity and host capability qualification (2026-10-26)

- **Merged to `main`:** [PR #20](https://github.com/mrAibo/Autopilot/pull/20), squash SHA `a566fb0d994326d82dc9f239c5e0b860f78fc58c` on 2026-10-26. Feature branch `fix/r03-claude-guard-corrupt-state-20261026`, head `de4a56dc51ab2a49b71dcc7afe4de0b97acab5e9`, based on clean `main` `be1833b7146ff47fe7fa16ea129d987cdc9b0ccc`. The preceding `main` [CI #40289459721](https://github.com/mrAibo/Autopilot/actions/runs/40289459721) passed **4/4** Ubuntu/Windows Python 3.11/3.13 jobs. Local Windows `main` fast-forwarded cleanly to the merge. No paid provider calls or native GUI agent attempts.
- **Read-only host results:** on connected Windows `Aibo`, `codex-cli 0.165.0-alpha.1` reports `multi_agent=stable/true` and `multi_agent_v2=stable/false`; standard Codex CLI `exec` flags for model/sandbox/cwd/JSONL are present. This is **not** proof that the Codex GUI can select a named custom child: the earlier owner's actual named-agent GUI smoke failed closed and has not been repeated without a new capability change. No `claude` or `claude-code` executable was found on PATH, at known npm/native user paths or global npm package list; real Claude Code execution remains **unverified** (general Claude desktop != Claude Code).
- **Confirmed R03 safety defect:** optional `claude_agent_guard.decision` previously treated malformed/unreadable existing `.autopilot/state.js` as absent state, permitting arbitrary `Agent|Task` invocations even if the saved strict policy could not be read. It now distinguishes *absent* state (allow ordinary unrelated Claude project) from existing but malformed, redirected or structurally invalid state (**deny**), rejects non-boolean strict flag, and preserves normal non-agent calls. The optional `PreToolUse` guard's narrow scope is unchanged; do not claim enforcement by an uninstalled Claude Code runtime.
- **Targeted evidence:** 20/20 Claude guard tests passed locally, including six direct negative/compatibility state checks and three real Python hook subprocess stdin/exit-code checks. Only temporary synthetic project fixtures were used. No new dependencies, API credentials, framework components, worker daemons or actual model calls.
- **Verified full QA:** Windows Python 3.13 local full **270/270 passed** (259 baseline + 11 R03 tests). [PR #20 CI #40290846258](https://github.com/mrAibo/Autopilot/actions/runs/40290846258) **4/4 passed** first attempt Ubuntu/Windows Python 3.11/3.13 on the exact feature head. STATUS-only merge checkpoint will trigger independent `main` CI; verify independently. No AI-model calls, provider billing or CLI installation. Stable release is **not** claimed; `2.3.0-dev` remains. See `docs/autopilot/gui-clients.md`. Next: investigate actual host GUI supported named-agent runtime only after concrete capability change; Claude Code CLI needs installation/discovery and genuine host execution before verification.

## R06 host test evidence integrity — forged receipt regression (2026-10-26)

- **Merged to `main`:** [PR #21](https://github.com/mrAibo/Autopilot/pull/21), squash commit `dafeb88a164e7484bb90b36fee9516f13096de12` on 2026-10-26. Feature branch `fix/r06-host-evidence-recheck-20261026` started from clean `main` `1ad0efee2f46184f72526cbf474e3ca3f83e1729`, finished at `35eb69cb13d88e88c84bd6915e230f24de6c73b9`. The previous PR #20 and `main` CI each **4/4 green**. Windows local `main` fast-forwarded cleanly.
- **Reproduced acceptance defect:** `test_evidence.check` accepted hand-crafted `{"status":"verified","runner":"python-unittest","passed":999,"failed":0,...}` from state with authentic worktree HEAD/fingerprint and a baseline-tracked test suite that **actually failed**. A second negative test inflated counts on a legitimate passing receipt; both failed before the patch (no `EvidenceError`), proving lack of attestation by serialized `state.js`. No existing production workspace or live model involved.
- **Patch:** `check` first enforces the existing approved suite/commit/fingerprint, then re-executes the same unchanged baseline-tracked Python unittest in the actual ticket worktree; compares real pass totals, process success and pre/post source integrity. `verify` records its bounded `timeout`; older saved receipts default to 90 seconds. Recheck incurs an additional test execution at host acceptance and must not be misrepresented as a signed receipt or protection against malicious approved tests.
- **Validation:** Two negative tests demonstrated the pre-patch failure (both failed because forged evidence was wrongly accepted), then turned green; third new test confirms old receipts without timeout remain compatible. Targeted suite **8/8**, full local Windows Python 3.13 **273/273**, [PR #21 CI #40293184857](https://github.com/mrAibo/Autopilot/actions/runs/40293184857) **4/4 successful** Ubuntu/Windows Python 3.11/3.13. A status-only checkpoint commit creates separate `main` CI to verify. Scope: R01 objective acceptance and R06 negative regression tests; optional strict isolated worktree path. `2.3.0-dev` remains; no paid model invocations.
- **Open:** ignored test dependencies, user-modified runtime/testing environment, external GUI native subagents, and A/B paid task costs are **not** solved by this patch. Follow `docs/autopilot/worktrees.md`.

## R06 strict test inputs: ignored Python and inherited environment (2026-10-26)

- **Merged to `main`:** [PR #22](https://github.com/mrAibo/Autopilot/pull/22), squash commit `e691eac3c84af961103ebfe1978be0ecb022c4ac` on 2026-10-26; feature branch head `73a106f8e7c1fb1a70adc9d5668d7530ccd710db`, from clean `main` `d03fd7f611338496c1c91d2e205cce2662a528d3`. Prior merged [main CI #40293850121](https://github.com/mrAibo/Autopilot/actions/runs/40293850121) **4/4 successful**. Local checkout fast-forwarded cleanly.
- **Observed fail-open:** before patch, temporary strict-isolated worktree tests confirmed (a) an ignored Python module was successfully imported by an approved tracked unittest while missing from the Git evidence fingerprint; (b) inherited host `PYTHONPATH` pointed a tracked test to a module outside the worktree. Both negative tests failed as intended before the fix and passed after it. No provider model calls.
- **R06 patch:** `test_evidence.fingerprint` now fails closed on ignored Python source, bytecode, importable archive and extension inputs (`.py/.pyw/.pyc/.pyo/.pyd/.so/.pth/.zip/.egg/.whl`, case-insensitive, nested). It never displays ignored filenames. Test runner strips inherited `PYTHON*` environment variables, then sets `PYTHONDONTWRITEBYTECODE` and `PYTHONNOUSERSITE` to safe values. Check now also rejects ignored Python files added after a prior passing receipt.
- **Bounds:** non-Python ignored data (`.env`, JSON, etc.) remain untracked by design and can affect tests if explicitly loaded; installed packages/interpreter/PATH and trusted test source are not independently attested. Ignored Python generated files / virtualenv may now block strict checks until removed or separately operator-reviewed. No claim of hermetic test sandbox or signed evidence. Read-only GUI runtime check: Codex Windows app `26.1021.3705.0`, bundled CLI `0.164.0-alpha.11.1` still reports `multi_agent=true`, `multi_agent_v2=false`; external Codex CLI `0.165.0-alpha.1` unchanged. Claude desktop installed `1.9255.2.0`, but no `claude`/`claude-code` command available. Neither host demonstrates supported native named-agent execution; no paid GUI probe repeated.
- **Validation:** 15/15 targeted test-evidence cases including ignored Python added between `verify` and `check`. Full local Windows Python 3.13 **280/280 passed** (273 baseline + 7 new). [PR #22 CI #40296567664](https://github.com/mrAibo/Autopilot/actions/runs/40296567664) **4/4 passed** Ubuntu/Windows Python 3.11/3.13 on exact branch SHA. This STATUS-only checkpoint generates a separate `main` CI run; verify independently. No new dependencies or billable API calls. Keep `2.3.0-dev`.

## Prioritized next steps

**P0 — GUI native execution:** Codex GUI named-agent selection **tested and unavailable in the owner's 2026-10-25 session** (see negative evidence above). Do not repeat the same paid probe without a meaningful configuration/runtime change. A first one-shot approved CLI fallback is implemented in the GUI bridge
(one authorized real CLI call has now run but was **incomplete**, with no worker commit or acceptance); strengthen budget enforcement, diagnosis and host launch evidence before calling it production-ready; re-test genuine native GUI child model/effort/cwd only after a concrete capability change. Test actual **Claude Code** separately (not general Claude chat). If child identity and model cannot be confirmed, block strict custom-agent dispatch.

**P0 — orchestrated lifecycle (remaining, optional research; not a stable 2.3 prerequisite):** PR #7 implements the host loop, PR #8 offline subprocess attempts, PR #9 Windows Job Object containment, PR #10 blocks unbounded real Codex calls, PR #11 adds host finalization for scoped uncommitted edits, and PR #12 qualifies a fixed temporary API toy path using mocked HTTPS, not a real paid API call. PR #13 restores priority to the original product brief. **Not yet implemented:** Linux/macOS parent-crash containment, production identity/reconciliation, enforced provider per-call spending cap, successful independently verified real-model worker acceptance or parallel AI dispatch. One previously authorized CLI turn ended **`incomplete`** and recorded 53,187 input + 341 output despite a 2,000-token soft threshold; **no further paid calls without genuinely bounded/explicitly reconciled risk**.

**P1 — broader verification and costs:** Extend trusted tests beyond one baseline-tracked Python unittest module (e.g. pytest, JS/TS) without executing arbitrary unapproved commands. PR #21 blocks forged saved test counts; PR #22 rejects ignored Python executable inputs and inherited Python startup paths, **not** ignored non-Python data or malicious runtimes. R06 **host-only** paired 2.2/2.3 comparison is complete in PR #16; it establishes no real LLM token savings. Actual `lean` vs `off` provider A/B, cost per **accepted AI task**, cached input and verified pricing require separately authorized successful real model tests; do not speculate or add more API layers.

**P2 — release qualification:** Reconcile GUI/runtime capability checks, installer/provenance, documentation, performance and security review. Only then consider changing `2.3.0-dev` to stable `2.3.0` and tagging a release.

## New-session resume instruction

> Продолжи разработку Autopilot 2.3 в репозитории `mrAibo/Autopilot`. Сначала проверь актуальную Git-ветку, `git status`, `HEAD`, последний merge/CI и раздел **Latest merged checkpoint** ниже; если в `STATUS.md` зафиксирована незавершённая feature-ветка, продолжай её, а не создавай новую. Прочитай `STATUS.md`, `brief.md`, `skills/autopilot/SKILL.md`, `docs/autopilot/scope-and-labs.md` и документы соответствующего текущего этапа. Проверь Windows checkout и Junction-навыки. Версия пока `2.3.0-dev`, без release tag. Сохраняй STATUS после этапов, не имитируй native GUI child-agent E2E, не запускай новые платные API-эксперименты по инерции и не объявляй релиз без настоящей проверки. Для восстановления **работы Autopilot внутри пользовательского проекта** (это отдельный случай!) используй `skills/autopilot/phases/0-resume.md` и `/autopilot` в папке этого проекта.

**Local Windows:** connected device `Aibo`, device ID `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`; repo `C:\Users\crown\Downloads\Projects\Autopilot`; Python `py -3.13`; Codex npm binary in `%APPDATA%\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`. GitHub account `mrAibo` connected. Disposable synthetic fixture has released T01; do not repeat paid calls there.

**Latest merged checkpoint:** PR #22 (`e691eac`) fixes **R06 ignored Python / inherited host Python environment affecting strict independent tests**. Before the patch, a tracked unittest could import a Git-ignored `.py` and a helper from inherited `PYTHONPATH` outside the worktree; both issues were reproduced in failing negative tests. Strict isolated test fingerprints now block ignored Python executable/importable inputs, including nested paths and uppercase extensions; the test runner drops inherited `PYTHON*` settings before fixed bytecode/user-site flags. Seven new cases include addition of hidden Python after `verify` and ordinary JSON compatibility. Local Windows Python 3.13 **280/280** and [PR #22 CI #40296567664](https://github.com/mrAibo/Autopilot/actions/runs/40296567664) **4/4 green**. Local `main` fast-forwarded cleanly. Read-only host discovery confirms bundled GUI Codex CLI `0.164.0-alpha.11.1` / `multi_agent_v2=false`; Claude Desktop exists but actual Claude Code CLI absent; native named GUI child model/effort/cwd remains unverified. This is not hermetic validation of ignored data or system Python packages. PR #21 serialized evidence rechecking and PR #20 Claude Code hook guard remain merged. Next priority: decide supported native host qualification / release R01–R06 checklist, without paid unbounded probes; maintain `2.3.0-dev`, no stable release.

**Hot code:** `skills/autopilot/tools/{ap,bounded_api_pilot,worktrees,codex_dispatch,worker_outcome,spend_guard,test_evidence,model_router,agent_profiles,codex_capabilities,scheduler,controller,host_loop,gui_bridge,offline_supervisor,offline_fixture_worker,process_containment,process_gate}.py`; `tests/{test_documentation_locales,test_ap,test_model_router,test_bounded_api_pilot,test_worktrees,test_codex_dispatch,test_spend_guard,test_test_evidence,test_host_loop,test_offline_supervisor,test_gui_bridge_e2e}.py`. Standard test: `python -m unittest discover -s tests -q`. Maintain LICENSE and one-skill-directory Junctions.
