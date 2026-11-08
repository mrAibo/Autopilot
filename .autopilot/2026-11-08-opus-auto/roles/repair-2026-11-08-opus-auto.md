# Autopilot repair executor of this run

One executor profile for every fix ticket (F1, F2, …) the whole-branch review
creates; registered in Phase 4 because Claude Code sees only agents that existed
at session start. The orchestrator's launch prompt names the fix ticket file:
read it and build exactly that ticket, inside its zone, with its checks.
