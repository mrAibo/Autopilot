# Audit mode — a read-only findings report

`/autopilot audit` inspects an existing project and writes one verified report. It changes nothing: no edits, no commits, no installs, no network. Rules for the agent: [`skills/autopilot/phases/audit.md`](../../skills/autopilot/phases/audit.md); subagent prompts: [`skills/autopilot/prompts/audit.md`](../../skills/autopilot/prompts/audit.md).

## Start it

```text
/autopilot audit
/autopilot audit: security and performance
/autopilot аудит: безопасность
/autopilot Audit: Tests und Abhängigkeiten
```

The text after the colon is the focus. Without one the whole project is audited; with one, only the matching lenses run (correctness always) and the rest is listed as "not checked". Run the main session on Sonnet — it is the main cost, and an audit does not need more.

If an unfinished Autopilot run exists in the folder, the audit refuses: finish or resume the run first (`/autopilot`). A finished run is fine.

## What happens

1. **Recon** — the agent reads the stack, size, tests, history and `AGENTS.md`/`CLAUDE.md`. It runs the project's existing test suite once only when the command is documented, dependencies are already installed, and it needs no network, database, container or credentials; otherwise the report says it was not run.
2. **Explorers** — 3 to 7 parallel subagents on the cheap tier (Claude Code: Haiku; Codex: the cheap route), each with one lens: correctness and edge cases, security, performance under real load, untested risky code, dead or duplicate code, docs drift, dependencies. Read-only tools only; each returns at most 12 compact findings.
3. **Verification** — one reviewer on the strong tier (Claude Code: Sonnet) opens every cited line, drops what the code does not confirm, and keeps a finding only with a concrete failure scenario.
4. **Report** — `.autopilot/audits/<YYYY-MM-DD>-audit.md`, the only file written. It is not committed.

No `ap.py`, no dashboard, no agent profiles, no hooks: an audit is not a run, so the strict Claude Code guard does not apply to it.

## The report

- **Summary** — the state of the project in a few plain lines.
- **Critical / Important / Improvements** — each finding has an id (`A01`…), a checkbox, `file:line`, why it matters, a failure scenario and a rough effort (S under an hour, M a day, L more).
- **Development ideas** — `I01`…, also with checkboxes.
- **Not checked** — lenses, zones or commands left out, with the reason (for example `npm audit`, which needs the network).

## From audit to fixes

Tick the items to fix (`- [ ]` → `- [x]`), then:

```text
/autopilot .autopilot/audits/2026-10-30-audit.md
```

That starts a normal build on existing code. Its brief is **only the ticked items**, verbatim with their ids; unticked findings and ideas are explicitly out of scope. If nothing is ticked, Autopilot asks which findings to fix. In Claude Code the usual two passes apply: plan on a strong model, then build in a fresh Sonnet chat in the same folder with `/autopilot`.

## Limits

- Findings are model judgement verified by a second model, not proof. Security findings name a reproduction; check critical ones yourself before acting on them.
- Offline only: vulnerable-version claims need `npm audit`, `pip-audit` or similar, which the report lists for you to run.
- If the host cannot route a subagent to the cheap model, the agent says so and works the lenses itself at the small-project scale.

**Windows / Git Bash, headless:** Git Bash rewrites a leading `/` in arguments into a Windows path, so `claude -p "/autopilot audit"` arrives as `C:/Program Files/Git/autopilot audit` and the skill is never invoked. Prefix the command with `MSYS_NO_PATHCONV=1` (e.g. `MSYS_NO_PATHCONV=1 claude -p "/autopilot audit" --model sonnet …`) or run it from PowerShell/cmd. Typing `/autopilot` inside an interactive chat is not affected.
