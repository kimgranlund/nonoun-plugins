# Plan doc, plan_done.py and run-plan

Status: built (design T-0410, approved 2026-10-10; build tickets A to D, T-0431 to T-0434). Version 0.2. The first customer plan doc is `docs/work/plan-reliability-docs/plan-doc.md`; its live run is the maintainer's call (section 8). Evidence labels: [V] read in the file or command named, [I] inferred, [D] a decision this design makes for approval.

## 1. Answer in one paragraph

Plan once with a strong model, in one session, into one file: the plan doc. It holds the goal, KPIs, rubric, ordered steps with their ticket sizes and criteria, the authorization, the stop rules and a dollar cap per step. A new linter (`plan_check.py plan`) checks its shape. Then tell any smaller session `/goal complete build and verify <plan-doc.md>`. That session reads the `run-plan` skill, which is a loop over scripts that already exist (`fanout.py prep` and `land`, `dispatch.py`, `steps.py`, `tickets.py`) plus one new script, `plan_done.py`. `plan_done.py` re-derives "is the plan finished" from the ticket, verifier and KPI records, never from the executor's notes, and its exit code is the goal's stop condition. The smaller model carries no judgment the scripts cannot carry: it routes by exit codes, the verifier is a separate sub-agent on a different model family that `dispatch.py prepare` picks, and when the plan needs a decision the run stops with state written. No new agent and no long-lived orchestrator is added.

## 2. Sources

All read for this design [V]: [plan-goal](../../../plugins/sdlc-lite/skills/plan-goal/SKILL.md) and its [goal rules](../../../plugins/sdlc-lite/skills/plan/references/goal.md), [plan-verification](../../../plugins/sdlc-lite/skills/plan-verification/SKILL.md) and its [outcome block](../../../plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md), [plan-campaign](../../../plugins/sdlc-lite/skills/plan-campaign/SKILL.md), [goals and KPIs](../repo-onboarding/goals-and-kpi.md), [plan_check.py](../../../plugins/sdlc-lite/scripts/plan_check.py), [fanout.py](../../../plugins/sdlc-lite/scripts/fanout.py) (module docstring: `prep`, `land`), [dispatch.py](../../../plugins/sdlc-lite/scripts/dispatch.py) (`family`, `recover`, `status`, `resume`), [run_lifecycle.py](../../../plugins/sdlc-lite/scripts/run_lifecycle.py), [conductor.md](../../../plugins/sdlc-lite/agents/conductor.md), [steps.py](../../../plugins/sdlc-lite/scripts/steps.py) (`lint`, `open`, `next`, `verifier-level`), [results.py](../../../plugins/sdlc-lite/scripts/results.py), [levels.json](../../../plugins/sdlc-lite/adapters/claude/levels.json), and the first customer, [the restart and blocked run plan](restart-and-blocked-run-plan.md) with the planner's `docs/work/plan-reliability-docs/plan.md` (8 steps).

Facts the design leans on:

- A `/goal` condition is evaluated by a session stop hook each turn, and it defers while background work runs [goal-rules table, from the host]. The hook reads the transcript, so the condition has to be something the executor runs and prints; I treat the evaluator as a model that reads the transcript [I]. That is why the stop condition is one command with a fixed output line.
- The pasted `/goal` text is not a file: it is capped near 5000 characters by `plan-goal`, cannot be re-read after a crash, and cannot be linted per step [V, plan-goal step 3].
- `steps.py lint` already accepts a whole planner-format plan file by path and printed `steps lint: ok` for `.sdlc/plan-reliability-docs/plan.md` [V, run on 2026-10-09]. Step blocks in the plan doc therefore use the planner's step format unchanged.
- `dispatch.py family` keeps a verifier off the model the work was done on, reading the solo or builder record, so independence is already enforced at dispatch [V, `dispatch.py:205`].
- `fanout.py prep` and `land` already do the per-ticket sequence a plan needs: lane choice, the solo or chain dispatch, the batched verifier command for L2 and L3, the locked merge, gates, close [V, fanout.py docstring].
- `levels.json` holds no Haiku row for solo or builder, and no Claude row is Haiku now (the scout row is `sonnet` low) [V]. A smaller driver session is therefore not a role row, and a Haiku step worker would be a model change, which the maintainer decides [D, section 6].
- The goal 002 plan builds `dispatch.py recover --root`, the one-command restart sweep. Today `dispatch.py recover` and `run_lifecycle.py recover` take one handoff directory [V, restart plan section 1]. The first customer therefore runs before the tool it would use.

## 3. The plan-doc contract

