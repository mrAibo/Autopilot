# Autopilot 2.3 — handoff to a new ChatGPT/Codex conversation

> **Current product-only scope (2026-10-27):** This handoff concerns **Autopilot**, not any other application repository. The separate historical cross-project report `HANDOFF_NEXT_CLIENT_2026-10-26.md` is **not the active development plan**. Current product work: [read-only repository preflight](docs/autopilot/repository-preflight.md), generic host test-verification contracts, model-only advisory effort, safe run continuity. Preserve historical evidence in [STATUS.md](STATUS.md), but do not import external project tickets or prioritization. Published `v2.3.0` stays unchanged; check latest main SHA/CI.

**Date:** 2026-10-26 (Europe/Berlin)
**Product stage:** [`v2.3.0`](https://github.com/mrAibo/Autopilot/releases/tag/v2.3.0) **officially published**, Codex limited sequential-host support. Tag points to product commit `90cf259b8919e512d22b518e9fe8c9c45b1744a5` (PR #32, full release PR CI 4/4 green and local Python 316/316). Native Codex GUI named-agent/model/Effort not included; Claude Code profile/guard offline-tested only, pending separate subscription and live CLI.
**Repository:** https://github.com/mrAibo/Autopilot
**Windows host:** Aibo
**Checkout:** `C:\Users\crown\Downloads\Projects\Autopilot`
**Branch:** `main`, clean and tracking `origin/main` at handoff preparation.
**Last fully tested pre-handoff HEAD:** `ec740a7c7555d09e62f3f6039700b3fdf3ea0f64`; a documentation-only handoff commit may advance HEAD. Always check `git rev-parse HEAD` and `git status --short --branch` first.
**Final pre-handoff CI:** [Actions #40352034156](https://github.com/mrAibo/Autopilot/actions/runs/40352034156): **4/4 succeeded** (Ubuntu and Windows, Python 3.11 and 3.13) on exact SHA `ec740a7`. Local Windows Python 3.13 **308/308** passed.

## 1. Normative reading order

1. [`STATUS.md`](STATUS.md) — full milestone history, owner restrictions, latest checkpoints, known obstacles, prior smoke evidence.
2. [`brief.md`](brief.md) — original product goals and requirements.
3. [`skills/autopilot/SKILL.md`](skills/autopilot/SKILL.md) and phases [4 Plan](skills/autopilot/phases/4-plan.md), [5 Subagents](skills/autopilot/phases/5-subagents.md), [0 Resume](skills/autopilot/phases/0-resume.md).
4. [Model routing](docs/autopilot/model-routing.md), [sequential host fallback](docs/autopilot/sequential-host.md), [R01–R06 release-readiness matrix](docs/autopilot/release-readiness.md), [GUI clients](docs/autopilot/gui-clients.md), [spend guard](docs/autopilot/spend-guard.md).
5. [`CHANGELOG.md`](CHANGELOG.md), `tests/test_ap.py`, `tests/test_model_router.py`, `tests/test_agent_profiles.py`, `tests/test_documentation_locales.py`.

Do **not** rebuild or re-plan the project from scratch. Use the clean existing `main` checkout; create a focused feature branch only for a concrete new change, then run local validation, PR CI, squash merge and record an updated checkpoint.

## 2. Most recent completed feature — true automatic per-ticket model + Effort selection

**Merged [PR #27](https://github.com/mrAibo/Autopilot/pull/27)**, squash `4be851dca5685c5e6e98e19e00557c576aadc8bc`; STATUS-only checkpoint `ec740a7`.

The owner noticed that earlier documentation *said* every task's AI model and reasoning Effort were determined automatically **during planning**, but the actual code still required separate manual `model_router.py` and `ticket NN route` invocations for every ticket. This gap is now corrected:

- In an initialized **application project**, Phase 4 publishes tickets, checks plan, then runs `py -3.13 .autopilot/ap.py plan-models --provider openai` (or `anthropic`). This **one** zero-inference operation independently scores every published pending ticket on six factors (algorithm, coupling, uncertainty, context, tests, risk), chooses cheap/balanced/strong, and proposes exact model + reasoning Effort for each. The proposals appear under `plannedRouting` and in the Dashboard as **plan only**.
- Without genuinely verified host capabilities, proposals remain `status=blocked` / **advisory**; neither named profiles nor runtime model execution are claimed.
- Only if a host can **actually attest supported model/Effort pairs** may the operator use `py -3.13 .autopilot/ap.py plan-models --provider openai --capabilities .autopilot/model-capabilities.json --apply`. The controller checks the **whole batch** (all ticket fingerprints, models, efforts, optional policy and collisions) before writing pinned native profiles and routes. Unsupported strong/high-risk choices or a pre-existing incompatible profile **block the entire batch**; there is no silent model downgrade.
- Existing `ticket NN route` remains for explicit overrides. The `--sequential-host` mode intentionally **rejects** native profile batching because it creates no subagent.
- Restricted expensive models (Astra/Fable/Opus) are **not** automatically dispatched. Model catalog names in the policy are examples of configured choices, **not proof of actual app support or subscription coverage**.
- EN/RU/DE READMEs, Phase 4/5, model-routing guide, Dashboard advisory panel and headless Chrome test updated.
- Evidence: **5 new disposable-Git negative/integration tests**, one new documentation regression; **308/308** local tests; [PR #27 CI #40350716786](https://github.com/mrAibo/Autopilot/actions/runs/40350716786) **4/4**, [final main CI #40352034156](https://github.com/mrAibo/Autopilot/actions/runs/40352034156) **4/4**.

**Crucial distinction:** recommended model + Effort in a plan is not confirmation that Codex GUI or Claude Code actually spawned the specified named agent or used/billed the selected model.

## 3. Prior tangible R03 integration result — real file edit + host acceptance

**Merged [PR #26](https://github.com/mrAibo/Autopilot/pull/26)**, squash `9968f45`: explicit `init --sequential-host` fallback. It permits **one** prepared/active ticket, Git worktree isolation and independent tests, rejects fake `N/0` test claims, changed code after verification, parallel starts and fake native routes; **does not** spawn a model or prove GUI model/Effort.

The owner created a **ChatGPT project** pointing at temporary Windows fixture `%TEMP%\Autopilot_GUI_R03_Smoke_20261026` and prompted it to edit only `.autopilot\worktrees\T01\src\core\calc.py` (`a - b` → `a + b`).
- The GUI agent *reported* reading `GUI_TEST_INSTRUCTIONS.md` and `tickets\01-calc.md`, changing one file and not determining effective GUI model or reasoning Effort.
- Trusted remote Windows host **independently confirmed** the exact one-file Git diff and unchanged tracked `test_calc.py`.
- Pre-edit host `verify` had appropriately failed; post-edit `worktree 01 verify --suite test_calc.py` passed **1/0**, recorded verified test evidence; host completed `finalize → land → ticket 01 done → release`.
- Test fixture integrated commit: `283c662b57a20562ee59996c891cc3e6b9b33253`. T01 status `done`, worktree `released`; real Autopilot checkout unaffected.
- **This is ChatGPT-project file editing, not Codex GUI native named-subagent proof.** Actual model/Effort/subscription accounting was *not* independently available. Do not repeat or claim it is Codex GUI E2E.

## 4. Other work already merged / stable design limits

- [PR #23](https://github.com/mrAibo/Autopilot/pull/23): R01 stale plan acceptance closure via G3 plan contract, and related invalidation.
- [PR #24](https://github.com/mrAibo/Autopilot/pull/24): durable blocking review B## ledger, prevent false `ticket done` / `finish`.
- [PR #25](https://github.com/mrAibo/Autopilot/pull/25): evidence-backed R01–R06 stable-release **NO-GO** matrix, corrected paid GUI→CLI fallback misinformation.
- [PR #26](https://github.com/mrAibo/Autopilot/pull/26): `--sequential-host` one-ticket verified safe protocol.
- [PR #27](https://github.com/mrAibo/Autopilot/pull/27): **automatic planning-stage model/Effort for all tickets** and proper UI/docs.

Code/test acceptance, real browser smoke, model-policy planning, native agent profile *file* creation and real named-agent *execution* are different evidence levels. Do not treat test fixtures or mock profile files as real subagent invocation or trusted provider token records.

## 5. Remaining blockers and next pragmatic work

**Priority P0 — native host runtime proof:** On Aibo, last observed standalone Codex CLI `0.165.0-alpha.1` and GUI-bundled Codex CLI `0.164.0-alpha.11.1` both advertise `multi_agent=true`, `multi_agent_v2=false`. An actual earlier named custom subagent probe in Codex GUI was negative. Claude **Desktop** was present but genuine Claude **Code** CLI (`claude`/`claude-code`) absent. Thus **no verified named subagent identity + enforced actual model/Effort/cwd**. First perform **read-only** current host capability discovery; do not retry a known-negative or token-intensive agent test unless a meaningful capability/version change justifies it.

**Priority P1 — user-facing plan UX and trust boundary:** Inspect applied vs advisory model/Effort rows in an actual GUI session when supported; present a visible **blocked** reason if the model catalog is missing, and avoid claiming model selection was applied. Consider test fixtures around recovery/replanning, task edits, profile collision and batch rollback as future hardening. Keep `--sequential-host` available for a real host-owned safe one-session workflow; it must not claim that it runs a named agent or pins the current GUI model.

**Priority P1 — broader trusted tests:** Worktree verification currently supports unchanged baseline-tracked Python unittest and has limited isolation against ignored non-Python code/runtime inputs. Extending testing to other languages/frameworks needs a separately reviewed command allowlist without arbitrary shell execution. No formal cross-platform crash isolation guarantee for Linux/macOS.

**Priority P2 — release decisions:** R01/R02 mostly code-verified, R04 browser smoke verified in synthetic pages, R05 docs/attribution updated, R06 host-only matched synthetic benchmark. No audited live provider spend/cost or matched model A/B savings. No stable `2.3.0` until runtime/cost proof, owner sign-off and release gates satisfied.

## 6. Non-negotiable user constraints

- **Only AI model requests included in the existing ChatGPT/Codex subscription.** **No separately billed tokens, API credits, purchases, keys, or external pay-as-you-go calls.** Older user notes may say paid tokens are okay; **the latest restrictive decision controls**.
- `gui_bridge.py --execute` and `codex_dispatch.py --execute` are **intentionally blocked** by `spend_guard`. ChatGPT sign-in, soft token budget and an owner's general approval do **not** supply a hard provider-side per-call cost cap. A previous CLI worker consumed **53,187 input tokens** despite a soft 2,000-token target; never silently bypass this guard.
- Preserve existing progress, rights, license attribution and EN/RU/DE documentation. No faked named subagents or model/Effort attestations. Avoid needlessly heavy orchestrators for trivial tasks.
- Remote Desktop Commander can access the authorized Aibo filesystem/terminal. Do **not** assume it supplies interactive mouse/keyboard control of Codex GUI; a separate Computer Use / Work session requires actual supported user authorization.
- No background work implied merely by this handoff. Continue only from active user request in the new chat.

## 7. Commands for next session

```powershell
cd C:\Users\crown\Downloads\Projects\Autopilot
git status --short --branch
git rev-parse HEAD
git log -5 --oneline
py -3.13 -m unittest discover -s tests -q
```

For **already initialized separate application projects** in Phase 4 (not from the Autopilot source repo root), after `tickets` and `check-plan`:

```powershell
py -3.13 .autopilot\ap.py plan-models --provider openai
# Only if native host model/Effort enforcement is independently verified:
py -3.13 .autopilot\ap.py plan-models --provider openai --capabilities .autopilot\model-capabilities.json --apply
```

For new chats, paste:

> Продолжи развитие Autopilot 2.3 из `C:\Users\crown\Downloads\Projects\Autopilot`. Прочитай `HANDOFF.md`, `STATUS.md`, `brief.md`, `skills/autopilot/SKILL.md`, `docs/autopilot/model-routing.md` и `docs/autopilot/release-readiness.md`. Проверь реальный `main` HEAD, чистоту Git и последний CI, затем **продолжай текущий этап без повторного планирования**. Последний выполненный этап — PR #27: автоматический расчёт модели и reasoning Effort для каждого таска на стадии планирования, с честным разделением advisory, pinned и actual runtime. Приоритет — безопасно подтвердить возможности настоящих GUI-именованных агентов или явно сохранить их как неподдерживаемые; не имитируй model/Effort/child. Только запросы в пределах подписки, без платных API/кредитов. Сделай конкретные изменения/тесты в отдельной ветке, PR, CI, обнови `STATUS.md`. Не выпускай stable `2.3.0` без подлинной проверки.
