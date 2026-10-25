# STATUS.md — Autopilot 2.3 development handoff

**Last updated:** 2026-10-25 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Branch:** `feat/autopilot-2.3-adaptive-router-dashboard`
**PR:** https://github.com/mrAibo/Autopilot/pull/1 — **Draft, NOT merged**
**Working branch HEAD before this STATUS-only update:** `1af3633e750d2b53db2d84e8229ef87e0715056d`; the STATUS commit itself advances HEAD, check GitHub branch before resuming.
**Baseline main:** `25b5fbada50742f1b6a900a5a92800759e5c74d4` (2.2.0)
**Release:** 2.3.0 UNDER DEVELOPMENT; no final tag, no merge to main without review.
**Specification:** `бриф.md`. State handoff is this file; update after each implementation milestone.

## Latest verified CI and local Windows validation

- **Latest completed full-branch CI [#40196940398](https://github.com/mrAibo/Autopilot/actions/runs/40196940398):** all **4/4** Ubuntu/Windows Python 3.11/3.13 jobs green, **144 Python tests** on Ubuntu 3.13, JavaScript syntax and headless Chrome wide/narrow dashboard smoke green. This includes the README/status updates following independent host test evidence. This STATUS-only commit itself advances HEAD and requires its own new CI; check its status when resuming.
- On the connected Windows computer (`Aibo`), local clone `C:\Users\crown\Downloads\Projects\Autopilot` is on the development branch; last synced source `9a5250b`, clean. **13/13 `test_worktrees.py` and 13/13 `test_codex_dispatch.py`** passed under Python 3.13. Use `git pull --ff-only` after future GitHub commits.
- Codex CLI **0.165.0-alpha.1** is installed from official NPM under `%APPDATA%\npm`; `codex login status` succeeded using ChatGPT. Existing graphical Codex app `OpenAI.Codex` 26.1021.3705.0 and Claude desktop AppX are installed. Native Codex CLI `codex.exe` is under `%APPDATA%\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`. The desktop-managed binary was not replaced.
- User disabled VPN: `codex doctor` reached **21 ok / 0 fail**; WebSocket and required provider HTTP endpoints reachable. `codex debug models` resolves account-visible GPT-6 Luna, GPT-6 Sol, GPT-6.1 Sol etc. `codex_capabilities.py` imported live catalog and routed a trivial task to `gpt-6-luna/low`.

## NEW: actual standalone Codex model and worktree E2E (verified)

A disposable *synthetic only* Git repository was created at `%TEMP%\autopilot-23-codex-e2e-20261025` (not a user's project). Autopilot `init --strict-routing --isolated-tickets` → manifest/ticket publication → real account catalog → approved `gpt-6-luna/low` route → pinned native profile → Git worktree prepare → ticket start → `codex_dispatch.py` dry-run preflight all passed.

- Two separate read-only standalone Luna/Low CLI requests **returned real expected text** and token totals: `CODEX_OK` (5 seconds, 19,718 input / 12,672 cache-read / 7 output) and `CONFIG_ISOLATED_OK` (4 seconds, 16,643 input / 11,776 cache-read / 9 output). The initial apparent hang was caused by leaving stdin open in the remote test harness; passing the prompt to stdin and closing it fixed that.
- An attempted actual `codex_dispatch.py --execute` **finished a model turn but created no commit**: on Windows `--ignore-user-config` had removed its required Windows sandbox backend. This matches a known Windows Codex issue; adding `-c windows.sandbox="elevated"` explicitly while **retaining** `--sandbox read-only|workspace-write` allowed sandboxed shell reads.
- With the supported backend and workspace-write sandbox, the model **did edit `calc.py`** in the isolated worktree, but it could not find `python` inside the sandbox and could not write `.git/worktrees/T01/index.lock` in the main Git metadata directory outside its writable root. This was observed from actual CLI JSONL command events; **never** silently disable the sandbox or claim successful tests/commit from that model turn.
- A trusted host process independently ran the synthetic tests: **2/2 successful**; after checking that only `calc.py` had changed (and deleting only confirmed generated `__pycache__/*.pyc` in this temporary fixture), it created commit `262b83e`. `ap.py worktree 01 land --tests 2/0` cherry-picked to `e7e1975`; `ap.py ticket 01 done` succeeded and `ap.py worktree 01 release` succeeded. The disposable main file has `return a + b`.
- This **confirms a real model made the code edit and the complete test/accept/land/release path works** with a host-created commit. It does **not** prove that the new `worktree finalize` command itself was used on a real paid task (it was added afterward and validated in CI), nor does it constitute a full G1–G4 final project acceptance.
- Model-turn != task acceptance: `codex_dispatch.py` now reports `incomplete` / nonzero exit if no clean single worker commit exists, while reporting tokens truthfully. A clean commit produces `ready-for-review`, **not accepted**, until independent tests and ledger gates pass. Its token reporter uses explicit UTF-8 to avoid Windows cp1252 decoding warnings. No real user project source was touched.

## NEW: reusable host-side Git finalization

- `worktrees.finalize(root, ticket, base, zones, passed, failed)` and `ap.py worktree NN finalize --tests N/0` support the documented Windows split: **model edits only inside the restricted worktree; trusted host independently tests and commits outside the sandbox**.
- Refuses failed/unconfirmed test counts, unknown/wildcard/unsafe zones, out-of-zone/untracked changes, symlink/junction redirects, dirty main checkout and stale base HEAD. Stages **only** allowed files, commits exactly once, then the existing `land → done → release` gates apply. Does not run arbitrary tests, delete untracked files, or overwrite source. An operator is responsible for truthfully verifying N/0 first; reported counts alone are not proof of execution.
- Existing Git crash recovery uses `cherry-pick -x`, patch IDs and `worktree recover` with no automatic destructive reset. Scheduler `ap.py schedule --max-parallel 2` is read-only and does not spawn models.
- **Windows-specific fix:** `safe_target` checks actual symlinks/junctions instead of comparing raw to normalized case-sensitive paths; both OS variants passed CI.

## NEW: Ponytail-inspired optional optimization — not yet benchmarked

- Source: [Ponytail](https://github.com/DietrichGebert/ponytail), with [JetBrains independent study](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/). Results on their tasks do not automatically transfer to Autopilot.
- `codex_dispatch.py --optimization lean` opt-in adds a **small original** reuse/stdlib/small-diff instruction. `off` is default. It NEVER permits skipping tests, validation, security, error handling or accessibility. **This is NOT the upstream Ponytail plugin**; no global installation or startup hook has been performed.
- See `docs/autopilot/optimization.md` for pairing methodology: equal model/effort, code baseline, independent accepted-task tests, actual input/output/cache and time; no claim of measured cost/token savings yet. JetBrains found upstream activation requires a Claude Code hook; merely copying SKILL.md did not work in their trial.

## Core 2.3 work completed in earlier milestones

- Manifest G1–G4 strict completion, task state and Git commit validation, concurrency state locks, requirement reconciliation, bounded retries and deterministic failure triage.
- Explicit approved provider/model/effort routing; deny premium subagent families by default; native pinned `.codex/agents/*.toml` and `.claude/agents/*.md` SHA-verified profiles. Optional Claude Code `PreToolUse` guard; actual graphical agent model inheritance remains unverified.
- Opt-in isolated per-task worktrees with safe cherry-pick/recovery/release, deterministic model-aware read-only scheduler, manually reported per-call token/budget events.
- Dashboard 3.0 responsive activity, gates, token/cached reports, worktree status, retry advice and wide/narrow browser CI.
- OpenAI NPM CLI binary and all project scripts are separate from global stable Autopilot 2.2. **Existing** `%USERPROFILE%\.agents\skills\autopilot` is global 2.2; Claude global skill junction points to it. Do not overwrite it with draft 2.3. Under Windows Git `core.symlinks=false`, checked-in `.agents/skills/autopilot` and `.claude/skills/autopilot` are plain text placeholders, not functioning skill links. See `docs/autopilot/gui-clients.md`.

## NEW: GUI skill smoke workspace (links, not copies)

- Isolated Windows workspace `%TEMP%\\autopilot-gui-skill-smoke-20261025` was created. It has **three real Junction directories**, each pointing to the SAME source folder `C:\\Users\\crown\\Downloads\\Projects\\Autopilot\\skills\\autopilot`: `.agents\\skills\\autopilot`, `.claude\\skills\\autopilot`, and `.codex\\skills\\autopilot`. All three paths passed `Test-Path SKILL.md=True` and are reported as `Junction`, not text placeholders.
- The existing global stable `%USERPROFILE%\\.agents\\skills\\autopilot` version 2.2 and its Claude Junction are untouched. This disposable workspace is prepared for **GUI discovery tests**, but neither Codex GUI nor Claude Code GUI has yet confirmed loading the skill or executing a model. The connected Desktop Commander provides filesystem/terminal access but no verified graphical GUI click integration.
- Next: open this exact disposable folder as a project in the graphical Codex app, reload skill discovery and inspect whether `/autopilot` is available. Do likewise only in actual Claude Code desktop integration, not generic Claude chat. Do not edit the global 2.2 install.

## NEW: independently measured host test evidence (2026-10-25)

- **Strict routing plus isolation now requires independent test evidence.** The new `skills/autopilot/tools/test_evidence.py` is copied by `0-instruments.md`. Command: `ap.py worktree NN verify --suite test_example.py [--timeout 90]`. The trusted host itself invokes a baseline-tracked, unchanged Python unittest suite inside the exact worktree with direct argv, `-B`, bytecode disabled, bounded timeout (10–300s), real test count and exit-0/OK parsing. This does not trust an executor's claimed N/0.
- The verifier fingerprints the worker Git HEAD, tracked diff and nonignored untracked content before/after the test; stores suite, count, source fingerprint, head and time in `tk.testEvidence`. Strict `worktree finalize`, `land`, `recover-land` and `ticket done` refuse missing/invalid/mismatched evidence. Wrong user-provided `--tests N/0` or source changed after testing are rejected. Legacy non-strict runs retain the previous explicitly reported counts for backwards compatibility.
- New `tests/test_test_evidence.py` negative tests: fake/failed tests, modified suite, path traversal and changed source after verification. Integrated `tests/test_ap.py` strict isolated scenario exercises `route → prepare → start → verify → finalize → land → done → release`; it also attempts false counts and source tampering. Targeted test passed on connected Windows device (Python 3.13); **CI #40196712436 passed 144/144 tests across four OS/Python jobs**.
- The verifier is **not cryptographic attestation** against an attacker editing `state.js`, ignored files or test process environment. Tests are executable Python code, so only run suites that the operator trusts. Pytest and arbitrary test commands are not yet supported; keep failing closed for unsupported suites. See `docs/autopilot/worktrees.md`.
- The GUI Codex/Claude Code skills share the same project files and can use this host-side verifier. **No native GUI session model/effort/cwd selection has yet been demonstrated**, so do not infer full GUI support from this CI.

## Remaining blockers and next steps

1. **P0** Actual graphical Codex app and Claude Code GUI integration: verify the shared skill is discovered using supported registration or an isolated test workspace Junction, model picker/effort and native custom agents, cwd and approval controls. Do **not** confuse the generic Claude app with Claude Code and do not claim GUI E2E yet.
2. **P0** On disposable Windows fixture, independently run tests and invoke the **new** `worktree finalize --tests N/0` with actual modified files, then land/accept/release; this complements the earlier successful manual host-commit E2E. Keep sandbox enabled.
3. **P0 partially completed:** Python unittest host evidence with source fingerprint is now mandatory for strict isolated finalize/land/acceptance. Still needed: trusted test-suite policy beyond single unchanged unittest module, evidence resistant to direct state tampering, broader source-zone enforcement across external tools, and multi-ticket recovery. Scheduler currently plans only; it does not autonomously launch/monitor native agents.
4. **P1** Optional upstream Ponytail Claude Code plugin evaluation in isolated workspace (not global) and controlled A/B lean/off with accepted-task quality and real tokens; no unmeasured cost claims.
5. **P1/P2** Actual model/billing identity, usage ingestion and comparable 2.2 vs 2.3 metrics, installer and provenance audit (`skills-lock.json`), release documentation. Keep PR Draft and `main` unchanged.

## Resume in a new ChatGPT session (copy)

> Продолжай Autopilot 2.3 в GitHub `mrAibo/Autopilot`, ветка `feat/autopilot-2.3-adaptive-router-dashboard`, draft PR №1. Прочитай `STATUS.md`, `бриф.md` и `docs/autopilot/{gui-clients,codex-cli,worktrees,optimization}.md`, проверь актуальные GitHub HEAD и CI. Прочитай последний новый раздел STATUS про реальную Windows E2E, Git sandbox и опциональную Ponytail-политику. Продолжай оставшиеся P0/P1 без перепланирования, не трогай `main` и глобальный Autopilot 2.2. После этапов обновляй STATUS.md.

**Local environment:** Connected Aibo Windows Desktop Commander device `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`; repository `C:\Users\crown\Downloads\Projects\Autopilot`; synthetic fixture `%TEMP%\autopilot-23-codex-e2e-20261025` has **completed/released ticket 01**, don't repeat model calls on it. `py -3.13` available. Current NPM Codex CLI `0.165.0-alpha.1`, logged in with ChatGPT. No credentials should be exposed in messages.

**Primary files:** `skills/autopilot/tools/{ap,worktrees,codex_dispatch,model_router,agent_profiles,codex_capabilities,scheduler}.py`; `tests/{test_ap,test_worktrees,test_codex_dispatch}.py`. Test with `python -m unittest discover -s tests -v`; check workflow matrix and dashboard/browser smoke.

**Keep this file authoritative and updated: do not substitute older chat summaries for the actual GitHub HEAD/tests.**