One Markdown file, normally `.sdlc/<plan-slug>/plan-doc.md`; the run records it causes (attempt files, `plan-state.json`) go to the plan folder's records dir (`.sdlc/runtime/tasks/<plan-slug>/`, since 0.23.0). Any path works; nothing reads the location. Goals and KPIs stay in `docs/goals/` and `docs/kpi/` and are cited by id, so durable intent keeps one home and the plan doc holds only execution. The file is a superset of the planner's plan: the H2 sections `## Goal` and `## Step <n>: <title>` keep their meaning and shape, so `steps.py lint` and `split` accept it.

### 3.1 Shape

```
---
id: PD-<slug>
title: <one line>
status: draft | approved | running | done | stopped
goal: G-002                    # a goals/ id, or `none: <reason>`
driver: sonnet-high            # the session that runs run-plan; free text, recorded not enforced
approved_by: maintainer
approved_on: 2026-10-09        # required once status is approved or later
reviewed: <path of a plan-reviewer result>   # required when any step is size L4 or L5
---
## Goal
## Outcome
Outcome: ... Why: ...
Measured by: K-002 (`cmd`), before: 34.3, target: <= 15.
Rubric:
1. ... | pass: ...
Negative control: ...
## Measures
| id | command | read | target | direction | before | when |
## Authorization
## Budget and stop rules
(one `## Step <n>: <title>` block per ticket, see 3.2)
## Upserts
| path | mode | step |
## Later measures
## Done when
Goal line: ...
```

The step blocks are H2 sections of their own, as in the planner format. Sections in order: front matter, Goal, Outcome, Measures, Authorization, Budget and stop rules, the Step blocks, Upserts, Later measures (optional), Done when.

| Section | Holds | Rule |
|---|---|---|
| Outcome | The four lines of the [outcome block](../../../plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md), unchanged | Same two fail rules as a goal block, reused: `outcome-block`, `done-measured` |
| Measures | One row per KPI the plan reads: id, backticked command, `read:` expression, `target`, `direction` (up, down, hold), `before`, and `when` (`now` or `later: <owner>, <date or event>`) | `plan_done.py` runs the command of every `now` row. A KPI file in `docs/kpi/` has the same fields; the plan row is authoritative for the run and a mismatch warns `kpi-drift` |
| Authorization | Exactly what the run may do beyond editing the repository and running checks: publish, push, tag, `onboard.py setup`, external writes. Each is named with its condition, or the section says `None` | Nothing is implied; section 7 |
| Budget and stop rules | A total dollar cap, a per-step cap in each step, the three-529s rule, the rate or weekly limit rule, `replan cap: 1, then stop`, and the state path `.sdlc/notes.md` (or `.sdlc/notes/notes.md`) | The same numbers `plan_check.py goal` already demands, plus the replan cap |
| Step block | Section 3.2 | One step is one ticket |
| Upserts | Every corpus record the run creates, edits or retires, with `mode` (`create`, `edit`, `retire`) and the one step that writes it | One writer per file |
| Later measures | KPIs that move only with elapsed time (a per-retro median), each with owner and date | They do not gate `plan_done.py`; the run never sets a goal `achieved` while one is listed |
| Done when | The command line of section 4 and the stop clause, plus `Goal line:` holding the fenced one-line `/goal` text to paste | A goal line that does not name this file's `plan_done.py` command fails |

### 3.2 Step block

The planner's block, plus key lines under the title that a script can read:

```
## Step 3: prepare --tree names the lane worktree as Tree and base
level: L3
ticket: T-0413                  # an existing id, or `new feature <slug>`
depends: [2]                    # earlier step numbers only
executor: auto                  # auto, or a levels.json row such as solo-L2 or builder-L3
verify: auto                    # auto (size L2 and above), or required
cap: $12                        # dollar ceiling for this step; becomes the ticket's budget_usd
upserts: [docs/references/sdlc-internals.md]
### Read first
### Do
### Acceptance criteria
- (red) `...`
- (guard) `...`
```

`level:` is the ticket size, which `steps.py lane` turns into the lane (solo for L1 and L2 by default [V, AGENTS.md]). For `ticket: new`, `run-plan` runs `tickets.py new` and copies Do and Acceptance criteria into the new handoff once; after a role has read that handoff it is frozen (repository rule) and a change is a replan, not an edit. For an existing ticket the handoff keeps its own Done when and the step's criteria must read `see ticket` or equal it.

### 3.3 The new `plan_check.py plan` rules

`plan_check.py plan [--text T | --file F] [--root .sdlc] [--run]` joins the existing kinds. It prints `FAIL <rule>: <why>` and `warn <rule>: <why>` as they do. `--run` adds the checks that apply only before execution starts. The selftest gets `GOOD_PLAN` (the first customer, shortened) and one mutant per clause, each of which must be flagged as exactly its rule; the live file `docs/work/plan-reliability-docs/plan-doc.md` must also pass. A parser shared by `plan_check.py` and `plan_done.py` lives in a new `plan_doc.py` so the two cannot disagree on what a step is.

| Rule | Fails when | Negative control (a mutant of `GOOD_PLAN`) |
|---|---|---|
| `plan-front` | Front matter lacks `id`, `title`, `status`, `goal`, `driver`, or has a `status` outside its set | `driver:` line deleted; `status: busy` |
| `no-approval` | With `--run`: status is not `approved` or `running`, or `approved_by` / `approved_on` is missing | `status: draft` with `--run`; `approved_on` deleted |
| `outcome-block`, `done-measured` | Reused from the goal check on the Outcome and Done when text | The goal check's own mutants, applied to the plan text |
| `measure-row` | A Measures row lacks id, command, `read`, `target` or `direction`, or its command is not backticked | `target` cell emptied; command unquoted |
| `measure-safe` | A `now` measure command contains `rm`, `git push`, `gh `, `npm publish`, `curl -X`, or writes with `>` (the same words the goal check treats as spending or publishing) | `now` command replaced by one containing `git push` |
| `later-named` | A KPI cited in Outcome or a goal's `kpis:` is in neither Measures nor Later measures | The Later measures row for K-004 deleted |
| `step-shape` | A step lacks `level` (L1 to L5), `ticket`, `depends`, `cap`, or a numbered or bulleted criterion list; or a criterion is vague (the goal check's `VAGUE`) or names no backticked command or file | `cap:` deleted from step 2; a criterion reading "looks good" |
| `depends-order` | `depends` names the step itself, a later step, or an absent number | step 2 `depends: [3]` |
| `cap-sum` | Per-step caps sum above the total cap, or the total cap is missing | A step cap raised so the sum passes the total by $1 |
| `executor-unknown` | A step's `executor:` is neither `auto` nor a row in `adapters/claude/levels.json` for `solo` or `builder` | `executor: haiku-5.5-high` on a step |
| `verifier-seat` | A step sets `verify:` to anything but `auto` or `required`, or any step text assigns verification to the driver | `verify: none` on an L2 step |
| `review-missing` | Any step is size L4 or L5 and `reviewed:` is absent | A step raised to L4 with no `reviewed:` |
| `upsert-shape` | An Upserts row has a mode outside the three, a path outside the repository or outside `docs/`, `plugins/`, `scripts/` and the root entry files, or a path owned by two steps | The same path listed for steps 2 and 4 |
| `upsert-sweep` | A step with `upserts:` has no criterion that runs `git grep` or `docs_check.py` | The sweep criterion of step 3 deleted |
| `authorization` | The goal check's rule, plus: any step or criterion text containing `git push`, `git tag`, `gh pr`, `npm publish` or `onboard.py setup` while Authorization does not name it | Authorization reduced to `None` while step 8 runs `onboard.py setup` |
| `stop-rules` | The goal check's four stop rules (dollar number, three 529s, rate or weekly limit, state path), plus a `replan cap` of 1 | The `replan cap` clause deleted |
| `goal-line` | `Goal line:` is absent, or its text does not contain `plan_done.py` with this file's path and the stop clause | Goal line pointing at another file |
| `done-plan-done` | Done when does not require `plan_done.py` to exit 0, or exit 4 (stopped with state written) | Done when reduced to "all tickets closed" |
| warn `l1-unverified` | An L1 step has `verify: auto` (no independent verifier will run) | n/a (warning) |
| warn `kpi-drift`, `kpi-unresolved` | A Measures row disagrees with the `docs/kpi/` file, or the file is absent | n/a (warning) |

Each FAIL row is a selftest case with the label `plan: <rule> ...`, and the build ticket's criterion 1 is `(red)`: before the change `plan_check.py plan` is an unknown kind (exit 2), after it `GOOD_PLAN` passes and every mutant is flagged. A rule that flags the original `GOOD_PLAN` is a vacuous-failure bug; a mutant flagged as a different rule is a leak between rules, and both fail the selftest.

## 4. `plan_done.py`

`plan_done.py <plan-doc> [--root .sdlc] [--records-only] [--json]`, plus three writers: `plan_done.py stop <plan-doc> --reason R`, `plan_done.py replan <plan-doc> --reason R` and `plan_done.py resume <plan-doc>` (clears the stop record once its cause is fixed, keeps the replan count; T-0438). It is deterministic, calls no model, and reads files and runs only the commands the plan lists as `now` measures.

### 4.1 What it reads

1. The plan, through `plan_doc.py`, after running the `plan_check.py plan` shape rules (a failure is exit 2).
2. Per step, the ticket through the `tickets.py` reader (live or archived `.NNNN-` folder): `status`, size, folder.
3. Per step that needs a verifier (`verify: required`, or `auto` with size L2 or above): the newest verifier result in the ticket's records dir (else the ticket folder, for legacy records) by `order.py`, validated with `results.py` (`Verdict: pass`); the worker's recorded model (the `runs.jsonl` solo record or the builder result header) against the verifier's header model, using the rule `dispatch.family` already applies; and that no solo or builder result is newer than the verifier pass.
4. Per step, `steps.py open <ticket folder>`: held (`unmet-dependency`, `deferred`) criteria. The check spans all steps, because a later step's pass settles an earlier hold.
5. Per `now` measure: the command, then the `read:` expression, then the comparison with `target` in the stated direction. A command that fails, prints no number, or times out reads as unreadable, never as green.
6. Per Upserts row: `create` and `edit` paths exist, `retire` paths are gone from their home or sit in `archive/`.
7. `plan-state.json` in the plan folder's records dir (a legacy copy beside the plan is still read): written only by `stop` and `replan`; it holds `replans`, `stopped` (reason, time, resume command) and nothing else. It never contributes to done.

### 4.2 Truth table

C1 every step ticket is closed. C2 every step that needs one has an independent verifier pass. C3 no held criterion across all step tickets. C4 every `now` KPI is readable and on the right side of its target. C5 every Upserts row holds. S: `plan-state.json` records a stop. "Out" is the last line printed.

| C1 | C2 | C3 | C4 | C5 | S | Exit | Out (last line) | Control (selftest) |
|---|---|---|---|---|---|---|---|---|
| yes | yes | yes | yes | yes | any | 0 | `plan done` | All-green fixture exits 0 and prints `plan done`; the same fixture with any one condition flipped must not |
| no | any | any | any | any | no | 1 | `open: step N: ticket T-x status <s>` | Fixture with one step ticket at `status: ready` exits 1 naming that step; closing it turns the row green |
| yes | no | any | any | any | no | 1 | `open: step N: no independent verifier pass (<why>)` | A verifier pass whose header model equals the worker model, a `Verdict: fail`, and a solo result newer than the pass each exit 1 with their own reason |
| yes | yes | no | any | any | no | 1 | `held: step N: #ref <state> <owner>` | Fixture with one `deferred` criterion exits 1; a later step's verifier pass settling the ref turns it green |
| yes | yes | yes | no | any | no | 1 | `kpi K-002 reads 34.3, target <= 15` | Measure printing 34.3 against `<= 15` exits 1; printing 12 exits 0; printing text or failing the command exits 1 `unreadable`, never 0 |
| yes | yes | yes | yes | no | no | 1 | `upsert: <path> <mode> not satisfied` | A `create` path missing and a `retire` path still present each exit 1 |
| any open | | | | | yes | 4 | `stopped: <reason>; resume: <command>` | A stop record plus one open item exits 4 with the resume command; contrast: a stop record with everything green exits 0 |
| yes | yes | yes | n/a | yes | no | 3 | `records ok; measures not read` (only with `--records-only`) | All-green fixture with `--records-only` exits 3 and never 0 |
| plan fails `plan_check.py plan`, or a step names an absent ticket id | | | | | any | 2 | `plan defect: <rule>` | A plan with one `plan_check.py plan` mutant, and a step naming ticket `T-9999` that does not exist, each exit 2 with `plan defect: <rule>` |

