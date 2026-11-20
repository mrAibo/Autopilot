# Phase 0 — Instruments

**Existing project upgrade (Dashboard 3.1):** the initial Phase 0 copies the dashboard template into the target project. Updating the skill does NOT replace those existing project-local HTML copies. For a project with an existing .autopilot/state.js, run the installed skill's tools/dashboard_upgrade.py --project TARGET_DIR instead of blindly copying the new template: it validates the project slug, embeds the latest state.js snapshot, and backs up the old page before atomic replacement. Reload the Dashboard tab afterwards. This does not reset tickets, specs, project code or application data.

The user's live view of the run: `.autopilot/dashboard.html`, a copy of the template, showing `.autopilot/state.js`. **You never edit either by hand.** Every event of the run is one call to `.autopilot/ap.py`, which stamps the time, recounts the requirements from `manifest.md`, closes the stages the run has passed, writes a snapshot of the state into the page and keeps a static server alive for it. This file is read once, in Phase 0; the command table in §4 is what you use for the rest of the run.

## 1. Find the skill, install the tools

Runs on every flight — new repo, new feature, resume alike. Find the skill folder, then one command; it is idempotent and picks up whatever the installed skill has learned since.

```bash
TPL=$(find -L ~/.claude/skills ~/.agents/skills ~/.claude/plugins .claude/skills .agents/skills \
        -maxdepth 6 -name dashboard-template.html 2>/dev/null | head -1)
[ -n "$TPL" ] && TPL=$(cd "$(dirname "$TPL")" && pwd -P)/dashboard-template.html
command -v cygpath >/dev/null && TPL=$(cygpath -m "$TPL")   # Windows: C:/…, а не /c/…
python3 "${TPL%/phases/*}/tools/ap.py" bootstrap --project "$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
```

It copies the dashboard template and every `.py` of the skill's `tools/` into `.autopilot/`, makes `index.html` (a symlink; where links are unavailable, a redirecting copy) and prints **`skillDir = …`**. In a project that already has `state.js` the dashboard goes through `dashboard_upgrade.py` (the snapshot is kept), not through a blind copy. It refuses while a ticket is `in-progress`/`review`/`repair`, and in a signed run when this is not the skill folder pinned at `init`; it never creates `state.lock` in the skill folder.

- **`skillDir` is what every subagent contract hangs on** — `prompts/executor.md` and `prompts/review.md` go down as paths built from it. It goes into `init` below and lives in `state.js`, never only in your context.
- `find -L` and no `*` in it: skills are installed through symlinks, which a plain `find` does not follow, and an unmatched glob aborts the whole line in zsh. Empty output → widen the search once by hand and carry on.
- **`python3` not a working interpreter** — on Windows it can be the Microsoft Store stub → use `python` or `py -3` wherever this skill says `python3`.
- `bootstrap` and `doctor` run from the skill folder, whose path no `allowed-tools` mask can pin without a free `*`, so Claude Code asks permission for them once.
- **`bootstrap` is needed before the first `init`** (there is no `.autopilot/ap.py` yet). After that `ap.py init` and `ap.py stage <id>` refresh the `.py` tools in `.autopilot/` from `skillDir/tools/` by themselves — new files of the skill included, only when no ticket is `in-progress`/`review`/`repair`; `ap.py` replaces its own copy at the end of the command — and `ap.py upgrade-tools` does it by hand.
- Never regenerate the template, never read it into context, never edit it.

## 2. Start the run

```bash
python3 .autopilot/ap.py init --slug telegram-repair-bot --title "Телеграм-бот для заявок на ремонт" \
  --mode semi --depth normal --memory-file AGENTS.md --memory-owner autopilot \
  --skill-dir "<skillDir>" --strict-routing --check-update
```

**Unsupported native named-agent host:** If the user chooses a single-session fallback after the host's model/Effort and subscription status have been reviewed, replace `--strict-routing` above with **`--sequential-host`** (implies `--isolated-tickets`, one ticket at a time and mandatory independently rerun baseline unittest). Do not combine both flags or pretend a named child ran. See `docs/autopilot/sequential-host.md`. Never reinitialize a live existing run merely to change modes. The optional billable GUI/CLI worker is still blocked by `spend_guard`.

It creates the run directory `<YYYY-MM-DD>-<slug>--wip/` with `tickets/` inside, writes `state.js` with all eight stages (`preflight` active), adds the run's row to `.autopilot/README.md` (writing the file on a new repo), puts `.autopilot/serve.*` and `.autopilot/state.lock` into `.gitignore`, writes the four permanent light profiles to `.claude/agents/` (an ordinary run, `phases/5-host-claude.md`), raises the server and prints its address. A finished run's `state.js` is archived into that run's directory first; an unfinished one means this is a resume, and `init` refuses (`phases/0-resume.md`).

