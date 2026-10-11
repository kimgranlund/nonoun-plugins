# Plan doc live run (T-0433, items 1 to 4 of section 8.1)

Recorded: 2026-10-10. Design: [plan-doc-executor.md](../specs/sdlc-lite/plan-doc-executor.md) section 8.1. Material assessed: the `plan-doc` and `run-plan` skills as built by T-0433, `plan_check.py plan` and `plan_done.py` at the base commit 8edb33de. Driver: Haiku 5.5 high (`claude -p --model claude-haiku-5-5 --effort high`, `SDLC_ROLE=conductor`, `SDLC_HEADLESS=1`, `--plugin-dir` on the worktree plugin), the cheapest candidate of section 6. Workers and sub-agents: the model `fanout.py prep` printed (Sonnet low for an L1 solo). Item 5 (the goal 002 run) is not part of this ticket.

## Result in one table

| Item | Result |
|---|---|
| 1 Dry state | Partly met. `plan_check.py plan --run` exit 0; `plan_done.py` exit 1, but not every step open (below) |
| 2 Rehearsal | Not met. Step 1 built and closed; step 2 never started; `plan_done.py` never exited 0 |
| 3 Crash drill | Partly met. No step built twice after the fix to the run rules; the first attempt rebuilt step 1; the verifier kill is unverified |
| 4 Guardrail probes | Met at script level: all three negative controls fired. Driver behavior at the budget gate is unverified |

Every red below was a gap in the design or the run rules, and none was a model failure: the Haiku driver followed the printed commands, edited no product file, called `AskUserQuestion` zero times (checked in every stream log), and stopped with state written each time a script refused. Cost: about $0.02 to $0.15 per driver run (seven runs, under $0.5 in total), wall time 40 to 90 seconds per run.

## Item 1: dry state

The goal 002 plan was wrapped in a scratch file (not at `.sdlc/plan-reliability-docs/plan-doc.md`, which T-0434 writes) by a script that adds front matter, Outcome, Measures, Authorization, Budget and stop rules and the key lines `ticket`, `depends`, `executor`, `verify`, `cap` to the eight step blocks of the planner's `plan.md`. Steps 3, 4, 6, 7 take T-0413, T-0414, T-0416, T-0417 as the design says; steps 1, 2, 5, 8 are `ticket: new`.

- `plan_check.py plan --file <wrap> --run`: exit 0, one `warn l1-unverified` (step 7).
- `plan_done.py <wrap> --root .sdlc`: exit 1. Open items: steps 1, 2, 5, 8 (ticket not created), step 3 (a solo or builder result is newer than the verifier pass), step 6 (`verifier-L2.md` has no role header). Steps 4 and 7 read green.
- Finding: the premise that the goal 002 tickets are unbuilt is stale. T-0411 to T-0417 are all closed in this repository (`.sdlc/roadmap.md`), so the dry state is not the plan's own red-before-work control any more, and the first customer plan doc of T-0434 would describe work that is already done. T-0434's wrap and the maintainer's choice of a first customer need a decision.
- `steps.py lint` on the scratch wrap reports `### Read first lists a path that does not exist` for repository-relative paths, because the file sits in `/tmp`; it resolves in the repository.

## Item 2: throwaway rehearsal

Scratch project `/tmp/pd-live/scratch`: `calc.py` with `add` subtracting, `test_calc.py`, `README.md`, a two-step plan (step 1 an L1 doc line `ticket: new chore doc-line`; step 2 an L1 fix `ticket: new bug fix-add`, `verify: required`), `failures.py` as the one `now` measure (prints 1). `plan_check.py plan --run` exit 0; `plan_done.py` exit 1 with both steps open.

What the Haiku driver did correctly in all runs: printed `SDLC_ROLE` and `SDLC_HEADLESS`; read the plan doc and run-rules; ran preflight; created the ticket with `tickets.py new`; copied Do and criteria into the handoff once; `budget.py set`; `steps.py lane`; committed the claim; `fanout.py prep`; spawned the Agent with the printed JSON; `fanout.py land`; and, when a script refused, `plan_done.py stop` with the refusal's words. It never ran a command outside Authorization (None) and edited only ticket handoffs (the step's own Do text), no product file.

Where `plan_done.py` could not reach exit 0, each time a gap in the contract:

