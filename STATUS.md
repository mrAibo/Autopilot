# STATUS.md — Autopilot 2.3 development handoff

**Updated:** 2026-10-25, Europe/Berlin
**Repository:** https://github.com/mrAibo/Autopilot
**Working branch:** `feat/autopilot-2.3-adaptive-router-dashboard`
**PR:** https://github.com/mrAibo/Autopilot/pull/1 — **open, Draft, NOT MERGED**
**Current source checkpoint before this STATUS.md update:** `22649612a23920019065c57a21a395a92f6711ca`
**Original base:** `25b5fbada50742f1b6a900a5a92800759e5c74d4` (Autopilot 2.2.0)
**Target:** Autopilot 2.3.0, NOT RELEASED.
**Authoritative specification:** `бриф.md`. Keep `main` untouched until release review/approval.

## Current verified checkpoint

- Most recent completed **application-code** CI: [GitHub Actions run 40188502124](https://github.com/mrAibo/Autopilot/actions/runs/40188502124), at commit `b9e6b9b5987dd1688cb0d05d48ff6ed849e6a2ef`: **all four jobs green** on Ubuntu/Windows with Python 3.11 and 3.13; **115 Python tests** on Ubuntu 3.13, dashboard JavaScript syntax and headless Chrome DOM checks for wide/narrow layouts.
- Since that code checkpoint, only documentation files were updated (`docs/autopilot/worktrees.md`, README EN/RU) before this STATUS checkpoint. Check CI for the newest HEAD after every change.
- **No real Codex/Claude Code agent run, paid-model verification, or real monetary savings measurement has been performed.** Never claim that config verification equals host/billing verification.

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

## Resume checklist — remaining work

**Priority P0: real host execution and crash robustness**
1. Re-read this STATUS, `бриф.md`, `docs/autopilot/model-routing.md`, `docs/autopilot/worktrees.md`, `docs/autopilot/retry-policy.md` and CI on the latest head.
2. Test actual native subagent discovery and model/effort dispatch in an accessible Codex CLI and Claude Code environment, including the opt-in Claude hook, `cwd` for worktrees, and restricted-model guard. Do not claim this passed from synthetic tests.
3. Integrate `schedule` with a real host-side orchestrator/action dispatcher **only if** the host supports enforceable per-agent model and cwd; otherwise use safe stepwise prompts and sequential work. `schedule` itself is read-only and intentionally does not run external commands.
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

**Test commands:** `python -m unittest discover -s tests -v`; `python tools/check-dashboard.py`; `python tools/check-dashboard-browser.py` in a Linux Chrome environment. GitHub Actions additionally runs Python 3.11/3.13 on Ubuntu/Windows. Use the connected GitHub plugin in ChatGPT; local Windows directory access is not established by this GitHub integration.

**Source of truth is this checked-in file plus actual GitHub HEAD and CI, not earlier chat guesses.**
