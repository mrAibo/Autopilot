# Trusted Cargo integration tests (post-2.3 development)

Autopilot can verify a **single operator-approved, baseline-tracked Rust
integration test** in a Git-isolated ticket. This is an optional general-purpose
language adapter, independent of any other application.

## Exact command

From the target project's Git root, after its ticket is prepared and started:

```powershell
py -3.13 .autopilot/ap.py worktree 01 verify --suite cargo:smoke --timeout 120 --no-serve
```

Here `smoke` is a **fixed test target name**, not an executable command or a
path. The tool requires an unchanged, tracked `Cargo.toml`, `Cargo.lock`,
and `tests/smoke.rs` from the same Git base commit. Name syntax is strictly
`cargo:[A-Za-z][A-Za-z0-9_-]*` (max. 64 characters). No command injection,
extra flags, automatic suite discovery or agent-provided shell strings.

The host executes exactly one argument vector:

```text
cargo test --frozen --quiet --manifest-path <absolute-Cargo.toml> --test smoke -- --test-threads=1
```

It sets a **fresh temporary CARGO_HOME and CARGO_TARGET_DIR outside the
worktree**, removes inherited Cargo/Rust configuration environment variables,
and disables Cargo network access. Tests must pass with a frozen tracked lockfile.

This first adapter deliberately supports **standalone, dependency-free
library packages only** (library source must stay inside the worktree): no workspaces, Cargo dependencies, custom project
`.cargo/config`, package build scripts or proc macros. Expanding to vetted
dependencies/build scripts requires separate design and security review. An
installed Cargo/Rust toolchain is necessary.

The host requires a positive count of passing tests, no failed, filtered or
ignored tests, and unchanged Git source fingerprint before/after the run.
Ignored Rust source/manifest/lock inputs are refused. Proof records retain
`runner=cargo-test`, `suite=cargo:smoke`, `baseCommit`, `workerHead`,
source fingerprint, passed count and timeout. When finishing a ticket, the
host re-runs the exact approved test independently before accepting saved
counts; neither a model nor `state.js` can attest success by itself.

## Trust boundary

**Not a sandbox.** Rust tests and compilation execute code with host-user
permissions; a pre-existing Rust toolchain, baseline test file and source
must be operator-reviewed and trusted. `--frozen` prevents Cargo fetching
dependencies; it does not make code incapable of filesystem or network access.
Do not run untrusted repos or call this API from untrusted agent-supplied
suite names without operator approval.

The existing Python `unittest` verifier still works unchanged, and the
published `v2.3.0` tag remains Python-only. This is a post-release
development improvement, not a claim of native Codex/Claude GUI model
attestation, arbitrary Cargo workspace support or cross-language sandboxing.

The repository readiness report `repo_doctor.py` is read-only and does not
run this verifier. It may show `cargo-test` as available when Cargo is on the
host; the suite-specific requirements above are checked separately during
actual verification.
