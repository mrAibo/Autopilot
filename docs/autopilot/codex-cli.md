# Real Codex CLI worker dispatch (Autopilot 2.3 development)

The optional `skills/autopilot/tools/codex_dispatch.py` invokes **one external Codex CLI process**, rather than trusting an in-session Codex `spawn_agent` request to respect a named custom agent. It pins the requested model and reasoning effort on the **actual CLI command line** and verifies the ticket, generated agent profile SHA, explicitly advertised capability pair and exact isolated Git worktree before launching anything.

This is an *executor process*; it is not yet a verified child agent in the parent Codex conversation and is not an automated `schedule` loop.

## Actual Windows CLI smoke and account models (2026-10-25)

After the owner's VPN was disabled, `codex doctor --summary` returned **21 ok, 0 fail** and confirmed HTTP provider endpoints reachable. `codex debug models` showed account-visible GPT-6 Luna, GPT-6 Sol, and GPT-6.1 Sol. A read-only `gpt-6-luna` call with `model_reasoning_effort=low`, stdin prompt and explicit EOF returned `CODEX_OK` in **5 seconds**, with **19,718 input tokens (12,672 cached), 7 output tokens**. Another invocation with `--ignore-user-config` and stdin returned `CONFIG_ISOLATED_OK` in **4 seconds**, with **16,643 input (11,776 cached), 9 output tokens**.

Previous timeouts were due to a test harness leaving stdin open (`Reading additional input from stdin...`), not a definitive model/network failure. The adapter already passes prompt via stdin and terminates input. These are actual completed **standalone CLI turns**, not proof that a GUI custom subagent used the model. High fixed input usage for tiny messages is a reason to benchmark before mass dispatch.

The `codex_capabilities.py` importer now reads the **resolved live account catalog**, not bundled defaults. Its discovered model/Effort matrix was validated on the owner's Windows machine and used with `model_router.py`; a simple task routed to `gpt-6-luna / low` with `status=ready`. No API keys are exposed.

## Setup and dry-run (no model calls)

- Codex CLI must be installed and signed in; check `codex --version` and `codex login status`.
- The Autopilot run must have `--strict-routing --isolated-tickets`.
- The ticket needs a verified OpenAI route, a prepared worktree and `ticket NN start`.
- Runtime must provide an actual host capability advertisement with the allowed `model` and `effort`.
- On Windows, the script resolves the **native** NPM Codex executable under `%APPDATA%\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\...\codex.exe` or you can pass its full path using `--codex-exe`. It does not use a shell or a `.cmd` shim.

```powershell
python .autopilot/codex_dispatch.py 01 --root .
```

Without `--execute` the script outputs the verified command, model, effort and checkout path. It does not print the ticket brief, secret environment values or initiate a model call.

## Host-verified handoff if Codex cannot make a Git commit (2026-10-26)

The Windows sandbox may allow editing source inside the checked-out worktree
while refusing access to shared Git metadata (e.g. `index.lock`). The executor
prompt now explicitly allows leaving **only approved source edits** without
committing. After a completed CLI turn with no source commit, the **read-only**
`worker_outcome.py` checks that the worktree remains at the exact ticket
base, the changed files are confined to its declared zone, no symlink/junction
escape exists and Git diff passes safety checks. When eligible, the adapter
reports `ready-for-host-verification`, with `accepted:false`,
`tests_verified:false` and **no worker commit**. This is NOT success.

A trusted host must independently run the baseline-tracked test suite
(`controller.py --suite test_core.py --advance` or the bounded host loop),
then the existing `worktrees.finalize` creates the commit from the verified
exact files; `land`/ `accept` / `release` still use the existing
strict lifecycle. Out-of-zone changes, no edits, unsafe paths, changed HEAD,
failed CLI turns and usage/accounting uncertainty do **not** qualify.

For a read-only diagnosis in an existing run (no model call or Git writes):

```powershell
py -3.13 .autopilot/worker_outcome.py --root . --ticket 01
```

Both the normal GUI bridge and direct CLI remain **blocked from new
paid execution** by `spend_guard.py` until verified hard caps exist.
This new handoff is proven using a synthetic offline subprocess that edits
only `src/core/calc.py` without committing, followed by independent host
tests, finalization, Git landing and acceptance. No new paid calls.

## Current safety stop (2026-10-25)

**Execution is intentionally disabled in `2.3.0-dev`** until a
verifiable provider-enforced per-call token or spending limit exists.
Both `codex_dispatch.py --execute` and `gui_bridge.py --execute`
fail closed before an external model call or a new attempt receipt.
No configuration or command-line bypass is provided. The example below
documents the intended future interface, not a currently usable call.
A user approving paid calls does not create a provider hard cap.

