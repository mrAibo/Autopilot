# Claude Code forks in strict runs (F1 design note)

**Status:** proposal, awaiting owner decision. No code until approved.

## Problem

The T08 live probe (`claude-code.md` § Live probe) showed that `/subtask` in the Claude desktop app starts a fork that never passes through the `Agent`/`Task` tool. The strict `PreToolUse` guard does not fire and no attestation is written. A strict run therefore cannot see or block `/subtask`.

## What the docs say (code.claude.com, checked 2026-10-29)

- A fork inherits the main session's full history, system prompt, tools and **main model**; per-invocation `effort` does not apply. A fork can never satisfy a pinned `haiku/low` route.
- Claude can start a fork on its own (fork mode, default on since v2.1.302) **through the Agent tool**. `"Agent(fork)"` in `permissions.deny` stops that; `CLAUDE_CODE_FORK_SUBAGENT=0` turns fork mode off.
- A human can start a fork with `/subtask` "whether or not fork mode is on". With agent view off, `/fork` does the same.
- `UserPromptSubmit` and `UserPromptExpansion` hooks can block a typed prompt (`decision: "block"` or exit 2). The docs do not say whether either fires for built-in commands such as `/subtask`.

## Threat model

Strict routing protects against **the orchestrating Claude** delegating work to an unapproved model or effort. It does not protect against the owner, who can always edit code by hand.

| Path | Who starts it | Covered today? |
|---|---|---|
| Agent call with `subagent_type: autopilot-…` | Claude | yes: guard + attestation + T07 gate |
| Agent call that forks (no or non-Autopilot `subagent_type`) | Claude | yes: the guard denies any name outside the `autopilot-…` regex |
| `/subtask`, `/fork` typed in chat | owner | **no** |

So the gap is an **owner action**, not an orchestrator escape. Its real risk: the owner forks while a ticket is open, the fork edits the ticket's zone on the main model, and the routed agent's attestation still exists, so `ticket done` passes for work the routed model did not do.

## Options

1. **Document only.** Add to `claude-code.md`: "strict runs do not cover `/subtask` or `/fork`; do not fork while tickets are in progress." Cost: docs only. Leaves the false-done risk above.
2. **Belt and braces for Claude-started forks.** Add `"Agent(fork)"` to `permissions.deny` when the guard hook is installed. The guard already denies these, but a settings-level deny is another, independent layer. Cost: a few lines in `claude_agent_guard.install_hook` + 1 test.
3. **Block typed forks.** Add a `UserPromptSubmit` hook (installed with the guard) that, during an active strict run, blocks prompts whose first token is `/subtask` or `/fork`, with the reason "strict Autopilot run: forks bypass routing". Cost: a small handler + tests. **Requires a live check first**: if built-in commands never reach `UserPromptSubmit`, this option does nothing, and must not be described as protection.
4. **Detect after the fact.** At `ticket done` in strict Claude runs, compare the commit's changed files with the ticket zone and require that the routed agent's attestation lines are newer than the ticket's `start`. Catches stale evidence, but cannot prove who wrote the code. Cost: medium.

## Recommendation

**1 + 2 now, 3 after one live check, skip 4.**

- 1 is honest and immediate.
- 2 is cheap, independent of the guard, and fail-closed.
- 3 is the only real block for the owner path, but it is worth building only if the live check shows `UserPromptSubmit` fires for `/subtask`. Probe: in `autopilot-t08-probe`, install a `UserPromptSubmit` hook that logs the payload, type `/subtask say hello`, check for a line.
- 4 adds complexity for a weak guarantee: attestation proves the routed agent ran, not who typed each line.

## Owner decision

- [ ] 1 Document only
- [ ] 2 `Agent(fork)` deny on guard install
- [ ] 3 `UserPromptSubmit` block for `/subtask` / `/fork` (after live check)
- [ ] 4 Post-hoc zone/attestation-age check
