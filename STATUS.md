# STATUS.md — Autopilot 2.3 handoff

**Updated:** 2026-10-25 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Active branch:** `main`
**P0 Codex native-agent guard:** [PR #2 merged](https://github.com/mrAibo/Autopilot/pull/2); `main` now contains verified fail-closed V1/V2/TOML checks. This is not native GUI E2E.
**Merged:** [PR #1](https://github.com/mrAibo/Autopilot/pull/1), squash commit `00600107be80fdb54015611647c767954aa096be` on 2026-10-25. Owner explicitly approved promotion to main after confirming the skill appears in Codex GUI.
**Development history:** `feat/autopilot-2.3-adaptive-router-dashboard` (192 commits retained; do not rely on it as the current deployment branch).
**Version:** `metadata.version = 2.3.0-dev`. This is a **main-branch development snapshot**, NOT a final 2.3.0 release. No stable release tag. Do not confuse publishing to main with feature-complete GUI runtime support.
**Specification:** `бриф.md`. Read this STATUS first when resuming work; update it after every milestone.

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

## Prioritized next steps

**P0 — GUI native execution:** Codex GUI named-agent selection **tested and unavailable in the owner's 2026-10-25 session** (see negative evidence above). Do not repeat the same paid probe without a meaningful configuration/runtime change. A first one-shot approved CLI fallback is implemented in the GUI bridge
(without a paid GUI end-to-end test); extend its acceptance and host launch
proof before describing it as production-ready; re-test genuine native GUI child model/effort/cwd only after a concrete capability change. Test actual **Claude Code** separately (not general Claude chat). If child identity and model cannot be confirmed, block strict custom-agent dispatch.

**P0 — orchestrated lifecycle:** Implement a host-side execution/controller loop that consumes `ap.py schedule` plan, validates approval, launches bounded workers, handles cancellation/crash, independently verifies trusted test suites, finalizes/lands exactly once and records results. Keep fail-closed budget/sandbox boundaries. Validate with at least two independent tasks and a recoverable failure.

**P1 — broader verification and costs:** Extend trusted tests beyond one baseline-tracked Python unittest module (e.g. pytest, JS/TS) without executing arbitrary unapproved commands. Make evidence tamper-resistant and verify ignored-file handling. Import provider usage reliably, price with verified versioned data, benchmark cost per **accepted** task. Compare `lean` vs `off` and 2.2 vs 2.3 under matched conditions; no speculative savings.

**P2 — release qualification:** Reconcile GUI/runtime capability checks, installer/provenance, documentation, performance and security review. Only then consider changing `2.3.0-dev` to stable `2.3.0` and tagging a release.

## New-session resume instruction

> Продолжи проект Autopilot 2.3 из GitHub `mrAibo/Autopilot`, ветка **`main`**. PR #1 уже squash-merged (`00600107`); версия пока `2.3.0-dev`, без release tag. Прочитай актуальные `STATUS.md`, `бриф.md` и `docs/autopilot/{gui-clients,model-routing,worktrees,codex-cli,optimization}.md`. Проверь HEAD/CI, локальный Windows checkout, Junction-навыки и продолжай приоритеты P0 без нового перепланирования. Сохраняй STATUS.md после каждого этапа, не объявляй GUI E2E или стабильный релиз без настоящих проверок.

**Local Windows:** connected device `Aibo`, device ID `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`; repo `C:\Users\crown\Downloads\Projects\Autopilot`; Python `py -3.13`; Codex npm binary in `%APPDATA%\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`. GitHub account `mrAibo` connected. Disposable synthetic fixture has released T01; do not repeat paid calls there.

**Hot code:** `skills/autopilot/tools/{ap,worktrees,codex_dispatch,test_evidence,model_router,agent_profiles,codex_capabilities,scheduler}.py`; `tests/{test_ap,test_worktrees,test_codex_dispatch,test_test_evidence}.py`. Standard test: `python -m unittest discover -s tests -q`. Maintain LICENSE and one-skill-directory Junctions.