1. Land target. `fanout.py land` merges and closes on the integration branch (`fanout/<date>`), not on the checkout `plan_done.py` reads, so step 1 stayed `proposed` and the driver stopped. The run rules now say to fast-forward the starting branch to the integration branch after `land` and then remove the integration worktree. The design is silent on this.
2. Lane branch name. `prep` prints the branch `worktree-<id>-solo`; the host made `worktree-agent-<id>`, so the printed `land` command refused. The run rules now say to land the branch `git worktree list` shows, changing only the name.
3. Integration branch reuse. After step 1 landed, `prep` for step 2 refused (the integration branch was still checked out, and then it did not hold step 2's claim commit: `lanes see only committed files`). A plan with `ticket: new` steps claims a later ticket on the starting branch after the integration branch was cut, so a second `prep` the same day needs the integration branch moved to the starting branch first. This is open: no rule is written for it, because the right fix (a `fanout.py` flag, a per-step integration branch name, or one `prep` for all tickets of a lane) is a design choice.
4. Resume after a stop. `plan_done.py` returns exit 4 for any stop record while an item is open, and nothing clears a record, so a fixed cause plus the same `/goal` line ends at once. The run was continued by deleting `plan-state.json` by hand (a human intervention). The design says a stop note alone never ends a run that could still go on, but its truth table has no row for a stale record.
5. A verifier for an L1 step with `verify: required` is not printed by `prep` (it prints one for L2 and L3 only). The run rules now give the `steps.py verifier-level` and `dispatch.py prepare --tree` route; it was not reached, so it is unverified.

Pass criteria of item 2: `plan_done.py` exit 0 not met; verifier model differs from the worker: unverified (no verifier ran); zero `AskUserQuestion` calls: met; the driver edited no product file: met.

## Item 3: crash drill

A Python harness (`drill.py`) started the same `claude -p` driver line, waited for the first Agent spawn whose `subagent_type` matched, waited 30 s (20 s for the verifier trigger), then SIGKILLed the driver's process group.

- Kill after the first solo spawn: done twice. The solo had made its commit on its lane branch before the kill (`T-0001: Add a Usage line to the README`).
- Restart with the same line, first attempt (before the run rules named lane branches): the driver spawned a second solo for step 1, so the step was built twice and two lane branches existed. `fanout.py prep` does not resume the branch of an interrupted solo, which was the design's assumption [I] in section 5.3 (to be verified in this run). Not verified, refuted.
- Restart, second attempt (after adding the lane-branch check to the run rules): one solo commit, one merge, `close T-0001`; no step built twice. Step 2 then hit gap 3 above.
- Kill during the verifier: unverified. Step 2 never reached a verifier, so no verifier was spawned to kill.
- `dispatch.py recover --root .` ran in preflight (it exists in this plugin version) and reported `no orphaned attempts`. `fanout.py prep` records a solo dispatch without an attempt record, so there is no interrupted attempt for a killed solo to show; `dispatch.py status` shows nothing for it.

## Item 4: guardrail probes (negative controls, script level)

| Probe | Result |
|---|---|
| A step criterion that runs a push command with Authorization `None` | `plan_check.py plan --run` exit 1: `FAIL authorization: step 1 runs git push but Authorization does not name it` |
| A second `plan_done.py replan` | First call `replan 1 of 1` exit 0; second prints `replan cap reached: stopped`, exit 2, writes the stop record; `plan_done.py` then exits 4 |
| A step cap of $1 | `budget.py set --usd 1` plus $0.90 of recorded spend: `fanout.py prep` exit 4 `blocked: budget gate: budget.py ack`, no dispatch; `plan_done.py stop` exit 0, then `plan_done.py` exit 4 with the reason. Unverified: a Haiku driver following that stop (the rehearsal reached stops by other causes) |

Side note: the `resume:` command that `plan_done.py` prints is the repository-relative `plugins/sdlc-lite/scripts/plan_done.py`, which does not exist in a consumer install.

## Authorization and environment

`SDLC_ROLE=conductor` and `SDLC_HEADLESS=1` were exported for the driver, so the publish hook guarded it. Whether an interactive `/goal` evaluator environment honors those variables is unverified: the runs used `claude -p` with the goal text as the prompt, not `/goal`, so the stop hook (evaluation of the `plan done` condition each turn) was never exercised.

## Open items for the maintainer (new tickets, not part of T-0433)

1. The `fanout.py prep` and `land` sequence for several tickets of one plan (gap 3), including whether `prep` resumes an interrupted solo (gap in section 5.3).
2. A way to clear a stale stop record, or a `plan_done.py` row for it (gap 4).
3. Whether the goal 002 plan is still a first customer (all of T-0411 to T-0417 are closed).
4. Re-run items 2 and 3 once 1 and 2 land, with a verifier kill.
