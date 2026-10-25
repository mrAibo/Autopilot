# Safe host-side controller (2.3.0-dev)

The controller coordinates one safe Git/test/state transition at a time for an
**existing** Autopilot run in `--strict-routing --isolated-tickets` mode. It uses
the existing `ap.py` and `scheduler.py` and NEVER launches a model. A missing
worker or a missing test suite stops execution rather than fabricating success.

## Commands

After Phase 0 installed `.autopilot/controller.py` in the actual project:

```powershell
py -3.13 .autopilot/controller.py --root .               # read-only next step
py -3.13 .autopilot/controller.py --root . --advance     # one safe host step
py -3.13 .autopilot/controller.py --root . --suite test_calc.py --advance
```

`--advance` is deliberately a **single step**, not a hidden background loop.
Supported steps, selected from live project/Git evidence:

`prepare → start → [external separately approved worker] → verify → finalize
(or verified worker commit) → land → accept → release`.

Every step rereads `state.js` while holding an OS-owned cross-process lock. The
lock file remains in place, allowing the OS to release ownership after crashes
without the remove-and-recreate inode race. Failed commands stop; the controller
does not blindly retry cherry-picks, model calls, or failed tests. Existing
`ap.py worktree NN recover` remains the manually audited crash recovery path.

The controller checks strict routing, isolated mode, dependency order, zone
ambiguities/escapes, active worktrees, recorded token budget, Git base
revisions and independent baseline-tracked Python unittest evidence. `ap.py`
independently revalidates tests and approved commit transitions before accepting
a task. No arbitrary shell commands from agent text are accepted.

When a clean prepared worker is waiting, the controller reports
`await-separately-approved-pinned-worker` and stops. A separate operator or GUI
host may explicitly invoke the proven sandboxed `codex_dispatch.py ... --execute`
with a verified model/Effort and approved token budget. This is NOT performed
by the controller, which does not spend tokens and cannot duplicate a model
call after a crash.

When changed worker files are present, give the exact previously tracked
unchanged unittest module using `--suite`; it executes on the trusted host.
A red test is a hard stop and leaves the worker files for diagnosis. After
a human or approved isolated worker corrects the problem, the next controller
run re-verifies the same suite. Unknown test runners, modified test modules,
ambiguous file zones and unauthorized direct GUI child agents remain blocked.

## Evidence

- Pure controller tests for dependency order, duplicate IDs, strict profile
  routing, wrong/unknown zones, active-task conflicts, readiness, budget,
  verified tests, one-command-only operation and zero implicit model calls.
- End-to-end synthetic integration exercises two real Git worktrees and two
  independently host-run tests, with a deliberately failing test in ticket
  02 and successful recovery. It validates actual Git cherry-pick landing,
  acceptance and worktree release.
- Scheduler regression tests cover Windows drive paths, parent-directory
  escape, case-insensitive overlaps and wildcard ambiguity.

This is a **bounded, operator-invoked state-transition controller**, not a
hands-off asynchronous daemon, a GUI native subagent runtime, or proof of actual
provider identity or token charges. Further iterations can add an approved
bounded worker launcher with explicit cancellation, durable dispatch receipts
and independently verified usage, then a policy-controlled multi-worker loop.
