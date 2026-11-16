# Phase 4 — Plan: strict Claude Code run and unsupported hosts

Read from `4-plan.md`, only in a run with `strictRouting` on Claude Code, or when the host cannot honour `--apply`. Nothing here applies to an ordinary run.

- The applied route is an authorized **configuration**, not evidence of an actual child/model/Effort; Phase 5 still checks profile hashes, runtime dispatch capabilities and the exact selected agent. On an unsupported GUI, **do not use `--apply` as a workaround**; use [`--sequential-host`](../../../docs/autopilot/sequential-host.md) and do not claim named subagents.

## Strict Claude Code run — register the agents, then a new chat

Claude Code reads `.claude/agents/` and the project hooks at session start; a profile created later in the same session answers «Agent type not found», and strict routing allows no fallback (T16). So a run with `strictRouting` on Claude Code (provider `anthropic`) ends Phase 4 here, once the plan stands (manual: after the «ок»; semi: instead of «и начинаю»):

1. Write `.autopilot/model-capabilities.json` from what this host really offers (`docs/autopilot/claude-code.md`), then **one** call creates every profile the run will use — an executor per ticket plus the run's reviewer, blind-acceptance and read-only explorer (`state.js` → `roleAgents`) and one repair executor for the fix tickets the whole-branch review may create (`state.js` → `repairAgent`): `python3 .autopilot/ap.py plan-models --provider anthropic --capabilities .autopilot/model-capabilities.json --apply`. It also marks the `plan` stage done. A blocked route is a stop, not a reason to skip a role.
2. Both hooks: `python3 .autopilot/claude_agent_guard.py --install-hook --root .` and `python3 .autopilot/claude_attest.py --install-hook --root .`.
3. No new commit — `.claude/` and the role brief stay out of the plan commit. `ap.py ask stop --note "новый чат: агенты зарегистрированы"`, then, in the user's language, as a **required** step that replaces the cost hint below:

   «Агенты сборки зарегистрированы, но Claude Code видит их только в новой сессии. Открой новый чат в этой папке (дешевле на Sonnet) и напиши `/autopilot` — сборка продолжится с этого места. Здесь сборка не пойдёт.» / "The build agents are registered, but Claude Code only sees them in a new session. Open a new chat in this folder (Sonnet is cheaper) and type `/autopilot` — the build resumes from here. It cannot run in this chat."

In every mode, full included, this is a stop: without the new session the build cannot dispatch a single agent — say so plainly, never carry on with `general-purpose`, a built-in agent, another ticket's profile or `--sequential-host`.
