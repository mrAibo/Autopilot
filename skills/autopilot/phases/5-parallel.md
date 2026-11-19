# Phase 5 — parallel checks and silent agents

Read when a ticket is back from its executor, or when an agent seems stuck.

## Checks and review at the same time

After the executor's `DONE`, start the full check and the branch review **in the same turn**: `ap.py ticket NN land` runs the full check; the reviewer (`phases/6-review.md`) reads the commit meanwhile. The executor ran only the tests of its own change; the full suite is `ticket NN land` or `tools/run-tests.py`, never the executor.

When either is red, the executor gets **one** message, not two: `ap.py ticket NN bundle` prints the tail of the failed check (`lastCheck`, written by `land` on a red check), the open blockers and the ticket's concerns. Pass its output as the retry prompt.

## A silent agent

An agent is stuck by silence, not by age: no output and no steps for `AUTOPILOT_SILENCE_SECONDS` (default 600). Run `ap.py silence` while agents work; exit code 3 lists the quiet ones. `ap.py` never stops anyone: stop the agent with `TaskStop`, then `ticket NN retry` as usual. `ap.py stage` also warns in chat when a stage has run longer than 60 minutes; the warning is a prompt to look, not a verdict.

## Dependencies in a worktree

`worktree NN prepare` copies `node_modules` when the lock files match byte for byte (see `docs/autopilot/worktrees.md`); the last line says `copied` or `skipped: <why>`. Skipped is the old path: the executor installs what it needs.
