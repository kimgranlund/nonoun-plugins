---
id: T-0040
title: "A script writes step handoffs from a plan"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
/chain turns a plan into step handoffs with a script, not per-session parsing.

## Intent
Literal ask: /chain turns a plan into step handoffs with a script, not per-session parsing. Suggested: `steps.py split <planner.md> [--only N]` writing step-<n>/handoff.md per the handoff-format step template (task goal plus step block), with a selftest.
Deltas:
- Location and name: defaulted: `plugins/sdlc-lite/scripts/steps.py`, stdlib-only Python 3 like board.py and tickets.py, subcommands `split` and `selftest`.
- Input: defaulted: `split <planner.md | task dir>`; given a task dir, it uses the newest `planner-*.md` by mtime (the current plan, per handoff-format). The task goal comes from the `## Goal` section of the `handoff.md` in the planner file's directory (ticket front matter ignored); if that handoff has no Goal section, fail with a clear message.
- Parsing: defaulted: a step block is a `## Step <n>: <title>` line through the line before the next `## ` heading (another step, `## Risks`, anything) or end of file; `### Do` and `### Acceptance criteria` stay inside the block verbatim. Fail (nonzero exit, message on stderr, nothing written) on: no steps, duplicate step numbers, or a step block with no `level: L<1-5>` line.
- Output: defaulted: `<task dir>/step-<n>/handoff.md` per the handoff-format Step handoff template: `## Task goal`, the goal text, a blank line, then the step block verbatim (trailing blank lines trimmed). Prints one line per file written.
- `--only N`: defaulted: repeatable; writes only those steps; an N not in the plan is an error, nothing written.
- Existing step dirs: defaulted: overwrite `step-<n>/handoff.md` when the dir holds no role output; refuse (nonzero, nothing written) when `step-<n>/` already holds any `builder-*.md` or `verifier-*.md`, naming the /chain 4.2 superseded rename (`step-<n>.superseded-<k>/`). The script does not perform the rename itself.
- Callers: defaulted: skills/chain/SKILL.md step 3 and step 4.2 call the script instead of describing a parse; chain's allowed-tools gains `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)`.
Do: add scripts/steps.py (split, selftest) as above; run its selftest from scripts/check.sh; point /chain steps 3 and 4.2 at it; add one line to skills/handoff-format/SKILL.md naming the script as the writer of step handoffs; update the repo CLAUDE.md Layout and `.claude/agents/sdlc-lite-author.md` if it lists the scripts; audit agents/conductor.md and other skills for a per-session step-parse instruction and point them at the script.
Non-goals: performing the superseded rename (stays in /chain 4.2); changing the planner's output format; changing run.sh or board.py.
Done when: `python3 plugins/sdlc-lite/scripts/steps.py selftest` passes and covers a normal split, `--only`, task-dir input picking the newest planner file, missing level, duplicate step, no steps, and the refuse-on-role-output case (each failure case proven to fire); a manual split of a real planner file in `.sdlc/` (into a temp copy) produces handoffs matching the template; scripts/check.sh passes and runs the steps selftest; /chain steps 3 and 4.2 name the script.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. /chain step 3 says "for each ## Step n block, write step-<n>/handoff.md" (skills/chain), so every conductor writes its own parser; that session needed a second one for a single-step replan. Suggested: `steps.py split <planner.md> [--only N]` writing step-<n>/handoff.md per the handoff-format step template (task goal plus step block), with a selftest. Pairs with the superseded-step-dirs ticket for replans.

## Constraints
Existing board.py, tickets.py, and run selftests keep passing. Roles are launched by a different checkout's run.sh (/Users/kimba/Projects/nonoun/sdlc-agents); edit only files in this worktree (plugins/sdlc-lite/ and repo-root CLAUDE.md, .claude/).