A line starting with **`↑`** is a hint: put it into the opening block as it is — one line, not a question, not a stop. There can be **two**: a newer Autopilot is out (never an update mid-run), and the main chat has grown past the context threshold (`AUTOPILOT_CONTEXT_HINT`, 150000 by default, `0` turns it off) — `/autopilot` in a new chat continues from this place. The second one also comes with `stage build`, `stage review` and `stage final`; no session log found means no line. A line starting with **`?`** is one question, asked once (`phases/5-host-claude.md`, the ordinary run): light profiles in the Claude Code settings folder, answered by `ap.py agents install-user`.

Also say once, in one line, that the main session's model is the biggest cost driver and Sonnet is recommended for the build (`/model` switches it); never block, never ask. For a complex or fuzzy idea Opus can plan first; the offer to build in a fresh Sonnet chat comes at the end of Phase 4 (`phases/4-plan.md`), not here.

## 3. Open it once, yourself

Immediately after `init`, before Phase 1 asks anything.

**Path A — the pane beside the chat (preferred), over http.** In Claude Code: `preview_start({url: "http://localhost:PORT"})`, then `navigate` to `/dashboard.html`. A bare `navigate` to localhost without `preview_start` is refused, and so is `127.0.0.1`. Never hand the pane a `file://` path: it loads the page as `data:`, which cannot fetch `state.js` — the snapshot shows, the clocks never move. If `preview_start` is not in your tool list, search for it before concluding there is no pane.

**Say the address in the chat too** — some clients show the pane only as a card with an «Open» button.

**Path B — no pane:** `open`, `xdg-open` or `start` on `.autopilot/dashboard.html`; a real browser polls `state.js` from `file://` by itself.

**No working python at all** means no `ap.py` and no dashboard. Say so in one line, skip the dashboard, keep the manifest's statuses by hand, and check G3 yourself against the ticket files. Everything else in the run is unchanged.

- Opened **once per flight**; on a resume **always re-pointed** — a tab does not outlive its session.
- `$SSH_CONNECTION` or `$CI` set → print the path, open nothing.
- A failure to open is not an error: print the path in one line and carry on.
- The server binds `127.0.0.1` only — it serves the run's own files.
- **«Дашборд отвалился», «подними дашборд»** — the machine slept or the server died. One bare `python3 .autopilot/ap.py`: it raises the server on the same port, and the open tab comes back by itself. Re-point the pane only if the printed address changed. One line in the chat, no investigation.

## 4. One call per event

