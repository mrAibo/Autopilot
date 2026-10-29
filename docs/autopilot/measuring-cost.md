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

