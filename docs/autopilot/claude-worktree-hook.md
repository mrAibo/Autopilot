# Claude Code `WorktreeCreate` hook (T12 design note)

**Status:** proposal, awaiting owner decision; no code until approved.

## Problem

Claude Code can create its own git worktrees (`isolation: worktree` on a subagent, `--worktree`, the `EnterWorktree` tool, background sessions). Autopilot already prepares one detached worktree per ticket (`worktrees.py`, `ap.py worktree <id> prepare`). The two mechanisms are unrelated: a Claude-made worktree is not a prepared ticket, so `finalize`, `land` and the T07 gate would not see its work. The question is whether a `WorktreeCreate` hook can make Claude Code use the ticket worktree, and whether that is worth its side effects.

## Facts from the docs (code.claude.com, read 2026-10-29)

Each fact is marked **verified** (stated in the docs, quoted or paraphrased closely) or **unverified** (not in the docs, or only tested on paper; nothing here was run live).

1. **verified** `WorktreeCreate` fires for `claude --worktree`, the `EnterWorktree` tool, a subagent with `isolation: "worktree"`, a workflow agent, a background session, and `claude remote-control` in worktree mode. It does not fire for `git worktree add` run through Bash (use a `PreToolUse` Bash hook for that).
2. **verified** "Configuring a WorktreeCreate hook replaces that default git behavior." Every trigger in fact 1 then goes through the hook. `.worktreeinclude` is not processed any more. The event has no matcher: it fires on every occurrence.
3. **verified** Input is the common fields plus `name`, "a slug identifier ... either specified by the user or auto-generated, for example `bold-oak-a3f2`". Example payload keys: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `name`.
4. **verified** A command hook prints the path "as the last non-empty line of stdout" (ANSI codes stripped); other output goes to stderr. A command hook cannot return JSON; an HTTP hook returns `hookSpecificOutput.worktreePath`.
5. **verified** Any non-zero exit, or no path, makes creation fail. An absolute path containing `.` or `..` segments, or passing through a symlink below the repository root, is refused.
6. **verified** `WorktreeRemove` input has `worktree_path`. It runs only for worktrees the hook created, on interactive exit, `ExitWorktree`, background-session delete and remote-control cleanup. Exit 0 means "removed"; the hook must delete the directory itself. Claude Code never deletes the branch of a hook-created worktree.
7. **verified** "When a subagent or a workflow agent finishes, Claude Code keeps the worktree your WorktreeCreate hook made for it and doesn't run your WorktreeRemove hook." The owner must remove those.
8. **verified** Without a hook, the sub-agents page says the isolated worktree branches from the default branch, not the parent session's `HEAD`, and "is automatically cleaned up if the subagent makes no changes". Fact 7 is the hook-created case; the pages do not contradict each other, but the combination was not run.
9. **unverified** Whether the `WorktreeCreate` payload carries `agent_id`/`agent_type` when a subagent triggers it. The docs list `agent_id` only for some other events.
10. **unverified** Whether the `name` of a subagent worktree can be influenced by the orchestrator (for example through the Agent call). The docs only say "specified by the user or auto-generated".
11. **unverified** Whether the hook inherits the project root as its working directory when triggered from a background session. The docs say only that a relative result is resolved against "the directory the hook ran in".
12. **unverified** Live behaviour on the desktop app. The T08 probe never exercised worktrees (`claude-code.md` § Live probe).

## How Autopilot isolates tickets today

- `worktrees.create` makes a **detached** worktree at `.autopilot/worktrees/T<id>` from a recorded base SHA (default `HEAD`). It refuses a dirty tree, a missing `.gitignore` entry, symlinks and junctions.
- `ap.py worktree <id> prepare` stores `{status: prepared, baseCommit, cwd}` on the ticket. `ticket start` verifies the worktree is present and unchanged. `finalize` commits only files inside the declared zone, `land` cherry-picks exactly one commit that sits directly on `baseCommit`, `release` removes the worktree.
- The orchestrator must pass the returned `cwd` to its agent. There is no automatic task-to-worktree scheduler (`worktrees.md`). `claude-code.md` already says: do not silently combine Claude's `isolation: worktree` with a prepared ticket.
- Mismatch with the Claude default: Claude branches from the **default branch**; Autopilot needs the base to be the commit the plan was made on.

## The name-to-ticket mapping problem

The hook sees a slug (`name`) and `cwd`; it does not see a ticket id. Nothing ties `bold-oak-a3f2` to ticket `03`. Without fact 9 or 10 the hook has to guess. A guess is only safe when it cannot be wrong, for example when exactly one ticket is `prepared` and unbound. With parallel executors that rule fails the second subagent, which is the case worktrees exist for.

## Options

| # | Option | Cost | Risk |
|---|---|---|---|
| A | **Card proposal.** Project-level `WorktreeCreate` hook: if exactly one ticket is `prepared` and unbound, bind it and print its `cwd`; otherwise exit non-zero. Outside an Autopilot run, fall back to our own `git worktree add` code. Plus a `WorktreeRemove` hook. | Hook script, a binding field on the ticket record, fallback creation, remove hook, tests for each branch. Medium. | The hook is global: every `--worktree`, `EnterWorktree` and background session now runs our code. The fallback must re-implement default behaviour (default-branch base, `.worktreeinclude`, branch naming); drift breaks owner workflows. Parallel subagents fail. Hook crash = no worktree anywhere. Subagent worktrees are never removed (fact 7). |
| B | **No hook.** Keep Autopilot's own worktrees. Generated Claude profiles never contain `isolation`; the integrity check rejects it in `autopilot-*` agents; the guard denies an Agent call whose input sets `isolation: "worktree"` (input field name needs a check, fact 12). Document the rule. | Small: generator, integrity check, guard branch, tests. | Does not stop an owner's own `--worktree` or `EnterWorktree` (same owner-action gap as F1). No Claude-side auto isolation. |
| C | **Name convention.** Like A, but the hook maps only names of the form `autopilot-<ticket>` to that ticket's prepared worktree and delegates everything else to a fallback (still global, so same fallback cost). | A plus a name parser. | Depends on fact 10. If the orchestrator cannot choose the name, this is A with extra code. |
| D | **Observe only.** Hook (or `PreToolUse`) that logs when Claude makes a worktree during a strict run, without replacing anything. | Not possible for `WorktreeCreate`: any configured hook replaces creation (fact 2). Only the Bash-matcher variant of B applies. | Listed to record that a log-only `WorktreeCreate` hook does not exist. |

## Recommendation

**B now; C only after a live probe; reject A.**

- A trades a small, local gap (Claude's worktrees are separate from tickets) for a project-wide replacement of core Claude behaviour, with a heuristic mapping that fails exactly in the parallel case.
- B costs a few lines and matches the existing rule in `claude-code.md`, and keeps `land`'s base-commit invariant intact.
- C is worth a probe only if the owner wants Claude-initiated isolation: in a disposable project, log the `WorktreeCreate` payload and check whether `agent_id` is present and whether the Agent call can set `name` (facts 9, 10).

## Owner decision

- [ ] B Keep own worktrees; forbid `isolation: worktree` in generated profiles and in guarded Agent calls (recommended)
- [ ] Probe for C: run the live payload/name check above, then decide
- [ ] A Implement the card proposal (hook + fallback + remove hook)
- [ ] Do nothing beyond this note
