# Autopilot 2.3: Codex GUI, Codex CLI and Claude Code

Autopilot is a **skill and project-state protocol**, not a command-line-only application. The same `SKILL.md`, phase files, `ap.py` state, dashboard and verification gates should be usable by both the desktop/GUI host and command-line host.

## Read-only runtime qualification, 2026-10-26 (not GUI E2E)

The connected Windows host `Aibo` was inspected without invoking an AI
model or changing host installations. The repository was clean at
`main` commit `be1833b` before this qualification. `codex --version`
reports `codex-cli 0.165.0-alpha.1`; `codex features list` reports
`multi_agent` stable/enabled but `multi_agent_v2` stable/**disabled**.
`codex exec --help` advertises `--model`, `--sandbox`, `--cd` and
`--json`. These are CLI metadata and do **not** reverse the actual
graphical Codex 2026-10-25 named-agent negative test or verify native child
profile/model/effort/cwd.

No `claude` / `claude-code` command was found on PATH, and known user
`npm` and native install locations and global npm package list did not
show a Claude Code CLI installation. The general Claude desktop application,
if present, must not be treated as the Claude Code agent runner. No native
Claude Code subagent E2E was possible during this read-only qualification.

An R03 fail-open condition was found and repaired in the **optional**
Claude Code `PreToolUse` guard: an existing but unreadable, malformed,
redirected or structurally empty Autopilot `state.js` previously looked
equivalent to no active strict run, which could allow a generic `Agent` /
`Task` launch. Now malformed existing state denies agent dispatch; a
project without `state.js` or an explicitly non-strict/finished valid
run keeps its usual behavior. Non-agent tool calls are not blocked.
Negative Python tests and OS-process stdin/exit-code tests use synthetic
temporary project state, not an authenticated Claude process. **This is
guard logic verification, not proof that Claude Code has installed or is
enforcing the hook in an active host session.**

## Dashboard 3.1: real browser viewport qualification

The dedicated smoke test `tools/check-dashboard-browser.py` opens the
**actual** standalone Dashboard in headless Chrome/Edge with synthetic state.
It verifies desktop (~1424 CSS px), narrow Claude/Codex split panel (**460
CSS px**) and phone-size (**390 CSS px**) in RU/EN and light/dark combinations.

Headless Chrome enforces a minimum top-level viewport width of roughly 500
CSS px. Older `--window-size=460,...` snapshots were therefore **not
actually taken at 460 CSS px**. The browser smoke now uses a same-origin,
fixed-width iframe for 460/390 widths and asserts the frame's *measured*
`window.innerWidth` and `documentElement.clientWidth`, not its CLI
window-size argument. The probe also checks scroll widths, main sections,
model/recovery content, navigation-rail breakpoint, labeled buttons and
small-label foreground contrast against inset panels (at least 4.5:1).
A default screenshot artifact stores wide/narrow/mobile/mobile-dark captures
for the Linux CI run; optional `AUTOPILOT_SCREENSHOT_DIR` saves local PNGs.

The four checked cases are desktop RU/light, 460 RU/dark, 390 EN/light and
390 EN/dark. These **synthetic browser checks do not prove** real GUI host
state updates, screen-reader reading order, keyboard interaction end-to-end
or complete WCAG compliance. They run without models, external scripts, a
development server, npm installs or additional Python dependencies.

## Supported GUI-to-CLI alternative (owner-approved direction)

When the tested GUI cannot select its native named agent, an authorized
Codex GUI workflow may use local terminal tools to invoke
`.autopilot/gui_bridge.py --root . --ticket NN` for a **read-only**
preview. **Actual `--execute --approve-ticket NN` is disabled by the
fail-closed spend guard** until real provider-side per-call enforcement can
be independently verified. The historical research prototype has a pinned
CLI worker and anti-replay receipt, but does not currently launch a model
or accept a task. See [gui-cli-bridge.md](gui-cli-bridge.md) and
[spend-guard.md](spend-guard.md).

The terminal tool, explicit invocation and local filesystem access
must be available to the GUI host; they have not yet been independently
verified together in a real GUI session. Never claim native GUI
subagents or authenticated human consent from a CLI flag alone.

## Support matrix

| Host | Skill workflow | Model-aware dispatch | Validation status |
|---|---|---|---|
| Codex desktop app / graphical interface | Shared Autopilot skill instructions, project files and dashboard | Native named subagents **not available in the user-tested GUI session**; safe host-side fallback: explicitly selected `--sequential-host` with one task and trusted Git/tests; real pinned CLI worker execution currently blocked | **GUI test performed 2026-10-25: fail-closed, no named child**; full GUI end-to-end still unverified |
| Codex CLI | Same skill instructions and project files | Explicit `codex exec` model/effort process via `codex_dispatch.py`, with isolated worktree and JSON usage | CLI 0.165.0-alpha.1 login, real Luna Low inference and a disposable code-edit / host-tested / accepted worktree E2E verified on Windows; GUI host remains unverified |
| Claude Code (terminal or supported graphical host) | Same skill instructions loaded from `.claude/skills/` | Native pinned `.claude/agents/*.md`, model/effort fields and optional strict `PreToolUse` guard; see [Claude Code qualification](claude-code.md) | Offline profile + guard tests only; **native CLI/GUI behavior and subscription billing unverified on Aibo** |
| Claude general chat app without code execution / filesystem tools | Can read project docs if attached, but cannot run the local workflow | No supported local dispatch guarantee | **Not equivalent to Claude Code** |

**Do not claim one CLI smoke validates a graphical host.** GUI applications may have their own model availability, tool restrictions and approval flows. Account catalog entries do not attest a model used in a given session.

## Existing installations: no second copies

As approved by the owner on 2026-10-25, the old global Autopilot 2.2 directory was removed. Three global skill discovery paths now point by Windows Junction **directly to the one development checkout** `C:\Users\crown\Downloads\Projects\Autopilot\skills\autopilot`: `C:\Users\crown\.agents\skills\autopilot`, `C:\Users\crown\.claude\skills\autopilot`, and `C:\Users\crown\.codex\skills\autopilot`. After the scoped release update, each Junction exposes the same real `SKILL.md` with `metadata.version: "2.3.0"` (previously `2.3.0-dev`). The obsolete global installer lock entry for `nick-vels/skills` was removed without altering the other skills. This proves working filesystem links, **not** live GUI discovery; restart a host session and verify.

The `mrAibo/Autopilot` repository has two tracked Git symlinks:
- `.agents/skills/autopilot` → `../../skills/autopilot`
- `.claude/skills/autopilot` → `../../.agents/skills/autopilot`

When Git is checked out on Windows with `core.symlinks=false`, the two tracked **repository-local** skill links can be plain-text placeholders rather than loadable skill directories. The separately verified **global Junctions** above bypass that issue without any copied skill files; the disposable GUI test workspace also uses Junctions to the same source.

For this development checkout, first check the repository is clean, then use `git -C C:\Users\crown\Downloads\Projects\Autopilot pull --ff-only` to update the working branch. The global Junctions expose changes immediately to new host sessions. Do **not** run `npx skills update autopilot -g` on this developer-linked preview: it may replace it with the published main-branch release. For a separate clean installation, use the supported `npx skills add mrAibo/Autopilot` workflow after the release has been merged. The global Junctions on Aibo should remain untouched.

## Owner's actual graphical Codex named-agent test (2026-10-25)

The owner opened the disposable Codex project and issued the exact read-only
`autopilot-explorer-smoke` request from a new **graphical Codex session**.
Screenshot evidence shows the GUI responding (in Russian) that its subagent
creation interface cannot select the named profile from `.codex/agents/`.
The on-screen verification table confirms: child agent **No**, profile
assigned **No**, model confirmed **No**, reasoning effort confirmed **No**,
`EXPECTED_PROBE_WORD` **not obtained**. Codex said it did not use a
substitute agent and did not change files. The visible turn duration was
approximately 23 seconds.

**Interpretation:** This is a genuine GUI *negative capability test*, not
just a CLI probe. It confirms strict named-agent dispatch is unavailable
in this particular session. It does **not** establish that future Codex
versions, different session capability flags or all users lack custom agent
selection. The upstream native tool schemas expose `agent_type`, model and
reasoning effort conditionally; investigate runtime flags/permissions and
version differences before retrying. Autopilot must continue to fail closed
and must not silently substitute a generic inheriting parent-model child.

**Safe operational option:** Use Codex GUI as the interface, then explicitly
delegate ticket execution through the separately validated `codex_dispatch.py`
CLI worker with approved model/Effort, sandboxed worktree, host-side test
evidence, Git integration and budget ledger; or use [the verified *host* sequential state/test mode](sequential-host.md).
Actual GUI model selection and billing still require separate host proof.
Do not call this verified native GUI subagent mode. Claude Code remains a
separate unverified host and needs its own authenticated runtime test.

## Actual Windows Codex native-runtime probe

The owner's Codex Desktop-bundled binary is 0.164.0-alpha.11.1; the
separately installed CLI is 0.165.0-alpha.1. Both catalog queries advertise
nine account-visible models. GPT-6 Sol/Luna report multi_agent_version=v2;
GPT-5.6 Luna reports v1. These are catalog claims, not executed sessions.

A clean synthetic, read-only Git fixture with one exact
.codex/agents/autopilot-explorer-smoke.toml named profile pinned to GPT-6
Luna / Low was tested using the GUI's **bundled executable in CLI mode**.
Parent GPT-6 Sol / Low replied NAMED_AGENT_UNAVAILABLE without a native
child event despite exit 0 (18,729 input, 12,928 cached, 78 output tokens;
6.3 seconds). The GPT-5.6 Luna / Low V1 parent likewise spawned no
child (16,838 input, 11,392 cached, 54 output tokens; 4.7 seconds).
Neither test modified any file or used a real project. The disposable
fixture lives under user TEMP/autopilot-native-gui-agent-smoke-20261025.

The new codex_native_agents.py validates native catalog and profile pins
and fails closed if model or effort is unavailable, V2 cannot choose a
custom agent, or native child execution cannot be independently attested.
Caller-supplied JSONL is only diagnostic, NOT authorization. Prefer the explicitly selected [sequential host mode](sequential-host.md)
with Git-isolated task/test acceptance; the sandboxed CLI dispatcher is
currently **blocked for real model calls** by the spend guard.
These read-only EXE tests **did not operate the graphical Codex window**;
GUI native subagents remain unverified. Claude Desktop is present, but no
Claude Code CLI command was found, so Claude Code GUI/CLI is also unverified.

## Capability discovery

On the current Windows machine, resolved `codex debug models` (not `--bundled`) advertises the **actual CLI account-visible model IDs and Effort values**. The project's `codex_capabilities.py` can export these:

```powershell
py -3.13 .autopilot/codex_capabilities.py --root . --write
```

Only after `ap.py init` created `.autopilot`. This writes `.autopilot/model-capabilities.json` and blocks a conflicting existing provider unless explicitly refreshed. It makes no model calls. **This catalog is the CLI's**; desktop users should verify the selected model with their GUI host too. It does not certify actual inference model IDs or charges.

## Refresh already-generated project Dashboards

Project Dashboards are **copies** of the skill template, not Junctions. The installed skill can be version 2.3 while an existing project still serves 2.2 HTML until explicitly refreshed. Use:

    py -3.13 C:\Users\crown\Downloads\Projects\Autopilot\skills\autopilot\tools\dashboard_upgrade.py --project C:\Users\crown\Downloads\Projects\WEG_HomeManager

The standalone upgrader requires a valid existing .autopilot/state.js, refuses mismatched project identity, backs up the old Dashboard under the user's temporary directory, and atomically replaces only the HTML while embedding the current snapshot. Reload the browser tab. It never changes an active application or task ledger. This was confirmed on the synthetic test suite and the real WEG_HomeManager local Dashboard (rev 41, two tickets) with a successful headless Chrome DOM read.

## Explicit single-session host fallback

A **new** run may choose [`--sequential-host`](sequential-host.md) when the named child is unsupported. Autopilot enforces exactly one in-progress/prepared task and independently re-runs unchanged baseline Python unittests before accepting Git changes; the Dashboard labels the mode and warns that GUI model/Effort are **not verified**. This does **not** enable blocked `gui_bridge --execute` nor prove native child-agent identity. The host must independently confirm which model is selected and whether its use is covered by the owner's subscription; otherwise stop any model work. This host/Git path is regression-tested in disposable repos only; real Codex GUI end-to-end remains unverified.

## Expected GUI user journey

1. Open the target project in the existing Codex/Claude Code graphical application.
2. Confirm the `autopilot` skill is visible (not a Windows text-file placeholder), then invoke `/autopilot` or the host-supported skill selector. Restart a session if the host caches skills.
3. Run project preflight. Select manual or strict execution modes; use the host's **own** model picker and approval flow.
4. Autopilot manages specification, tasks, scheduler, detached Git worktrees and dashboard through project files. The GUI agent executes the approved actions using its native tools.
5. Native named subagents must be discovered in the host session with the approved model/effort. If not, choose the explicit [`--sequential-host` workflow](sequential-host.md) only after reviewing host model/effort and subscription exposure; **never silently inherit a costly parent model or claim verified child dispatch**.
6. At acceptance, check actual tests, Git commits, requirements and G1–G4 gates. Persist `STATUS.md` and `PROGRESS.md`.

## Host-side lifecycle controller (not GUI agent dispatch)

`controller.py` implements a safe, bounded, operator-invoked transition loop
for a strict isolated Autopilot run. Read-only default; `--advance` applies
one Git/state/test step, never calls a model or accepts unverified evidence.
This gives both GUI hosts a shared file-driven workflow, but is not native
GUI child-agent dispatch. It is tested on two actual disposable Git worktrees,
including a red test followed by an independently verified correction.
See [controller.md](controller.md).

## Known blockers

- No completed end-to-end GUI test with Codex Desktop or Claude Code Desktop.
- No proven GUI enforcement of the exact pinned model/effort, native custom subagent creation or isolated `cwd` yet. The CLI adapter is a separate optional execution path, not the implementation of graphical integration.
- Global and disposable Windows Junction directories now point to the same 2.3-dev source and expose a real `SKILL.md`; still verify that *each graphical host actually discovers and loads* the new version after session restart.
- Need real Claude Code installation/tooling discovery and authenticated execution before marking Claude GUI support verified.

After release, a single supported installation/update path should make the skill discoverable to all installed compatible hosts, but the provider's GUI mechanisms and permissions remain the final authority.
