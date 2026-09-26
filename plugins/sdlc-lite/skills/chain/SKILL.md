---
name: chain
description: Drive one task through the whole loop: optional scout, research, and architect, then plan, then build and verify each step with escalation, then file. Use when a task should run end to end.
argument-hint: <handoff.md | goal>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Read, Write, Grep, Glob, AskUserQuestion
---
Arguments: `$ARGUMENTS`

Every role runs through `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh <role> <level> <handoff.md>` from the project root. Levels follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`; layout follows `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`. You orchestrate; you never do a role's work yourself. How to run `run.sh` depends on the session. Headless (`claude -p`, including `scripts/bench.sh`, which raises `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`): run every call in the foreground with the Bash tool's `timeout` set to 600000 or more, do not use `run_in_background` there, and never end your turn while a role is running, because ending the turn ends the session and abandons the run. `hooks/block-background.sh` denies Bash `run_in_background` calls and denies any Agent call unless `run_in_background` is explicitly `false` (Agent runs in the background by default, so a missing field counts as background) whenever `SDLC_ROLE` is set or `SDLC_HEADLESS=1`; bench.sh and fanout set `SDLC_HEADLESS=1`, and any other headless launcher (a dogfood script) must set `SDLC_HEADLESS=1` itself. In an interactive session: a role, or a bench task's full /chain, can take 15 to 30 minutes, past the Bash tool's 10-minute cap. Run `run.sh` with `run_in_background: true`, then wait for the completion notification. Never poll with `sleep`. Once notified, read the result from `<role>-<level>.md`. Ending the turn is safe here because the notification re-invokes the session.

## 1. Brief
Get or create `.sdlc/<task>/handoff.md`. If it lacks context a clean agent would need, ask the user before running anything.

## 2. Understand (only what the task needs)
- Vague or overloaded ask → the /clarify flow first (unattended mode when no person is present: name gaps, never block).
- Greenfield with most decisions unmade → the /grill flow, only when a person is present; unattended, stop and tell the user a grill is needed.
- Scoped but many parts, or cross-cutting → the /decompose flow with `--plan` after any architect run.
- Unfamiliar code location → scout L1.
- Code whose history matters (odd patterns, "why is this here") → archaeologist L1.
- Outside facts needed → researcher at the rubric level.
- Cross-cutting or unfamiliar design → architect L1.
All run on the task handoff; their outputs land in the task dir for the planner.

A /chain run under fanout that stops mid-step leaves its work as a `wip(<id>): <outcome>` commit that fanout.py makes on the lane branch. A plain /chain outside fanout commits nothing and never commits on main.

## 3. Plan
Run planner on the task handoff. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py split .sdlc/<task>`, which writes each `step-<n>/handoff.md` from the newest planner file; never parse the plan by hand.

If `steps.py split` refuses with `plan defect`, the plan is wrong, not the build: append the refusal text to the task handoff under a `## Plan review` heading (create it if missing, keep earlier entries), rerun planner L3 on the task handoff, and split again. After the second such refusal for this task, stop and ask the user. The full split here executes no criteria. The same handling applies to the split in 4.2, including a refusal from `--only N` for a red guard or a guard that changed the work tree.

## 4. Build and verify, one step at a time, in order
After each builder run and each verifier run, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py next .sdlc/<task>/step-<n>` and follow the action on its first line: `build`, `rebuild`, or `bump` → builder at that level; `verify` or `reverify` → verifier at that level; `replan` → the 4.2 path; `swap` → run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py swap .sdlc/<task>/step-<n>`: exit 0 → append one line `swap applied: step <n>: <its stdout line>` to the task handoff's `## Plan review` (create it if missing, keep earlier entries) and run the builder at the level `next` printed (a rebuild: no `## Previous attempt`, never a bump, never counted toward "a second fail"); exit 1 → append its stderr to `## Plan review` and take the 4.2 replan path; `done` → next step; `stop` → ask the user; `inherited` → the gate was already red at the pre-build HEAD (builder Status `inherited red: <tests>`): interactive, ask the user through AskUserQuestion (fix main first, rebuild once main is green, or stop); unattended, stop the task and report the inherited tests. It is never a fail, a rebuild, a bump, or a replan, and never waives the gate. A nonzero exit → stop and report its stderr. `run.sh` exits 3 when the result lacks its required section; the result file still exists, so run `steps.py next` as usual. The rules below are the spec the script implements.

