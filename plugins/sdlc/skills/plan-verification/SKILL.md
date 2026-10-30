---
name: plan-verification
description: "Capture the outcome a plan serves: one outcome sentence with its why, a measure with its before value and target, a 3 to 5 criterion rubric, and a negative control, as lines another plan skill places in its block. Use before a goal is written (plan-goal reads it), or for \"what is this goal for\", \"how will we know it worked\", \"add a measure to this goal\". NOT for step criteria (planner), pass or fail on built work (verifier), or creating a goal or KPI file."
argument-hint: "[<goal-id|outcome>]"
allowed-tools: Read, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (a goal id, or the outcome in a sentence; empty means infer it from the thread).

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `<goal-id\|outcome>` | A goal id, or the outcome in a sentence | inferred from the thread | `G-001` |

A plan that can end green with the outcome unmoved has no measure. This skill produces the outcome block: Outcome, Measured by, Rubric, Negative control. Read [the outcome block](references/outcome-block.md) for the format, the rules of each part, the control forms, and an example. The caller (plan-goal) places the lines in its block and checks them with `plan_check.py goal`; this skill writes no file under `docs/` and never creates a goal or KPI file.

## 1. Gather

When the caller cites a goal id (`G-001`), read that file under `docs/goals/` and take Outcome, Why and Done when from it. Otherwise list `docs/goals/` and `docs/kpi/` with Glob (a repository without them skips this) and use an active goal whose scope matches the thread. Never invent a KPI id.

## 2. Choose the measure

An existing KPI first (its `measure:`, `read:`, `target:`), then a command the thread names, then ask once. A command that writes, spends, or publishes is never run to get a `before` value.

## 3. Read the before value

Run the measure once for `before`. Show the command and its output line for `Why this plan`. No run possible: `before: unmeasured: <reason>` (a warning, not a failure). No measure exists yet: `Measured by: none: <reason>` replaces the whole line.

## 4. Draft the rubric

Draft 3 to 5 numbered criteria from the goal's Done when and the tickets' own acceptance criteria: read them, do not rewrite them. One criterion is the Measured by threshold; the rest cover what the number cannot. Each is `<what> | pass: <threshold>` with the file or command that decides it.

## 5. Write the negative control

One line naming a state in which the measure reads red and the variable that makes it red. The cheapest: the `before` value sits on the wrong side of `target`. Otherwise name a mutation, per the `checks-that-bite` skill at `${CLAUDE_PLUGIN_ROOT}/skills/checks-that-bite/SKILL.md`.

## 6. Return

Return the four parts as lines in the order of the example, plus one `Why this plan` line with the measure command and its output. When no KPI exists for a measure worth keeping, add `propose K-file for <command>`, left to a ticket. A missing target or measure: one `AskUserQuestion` round with 2 to 4 reasoned options.

Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion; mark each gap as a `warn` line.