Rules that make the table exact:

- Exit 0 needs every condition, so a stale stop note never blocks a finished plan: the records win over the note. Exit 4 needs a stop record and at least one open item, so a stop note alone never ends a run that could still go on once the cause is fixed.
- Every open item is printed, one line each, before the last line; the executor works from that list, in step order.
- `ticket: new` with no ticket yet is an open item, not exit 2.
- Later measures are printed as `later: K-004 (owner, date)` and never change the exit code.
- `--records-only` is the cheap per-step poll. It cannot exit 0, so it cannot be mistaken for done.
- The Control column is the selftest: one case per row, labelled `plan_done: <row>`, each built from the all-green fixture with exactly one condition changed, so a case that passes for the wrong reason is visible. The build ticket B criterion 1 is `(red)`: before the change the file does not exist, after it every case prints `ok`.

`stop` writes the state file, appends one line to the notes file named in the plan, and exits 0. `replan` increments `replans`; the second call refuses (exit 2), writes the stop record itself, and prints `replan cap reached: stopped`. The cap of one is enforced by a counter in a file, not by the executor remembering it.

### 4.3 The goal condition

The line `plan_done.py` prints for the stop hook, and the text of `Goal line:`:

```
/goal complete build and verify <plan-doc.md> by the run-plan skill: done when `python3 plugins/sdlc-lite/scripts/plan_done.py <plan-doc.md>` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state. Do not end the turn while it exits 1 and an item is open that you can work on.
```

