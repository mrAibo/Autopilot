# Phase 5 — Claude Code host specifics

Install the optional project-level blocking hook once before strict dispatch: `python .autopilot/claude_agent_guard.py --install-hook --root .` (inspect `.claude/settings.json`; the guard is active only while an unfinished strict run exists). `SubagentStart` hooks are too late to block a launch, so this uses `PreToolUse` on `Agent|Task`.

Rules for the orchestrator (see `docs/autopilot/claude-code.md`, `docs/autopilot/claude-fork-policy.md`):

- Install both hooks once per project: `python .autopilot/claude_agent_guard.py --install-hook --root .` and `python .autopilot/claude_attest.py --install-hook --root .`.
- Call only routed `autopilot-…` agents; the guard denies any other Agent name. `--install-hook` also denies `Agent(fork)`.
- In strict runs `ticket NN done` needs the subagent's attestation (`resolvedModel`).
- In the desktop app Agent calls run asynchronously; this does not block the gate.
- Never start or suggest `/subtask` or `/fork` during strict tickets: they bypass the guard and write no attestation.