One authorized synthetic Git fixture real Codex CLI call reported
53,187 input (46,464 cached) and 341 output tokens, against a
recorded soft threshold of 2,000, and produced no worker Git commit
(`incomplete`). The receipt is non-replayable. See the
[spend guard and audit](spend-guard.md).

## Execute one task

```powershell
python .autopilot/codex_dispatch.py 01 --root . --execute --timeout 900
```

This uses `codex exec --cd <prepared-worktree> --model <approved-model> -c model_reasoning_effort=<approved-effort> --sandbox workspace-write --ignore-user-config --ephemeral --json -`. It passes the ticket body via stdin (not command-line arguments) and checks model, effort and profile integrity before the call. The only supported sandboxes are `read-only` and `workspace-write`; `danger-full-access` is not allowed. No built-in managed Codex `--worktree` is used because Autopilot already owns a detached checkout.

When the CLI reports a completed turn, the adapter parses the JSONL `thread.started` + `turn.completed.usage` records, attributes real reported input/output/cache-read counts via `ap.py usage`, and returns a summary. **Only the caller can approve the final worktree commit**: independently review changes and run checks, then `ap.py worktree NN land --tests N/0` and `ticket NN done` with the landed SHA. A successful CLI process is not an acceptance gate.

## Runtime Windows end-to-end result

On the owner's Windows system a real Codex CLI worker with explicit Luna/Low
and workspace-write edited one line of a disposable `calc.py`. The call
returned `turn.completed`, but the CLI sandbox could not find `python` and
could not write the Git `index.lock` under the shared primary `.git/worktrees`
directory. The first adapter version had incorrectly reported success.
The adapter now distinguishes `turn_completed` from `status` and
`accepted` and returns `incomplete` when it cannot verify a clean worker
commit.

Independent host tests then passed 2/2; a deliberately scoped trusted-host
commit was created, cherry-picked to the disposable main checkout, accepted
by `ticket done`, and the worktree released. No user project source was
touched. The new `worktree finalize --tests N/0` implements this controlled
host-side commit path in reusable form, with negative tests for wrong zones.

For Windows with `--ignore-user-config`, the CLI adapter explicitly selects
`windows.sandbox="elevated"` as the supported sandbox backend while keeping
`--sandbox workspace-write` (or `read-only`). This is **not**
`--danger-full-access`; unsupported/denied commands remain blocked.
Host-level ACLs and test execution must still be checked.

## Optional lean-coding mode

Add `--optimization lean` to enable a small built-in Ponytail-inspired
instruction set, or `--optimization off` (the default) for the baseline.
It is **not** the upstream Ponytail plugin and the cost effect is unknown.
See [optimization](optimization.md); do not globally install upstream Ponytail
or claim an A/B benchmark was done.

## Limitations and security

- **A passed CLI preflight does not prove the server used or billed the requested model.** A real runtime call with observed model data, host capability discovery and accounting is still needed. This adapter only makes the requested settings explicit and blocks stale state. It does not prove arbitrary nested agents are disabled.
- A per-ticket `.autopilot/dispatch-NN.lock` is created atomically before the model call and held through token reporting. An existing file blocks the next invocation. If a process crashed, **verify that its Codex child and model request are no longer running before removing the stale lock manually**. The lock file is excluded from Git.
- Model invocation can incur usage. `--execute` is intentionally opt-in. The runtime budget counts **already recorded** tokens, not an up-front charge reserve, and cannot stop a model mid-turn. Unexpected CLI failures can lack a usage event.
- This process is isolated by a Git worktree and Codex workspace-write sandbox, **not** a full VM; user-level environment, external network access and shared services may still exist.
- CLI `--ephemeral` reduces session persistence, but provider and OS activity may still be logged. Do not put credentials inside tickets.
- `--ignore-user-config` avoids surprising local model overrides, but may also change user MCP/skill access. The CLI login uses the user's normal Codex credentials; the adapter never reads them.
- The temporary CLI smoke on the user’s connected Windows system found `codex-cli 0.165.0-alpha.1` installed and `Logged in using ChatGPT`. An attempted read-only Luna turn did not finish within the observed interval and was cancelled, so **no real model/effort success was demonstrated by that smoke**.

## Follow-up

1. Confirm real CLI execution on a synthetic, disposable repository with read-only file system access.
2. Validate actual model/effort selected by the host (not just CLI arguments) and accept observed usage.
3. Add native Claude Code equivalent using feature/version verification.
4. Integrate `scheduler.py` with explicitly authorized dispatcher actions under process-safe capacity limits.
