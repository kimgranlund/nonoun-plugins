---
name: plan
description: "Plan a task: run the planner to produce ordered steps with acceptance criteria and a builder level per step. Use when a goal is ready to be broken into buildable steps."
argument-hint: "[L1..L3] <handoff.md | goal>"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, set `SDLC_ROUTING_REASON` to a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). The runner records the resolved model and effort separately. Read [run operations](../handoff-format/run-operations.md) for readiness and interrupted-attempt recovery.

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section planner.
3. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner <level> <handoff.md>` from the project root.
4. On success the script prints the result path. Read it, then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <result path>` and report its outcome with the key lines in a few bullets plus the path. A lint refusal (exit 1) is a plan defect: report it to the user as one, with the spans it names. On a run failure, report the error and the log path.
5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py review <task dir>` (the handoff's folder) and follow its first line. `review L1` → run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh plan-reviewer L1 <handoff.md>` and report its Verdict, Findings, and Missing decisions with the result path. `split` → say no plan review is required. `replan` or `stop` → report its reason line and the /chain 3 route (a replan at planner L3 with the findings under `## Plan review`, or a question for the user).

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
