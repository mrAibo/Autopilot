# Adaptive model routing (Autopilot 2.3+; model-only capability path)

Autopilot routes *executor tasks*, not its user's main model. The orchestrator may run on a powerful model while a document-writing subagent uses a cheaper model with low effort. No executor should silently inherit the orchestrator's model.

Implementation: `skills/autopilot/tools/model_router.py`. The library is Python-standard-library-only; it does **not** create agents and does not by itself guarantee that the host obeys the choice.

## Model-only routing when a harness cannot set effort (2026-10-27)

The policy **still recommends** an effort for every ticket, but an actual host may explicitly advertise `"effort_selection": false`. In that **opt-in, model-only** case, `effortEnforced=false` is written to the route and the generated Claude/Codex native agent profile contains **only the exact model** (no `effort` / `model_reasoning_effort` setting). A displayed Low/Medium/High value is **advisory only**, and the actual runtime effort is **unverified**; never claim token savings or enforcement.

Example of the **format, not verified capability evidence**:

```json
{
  "provider": "anthropic",
  "model_selection": true,
  "effort_selection": false,
  "models": {"haiku": [], "sonnet": []}
}
```

Use `"provider": "openai"` and genuinely supported exact model IDs for Codex. The empty lists express **no enforceable effort claims**; they are **not** proof of model availability. A real host must separately confirm it can enforce each exact named agent/model pair. Do not invent this file merely to make a run pass. Missing `effort_selection` retains the old strict pair-checking behavior. `model_selection: false`, a missing model, malformed capability metadata, inherited/premium models, stale profile hashes, forbidden generic agents and V2 Codex custom-agent unavailability **still block**. `--sequential-host` continues to be the safe Codex GUI fallback and makes no native child claims.

Existing active routes must not be silently downgraded to model-only. Only a new reviewed planning/apply step with real host capabilities can create such routes; previously pinned effort remains enforced in older profiles.

## Automatic per-ticket selection at the planning stage (Phase 4)

**Yes: every ticket has its own independently calculated model and reasoning Effort before development begins.** The full process is:

1. Phase 4 creates `tickets/01-*.md`, `02-*.md`, etc. and validates their requirements/zones/dependencies with `ap.py tickets` and `ap.py check-plan`.
2. `ap.py plan-models --provider openai` **automatically** scores *all* published tickets in one run, selects a tier and exact model/Effort, and stores `plannedRouting` for each. Without a trusted catalog, the result is **`blocked`/advisory** with the diagnostic `No verified host capabilities`. This is a useful readable proposal, **not** verified provider availability.
3. After obtaining actual *host*-supported capability data and confirming **model selection** (and effort only if supported), one `ap.py plan-models --provider openai --capabilities .autopilot/model-capabilities.json --apply` **atomically validates the full plan** and creates all approved native project profiles. **`--apply` requires a successful, still-current G3 `ap.py check-plan`:** the exact ticket and requirement contract **and** the manifest statuses at validation must still match. If G3 is missing/failed, a ticket or requirement changes, statuses change, a model/Effort pair is unavailable, or a profile conflicts, the batch is refused *before* any profile is created. Run `tickets`, `check-plan`, and recalculate/reapply the plan after reviewing the changes; never silently downgrade or skip G3.
4. Phase 5 calls exact already assigned `agentType`, only after checking the profile integrity and live host functionality. **A profile on disk does not prove GUI dispatch or the effective model.** If actual host selection cannot be established, no subagent is spawned. An explicitly chosen `--sequential-host` run does not create named child agents and rejects `plan-models`.

Example of an automatic table (illustrative **policy**, not measured runtime):

| Ticket | Heuristic complexity | OpenAI policy choice | Anthropic policy choice |
|---|---|---|---|
| Small documentation or wording | cheap | Luna / low | Haiku / low |
| Several connected modules / unclear interfaces | balanced | Luna / high | Sonnet / medium |
| Authentication, passwords or sensitive migrations | strong (risk override) | Sol / high | Sonnet / high |

**Automatic** means a deterministic policy selects values without manually typing `--model` and `--effort` for each ticket. It does **not** mean the system invents host entitlements, silently uses a paid API, or proves the runtime honored a profile. Premium/restricted models are not selected automatically. Individual `ticket NN route` remains for reviewed exceptions/custom policies; the batch command is the normal Phase 4 path.

### Reading Dashboard routing status

- **BLOCKED / ЗАБЛОКИРОВАНО:** a ticket has only a proposed model/Effort and no applicable pinned profile. The panel displays the reason (for example, `No verified host capabilities`) and warns **not** to spawn a subagent. Check actual host enforcement, attest the exact capability catalog, then deliberately run `plan-models --capabilities ... --apply`; never fabricate a catalog from this documentation.
- **NOT APPLIED / НЕ ПРИМЕНЕНО:** a proposal may be compatible with a supplied catalog but is still not a pinned route. Review the complete batch and apply explicitly.
- **Profiles pinned / Профили закреплены:** matching native profile files have been written and their hashes recorded. This is **not** independent evidence of a created GUI child, effective model, reasoning Effort or billing; live runtime qualification remains a separate release gate.

The Dashboard distinguishes these states in RU/EN. `--sequential-host` deliberately has no per-ticket native subagent routing and independently warns that its GUI model/Effort cannot be attested by the controller.

