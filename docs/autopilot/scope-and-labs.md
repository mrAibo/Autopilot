# Autopilot 2.3 — product scope versus research tools

Source of truth: [original brief](../../brief.md) (2026-10-25). The current audited [R01–R06 stable-release readiness matrix](release-readiness.md) separates implementation, host observation and live provider validation.
The brief expressly says: **do not rewrite the project; preserve the CLI;
do not use paid API calls for tests**. Work added beyond that scope is not
automatically a product requirement or release blocker.

## Required product (R01–R06)

| Requirement | Product surface | Evidence for release |
|---|---|---|
| R01 — accurate completion | `ap.py` gates, ticket lifecycle, manifest | Negative finish/done/reopen/rebase tests; no stale acceptance |
| R02 — safe operation | state locks, path validation, running dashboard ownership | Failed/parallel/crash tests without unsafe writes or secrets |
| R03 — economical model routing | routing policy, capabilities, profiles | Cheap/balanced/restricted rules actually checked in supported hosts; no inherited expensive agent silently |
| R04 — legible Dashboard | self-contained Dashboard 3.1, RU/EN, dark/light | Real headless/browser narrow and wide smoke |
| R05 — documentation | skill phases, READMEs, model/GUI guide | Clear distinction between instructions and verified host behavior |
| R06 — regressions and measured costs | cross-platform CI, tests, benchmark methodology | Four CI jobs green; costs only when measured |

The expected user flow remains **brief → manifest → briefing → spec →
plan → build → review → acceptance**. The product is a **skill**, not a new
standalone API service.

**Final G3 integrity:** Successful `check-plan` now records a SHA-256
contract over all requirement IDs, exact wording and rationale (including
constraints) plus the file names and bytes of each planned ticket. Normal
progress columns of `manifest.md` may still change during execution.
Before `finish`, Autopilot requires this contract to match and checks
the plan again; missing/replaced/deleted tasks, duplicate requirement IDs
and even `done` requirements with no owner block release. After a changed
plan passes another `check-plan`, saved G1/G2/G4 approvals are revoked and
blind acceptance must be repeated. An identical re-check preserves approvals.
Older in-progress 2.3-dev states without the contract must rerun
`ap.py check-plan` and renew G1/G2/G4 acceptance if their earlier G3 was green. This is a Git/project
consistency gate, not a cryptographic signature or real-model attestation. The normal `/autopilot` route does not require an
OpenAI API key, Python SDK, an HTTP worker, a background supervisor or
a separate experimental runtime.

**Native-GUI limitation and safe fallback:** A new run may explicitly choose the [`--sequential-host` mode](sequential-host.md) when named subagents are unavailable. It enforces one prepared/active ticket, detached Git worktree and independent baseline-tracked Python unittest evidence at `finalize`/`land`/`done`, without a fake native agent profile or model dispatch. This qualifies the **host test/Git protocol**, not a real GUI-selected model, effort or subscription cost. The user must confirm those outside Autopilot or stop. Default normal flows and existing run states are not automatically converted.

## Optional, not the product's default execution path

- `controller.py`, `host_loop.py`: deterministic host-side
  state/Git/test transitions used only when strict isolated execution is
  explicitly selected. They do not themselves execute an AI agent.
- `gui_bridge.py`, `codex_dispatch.py`, `spend_guard.py`: optional
  Codex GUI-to-CLI fallback. Actual paid execution remains **blocked** until
  its provider-side hard-cap gap is resolved; the GUI named-subagent
  capability was unavailable in the user's tested session. Do not make this
  optional adapter a default prerequisite.
- `offline_supervisor.py`, `offline_fixture_worker.py`,
  `process_containment.py`, `process_gate.py`: test-only subprocess
  lifecycle qualification. They are not production AI workers.
- `bounded_api_pilot.py`: strictly synthetic, manually approved,
  temp-project-only Responses API research harness. **No live API call was
  performed** because no API credential was configured. It is not installed
  by normal phase 0 and is not required for release.
- `worker_outcome.py`: read-only scoped worktree examination when an
  optional executor cannot make a Git commit. Host tests and acceptance
  are still required.

Keep these implementations isolated, documented and regressively tested
while they exist, but **do not expand or promote them to the user-facing
workflow without a concrete R01–R06 use case and separately demonstrated
benefit**.

## Decision rules for further changes

1. Each proposed change identifies an original brief requirement or a
   directly demonstrated regression in the default user journey.
2. Prefer a small test and patch to another dispatcher, integration,
   framework or install requirement.
3. Do not introduce a new paid dependency merely to validate Autopilot.
4. Treat account catalog, model pin, CI success and GUI skill discovery
   as distinct claims; none alone proves native child-agent execution.
5. Stable 2.3 requires the brief's R01–R06 gates, not passing optional
   experimental research milestones. Keep `2.3.0-dev` until then.

For historical implementation detail see [STATUS.md](../../STATUS.md)
and the individual `docs/autopilot/` research reports.
