---
name: plan-doc
description: "Write a plan doc: one file with the goal, outcome block, measures, authorization, stop rules and ordered ticket steps with runnable criteria, linted by plan_check.py plan, so a smaller session can run it with run-plan. Use for \"write a plan doc\", \"plan this so a smaller model can run it\", or before /goal complete build and verify <plan-doc.md>. NOT for a goal with no steps to keep (plan-goal), for running a plan doc (run-plan), or for one step's builder handoff (plan)."
argument-hint: "[what the plan should achieve]"
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check:*), Bash(git grep:*), Bash(git log:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. `/goal` behavior on Codex is unverified here: emit the same goal line and say so. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (the outcome the plan serves; empty means infer it from the thread).

The plan doc is the only place judgment enters. A smaller session runs it afterwards with `run-plan`, and a script (`plan_done.py`) decides when it is finished, so every number, command and criterion has to be written here, checkable, and complete. Read [the plan doc format](references/plan-doc-format.md) for the file shape, the step block and the lint rules before writing.

## 1. Gather

Take every input from the thread and repo before asking: the goal and KPI files the plan serves (`docs/goals/`, `docs/kpi/`), open tickets (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check`), each existing ticket's size, and the records each change would make stale (`git grep -l` for the changed behavior). Ask only for what is still missing, once, with 2 to 4 reasoned options each: a money cap, an authorization (publish, push, tag, `onboard.py setup`), the driver. If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Capture the outcome

Read `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/SKILL.md` and follow it: it returns the Outcome, Measured by, Rubric and Negative control lines, with the measure run once for its `before` value. The Measures table repeats each KPI as a row (command, `read:` path, target, direction, before, `when`); a KPI that moves only with elapsed time goes to Later measures with an owner and a date.

## 3. Write the steps

One `## Step <n>: <title>` block per ticket, in the planner's step format (`${CLAUDE_PLUGIN_ROOT}/agents/planner.md`) plus the key lines `level`, `ticket`, `depends`, `executor`, `verify`, `cap` and `upserts`. The ticket level is the lane: solo for L1 and L2 by default (`steps.py lane`), so keep steps at L1 or L2 where the work allows. Every criterion carries a backticked command or file; a `(red)` criterion is a control that fails before the step and passes after it. A step that edits a record other files name lists those files in `upserts:` and carries a `git grep` or `docs_check.py` criterion that sweeps them. A step of size L4 or L5 needs a plan-reviewer result from a different model family, named in `reviewed:`. Verification is never assigned to the driver.

## 4. Write the frame

Authorization names exactly what the run may do beyond editing the repository and running checks (publish, push, tag, `onboard.py setup`, external writes), each with its condition, or says `None`. Budget and stop rules carry the total dollar cap, the per-step caps, the three 529s rule, the rate or weekly limit rule, `replan cap: 1, then stop`, and the notes path. Done when requires `plan_done.py` to exit 0, or exit 4 after `plan_done.py stop` wrote state, and holds the fenced `Goal line:`. Every number comes from the thread or the person's answer, never a default you invented.

## 5. Check

Save the file (normally `.sdlc/<plan-slug>/plan-doc.md`, `status: draft`), then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py plan --file <plan-doc.md>` and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <plan-doc.md>`. Fix every `FAIL` line and rerun; show `warn` lines (`l1-unverified` means an L1 step has no independent verifier unless it sets `verify: required`). `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py <plan-doc.md>` on the unstarted plan must exit 1 and list every step open: that is the plan's own negative control. Do not hand over a plan that fails.

## 6. Return

Return the path, a three-line summary (steps with levels, total cap, what the Authorization allows), the `warn` lines, and the Goal line as one fenced `/goal` block. Then state that the maintainer approves it by setting `status: approved`, `approved_by:` and `approved_on:` (the run refuses an unapproved plan), that an unattended driver is started with `SDLC_ROLE=conductor` and `SDLC_HEADLESS=1` exported, and that a goal pasted as plain text is not registered until it is run as `/goal`.

Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion; mark each missing input as a `warn` line in the plan and leave `status: draft`. This skill never edits product files, never sets `status: approved`, and never runs the plan.
