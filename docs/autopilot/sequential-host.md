# R03 — Codex 2.3.0 released host-verified sequential mode

Use this mode **only when the current graphical/terminal host cannot prove native named-subagent execution** with the exact model, reasoning effort and working directory. It is a **single-operator / single active ticket** file and Git workflow, not a replacement AI launcher.

**Supported and tested here:** Python/Git host operations in a disposable repository, a real one-at-a-time worktree, baseline-tracked Python unittest re-execution and evidence, detected source changes, one validated finalization / integration / ticket acceptance. **Not established:** what real Codex/Claude GUI model ran, token billing, effective inference effort, parent-context isolation, independent blind reviewer identity or complete real GUI end-to-end. No provider model is invoked by `ap.py`. Your graphical host/model picker controls any inference you choose to perform. **If the host's effective model/Effort and subscription-covered usage cannot be established independently, stop instead of letting Autopilot silently run a premium model.**

## New run: create an explicit sequential host workflow

Use a **clean or reviewed project** and prepare its plan according to the ordinary phases. During Phase 0, choose this mode instead of the strict native subagent route:

```powershell
py -3.13 .autopilot/ap.py init --slug my-project --title "My project" --skill-dir PATH_TO_AUTOPILOT_SKILL --sequential-host
```

- `--sequential-host` implies `--isolated-tickets`, sets `sequentialHost=true` and `strictRouting=false`. These two modes cannot be combined. It does **not** create a named agent, model assignment or false verified provider record.
- Only **one prepared/running ticket** is allowed, including across dependency waves; `schedule --max-parallel 2` is rejected rather than silently downgraded. The default scheduler capacity becomes 1.
- The normal `route` action is deliberately disabled in this mode: its TOML/Markdown profile would be a claim about an unavailable native worker, not proof of execution.
- Recover an existing unfinished project using [Phase 0 resume](../../skills/autopilot/phases/0-resume.md); never run `init` again just to change its mode or bypass accepted tasks.

## Existing strict run stopped by Codex GUI (no re-init)

For an **unfinished, unstarted** run that selected `--strict-routing` before Codex GUI reported that named-agent model/effort cannot be verified, the safe migration is:

```powershell
py -3.13 .autopilot/ap.py execution sequential-host --no-serve
```

This keeps the run ID, requirements, completed planning stages, and source unchanged, sets `strictRouting=false`, `sequentialHost=true`, `isolateTickets=true`, closes a pending `stop` notice, and records the decision. It refuses completed runs, launched or approved tasks, existing worktrees, applied native routing, or any evidence of earlier worker execution. It does **not** run a model, create a Git commit, or make dirty source safe. Run `git status --short --branch` first; if the source is dirty, `worktree prepare` remains blocked. Never automatically `git add -A` or discard unrelated user files just to make it pass.

**Non-Python projects:** the released sequential workflow currently accepts only baseline-tracked Python `unittest`. Rust/Node-only projects are **not** accepted by this verifier. A Rust `cargo test` adapter requires a separate safe implementation with host-owned command allowlisting, baseline-tracked test evidence and regression coverage; until then stop before `worktree prepare` / acceptance rather than inventing Python proofs.

## Work one ticket at a time

```powershell
py -3.13 .autopilot/ap.py tickets
py -3.13 .autopilot/ap.py check-plan
py -3.13 .autopilot/ap.py schedule --max-parallel 1
py -3.13 .autopilot/ap.py worktree 01 prepare
py -3.13 .autopilot/ap.py ticket 01 start
```

At this point the CLI has **only reserved a checkout**. Review the `worktree.cwd` in the recorded state. If the current GUI host can safely edit files **in that exact worktree**, an explicitly authorized **single-session** operation may implement only the assigned ticket; do not label it `autopilot-executor-01`, claim that a child agent was created, or claim that the model was enforced by Autopilot. **Do not invoke `codex_dispatch.py --execute`, `gui_bridge.py --execute`, arbitrary API clients or generic premium subagents.** The separate optional CLI bridge remains disabled by `spend_guard`.

After edits and any real tests, have the **trusted host** use the existing fixed runner. The suite must be an unchanged baseline-tracked Python `unittest` module; it cannot be an arbitrary shell command, a freshly added self-approving test, pytest, JavaScript, or a manually supplied pass count.

```powershell
py -3.13 .autopilot/ap.py worktree 01 verify --suite test_calc.py
py -3.13 .autopilot/ap.py worktree 01 finalize
py -3.13 .autopilot/ap.py worktree 01 land
py -3.13 .autopilot/ap.py ticket 01 done --commit ACTUAL_LANDED_SHA
py -3.13 .autopilot/ap.py worktree 01 release
py -3.13 .autopilot/ap.py schedule --max-parallel 1
```

`verify` invokes real tests on the host, stores code fingerprint and observed passed/failed counts. `finalize`, `land`, `done`, and recovery checks refuse an absent, stale or forged test result. `finalize` only stages the approved ticket zones; integration requires a clean main checkout and commits. If the trusted suite is unavailable or fails, **stop acceptance**. Complete the ordinary G1–G4, whole-project tests and blind acceptance without inventing a separate reviewer or claiming G4 is independently attested by the runtime.

## Failures and recovery

| Observed situation | Safe next action |
|---|---|
| Another task already prepared or active | Finish or explicitly recover that worktree before preparing/starting a second; no parallel executor |
| Tests fail or nobody can run a trusted baseline `unittest` | Do not finalize, land or mark done; report the blocker. Manual `N/0` does not replace host evidence |
| Source edited after `verify` | Repeat real `verify`; stale test fingerprint invalidates finalization |
| Crash after `prepare`, `finalize`, Git cherry-pick or `release` | In the **same project**, inspect `state.js`, `git status --short --branch`, `ap.py commits` and `worktree NN status`; use conservative `worktree NN recover` only after reviewing preserved files, never `git reset --hard` |
| Native GUI model/premium status unknown | Stop model work. Existing CLI commands inspect files and do not prove provider identity/cost |
| Real Codex/Claude named agent becomes verifiable in a later version | Start an explicitly new, approved native-routing run after live capability proof. Do not silently mutate a running sequential state into a named-agent run |

**2026-10-26 owner-assisted result:** In a disposable ChatGPT **project** (not native Codex GUI named-agent mode), the GUI agent reported editing the prepared `T01/src/core/calc.py` only. The trusted Windows host observed exactly that one-file Git diff, passed an unchanged tracked test **1/0**, and completed `verify → finalize → land → done → release`, integrated fixture commit `283c662b57a2`. See [R03 evidence ledger](release-readiness.md). The agent **could not identify effective model or Effort**; identity and subscription charging remain unverified.

**Trust limits:** Unit tests exercise this exact host/Git state machine; the above one user-assisted file-edit does not prove the GUI's model metadata, native child dispatch or provider usage. Non-Python ignored inputs and external package integrity are not fully hermetic; see [worktrees.md](worktrees.md) and [release-readiness.md](release-readiness.md). The Codex 2.3.0 limited release includes this host/Git state machine. Native GUI named-agent and model/billing enforcement remain **unsupported, not release-complete**.
