---
name: chain
description: Drive one task through the whole loop: optional scout, research, and architect, then plan, then build and verify each step with escalation, then file. Use when a task should run end to end.
argument-hint: <handoff.md | goal>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Read, Write, Grep, Glob
---
Arguments: `$ARGUMENTS`

Every role runs through `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>` from the project root. Levels follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`; layout follows `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`. You orchestrate; you never do a role's work yourself. Run every `run.sh` call in the foreground with the Bash tool's `timeout` set to 600000 or more, never `run_in_background`, and never end your turn while a role is running: in a headless session, ending the turn ends the session and abandons the run.

## 1. Brief
Get or create `.sdlc/<task>/handoff.md`. If it lacks context a clean agent would need, ask the user before running anything.

## 2. Understand (only what the task needs)
- Vague or overloaded ask → the /clarify flow first (unattended mode when no person is present: name gaps, never block).
- Greenfield with most decisions unmade → the /grill flow, only when a person is present; unattended, stop and tell the user a grill is needed.
- Scoped but many parts, or cross-cutting → the /decompose flow with `--plan` after any architect run.
- Unfamiliar code location → scout L1.
- Code whose history matters (odd patterns, "why is this here") → archaeologist L1.
- Outside facts needed → researcher at the rubric level.
- Cross-cutting or unfamiliar design → architect L1.
All run on the task handoff; their outputs land in the task dir for the planner.

## 3. Plan
Run planner on the task handoff. For each `## Step n` block, write `step-<n>/handoff.md` per the step template.

## 4. Build and verify, one step at a time, in order
For each step:
1. builder at the step's `level:`.
2. builder Status blocked → skip the verifier (never verify a blocked build) and run planner L3 on the task handoff (replan; it writes a new `planner-L3[-k].md`), move each `step-<n>/` with n at or above the blocked step that already holds builder or verifier output to `step-<n>.superseded-<k>/` (first free k), then write fresh `step-<n>/handoff.md` files, rewriting the remaining step handoffs from the newest planner file (earlier plans stay in place), continue from the blocked step.
3. verifier at the level the rubric derives from the build level.
4. Verdict fail → rebuild the same level once (it writes `builder-L<n>-<k>.md`, so earlier attempts stay for the rubric's "earlier builder-*.md with Status blocked" count), with the verifier's "For the next attempt" appended to the step handoff under `## Previous attempt`. A second fail → bump the builder one level and repeat. A fail at L5 → stop and ask the user.

## 5. File
Run the /file flow on the task dir. Publishing still needs the user's approval.

## Report
At every pause (after the plan, after each verdict, at the end) the whole status message is the /board render for this task: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --task <slug> --waiting "<line>"`, printed verbatim. Never a hand-made status table. Add only the task dir path at the end.
