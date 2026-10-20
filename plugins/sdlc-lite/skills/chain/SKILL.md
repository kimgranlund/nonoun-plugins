---
name: chain
description: "Drive one task through the whole loop: optional scout, research, and architect, then plan, then build and verify each step with escalation, then finish loose ends, file, and close out in one question round. Use when a task should run end to end."
argument-hint: "<handoff.md|goal>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/order.py:*), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*), Agent, Read, Write, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

For every role launch, pass `--routing-reason` to `dispatch.py prepare` (Codex: `SDLC_ROUTING_REASON`) as the selected role/level rationale, including the recorded cause of any escalation or replan. Read shared run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md` for readiness, attempt records, safe recovery, and `Run a role from a temporary worktree`.

Arguments: `$ARGUMENTS`

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `<handoff.md\|goal>` | The task handoff, or the goal a task handoff is created from | - | `.sdlc/add-retry/handoff.md` |

Every role is dispatched from the project root as a sub-agent, in three steps (the full contract is in `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md`, "How you run roles"): `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare <role> <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes the printed `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --transcript <sub-agent transcript jsonl> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message (the one-line pointer `<role> <status> <path>`) on stdin, validates and records the result file; record each role before you prepare the next. Below, "run" a role, or "dispatch" it, means those three steps, and "the result" is `<role>-<level>.md` next to the handoff. On Codex a role runs through `SDLC_BACKEND=codex run.sh <role> <level> <handoff.md>` as the Codex adapter describes. Levels follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`; layout follows `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`. You orchestrate; you never do a role's work yourself. Headless (`SDLC_HEADLESS=1`) spawns run in the foreground; interactive spawns run in the background (`run_in_background: true`), and you wait for the completion notification, never `sleep`. How to spawn, when to prune, and how `dispatch.py advance` chains record, prune, `steps.py next`, and the next prepare in section 4: read `references/dispatch.md` before the first spawn.

## Lean chain
A ticket of level L1 or L2 can run as a lean chain: the same roles with one or two coarse steps.

Lean conditions, when the full chain is mandatory, what lean changes, and what `steps.py lane` computes: `references/lean-chain.md`.

Close-out: the lean lane closes through tickets.py close, which checks each step's verifier verdict and writes the Outcome; sections 5 to 7 apply.

## 1. Brief
Get or create `<task dir>/handoff.md`, where `<task dir>` is `<task>/` in the work root (`.sdlc` by default, `docs/work` with `work_root: docs/work`). If it lacks context a clean agent would need, ask the user before running anything.

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
Run planner on the task handoff. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py review .sdlc/<task>` and follow the action on its first line:
- `split` → run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py split .sdlc/<task>`, which writes each `step-<n>/handoff.md` from the newest planner file; never parse the plan by hand. A review whose findings are all `- step <n>: notes-fix: <text>` lines reads as `pass` (never a replan): `split` appends them to that step's handoff under `### Notes`.
- `amend` → every finding of the newest review is `criterion-only`: run `steps.py split .sdlc/<task>` as for `split`; it amends each criterion in place and logs it. No planner run and no replan spent (`references/plan-review.md`).
- `review L1` → dispatch plan-reviewer L1 on `<task dir>/handoff.md`, then `steps.py review` again. If `dispatch.py prepare` exits 2 with `specgate:` lines on stderr (Codex: `run.sh`), `specgate.py check` refused the plan before any spawn: append those lines under `## Plan review` and replan as for a `steps.py split` `plan defect` (below).
- `replan` → append to the task handoff's `## Plan review` (create it if missing, keep earlier entries) one line `plan review: replan: <result path>` and one `plan review: replan: <finding>` line per `## Findings` item of that result, rerun planner L3 on the task handoff, then `steps.py review` again (a replan is reviewed only when it holds an L4 or L5 step).
- `stop` → interactive: one AskUserQuestion carrying the reviewer's `## Missing decisions` (a `blocked` verdict), or whether to replan once more (a second `replan` verdict), or the plan's `unresolved:` assumption; unattended: stop the task and report the reason line.

A rejected plan (`replan` or `blocked`) is never split, the second design `replan` stops, and only the user can lift a `replan` verdict (`--override-review`). A `replan cap:`, `step cap:`, or `time budget:` refusal is never a `plan defect` and never answered with a replan: ask the person, or stop `blocked` unattended. A `plan defect` refusal from `steps.py split` (also from `--only N` on a red guard or a guard that changed the work tree) appends the refusal under `## Plan review` and reruns planner L3. The rules for each: `references/plan-review.md`.

