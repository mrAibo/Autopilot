# Autopilot role agents of this run

One profile per role, shared by the whole run. The orchestrator's launch prompt
names the task, the files to read and the limits; follow it.

- reviewer: point review, repair re-review and whole-branch review. No edits.
- acceptance: blind acceptance against the brief files. No edits.
- explorer: read-only reading tasks (coverage reader, memory and ADR drafts);
  return text, write nothing.
