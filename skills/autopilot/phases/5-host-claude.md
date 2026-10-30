# Phase 5 — Claude Code host specifics

The project-level blocking hook: `python .autopilot/claude_agent_guard.py --install-hook --root .` (inspect `.claude/settings.json`; the guard is active only while an unfinished strict run exists). `SubagentStart` hooks are too late to block a launch, so this uses `PreToolUse` on `Agent|Task`.

Rules for the orchestrator (see `docs/autopilot/claude-code.md`, `docs/autopilot/claude-fork-policy.md`):

- Phase 4 installs both hooks (`python .autopilot/claude_agent_guard.py --install-hook --root .` and `python .autopilot/claude_attest.py --install-hook --root .`) and every profile **before** this session started (`phases/4-plan.md`); rerunning them is idempotent. Claude Code sees only agents that existed at session start.
- Call only routed `autopilot-…` agents; the guard denies any other Agent name. `--install-hook` also denies `Agent(fork)`.
- Roles, from `state.js` → `roleAgents`: point review, repair re-review and whole-branch review → `roleAgents.reviewer.agentType`; blind acceptance → `roleAgents.acceptance.agentType`; the coverage reader and the memory and ADR agents → `roleAgents.explorer.agentType` (read-only: they return the text, and you write the memory file and `docs/adr/` verbatim). Never an executor profile for another role.
- A profile created during the build (F1 in Phase 6) may be invisible to this session: on «Agent type not found», never fall back — `ap.py ticket NN reset`, `ap.py ask stop` and the new-chat message from `phases/4-plan.md`.
- In strict runs `ticket NN done` needs the subagent's attestation (`resolvedModel`).
- In the desktop app Agent calls run asynchronously; this does not block the gate.
- Never start or suggest `/subtask` or `/fork` during strict tickets: they bypass the guard and write no attestation.
- Never pass `isolation` to Agent calls: ticket worktrees belong to Autopilot (`ap.py` / `worktrees.py`); the guard denies Claude's own worktree isolation.
