---
name: plan
description: Plan a task: run the planner to produce ordered steps with acceptance criteria and a builder level per step. Use when a goal is ready to be broken into buildable steps.
argument-hint: [L1..L3] <handoff.md | goal>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Read, Write, Grep, Glob
---
Arguments: `$ARGUMENTS`

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section planner.
3. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner <level> <handoff.md>` from the project root.
4. On success the script prints the result path. Read it, then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <result path>` and report its outcome with the key lines in a few bullets plus the path. A lint refusal (exit 1) is a plan defect: report it to the user as one, with the spans it names. On a run failure, report the error and the log path.

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
