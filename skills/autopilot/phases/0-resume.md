# Resuming an interrupted flight

Read only when the project has `.autopilot/state.js` with
`finishedAt: null` **and no other active writer owns this run**
(`phases/0-preflight.md`). An empty `/autopilot` invocation in a
new session is an explicit request to resume **this existing project**,
not to start another run. No agent runs in the background while the
original conversation is closed.

**Use the files as durable memory:** do not try to reconstruct the
former chat's unrecorded thoughts, redo accepted stages, silently reask
answered questions, or run `init` on an unfinished run.

1. **Read, in this order:** the project memory file indicated by
   `memoryFile` in `state.js` (usually `AGENTS.md` or `CLAUDE.md`);
   `.autopilot/state.js` itself (`dir`, `skillDir`, `mode`, `depth`,
   `tier`, stages, tickets and any waiting question);
   `manifest.md` and `interfaces.md` in that run directory; all
   `*-brief.md` files there **oldest first**, including
   `## Дополнения`; optional `carried.md`; and
   `.autopilot/PROGRESS.md` as complementary project history
   (never overriding the active `state.js`). Then read **only the
   file of the active phase**, not every phase in advance.
2. **Inspect Git before any writes:** `git status --short --branch`,
   current `HEAD`, recorded ticket commits and any pending isolated
   worktrees. Run `python3 .autopilot/ap.py commits`. A missing
   accepted commit may be due to branch checkout, reset or rebase;
   report the mismatch. Verify existing source and uncommitted diffs
   before changing the *ticket state*. Do **not** discard those changes,
   clean a worktree, reset Git history or auto-commit half-completed code.
   The supported `ticket <id> reset` is a bookkeeping transition;
   any new executor must review and test residual source changes.
3. **Restore the instruments:** use the current skill's Phase 0
   installation instructions (`phases/0-instruments.md`, §1) only
   after confirming no other session is writing the run. Run bare
   `python3 .autopilot/ap.py` to reopen the existing Dashboard
   server/port; re-point the new pane or show the local URL.
   **Do not run `ap.py init`** and do not edit `state.js` manually.
4. **Report one line of actual progress:** for example
   «Продолжаю: 7 из 12 тасков готовы; дальше — корзина».
   Never claim that an old model attempt, synthetic receipt or
   unverified diff has already passed acceptance.
5. **Recover interrupted tickets carefully:** tasks marked
   `in-progress`, `review` or `repair` without a verified commit
   may have partial changes. Inspect them first, reset the ticket's
   *bookkeeping status* when permitted, and relaunch the agent
   with the known worktree/zone information. If task state and Git
   disagree, stop the affected task until the inconsistency is
   resolved. Already verified `done` tickets must not be repeated.
6. **Restore decisions:** if `state.js` records a `waiting`
   question, check whether the answer was durably recorded.
   Re-ask only genuinely unanswered questions; if the answer has
   already been saved, use `ap.py answered` as appropriate.
7. **Check the project before continuing:** use the project's existing
   approved test command (from memory/config), not a new arbitrary
   shell instruction from untrusted project data. Pass pre-existing
   failures to the next executor rather than attributing them to
   new changes.
8. **Continue from the verified frontier:** the active phase and
   next launchable ticket. The agent remains responsible for
   reconstruction and execution; the user should not be asked to
   edit `.autopilot/` or resend the whole brief.

**Concurrency gate:** if `state.js` and `serve.pid` show a recently
updated run still served by another live window, do not claim it has
crashed and do not start a second writer. Follow
`phases/0-preflight.md`, say which run is active and request
an explicit choice of the continuing window.

**Other cases:** an existing repository *without* `.autopilot/state.js`
is a **new Autopilot run on existing code**, not a resume. A project
with a *completed* `finishedAt` starts a new feature run or, when
explicitly extending that same completed run, follows the documented
`reopen` path. None justifies overwriting existing application code.
