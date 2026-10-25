# Git worktree isolation (Autopilot 2.3 development)

`skills/autopilot/tools/worktrees.py` provides **opt-in** isolated Git checkouts per executor ticket. It never reads secrets, makes network requests or force-removes dirty files.

## Host-verified test evidence (strict + isolated)

For strict model routing with isolated task worktrees, manually entered
`--tests N/0` is **not sufficient evidence** for finalization or landing.
The host now runs a baseline-tracked, unchanged Python unittest suite from
the exact worktree, pins the worktree Git HEAD and hashes its tracked diff
plus all nonignored untracked file contents before and after the tests.

```powershell
# Run from the PRIMARY repository, not inside the worktree.
# Must be an existing test module committed in the worktree baseline.
py -3.13 .autopilot/ap.py worktree 01 verify --suite test_calc.py
# If Python unittest reports actual passes and the Git-visible source did not change:
py -3.13 .autopilot/ap.py worktree 01 finalize
py -3.13 .autopilot/ap.py worktree 01 land
py -3.13 .autopilot/ap.py ticket 01 done --commit <landedSHA>
py -3.13 .autopilot/ap.py worktree 01 release
```

`verify` executes the literal interpreter command
`sys.executable -B -m unittest -q <baseline-tracked-module>` with direct
argument passing (no shell expansion), a bounded timeout (default 90 sec,
10–300 sec permitted), disabled Python bytecode writes and user site
packages. It requires a real `Ran N tests`, `OK`, process exit 0,
N greater than zero, and an unchanged Git-visible fingerprint. The task's
state records the suite name, approved worktree head, fingerprint, count,
timestamp and a host-generated verifier marker. Attempts to supply
different `--tests` counts at `finalize`, `land` or `ticket done`
fail closed. After a worker changes the files, **rerun verify**.

This is an **independent execution record, not a tamperproof attestation**:
Python tests execute arbitrary test code, including imports from the
worktree. Only run suites you trust. The runner currently supports
Python unittest and Git-visible files, not pytest, ignored local files,
symlinked modules, Docker environments or proof against an actor who can
directly rewrite the state file. A test suite modified relative to the
baseline is refused. Tests must not require model permissions or network.

Older non-strict workflows still accept explicitly reported `N/0` for
backward compatibility. **Use `--strict-routing --isolated-tickets`**
when independently verified results are mandatory.

## Host-side finalization for constrained Windows sandboxes

Windows Codex may safely edit files within a worktree while refusing to create Git
index locks under the main repository's `.git/worktrees` metadata directory,
outside its workspace-write boundary. Test runners may also be unavailable
inside a sandbox. **Do not disable the sandbox or use danger-full-access.**

When Codex has finished editing but produced no commit, the **trusted host**
can run project tests independently from the worktree, then call:

```powershell
# From the main project root, after verifying the worker has stopped:
# Run your actual independent test suite from the worker cwd, not from main.
# Prevent Python tests from creating unwanted __pycache__/ artifacts.
$env:PYTHONDONTWRITEBYTECODE = "1"
py -3.13 -m unittest -q test_calc.py   # EXAMPLE; run inside worker cwd
py -3.13 .autopilot/ap.py worktree 01 finalize --tests 2/0
py -3.13 .autopilot/ap.py worktree 01 land --tests 2/0
py -3.13 .autopilot/ap.py ticket 01 done --commit <landedSHA>
py -3.13 .autopilot/ap.py worktree 01 release
```

`finalize` creates a single host-side Git commit **only** when test totals are
declared N/0, the executor HEAD still matches its base, the main source
checkout is clean, all changed files are confined to exact ticket zones
(no wildcard, unsafe path, redirected symlink or extra untracked file), and
`git diff --check` passes. It stages only approved paths, does not delete
untracked files and does not run arbitrary test commands. The user/host must
actually run and inspect tests first; **the reported N/0 is not a cryptographic
proof of test execution**. If the host has no configured Git author, configure
local user.name/email before finalization.

This is optional: on hosts where an isolated executor can safely create one
Git commit on its own, continue directly to `land` after independent review.
Only the host may finalize; an LLM must not silently claim a commit occurred.
A completed Codex model turn without a clean worker commit now returns
`incomplete`, never accepted.

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
