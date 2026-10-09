---
name: plan-campaign
description: "Plan a wave-based campaign (build the tool and gate, migrate N units in parallel lanes, bulk review, bulk PRs) and return one /goal block plus a lane partition. Use for \"migrate every page\", \"plan a campaign\", or a standard that must hold across many units. NOT for a single goal (plan-goal), one fanout run (plan-fanout), or running anything."
argument-hint: "[the outcome the campaign should reach]"
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/budget.py:*), Bash(uptime:*), Bash(git log:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. AskUserQuestion becomes the host question mechanism. `/goal` and `/loop` behavior on Codex is unverified here: emit the same block and say so. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (the outcome in one sentence; empty means infer it from the thread).

A campaign is a migration where a shared tool and a blocking gate must land before N parallel lanes run, then bulk review and bulk PRs. Read [the campaign rules](references/campaign-rules.md) for the template, the lessons, and a block that passes the check.

## 1. Gather

Take every input from the repo and thread before asking:
- The outcome in one sentence.
- A census command that counts the units still to migrate (exit 0, prints a number). Find one or have Wave 0 build it; refuse to plan without one.
- The existing gates and how a new gate joins the gate chain (`gate-classes.json` or the equivalent). A new gate adds no CI job, step, or required check.
- Machine load (`uptime`) and the plugin lane caps (4 lanes by default, above 16 needs `--yes-many`).
- The ready tickets (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check`) and the budget levels (`budget.py`, L1 $5, L2 $30, L3 $60).

Then ask once, with 2 to 4 reasoned options each: the spend cap, the GitHub rights (push, PR, merge), and the lane cap. If `AskUserQuestion` is unavailable, ask in plain lines.

## 2. Write the plan

Follow the template in the rules file, in this order:
1. Wave 0, one lane, lands first: the shared tool and a blocking gate that starts green through a day-one allowlist of current violators, each with a justification string.
2. Wave 1, N lanes: a directory partition generated from the census, file-disjoint, one writer per file, one reference PR named as the pattern. Print it as a table of lane, directory, units.
3. Wave 2, bulk review: one verifier per bundle of 5 to 10 lanes on a different model family than the builders, plus a probe sweep with before and after numbers per unit.
4. Wave 3, bulk PRs: one integration branch per area, a target PR count (8 to 10), one plain push each.
5. One `/goal` block (the goal rules in plan-goal apply, including the outcome lines from `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/SKILL.md`): authorization explicit, with publish, tag, and deploy never implied. When the owner says "no limits", set a dollar backstop from the budget level times the lane count and call it a backstop.

Every number comes from the repo or the person's answer, never a default you invented.

## 3. Check

Pipe the whole plan, the lines above the fence plus the fenced `/goal` block, to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py campaign` with a quoted heredoc on stdin (no temp file). Fix every `FAIL` line and rerun; show `warn` lines. Do not return a plan that fails.

## 4. Return

Return, in this order: the plan (census, dependency order, lane cap, the four waves, the partition table, the stop rules, done when); ONE fenced block starting with `/goal`; five lines of `Why this plan` (the census, the partition, the cap, the gate); a list `You must authorize` naming each thing the plan permits that is not free (spend, push, PRs, merge). Then say: a goal pasted as plain text is not registered until you run it as `/goal`; this skill cannot run the campaign for you.

Unattended (`SDLC_HEADLESS=1`): never call AskUserQuestion; return the plan with each missing input marked as a `warn` line.
