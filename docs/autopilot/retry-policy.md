# Repair and retry triage (Autopilot 2.3)

The deterministic policy in \`skills/autopilot/tools/retry_policy.py\` distinguishes:
environment, dependency, requirements, tests, reasoning, security, unknown.

**Never upgrade a model merely because a command failed.** Missing network, disk,
packages and permissions mean fix the environment. An ambiguous spec means clarify
or replan; security incidents need human review. Failed assertions normally warrant
repair in the same executor and a repeat of the full test suite. Architectural or
algorithmic failures require re-evaluation and, only when justified, a fresh
host-verified model route.

No agent is started by the triage tool. It emits a recommendation, not a purchase:

\`\`\`bash
python .autopilot/retry_policy.py --kind tests --retries 0 --repairs 0
python .autopilot/retry_policy.py --text "Permission denied"
\`\`\`

The running ledger can record a diagnosed retry:

\`\`\`bash
python .autopilot/ap.py ticket 03 retry --cause tests
\`\`\`

In strict routing mode \`--cause\` is required, and the previously verified
model profile must still be valid. Environment, dependencies, unclear requirements,
security and reasoning replan scenarios block direct retry. Unknown causes require
investigation and never imply an automatic model upgrade. Retries and in-context
repairs are limited to **two each**; exceeding the limit stops further attempts.

The classification is heuristic. It can be wrong, particularly on multilingual or
truncated logs. Do not paste unsanitized secrets into the \`--text\` CLI: error text
is processed locally and not persisted, but process arguments may be logged by OS.
The ledger stores only category/advice, not raw failure output.

`--cause` is required for strict routing; `retry_policy.py` is copied into
the project's `.autopilot` bootstrap alongside `ap.py`, `model_router.py`
and `worktrees.py`. The CLI allows a diagnosed `tests` repair or a tracked
`unknown` investigation without silently escalating the model. For reasoning
failures, first replan and explicitly reroute (no automatic Opus/Astra/Fable).