| Event | Call |
|---|---|
| entering a phase | `stage <id>` — the stage before it closes itself |
| a phase consciously not run | `stage <id> skip --note "причина"` |
| tier decided | `set tier=T2` |
| ticket files written | `tickets` — publishes every ticket; manifest rows `in-spec` → `in-ticket` |
| gate G3 | `check-plan` |
| the plan commit is made | `set baseCommit=<sha>` — chained with it (`phases/4-plan.md`) |
| a ticket or a whole wave launched | `ticket 02 03 start` — **before** the subagents go out |
| a ticket goes to point review | `ticket 02 review` |
| a blocking finding goes back | `ticket 02 repair --note "условие одной строкой"` — opens an outstanding `B##` blocker |
| an independent re-review confirms a fix | `blocker resolve --id B01 --commit <newSHA> --tests 34/0 --note "конкретный результат ревью"` |
| whole-branch BLOCKING not tied to a repair | `blocker open --note "условие"` (optional `--ticket 02`) |
| a failed ticket restarts | `ticket 02 retry` |
| committed | `ticket 02 done --tests 34/0 --commit <sha>` (+ `--placeholder R05` for a stubbed row) — closes the manifest rows whose tickets are all done |
| failed for good | `ticket 02 fail --note "что блокирует"` |
| a deferred finding | `add concerns "файл:строка — что не так"` |
| a stub, an assumption, an empty variable | `add debt.placeholders "…"` · `add debt.assumptions "…"` · `add debt.emptyEnv NAME` |
| an `A##` that reached the code | `add additions "что — ради R01"` |
| a finding for the final report | `add report "…"` |
| G2 result | `coverage found=2 fixed=1 deferred=1 --item "R07 — отложено: …"` |
| blind acceptance | one call: `blind checked=12 matched=11 --mismatch "R07 — статус не виден" --mismatch "…"` |
| a full check outside a ticket | `tests 34/0` (+ `--seconds 42` if you timed it) |
| the run waits for the user — a briefing round, the manual spec or plan gate, the manual acceptance of the delivery (`accept`: only in **manual**, after the report, before `finish`), a yes/no before an irreversible action, a stop condition | `ask briefing\|spec\|plan\|accept\|action\|stop --note "что ждём, одной строкой"` — chained with nothing: the message goes out after it |
| the user may answer with a button on the dashboard (`briefing`, `spec`, `plan`, `accept` only — never `action` or `stop`) | `await [--timeout 300]` after the message went out (the host runs it in the background where it can). Code 0 prints one JSON line: `source` `dashboard` with `answer` (the typed briefing text; empty for the others) or `chat`; code 3 `нет ответа` — ask once in the chat and go on with the chat's answer; code 4 — nothing is awaited. The typed answer lives only in that line and in `serve.answer.json`, never in `state.js`. A button only closes the wait: it is not the user's words for `finish --by-user`, `ticket NN reset --by-user`, `opus approve` or `dropped` |
| the answer came | `answered` — or nothing, when the next call is a `stage` or `ticket`: those close the wait themselves |
| the run lands | `finish --result "одна строка: что теперь есть"` — a landing with caveats only with the user's words: `finish --result "…" --by-user "<цитата>"` (writes `landedWith`) |
| the user asks for the dashboard address | `url` — prints the address with the token; never paste it into the chat or a screenshot: no other command prints it (the status line shows the address without `?t=`) |
| the whole pre-flight at once (Phase 0, from the skill folder, before `init`) | `python3 "<skillDir>/tools/ap.py" doctor` — one line each for `git-check`, the Claude Code version, `advisorModel`, `repo_doctor`; code 2 only when Git cannot write or Claude Code is below the minimum |
| Git accepts writes (Phase 0, before `init`) | `git-check` — a refusal stops the run |
| the tools into a project (Phase 0, from the skill folder) | `python3 "<skillDir>/tools/ap.py" bootstrap --project .` — §1 |
| a generator the plan declared in `interfaces.md` («Команды-генераторы») | `chore <name>` — runs it, refuses if anything but its declared files changed, commits only those with `Autopilot-Run`; `0` also for «нечего коммитить» |
| a ticket returns green and is to be landed | `ticket 02 land --message "T02: …" --requirements R01,R02 [--zone a/,b/]` — `phases/5-subagents.md`; refuses in an isolated run |
| the user lifts a repair/retry limit or reopens a failed ticket | `ticket 02 reset --by-user "<цитата>"` — never without their words |
| Opus (only by the user's yes) | `opus propose` (print only) · `opus approve [--tickets 03,05] [--roles repair,reviewer] --by-user "<цитата>"` · `opus status` (also checks the approval signature) · `agent-for reviewer\|repair [--diff-lines N]` — prints the agent to call, the Opus profile only if the user approved that role (`phases/4-plan.md`) |
| the user answers the `?` line from `init` (light profiles in the Claude Code settings folder) | `agents install-user --by-user "<цитата>"` writes the four profiles to `agents/` there · `agents install-user --decline` remembers a no; neither writes anything outside the project without the user's words |
| old runs left `autopilot-*` profiles in `.claude/agents/` | `agents prune` lists them, `agents prune --apply` deletes those no unfinished run uses (never the four permanent ones) |
| the installed skill got newer tools (no ticket in `in-progress`/`review`/`repair`) | `upgrade-tools` — copies the `.py` that differ from `skillDir/tools/`, and the skill's new ones, and prints their names; `init` and every `stage <id>` do it by themselves |
| where the time and tokens went (reads `.autopilot/run-log.jsonl`, never blocks) | `report-run` — `report-run --share` for an issue attachment, no project data (`docs/autopilot/run-log.md`) |
| a resume, before anything relaunches | `commits` — every `done` ticket's commit still in `HEAD`; a `!` line is a ticket to reset (`phases/0-resume.md`) |

All are `python3 .autopilot/ap.py …`, and `add` takes several values in one call. **Chain a call with the command it belongs to**, so one event is one turn — the commit of a ticket and its `done` go together (`ticket NN land`, `phases/5-subagents.md`). Never chain a commit after a check whose result you have not read: `| tail` always exits 0.

- **Two kinds of `!` lines.** From ordinary calls — a stage skipped in the books, a ticket without a start — they are bookkeeping: fixed in the same turn, one call, not investigated. From `check-plan` they are defects of the plan, and gate G3 does not pass until they are gone.
- Manifest rows the tool cannot know — `in-spec`, `deferred`, `dropped`, a new `G##` or `D##` — you edit in `manifest.md` yourself; `in-ticket`, `done` and `placeholder` are the tool's. The counts on the dashboard follow on the next call.
- **Never a secret value** in any call: `emptyEnv` holds names, and an `ask` note says *what* is awaited, never a value.
- **`ask` is what puts «Ждём тебя» on the dashboard** and stops its clocks — the time the user takes to answer is not build time. A question you send without it leaves the page ticking as if work were going on.
- The page repaints every ten seconds, counts working time rather than calendar time, and freezes at `finish`. Mention it **once**, in the opening block, and never explain it in the chat.

After each ticket the user gets one plain line in the chat — what became possible, and the count: «Бот принимает заявки — 3 из 8 готово». No file lists, no ticket numbers.
