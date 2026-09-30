---
name: fix
description: "Fast lane for a size-S item (a doc line, a lint tweak, one test, a one-file fix). The conductor writes the step handoff itself, runs builder L1 or L2 and verifier L1, and closes the ticket inline with `tickets.py close --reason`; no planner, no filer, no follow-up tickets. Use for \"quick fix\", \"small fix\", or a size-S ticket. NOT for work touching more than one file's behavior or needing a plan, which is /chain."
argument-hint: "<ticket slug | one-line ask>"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*), Read, Write, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

For every role launch, set `SDLC_ROUTING_REASON` to the selected role/level rationale, including the recorded cause of any escalation or replan. Read [shared run operations](../handoff-format/run-operations.md) for readiness, attempt records, and safe recovery.

Arguments: `$ARGUMENTS`

The fast lane: one step, no planner, no filer, no follow-up tickets. Layout follows `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`; levels follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`.

Long runs: every role runs through `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh` from the project root. Headless (`claude -p`): run every call in the foreground with the Bash tool's `timeout` set to 600000 or more, do not use `run_in_background` there, and never end your turn while a role is running, because ending the turn ends the session and abandons the run; headless launchers set `SDLC_HEADLESS=1`, and `hooks/block-background.sh` denies background calls then. In an interactive session: run `run.sh` with `run_in_background: true`, then wait for the completion notification. Never poll with `sleep`. Once notified, read the result from `<role>-<level>.md`.

1. Size gate. Size S means docs, a lint tweak, one test, or a fix in one file with an obvious effect, provable by 1 to 3 checks. Anything else: say so in one line and route to `/sdlc-lite:chain`.
2. Handoff. Use `.sdlc/<slug>/handoff.md` when it exists (a ticket); otherwise create it per handoff-format's free-text rule. Write `.sdlc/<slug>/step-1/handoff.md` yourself per the step template: `## Task goal`, `## Step 1: <title>`, `level: L1` or `L2` per the builder rubric, a `### Read first` subsection when the fixed file's nearest `AGENTS.md` is not the root (same rule as the planner: one ``- `<path>` `` line per entry, after `level:` and before `### Do`), `### Do`, and `### Acceptance criteria` with 1 to 3 criteria, each a runnable command span that is red now or a `(guard)` that is green now, no `||`, no pinned sha. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint .sdlc/<slug>/step-1/handoff.md` and fix any refusal. Never run `steps.py split`.
3. Build and verify. Run `run.sh builder <level> .sdlc/<slug>/step-1/handoff.md`, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py next .sdlc/<slug>/step-1`, then `run.sh verifier L1` on the same handoff. On a fail, rebuild once at the same level with the verifier's note under `## Previous attempt`. A second fail, a blocked builder, or `inherited` from `steps.py next`: stop, report, and offer /chain (the item was not size S). Never bump, replan, or fix it yourself.
4. Close. On a pass, when the task handoff has ticket front matter, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug> --reason "fixed in session by /fix: <one line>"`. No filer, no follow-ups. No ticket: nothing to close.
5. Publish (commit, push, PR) only after an AskUserQuestion approval, as in /file step 4; never publish on your own. Unattended (headless, or an unattended goal, no person present): never call AskUserQuestion, never push or open a pull request (a local commit is the most it may do), and end with a report that lists the work waiting to be published. Report with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --task <slug>`.
