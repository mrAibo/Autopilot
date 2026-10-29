# Claude Code support in Autopilot 2.3.0

**Qualification level:** agent profiles and PreToolUse guard are tested offline with Python/subprocess fixtures. No Claude Code CLI is currently installed on the tested Windows Aibo host, so **native Claude Code subagent execution, actual model, effort, cwd and subscription billing have not been verified**. The Codex limited 2.3.0 release does **not** claim these results.

## Why Claude Code is a good target

Claude Code project agents live in `.claude/agents/<name>.md`. Relevant frontmatter:
- `model`: `sonnet`, `opus`, `haiku`, `fable`, a full model ID, or `inherit`.
- `effort`: `low`, `medium`, `high`, `xhigh`, `max` (available levels depend on the model).
- Effort precedence: `CLAUDE_CODE_EFFORT_LEVEL` > per-invocation `effort` (v2.1.292+) > frontmatter > session.
- Model precedence: per-invocation `model` > frontmatter > `CLAUDE_CODE_SUBAGENT_MODEL` > main model. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` ignores frontmatter; an `availableModels` allowlist can substitute a model.
- `/tasks` shows model and effort per running subagent (v2.1.242+).

Autopilot already writes those profiles from one Phase-4 `plan-models --provider anthropic` pass, choosing models by ticket complexity and risk. Tiers: cheap haiku/low · balanced sonnet/medium · strong sonnet/high · critical sonnet/xhigh (risk >= 10 and algorithm >= 20). Opus and Fable are not used as subagents by default.

Tool rules per role (field names are case-sensitive; Claude Code silently ignores misspelled fields):
- executor: `tools: Read, Grep, Glob, Bash, Edit, Write`.
- reviewer and acceptance: `tools: Read, Grep, Glob, Bash` plus `disallowedTools: Edit, Write, Agent`, so they can run tests or install and run the project without edit rights. Acceptance also sets `omitClaudeMd: true` (blind acceptance, no project memory).
- explorer: read-only (`Read, Grep, Glob`).

Claude Code documentation: [Custom subagents](https://code.claude.com/docs/en/sub-agents), [Model configuration](https://code.claude.com/docs/en/model-config).

## Installation and subscription prerequisites (owner-operated)

1. Claude Code is **not** the general Claude Desktop chat application. Install Claude Code from the [official setup instructions](https://code.claude.com/docs/en/setup), e.g. `winget install Anthropic.ClaudeCode` on Windows, only if authorized. Verify `claude --version`.
2. Sign in via `claude` using the separate **Claude Pro or Max (or organization) subscription**. A ChatGPT/Codex Plus subscription **does not include Claude Code inference**. Avoid Claude Console API-key login. If `ANTHROPIC_API_KEY` is set, Claude Code can use it **instead of** the subscription and incur API charges. Decline extra **usage credits** when your plan limit is reached. Consult [Anthropic's subscription billing instructions](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan).
3. Confirm the Autopilot skill is reachable from `~/.claude/skills/autopilot/SKILL.md`. On Aibo the existing Junction points to the source checkout; do not reinstall the skill or overwrite global Claude settings.
4. Before starting any *new* run, confirm from the **actual Claude Code host** that the chosen models and effort levels are available and the agent can run under the subscription. Do not invent a `model-capabilities.json` just to enable `--apply`.

## New strict Claude Code run (after live host qualification)

In the project, prepare Autopilot through the normal phases. After `tickets` and **successful `check-plan`**:

```powershell
py -3 .autopilot/ap.py plan-models --provider anthropic
# Read-only recommendation; status may be blocked until actual host capability discovery.
```

If live host **model and named-agent** support is independently established and represented in a verified project-local capability catalog (effort support is optional, with `effort_selection:false` when not enforceable), the owner may approve:

```powershell
py -3 .autopilot/ap.py plan-models --provider anthropic --capabilities .autopilot/model-capabilities.json --apply
py -3 .autopilot/claude_agent_guard.py --install-hook --root .
```

The generated project-local `.claude/agents/*.md` always pin `model` and restricted `tools`; they pin `effort` **only when the host advertises enforceable effort selection**. With a verified model-only catalog (`effort_selection:false`), the effort recommendation stays advisory and no profile effort field is written. The optional `PreToolUse` guard refuses unapproved agent types, modified profile hashes, **model** overrides and globally forced `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`. It additionally refuses conflicting per-call/environment **effort** only for routes that declare `effortEnforced:true`. Model-only mode never claims effort enforcement.

**Important runtime limitations:** in newer Claude Code versions, an Agent invocation can override frontmatter `model` / `effort`; `CLAUDE_CODE_EFFORT_LEVEL` overrides even both; a forced model override can ignore pinned profiles; organization allowlists may substitute another model. The guard is an additional protection, **not** evidence of the effective spawned model. The owner must check `/tasks` while an agent is running (where available), the agent identity, cwd and actual tool activity before calling the path qualified.

Claude Code's own `isolation: worktree` starts from the default branch by default; it is **not automatically the same worktree** as an Autopilot prepared ticket. Do not silently combine the two. Keep the ticket restricted to its explicitly approved Autopilot worktree.

**No paid API tests authorized:** If real subscription-only execution cannot be established, stop at advisory planning; use `--sequential-host` for the Codex limited release or test the Claude side manually after appropriate account authorization. Never bypass `spend_guard`.

## Current status

| Component | Evidence |
|---|---|
| Ticket model/effort selection | Offline algorithm + synthetic catalog tests |
| Claude custom agents / YAML frontmatter | Generated and tested offline; documented officially |
| PreToolUse strict guard | Offline and real Python subprocess tests |
| Effective Claude Code subagent model / effort | **Not yet observed on Aibo** |
| Subscription charge boundary | **Not yet observed on Aibo** |

Do not call this a completed native Claude Code E2E until those last two rows have independently passing evidence.
