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
lifetime to prevent competing host-side Git/test transitions. An
unexpected parent crash may leave a process behind on some operating
systems; the receipt deliberately remains `invocation-uncertain` or
`running` and **no restart/retry is allowed**. A cancel marker is
best-effort: if the supervisor has crashed, it cannot kill the child.
True kill-on-parent-death process containment, cancellation acknowledgement,
heartbeat/process identity attestation and production worker recovery
are **not** established by this test harness.

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
