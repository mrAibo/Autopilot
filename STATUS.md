# STATUS.md — Autopilot 2.3 development handoff

**Updated:** 2026-10-25 (Europe/Berlin)
**Canonical repo:** https://github.com/mrAibo/Autopilot
**Working branch:** `feat/autopilot-2.3-adaptive-router-dashboard`
**Pull request:** https://github.com/mrAibo/Autopilot/pull/1 (**Draft**, NOT merged)
**Base main commit:** `25b5fbada50742f1b6a900a5a92800759e5c74d4`
**Checkpoint when this file was written:** `4b31fd74378248571d9042b5eb3725f2f573fa4c` (subsequent commits on the same branch supersede this SHA)
**Release:** 2.3.0 IN DEVELOPMENT. Do not merge/tag as final yet.
**Latest implemented branch HEAD (during this update):** `e61a6add6927469907589c6655dbcef73667710c`. Validate CI against the SHA currently shown by GitHub, not an earlier completed run.

## Mission and non-negotiables

Deliver `бриф.md`: reliable CLI lifecycle; provider-neutral economical task routing for OpenAI/Codex and Anthropic/Claude Code; premium models blocked by default; native pinned agent definitions; safe per-ticket Git worktree isolation; strict acceptance gates, tests, clearer Dashboard 3.0, token reports and honest limits; complete EN/RU documentation.

Do not modify `main` until reviewed and approved. Use the existing draft PR. NEVER claim external model selection or dollar cost was verified without evidence from a real Codex or Claude Code run. Preserve backwards compatibility when possible. Keep the tracked `STATUS.md` updated after every substantive implementation/test milestone.

## Completed and already committed to PR

1. `бриф.md` captures R01–R06, stages and definition of done.
2. `skills/autopilot/tools/ap.py`: hard `finish` gates, ticket Git ancestor/test checks, requirement reconciliation, validation, OS process lock, safe delayed dashboard server shutdown, model route verification, protected state fields.
3. `skills/autopilot/tools/model_router.py` & `agent_profiles.py`: complexity tiers, separate OpenAI and Anthropic profiles, no automatic Astra/Fable/Opus; fail-closed host-capability handshake; generate native pinned `.claude/agents/*.md` and `.codex/agents/*.toml`; profile SHA verified on strict ticket start/done.
4. `skills/autopilot/tools/claude_agent_guard.py`: opt-in Claude Code PreToolUse guard + installer and tests; not a host-level sandbox.
5. `skills/autopilot/phases/dashboard-template.html`: redesigned responsive UI, current activity, gates, task status, model/effort, token counters and threshold; browser CI smoke for desktop/narrow and screenshot artifacts.
6. `skills/autopilot/tools/worktrees.py`: detached per-ticket checkouts, clean-source safeguards, single-commit cherry-pick, refusal to delete dirty worktrees. `ap.py worktree ID prepare|status|land` now integrates worktree lifecycle with ticket state (new milestone still being tested).
7. `skills/autopilot/tools/retry_policy.py`: deterministic failure diagnosis (environment/dependency/requirements/tests/reasoning/security/unknown). `ap.py ticket NN retry --cause tests|unknown` stops inappropriate model escalation and caps retries/repairs at two (new milestone still being tested).
8. `ap.py usage` accepts identified token observations; `ap.py budget` stops *new* task starts at a **recorded token** threshold; it cannot enforce monetary budget or stop a running model. Dashboard displays missing price as unavailable.
9. Tests/CI for Linux and Windows (Python 3.11 and 3.13), Node syntax, headless Chrome DOM/screenshot. EN/RU README, CHANGELOG, routing, observability and worktree docs.

## Current in-progress checkpoint / verification

- Last verified all-green checkpoint before latest worktree/retry changes: commit `5ef6b92e8ae6c12c67d2f43989ff046af0d052d8`, GitHub Actions run `40184704422`, all four platform/Python combinations succeeded, 80 tests on Linux, dashboard smoke.
- New integrated worktree + retry changes are on this branch. A first end-to-end test failed because the test Git repo lacked `user.name/email` for `cherry-pick`. The test now configures the local Git committer; detailed landing failure messages added.
- Linux checks for the subsequent commit `b214bb91f6a931ca48e96c5df8f2c3fdb2acdc9c` were green. Current HEAD includes additional integration and docs; recheck CI for **current HEAD**, do not use old green status.
- Completed all-green integrated worktree/retry checkpoint: GitHub Actions run `40186489341` (Ubuntu and Windows, Python 3.11 / 3.13). This is distinct from the earlier green baseline.
- Since that success, more tests/guards were added: reject missing worktree on `ticket done`, release accepted worktrees, prevent live worktree records from being invalidated by ticket edits, and update phase/docs. **Latest HEAD CI must still be checked.**
- No actual Anthropic or Codex session was launched; no paid-model/billing evidence, and model/cwd behavior must be validated in real harnesses.