The executor runs the command and shows its output at every step boundary, which is what the stop hook can read [I].

## 5. The `run-plan` skill

Two skills, one concern each: `plan-doc` writes and lints a plan doc with a strong model (it reads `plan-goal`'s inputs, runs `plan-verification` for the outcome block, takes the planner's steps, and ends with `plan_check.py plan`), and `run-plan` executes one. `run-plan` is a short `SKILL.md` that routes, plus `references/run-rules.md` that the executor reads in full. Both skills carry the Codex host note and the `SDLC_HEADLESS=1` rule: never ask, mark the gap, stop.

### 5.1 What the executor reads, files, dispatches, records

Reads: the plan doc, `run-rules.md`, and per step the ticket handoff. Nothing else by default.

The loop, every pass starting from the files and never from memory:

1. Preflight, once per session: `plan_check.py plan <doc> --run` (exit 0), `tickets.py --root .sdlc check`, `dispatch.py recover <handoff dir>` for each step folder that exists (once goal 002 step 4 lands: `dispatch.py recover --root .`), then `dispatch.py status` on the same dirs. An attempt marked interrupted is re-dispatched by a fresh `prepare`; the `resume` ladder (`SendMessage` by name, then `prepare`) applies to a live agent.
2. `plan_done.py <doc>`. Exit 0 or 4: stop and report. Exit 2: stop, plan defect. Exit 1: take the first open item.
3. Step prep: `ticket: new` runs `tickets.py new` and copies the step body; set `budget.py set` from `cap`; claim; write `Lane: <lane> because <reason>` from `steps.py lane`.
4. Dispatch with the existing path: `fanout.py prep <lane>=<id>` prints the dispatch JSON, the executor spawns exactly that JSON (`name`, `model`, `prompt`, `isolation`), then `fanout.py land <branch>` merges, gates and closes. A `full` lane step is driven by `/sdlc-lite:chain` against the lane tree. Independent steps with disjoint Upserts may run as parallel lanes, at most three; the default is one at a time.
5. The batched verifier for L2 and L3 is the command `prep` prints; the executor runs it as printed, `record`s it, and reads `steps.py next`. It never chooses a verifier model or level.
6. Every routing decision after a role ends comes from `steps.py next <step dir>` and from the `dispatch.py record` exit code, as the conductor already does. The skill restates none of that table; it says "follow `steps.py next`".
7. After a step closes, run `plan_done.py <doc> --records-only` and loop to 2.

