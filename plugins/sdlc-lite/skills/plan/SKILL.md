---
name: plan
description: "Plan a task: dispatch the planner to produce ordered steps with acceptance criteria and a builder level per step. Use when a goal is ready to be broken into buildable steps."
argument-hint: "[L1..L3] <handoff.md | goal>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Agent, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, set `SDLC_ROUTING_REASON` to a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). `dispatch.py prepare` (Codex: `run.sh`) reads it and records the resolved model and effort separately. Read [run operations](../handoff-format/run-operations.md) for readiness and interrupted-attempt recovery.

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section planner.
3. Dispatch the planner at `<level>` on `<handoff.md>` from the project root, the three steps of `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md` ("How you run roles"): `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare planner <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes its `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message on stdin, validates and records the result. On Codex run `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner <level> <handoff.md>` instead.
4. On success `record` exits 0 and prints the result path. Read it, then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <result path>` and report its outcome with the key lines in a few bullets plus the path. A lint refusal (exit 1) is a plan defect: report it to the user as one, with the spans it names. On a failed run (`record` exit 1 or 3), report the error and the result or `.limit` file path (Codex: the log path).
5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py review <task dir>` (the handoff's folder) and follow its first line. `review L1` → dispatch the plan-reviewer at L1 on `<handoff.md>` (`dispatch.py prepare plan-reviewer L1 <handoff.md>`, the `Agent` spawn, `dispatch.py record`; Codex: `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh plan-reviewer L1 <handoff.md>`) and report its Verdict, Findings, and Missing decisions with the result path. `split` → say no plan review is required. `replan` or `stop` → report its reason line and the /chain 3 route (a replan at planner L3 with the findings under `## Plan review`, or a question for the user).

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
