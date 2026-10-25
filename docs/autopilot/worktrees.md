# Git worktree isolation (Autopilot 2.3 development)

`skills/autopilot/tools/worktrees.py` provides **opt-in** isolated Git checkouts per executor ticket. It never reads secrets, makes network requests or force-removes dirty files.

## Recovery after an interrupted run

The Python CLI records a source Git SHA and uses `git cherry-pick -x` to preserve
source provenance in the integrated commit message. If power is lost **after**
Git integration but **before** the state file is saved, do not cherry-pick again.
Use:

```bash
python .autopilot/ap.py worktree 03 recover --tests 34/0
```

This validates the source commit, exact cherry-pick marker and stable patch ID,
then records the previously landed commit without modifying Git. Tests must be
independently confirmed (`34/0` is supplied by the orchestrator, not generated
by the recovery routine). A duplicate `worktree land` is also idempotent when
matching Git provenance exists.

If `git worktree add` completed before ledger persistence, `recover` can
reconstruct the prepared record **only if** the worktree is clean, its HEAD
equals primary HEAD and the task is pending. Dirty or ambiguous checkouts remain blocked for manual investigation.
If a crash leaves `CHERRY_PICK_HEAD`, the recovery helper **does not**
automatically abort or continue the sequencer. Inspect `git status`, any
conflict markers and user modifications. Resolve via `git cherry-pick
--continue` or `git cherry-pick --abort` only after review. After abort,
retry a controlled landing; after continuation, verify provenance and use
`worktree recover --tests N/0`. Never force-remove a dirty worktree.

The read-only scheduler command

```bash
python .autopilot/ap.py schedule --max-parallel 2
```

outputs JSON `selected` actions `route`, `prepare`, `start`; its
`blocked` reasons include dependencies, source-zone collisions, exhausted
recorded-token budget and no remaining concurrency. The scheduler does **not**
spawn or manage external model agents: the orchestrator must obey actions/cwd.
Worktree `reset` and `reopen` refuse unreleased worktrees.

## Integrated Autopilot CLI lifecycle

For a new run explicitly enable `ap.py init ... --isolated-tickets` and
commit setup file changes such as `.gitignore` before worktree preparation.
Run the following commands from the **primary project directory**:

```bash
python .autopilot/ap.py worktree 03 prepare
python .autopilot/ap.py ticket 03 start
# Dispatch the executor with cwd returned by prepare; it writes exactly one
# Git commit to that detached checkout (it must not edit the primary sources).
python .autopilot/ap.py worktree 03 land --tests 34/0
python .autopilot/ap.py ticket 03 done --commit <landedCommit>
python .autopilot/ap.py worktree 03 release  # only AFTER accepted done
```

`ap.py worktree 03 status` reports the current checkout state. Dependencies
must be satisfied before `prepare`. Landing checks that an executor has exactly
one clean commit directly after its recorded base and the main **source** checkout
is clean; the changing internal `.autopilot` run ledger is excluded from that
cleanliness check. The worktree landing step records the actual integrated SHA
after cherry-pick (it can differ from the source SHA). Ticket `done` rejects
unlanded or mismatched commits. `release` will remove only a clean worktree
after its ticket has been accepted and its integrated commit is still in HEAD;
the source SHA may differ from cherry-picked SHA. If the ticket Markdown
changes while a prepared/landed worktree exists, republishing the plan blocks
rather than silently losing its state. `done` cannot bypass preparation in
isolated mode.

**The CLI does not spawn any external model agent, and it cannot prove which
cwd the host actually used.** The host must launch the agent in the returned
worktree and ensure its source checkout, local services and test environment are
truly isolated. If it cannot, run work sequentially.

## Low-level Git workflow


```bash
# From the project root, after the base commit is established:
python .autopilot/worktrees.py create 03 --root . --base HEAD
# Returns .autopilot/worktrees/T03; launch the executor with this exact cwd.

# Executor edits and commits in its detached worktree; no direct edits in the primary tree.
python .autopilot/worktrees.py status 03 --root .

# The orchestrator serializes integration, verifies tests and lands ONE commit:
python .autopilot/worktrees.py land 03 --root . --base <base-commit-SHA>

# Only after verifying the landed change, explicitly discard detached source:
python .autopilot/worktrees.py remove 03 --root . --acknowledge-loss
```

The baseline commit is recorded when the worktree is created. `land` requires a clean primary checkout, clean executor checkout and exactly one commit after that base. On merge conflicts, it aborts the cherry-pick. It does **not** automatically resolve conflicts or repair tests. Never remove a worktree with uncommitted files.

The `--acknowledge-loss` option is deliberately explicit because cherry-picking can rewrite SHA, so a successful landed commit may not be an ancestor of `main`. A detached worktree may hold otherwise unreachable commits; verify source SHA and resulting files before removal.

## Limitations

- No automatic task-to-worktree scheduler yet; the orchestrator must pass the returned `cwd` to its agent. If the harness cannot assign an isolated cwd, serialize writes.
- Each parallel executor must use separate temp directories, services, ports, database schemas and build outputs. Git isolation alone does not isolate PostgreSQL or other shared services.
- Do not run `land` for multiple executors simultaneously. The primary Git tree is a single-writer integration target.
- A task that creates multiple commits, has uncommitted modifications, or needs history rewrites requires explicit manual integration rather than automatic `land`.
- `.autopilot/worktrees/` must be Git-ignored. Reused dependency installations may need their own isolated setup.
