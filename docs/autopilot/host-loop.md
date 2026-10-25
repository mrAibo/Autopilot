# Bounded host lifecycle loop (2.3.0-dev)

`host_loop.py` is an **optional operator-invoked host-only coordinator** for
strict isolated Autopilot runs. It chains already-implemented controller
transitions across a small bounded number of steps. **It never directly
launches Codex, Claude, another agent, or a paid inference call.** However,
approved host-side Python test modules are executable code, and may themselves
make network requests or have other side effects. Only explicitly select
trusted, independently reviewed offline suites. Default mode is read-only.
This is not the future full AI worker orchestrator.

## Usage in an initialized project

The Phase 0 instrument installation copies `.autopilot/host_loop.py`
alongside `controller.py`. On existing projects, update the installation
only after checking any local modifications; do not reinitialize the run.

```powershell
# Shows the next allowed transition. No controller lock, no write.
py -3.13 .autopilot/host_loop.py --root .

# Explicitly run at most eight host-side transitions, then stop.
py -3.13 .autopilot/host_loop.py --root . --advance

# Trust only specifically approved baseline-tracked unittest files.
py -3.13 .autopilot/host_loop.py --root . --advance --max-steps 8 --suite 01=test_core.py --suite 02=test_bot.py
```

`--max-steps` ranges from 1 to 32. Each transition rechecks live Git/state
while holding the existing controller's OS lock. The lock remains on disk
between steps; simultaneous sessions may change the plan. If the action
changes between preview and execution, the loop stops instead of silently
continuing with a different ticket.

`--suite NN=FILE` selects an explicit **per-ticket** baseline-tracked
unittest module. The controller/ap.py verify that the suite was in the
unchanged Git baseline before accepting any evidence. A missing suite blocks
verification; no command from ticket prose is executed. A failed test or
Git transition stops the loop without a hidden retry. No force/replay/reset
operation is exposed.

## Interpreting statuses

- `dry-run`: next action preview only; no effects.
- `paused`: a clean isolated worktree is waiting for a **separately**
  authorized and model-pinned worker, never started by this command.
- `limit-reached`: explicit host-step bound was reached; inspect before
  continuing.
- `blocked`: unsafe, inconsistent, missing approval/evidence or failed
  transition; inspect ledger and Git before resuming.
- `tickets-settled`: all current tickets were accepted and worktrees
  released. **NOT** final project acceptance, G1-G4 or `ap.py finish`.

`model_invoked` is always `false` for this tool, regardless of status.
Usage/price from any separately executed worker are not measured by this loop; the loop itself does not contact a provider. Host-run test modules must be separately trusted.

## Offline validation

The real Git integration test builds two synthetic, disposable ticket
worktrees; the loop prepares/starts the first then stops before a model call.
A scripted **offline** file edit stands in for the first worker. The loop runs
independent host Python unittest, finalization, cherry-pick, acceptance and
release, then prepares/starts the dependency-unblocked second ticket. It
deliberately fails the second unittest, stops without accepting, and resumes
successfully only after a separate offline source correction.

Additional unit tests cover dry-run, invalid suites/step bounds, no model
invocation, bounded progression, single failed transition and concurrent
plan shifts. All tests use disposable Git fixtures and no paid API.

## Remaining P0

This loop **does not** consume a plan into automatically launched Codex/Claude
workers, enforce provider-side hard token limits, verify graphical subagents,
handle concurrent paid calls, or provide a daemon. Next qualification is a
separately approved real GUI-to-Codex-CLI end-to-end run (not authorized by
these tests), then explicit cancel/dispatch and parallel workers with durable
receipts. Preserve `2.3.0-dev` until independently attested.