For each step:
1. builder at the step's `level:`.
2. builder Status blocked → skip the verifier (never verify a blocked build) and run planner L3 on the task handoff (replan; it writes a new `planner-L3[-k].md`), move each `step-<n>/` with n at or above the blocked step that already holds builder or verifier output to `step-<n>.superseded-<k>/` (first free k), then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py split .sdlc/<task>` (optionally `--only N` for the steps being rewritten; `--only N` also runs that step's `(guard)` criteria against the current tree and refuses on a red guard or a guard that changed the work tree, a `plan defect` handled like the section 3 split refusal) to write the remaining step handoffs from the newest planner file (earlier plans stay in place; the script refuses a step dir that still holds builder or verifier output, so rename first), continue from the blocked step. A blocked builder is never rerun at the same or a higher level and its step handoff never gets `## Previous attempt`; the replan reads the builder's Notes itself (a Notes line starting with `plan defect:` names the criterion to fix). A replanned step whose builder blocks again on the same finding (same criterion, same root cause) is a recurring finding: append a `recurring finding:` entry quoting both Notes to the task handoff's `## Plan review` before the replan.
3. verifier at the level the rubric derives from the build level.
4. Verdict fail → rebuild the same level once (it writes `builder-L<n>-<k>.md`, so earlier attempts stay for the rubric's "earlier builder-*.md with Status blocked" count), with the verifier's "For the next attempt" appended to the step handoff under `## Previous attempt`. Before a second fail bumps, check whether it is a recurring finding: same criterion and same root cause as the first fail's For the next attempt, after the rebuild addressed it. A recurring finding appends a `recurring finding:` entry quoting both notes to the task handoff's `## Plan review` and takes the 4.2 replan path (planner L3, supersede, split, continue from this step); no bump, no `## Previous attempt`, and it does not count toward a bump. Any other second fail → bump the builder one level and repeat. A fail at L5 → stop and ask the user. Exception: a fail whose `## For the next attempt` starts with `plan defect:` takes the 4.2 replan path (planner L3, supersede, split, continue from this step) unless `steps.py next` prints `swap`, which takes the swap route in item 8; either way it never rebuilds as a fail, never bumps a level, never adds `## Previous attempt`, and does not count toward "a second fail". Every other fail keeps the rule above.
5. A verifier result with no pass/fail `## Verdict` is "no verdict": `steps.py next` prints `reverify`. Rerun the verifier at the same level. It is never a fail, never counts toward "a second fail", and never adds `## Previous attempt`. A second consecutive no verdict at the same build → stop and ask the user.
6. A builder result with no done/blocked `## Status`: `steps.py next` prints `rebuild` at the same level. It is never a fail and never a bump, and a second in a row → stop and ask the user.
7. Builder Status `inherited red: <tests>`: the gate was already red at the pre-build HEAD, and `steps.py next` prints `inherited`. Interactive: ask the user through AskUserQuestion (fix main first, rebuild once main is green, or stop). Unattended: stop the task and report the inherited tests. It is never a fail, a rebuild, a bump, or a replan, and never waives the gate.
8. Criterion swap: a verifier fail tagged `plan defect:` whose `## For the next attempt` holds exactly one `swap old:` line (the defective criterion's command span) and one `swap new:` line (the full replacement criterion) makes `steps.py next` print `swap L<build level>`. Run `steps.py swap` as in the action list above: it checks the pair, rewrites that one criterion line in the step handoff, and reruns the new spans against the built tree; never edit the criterion by hand. Exit 0 → append `swap applied: step <n>: <its stdout line>` to `## Plan review` and rebuild at the printed level, with no `## Previous attempt`, no bump, and no count toward "a second fail". Exit 1 (a refusal, whose last line starts `plan defect:`) → append its stderr to `## Plan review` and take the 4.2 replan path. A swap comes only from the verifier: a builder's `plan defect:` note always replans (item 2), because whoever writes the work never sets its check. One swap per step: a second swap proposal on the same step replans.

## 5. File
Run the /file flow on the task dir. Publishing still needs the user's approval.

## 6. Close out
After File, run the /open-questions flow (`${CLAUDE_PLUGIN_ROOT}/skills/open-questions/SKILL.md`) on the task dir. Items already asked in /file's publishing round are stale and dropped.
- Interactive: ask one batched AskUserQuestion round for everything left unresolved.
- Unattended (headless, no person present): never call AskUserQuestion. List the open items as plain lines in the final report, or say nothing is open.

## Report
At every pause (after the plan, after each verdict, at the end) the whole status message is the /board render for this task: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --task <slug> --waiting "<line>"`, printed verbatim. Never a hand-made status table. Add only the task dir path at the end.