## Immediate TODO (continue in this order)

1. **Check latest CI on current HEAD** via GitHub connector; inspect failing job logs and fix every regression on the feature branch.
2. **DONE:** bootstrap `skills/autopilot/phases/0-instruments.md` now copies both `worktrees.py` and `retry_policy.py`; CLI integration tests copy both helpers.
3. **DONE for this increment:** phase 5 subagent/repair docs, worktree and retry-policy docs, README EN/RU and CHANGELOG now include the new API; lifecycle includes `worktree release` after `ticket done`. Verify any remaining gaps in `бриф.md` at release.
4. **PARTIALLY DONE:** integrated isolated task lifecycle, preparation-before-start, dependency ordering, malformed/failed tests and safe accepted release all have tests. Retry category, two-retry limit and avoidance of environment-model escalation have tests. **Remaining:** concurrent wave, multiple landed commits, restart/recovery and strict mode reroute; replay tests from a process crash; verify on both OS.
5. **PARTIALLY DONE:** source-clean Git landing verified, dirty checkout refused, repo local Git committer required; ticket fingerprint modifications with active worktree now block; done cannot bypass isolation; helpers are bootstrapped. **Remaining:** crash recovery, reset/reopen semantics with worktrees, automatic cleanup policy and true multi-task scheduler.
6. **Real-host verification** requires accessible local Codex CLI and Claude Code with permitted test models: verify actual agent type, effort, Claude hook, isolated cwd, usage reports. GitHub CI tests alone cannot assert external harness behavior.
7. **Cost and benchmark:** automatic read of sanitized provider log counters, comparisons with 2.2.0 across same tasks, optional pricing; do not invent cost.
8. Keep PR Draft, update PR description with current truthful limits. Prepare release only after all critical gates pass.
9. Maintain this `STATUS.md` after EVERY substantial milestone, including exact latest green workflow ID, open blockers and how to resume.

## How to resume in a NEW ChatGPT session

Send this instruction:

> Continue development of https://github.com/mrAibo/Autopilot in branch `feat/autopilot-2.3-adaptive-router-dashboard`, PR #1. Read `STATUS.md`, `бриф.md`, `docs/autopilot/model-routing.md`, `docs/autopilot/worktrees.md`, `docs/autopilot/retry-policy.md`, `docs/autopilot/observability.md` and relevant code/tests via connected GitHub. Verify latest HEAD and CI. Continue unfinished work from STATUS.md without replanning. Update STATUS.md after each milestone. Work only in branch, leave main unchanged, do not prematurely merge. Report genuine limitations and tests.

Current integrated commands: `ap.py init ... --isolated-tickets`, `ap.py worktree NN prepare|status|land|release`, `ap.py ticket NN retry --cause tests|unknown`. Always checkpoint generated `.gitignore` source changes before creating an isolated worktree. The host must truly launch the executor in the returned `cwd`, which is not enforced by a GitHub-only test.

The ChatGPT assistant can use the **connected GitHub plugin** tools through `functions.exec`; GitHub repository is accessible. Avoid relying on a local clone unless its availability is confirmed. Do not repeat work done in this branch. The user prefers Russian communication and a useful, informative Dashboard.

## Reference files and checks

- `skills/autopilot/tools/ap.py`
- `skills/autopilot/tools/model_router.py`
- `skills/autopilot/tools/agent_profiles.py`
- `skills/autopilot/tools/worktrees.py`
- `skills/autopilot/tools/retry_policy.py`
- `skills/autopilot/tools/claude_agent_guard.py`
- `tests/test_ap.py`, `tests/test_worktrees.py`, `tests/test_retry_policy.py`, `tests/test_agent_profiles.py`, `tests/test_model_router.py`
- `.github/workflows/python-tests.yml`
- Run: `python -m unittest discover -s tests -v`; `python tools/check-dashboard.py`; headless Chrome smoke `python tools/check-dashboard-browser.py` on Linux CI.

**Maintain this file as an accurate handoff, not a blanket “everything completed” claim.**
