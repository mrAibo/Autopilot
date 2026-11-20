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

## Cache and orchestrator numbers in the run log

`report-run` and the dashboard "Details" tab now show two more numbers next to input and output tokens:

- **Cache read / cache write** per role, model and ticket, and the **hit share**: `cache_read / (input + cache_read + cache_write)`, whole percent, `—` when there is nothing to divide. `report-run` also prints the same by agent profile (not with `--share`), which shows whether the shared cache holds across executors of different tickets.
- **The `orchestrator` row**: tokens of the main session since the run started. `ap.py spend-orchestrator [--transcript PATH]` writes it (and `finish` calls it), one row per model, numbers and model name only, never message text. Calling it again replaces the earlier numbers, it does not add to them.
- **One ledger:** `state.spendLedger` is the last 200 normalized spend rows for the dashboard, built from the same `run-log.jsonl` lines that feed `compute_spend`; it is a snapshot, not a second source. `executor` and `spend` rows are read as one schema (`docs/autopilot/run-log.md`).

Limits, so the numbers are not over-read:

- **Cache is not a cost.** Reads, writes and input are priced differently, and the log keeps no prices. The hit share says how much input came from the cache, not what it cost.
- **The session log is a guess.** Without `--transcript`, the newest `*.jsonl` of `~/.claude/projects/<project folder>/` is taken (the root follows `CLAUDE_CONFIG_DIR`). With two sessions in one folder that is whichever wrote last; pass `--transcript` to choose.
- **The orchestrator is one line per run.** Main-session turns cannot honestly be assigned to a ticket, so it appears in role and model tables only, never per ticket. It is written at `finish`, so the dashboard has no orchestrator figure while the run is still going unless you call the command yourself.
- Sidechain (subagent) messages in the session log are skipped there: the subagents are counted from their own transcripts.

## Class x model x effort (calibration of the router)

`report-run` prints, after «## Модели», a table by the combination class x model x effort over every run in the journal: tickets, done at the first attempt, retries, Haiku -> Sonnet escalations, tokens per ticket (input + output of the ticket's executor rows). The combination is read from the `start` row of the ticket; old rows without `class`/`model`/`effort` fall into «не указан». `--share` prints the same numbers, no ticket names. The history is bounded by one journal rotation (`run-log.md`).

## Subagent spend in a normal run

Without `--strict-routing` there are no hooks, but Claude Code keeps a log per subagent: `<session log without .jsonl>/subagents/agent-<id>.jsonl` plus `agent-<id>.meta.json`. `ap.py spend-subagents [--transcript PATH]` (and `finish`) writes one spend row per agent (`k=executor` is the historical name; `k=spend` is accepted too): token sums, model, `agent_type`, agent id, role, ticket, `source=subagent`, `origin=claude-subagents`. Message text, prompts and `description` are never read or saved.

- Only messages since the run's `startedAt` count; a repeated `message.id` counts once (the last). An agent still running is counted by what is written so far.
- Calling it again does not double the numbers: readers keep the last row per agent. In a strict run, hook rows win: the log rows of an `autopilot-…` agent are dropped only when the hooks also wrote a row for that same `agent_type`, so an agent the hooks missed keeps its spend.
- The ticket comes from the agent profile name (`autopilot-executor-01-…` → `01`). Only an executor or a general-purpose agent without a profile number falls back to the single `startedAt…finishedAt` window; a reviewer is never given somebody else's ticket by time. In a parallel wave (several fit) or with none, the row has no ticket. A broken or missing `.meta.json` gives role `agent`; a BOM at its start is fine (`utf-8-sig`). The permanent profiles `autopilot-executor`, `autopilot-reviewer`, `autopilot-acceptance` and `autopilot-explorer` give their roles too.
- No `subagents/` folder prints "субагентов нет" and `finish` goes on.

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

## Measured: start context by agent type and orchestrator turns per landing (2026-11-16, before the light profiles)

Source: `python tools/measure-run.py <project> all` on the real Claude Code logs of this project: 14 of 21 sessions that have subagents, 212 contexts (the session that was running at the time is among them). The tool reads numbers, timestamps, ids, tool names, `subagent_type` and `agentType` only; message text and prompts are not read or saved (the context label is the `description` from `meta.json`, as before). One project on one machine: a direction, not a precision.

