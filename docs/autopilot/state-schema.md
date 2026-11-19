# State schema (`state.js`)

`state.js` carries `schemaVersion` next to the older `version` field. `version` remains the
run-format number; `schemaVersion` says which additive contract the dashboard and tools may rely on.

| `schemaVersion` | Meaning |
|---|---|
| `1` | `spendLedger` (last 200 normalized spend rows), ticket/plan fields and the existing dashboard contract |

Rules:

- A legacy `state.js` without `schemaVersion` is read as v1; the next `save` writes the field.
- A missing/`null` version is upgraded in memory; a non-integer, boolean, `< 1` or newer version is
  a clear `StateError` instead of a silent wrong render.
- New fields are additive; a new version is needed only when an existing field changes meaning or is
  removed. There is deliberately no JSON Schema dependency: the validator lives in
  `state_io.ensure_schema_version` and grows with the first breaking change.
- `state.spendLedger` is a bounded snapshot of `run-log.jsonl`, not a second spend source; see
  `docs/autopilot/measuring-cost.md`.
- `state.planFact` (optional, additive; absent in older runs): `{items: [{id: "T02.1", ticket, text,
  status: "сделано"|"частично"|"не сделано", evidence}], done, total}`, written by
  `ap.py plan-fact record` (an item without evidence is `не сделано`); the dashboard shows
  «план: N из M» only when the field exists.
- `blockingFindings[].status` may be `downgraded`: the second pass (`ap.py blocker confirm
  --verdict not-confirmed`) did not confirm the finding; it no longer blocks, the condition is
  copied to `concerns` as «не подтверждено вторым проходом: …». `confirmQuote` keeps the quote.
- `state.kind` (optional, additive; absent = `task`): `quick | bug | task | refactor`, set by
  `ap.py init --kind` / `set kind=`. Ticket fields: `startHead` (HEAD at `ticket NN start`, used by
  the pre-landing check), `redproof` (`{command, exit, at}`, `bug`: written only on a non-zero
  exit), `baseline` (`{command, exit, at}`, `refactor`: written only on exit 0). See `docs/adr/0020-work-kinds.md`.
