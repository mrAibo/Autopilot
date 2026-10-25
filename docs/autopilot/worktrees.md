# Git worktree isolation (Autopilot 2.3 development)

`skills/autopilot/tools/worktrees.py` provides **opt-in** isolated Git checkouts per executor ticket. It never reads secrets, makes network requests or force-removes dirty files.

## Workflow

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
