# Bounded Responses API toy pilot — development qualification (2.3.0-dev)

This is a **separate, deliberately narrow** path for a single, synthetic
addition-function repair. It is **not** a replacement for the real Codex
CLI, a production dispatcher, a general AI agent or a verified monetary
hard cap. The old paid `codex_dispatch.py` and `gui_bridge.py` paths
remain blocked by `spend_guard.py`.

## Verified public API envelope

- Fixed HTTPS host `api.openai.com` and `POST /v1/responses`, no user-defined
  endpoint, redirect, tool calls, previous-response history or background
  execution; no automatic network retries.
- Fixed `gpt-6-luna` model, `reasoning.effort=low`, `store=false`,
  `truncation=disabled`, `tools=[]`, `tool_choice=none`.
- A fixed synthetic prompt and baseline; complete JSON request **≤4096 bytes**.
  API `max_output_tokens=192` is a **server-side output-token limit,
  including reasoning tokens**. The provider can return `incomplete` at
  the limit. On failure no source is applied.
- Only one strict JSON schema field `source`; an exact expected corrected
  toy source is allowed. Nothing supplied by the model is executed as
  shell code, auto-committed, or copied into an actual application project.
- Recorded soft run threshold must have ≥4288 tokens remaining. This is a
  conservative **client-side admission gate**, not a billing guarantee:
  request bytes are not the same as provider-accounted tokens, provider
  overhead may exist and client timeouts do not cancel billing.
- No real API credentials were detected in the authorized Windows environment
  on 2026-10-26; no live API call was possible in this qualification.

Official references:
- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/reference/resources/responses/methods/create
- https://platform.openai.com/pricing

The published standard short-context rate for GPT-6 Luna on 2026-10-26
is $0.10 / 1M input tokens and $0.50 / 1M output tokens, not a fixed
price or an invoice. Model pricing, provider acceptance and API account
billing must be rechecked before live testing. ChatGPT Plus / authenticated
Codex CLI access **does not supply a separate OpenAI API key**.

## Mandatory environment and approval

The module lives in `skills/autopilot/tools/bounded_api_pilot.py`, not
copied automatically to arbitrary projects by Phase 0. Run only on a
disposable Git project **under the OS temporary directory**, initialized
with the normal strict/isolated Autopilot lifecycle. Exactly one ticket
must be started and routed, with provider OpenAI, model `gpt-6-luna`,
effort `low` and zone `src/core/`. It must have the exact unmodified
toy `src/core/calc.py` and tracked `test_core.py`, plus a special
`.autopilot/api-pilot-consent` file whose bytes exactly match
`AUTOPILOT_BOUNDED_API_PILOT_V1\\n`.

Use a separate OpenAI API credential in the *process environment*
(`OPENAI_API_KEY`), never paste one into a chat, the source code, tests,
a PR or a Git-tracked file. The first read-only command uses no tokens:

```powershell
py -3.13 skills/autopilot/tools/bounded_api_pilot.py --root TEMP_FIXTURE --ticket 01
```

Only when the environment and **specific synthetic task** are approved,
execution requires both `--execute` and
`--approve-pilot-ticket 01`. No call takes place before key validation.
A per-ticket receipt is claimed exclusively and fsynced **before** the
HTTPS call; a failure or crash leaves a receipt and bans all retries
for that ticket. The receipt omits credentials and transcript.

Once the API confirms a completed single text response with the requested
model, matching response ID, **complete usage counters and exact expected
toy source**, the host first writes token usage to the Autopilot ledger.
Only then does it put the allowed toy edit into the ticket worktree.
The result is `ready-for-host-verification`, **not acceptance**. Use
the existing independently trusted baseline Python unit test path and
scoped host `finalize → land → accept → release` sequence; this pilot
never performs those steps automatically.

Because no `OPENAI_API_KEY` is currently configured, this entire
lifecycle was exercised with a **mock Responses API response**, while Git
worktrees, state transitions, local host tests and commits were real.
The nine targeted tests cover completion, partial/incomplete response,
unauthorized source output, missing key, no retry after timeout, bad
zone/marker, input/output limits and full Git acceptance.

## Do not overclaim

An output-token cap and bounded request body do **not** constitute a
provider-enforced dollar cap; there is no proof of actual API spend,
provider-side project budget or model authentication until a real
credentialed call is completed and reconciled. This pilot is
deliberately incapable of acting on the user's production repositories.
Never disable `spend_guard.py` to use it. Version stays `2.3.0-dev`.
