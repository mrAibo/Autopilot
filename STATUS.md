# STATUS.md — Autopilot 2.3 development handoff

**Updated:** 2026-10-25, Europe/Berlin
**Repository:** https://github.com/mrAibo/Autopilot
**Working branch:** `feat/autopilot-2.3-adaptive-router-dashboard`
**PR:** https://github.com/mrAibo/Autopilot/pull/1 — **open, Draft, NOT MERGED**
**Source checkpoint before STATUS.md update:** `d636a6ba012ba9354d6282575ffddde7740f2c3d` (latest code/docs before this status commit). STATUS.md itself advances HEAD.
**Original base:** `25b5fbada50742f1b6a900a5a92800759e5c74d4` (Autopilot 2.2.0)
**Target:** Autopilot 2.3.0, NOT RELEASED.
**Authoritative specification:** `бриф.md`. Keep `main` untouched until release review/approval.

## Current verified checkpoint

- Most recent completed **application-code** CI: [GitHub Actions run 40188502124](https://github.com/mrAibo/Autopilot/actions/runs/40188502124), at commit `b9e6b9b5987dd1688cb0d05d48ff6ed849e6a2ef`: **all four jobs green** on Ubuntu/Windows with Python 3.11 and 3.13; **115 Python tests** on Ubuntu 3.13, dashboard JavaScript syntax and headless Chrome DOM checks for wide/narrow layouts.
- Subsequent milestone: [GitHub Actions run #40190471119](https://github.com/mrAibo/Autopilot/actions/runs/40190471119), code checkpoint `94422b0bda30e9ff068ffeee86c69b6b97de0d6b`: all 4 Windows/Linux 3.11/3.13 jobs passed, **126 tests** on Linux 3.13, Dashboard syntax and Chrome desktop/narrow smoke green. Later commits only add Git ignore entry and update Codex documentation. Fully green follow-up current-source CI: [GitHub Actions run #40190659280](https://github.com/mrAibo/Autopilot/actions/runs/40190659280), all 4 jobs passed. Subsequent edits only remove two Python SyntaxWarnings in test fixtures, plus this status update; verify CI for latest HEAD.
- **Validated milestone after VPN off:** [GitHub Actions run #40192060051](https://github.com/mrAibo/Autopilot/actions/runs/40192060051) passed all four Ubuntu/Windows Python 3.11/3.13 jobs, **132 unittest cases on Ubuntu 3.13**, Dashboard JavaScript syntax and Chrome wide/narrow DOM. This checkpoint includes `codex_capabilities.py`, `tests/test_codex_capabilities.py` and `docs/autopilot/gui-clients.md`. Later changes to README and Codex CLI docs, plus this STATUS, require checking newer CI.
- **Windows host discovery / installation (2026-10-25):** Connected device `Aibo`, ID `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`. Found existing graphical Codex AppX `OpenAI.Codex` version `26.1021.3705.0` and managed alpha CLI `0.164.0-alpha.11.1` at `%LOCALAPPDATA%\OpenAI\Codex\bin\2993767bd1dfb009\codex.exe`. Verified npm official alpha tag `0.165.0-alpha.1` and installed `@openai/codex@0.165.0-alpha.1` globally with npm. New CLI: `%APPDATA%\npm\codex.cmd`, native binary under NPM `codex-win32-x64` vendor subtree. `codex --version` => `codex-cli 0.165.0-alpha.1`, `codex login status` => `Logged in using ChatGPT`. The managed desktop binary was not replaced. **Local checkout now created:** `C:\Users\crown\Downloads\Projects\Autopilot`, cloned at `2e33fd9` on `feat/autopilot-2.3-adaptive-router-dashboard`. `py -3.13 -m unittest discover -s tests -q` passed **126 tests** in 64.971 seconds; `py -3.13 tools\check-dashboard.py` passed JS checks. Git checkout clean. The test run emitted two benign SyntaxWarnings for escaped backticks, which were subsequently corrected on GitHub; pull branch locally before next changes.
- **Real CLI model smoke SUCCESS after VPN off (2026-10-25):** Codex Doctor v0.165.0-alpha.1 returned **21 ok, 0 fail** and active provider HTTP endpoints reachable, WebSocket connected. The previous hung tests were caused by the remote test runner leaving stdin open (`Reading additional input from stdin...`), not confirmed inference/network failure. A correct read-only stdin+EOF `codex exec` invocation requested `gpt-6-luna`, `model_reasoning_effort=low`, returned **`CODEX_OK` in 5 s** with reported `input_tokens=19718`, `cached_input_tokens=12672`, `output_tokens=7`. A second read-only invocation with `--ignore-user-config` returned **`CONFIG_ISOLATED_OK` in 4 s** (`input=16643`, `cached_input=11776`, `output=9`). This verifies successful standalone CLI inference **with requested settings**; it does not independently certify internal billed model or GUI custom-agent behavior. No actual `codex_dispatch.py --execute` run on a full ticket yet.

## Implemented and committed

1. Reliability: strict `finish` gates (G1–G4), verified Git ancestor/test counts for `ticket done`, requirement reconciliation, plan validation, safe path/slug handling, state process lock, safe dashboard stopper.
2. Provider-aware selection: `skills/autopilot/tools/model_router.py` scores complexity and risk; OpenAI and Anthropic adapters support cheap/balanced/strong profiles, deny premium agent families by default, demand host capability advertisement.
3. Native agent definitions: `agent_profiles.py` creates pinned `.codex/agents/*.toml` and `.claude/agents/*.md`; `ap.py ticket route` records an integrity SHA. Optional `claude_agent_guard.py` installs a project `PreToolUse` hook. Real execution proof still required.
4. Parallel Git worktree helper: `worktrees.py` creates detached per-ticket checkouts, checks clean source, lands exactly one executor commit, refuses unsafe/dirty removals. Ledger supports `worktree NN prepare|status|land|release`, with tests ensuring `ticket done` cannot bypass landing.
5. **New crash recovery milestone:** `git cherry-pick -x` embeds the source SHA; matching commits are independently cross-checked by stable patch ID before recognizing a previously completed Git landing. `ap.py worktree NN recover --tests N/0` reconciles an incomplete ledger after Git worktree creation, successful cherry-pick, or worktree release. Recoveries are read-only when investigating Git; no forced deletion or arbitrary reset. A detected incomplete `CHERRY_PICK_HEAD` blocks recovery and requires an explicit manual `git cherry-pick --continue` or `--abort` decision after inspection. Duplicate `ticket start` is rejected.
6. **New deterministic dispatch planner:** `scheduler.py`, integrated as `ap.py schedule --max-parallel 2`, emits machine-readable JSON with `selected` actions (`route`, `prepare`, `start`) and `blocked` reasons. Respects dependencies, overlap/wildcard code zones, active agents, reserved prepared worktrees, strict verified model profiles and the recorded-token budget. Default 2, explicit max 3. **It does NOT invoke external agents.**
7. Retry triage: `retry_policy.py` classifies environment, dependencies, requirements, tests, reasoning, security, unknown. Rejects unjustified model escalation; retries/repairs are capped at 2 and diagnosed causes are logged.
8. Token observability: `ap.py usage` stores de-duplicated per-call input/output/cache events, and `ap.py budget` blocks NEW starts at a recorded-token threshold. These are not true billing amounts or spending caps.
9. Dashboard 3.0: redesigned responsive UI, next-action summary, gates, model/effort, token counters, worktree statuses and retry advice; Chrome screenshots and tests. Docs/README EN/RU and CHANGELOG updated.
10. **New Codex CLI adapter:** `skills/autopilot/tools/codex_dispatch.py` is bundled in bootstrap, with `tests/test_codex_dispatch.py` and `docs/autopilot/codex-cli.md`. Strict+isolated ticket preflight checks the approved OpenAI route, SHA-pinned native agent definition, ticket fingerprint, model-effort host advertisement, token threshold and exact clean prepared Git cwd. `--execute` (explicit opt-in) launches **one standalone external Codex process** using explicit `--model`, reasoning effort, workspace-write/read-only sandbox, JSONL and stdin brief; optional token reporting via `ap.py usage`. Dry-run is default. An atomic `.autopilot/dispatch-NN.lock` prevents double launch; if a crash leaves a lock, verify the old agent is stopped before removing it. This is **not** an automatic scheduler loop or proof of an in-session named subagent. No real successful model call confirmed.

11. **Live Codex capability discovery and GUI contract:** `codex_capabilities.py` queries `codex debug models` account-resolved catalog (not bundled); validates model+Effort pairs and optionally writes `.autopilot/model-capabilities.json` atomically. Synthetic CI includes `tests/test_codex_capabilities.py`. On local Windows host actual account catalog contains `gpt-6-luna`, `gpt-6-sol`, `gpt-6.1-sol`, etc. Local importer `--write` in temporary test workspace succeeded, and `model_router.py` selected `gpt-6-luna/low` with `status=ready`. `docs/autopilot/gui-clients.md` defines one shared skill across Codex GUI/CLI and Claude Code; the existing global Autopilot 2.2 at `%USERPROFILE%\.agents\skills\autopilot` and Claude Junction are **not** replaced, nor was the managed desktop Codex binary. Repo local `.agents/skills` and `.claude/skills` symlinks appear as small plain files under Windows `core.symlinks=false`: a future GUI integration test must use actual skill-directory registration, not rely on those text placeholders. Actual GUI subagent dispatch **still unverified**.

## Resume checklist — remaining work

**Priority P0: real host execution and crash robustness**
1. Re-read this STATUS, `бриф.md`, `docs/autopilot/model-routing.md`, `docs/autopilot/worktrees.md`, `docs/autopilot/codex-cli.md` and CI on the latest head. The Windows clone `C:\Users\crown\Downloads\Projects\Autopilot` exists on the working branch; run `git pull --ff-only` to fetch latest source/docs and tests.
2. **CLI smoke complete:** two successful, measured read-only Luna calls. Next run one full disposable strict/isolated ticket with `codex_dispatch.py` and verified Git/tests/usage; compare CLI actual usage across configurations and avoid needless model calls. GUI Codex and GUI Claude Code still require skill discovery + native subagent model/effort verification. **Claude desktop AppX is installed**, but Claude Code CLI executable has not been found via PATH; do not equate the general Claude app with Claude Code.
3. Codex CLI standalone one-task launcher now exists as an opt-in adapter. Next integrate `schedule` with explicit handoff to this dispatcher ONLY after proving host model/cwd behavior, safe per-wave reservations, handling timeouts and user-approved model invocation. The planner itself remains read-only and never calls models.
4. Add more multi-ticket wave/restart tests, strong proof of non-overlapping source zones, recovery from Git conflict cases, and stale-task/reset/reopen cases; do not auto-abort conflict sequencers.
5. Investigate operator-friendly diagnostic messages and safe recovery of previously detached worktrees that were manually edited; never discard uncommitted work.

**P1/P2: economic measurement, packaging and release**
6. Add opt-in import of trustworthy local Codex/Claude usage metrics and transparent pricing *only where provider data supports it*. Compare 2.2 vs 2.3 on equal tasks (quality, retries, latency, token reports).
7. Resolve inherited `skills-lock.json` provenance/upstream installation/packaging and release docs.
8. Keep PR Draft; complete final tests and explicit release review before merging to `main` or tagging 2.3.0.

## To resume in a fresh ChatGPT session (copy verbatim)

> Продолжай разработку Autopilot 2.3 в https://github.com/mrAibo/Autopilot, ветка `feat/autopilot-2.3-adaptive-router-dashboard`, черновой PR №1. Сначала прочитай `STATUS.md`, `бриф.md`, документацию в `docs/autopilot/`, затем проверь фактический HEAD и GitHub Actions CI. Продолжай по разделу Resume checklist без нового планирования, меняй только рабочую ветку и обновляй `STATUS.md` после каждого этапа. `main` не трогать. Проверки реального запуска Codex/Claude и расходов не считать пройденными без фактического доказательства.

**Runtime GUI note:** Existing global skill installation on Windows remains the stable 2.2 and is used by Claude via Junction; do not overwrite it with a draft 2.3. For GUI test use a disposable workspace with actual directory symlinks/Junctions to the working branch, or update via supported installer only after release. Never assume tracked Git symlinks extracted as Windows text placeholders are readable skills.

**Repository code hotspots:**
- `skills/autopilot/tools/ap.py` (main state/CLI)
- `skills/autopilot/tools/worktrees.py` (Git isolation, recovery)
- `skills/autopilot/tools/scheduler.py` (pure deterministic dispatch decisions)
- `skills/autopilot/tools/model_router.py`, `agent_profiles.py`, `claude_agent_guard.py`
- `tests/test_ap.py`, `test_worktrees.py`, `test_scheduler.py`
- `skills/autopilot/phases/0-instruments.md`, `5-subagents.md`, `5-repair.md`
- `.github/workflows/python-tests.yml`, `tools/check-dashboard-browser.py`

**Codex CLI adapter dry-run:** `python .autopilot/codex_dispatch.py 01 --root .`; requires an active strict+isolated routed ticket, prepared worktree and CLI native binary. Only `--execute` consumes a model call. Never remove stale `.autopilot/dispatch-NN.lock` before examining any unfinished model process.

**Test commands:** `python -m unittest discover -s tests -v`; `python tools/check-dashboard.py`; `python tools/check-dashboard-browser.py` in a Linux Chrome environment. GitHub Actions additionally runs Python 3.11/3.13 on Ubuntu/Windows. Use the connected GitHub plugin in ChatGPT; local Windows directory access is not established by this GitHub integration.

**Source of truth is this checked-in file plus actual GitHub HEAD and CI, not earlier chat guesses.**
