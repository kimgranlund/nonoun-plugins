---
name: handoff-format
description: Layout and templates for sdlc-lite task folders (.sdlc/<task>/) and handoff files. Reference for the launcher skills; not a command.
user-invocable: false
---
## Layout

```
.sdlc/<task-slug>/
  handoff.md            task brief (goal, intent, context, constraints)
  design.md             /grill ratified design (optional)
  decompose/            /decompose manifest-v<n>.json + report.md (optional)
  scout-L1.md           outputs of task-level roles: <role>-<level>.md
  planner-L2.md
  runs.jsonl            one line per run: role, level, model, effort, cost, duration
  step-1/
    handoff.md          one plan step: level, do, acceptance criteria
    builder-L2.md
    verifier-L1.md
  step-2/ ...
```

`scripts/run.sh <role> <level> <handoff.md>` writes `<role>-<level>.md` and `.log` next to the handoff it is given. Rerunning the same role and level overwrites them; runs.jsonl keeps the history. Add `.sdlc/` to the project's `.gitignore` unless the user wants the trail committed.

## Task handoff (`.sdlc/<task>/handoff.md`)

```
## Goal
One or two sentences: the outcome, not the method.

## Intent
Written by /clarify: literal ask, deltas, do, non-goals, done when. Optional.

## Context
Decisions already made, relevant paths, links. Point to `design.md` and `decompose/report.md` when they exist. Everything a clean-context agent needs; it sees nothing else.

## Constraints
What must not change, limits, deadlines. "None" if none.

## Question
Only for scout, archaeologist, or researcher runs: the exact question.
```

## Step handoff (`.sdlc/<task>/step-<n>/handoff.md`)

Copied from the plan's step block, plus the task goal for orientation:

```
## Task goal
<from the task handoff>

## Step <n>: <title>
level: L<n>

### Do
...

### Acceptance criteria
- ...
```

## Free-text arguments

When a launcher skill gets text instead of a handoff path, create `.sdlc/<slug>/handoff.md` (slug: 2 to 5 lowercase words from the text, hyphenated; add `-2` etc. if taken) from the template, put the text in Goal (or Question for question roles), fill Context from what the current conversation established, and show the user the path.