Records: only what the scripts write (attempt records, `runs.jsonl`, results, `skips.md`) and `plan-state.json` through `stop` and `replan`. The executor hand-writes no JSON and no verdict.

### 5.2 Upserting corpus docs and repairing stale records

The plan names each record in Upserts, and the step's ticket, not the driver, makes the change, in the same ticket that invalidates the record (repository rule: a change that invalidates a record repairs it in the same change). Mechanics, per home:

| Home | Mode | How | Gate the step's criteria carry |
|---|---|---|---|
| `docs/goals/`, `docs/kpi/` | create | next number from the folder listing, front matter per [goals and KPIs](../repo-onboarding/goals-and-kpi.md); never renumber | `docs_check.py --root .` rules G-1 to G-5 |
| `docs/goals/` status | edit | `proposed` to `active` at the first step, to `achieved` only by the close-out step and only when Later measures is empty and every `now` KPI reads right | `docs_check.py`; `plan_done.py` exit 0 |
| `docs/specs/`, `docs/planning/`, `docs/references/` | create, edit | edit in place; the status line moves with the change; the index README row and the managed block of the folder's `AGENTS.md` change through `onboard.py`, never by hand inside the markers | `docs_check.py`, `onboard.py check` |
| `plugins/*/skills/` | create, edit | the skill's own conventions; routing row in the entry skill | `check.py` items, `python3 scripts/check-packaging.py` |
| Entry files (`AGENTS.md`, `CLAUDE.md`) | edit | the managed block through `onboard.py`; text outside the block only when the Upserts row names the file | `onboard.py check` |
| `.sdlc/roadmap.md` | regenerate | `tickets.py roadmap`, never by hand | `tickets.py check` |

