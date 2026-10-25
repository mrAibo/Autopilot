# Telemetry and token threshold (Autopilot 2.3 development)

`ap.py` records **attributed token observations**. It does not price tokens or fabricate billing data.

## Report a real model call

```bash
python .autopilot/ap.py usage 03 --call-id claude:message-123 \
  --input 5000 --output 1200 --cache-read 3000 --cache-write 400 \
  --source claude-jsonl
```

Valid sources: `claude-jsonl`, `codex-jsonl`, `host-reported`, `manual`. The source is an attribution label, not a cryptographic verification. Only use actual harness-recorded counters and unique call IDs. Repeated identical IDs are idempotent; an ID with conflicting data is rejected. Each counter is a nonnegative integer; a zero-only event is refused.

Claude and Codex differ in what they include in input and cache readings. **Do not sum input + cache read + cache write to present an invoice**; the figures may overlap. The dashboard reports them separately and always labels cost as unavailable until a trustworthy price + accounting mechanism exists.

## Budget threshold

```bash
python .autopilot/ap.py budget --tokens 120000
```

This sets a **threshold of recorded input + output tokens**. New `ticket start` events are blocked once recorded usage meets or exceeds it. It is *not* a pre-paid spending cap, cannot stop a running model turn mid-call, and can be circumvented if usage isn't reported. Displayed as a threshold, not a guaranteed account credit limit.

The `usageEvents` journal keeps at most 2,000 events per run; if full, it fails instead of silently discarding earlier usage. Future iterations can add a dedicated append-only store and direct provider log import. Model cost forecasts should use measured post-run data, not this raw counter alone.

## Dashboard

Under “Models & resources”, the dashboard shows input, output, cache-read/cache-write counters and any recorded threshold. It explicitly distinguishes selected model profiles from observed consumption, and never silently treats missing usage as zero-cost.
