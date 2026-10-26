# Autopilot 2.3 — optional lean-coding experiment

**Status:** opt-in experiment; no measured cost savings claim.
For a checked-in **offline** comparison of the deterministic Autopilot 2.2
versus 2.3 host CLI and the prompt-byte overhead of `off`/`lean`, see
[R06 measured baseline](r06-offline-benchmark.md). That experiment invokes
no models and establishes no lean token savings.

## Why

Ponytail ([upstream](https://github.com/DietrichGebert/ponytail)) encourages understanding the current code before writing more, reusing existing code and built-in features, and preserving all acceptance and safety checks. In an independent 80-paired-task assessment, [JetBrains reported](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/) a median cost reduction of about 10.3%, with heterogeneous outcomes and no guarantee for this project. Crucially, JetBrains reported that merely putting the upstream skill file into a skills folder had **no actual activation**; the Claude plugin's session-start instruction injection was required.

**Autopilot does NOT bundle or falsely claim to run upstream Ponytail.** It provides a short, original, Ponytail-*inspired* alternative for standalone Codex CLI execution that can be activated explicitly:

```powershell
# Baseline (unchanged default)
py -3.13 .autopilot/codex_dispatch.py 01 --root . --optimization off

# Lean instructions (still a dry run unless --execute is added)
py -3.13 .autopilot/codex_dispatch.py 01 --root . --optimization lean
```

The lean rules ask the worker to understand relevant code/callers, reuse installed mechanisms and stdlib, make only the needed maintainable diff, and **never omit tests, validation, security, accessibility or error handling to save tokens**. The active mode appears in the dry-run JSON. There are no extra dependencies, network downloads or global Claude/Codex settings changed.

Codex GUI and Claude Code GUI **do not automatically inherit this standalone CLI mode**. To evaluate the *original* Ponytail in Claude Code, install its upstream Claude plugin via the provider's supported installer in an isolated test workspace, verify hook startup injection and permissions, and run matching tasks. Do not install globally or replace the owner's existing stable Autopilot 2.2 skill without approval.

## Measurement protocol

For meaningful comparisons use **matched tasks**, same code baseline, same model+effort and sandbox. Alternate baseline and lean to avoid order effects. For each run report actual:
- ticket ID, model, effort, application + skill revisions, host and optimization mode
- JSONL input, output, cached input, duration, retries
- exact file diff size and independent test outcome
- Git acceptance: landed single commit, satisfied requirements, no security regression
- billing (only when actual provider price and usage records support a cost calculation)

**Primary score:** total verified input/output consumption per *accepted* task; report cache tokens separately and never subtract cached tokens from input totals a second time. **Secondary:** accepted-task duration, diff size, and rejection/retry rate. A/B runs consuming twice the compute must be deliberately authorized; no automatic double-run in production. A smaller diff is a benefit only if correctness is maintained.

Stop the experiment if tests fail, a security control regresses, or tool access is blocked. Do not reward a model for returning a short response without doing the work.

## Other meaningful savings

1. Pin cheaper worker models where actual task complexity permits and record route/effort.
2. Prefer short task brief paths over repeating large file contents inside a prompt.
3. Cache observations and avoid re-reading unchanged files after each action.
4. Use a deterministic scheduler and limit repeated agent spawns/repair attempts.
5. Keep validation deterministic outside the LLM where practical, especially Git checks.
6. Measure actual token and acceptance events; no fabricated dollar cost estimate.

## Windows sandbox finding

On Windows, `codex exec --ignore-user-config` may drop a required Windows sandbox backend selector. Autopilot now explicitly supplies `windows.sandbox="elevated"` for the **supported sandbox backend while keeping `--sandbox read-only|workspace-write`**. This is not `--danger-full-access`. In real 2026-10-25 testing, Codex could edit a permitted source file but could not create the shared `.git/worktrees` lock or locate the Python command inside its sandbox. Thus independent host-side tests and a tightly zone-checked Git finalization are necessary; see [worktrees](worktrees.md). Never broadly expose the primary project checkout or disable sandboxing to make commits work.
