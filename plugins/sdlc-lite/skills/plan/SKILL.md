---
name: plan
description: "Plan work by kind and return a linted, paste-ready result with a dry run printed first. Kinds: steps (default: dispatch the planner to turn a goal into ordered steps with acceptance criteria and a builder level per step), doc (a plan doc a smaller session runs with run-plan), goal (one /goal block for unattended work), campaign (a wave plan with a gate and parallel lanes), fanout (one fanout command for ready tickets), compaction (one prompt to paste into a manual /compact). Use for \"buildable steps\", \"write me a goal\", \"overnight goal\", \"plan doc\", \"plan this so a smaller model can run it\", \"plan a campaign\", \"migrate every page\", \"plan a fanout\", \"run these tickets in parallel\", \"compaction prompt\", \"before I /compact\". NOT for running a goal, a plan doc or a fanout (run-plan, fanout), a /loop line (plan-loop), or the outcome block alone (plan-verification)."
argument-hint: "[steps|doc|goal|campaign|fanout] [L1|L2|L3] <handoff.md|goal|tickets> | compaction [options]"
allowed-tools: Read, Grep, Glob, Write, Edit, Agent, AskUserQuestion, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/budget.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run --dry-run:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check:*), Bash(uptime:*), Bash(git log:*), Bash(git grep:*), Bash(git status:*), Bash(gh pr list:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/plan/scripts/compaction_handoff.py:*)
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (a kind, then a level, a handoff file, the goal, or ticket ids; empty means infer the goal from the thread; or `compaction [--write-handoff|--clear] [<prose>]`).

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `steps\|doc\|goal\|campaign\|fanout` | The kind of plan | `steps` when the rest names a `handoff.md`, else asked | `goal` |
| `L1\|L2\|L3` | The planner level, for the steps kind | resolved as `references/steps.md` says | `L2` |
| `<handoff.md\|goal\|tickets>` | A handoff file, the goal, or ticket ids | the goal inferred from the thread | `T-0101 T-0102` |
| `compaction` | The compaction kind: one prompt to paste into a manual `/compact` | - | `compaction` |
| `--write-handoff` | With `compaction`: also write the file that `references/compaction.md` names | off | `compaction --write-handoff` |
| `--clear` | With `compaction`: clear that file and do nothing else | off | `compaction --clear` |
| `<prose>` | With `compaction`: the focus, passed through verbatim | none | `compaction finish the board fix` |

Read the plan rules at `references/plan-rules.md` for every kind but compaction: the lint of each kind, the rules for numbers, stop rules and authorization, and what to return.

## 0. Kind and handoff

The kind is the first argument token when it is one of `steps|doc|goal|campaign|fanout`. Otherwise it is `steps` when the rest names a `handoff.md`. Otherwise ask one `AskUserQuestion` for the kind, with at most 4 options: `steps` first and recommended, then `doc`, `goal` and `campaign`, and `fanout` named in the question text for the Other box. Unattended, the kind is `steps`.

The first token `compaction` selects the compaction kind: read `references/compaction.md` and follow it alone. The plan rules, sections 1 to 5 and the dry run do not apply to it.

Reserved first word: a goal whose text starts with a kind name is written with the kind first (`goal steps toward the release`) or in quotes. `compaction` is reserved too (`goal compaction ...`).

| Kind | Returns | Read |
|---|---|---|
| steps | ordered steps from the planner | `references/steps.md` |
| doc | a plan doc that `run-plan` runs | `references/doc.md` |
| goal | one `/goal` block | `references/goal.md` |
| campaign | a wave plan and one `/goal` block | `references/campaign.md`, then the goal reference |
| fanout | one fanout command | `references/fanout.md` |
| compaction | one prompt for a manual `/compact` | `references/compaction.md` |

Read the handoff first. When the argument is a `<work root>/<slug>/handoff.md` (the work root: `.sdlc` by default, `docs/work` with `work_root: docs/work`) written by `/clarify`, fill the slots from it and do not ask for them again: `Level:` gives the lane, the level and the cap; `Do:` gives Scope or the steps; `Non-goals:` gives the scope-held rubric line; `Done when:` and `Verify:` give Done when and the fanout gate; `## Outcome` gives the outcome block; `## Constraints` gives the Authorization lines.

## 1. Gather

Take every other input from the thread and repo before asking: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check`, then the ready tickets, each ticket's size and lane (`steps.py lane <task dir>`, which records the lane in that task's `skips.md`), and the extras the kind reference names.

Ask only for the slots still empty, in one round, with 2 to 4 reasoned options each. Goal needs the cap and the authorization; campaign the census command, the lane cap and the GitHub rights; fanout the tickets and the cap; doc the driver, the cap and the authorization; steps the level only. If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Capture the outcome

Goal, doc and campaign only. Read `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/SKILL.md` and follow it: it returns the Outcome, Measured by, Rubric and Negative control lines, with the measure run once for its `before` value. A handoff `## Outcome` that passes the lint replaces the call.

## 3. Write

Write per the kind reference and the plan rules. The `steps` kind writes no plan: it dispatches the planner as its reference says.

## 4. Check

Run the lint of the kind, fix every `FAIL` line and rerun; never return a result that fails.

- goal, campaign, fanout: pipe to `plan_check.py goal`, `plan_check.py campaign` or `plan_check.py fanout`. Fanout and campaign then run the lanes as `fanout.py run --dry-run`.
- doc: `plan_check.py plan --file <plan-doc.md>`, then `plan_done.py <plan-doc.md>`, which must exit 1 on the unstarted plan.
- steps: `steps.py lint <result path>`, then `steps.py review <task dir>`; a `review L1` first line routes to the plan-reviewer.

## 5. Return

Print the dry run first, in this fixed shape, each line taken from a command and none written from memory:

```
Dry run (<kind>)
lint: <the plan_check.py or steps.py lint line(s), verbatim>
cost: $<sum of caps> of $<cap> (<n> tickets: T-0001 L2 $30, ...)
lanes: <fanout.py run --dry-run output, verbatim>        # fanout and campaign only
control: plan_done.py exits 1, <n> steps open            # doc only
```

Take `cost:` from `plan_check.py <kind> --summary`, which sums the `TIERS` row of each ticket the block names (`${CLAUDE_PLUGIN_ROOT}/scripts/budget.py`); the steps kind has no such lint, so give its `cost:` as `unknown`. Print the line verbatim; the plan rules say what `unknown` and `over` mean.

Then return the block of the kind, five lines of `Why this plan`, the list `You must authorize`, and the line that a goal pasted as plain text is not registered until it is run as `/goal`. This skill runs nothing it plans.

Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion; return the result with each missing input marked as a `warn` line.