Stale-record repair is a planning duty with a mechanical check: the planner lists, per step, every record that names the changed behavior (found with `git grep -l`) in `upserts:`, and `upsert-sweep` refuses a step that lists upserts but carries no `git grep` or `docs_check.py` criterion. The verifier checks the sweep like any criterion. The executor never decides what is stale; it runs the criteria.

### 5.3 Resuming after a crash

Nothing the executor holds is load-bearing. After a host restart or a new session: run the same `/goal` line; preflight recovers orphaned attempts; `plan_done.py` shows what is still open; the loop continues at the first open item. A step whose solo sub-agent died has an interrupted attempt and a lane branch with WIP commits; `fanout.py prep` for that ticket resumes on the existing branch [I, to be verified in the live run], and a verifier that died is dispatched again, never counted as a fail (`steps.py next` prints `reverify`). The most work a restart can cost is the step in flight, bounded by the step's cap.

Bootstrapping note: goal 002 is the first customer and builds the sweep (`dispatch.py recover --root`), so its first run uses the per-directory recovery and the maintainer is present at restarts. Section 8 makes that an explicit live-run condition.

## 6. Model-agnostic executor

Two seats, kept apart:

| Seat | Set by | What it does | Options |
|---|---|---|---|
| Driver | the person who starts the session (`claude --model <m> --effort <e>`), recorded in front matter `driver:` | Runs `run-plan`: the loop above | Haiku 5.5 high, Sonnet low, Sonnet high, or the model and effort of any builder row in `levels.json` |
| Worker | each step's `executor:` | The solo or builder sub-agent that edits | `auto` (the row `steps.py lane` and the ticket size pick: solo L1 sonnet high, L2 opus medium, L3 opus high [V levels.json]) or a named row |

`driver:` is not enforced by any script, because the session already exists when the plan is read; `run-plan` prints it and warns when the running model is not the stated one. `executor:` is enforced by `executor-unknown`: only rows that exist. Haiku 5.5 as a worker is not a row, adding one is a model and effort change the maintainer authorizes in its own ticket, and until then a Haiku-driven run uses `auto` workers [D, repository invariant: model and effort defaults are user decisions].

Minimum the driver must do, each testable in the live run:

1. Follow a numbered procedure and branch on an exit code, without inferring intent.
2. Call Bash and Read, write the plan's named files only through scripts, and call the Agent tool with a printed JSON unchanged (`name`, `model`, `prompt`, `isolation`).
3. Print command output verbatim so the stop condition is visible.
4. Stop when a script says stop (exit 2, 4, 5 of `prepare`, a second replan, a spend limit) and write state instead of improvising.

What stays with a stronger or separate seat:

| Work | Seat | Why |
|---|---|---|
| Writing and approving the plan | the planning session and the maintainer | The plan is the only place judgment enters |
| Plan review of an L4 or L5 step | plan-reviewer, a different family from the planner, before approval (`reviewed:`) | Existing rule: plan review is for L4 and L5 only |
| Verification of every L2 and above step | the verifier `dispatch.py prepare` chooses (L2, or L3 for L4 and L5, merge, security or pinned-string tickets) | Independence; the driver never selects or reads the level |
| The one replan after a block or plan defect | planner L3, dispatched through `dispatch.py prepare`, at most once (`plan_done.py replan`) | A replan is design work |
| Merge conflicts, inherited red, `steps.py next` printing a stop | stop with state; the maintainer decides | No person is present, so a decision is a stop, not a guess |

## 7. Guardrails

1. The executor never grades itself. The verifier is a separate sub-agent started only by the printed dispatch (the spawn gate in `hooks/block-role-spawn.sh` denies an `sdlc-lite:<role>-L<n>` spawn without a matching dispatch record [V, conductor.md]); `dispatch.family` keeps it off the worker's family; `plan_done.py` re-checks the family and the order of results from records; `verifier-seat` forbids a plan that assigns verification to the driver. The driver edits no product file.
2. Publish, push, tag, `onboard.py setup` and external writes happen only when Authorization names them with their condition. `authorization` fails a plan whose steps contain such a command that Authorization does not name. At run time `run-plan` reads Authorization first and treats any command outside it as a stop.
   Limit [V conductor.md, hooks/_role.sh]: `block-publish.sh` applies only when `SDLC_ROLE` is set or the caller is a pipeline sub-agent; an interactive driver session has neither, so the hook does not guard the driver itself. The `run-plan` skill therefore tells the person to start an unattended driver with `SDLC_ROLE=conductor` and `SDLC_HEADLESS=1` exported, and the skill's first preflight line prints `SDLC_ROLE` so a missing value is visible [D]. Whether the `/goal` evaluator environment honors those variables on a live session is unverified and is a live-run item.
