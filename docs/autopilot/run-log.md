# Run log (`.autopilot/run-log.jsonl`)

Every run leaves one JSON line per event, so it is visible where time and tokens went:
phases, tickets and their retries, test runs, resets, waits for the user, executors.
The log only writes: a failure to write or parse it is swallowed and never stops an
`ap.py` command or a hook. It lives outside `state.js`, ticket fingerprints and the
signed gates, so it changes none of them. It is on by default and has no switch.

```bash
python3 .autopilot/ap.py report-run            # Markdown tables for the latest run in the log
python3 .autopilot/ap.py report-run --share    # the same, safe to attach to an issue
```

`report-run` reads only the log: it takes no state lock and works without `state.js`.
An empty or missing log prints one line and exits 0. The report covers the run of the last line
that has a `run`; lines without one are left out (no line has one: "в журнале нет записей с номером прогона").
Unreadable lines and lines of the wrong structure are skipped and counted: "пропущено испорченных строк: N"
(also in `--share`).

If `run_log.py` is not importable, every `ap.py` command prints one stderr line
("`run_log.py` не найден, журнал не пишется"; for an error inside the module it names the error type),
works as before, and `report-run` prints "журнал недоступен: ..." instead of "журнал пуст".

## Line format

Every line has `t` (local time, ISO with offset), `run` (run folder name) and `k` (kind).

| `k` | Fields | When |
|---|---|---|
| `phase` | `id`, `act` = start / done / skip / fail | `stage` |
| `ticket` | `id`, `act` = start / done / retry / fail / repair / review / escalate, `cause`; on `start` also `class` (from `class=` in the routing reason), `model`, `effort` (from `routing`, else `plannedRouting`) | `ticket NN <act>`; `cause` is `tests-failed` or the short tag from `--cause`; `escalate` is the single Haiku -> Sonnet move of `retry --cause tests --escalate` (`retry-policy.md`) |
| `gate` | `g`, `ok`, `reason` | G1-G4 decided; `reason` = `plan-changed` after a plan change |
| `tests` | `passed`, `failed`, `seconds`, `source` = ticket / host / manual | `tests N/M [--seconds S]`, `ticket ... --tests`, `worktree NN verify` (measured) |
| `reset` | `what` = ticket / gate, `id`, `reason` | edited unfinished ticket (`ticket-edited`), `ticket NN reset` (`manual`), gate reset (`plan-changed`) |
| `wait` | `kind`, `act` = start / end | `ask` and `answered` |
| `executor` | `agent_type`, `role`, `ticket`, `agent`, `model`, `effort`, `turns`, `input`, `output`, `cache_read`, `cache_write`, `source` = subagent / orchestrator / hook / manual, `origin` = claude-subagents / claude-transcript | `SubagentStop`: summed from the subagent transcript by `claude_attest.py` (reads at most 5 MB); `ap.py spend-subagents` and `spend-orchestrator` write the same kind |
| `spend` | the same fields as `executor` | accepted alias for a new spend source; readers treat both kinds as one ledger |

`role` is `executor`, `reviewer`, `explorer` or `acceptance` by the profile name
(`autopilot-<role>-...`; the repair executor is `executor`), otherwise `agent`. `executor` is the
historical line kind; `spend` is the same schema for future sources. Both are one ledger: readers
normalize them, keep the last row per agent and compute the same role/model/ticket totals. Older
lines without `role` get it from `agent_type` in the report. `model` and `effort` come from the subagent's profile `.claude/agents/<agent_type>.md`, else from the attested `resolvedModel`, else stay empty; the report shows such lines as «не указана». `report-run` also groups by model: tickets, share done at the first attempt, repairs, tokens per ticket. A second block, «Класс × модель × усилие», groups tickets by class, model family (`sonnet` = `claude-sonnet-5-5`) and effort over the **whole** journal (current and past runs): tickets, done at the first attempt, retries, Haiku -> Sonnet escalations, tokens per ticket; lines without the new fields count as «не указан». `plan-models` adds one `advice` line to its JSON from the same history (e.g. how many mechanical Haiku tickets were escalated); it never changes the route, and no history means no key.

**Limit:** the journal keeps one rotation (`run-log.1.jsonl`), so the history is the last two files, not all builds.

A failed write never stops a command, but it is counted in `.autopilot/run-log.fail`; `ap.py` shows the count as `state.logFailures` and the dashboard marks the log as incomplete.

Other fields are dropped. A string longer than 120 characters is cut; a value holding a
machine path (`C:\Users\...`, `/home/...`) becomes `"[path]"`.

## Rotation

When the file grows past 1 MB, the next write moves it to `run-log.1.jsonl` (replacing the
previous one) and starts a fresh `run-log.jsonl`. `report-run` reads both parts in order and
skips broken lines. `ap.py init` adds `.autopilot/run-log*.jsonl` to `.gitignore`: the log is
local diagnostics, not a record of what was promised.

## `--share`

Prints numbers and role types only: no run name, no ticket ids (tickets are numbered 1, 2, ...),
no absolute times (phases show durations), no agent profile names (they carry the run slug;
shown as `executor`, `reviewer`, ...), no reset reasons or causes.

## What the log does not hold

Prompts, messages, tool inputs, file contents, ticket titles, `--note` texts, machine paths,
secrets. `tests/test_no_machine_data.py` patterns are checked against a log produced by an
end-to-end run.
