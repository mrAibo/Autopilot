# Project-independent, read-only Git preflight

Autopilot provides a non-mutating repository diagnostic. Use it before creating an
isolated ticket worktree, especially when attaching Autopilot to **any existing
project**. It is not a migration tool and does not change project source.

```powershell
py -3.13 C:\path\to\Autopilot\skills\autopilot\tools\repo_doctor.py --root C:\path\to\project
```

Or, from the Autopilot checkout, invoke `py -3.13 skills/autopilot/tools/repo_doctor.py --root <repository-root>`.

The command produces JSON (exit 0 for basic Git readiness, exit 2 when blocked)
and does **not** create state, run tests, start agents, stage changes, stash,
reset, clean, commit or modify `.gitignore`. It reports only aggregate
staged/unstaged/untracked/conflict counts, never filenames or contents.

It checks that you selected the exact Git root, a valid base commit exists,
source files (excluding the Autopilot runtime ledger) are clean, the isolated
worktree location is ignored by Git and no redirecting symlink/junction occupies
the default worktree path.

The `can_prepare_worktree` result checks basic prerequisites only: it is **not**
permission to prepare a particular ticket, proof of a healthy build, or a
guarantee that a particular worktree name is available. `worktrees.create`
performs its own final checks.

For a blocked source checkout, **review the changes yourself** and decide
which files belong in a scoped commit; Autopilot must never stage all files,
discard untracked data or quietly switch the source baseline. In a repository
with no first commit, make a deliberately reviewed initial baseline first.

The standalone diagnostic never executes language-specific test scripts.
Autopilot currently accepts host-owned **baseline-tracked Python unittest**
proofs for strict isolated ticket acceptance. Detecting `Cargo.toml`,
`package.json` or `go.mod` prints a warning that Cargo, JavaScript/TypeScript
and Go are **not yet accepted by the trusted host verifier**. It does not
pretend that lint, build success, or an arbitrary test command proves
acceptance.

This facility belongs to Autopilot itself; no other product's work plan or
application-specific requirements are imported by running it.
