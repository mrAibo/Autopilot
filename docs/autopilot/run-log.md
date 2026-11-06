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
| `ticket` | `id`, `act` = start / done / retry / fail / repair / review, `cause` | `ticket NN <act>`; `cause` is `tests-failed` or the short tag from `--cause` |
| `gate` | `g`, `ok`, `reason` | G1-G4 decided; `reason` = `plan-changed` after a plan change |
| `tests` | `passed`, `failed`, `seconds`, `source` = ticket / host / manual | `tests N/M [--seconds S]`, `ticket ... --tests`, `worktree NN verify` (measured) |
| `reset` | `what` = ticket / gate, `id`, `reason` | edited unfinished ticket (`ticket-edited`), `ticket NN reset` (`manual`), gate reset (`plan-changed`) |
| `wait` | `kind`, `act` = start / end | `ask` and `answered` |
| `executor` | `agent_type`, `role`, `turns`, `input`, `output`, `cache_read`, `cache_write` | `SubagentStop`: summed from the subagent transcript by `claude_attest.py` (reads at most 5 MB) |

`role` is `executor`, `reviewer`, `explorer` or `acceptance` by the profile name
(`autopilot-<role>-...`; the repair executor is `executor`), otherwise `agent`. The line kind stays
`executor`; older lines without `role` get it from `agent_type` in the report.

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
