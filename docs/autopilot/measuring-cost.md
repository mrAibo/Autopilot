# Measuring the cost of a run

Two ways to see what an Autopilot run spent. Both give **estimates, not charges**: `cost.usage` is a
list-price estimate and says nothing about what a subscription is billed.

| Method | Tool | Needs | Best for |
|---|---|---|---|
| OpenTelemetry (live) | `tools/otel_sink.py` + `tools/otel_summary.py` | user-level env, a local sink | main vs subagent cost per model/effort, A/B runs |
| Transcript logs (after the fact) | `tools/measure-run.py <project dir>` | nothing, reads `~/.claude/projects/` | context growth, rule compliance, a run you did not instrument |

## OpenTelemetry

Claude Code reads `OTEL_*` and `CLAUDE_CODE_ENABLE_TELEMETRY` only from **user settings
(`~/.claude/settings.json`) or the shell**, never from a project's `.claude/settings.json`.

1. **Back up** `~/.claude/settings.json`, then merge these keys into its existing `env` (do not replace it):

   ```json
   "env": {
     "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
     "OTEL_METRICS_EXPORTER": "otlp",
     "OTEL_LOGS_EXPORTER": "otlp",
     "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json",
     "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "http://127.0.0.1:4318/v1/metrics",
     "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "http://127.0.0.1:4318/v1/logs",
     "OTEL_METRIC_EXPORT_INTERVAL": "5000",
     "OTEL_LOGS_EXPORT_INTERVAL": "2000",
     "OTEL_LOG_TOOL_DETAILS": "1"
   }
   ```

   `OTEL_LOG_TOOL_DETAILS=1` is what puts the real agent name into `agent.name`; without it you get `custom`.
2. **Start the sink**, one directory per run so runs never mix: `python tools/otel_sink.py --dir <run>/otel`
   (`--port` defaults to 4318; it binds `127.0.0.1` only). Keep it running.
3. **Fully restart** the Claude Code app or CLI (env is read at start), run the work, wait about 10 s after the last
   agent finishes so the last metrics are exported, then stop the sink (Ctrl+C).
4. **Summarize**: `python tools/otel_summary.py --dir <run>/otel` prints subagent rows per
   `query_source x model x effort` (tokens in / out / cacheRead / cacheCreation, cost) and a
   main-vs-subagent cost share. `--all` also lists main and auxiliary rows. The summary reads both
   metrics and `api_request` events; in events `agent:*` counts as subagent and `sdk` as the main session.
5. **Restore** `~/.claude/settings.json` from the backup (remove the OTel keys) and restart the app.

Privacy: with `OTEL_LOG_TOOL_DETAILS=1` tool arguments (file paths, commands) land in `<run>/otel/*.jsonl`
on your disk. Nothing leaves the machine, but do not publish or commit those files.

Limits: assumes delta temporality (the Claude Code default); a protobuf/gzip exporter is recorded only as a
marker line, so keep `http/json`.

## Measured: main-session model and ticket routing (2026-10-29)

Same 3-ticket strict run in all three cases (Claude desktop app, subscription OAuth, OTel `cost.usage` estimates in USD, not charges). All runs were VALID: 3/3 tickets done through the attestation gate, G1–G4 ok.

| Run | Main session | Ticket routes | Main | Subagents | Total |
|---|---|---|---:|---:|---:|
| T13 | Opus / medium | haiku/low ×2, sonnet/medium | 1.40 | 0.054 | ≈1.45 |
| A | Sonnet / medium | haiku/low ×2, sonnet/medium | 0.63 | 0.050 | ≈0.68 |
| B | Sonnet / medium | sonnet/medium ×3 | 0.44 | 0.111 | ≈0.56 |

What this shows, and what it does not:
- **Main-session model is the biggest lever.** Opus → Sonnet cut the total by about 53 % (T13 → A) with the same subagent work.
- **Ticket routing halves subagent cost.** Subagents cost 0.050 with routing versus 0.111 without (A vs B), about 55 % less.
- **On a run this small, routing does not show up in the total.** B came out cheaper overall than A because its main session was cheaper (0.44 vs 0.63; mostly cache creation, 58K vs 106K tokens). That is run-to-run noise in the orchestrator, larger than the whole subagent bill here.
- One run per variant, three tiny tickets: treat these numbers as direction, not precision. Larger projects shift the share toward subagents, where routing matters more.


## Measured: does a local code graph make `/autopilot audit` cheaper? (2026-10-30)

Question: would [graphify](https://github.com/Graphify-Labs/graphify) (Apache-2.0, local tree-sitter code graph, no LLM, no cloud) cut the cost of an audit? Project: a copy of a real Python repo, ~92k lines / 274 source files (graph: 7,079 nodes, 19,685 edges, built in 17 s with `graphify update .`). Headless `claude -p "/autopilot audit" --model sonnet --output-format json`, one run per variant, so direction, not precision (`total_cost_usd`, list-price estimates).

| Run | Total USD | Sonnet | Haiku | Turns | Findings | Graph actually queried |
|---|---:|---:|---:|---:|---:|---|
| No graph | 1.91 | 1.29 | 0.62 | 6 | 19 | n/a |
| Graph present, hinted in `CLAUDE.md` | 1.74 | 1.37 | 0.37 | 6 | 14 | **never** |
| Graph present, use mandated in `CLAUDE.md` | 1.51 | 1.09 | 0.43 | 4 | 14 | some explorers; one said it skipped it |

What this shows, and what it does not:
- **A hint is ignored.** With the graph only mentioned, no agent called `graphify` once; the 9 % difference to the baseline is run-to-run noise.
- **Mandated use saved ~21 %** (1.91 → 1.51), but on a single run, with fewer findings (14 vs 19), and not all explorers obeyed. That is inside the noise seen between the first two runs, so it is not a reproducible saving.
- **The main session is not helped.** Sonnet (main session plus the strong-tier verifier) stayed at 1.1–1.4 USD, about 65–70 % of every run; the graph can only touch the cheap Haiku explorers (0.4–0.6 USD).
- **Quality was not lost on the top items.** The two most severe findings (a module imported but missing from the repo; a Windows process-liveness probe that always returns False) were confirmed in all runs and re-checked against the code. The graph run did not find anything the baseline missed.

Decision: **not integrated.** The possible gain (a fraction of the Haiku explorer bill) is small, unproven, and depends on agents obeying an instruction they ignore by default; the cost is an external dependency, a stale-graph risk and docs in three languages. Revisit if an audit on a much larger project (200k+ lines) shows the explorer share dominating the bill.
