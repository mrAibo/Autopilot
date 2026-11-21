# Phase 0 — Mode and depth (digest)

Working digest of `phases/0-modes.md`. **Read the full text only if something below is not enough** (the opening block, the trigger words, the mid-run rules).

- `audit` as the first word is not a mode: it routes to `phases/audit.md`.
- After `/autopilot`: **mode** (`full` · `semi` default · `interview` · `manual`), **depth** (`strict` · normal default · `deep`), everything else is the brief. Bare words, any order, both optional.
- Gates by mode: full none · semi questions on genuine forks only · interview all questions · manual the same + `ap.py ask spec` and `ap.py ask plan` (explicit «ок», chat or dashboard button, `ap.py await`). `interview` asks about the product, `manual` adds approval of the two process artifacts.
- Ambiguity → semi. A mode word contradicting the sentence wins; two mode words → ask which, one line. Switch mid-run applies from the next phase, one line of acknowledgement.
- Instructions in the brief (stack, budget, «без базы данных», deadline) are requirements in the manifest; they never replace a phase.
- **No mode removes the manifest gates or the safety gates.** Deploy, publish, pay, message a third party, delete data, rewrite history → a question in all four modes, `ap.py ask action --note "…"` before it goes out.
- Depth: `strict` — deepen only what a requirement cannot work without, no `A##`; normal — by judgement, `A##` allowed with a parent; `deep` — every dimension, `A##` encouraged. `strict` still handles errors and empty states. The adversarial pass (`2-adversarial.md`) runs at `deep` in every mode and in interview/manual at every depth. Rules per level: `3-spec.md`.
- **Opening block, once, before Phase 1:** mode · depth · dashboard address (no server → `.autopilot/dashboard.html`) · memory file · the `↑` lines exactly as `ap.py` printed them (newer version; long chat) — a hint, never a question — and the five switch phrases («полный автомат», «режим интервью», «ручной режим», «строго по брифу» / «проработай глубоко», «лимит N токенов»). Never repeated; a mid-run switch gets one line.
