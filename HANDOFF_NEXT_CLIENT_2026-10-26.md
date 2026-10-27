# Autopilot — continuation handoff to Codex, Claude Code or another client

> **Archived cross-project incident context — not the current Autopilot roadmap.** This document records a historical support case from another repository. The owner clarified on 2026-10-27 that other project is separate. Do not treat its 15 requirements, Rust codebase, or dirty Git tree as Autopilot's own project or as a priority mandate. For current Autopilot development, use [HANDOFF.md](HANDOFF.md), [STATUS.md](STATUS.md), [brief.md](brief.md) and the independently scoped [repository preflight](docs/autopilot/repository-preflight.md). Do not modify the other repository as part of Autopilot work.

**Date:** 2026-10-26 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Workstation:** Aibo, `C:\Users\crown\Downloads\Projects\Autopilot`
**Published baseline:** `v2.3.0`, product commit `90cf259b8919e512d22b518e9fe8c9c45b1744a5`. **Post-release fix already merged on main:** `54d8ca32d191aa98ed11246ad0fd86b2d5f76590` ([PR #33](https://github.com/mrAibo/Autopilot/pull/33), 4/4 GitHub CI; Windows Python 3.13 local 320/320). Do not change the published tag.
**Continue from:** clean, synchronized `main` on Aibo. The strict-to-sequential switch is **already implemented and applied** to FBreaderREA; next work is host-attested Rust tests and safe dirty-repo onboarding, not another switch rewrite.
**Mandatory reading:** `STATUS.md`, `brief.md`, `HANDOFF.md`, `docs/autopilot/release-readiness.md`, `docs/autopilot/sequential-host.md`, `skills/autopilot/phases/0-resume.md`.

## 1. What is released and what remains unverified

Codex 2.3.0 is a **limited sequential-host release**: one isolated Git ticket, pre-existing host-owned Python unittest evidence, conservative acceptance. Codex GUI **does not prove native named subagent model/effort/cwd**, so fail closed instead of inventing a worker or replacing it with a generic one.

Claude Desktop and Claude Code CLI are installed on Aibo (Desktop `3.6556.2.0`, CLI `2.1.302`), the global `~/.claude/skills/autopilot` Junction exists, and the CLI is logged in via OAuth; subscription entitlement and actual child model/effort remain unverified. No extra paid API calls should be made for smoke testing without explicit approval and a subscription-only cost boundary. `ANTHROPIC_API_KEY` was not present.

## 2. Actual Codex failure reported by owner

In `C:\Users\crown\Downloads\Projects\FBreaderREA`, branch `research/native-fbreader`, Git HEAD `723416d7a9be579135cb998cef97bbd588127c39`, the run was initialized as `strictRouting=true, sequentialHost=false, isolateTickets=false`. Codex GUI couldn't spawn a named profile with independently observed model/effort, so it wrote a stop/waiting notice rather than starting a generic worker.

**Run ledger:** `FBreaderREA\.autopilot\state.js`, run folder `.autopilot\2026-10-26-audit-fixes--wip`. 15 requirement rows R01–R15 are recorded in `manifest.md`; `PLAN.md` and `host-blocker.md` exist. Phase `manifest` active; published tickets 0, no executable Autopilot worktree or executor commit. **Do not re-run `init`** or discard these documents.

The project is **intentionally very dirty**: dozens of untracked files (including code, local fixture, audits, scripts) and changes in `.gitignore`, `README.md`. Never run `git add -A`, `git reset --hard`, `git clean`, stash or wholesale commit as an autopilot convenience. A clean baseline would require a deliberately reviewed, scoped Git commit or another separately approved safe fixture. Check `git status --short --branch` before any action.

The project's main native app includes **Rust**, while the 2.3.0 sequential acceptance harness accepts only a baseline-tracked Python `unittest`. This is a real product gap: switching the run to sequential-host alone **cannot** produce an accepted Rust ticket. Do not fake Python wrappers or test totals.

## 3. Completed and tested hotfix — do not repeat

PR #33 **added** `py -3.13 .autopilot/ap.py execution sequential-host --no-serve` for a **still-unstarted** strict run without overwriting source, requirements or progress. It refuses prior worker/routing/worktree execution or a finished run. New negative tests, complete local Windows 320/320 and 4/4 GitHub CI passed.

This was performed on the **actual** FBreaderREA run on 2026-10-26 at 22:24 Europe/Berlin, with saved script/state/dashboard backup in `%TEMP%\Autopilot_FBREADER_PreSwitch_20261026_222450`: verified `strictRouting=false`, `sequentialHost=true`, `isolateTickets=true`, `waiting=null`, **15 requirements, zero published tickets**, unchanged `manifest.md` and unchanged complete Git status. Do not re-run the switch. Do not start Rust execution or `worktree prepare` until the baseline/test gaps below are resolved. See the local project-specific handoff `FBreaderREA\HANDOFF_AUTOPILOT_CROSS_CLIENT_2026-10-26.md`.

## 4. Next actual engineering work (no broad refactor)

1. **R03 non-Python acceptance:** Design/test a minimal, allowlisted, baseline-tracked `cargo test` host verification analogous to current Python unittest integrity. Bind evidence to source fingerprint/base commit and prevent arbitrary shell/command injection; verify stale test proofs are rejected. Keep Rust and Python runners separate and labelled.
2. **Dirty existing-repo onboarding:** non-mutating `doctor` report showing exactly why isolation is blocked, with reviewed/scoped baseline options. No auto-stage of secrets, unknown untracked files or uncontrolled repo-wide changes.
3. **Real host smoke after fixes:** in a disposable copied repository with known-safe files, verify Codex single-host ticket → worktree → edit → Rust tests → trusted finalize/land/accept; distinguish this from native subagent proof.
4. **Docs and UX:** Codex GUI should present the valid sequential fallback at Phase 0 and show exact next command on a blocked strict run; EN/RU/DE instructions, Dashboard, `STATUS.md`, GitHub CI after merge. Do not promise native model+effort enforcement.

## 5. Safety and release

Read the original `brief.md` and current `STATUS.md` before broad changes. Do not create a second writer on a live run or replace native agents with arbitrary premium models. Preserve the `spend_guard` hard stop. Do **not** alter already published `v2.3.0` tag; use a scoped patch release (e.g. 2.3.1) only after suitable verified tests and operator sign-off.

## Copy-ready request to the next client

> Continue `mrAibo/Autopilot` on Aibo from `HANDOFF_NEXT_CLIENT_2026-10-26.md`. Read its required documents and inspect Git/CI first. The fail-closed mid-run switch was already merged in PR #33 and applied to `FBreaderREA`. Its working tree remains dirty, with 15 open requirements and no published tickets. Do not re-init, switch again, or commit unknown source. Next tackle independently verified Rust tests and dirty-project onboarding in separately reviewed changes. No independently billed API calls. Explain the exact supported actions and blockers instead of impersonating subagents.
