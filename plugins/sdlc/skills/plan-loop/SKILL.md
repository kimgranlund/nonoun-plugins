---
name: plan-loop
description: "Plan a /loop: pick the interval or dynamic mode, write a self-contained idempotent prompt with a stop condition, check it with plan_check.py, and return one copy/paste /loop line. Use for \"check this every 20 minutes\" or \"keep watching X\". NOT for running the loop, or for watching running roles or lanes (the run-plan driver turn wakes on their completion)."
argument-hint: "[<task>] [<interval>]"
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. `/goal` and `/loop` behavior on Codex is unverified here: emit the same block and say so. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (what to repeat and, if known, how often).

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `<task>` | What to repeat | taken from the thread, else asked | `check the deploy` |
| `<interval>` | How often: `20m`, `1h`, `30s`, or `2d` | taken from the thread, else asked; none means dynamic mode | `20m` |

Read [the loop rules](references/loop-rules.md) for the interval parser, the cron rounding, and the cost note.

## 1. Gather

Take the task, the cadence, and the end condition from the thread first. Ask only what is missing, once, with 2 to 4 reasoned options each: how often (the longest interval that still fits the need), and when the loop ends. If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Choose the mode

- A fixed cadence: a leading token `20m`, `1h`, `30s`, or `2d`, or a trailing `every 20m`. A token like `20mins:` or `20 minutes:` is NOT an interval: the loop would fall into dynamic mode and ignore the cadence.
- No loop: when the thing watched is running roles or lanes. A fixed-interval status or driver prompt fails `status-polls-running-work`; return the driver turn from `${CLAUDE_PLUGIN_ROOT}/skills/run-plan/SKILL.md` instead, which the completion notification wakes.
- Dynamic mode (no interval): when the next run depends on the work finishing. Prefer an event monitor over polling when the thing waited on has a signal.

## 3. Write the prompt

The prompt is self-contained (the next fire has none of this thread), idempotent (a rerun repeats nothing harmful), reads its state from files or commands and never from memory, reports progress since the last run, and says when to stop (a stop or no-op condition for a recurring loop).

## 4. Check

Pipe the line to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py loop` with a quoted heredoc on stdin (no temp file). Fix every `FAIL` line; show `warn` lines (seconds round up, uneven intervals, a missing "since the last run").

## 5. Return

ONE fenced `/loop ...` line; five lines of `Why this plan` (cadence, cost per fire, stop condition); `You must authorize` for anything the prompt may do each fire (spend, writes). State that recurring jobs expire after 7 days and fire only while the session is idle, and that this skill cannot run the loop for you.

Unattended: never call AskUserQuestion; return the line with each missing input as a `warn`.
