# Offline worker supervision qualification (2.3.0-dev)

The dedicated `offline_supervisor.py` is a **development-only synthetic
process harness**. It does not call Codex, Claude, an AI model or a network
provider. It is NOT a production dispatcher and is deliberately **not**
copied into projects by Phase 0. Its purpose is to prove the worker
lifecycle around a real child OS process before designing billable dispatch.

## Scope and hard gates

The only executable is `offline_fixture_worker.py`, a bundled fixed script
with two deterministic examples (`calc-add` / `calc-mul`). The CLI
**does not accept any arbitrary executable or prompt**, and it refuses to
run outside a temporary OS directory, outside a real strict-isolated Git
project, or without a precisely matching `.autopilot/offline-test-consent`
file. It additionally requires a clean pre-started worktree, the exact
approved ticket's zone and an explicit `--approve-offline-ticket NN`.

Only the **offline integration tests** create temporary marker files. Never
put this marker in a real application project; doing so would not authorize
any real provider billing either. The synthetic worker edits only one
literal file with an exact expected baseline; it cannot handle arbitrary
tasks and does not generate provider usage tokens.

## Test commands (temporary fixture only)

~~~powershell
# Preview; read-only, does not create a receipt:
py -3.13 .autopilot/offline_supervisor.py --root . --ticket 01 --fixture calc-add

# Explicit one-shot offline operation; no AI calls:
py -3.13 .autopilot/offline_supervisor.py --root . --ticket 01 --fixture calc-add --execute --approve-offline-ticket 01

# From a second shell while the supervisor is running:
py -3.13 .autopilot/offline_supervisor.py --root . --ticket 01 --cancel

# Reconcile by reading the saved receipt; never trusts a stale PID:
py -3.13 .autopilot/offline_supervisor.py --root . --ticket 01 --status
~~~

A receipt is created with exclusive create + fsync **before** process
launch, and remains in `.autopilot/offline-worker/NN.json` for all
terminal outcomes (`completed`, `failed`, `cancelled`, `timed-out`)
or uncertain ones. A prior receipt forbids replay, even if a previous
process might have failed before launch. A cancel request creates a
durable `.cancel` marker. **Only the live supervisor kills the
child process it still owns**: it does not use a persisted PID to
kill an arbitrary possibly reused process.

The supervisor holds the existing host-controller lock across the child
lifetime to prevent competing host-side Git/test transitions.

**Windows:** `process_containment.py` creates a Windows Job Object with
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. The inert `process_gate.py` cannot
launch the fixture until the supervisor assigns the gate process to the
Job Object. If assignment fails, the worker never starts (fail closed).
The supervisor alone owns the kernel job handle: parent death closes it,
causing the kernel to terminate contained child processes. An actual Windows
integration test killed the parent and verified the gate process signalled
termination via an open OS handle; the fixture source remained untouched.

**Windows receipt-sharing race:** a read-only status probe may temporarily
hold the old `NN.json` receipt while the supervisor atomically replaces
it. Unlike POSIX rename, Windows can return WinError 5/32
(ACCESS_DENIED/SHARING_VIOLATION). `persist()` now retries only these two
recognized errors with **12 bounded attempts** and a total delay of less
than a second. It never deletes the old receipt to make replacement work;
an exhausted lock or an unrelated error still fails closed and leaves
the existing receipt in place. Portable fault-injection tests exercise
transient recovery, permanent lock preservation and no retries for
unrelated errors or POSIX mode. No OS-process or model launch retries.

**Linux/macOS:** processes run in a separate POSIX session, but parent-death
kill of descendants is **not** guaranteed. Production calls must not rely
on that weak fallback; platform-specific containment remains to be built.

Cancel requests contain the exact `claim_id` from the durable receipt.
The live supervisor validates this ID, kills the owned process tree and
writes `cancel_acknowledged_at` in the terminal receipt. A `--status`
command exposes recorded outcomes read-only without claiming a stored PID is
alive. If the supervisor dies, the receipt deliberately remains
`invocation-uncertain` or `running` and **no automatic restart/retry is
allowed**. A cancel marker alone is not evidence of termination. There is
still no production-ready cross-platform lifecycle recovery.

## Verification and boundaries

The tests use real disposable Windows/Linux subprocesses and actual Git
worktrees. They cover a successful first ticket with real independent
host tests, Git landing and acceptance; cancellation of a delayed second
worker with no acceptance; timeout; failure; crash between claiming a
receipt and spawn; refusal after replay; refusal without marker or with
wrong file zone. Neither fake worker usage nor fake provider billing
is added to the Autopilot ledger.

The host loop and the test suite may execute **trusted local Python**;
that code could have its own side effects. This proof uses reviewed,
bundled fixed synthetic sources only. Do not infer real Codex/Claude
runtime identity, pricing, provider-side budget enforcement, GUI agent
support, paid invocation consent, or parallel dispatch from these tests.

Next: design a separate **explicitly approved**, fail-closed actual worker
launcher with robust cross-platform process containment and cancel
acknowledgements; require a separate, ticket-specific paid-call approval
for any real provider test. Maintain `2.3.0-dev`.