3. Replan cap is one: `plan_done.py replan` counts in a file; the second call stops the run and writes state. A recurring finding (same criterion, same root cause) is a replan of the plan, never a level bump, as the conductor already rules.
4. Spend: `cap` becomes the ticket's `budget_usd`; the budget gate exits 4 at 80 percent with no ack, which `run-plan` treats as a stop; the total cap is checked against the sum of ticket spend by `budget.py` before each step. No ack is ever invented.
5. State on stop: `plan_done.py stop` writes `plan-state.json` and the notes line, so a stopped run is a known state and exit 4 is a valid end of the goal. `plan_done.py resume` is the only way back from it.
6. The executor never asks a person. `AskUserQuestion` is not used; a missing input is a plan defect found by `plan_check.py plan --run` before the run starts.
7. A new idea becomes a new ticket, not a larger step; a step whose ticket is frozen is changed only by the one replan.

## 8. The build, split into tickets

All four are filed after the maintainer approves this design, in this order. `check.py` and `check.sh` are shared hot files, so one writer at a time and one lane.

| # | Ticket | Size | Files changed | Done when |
|---|---|---|---|---|
| A | Plan-doc parser and `plan_check.py plan` | L2 | new `plugins/sdlc-lite/scripts/plan_doc.py`; `plan_check.py` (kind `plan`, `GOOD_PLAN`, mutants, usage and docstring); `check.sh` (the `plan_doc.py` selftest line); `check.py` (item for the new selftest and the list of mutants) | `(red)` `plan_check.py plan` is unknown now; after, `plan_check.py selftest` exits 0 and prints one case per rule of 3.3; `steps.py lint` accepts a plan doc; `check.sh` exits 0 |
| B | `plan_done.py` | L2 | new `plugins/sdlc-lite/scripts/plan_done.py`; `check.sh` and `check.py` wiring; `docs/references/sdlc-internals.md` (one paragraph) | `(red)` the file does not exist now; after, `plan_done.py selftest` runs one case per row and per control of 4.2; `stop` and `replan` second-call refusal covered |
| C | The `plan-doc` and `run-plan` skills | L2 | new `plugins/sdlc-lite/skills/plan-doc/SKILL.md` and `references/plan-doc-format.md`; new `skills/run-plan/SKILL.md` and `references/run-rules.md`; `skills/sdlc-lite/SKILL.md` (two routing rows and the Codex translations); `agents/conductor.md` (one routing line) and the generated `adapters/codex/agents/sdlc-conductor-l1.toml` through `codex_roles.py generate`; `check.py` (new item: both skills name `Gather` or `Read`, `plan_check.py plan`, `plan_done.py`, `Unattended`, `Codex host`, `SDLC_ROLE`; no reference to another plugin); `plugins/sdlc-lite/AGENTS.md` if it lists scripts or skills | `check.py` item passes and fails when each phrase is removed; `codex_roles.py generate --check` and `python3 scripts/check-packaging.py` exit 0 |
| D | Docs and the first customer plan doc | L1 | `docs/specs/sdlc-lite/plan-doc-executor.md` (status to built); `docs/specs/sdlc-lite/README.md` and the managed block of `AGENTS.md` (through `onboard.py`); `docs/README.md` row; `docs/work/plan-reliability-docs/plan-doc.md` (the goal 002 plan wrapped in this contract) | `docs_check.py --root .` and `plan_check.py plan ... --run` exit 0 |

Not changed: model and effort rows, `levels.json`, `models.json`, `dispatch.py`, `steps.py`, `fanout.py`, `tickets.py`, `results.py`, hooks, any version number. A and B are independent in code (they share only `plan_doc.py`), but A lands first because B imports it.

Version targeted: 0.22.3 or later, the release owner's call.

### 8.1 Live-run plan, goal 002 as first customer

The structural checks (`plan_check.py plan`, `plan_done.py` selftest) do not show that a small model finishes unattended work, so the live run is part of the acceptance of ticket C, recorded in `docs/reports/<date>-plan-doc-live-run.md`. If a step cannot run it is reported unverified, not substituted.

The first live run and rehearsal are recorded in `docs/reports/2026-10-11-plan-doc-live-run.md`.