## 4. Build and verify, one step at a time, in order
Resume: a /chain run on a task that already has `step-<n>/` dirs first checks for stale attempts. On a step dir whose attempt is stale and needs explicit recovery (always on Codex native transport; see shared run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md`), run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py recover <task dir>/step-<n>` (Codex: `run_lifecycle.py recover`; `dispatch.py status <step dir>` lists the attempts; after a host or session restart, `dispatch.py recover --root .` sweeps every attempt under `.sdlc` at once), then inspect that step's artifacts and the working tree. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py resume .sdlc/<task>` and continue from the step dir on its first line, following the action on its second line as below (`replan` takes the 4.2 path; `done` alone means every step passed, so go to section 5). Never start from the newest or highest step dir. A task with a plan but no `step-<n>/` dir returns to section 3 (`steps.py review`).

After each builder run and each verifier run, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py next <task dir>/step-<n>` and follow the action on its first line (on Claude, `dispatch.py advance` runs it). The actions (`build`, `rebuild`, `bump`, `verify`, `reverify`, `replan`, `resplit`, `swap`, `amend`, `done`, `stop`, `inherited`, `invalid result:`) and what each runs are in `references/step-rules.md`; read it before acting on any action other than `build`, `verify`, or `done`.

For each step:
1. builder at the step's `level:`.
2. builder Status blocked → skip the verifier (never verify a blocked build), replan with planner L3, supersede each step dir at or above it, `steps.py split` (optionally `--only N`, which refuses on a red guard or a guard that changed the work tree), and continue from the blocked step. A block on a file outside scope takes item 9; an amend pair takes item 10. A repeat block on the same finding is a recurring finding: log `recurring finding:` under `## Plan review` first.
3. verifier at the level the rubric derives from the build level.
4. Verdict fail → rebuild the same level once with `## Previous attempt`; a second fail bumps one level, unless it is a recurring finding (`recurring finding:` under `## Plan review`, then the 4.2 replan path). A fail at L5 → stop and ask the user. A `plan defect:` fail replans unless `steps.py next` prints `swap` (item 8).
5. A verifier result with no pass/fail `## Verdict` is "no verdict": `steps.py next` prints `reverify`. Rerun the verifier at the same level. It is never a fail, never counts toward "a second fail", and never adds `## Previous attempt`. A second consecutive no verdict at the same build → stop and ask the user.
6. A builder result with no done/blocked `## Status`: `steps.py next` prints `rebuild` at the same level. It is never a fail and never a bump, and a second in a row → stop and ask the user.
7. Builder Status or verifier Verdict `inherited red: <tests>` → `steps.py next` prints `inherited`: ask the user (interactive) or stop and report (unattended). Never a fail, rebuild, bump, replan, or reverify, and never waives the gate.
8. Criterion swap: a verifier `plan defect:` fail with one `swap old:`/`swap new:` pair → run `steps.py swap`; never edit the criterion by hand. One swap per step.
9. Scope widening: a builder blocked only by a file outside the step's scope criterion, when the file serves the task goal → run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py widen <task dir>/step-<n> <path>...`; never record the decision as prose alone.
10. Criterion amend: a builder blocked by one defective criterion of an unbuilt step, with one `amend old:`/`amend new:` pair → `steps.py next` prints `amend`; run `steps.py amend`. It is the task's one replan.
Every exit code, log line, and count rule for items 2 and 4 to 10: `references/step-rules.md`.

## 5. Loose ends
After the last planned step is `done`, finish small leftovers inside the task's Goal here, in this run, instead of filing them as tickets. No filer runs here.
1. Collect the items from the passed steps' builder and verifier `## Notes`: the `fix-now:` lines, plus leftovers that a doc line, one test, a guard, or a one-file fix settles, inside the task's Goal. Leave out anything that widens scope, needs a design choice, or needs the user; those stay `decide:` or `note:` follow-ups.
2. Nothing collected → section 6. Otherwise write `<records-dir>/step-<n+1>/handoff.md` yourself from the step template in handoff-format, titled `## Step <n+1>: Loose ends`, with a `### Read first` subsection, and lint it; never run `steps.py split` for this step. The handoff rules: `references/loose-ends.md`.
3. Run the builder, then the verifier at the level `steps.py next` prints. `done` → section 6. Any other outcome → one report line `loose end not finished: <item>: <reason>` and a `skip: verifier` entry in `skips.md`; never a rebuild, a bump, a replan, or a question (`references/loose-ends.md`).

## 6. File
Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <task> --dry-run` and mark its lines per /file 3.2, with no filer dispatch. The dry run checks the verdict gate and lists the verifier `## Notes` follow-ups. A refusal stops the run and is reported. Run /file (the filer) only when the user asks for a PR draft. Hold the close (3.3 to 3.5) and the publish question (step 4) for section 7.

## 7. Close out
Run the /open-questions flow (`${CLAUDE_PLUGIN_ROOT}/skills/open-questions/SKILL.md`) on the task dir to collect what is still open. Drop items the /file questions below already cover.
- Interactive: make one AskUserQuestion call carrying the /file decide question (which `decide:` follow-up becomes the one ticket, 3.3), the /file publish question (step 4), and up to two open-questions items: at most 4 questions per call. Then close per /file 3.4 without `--filer`, adding `--changed "<one line from the task Goal>"` (`--ticket N --expect <digest>` when the user picked one), do only the publishing the user approved, and resolve the open items.
- Unattended (headless, no person present): never call AskUserQuestion. /file 3.5 decides the close, without `--filer` and with `--changed "<one line from the task Goal>"`, nothing is published, and the open items go in the final report as plain lines, or say nothing is open.

## Report
At every pause (after the plan, after each verdict, at the end) the whole status message is the /board render for this task: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py --task <slug> --waiting "<line>"`, printed verbatim. Never a hand-made status table. Add only the task dir path at the end.
