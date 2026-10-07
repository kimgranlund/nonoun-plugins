---
name: plan-fanout
description: "Plan a fanout run: choose ready tickets, group them into lanes with no file overlap, set the lane cap, stagger, gate, and budget, check the command with plan_check.py and fanout.py --dry-run, and return one copy/paste fanout command. Use for \"run these tickets in parallel\" or \"plan a fanout\". NOT for running it."
argument-hint: "[tickets or the goal to parallelize]"
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lane:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run --dry-run:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. `/goal` and `/loop` behavior on Codex is unverified here: emit the same block and say so. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (ticket ids, or the goal to split into lanes).

Read [the fanout rules](references/fanout-rules.md) for lane grouping, caps, and the hot-spot list.

## 1. Gather

Run `tickets.py --root .sdlc check`, list the ready tickets, and run `steps.py lane <task dir>` for each (it records the lane in that task's `skips.md`; that is its only write). Read each ticket's handoff for the paths it will touch. Ask only for what is missing (which tickets, the spend cap), once, with reasoned options. If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Group the lanes

One lane per ticket by default. Two tickets share a lane only when they touch the same files, so they run in order. Tickets that touch a hot-spot file (`check.py`, `check.sh`, `AGENTS.md`, `README.md`) go to separate merge turns or one lane. Keep lanes at or below 4; above 4 raise `--max-lanes`, and above 16 add `--yes-many` only with the person's say-so. Solo tickets use `--lane auto` so the lane script decides. Set `--gate` to the check that must pass after each lane merge, and `--stagger` at the default 20 seconds unless the person knows better.

## 3. Check

Build the command, pipe it to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py fanout` with a quoted heredoc on stdin (no temp file), then run it as `fanout.py run --dry-run <specs and flags>` (the flag right after `run`) and fix whatever it prints. The returned block holds two lines: the dry-run command first, then the same command without `--dry-run`; `plan_check.py` rejects any other shape. Do not return a command that fails.

## 4. Return

ONE fenced block of two lines, the `fanout.py run ... --dry-run` command and then the same command without the flag; five lines of `Why this plan` (the lane grouping, the cap, the gate); `You must authorize` naming the spend (tier caps S $5, M $30, L $60 from budget.py) and that fanout merges nothing to a remote and publishes nothing. This skill cannot run it for you.

Unattended: never call AskUserQuestion; return the command with each missing input as a `warn`.
