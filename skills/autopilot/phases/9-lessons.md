# Phase 9 — lessons after `finish`

`ap.py finish` refreshes `.autopilot/profile.md` and prints a hint. One **light** agent (`autopilot-explorer`, read-only profile; cheapest model) turns the run's trouble into at most 5 lessons.

1. `ap.py lessons candidates [--max 5]` prints the raw material: concerns, tickets with retries or repairs, blockers closed as unconfirmed.
2. The agent reads that list and `.autopilot/lessons.md`, and writes each lesson as one short line of advice for the next executor: what to do or avoid, no names of people, no secrets, no absolute paths.
3. The orchestrator records them: `ap.py lessons add "…" "…"`. A refused line (secret, absolute path outside the project, a line break, or one already recorded or deleted before) is reported, not retried.
4. `ap.py lessons check` must exit 0.

The file is plain text in `.autopilot/`; the user reads it and deletes a line (`ap.py lessons drop N`, 1 is the newest, or by hand — a deleted lesson does not come back). The next `init` says how many lines there are; executors read the newest 2 KB (`ap.py lessons show`) and `profile.md`. Nothing is written outside `.autopilot/`.