**Start context** is the first step of a context: input + cache read + cache write. By `agentType` of the subagent (`autopilot-<role>-*` is the strict run's profile per ticket or per run):

| Agent type | Contexts | Min | Median | Max |
|---|---:|---:|---:|---:|
| `general-purpose` (ordinary run) | 58 | 71K | 72K | 85K |
| no `agentType` in `meta.json` (older sessions) | 9 | 71K | 71K | 71K |
| `Explore` | 8 | 58K | 59K | 64K |
| `autopilot-executor-*` (strict) | 42 | 11K | 12K | 13K |
| `autopilot-reviewer-*` (strict) | 42 | 10K | 11K | 12K |
| `autopilot-explorer-*` (strict) | 20 | 9K | 10K | 10K |
| `autopilot-acceptance-*` (strict) | 19 | 7K | 8K | 9K |

An ordinary run starts every subagent at about 72K; a profile with a short tool list starts at 7–13K. The permanent light profiles of `ap.py init` have the same short tool lists, so the expected gap is the same, but **this build cannot measure it**: Claude Code sees a profile written during a chat only from the next chat. The "after" row is for the first build run in a new chat (`PROGRESS.md`).

**Orchestrator turns between subagents.** A window opens when a subagent returns (a background agent: the last line written in its own log; otherwise its tool result) and closes at the next subagent launch (that step is in) or the next return. Steps are distinct main-session replies in the window; "norm. units" are output ×5 + cache write ×1.25 + cache read ×0.1 over those steps. Windows are grouped by the role of the agent that returned (its label, the existing role rules).

| After | Windows | Steps | Steps per window | Norm. units per window |
|---|---:|---:|---:|---:|
| executor | 49 | 401 | 8.2 | 0.255M |
| point and branch review | 42 | 143 | 3.4 | 0.112M |
| blind acceptance | 35 | 383 | 10.9 | 0.358M |
| repair | 23 | 100 | 4.3 | 0.215M |
| exploring | 6 | 28 | 4.7 | 0.203M |
| memory | 4 | 52 | 13.0 | 0.369M |
| role not recognised | 28 | 229 | 8.2 | 0.511M |

After an executor the main session spends on average **8.2 steps, median 3** (49 windows, 14 sessions); most of the steps are `Bash` (245 of 401: `git status`, the full check, the commit, `ap.py`), the rest reading the contract, planning, and launching the next agent.

Решение по R05: три шага и больше (в среднем 8,2 на посадку таска, медиана 3; 49 окон после возврата исполнителя, 14 сессий), поэтому команда `ticket NN land` сделана.

Caveats, so the numbers are not over-read:

- **A window is not a clean landing.** It holds everything the orchestrator did between the two events: reading the contract, the memory notes, plan updates, a chat with the user. That inflates the mean (8.2) over the median (3); the real cost of landing is nearer the median, and nothing here separates the two.
- **49 windows are returns, not tickets.** A retry or a repair gives one more window, a parallel wave shares its windows, and ticket numbers are not read. The tail of a session (the final report) has no closing event and is not counted.
- **The role of a returned agent comes from its `description`.** Windows after an agent whose label no rule recognises sit in "role not recognised" (28) and are not in the executor row; the executor row may be low.
- **A background agent returns when its log ends.** The orchestrator notices later, so the window can start before its first step.
- **Start context is one number per context**, taken from the first reply in its log; the cache state of that first call is not separated.

`measure-run.py <project>` (one session, the one with the most subagents, or `<project> <session id>`) prints the same two tables for that session next to the per-context table, which now has the columns "старт" (start context) and "тип агента".

## Лёгкие профили: замер «после» (сборка 2026-11-17-orchestrator-spend-waves-4-6)

Источник: `python tools/measure-run.py . <id сессии>` на журнале сессии этой сборки (16 субагентов на момент замера, сборка ещё не сдана: слепая приёмка шла, хвост сессии не посчитан). Читаются только числа, типы агентов и метки; текст не читается.

| Тип агента | Контекстов | Стартовый контекст (мин / медиана / макс) |
|---|---|---|
| `autopilot-executor` | 11 | 14K / 14K / 15K |
| `autopilot-reviewer` | 3 | 14K / 14K / 14K |
| `autopilot-acceptance` | 1 | 8K / 8K / 8K |
| `general-purpose` (разведка до записи профилей, один запуск) | 1 | 86K |

«До»: `general-purpose` — 82–83 тыс. (20 запусков, прошлые замеры выше), профили с `tools:` строгого прогона — 8–13 тыс. Лёгкий `autopilot-executor` в обычном прогоне стартует с 14 тыс.: примерно в шесть раз меньше `general-purpose`, ближе к профилям строгого прогона. Средний контекст исполнителя на шаге 31–87 тыс. против 107–238 тыс. у `general-purpose` в сессии `6be83693`.

Ходы оркестратора на посадку таска (R05 + `ticket NN land`): 9 окон после исполнителя, в среднем **2,9 шага, медиана 2** (до: 8,2 и 3).

Оговорки:

- Одна сессия, одна машина: направление, не точность. Первый запуск субагента (разведка) шёл до того, как Claude Code увидел профили (`init` записал их в этой же сессии), поэтому он на `general-purpose`; профили стали видны уже со следующего вызова в той же сессии — осторожнее, чем «со следующего чата», как считалось раньше.
- Исполнители этой сборки получали пути, а не содержимое; на стартовый контекст влияют только список инструментов и системный запрос профиля.
- Исполнители — Sonnet с усилием из маршрута; профиль `model`/`effort` не несёт, они шли параметрами вызова: параметр модели в вызове профиль не отменил (проверено фактом запуска на Sonnet).
- Стоимость не мерена: нормированные единицы по сессии — 8,99 млн на 449 шагов, из них оркестратор 38 %.

## Доля блокирующих, снятых вторым проходом

Вердикт второго прохода хранится в самом блокере: `blockingFindings[].secondPass = {verdict, quote, at}` (и поле `verdict` в событии журнала `blocker`). Доля снятых = блокеры с `secondPass.verdict == "not-confirmed"` (статус `downgraded`) / блокеры с любым `secondPass`. Блокеры прошлых сборок `secondPass` не несут и в расчёт не входят: на них число не измерено.

## Speed changes: before and after

Not measured (not measured, on purpose): parallel check and review, the one-message bundle, the silence watchdog and the worktree dependency copy have no before/after numbers. The earlier runs' logs do not record how long a red check waited for the review or how long agents sat silent, so there is no baseline to compare with, and a single run after the change would not be a comparison. To measure: on the next build record the minutes between `ticket NN land` and the reviewer's verdict (`run-log.jsonl`) and the count of `ap.py silence` exits with code 3; compare with this build.