**Resume and replan invariant:** `ap.py tickets` and `ap.py check-plan` reconstruct ticket metadata. They retain `plannedRouting` and applied `routing` for tickets with unchanged SHA-256 content, so normal refresh, resume or G3 validation does not erase Phase-4 choices. If a ticket's bytes change, its cached plan and route are discarded; publish/check the updated plan and run `plan-models` again before native dispatch. Existing generated agent files are never silently overwritten or deleted during ticket refresh; inspect any conflicting old profile manually. These retention rules are verified using temporary Git projects, not actual agent execution.

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

## Custom policy for the normal ticket route

The default provider and tier policy remains fully usable without a policy
file. To change one profile without losing the other tiers or provider,
create a JSON file inside the application project, for example
`.autopilot/model-policy.json`:

```json
{
  "version": 1,
  "max_parallel": 2,
  "providers": {
    "anthropic": {
      "cheap": {"effort": "medium"}
    }
  },
  "restricted": {
    "anthropic": ["company-private-premium-model"]
  }
}
```

`load_policy` deep-merges only the declared model/effort overrides with a
fresh copy of defaults. It **adds** restricted names to the built-in deny
lists, never replaces the defaults. Invalid fields, unsupported versions,
unknown providers/tiers, wrong types and padded model names are rejected,
not silently ignored. This JSON is a **local routing proposal**, not
host attestation and not a license to spawn costly agents. The host still
must advertise and enforce the exact selected model/Effort.

For an active ticket, route using that same policy file:

```bash
python3 .autopilot/ap.py ticket 01 route --provider anthropic \
  --model haiku --effort medium --reason "small task, approved profile" \
  --capabilities .autopilot/model-capabilities.json \
  --policy .autopilot/model-policy.json
```

The `ticket route` command passes the **same file** to both the model
selector and the generated agent profile. It records the policy's SHA256;
later changes to the policy invalidate strict ticket `start`, `retry`
and `done` until a fresh route/profile is established. The policy must
resolve inside the project; external file paths are rejected. Existing
tickets without a policy continue to use the unchanged defaults.

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

For Codex use `--provider openai`; it writes `.codex/agents/<name>.toml` with `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`. Claude writes `.claude/agents/<name>.md` with `model` and `effort` frontmatter. Agents are named `autopilot-executor-...` and must be launched by that **exact name**. Existing files are left untouched unless identical (idempotent). Claude Code sees only agents that existed when its session started, so a strict Claude run creates every profile at the end of Phase 4 and continues in a new session (`claude-code.md`). Once a ticket has `routing`, that record is authoritative: `ticket NN route` drops the ticket's earlier advisory `plannedRouting`. Project/managed configuration and environment variables may override lower-priority settings; confirm host behavior.

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

## Explicit no-child sequential fallback

When the GUI cannot prove named-subagent model/Effort selection, do **not** claim a generated `.codex/agents` or `.claude/agents` file proves a real child. For a **new** owner-approved run, `ap.py init ... --sequential-host` selects a one-ticket, detached-worktree host mode with mandatory independent baseline-tracked Python unittest evidence, and prohibits `ticket NN route`. It does not spawn AI models, certify effective model/Effort or promise token billing. See [sequential-host.md](sequential-host.md). This is a **host acceptance fallback**, not a substitute for runtime model enforcement, and not proof that R03 native dispatch is released.

## Retry

1. Diagnose first. Missing files, dependencies, permissions, tool limitations and unclear instructions do not justify an automatic model upgrade.
2. A genuine reasoning failure may increase effort or move to the next allowed profile, with a new checked route.
3. Never auto-upgrade to a restricted model; ask for explicit consent and adjust the policy deliberately.
4. Stop after the configured repair/retry cap. Count all attempts when assessing cost and quality.

## Parallelism and safety

Default concurrency is two, with a hard policy maximum of three; never launch agents writing overlapping paths in the same checkout. For substantial parallel builds prefer independent Git worktrees; this is a planned improvement, not yet enforced by the present router.

## Main session model

Routing covers subagents only; the model of your main session is your choice and usually the biggest cost, because it lives through the whole run and re-reads its growing context at every step. For ordinary work run `/autopilot` on Sonnet. Opus is worth it only for a complex or fuzzy idea: (1) start `/autopilot` on Opus through briefing, spec and plan (`check-plan` green, plan approved); (2) open a new chat in the same folder with Sonnet selected (desktop: model picker; CLI: `claude --model sonnet` or `/model sonnet` before typing); (3) type `/autopilot` — the run resumes at Phase 5 from `.autopilot/` (`phases/0-resume.md`) and the fresh chat starts with a small context. Leave the old chat idle. Phase 4 offers this at the end of the plan. In one small measured run (T13, 3 tickets, Claude desktop app) the main session on Opus was about 1.40 USD and all three subagents together about 0.054 USD (~96 % of the estimate); a terminal run (T15, 2 tickets, Opus) came to about 1.20 USD. These are `cost.usage` estimates, not subscription charges, from small runs; larger projects shift the share toward subagents.

## Development status and limits

The routing selector, native profile generator, integrity check and dashboard event recording are implemented. Harness-capability discovery and assurance that the orchestrator invokes only approved agent types are still **not** enforced by the Python code; the runtime can independently override profile settings (Claude Code also supports the `CLAUDE_CODE_EFFORT_LEVEL` override). Worktree isolation, automatic model cost telemetry, and empirical benchmark calibration remain future work. Treat unverified configuration as blocked, not as a successful test.
