# Autopilot 2.3: Codex GUI, Codex CLI and Claude Code

Autopilot is a **skill and project-state protocol**, not a command-line-only application. The same `SKILL.md`, phase files, `ap.py` state, dashboard and verification gates should be usable by both the desktop/GUI host and command-line host.

## Support matrix

| Host | Skill workflow | Model-aware dispatch | Validation status |
|---|---|---|---|
| Codex desktop app / graphical interface | Shared Autopilot skill instructions, project files and dashboard | Native Codex subagent definitions (`.codex/agents/*.toml`) and host UI model picker. CLI adapter **not required** | **GUI end-to-end not yet validated** |
| Codex CLI | Same skill instructions and project files | Explicit `codex exec` model/effort process via `codex_dispatch.py`, with isolated worktree and JSON usage | CLI 0.165.0-alpha.1 login, real Luna Low inference and a disposable code-edit / host-tested / accepted worktree E2E verified on Windows; GUI host remains unverified |
| Claude Code (terminal or supported graphical host) | Same skill instructions loaded from `.claude/skills/` | Native pinned `.claude/agents/*.md` with optional `PreToolUse` guard | Synthetic tests only; **actual GUI/CLI behavior unverified** |
| Claude general chat app without code execution / filesystem tools | Can read project docs if attached, but cannot run the local workflow | No supported local dispatch guarantee | **Not equivalent to Claude Code** |

**Do not claim one CLI smoke validates a graphical host.** GUI applications may have their own model availability, tool restrictions and approval flows. Account catalog entries do not attest a model used in a given session.

## Existing installations: no second copies

As approved by the owner on 2026-10-25, the old global Autopilot 2.2 directory was removed. Three global skill discovery paths now point by Windows Junction **directly to the one development checkout** `C:\Users\crown\Downloads\Projects\Autopilot\skills\autopilot`: `C:\Users\crown\.agents\skills\autopilot`, `C:\Users\crown\.claude\skills\autopilot`, and `C:\Users\crown\.codex\skills\autopilot`. Each Junction exposes a real `SKILL.md` with `metadata.version: "2.3.0-dev"`. The obsolete global installer lock entry for `nick-vels/skills` was removed without altering the other skills. This proves working filesystem links, **not** live GUI discovery; restart a host session and verify.

The `mrAibo/Autopilot` repository has two tracked Git symlinks:
- `.agents/skills/autopilot` → `../../skills/autopilot`
- `.claude/skills/autopilot` → `../../.agents/skills/autopilot`

When Git is checked out on Windows with `core.symlinks=false`, the two tracked **repository-local** skill links can be plain-text placeholders rather than loadable skill directories. The separately verified **global Junctions** above bypass that issue without any copied skill files; the disposable GUI test workspace also uses Junctions to the same source.

For this development checkout, first check the repository is clean, then use `git -C C:\Users\crown\Downloads\Projects\Autopilot pull --ff-only` to update the working branch. The global Junctions expose changes immediately to new host sessions. Do **not** run `npx skills update autopilot -g` on this developer-linked preview: it may replace it with the published main-branch release. After 2.3 is merged and released, use the supported `npx skills add mrAibo/Autopilot` workflow if preferred.

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
Caller-supplied JSONL is only diagnostic, NOT authorization. Prefer
sequential GUI execution or verified pinned, sandboxed CLI dispatcher.
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

## Expected GUI user journey

1. Open the target project in the existing Codex/Claude Code graphical application.
2. Confirm the `autopilot` skill is visible (not a Windows text-file placeholder), then invoke `/autopilot` or the host-supported skill selector. Restart a session if the host caches skills.
3. Run project preflight. Select manual or strict execution modes; use the host's **own** model picker and approval flow.
4. Autopilot manages specification, tasks, scheduler, detached Git worktrees and dashboard through project files. The GUI agent executes the approved actions using its native tools.
5. Native named subagents must be discovered in the host session with the approved model/effort. If not, use single-agent sequential mode; **never silently inherit a costly parent model**.
6. At acceptance, check actual tests, Git commits, requirements and G1–G4 gates. Persist `STATUS.md` and `PROGRESS.md`.

## Known blockers

- No completed end-to-end GUI test with Codex Desktop or Claude Code Desktop.
- No proven GUI enforcement of the exact pinned model/effort, native custom subagent creation or isolated `cwd` yet. The CLI adapter is a separate optional execution path, not the implementation of graphical integration.
- Global and disposable Windows Junction directories now point to the same 2.3-dev source and expose a real `SKILL.md`; still verify that *each graphical host actually discovers and loads* the new version after session restart.
- Need real Claude Code installation/tooling discovery and authenticated execution before marking Claude GUI support verified.

After release, a single supported installation/update path should make the skill discoverable to all installed compatible hosts, but the provider's GUI mechanisms and permissions remain the final authority.
