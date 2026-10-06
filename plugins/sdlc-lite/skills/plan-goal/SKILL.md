---
name: plan-goal
description: "Plan a /goal session: gather the scope and limits from the thread and repo, apply the goal rules (a checkable done-when, stop rules with numbers, explicit authorization), check the block with plan_check.py, and return one copy/paste /goal block. Use for \"write me a goal\", \"overnight goal\", or before unattended work. NOT for running the goal."
argument-hint: "[what the goal should achieve]"
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lane:*), Bash(git log:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. `/goal` and `/loop` behavior on Codex is unverified here: emit the same block and say so. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (the outcome the person wants; empty means infer it from the thread).

A `/goal` condition is checked by a session stop hook on every turn, so it must be a condition a command or file can prove. Read [the goal rules](references/goal-rules.md) for the field list and the example.

## 1. Gather

Take every input from the thread and repo before asking: open tickets (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check`, then the ready ones), each ticket's size and lane (`steps.py lane <task dir>`, which records the lane in that task's `skips.md`), spend so far, and what the person already authorized. Ask only for what is still missing, once, with 2 to 4 reasoned options each (a money cap, a release authorization, what to include). If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Write the block

Fill the five labelled sections in the order of the example: Scope (a numbered list), How to work, Budget and stop rules, Authorization, Done when. Every number comes from the thread or the person's answer, never a default you invented. Authorization is explicit: publish, push, tag, and external writes are never implied; name exactly what is allowed and under what condition, or write `None`. Done when is a command exit code, a file, a tag, or a closed ticket, and it also covers stopping on a limit with state written to the notes file (`.sdlc/notes.md` (`.sdlc/notes/notes.md` with `layout: topics`)). Keep it under about 5000 characters so it can be read overnight.

## 3. Check

Pipe the block to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py goal` with a quoted heredoc on stdin (no temp file). Fix every `FAIL` line and rerun; show `warn` lines. Do not return a block that fails.

## 4. Return

Return, in this order: ONE fenced block starting with `/goal`; five lines of `Why this plan` (the evidence behind the scope, caps, and lane choices); a list `You must authorize` naming each thing the block permits that is not free (spend, push, publish). Then say: a goal pasted as plain text is not registered until you run it as `/goal`; this skill cannot run it for you.

Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion; return the block with each missing input marked as a `warn` line.
