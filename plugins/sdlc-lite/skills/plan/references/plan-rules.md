# Plan rules

The rules every kind of `/plan` shares. The skill body gives the order of work; the kind reference gives the fields and the example.

## Kinds and lints

| Kind | Writes | Lint | Reference |
|---|---|---|---|
| steps | nothing: the planner writes ordered steps with criteria | `steps.py lint <result path>`, then `steps.py review <task dir>` | [steps](steps.md) |
| doc | a plan doc file, normally `.sdlc/<plan-slug>/plan-doc.md`, `status: draft` | `plan_check.py plan --file <plan-doc.md>` and `steps.py lint <plan-doc.md>` | [doc](doc.md) |
| goal | one fenced block that starts with `/goal` | `plan_check.py goal` | [goal](goal.md) |
| campaign | a wave plan, then one fenced `/goal` block | `plan_check.py campaign` | [campaign](campaign.md) |
| fanout | one fenced block of two command lines | `plan_check.py fanout`, then the command itself as `fanout.py run --dry-run` | [fanout](fanout.md) |

- `plan_check.py plan` is the plan doc lint. No `plan_check.py` kind covers steps.
- Pipe a block to its lint with a quoted heredoc on stdin (no temp file); a plan doc is linted from its file. Fix every `FAIL` line and rerun. Show every `warn` line. Do not return a block, command or plan that fails.
- Read first, for goal and doc: `docs/specs/doc-standards/intent.md`, when that file exists in the repository.

## Goal and doc lines

- goal, gather: spend so far and what the person already authorized. Ask for a money cap, a release authorization, what to include.
- goal, write: fill the labelled sections in the order of the example: Scope (a numbered list), the outcome lines, How to work, Budget and stop rules, Authorization, Done when. Done when is a command exit code, a file, a tag, or a closed ticket; it names the Measured by id, command, or target, so closing tickets alone cannot end the goal; it also covers stopping on a limit with state written to the notes file. Keep the block under about 5000 characters.
- doc, gather: the goal and KPI files the plan serves (`docs/goals/`, `docs/kpi/`), each ticket's size, and the records each change would make stale (`git grep -l` for the changed behavior). Ask for a money cap, an authorization (publish, push, tag, `onboard.py setup`), the driver.
- doc, measures: the Measures table repeats each KPI as a row (command, `read:` path, target, direction, before, `when`); a KPI that moves only with elapsed time goes to Later measures with an owner and a date.
- doc, steps: one `## Step <n>: <title>` block per ticket, in the planner's step format (`${CLAUDE_PLUGIN_ROOT}/agents/planner.md`) plus the key lines `level`, `ticket`, `depends`, `executor`, `verify`, `cap` and `upserts`. The ticket level is the lane, so keep steps at L1 or L2 where the work allows. Every criterion carries a backticked command or file; a `(red)` criterion fails before the step and passes after it. A step that edits a record other files name lists those files in `upserts:` and carries a `git grep` or `docs_check.py` criterion that sweeps them. A step of size L4 or L5 needs a plan-reviewer result from a different model family, named in `reviewed:`. Verification is never assigned to the driver.
- doc, control: `plan_done.py <plan-doc.md>` on the unstarted plan must exit 1 and list every step open. `l1-unverified` means an L1 step has no independent verifier unless it sets `verify: required`.

## Outcome block

Goal, doc and campaign carry the four parts Outcome, Measured by, Rubric and Negative control; fanout and steps do not. The format and the rule of each part are in `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/references/outcome-block.md`. A handoff `## Outcome` section stands in for the plan-verification call when the kind's lint prints no `outcome-block` finding for it. Keep the measure command and its output line for `Why this plan`.

## Numbers, stop rules, authorization

- Every number comes from the thread or the person's answer, never a default you invented.
- Stop rules carry numbers: a total dollar cap, a cap per ticket, step or lane, a rate or weekly limit, and three 529s in a row. State goes to the notes file (`.sdlc/notes.md`, or `.sdlc/notes/notes.md` with `layout: topics`). No retry loops. A plan doc adds `replan cap: 1, then stop`.
- Authorization is explicit. Publish, push, tag, and external writes are never implied: name exactly what is allowed and under what condition, or write `None`.

## Budget levels and the cost line

The dollar cap of each ticket level is `TIERS` in `${CLAUDE_PLUGIN_ROOT}/scripts/budget.py`. Read the table there; do not copy its numbers into a rule. The `cost:` line of the dry run is the sum of the caps of the tickets in scope against the cap the person gave: `cost: $<sum of caps> of $<cap> (<n> tickets: T-0001 L2 $30, ...)`. A ticket with no size, or a level with no row in `TIERS`, counts as `unknown`, never 0; a sum above the cap ends with `over`. The line is a ceiling, not a forecast of spend.

## Goal line

A plan doc ends with this line in the last fenced block of Done when, and the doc kind returns it as its `/goal` block. Write the resolved plugin path, since the stop hook cannot expand a variable:

```
/goal complete build and verify <plan-doc.md> by the run-plan skill: done when `python3 <plugin-root>/scripts/plan_done.py <plan-doc.md>` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state. Do not end the turn while it exits 1 and an item is open that you can work on.
```

## Return

After the dry run, in this order: ONE fenced block; five lines of `Why this plan` (the evidence behind the scope, the caps and the lane choices, and the measure command with its `before` output line); a list `You must authorize` naming each thing the block permits that is not free (spend, push, publish). Then say: a goal pasted as plain text is not registered until you run it as `/goal`; this skill cannot run it for you.

- doc returns the path, a three-line summary (steps with levels, total cap, what the Authorization allows) and the Goal line as the fenced block. It states that the maintainer approves the plan by setting `status: approved`, `approved_by:` and `approved_on:`, and that an unattended driver starts with `SDLC_ROLE=conductor` and `SDLC_HEADLESS=1` exported. This kind never edits product files, never sets `status: approved`, and never runs the plan.
- steps returns the planner result path in place of the fenced block.

## Unattended and Codex

- Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion. The kind is `steps` when no kind token is given. Return the block with each missing input marked as a `warn` line; a plan doc keeps `status: draft`.
- Codex: AskUserQuestion becomes the host question mechanism. `/goal` and `/loop` behavior on Codex is unverified here: emit the same block and say so.
