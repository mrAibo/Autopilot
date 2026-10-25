# Provider spending guard and recorded token audit (Autopilot 2.3.0-dev)

## Why real paid calls are blocked

A real one-shot Codex CLI invocation on 2026-10-25, performed with explicit
owner approval inside an already disposable isolated Git checkout,
reported 53,187 **input tokens** (46,464 cached) and 341 **output tokens**,
or **53,528 total counted tokens**. The run's recorded **2,000-token limit**
was checked *before* the turn, but it is a **soft cumulative admission
threshold**, not a provider-side per-call quota. Its recorded overage
was 51,528 tokens. The CLI reported `turn.completed`, but it did not
produce the required Git commit; the bridge returned `incomplete`,
left the ticket in progress, did not accept work, and wrote a durable
non-replayable receipt. The recorded token counts are NOT an invoice or
proof of the model identity independently attested by the provider.

There is currently **no proven per-call hard spending ceiling** for
this authenticated Codex CLI route. Consequently, direct
`codex_dispatch.py --execute` and `gui_bridge.py --execute` must
both **refuse all real provider model invocations before any subprocess**,
even if a user authorizes spending or sets a positive recorded threshold.
Timeouts and remaining recorded budget cannot guarantee a financial cap.

This safeguard lives in `spend_guard.assert_enforced_cap` and is
unconditionally fail-closed. There is **no env variable, user config,
argument or locally authored self-attestation** that enables execution.
Tests may patch the function in their own Python process only while
substituting the paid executor with deterministic offline fixtures.
Production activation requires a separately reviewed implementation
which independently verifies a provider-enforced per-call cap and ties
the authorization to an exact authenticated account, model, and request
before the live call.

## Read-only usage audit

After Phase 0 has copied `spend_guard.py` into `.autopilot`:

```powershell
py -3.13 .autopilot/spend_guard.py --root . --ticket 01
```

This inspects the local `.autopilot/state.js` usage ledger and
`.autopilot/gui-dispatch/NN.json` receipt, **without creating a
dispatch receipt or sending an AI request**. It reports input/output,
cached-input subset, total recorded tokens, soft threshold, overage,
attempt status, whether any worker commit is recorded and uncertainty.
There is no inference about monetary API price, invoice amount, remaining
provider budget, or whether the actual model matches a pinned CLI flag.
Rejects corrupt usage events, invalid ticket numbers and redirected
receipt paths. The per-ticket receipt status is reported alongside the
**run-wide** recorded usage totals; the report does not pretend that
all run-wide tokens belong to that one ticket.

Read-only `gui_bridge.py --check-runtime` still checks the real CLI,
fresh account-visible model catalog and supported flags, but the doctor
says `execution_permitted:false`; capability discovery is not spending
authorization. Pre-existing project-local `.autopilot` copies must be
refreshed from the installed skill together with the new `spend_guard.py`
dependency; a missing dependency must fail rather than falling back
to unguarded execution.

## Resume criteria

Before paid calls resume, independently establish (1) genuine
provider-side per-call spending/token enforcement for the specific
runtime and account, not only client-side timeouts; (2) atomic, durable
per-ticket anti-replay + provider-side usage reconciliation; (3) a
synthetic successful worker commit followed by independent host tests,
before any acceptance; and (4) sanitized diagnosis of incomplete
turns without sensitive transcript persistence.

No further paid retries against the prior disposable ticket: the
receipt remains non-replayable. Version stays `2.3.0-dev`.
