# Adaptive model routing (Autopilot 2.3 development)

Autopilot routes *executor tasks*, not its user's main model. The orchestrator may run on a powerful model while a document-writing subagent uses a cheaper model with low effort. No executor should silently inherit the orchestrator's model.

Implementation: `skills/autopilot/tools/model_router.py`. The library is Python-standard-library-only; it does **not** create agents and does not by itself guarantee that the host obeys the choice.

## Provider mapping

| Level | OpenAI / Codex | Anthropic / Claude Code |
|---|---|---|
| cheap | `gpt-6-luna`, low | `haiku`, low |
| balanced | `gpt-6-luna`, high | `sonnet`, medium |
| strong | `gpt-6.1-sol`, high | `sonnet`, high |
| restricted / not automatically dispatched | `gpt-6-astra` | `fable`, `claude-fable-5` |

These are defaults, **not a guarantee of host availability**. API model IDs and CLI aliases may differ; actual host capability discovery must resolve them. The default policy does not escalate to Opus, Astra or Fable. A model's accepted reasoning effort may differ across versions.

Models/prices/availability can change. The host must advertise supported model/effort pairs before dispatch; never infer access from the current orchestrator model.

## Scoring (0–100)

- algorithm: up to 25
- coupling across modules: up to 20
- uncertainty: up to 15
- context size: up to 15
- test complexity: up to 15
- security/irreversible risk: up to 10

Scores of 0–25 use `cheap`, 26–55 `balanced`, 56–100 `strong`. High risk is an override (risk 10 forces strong); algorithm score >=20 forces strong. A risk-bearing task may also require independent review. Simple heuristics based on ticket contents are a starting estimate; supply verified factors explicitly if the default estimate is inadequate.

## Capabilities handshake — mandatory

Create the *runtime* capability advertisement from what Codex or Claude Code **actually supports**; do not blindly reuse this example in a real run:

```json
{
  "provider": "anthropic",
  "model_selection": true,
  "models": {
    "haiku": ["low", "medium"],
    "sonnet": ["medium", "high"]
  }
}
```

Usage:

```bash
python3 .autopilot/model_router.py .autopilot/<run>/tickets/02-example.md \
  --provider anthropic \
  --capabilities .autopilot/model-capabilities.json
```

OpenAI example: `--provider openai` and capability entries for `gpt-6-luna` and `gpt-6.1-sol`.

Exit 0 + `"status": "ready"` means *eligible for host dispatch*. Exit 2 + `"status": "blocked"` means **do not spawn**. Omitting capabilities always blocks. The host must dispatch the newly generated `agentType` (not `default`, `worker`, or `Explore`) and must refuse any model/effort override. Codex custom agents pin `model` and `model_reasoning_effort`; Claude custom subagents pin `model` and `effort`. These files may require a session reload to be discovered, and the host still must support these fields. The skill is a policy and **cannot compel an external agent tool to use a given model**.

The agent records an approved decision for the dashboard:

```bash
python3 .autopilot/ap.py ticket 02 route --provider anthropic \
  --model haiku --effort low \
  --reason "limited documentation edit; low risk" \
  --capabilities .autopilot/model-capabilities.json
```

The `route` event recomputes the model recommendation and checks the capabilities file, then creates a **native project agent** at `.claude/agents/autopilot-executor-<ticket>.md` or `.codex/agents/autopilot-executor-<ticket>.toml`, records its name/path/SHA256 in state, and sets `verified=true`. On strict starts, the SHA256 must still match. Start new runs with `ap.py init ... --strict-routing` to enforce presence of that checked assignment at `ticket ... start`. This does **not** cryptographically authenticate the capabilities file or prove that an external harness billed the selected model. The recorded assignment is a plan, not proof that tokens were billed to that model. The dashboard shows cost as unavailable until real usage telemetry is connected.

## Native Codex and Claude Code agent profiles

`agent_profiles.py` creates project-scoped agent definitions with explicit model and reasoning effort (without launching agents):

```bash
python3 .autopilot/agent_profiles.py --root . \
  --ticket ".autopilot/<run>/tickets/01-example.md" \
  --provider anthropic --capabilities .autopilot/model-capabilities.json \
  --role executor --install
```

For Codex use `--provider openai`; it writes `.codex/agents/<name>.toml` with `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`. Claude writes `.claude/agents/<name>.md` with `model` and `effort` frontmatter. Agents are named `autopilot-executor-...` and must be launched by that **exact name**. Existing files are left untouched unless identical (idempotent). The active host may need restarting to discover new agents. Project/managed configuration and environment variables may override lower-priority settings; confirm host behavior.

When `ap.py ticket NN route ...` runs, it generates the executor profile, saves `agentType`, `agentFile` and a SHA256 hash; strict `start` checks this hash. This validates the project file, **not** the actual model chosen by an external process.

### Claude Code optional PreToolUse gate

```bash
python .autopilot/claude_agent_guard.py --install-hook --root .
```

This opt-in command merges a project hook into `.claude/settings.json`, preserving unrelated settings. During an unfinished `strictRouting` run it denies generic `Agent`/`Task` calls, premium/inherited profiles, explicit model/effort overrides, missing capability entries, and executor profiles whose hash no longer matches the approved route. The `SubagentStart` event **cannot** prevent spawning; `PreToolUse` can deny a tool invocation. Hooks can be disabled or bypassed by the host, so this is not a sandbox/security guarantee. Only enable this project-wide guard when you intend to route every subagent through Autopilot definitions; it will intentionally reject generic Explore calls during a strict run.

For Codex, named custom roles are the supported native mechanism. `[agents].default_subagent_model` and `default_subagent_reasoning_effort` may set cheap defaults as defense in depth, but explicit model selection can override them. There is no equivalent Codex hook installed here: do not claim hard prevention of arbitrary external spawns.

## Non-executor subagents

Routing applies equally to code reviewers, independent spec-coverage reviewers, repository exploration, blind acceptance, ADR writers and memory agents. Create a lightweight **role-specific routing brief outside `tickets/`**, select its complexity factors (using `--scores` if the heuristic undershoots security review), then run the same provider/capability check before calling the host's Agent tool. Do not inherit the main session's model or silently bypass a blocked route.

`ap.py ticket ... route` records **executor** assignments; it does not create reviewer/ADR telemetry. The latter remains a future extension, and no fabricated spend should appear in the dashboard.

## Retry

1. Diagnose first. Missing files, dependencies, permissions, tool limitations and unclear instructions do not justify an automatic model upgrade.
2. A genuine reasoning failure may increase effort or move to the next allowed profile, with a new checked route.
3. Never auto-upgrade to a restricted model; ask for explicit consent and adjust the policy deliberately.
4. Stop after the configured repair/retry cap. Count all attempts when assessing cost and quality.

## Parallelism and safety

Default concurrency is two, with a hard policy maximum of three; never launch agents writing overlapping paths in the same checkout. For substantial parallel builds prefer independent Git worktrees; this is a planned improvement, not yet enforced by the present router.

## Development status and limits

The routing selector, native profile generator, integrity check and dashboard event recording are implemented. Harness-capability discovery and assurance that the orchestrator invokes only approved agent types are still **not** enforced by the Python code; the runtime can independently override profile settings (Claude Code also supports the `CLAUDE_CODE_EFFORT_LEVEL` override). Worktree isolation, automatic model cost telemetry, and empirical benchmark calibration remain future work. Treat unverified configuration as blocked, not as a successful test.
