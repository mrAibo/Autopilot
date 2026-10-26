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

# Read-only host metadata check. This also never calls a model.
py -3.13 .autopilot/gui_bridge.py --root . --ticket 01 --check-runtime --timeout 90

# After a separately verified, independently host-tested worker output,
# the controller can apply one authorized Git/state transition.
py -3.13 .autopilot/controller.py --root . --suite test_calc.py --advance
```

**Execution is presently disabled on purpose.** The bridge and the underlying
`codex_dispatch.py` reject all real `--execute` invocations in
`spend_guard.assert_enforced_cap` **before spawning a model**, even when
`--approve-ticket` is supplied. A positive recorded token threshold, explicit
user permission, a ChatGPT subscription login, or a finite timeout cannot
establish provider-side per-call cost enforcement. Do **not** attempt to
enable execution by changing configuration or bypassing the guard.
This is a future design, not a currently supported or billable fallback.
The bridge never launches from the Dashboard page or an untrusted suggestion.
See [spend-guard.md](spend-guard.md) and
[release-readiness.md](release-readiness.md).

Read-only preflight reports configured model, reasoning effort, isolated cwd,
sandbox and **recorded** token usage/remaining threshold. It never establishes
a provider-side token/monetary hard limit, actual agent identity, or permission
to invoke a model. A wall-clock timeout cannot bound token usage.

## Read-only runtime doctor before an approved model call

For an existing, prepared isolated ticket:

~~~powershell
py -3.13 .autopilot/gui_bridge.py --root . --ticket 01 --check-runtime --timeout 90
~~~

The doctor performs the normal receipt-free ticket/profile/worktree and
recorded-budget preview. It then queries the **actual native Codex binary**
for its current account-visible model catalog, version and `exec --help`.
The pinned model/Effort must be listed, and required execution switches
must exist. Unknown binaries, stale models and missing flags fail closed.
`--check-runtime` is incompatible with `--execute` or `--approve-ticket`.
No model call or attempt receipt is created; success means compatible
CLI metadata, not attested provider execution or hard token budgeting.

On the Windows host (2026-10-25), this passed with Codex CLI
`0.165.0-alpha.1`, GPT-6 Luna / Low and the clean synthetic ticket 01
with an unused recorded 2,000-token threshold. No file changes or receipt.
GUI-to-terminal paid inference is still a separate outstanding gate.

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

## Actual OS-process offline integration test

Two integration tests initialize a real strict-isolated temporary Autopilot
project, route GPT-6 Luna / Low to a SHA-pinned profile, set a positive
recorded token threshold, and prepare/start a real Git worktree.

**Only the external Codex executable is replaced with an offline Python
process**. The bridge still performs real pinned routing/profile/brief
checks, writes its durable claim and launches a separate process. The
offline process writes and commits an approved code change, emits
synthetic Codex JSONL, and the real ap.py usage command records counts.
The real controller then insists on independent baseline-tracked host
tests before it lands, accepts and releases the worktree.

The second test uses an actual CLI process exiting nonzero; the bridge
persists its receipt, records provider execution as **unknown**, and
blocks any attempt to repeat the same ticket. No paid model was contacted.
The tests establish process orchestration, not effective provider model
identity or direct GUI terminal access.

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
