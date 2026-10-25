# Autopilot 2.3: Codex GUI, Codex CLI and Claude Code

Autopilot is a **skill and project-state protocol**, not a command-line-only application. The same `SKILL.md`, phase files, `ap.py` state, dashboard and verification gates should be usable by both the desktop/GUI host and command-line host.

## Support matrix

| Host | Skill workflow | Model-aware dispatch | Validation status |
|---|---|---|---|
| Codex desktop app / graphical interface | Shared Autopilot skill instructions, project files and dashboard | Native Codex subagent definitions (`.codex/agents/*.toml`) and host UI model picker. CLI adapter **not required** | **GUI end-to-end not yet validated** |
| Codex CLI | Same skill instructions and project files | Explicit `codex exec` model/effort process via `codex_dispatch.py`, with isolated worktree and JSON usage | CLI 0.165.0-alpha.1 login, resolved catalog and read-only Luna Low smoke verified on Windows, 2026-10-25; full ticket dispatch still pending |
| Claude Code (terminal or supported graphical host) | Same skill instructions loaded from `.claude/skills/` | Native pinned `.claude/agents/*.md` with optional `PreToolUse` guard | Synthetic tests only; **actual GUI/CLI behavior unverified** |
| Claude general chat app without code execution / filesystem tools | Can read project docs if attached, but cannot run the local workflow | No supported local dispatch guarantee | **Not equivalent to Claude Code** |

**Do not claim one CLI smoke validates a graphical host.** GUI applications may have their own model availability, tool restrictions and approval flows. Account catalog entries do not attest a model used in a given session.

## Existing installations: no second copies

On the owner's Windows machine, `C:\Users\crown\.agents\skills\autopilot` is the **existing global stable 2.2 installation** and `C:\Users\crown\.claude\skills\autopilot` points to it using a Junction. Do not overwrite it with this unfinished branch.

The `mrAibo/Autopilot` repository has two tracked Git symlinks:
- `.agents/skills/autopilot` → `../../skills/autopilot`
- `.claude/skills/autopilot` → `../../.agents/skills/autopilot`

When Git is checked out on Windows **with `core.symlinks=false`**, the links are represented as tiny plain-text files containing their link targets. Those **are not loadable skills**. Windows Developer Mode or authorized directory Junctions can resolve this for a disposable test workspace, but do not mutate tracked link files or change the global 2.2 installation as a side effect.

The best portable production path is to use the existing `npx skills add` workflow to register a released Autopilot skill with the GUI host, then start a fresh host session. Test branch access can instead be obtained through an isolated test workspace and an explicitly opted-in project-level link to the repository's `skills/autopilot` folder; this is not a second installation/copy.

## Capability discovery

On the current Windows machine, resolved `codex debug models` (not `--bundled`) advertises the **actual CLI account-visible model IDs and Effort values**. The project's `codex_capabilities.py` can export these:

```powershell
py -3.13 .autopilot/codex_capabilities.py --root . --write
```

Only after `ap.py init` created `.autopilot`. This writes `.autopilot/model-capabilities.json` and blocks a conflicting existing provider unless explicitly refreshed. It makes no model calls. **This catalog is the CLI's**; desktop users should verify the selected model with their GUI host too. It does not certify actual inference model IDs or charges.

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
- Need Windows symlink/Junction setup or installer release verification in a disposable test workspace to ensure the *same* skill activates in both GUI and CLI.
- Need real Claude Code installation/tooling discovery and authenticated execution before marking Claude GUI support verified.

After release, a single supported installation/update path should make the skill discoverable to all installed compatible hosts, but the provider's GUI mechanisms and permissions remain the final authority.
