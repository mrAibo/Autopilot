# STATUS.md — Autopilot 2.3 development handoff

**Updated:** 2026-10-25, Europe/Berlin
**Repository:** https://github.com/mrAibo/Autopilot
**Working branch:** `feat/autopilot-2.3-adaptive-router-dashboard`
**PR:** https://github.com/mrAibo/Autopilot/pull/1 — **open, Draft, NOT MERGED**
**Source checkpoint before current STATUS.md update:** `d1e65c57075134c0c9a6a8b055ec1710912ddde2`. This status-only commit will advance HEAD.
**Original base:** `25b5fbada50742f1b6a900a5a92800759e5c74d4` (Autopilot 2.2.0)
**Target:** Autopilot 2.3.0, NOT RELEASED.
**Authoritative specification:** `бриф.md`. Keep `main` untouched until release review/approval.

## Current verified checkpoint

- Most recent completed **application-code** CI: [GitHub Actions run 40188502124](https://github.com/mrAibo/Autopilot/actions/runs/40188502124), at commit `b9e6b9b5987dd1688cb0d05d48ff6ed849e6a2ef`: **all four jobs green** on Ubuntu/Windows with Python 3.11 and 3.13; **115 Python tests** on Ubuntu 3.13, dashboard JavaScript syntax and headless Chrome DOM checks for wide/narrow layouts.
- Subsequent milestone: [GitHub Actions run #40190471119](https://github.com/mrAibo/Autopilot/actions/runs/40190471119), code checkpoint `94422b0bda30e9ff068ffeee86c69b6b97de0d6b`: all 4 Windows/Linux 3.11/3.13 jobs passed, **126 tests** on Linux 3.13, Dashboard syntax and Chrome desktop/narrow smoke green. Later commits only add Git ignore entry and update Codex documentation. Check newest HEAD CI before claiming that its checks passed.
- **Windows host discovery / installation (2026-10-25):** Connected device `Aibo`, ID `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`. Found existing graphical Codex AppX `OpenAI.Codex` version `26.1021.3705.0` and managed alpha CLI `0.164.0-alpha.11.1` at `%LOCALAPPDATA%\OpenAI\Codex\bin\2993767bd1dfb009\codex.exe`. Verified npm official alpha tag `0.165.0-alpha.1` and installed `@openai/codex@0.165.0-alpha.1` globally with npm. New CLI: `%APPDATA%\npm\codex.cmd`, native binary under NPM `codex-win32-x64` vendor subtree. `codex --version` => `codex-cli 0.165.0-alpha.1`, `codex login status` => `Logged in using ChatGPT`. The managed desktop binary was not replaced. There is no verified local clone of Autopilot under `C:\Users\crown\Downloads\Projects\Autopilot` yet.
- **Real model smoke limitation:** Attempted `codex exec --model gpt-6-luna -c model_reasoning_effort="low" --sandbox read-only --ephemeral --ignore-user-config --json` in a disposable temp directory. The process did not produce a model response during the observed check; the terminal run was deliberately terminated. **No actual model output, successful execution, billable usage or model/effort server confirmation is established.** The cause is not yet diagnosed. Never claim otherwise.

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

## Resume checklist — remaining work

**Priority P0: real host execution and crash robustness**
1. Re-read this STATUS, `бриф.md`, `docs/autopilot/model-routing.md`, `docs/autopilot/worktrees.md`, `docs/autopilot/retry-policy.md` and CI on the latest head.
2. **Now possible on connected Windows host:** standalone Codex CLI 0.165.0-alpha.1 installed and logged in. Diagnose the read-only smoke not returning a response, without leaking tokens; verify actual server model+effort and usage on a disposable synthetic repo, then build the full isolated task run using `codex_dispatch.py`. Claimed model must be **observed**, not inferred from the command line. Claude Code availability remains unverified. Do not claim this passed from synthetic CI tests.
3. Codex CLI standalone one-task launcher now exists as an opt-in adapter. Next integrate `schedule` with explicit handoff to this dispatcher ONLY after proving host model/cwd behavior, safe per-wave reservations, handling timeouts and user-approved model invocation. The planner itself remains read-only and never calls models.
4. Add more multi-ticket wave/restart tests, strong proof of non-overlapping source zones, recovery from Git conflict cases, and stale-task/reset/reopen cases; do not auto-abort conflict sequencers.
5. Investigate operator-friendly diagnostic messages and safe recovery of previously detached worktrees that were manually edited; never discard uncommitted work.

**P1/P2: economic measurement, packaging and release**
6. Add opt-in import of trustworthy local Codex/Claude usage metrics and transparent pricing *only where provider data supports it*. Compare 2.2 vs 2.3 on equal tasks (quality, retries, latency, token reports).
7. Resolve inherited `skills-lock.json` provenance/upstream installation/packaging and release docs.
8. Keep PR Draft; complete final tests and explicit release review before merging to `main` or tagging 2.3.0.

## To resume in a fresh ChatGPT session (copy verbatim)

> Продолжай разработку Autopilot 2.3 в https://github.com/mrAibo/Autopilot, ветка `feat/autopilot-2.3-adaptive-router-dashboard`, черновой PR №1. Сначала прочитай `STATUS.md`, `бриф.md`, документацию в `docs/autopilot/`, затем проверь фактический HEAD и GitHub Actions CI. Продолжай по разделу Resume checklist без нового планирования, меняй только рабочую ветку и обновляй `STATUS.md` после каждого этапа. `main` не трогать. Проверки реального запуска Codex/Claude и расходов не считать пройденными без фактического доказательства.

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
