# Claude Code qualification run (T13, 2026-10-29)

**Verdict: GO** for Claude Code strict routing on a subscription (Claude desktop app, Code tab), with the caveats below.

## Setup

- Disposable project: a small Python calculator with 3 tickets, each with its own unittest module (6 tests in total, all red at baseline).
- Strict Autopilot run built with the `main` tools after the T02–T11/F1/F2 merges. The guard (`claude_agent_guard.py`) and attestation hooks (`claude_attest.py`) were installed, and `permissions.deny` contained `Agent(fork)`.
- Host: Claude desktop app with its bundled Claude Code. `claude --version` on PATH reported 2.1.302; the OTel `service.version` was 4.29.0. `/status` cannot be opened in this host.
- Auth: subscription login. `ANTHROPIC_API_KEY` was not set, and `ANTHROPIC_BASE_URL` was set explicitly to `https://api.anthropic.com` to override an inherited local-router variable. OTel resource attributes show an account login; their values are not recorded here.
- Telemetry: `CLAUDE_CODE_ENABLE_TELEMETRY=1`, OTLP over http/json sent to a local sink, with `OTEL_LOG_TOOL_DETAILS=1` so that metrics carry the real `agent.name`. The env had to be set in user settings, because project settings ignore `OTEL_*`. It took effect for a newly started session without restarting the app.

## Tickets (run one at a time: 01, then 03, then 02)

| Ticket | Route | Tests | `done` exit | Attestation (lines / model / effort) |
|---|---|---|---|---|
| 01 fix `add`/`sub` | haiku / low | 2/0 | 0 | 7 / claude-haiku-5-5 / low |
| 03 add `percent` | haiku / low | 2/0 | 0 | 7 / claude-haiku-5-5 / low |
| 02 fix `mean` (depends on 01) | sonnet / medium | 2/0 | 0 | 9 / claude-sonnet-5-5 / medium |

- Every Agent call returned `async_launched`, and the strict `done` gate (T07) accepted each one, because `PostToolUse` carries `resolvedModel` even for async launches.
- The scheduler respected `--max-parallel 1` and the 02 → 01 dependency.
- The guard blocked a generic `general-purpose` agent with `Autopilot guard: Only explicitly configured Autopilot agents are allowed`.

## Gates

G1, G2 (`tests 6/0`, `coverage found=0`), G3 (`check-plan`) and G4 (blind check of 3 requirements without opening the tickets) were all `ok: true`. `stage build done`, `finish` and `commits` all returned exit 0.

## OpenTelemetry (`query_source = subagent`)

| Model / effort | Agent | Input | Output | Cache read | Cache creation | Cost USD (estimate) |
|---|---|---|---|---|---|---|
| haiku / low | executor-01 | 8 | 1434 | 35406 | 14116 | 0.0028 |
| haiku / low | executor-03 | 10 | 1282 | 52832 | 9072 | 0.0023 |
| sonnet / medium | executor-02 | 10 | 1077 | 48103 | 13361 | 0.0490 |
| **Total** | | 28 | 3793 | 136341 | 36549 | **0.0541** |

- The models and efforts in the metrics match the routes.
- The metric totals equal the sums of the `api_request` events.
- `cost.usage` is an estimate, not a charge to the subscription.
- The orchestrating main session (opus / medium) accounted for about 96 % of the estimated cost, and the subagents for about 4 %.

## Findings and caveats

1. **Bug, fixed in #54:** the ticket's `attestation` summary was dropped on the next `ap.py` call, because `publish_tickets()` keeps only whitelisted fields. The gate itself worked; only the stored evidence was lost.
2. The auth type was not confirmed via `/status`, only indirectly (no API key; account attributes present in OTel).
3. In OTel events, subagents appear as `query_source = agent:custom` with no `agent_id` (that needs v2.1.310+). Per-agent attribution is reliable in the metrics (`agent.name`), but in the events it can only be done by timing.
4. The ticket field «Модель: обычная» is not checked against the route (follow-up F3). The route is enforced by the pinned profiles and by attestation.
5. `finish` renames the run folder (drops `--wip`).
6. Not covered by T13: the terminal CLI (only the desktop app was run). Parallel tickets and the worktree/fork rules are covered by T14 below.

## T14 live probe: parallel tickets, isolation and fork rules (2026-10-29)

The same host (desktop app, subscription OAuth) ran a new strict run with `--isolated-tickets`: two independent haiku/low tickets, each in an Autopilot-owned worktree.

- **(a) Parallel tickets: PASS.** Both routed Agent calls went out in one message and ran truly in parallel: their attestation windows overlap. Each `agent_type` got its own attestation group, with no malformed or cross-attributed JSONL lines. The agents worked only inside the worktree path given in their prompt, and the primary tree stayed clean. Per ticket, `verify`, `finalize`, `land` and `done` all passed. Each stored attestation counted only its own lines (7 and 8). `ticket 02 done` before `land` was refused. G1–G4 were ok.
- **(b) `isolation: "worktree"`: PASS.** The guard blocked the call before launch with `Claude worktree isolation is not allowed in strict runs`, leaving no side effects.
- **(c) `Agent(fork)` without the guard: PASS.** After `finish`, when the guard allows everything, the host refused a fork with `Agent type 'fork' has been denied by permission rule 'Agent(fork)' from projectSettings`. While the guard is active, its message is shown first.
- **Found:** the probe's manifest used the status `ticket` instead of `in-ticket`, and every gate silently ignored those rows. `check-plan` (G3) now rejects unknown statuses.
- **Not run:** removing the guard entry while a run is active (auto mode refuses to edit project settings), and shared-tree parallel tickets.
- Environment note: the desktop session exposes the owner's 27-character router placeholder as `ANTHROPIC_API_KEY`. It is not a credential; authentication is the host's OAuth.

