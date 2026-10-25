# Codex GUI to approved pinned CLI worker bridge (2.3.0-dev)

When a graphical Codex session cannot select a named subagent, it can still
operate the **same** Autopilot ticket ledger through the local terminal.
This is a GUI-originated workflow invoking a **separate native Codex CLI
process**, not an in-session child agent. Claude Code hosts with file and
terminal access may also use the bridge; actual Claude Code host operation
has not yet been tested on the owner's machine.

The bridge reuses the existing strict isolated Codex dispatcher, verified
model+Effort route, SHA-pinned TOML profile, baseline-checked ticket brief,
prepared clean Git worktree and independent host test/acceptance flow.

## Usage from Codex GUI (or any trusted local shell)

An initialized strict and isolated project needs an approved OpenAI model
route, a prepared and started clean worktree, a positive recorded token
threshold and a native Codex CLI binary.

From **that project's root**:

```powershell
# Safe: read-only preview, no dispatch, no receipt, no charge.
py -3.13 .autopilot/gui_bridge.py --root . --ticket 01

# Potentially billable: explicit consent to one ticket, at most ONE attempt.
py -3.13 .autopilot/gui_bridge.py --root . --ticket 01 --execute --approve-ticket 01 --timeout 180

# After worker edits, independently verified tests + one Git/state transition.
py -3.13 .autopilot/controller.py --root . --suite test_calc.py --advance
```

The execution command is an **explicit consent action**. The user should
authorize this exact invocation and inspect the preview first; a GUI assistant
must not infer approval from a previous generic request or run the execution
flags on its own. It is a potentially billable inference call. The bridge
never launches from the Dashboard page or an untrusted model suggestion.

Preflight reports model, reasoning effort, isolated cwd, sandbox and
**recorded** token usage/remaining threshold. This is NOT a guaranteed
provider-side token/monetary hard limit. A bounded wall-clock timeout helps
control risk but a timed out call may still consume tokens; charges must be
reconciled with provider billing.

## Durable anti-replay

Before invoking the CLI worker, the bridge creates
`.autopilot/gui-dispatch/NN.json` using OS-exclusive create + fsync:
ticket, model, effort, prompt fingerprint, approval envelope, and status
`invocation-uncertain`. This occurs **before** model execution.

After the run, the bridge atomically updates it with executor status, optional
source commit and reported JSONL counters. The existing dispatcher records
usage in Autopilot's ledger keyed by native thread ID. Receipt contains no
ticket brief, source, full prompt or model transcript; it is ignored by Git.

If the process crashes before/during/after inference, a receipt remains.
**Re-running the same ticket is blocked**, even if execution failed/incomplete
or no usage was recorded. It is impossible to distinguish a call never
received by the provider from a lost response reliably. Inspect receipt,
Git worktree, account usage and ledger. No force/retry bypass is included.

The controller's OS lock serializes invocations with other host transitions.
The bridge never invokes finalize, land, done or release. Those require
unchanged baseline-tracked tests run by the trusted host; a successful
model turn or source commit alone is NOT task acceptance.

## Limits and tests

GUI must have terminal/tool access to use this method; otherwise it reports
a blocker. Native GUI named subagents are not available in the owner's tested
session. This is not an unattended daemon, GUI plugin, authenticated human
consent token, hard provider-side budget, parallel pool or billing proof.

The bridge's preview/approval/receipt/anti-replay/error behavior has been
tested without paid calls in disposable Git fixtures with a mocked Codex
process. The existing native CLI worker is reused, not reimplemented.
Full GUI-to-terminal-to-paid-CLI-to-accepted-code end-to-end remains
**unverified** until a deliberately approved live test.
