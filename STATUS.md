# STATUS.md — Autopilot 2.3 handoff

**Updated:** 2026-10-25 (Europe/Berlin)
**Repository:** https://github.com/mrAibo/Autopilot
**Active branch:** `main`
**Merged:** [PR #1](https://github.com/mrAibo/Autopilot/pull/1), squash commit `00600107be80fdb54015611647c767954aa096be` on 2026-10-25. Owner explicitly approved promotion to main after confirming the skill appears in Codex GUI.
**Development history:** `feat/autopilot-2.3-adaptive-router-dashboard` (192 commits retained; do not rely on it as the current deployment branch).
**Version:** `metadata.version = 2.3.0-dev`. This is a **main-branch development snapshot**, NOT a final 2.3.0 release. No stable release tag. Do not confuse publishing to main with feature-complete GUI runtime support.
**Specification:** `бриф.md`. Read this STATUS first when resuming work; update it after every milestone.

## Verified QA / source

- Feature HEAD `b3dee4d319a4145c8c8a9f74bde6335237347993` passed [Actions #40199093084](https://github.com/mrAibo/Autopilot/actions/runs/40199093084): **4/4 jobs green** (Ubuntu and Windows / Python 3.11 and 3.13), **144 Python tests** on Ubuntu 3.13, JavaScript syntax and headless Chrome dashboard smoke (desktop/narrow).
- GitHub reports **PR #1 merged** into `main` via a single squash commit. Re-check the post-merge `main` CI after this STATUS update; do not claim it green without observing its result.
- User confirmed `autopilot` is visible in the graphical Codex skill selector. **This verifies discovery only**, not GUI child-agent model/effort/cwd, writable sandbox or accepted end-to-end GUI task.
- Earlier Windows host targeted tests: 13 worktree and 13 Codex adapter tests; strict isolated host verification integration passed. Live account Codex catalog import worked, and standalone Luna/Low read-only requests returned `CODEX_OK` (5s; input 19718, cached 12672, output 7) and `CONFIG_ISOLATED_OK` (4s; input 16643, cached 11776, output 9).
- Live synthetic Windows model task: Codex Luna/Low actually changed `calc.py` in `%TEMP%\autopilot-23-codex-e2e-20261025`; trusted host ran **2/2 tests**, committed only the approved edit (`262b83e`), landed in synthetic checkout (`e7e1975`), accepted the ticket and released its worktree. The now-implemented host `worktree finalize` command was independently validated in tests, not in that live paid task.
- The initial Windows CLI hang resulted from unclosed stdin in the remote test; prompt sent via stdin+EOF fixed it. The Windows Codex sandbox backend needed explicit `windows.sandbox="elevated"` while preserving `--sandbox read-only|workspace-write`; it could edit source but not access shared Git `index.lock` or `python` inside the sandbox. **Never disable sandboxing to make the test pass.**

## Current installation on owner's Windows PC

- Repo: `C:\Users\crown\Downloads\Projects\Autopilot`. After merging, fetch/switch or fast-forward to `main` **only if clean**. Global skills are Junctions to `...\Autopilot\skills\autopilot`; the directory must remain intact during branch change.
- Verified global directories `%USERPROFILE%\.agents\skills\autopilot`, `%USERPROFILE%\.claude\skills\autopilot`, `%USERPROFILE%\.codex\skills\autopilot`: each is a Windows **Junction** to the SAME checked-out skill folder and each reported `metadata.version=2.3.0-dev`. No duplicate skill installation.
- The old globally installed 2.2 skill directory was removed with owner approval. Its obsolete `nick-vels/skills` entry was removed from the **user's** installer lock; other skills were left untouched. Do not run `npx skills update autopilot -g` while working from the Junction-linked dev checkout or it may replace these links.
- Installed official Codex CLI `0.165.0-alpha.1` via npm and logged in with ChatGPT, GUI Codex app installed. VPN off resolved HTTP provider availability (doctor 21 ok, 0 fail). Claude general desktop app is present; actual Claude Code CLI and GUI-native agents remain unverified.
- Isolated GUI test folder `%TEMP%\autopilot-gui-skill-smoke-20261025` also has project-level Junctions to the same source; safe to reuse for validation.

## Implemented in 2.3.0-dev

1. Spec/requirement ledger; G1–G4 hard acceptance gates; strict task state, commit/test checks, state locking and bounded retry diagnosis.
2. OpenAI/Anthropic model+effort routing with fail-closed account capability verification; SHA-pinned native `.codex/agents/*.toml` and `.claude/agents/*.md`. Restricted expensive model tiers excluded by default. Optional Claude Code `PreToolUse` guard; runtime model inheritance still subject to host behavior.
3. Detached Git worktrees with safe `prepare → start → finalize → land → done → release`, source-linked cherry-pick and conflict recovery. Host `finalize` only stages exact approved zones, not unknown or symlink files.
4. Strict isolated `worktree NN verify --suite test_file.py` invokes an **unchanged baseline-tracked Python unittest** on trusted host, records genuine test count + source fingerprint, and denies fake N/0 or source changes at finalize/land/acceptance. This is not tamperproof against editing `state.js` or ignored files; other test runners are not yet supported.
5. Standalone Codex CLI worker with isolated sandbox/cwd and JSON token usage; **completed model turn without clean worker commit = `incomplete`, never accepted**. Scheduler `ap.py schedule --max-parallel 2` produces a read-only plan, it **does not dispatch agents automatically**.
6. Dashboard 3.0 (model assignments, worktree/recovery state, gates, recorded tokens and threshold), responsive Chrome smoke. Optional `codex_dispatch.py --optimization lean` instructions inspired by Ponytail (OFF by default; original Ponytail plugin NOT installed or benchmarked).
7. English/Russian READMEs display 4 **actual current Dashboard 3.0 Chrome screenshots** generated from synthetic state (desktop/narrow). Retired 14 obsolete 2.2 screenshots and imported old `skills-lock.json`. README only credits *Inspired by*; required original MIT copyright remains in `LICENSE`. No old Telegram-channel promotion observed. See `docs/autopilot/gui-clients.md`, `worktrees.md`, `codex-cli.md`, `optimization.md`, `model-routing.md`.

## Current presentation and GitHub upstream status (2026-10-25)

- User noticed earlier README images still displayed inherited original branding. Fixed the *actual dashboard template*, not just screenshot names: removed the embedded old PNG logo, replaced both headers (including error state) with text-only \`Autopilot / 2.3 DEV\`. Removed the two inherited README logo PNG assets and header references.
- Generated six fresh, actual Chrome captures from the updated Dashboard 3.0 implementation and the existing synthetic CI fixture: wide, narrow and an enlarged crop emphasizing model/effort selection, token reports and worktree state, for EN and RU galleries. They are clearly labeled synthetic demonstrations, not claims of a successful real user deployment. Confirm screenshot build, visual review, README links, smoke CI on \`main\`.
- The GitHub API explicitly reports \`fork: true\`, \`parent: nick-vels/skills\` for \`mrAibo/Autopilot\`. GitHub's “This branch is N commits ahead of ...” is a **fork network comparison**, not installed Autopilot version or incorrect active code. Rebranding cannot change GitHub fork metadata. GitHub supports **Settings → General → Danger Zone → Leave fork network** for eligible public forks; it is irreversible and can lose PR/issues/comments/stars/fork metadata. **Do not detach or recreate without explicit informed consent**. Keep original MIT copyright and appropriate \`Inspired by\` reference even if later detached.
- Owner confirmed the Autopilot skill appears in graphical Codex. Native child agent model/effort and working directory still require separate GUI execution validation; do not conflate skill discovery with full runtime verification.

## Prioritized next steps

**P0 — GUI native execution:** In *Codex graphical application* run a disposable strict isolated ticket with approved model/effort and verify actual child-agent identity, effective cwd, tool approvals and commit/test evidence. Repeat separately for an actual **Claude Code** host (not a generic Claude chat). Host GUI success cannot be inferred from a CLI smoke; if model/effort cannot be confirmed, fall back to sequential single-agent or block the strict spawn.

**P0 — orchestrated lifecycle:** Implement a host-side execution/controller loop that consumes `ap.py schedule` plan, validates approval, launches bounded workers, handles cancellation/crash, independently verifies trusted test suites, finalizes/lands exactly once and records results. Keep fail-closed budget/sandbox boundaries. Validate with at least two independent tasks and a recoverable failure.

**P1 — broader verification and costs:** Extend trusted tests beyond one baseline-tracked Python unittest module (e.g. pytest, JS/TS) without executing arbitrary unapproved commands. Make evidence tamper-resistant and verify ignored-file handling. Import provider usage reliably, price with verified versioned data, benchmark cost per **accepted** task. Compare `lean` vs `off` and 2.2 vs 2.3 under matched conditions; no speculative savings.

**P2 — release qualification:** Reconcile GUI/runtime capability checks, installer/provenance, documentation, performance and security review. Only then consider changing `2.3.0-dev` to stable `2.3.0` and tagging a release.

## New-session resume instruction

> Продолжи проект Autopilot 2.3 из GitHub `mrAibo/Autopilot`, ветка **`main`**. PR #1 уже squash-merged (`00600107`); версия пока `2.3.0-dev`, без release tag. Прочитай актуальные `STATUS.md`, `бриф.md` и `docs/autopilot/{gui-clients,model-routing,worktrees,codex-cli,optimization}.md`. Проверь HEAD/CI, локальный Windows checkout, Junction-навыки и продолжай приоритеты P0 без нового перепланирования. Сохраняй STATUS.md после каждого этапа, не объявляй GUI E2E или стабильный релиз без настоящих проверок.

**Local Windows:** connected device `Aibo`, device ID `c8955f46-4ed5-4b7e-aa56-cecf1f98e21d`; repo `C:\Users\crown\Downloads\Projects\Autopilot`; Python `py -3.13`; Codex npm binary in `%APPDATA%\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`. GitHub account `mrAibo` connected. Disposable synthetic fixture has released T01; do not repeat paid calls there.

**Hot code:** `skills/autopilot/tools/{ap,worktrees,codex_dispatch,test_evidence,model_router,agent_profiles,codex_capabilities,scheduler}.py`; `tests/{test_ap,test_worktrees,test_codex_dispatch,test_test_evidence}.py`. Standard test: `python -m unittest discover -s tests -q`. Maintain LICENSE and one-skill-directory Junctions.
