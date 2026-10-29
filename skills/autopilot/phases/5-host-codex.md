# Phase 5 — Codex host specifics

**Account-resolved capability discovery:** For Codex CLI (including Codex GUI projects using the same skill), run `python .autopilot/codex_capabilities.py --root . --write` to obtain current account-visible model/Effort pairs from `codex debug models`. It makes **no model calls** and never falls back to a bundled (unentitled) model catalog. To refresh an existing OpenAI catalog use `--overwrite` after review. This is capability advertising, not proof of server-side billing. GUI clients can expose different model catalogs; verify in the actual app before dispatch.

**Codex GUI named-agent unavailable:** Do **not** substitute a
generic worker inheriting the parent's model. Prefer the explicitly
approved **`--sequential-host`** single-session fallback described in
`docs/autopilot/sequential-host.md`; it supports real independent
host-side tests and Git isolation, but it does not attest a selected
AI model, token billing or a child agent. The optional
`python .autopilot/gui_bridge.py --root . --ticket NN` is a **read-only**
metadata preview. All real `gui_bridge.py --execute` and
`codex_dispatch.py --execute` invocations are currently **unconditionally
blocked by `spend_guard`**, regardless of approval flags or soft token
thresholds. Do not suggest bypassing that guard. See
`docs/autopilot/gui-cli-bridge.md` and `docs/autopilot/spend-guard.md`.

**Codex CLI integration (opt-in).** For OpenAI tickets already started in strict isolated mode, `python .autopilot/codex_dispatch.py NN --root .` performs a **read-only dry-run preflight**. Historically, `--execute` could launch a single separate `codex exec` process; **current production invocation is refused by `spend_guard`**. In that earlier design it used the approved model and effort, in the prepared worktree, using a bounded sandbox, then records reported token counters when available. This is a separate Codex worker process, **not** proof that an in-session custom named subagent inherited the right model. It does not auto-merge: review/test before `worktree land`. On Windows, if the sandbox can edit but cannot use shared Git metadata, run independent tests in the trusted host and invoke `ap.py worktree NN finalize --tests N/0` after verifying changed paths. Finalization stages only paths inside the ticket's exact zones and makes one Git commit outside the model sandbox, then `land` performs ordinary integration. A model turn without a worker commit is `incomplete`, not success. Optional `--optimization lean` activates a short Ponytail-inspired implementation policy in the standalone Codex worker; default is `off` and it is **not** the official upstream Ponytail plugin. Never invoke `--execute` without the run owner's approval of the planned model call. See `docs/autopilot/codex-cli.md`.

**Mandatory Codex native custom-agent preflight (fail closed):** A GUI-visible
TOML file is not evidence that a subagent inherited its exact model/Effort.
GPT-6 parent models currently advertise native multi-agent V2; the runtime
may omit named agent_type from spawn_agent even with feature flags disabled.
Before any strict Codex named-agent spawn, run in the project root:

    python3 .autopilot/codex_native_agents.py --codex-exe PATH_TO_GUI_BINARY --profile .codex/agents/AGENT.toml --name AGENT --parent-model ACTUAL_GUI_PARENT_MODEL --child-model APPROVED_MODEL --effort APPROVED_EFFORT

This gate checks pinned TOML, exact resolved model/Effort and V1/V2.
Catalog V1 is only a *candidate*, not proof of an executed child.
A quoted model reply, process exit 0 or supplied JSONL file does not prove
the child runtime; diagnostic JSONL is deliberately not authorization.
If strict named GUI agents are unavailable, use the explicit `--sequential-host` single-session mode with trusted host tests. The separately pinned Codex CLI worker is **disabled for real inference** by `spend_guard`; do not claim it is an available workaround. Never remove sandbox or
silently charge the parent model. Keep actual GUI E2E as a release gate.

**Dispatch guard:** On Codex the configuration pins a named custom agent but does not prevent an unrelated `spawn_agent` call; keep the default worker inexpensive and do not advertise this as a full security boundary.
