# Phase 5 — Claude Code host specifics

The project-level blocking hook: `python .autopilot/claude_agent_guard.py --install-hook --root .` (inspect `.claude/settings.json`; the guard is active only while an unfinished strict run exists). `SubagentStart` hooks are too late to block a launch, so this uses `PreToolUse` on `Agent|Task`.

Rules for the orchestrator (see `docs/autopilot/claude-code.md`, `docs/autopilot/claude-fork-policy.md`):

- Phase 4 installs both hooks (`python .autopilot/claude_agent_guard.py --install-hook --root .` and `python .autopilot/claude_attest.py --install-hook --root .`) and every profile **before** this session started (`phases/4-plan.md`); rerunning them is idempotent. Claude Code sees only agents that existed at session start.
- Call only routed `autopilot-…` agents; the guard denies any other Agent name. `--install-hook` also denies `Agent(fork)`.
- Roles, from `state.js` → `roleAgents`: point review and repair re-review → `roleAgents.reviewer.agentType`; whole-branch review → the name printed by `ap.py agent-for reviewer --diff-lines N` (N from `git diff --shortstat <baseCommit>..HEAD`; the Opus reviewer only when the user approved the `reviewer` role and N is over 3000, else `roleAgents.reviewer.agentType`); blind acceptance → `roleAgents.acceptance.agentType`; the coverage reader and the memory and ADR agents → `roleAgents.explorer.agentType` (read-only: they return the text, and you write the memory file and `docs/adr/` verbatim). Never an executor profile for another role.
- Fix tickets (`F1`, `F2`, … in Phase 6) never get a profile of their own: `ap.py ticket F1 route --provider anthropic --reason "…" --capabilities .autopilot/model-capabilities.json` assigns the run's repair executor (`state.js` → `repairAgent`, registered in Phase 4) — or, when the user approved the `repair` role (signature valid, `opusAgents.repair` present), the Opus repair profile instead; `ap.py agent-for repair` prints the name to call, and the launch prompt names the fix ticket file. One fix ticket at a time: the guard admits the repair executor only for the one fix ticket `in-progress` or `repair`, and its `done` counts only attestation lines written after its `start`.
- An agent missing from this session (a plan from before the repair executor, a deleted file): on «Agent type not found», never fall back — `ap.py ticket NN reset`, `ap.py ask stop` and the new-chat message from `phases/4-plan.md`.
- In strict runs `ticket NN done` needs the subagent's attestation (`resolvedModel`).
- In the desktop app Agent calls run asynchronously; this does not block the gate.
- Never start or suggest `/subtask` or `/fork` during strict tickets: they bypass the guard and write no attestation.
- Never pass `isolation` to Agent calls: ticket worktrees belong to Autopilot (`ap.py` / `worktrees.py`); the guard denies Claude's own worktree isolation.

## Ordinary run (no `--strict-routing`) — four light profiles

`ap.py init` writes four **permanent** profiles to `.claude/agents/` if they are missing or their text differs: no run name, no ticket number, no task path inside, and **no `model` or `effort`** — the call sets those. They start at about a tenth of the context of `general-purpose` (their tool list is short). The profiles of earlier runs and any other file there are left alone.

| Role | Agent type | Tools |
|---|---|---|
| executor — a ticket, a fix ticket `F<n>`, the memory agent and the ADR agent (they write files) | `autopilot-executor` | Read, Grep, Glob, Bash, Edit, Write |
| point review, whole-branch review, the G2 coverage check | `autopilot-reviewer` | Read, Grep, Glob, Bash |
| blind acceptance (G4) | `autopilot-acceptance` | Read, Grep, Glob, Bash |
| the exploring subagent (notes, context pack, commit log) | `autopilot-explorer` | Read, Grep, Glob |

- **Always pass `model` and `effort` in the call.** The profile has none, so without them the subagent inherits the main session's model. They come from `plan-models` or the router, as before. For a fix ticket `ap.py ticket F1 route --model <name> --effort <level> --reason "…"` records that choice in `state.js` (no profile is created; Haiku and Sonnet only, Opus only after the user's approval, never Fable).
- **The task names the request.** The launch prompt carries the ticket file path and the limits; the profile text does not.
- **«Agent type not found»** — Claude Code sees profiles written during this session only from the next chat. It is never a stop and never a question: call `general-purpose` for that role instead, tell the user in one line («лёгкие профили видны со следующего чата — дальше будет дешевле»), and go on.
- **A `?` line from `init`** is one question, asked once: may the same four profiles also live in the Claude Code settings folder, so they are there on the first build in any project? A yes → `ap.py agents install-user --by-user "<его слова>"`; a no → `ap.py agents install-user --decline`. Either answer is kept and `init` stops asking. Without the user's words nothing is written outside the project.

The strict rules above are unchanged; a strict run keeps its own profiles per ticket and writes no permanent ones.