1. Dry state. Wrap `docs/work/plan-reliability-docs/plan.md` as `plan-doc.md` (its steps 3, 4, 6 and 7 already have tickets T-0413, T-0414, T-0416, T-0417 [V, roadmap]; the others are `ticket: new`). `plan_check.py plan --run` exits 0. `plan_done.py` on the unstarted plan exits 1 and lists every step open (the plan's own negative control: red before any work).
2. Throwaway rehearsal, no repo risk. In a scratch project, a two-step plan (an L1 doc line and an L1 script fix, one `verify: required`) driven by the cheapest candidate driver, Haiku 5.5 high. Pass: `plan_done.py` exits 0; the verifier model differs from the worker's; zero `AskUserQuestion` calls; the driver edited no product file.
3. Crash drill on the rehearsal. Kill the session after the first solo is spawned and again during the verifier. Restart with the same `/goal` line. Pass: the second session finishes; no step is built twice; each step has exactly one passing verifier result; `dispatch.py status` shows interrupted attempts re-dispatched, not failed rows.
4. Guardrail probes, each a negative control. A plan whose step runs `git push` without authorization fails `plan_check.py plan`. A second `plan_done.py replan` refuses and writes the stop record. A step cap set to $1 stops the run at the budget gate with state written and exit 4.
5. Goal 002 run. The driver is the maintainer's choice from section 6 (the design recommends Sonnet high for this run, because it is the first plan that builds the recovery tool the run depends on, and moves to Haiku after it passes), with the maintainer present for restarts. Steps run in the plan's order and lanes (steps 2 to 4 in one dispatch lane). Pass: `plan_done.py` exits 0 or exits 4 with a state that names the real limit; K-002 to K-004 are read (K-002's per-retro median is a Later measure, so G-002 stays `active`).
6. Record per run: dollars against the sum of caps, wall minutes, driver turns, human interventions (target 0 outside the planned restarts), self-grade or out-of-authorization attempts (target 0). Compare dollars with the same steps through `/chain` only if the maintainer wants the cost comparison; it is not required.

## 9. Rejected alternatives

- Extend `plan-goal` only. Rejected: its output is pasted text capped near 5000 characters, so eight steps with criteria do not fit; text in a stop hook cannot be re-read after a crash or compaction, so a smaller model loses the plan exactly when it needs it; nothing can lint a step inside it; and `check.py` item 31 fixes the phrase set of every block-returning plan skill, so a plan-document mode inside `plan-goal` would couple two concerns. The cost of the separate pair of skills is one more read. `plan-goal` stays the way to write a goal for tickets that need no plan document.
- A new long-lived orchestrator agent. Rejected: it keeps run state in its own context, which a restart destroys (the problem goal 002 measures); it adds a model seat and a dispatch hop with no failure in evidence that needs it; and the conductor already routes, dispatches and applies escalation, with the rule to stay thin. State in files plus a derived stop condition gives resumption with no seat to keep alive.
- A model-evaluated "is it done". Rejected: asking the smaller model, or the `/goal` evaluator alone, whether the plan is finished is the executor grading itself; `plan_done.py` answers from records.
- Put steps only in the tickets. Rejected: one outcome spans several tickets, and the stop hook reads the goal text, not ticket files; it is the same gap `plan-verification` found.

## 10. Risks and decisions for the maintainer

- Decision: the driver for the goal 002 run (recommended Sonnet high first, then Haiku 5.5 high on a plan with no recovery dependency). Default if unanswered: Sonnet high.
- Decision: whether Haiku 5.5 is also allowed as a step worker. It needs a `levels.json` row and a `models.json` row, which are model and effort changes outside this design. Default: no.
- Decision: an L1 step has no independent verifier by default (`verify: auto` covers L2 and above, as `solo.md` has it); `l1-unverified` warns. Set `verify: required` per step to change that. Default: as stated.
- Risk: the `/goal` evaluator reads the transcript, not the exit code [I]. If it also defers while background work runs, a driver that backgrounds a role looks idle; the skill runs roles in the foreground under `SDLC_HEADLESS=1` as the conductor already does for headless runs.
- Risk: `SDLC_ROLE` cannot be set from inside a running session, so publish protection of the driver itself is by instruction and by `authorization` linting until the person starts it with the variable (section 7, item 2). A launcher script that sets it is a follow-up if the live run shows the gap matters.
- Risk: a KPI that moves only with time cannot gate a plan; it sits in Later measures and the goal stays `active`. That is deliberate, and it is how goal 002 reads today ("until then this line is open").
- Risk: a lane worktree that died mid-step may need a manual look. The live run item 3 measures whether `fanout.py prep` resumes it; if not, a ticket is filed rather than guessing here.
- Limits: sizes in section 8 are estimates. The 0.22.3 sweep (`dispatch.py recover --root`) is assumed only after goal 002 step 4; this design works without it, per directory. Nothing here changes any model, effort or version.
