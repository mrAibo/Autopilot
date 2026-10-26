# Autopilot — continuation handoff to Codex, Claude Code or another client

**Date:** 2026-10-26 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Workstation:** Aibo, `C:\Users\crown\Downloads\Projects\Autopilot`
**Published baseline:** `v2.3.0`, product commit `90cf259b8919e512d22b518e9fe8c9c45b1744a5`; later checkpoint on main `a5f05600b101c8f05742520fcf9e40633ddb9456`.
**Next focused branch:** `fix/codex-midrun-sequential-handoff` (verify current HEAD, PR and CI before changing it; this handoff is part of that branch).
**Mandatory reading:** `STATUS.md`, `brief.md`, `HANDOFF.md`, `docs/autopilot/release-readiness.md`, `docs/autopilot/sequential-host.md`, `skills/autopilot/phases/0-resume.md`.

## 1. What is released and what remains unverified

Codex 2.3.0 is a **limited sequential-host release**: one isolated Git ticket, pre-existing host-owned Python unittest evidence, conservative acceptance. Codex GUI **does not prove native named subagent model/effort/cwd**, so fail closed instead of inventing a worker or replacing it with a generic one.

Claude Desktop and Claude Code CLI are installed on Aibo (Desktop `3.6556.2.0`, CLI `2.1.302`), the global `~/.claude/skills/autopilot` Junction exists, and the CLI is logged in via OAuth; subscription entitlement and actual child model/effort remain unverified. No extra paid API calls should be made for smoke testing without explicit approval and a subscription-only cost boundary. `ANTHROPIC_API_KEY` was not present.

## 2. Actual Codex failure reported by owner

In `C:\Users\crown\Downloads\Projects\FBreaderREA`, branch `research/native-fbreader`, Git HEAD `723416d7a9be579135cb998cef97bbd588127c39`, the run was initialized as `strictRouting=true, sequentialHost=false, isolateTickets=false`. Codex GUI couldn't spawn a named profile with independently observed model/effort, so it wrote a stop/waiting notice rather than starting a generic worker.

**Run ledger:** `FBreaderREA\.autopilot\state.js`, run folder `.autopilot\2026-10-26-audit-fixes--wip`. 15 requirement rows R01–R15 are recorded in `manifest.md`; `PLAN.md` and `host-blocker.md` exist. Phase `manifest` active; published tickets 0, no executable Autopilot worktree or executor commit. **Do not re-run `init`** or discard these documents.

The project is **intentionally very dirty**: dozens of untracked files (including code, local fixture, audits, scripts) and changes in `.gitignore`, `README.md`. Never run `git add -A`, `git reset --hard`, `git clean`, stash or wholesale commit as an autopilot convenience. A clean baseline would require a deliberately reviewed, scoped Git commit or another separately approved safe fixture. Check `git status --short --branch` before any action.

The project's main native app includes **Rust**, while the 2.3.0 sequential acceptance harness accepts only a baseline-tracked Python `unittest`. This is a real product gap: switching the run to sequential-host alone **cannot** produce an accepted Rust ticket. Do not fake Python wrappers or test totals.

## 3. Targeted fix in this branch

Add `py -3.13 .autopilot/ap.py execution sequential-host --no-serve` to switch a **still-unstarted** strict run without overwriting `state.js`, tickets, the requirement manifest, phase/startedAt or source. It must fail closed if any ticket was launched, worktree prepared, pinned routing approved, execution stage entered, or the run already finished. It closes only the recorded `stop` question and logs the transition. The state lock is handled by the usual `ap.py` wrapper.

After a green code review, regression suite and PR merge, upgrade only the exact `.autopilot/ap.py` copy in the affected project (first verify it matches the previously shipped source hash) and run the switch command **once**, not `init`. Then inspect `strictRouting=false, sequentialHost=true, isolateTickets=true` and unchanged manifest/Git source. Do not start a Rust implementation or call `worktree prepare` until the baseline/test gap below is solved.

## 4. Next actual engineering work (no broad refactor)

1. **R03 non-Python acceptance:** Design/test a minimal, allowlisted, baseline-tracked `cargo test` host verification analogous to current Python unittest integrity. Bind evidence to source fingerprint/base commit and prevent arbitrary shell/command injection; verify stale test proofs are rejected. Keep Rust and Python runners separate and labelled.
2. **Dirty existing-repo onboarding:** non-mutating `doctor` report showing exactly why isolation is blocked, with reviewed/scoped baseline options. No auto-stage of secrets, unknown untracked files or uncontrolled repo-wide changes.
3. **Real host smoke after fixes:** in a disposable copied repository with known-safe files, verify Codex single-host ticket → worktree → edit → Rust tests → trusted finalize/land/accept; distinguish this from native subagent proof.
4. **Docs and UX:** Codex GUI should present the valid sequential fallback at Phase 0 and show exact next command on a blocked strict run; EN/RU/DE instructions, Dashboard, `STATUS.md`, GitHub CI after merge. Do not promise native model+effort enforcement.

## 5. Safety and release

Read the original `brief.md` and current `STATUS.md` before broad changes. Do not create a second writer on a live run or replace native agents with arbitrary premium models. Preserve the `spend_guard` hard stop. Do **not** alter already published `v2.3.0` tag; use a scoped patch release (e.g. 2.3.1) only after suitable verified tests and operator sign-off.

## Copy-ready request to the next client

> Continue `mrAibo/Autopilot` on Aibo from `HANDOFF_NEXT_CLIENT_2026-10-26.md`. Read its required documents and inspect Git/CI first. Finish the fail-closed mid-run switch implementation, tests and PR. The affected `FBreaderREA` working tree is dirty and has 15 open requirements with no started tickets; do not re-init or commit unknown source. After the safe mode switch, tackle independently verified Rust tests and dirty-project onboarding in separately reviewed changes. No independently billed API calls. Explain the exact supported actions and blockers instead of impersonating subagents.
