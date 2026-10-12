# Plan merge replay: goal and fanout on the old and the new skill

Date: 2026-10-12. Ticket: T-0467, step 2.

## Method

The goal ask and the fanout ask of `plugins/sdlc-lite/skills/plan/evals/` (`01-goal.ask.md`, `02-fanout.ask.md`) were each run twice in the T-0467 lane at base `a3e2cd9b`: once by the old skill as written (`plugins/sdlc-lite/skills/plan-goal/SKILL.md`, `plugins/sdlc-lite/skills/plan-fanout/SKILL.md`) and once by the new skill (`plugins/sdlc-lite/skills/plan/SKILL.md`, kind goal and kind fanout). Every run had `SDLC_HEADLESS=1` set, so no question was asked; the Questions column counts the `warn` lines the skill returned in place of a question.

Tickets: `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` printed `ok: 493 tickets, roadmap current`, and the roadmap holds 0 ready tickets. The placeholders were filled with two proposed tickets, `<T-A>` = T-0498 and `<T-B>` = T-0499 (both size L1). `fanout.py run --dry-run` did not refuse the pair, so there is no refusal to record on the `lanes:` line.

Gather, the same for all four runs: `steps.py lane` printed `solo` with `reason: size L1 decides before planning (no planner result yet)` for each ticket; `TIERS` in `budget.py` gives L1 $5. The two `skips.md` files the lane script wrote were removed after the replay. No active goal or KPI covers both tickets, so plan-verification returned `Measured by: none: <reason>`.

Each returned block was piped on stdin to its lint (`plan_check.py goal`, `plan_check.py fanout`) on first return, before any fix. No plan artifact was written to the tree; the blocks are below. The kinds steps, doc and campaign were not run.

This replay was run by the builder of step 2, who read both skills, wrote the blocks and counted the lines. It is unverified: not an independent run. A second session ran it again; see [Independent replay](#independent-replay). The same reader followed the old and the new skill, so the run cannot show a difference a fresh reader would produce.

## Result

| Ask | Skill | Questions | plan_check.py refusals | First-return lint |
|---|---|---|---|---|
| goal | old | 3 warn lines (money cap, authorization, measure) | 0 | `ok: goal plan passes` |
| goal | new | 3 warn lines (money cap, authorization, measure) | 0 | `ok: goal plan passes` |
| fanout | old | 1 warn line (spend cap) | 1 | `warn no-budget: T-0499 has no budget_usd; set one with budget.py set` |
| fanout | new | 1 warn line (spend cap) | 1 | `warn no-budget: T-0499 has no budget_usd; set one with budget.py set` |

Outcome metric (questions and refusals per plan artifact, old against new): goal 3 and 0 against 3 and 0; fanout 1 and 1 against 1 and 1. The table shows no difference between the old and the new skill on these two asks.

Notes on the rows:
- The measure warn line comes from plan-verification, which both skills call; the money cap and the authorization are the skill's own. `01-goal.expected.md` expects 2 questions and counts only the skill's own.
- The one fanout refusal, in both runs: `FAIL overlap: T-0498 (a) and T-0499 (b) both cite docs/reports/2026-10-12-fleet-retro-12.md: put them in one lane or pass --allow-overlap`. Both tickets cite that report as evidence and neither edits it. The fix round added `--allow-overlap`, and the lint then ended `ok: fanout plan passes`.
- The goal lint printed one warning in both runs: `warn no-measure: Measured by is `none`: the goal cannot show the outcome moved`.
- The old and the new skill returned the same goal block and the same fanout block. The new skill added the dry run below.

### Goal block (old and new, as first returned)

```
/goal Overnight: ship T-0498 and T-0499, then stop.

Scope (verify with tickets.py check first):
1. T-0498 agents/planner.md: run each criterion against a reference sibling before shipping
2. T-0499 tickets.py close: no skip entry required for a role with a run record

Outcome: the planner probes each criterion before a plan ships and a close asks for no skip entry for a role that ran. Why: retro 12h rows 5 and 6 cost a blocked L3 build and 4 extra commands per ticket.
Measured by: none: no active goal or KPI covers both tickets and the thread names no measure command.
Rubric:
1. T-0498 done | pass: its check.py or prompt_lint.py case is red first, then check.py exits 0.
2. T-0499 done | pass: the tickets.py selftest case with run records closes, and the no-record case still refuses.
3. No regression | pass: check.sh exits 0 on main.
4. Scope held | pass: only T-0498 and T-0499 are closed by this goal.
Negative control: both ticket checks are red before the change: planner.md lacks the Probe-criteria handle and the selftest case with run records refuses the close.

How to work: lane first with steps.py lane (both tickets print solo); solo for ticket levels L1 and L2; one writer per file; replan cap one, then record a limit; every status claim from a command or a committed file.
A verifier fail means fix and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $5 per ticket (the budget.py L1 cap), a rate or weekly limit, or three 529s in a row. No retry loops.

Authorization: publish, push, and tag are not implied. None of them is authorized.

Done when: tickets.py check exits 0 and T-0498 and T-0499 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md.
```

Returned with it:

```
warn missing-input: no total money cap was given; the block carries only the per-ticket cap from budget.py
warn missing-input: no authorization was given; the block authorizes nothing
warn missing-input: no measure or target was given; Measured by is none
```

### Dry run the new skill printed, goal

```
Dry run (goal)
lint: warn no-measure: Measured by is `none`: the goal cannot show the outcome moved
lint: ok: goal plan passes
cost: $10 of $unknown (2 tickets: T-0498 L1 $5, T-0499 L1 $5); warn: no cap given
```

### Fanout block (old and new, as first returned)

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run --dry-run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
```

Returned with it: `warn missing-input: no spend cap was given`.

After the fix round both lines carry `--allow-overlap` after `--max-lanes 2`.

### Dry run the new skill printed, fanout

Printed after the fix round. The `lanes:` output is verbatim up to the gate line; the driver, close and logs lines that follow (5 lines, with host paths and the full role briefs) are left out here.

```
Dry run (fanout)
lint: warn no-budget: T-0498 has no budget_usd; set one with budget.py set
lint: warn no-budget: T-0499 has no budget_usd; set one with budget.py set
lint: ok: fanout plan passes
cost: $10 of $unknown (2 tickets: T-0498 L1 $5, T-0499 L1 $5); warn: no cap given
lanes: fanout plan (dry run: nothing created)
base: a3e2cd9b273ade52a66978f8e1938ad8e7fae948 (HEAD)
integration branch: fanout/2026-10-12 (new, at the base)
integration worktree: /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/.worktrees/fanout/integration
ticket root in each worktree: .sdlc
lane cap: 2 regular lane(s) of at most 2 (--max-lanes; above 16 also needs --yes-many); stagger: 20 s between lane starts (--stagger)
lane a: branch fanout/2026-10-12-a, worktree /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/.worktrees/fanout/a
  T-0498 0498-planner-run-each-criterion: agents/planner.md: run each criterion against a reference sibling before shipping (retro 12h row 5)
    lane: solo, level L1: sonnet low (size L1 decides before planning (no planner result yet))
lane b: branch fanout/2026-10-12-b, worktree /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/f/.worktrees/fanout/b
  T-0499 0499-close-skips-for-ran-roles: tickets.py close: no skip entry required for a role with a run record (retro 12h row 6)
    lane: solo, level L1: sonnet low (size L1 decides before planning (no planner result yet))
overlap (planned scope): none
overlap (planned scope): not planned, checked at merge time: T-0498, T-0499
gate 1: python3 plugins/sdlc-lite/scripts/check.py
```

## Independent replay

Run by a second builder session (T-0467, step 3) that had not seen the first replay: one reader for old and new, with both old runs written here before the new skill was read. Same asks, same tickets (T-0498, T-0499), same base, `SDLC_HEADLESS=1`.

| Ask | Skill | Run | Questions | plan_check.py refusals | First-return lint |
|---|---|---|---|---|---|
| goal | old | independent | 3 warn lines (total cap, measure, authorization) | 0 | `ok: goal plan passes` |
| goal | new | independent | 3 warn lines (total cap, measure, authorization) | 0 | `ok: goal plan passes` |
| fanout | old | independent | 1 warn line (spend cap) | 1 | `warn no-budget: T-0499 has no budget_usd; set one with budget.py set` |
| fanout | new | independent | 1 warn line (spend cap) | 1 | `warn no-budget: T-0499 has no budget_usd; set one with budget.py set` |

Gather, as this session ran it: `tickets.py --root .sdlc check` printed `ok: 493 tickets, roadmap current`; `steps.py lane` printed `solo` with `reason: size L1 decides before planning (no planner result yet)` for each ticket, and the two `skips.md` files it wrote were removed. Of the three goals in `docs/goals/`, only G-001 is active and its scope is cost rows, so the goal blocks carry `Measured by: none: <reason>`.

### Independent: goal, old skill (`plan-goal`), first return

```
/goal Overnight: deliver T-0498 and T-0499, then stop.

Scope (verify with tickets.py check first):
1. T-0498 agents/planner.md: run each criterion against a reference sibling before shipping
2. T-0499 tickets.py close: no skip entry required for a role with a run record

Outcome: the planner probes each acceptance criterion before a plan ships, and tickets.py close accepts a role that has a run record. Why: a criterion that cannot pass costs a blocked build and a replan, and the false skip refusal costs four extra commands per ticket.
Measured by: none: no active goal or KPI covers both tickets (G-001 is about cost rows; G-002 and G-003 are proposed).
Rubric:
1. Planner handle | pass: a check.py item or prompt_lint.py case fails when planner.md lacks Probe-criteria and passes with it.
2. Close with run records | pass: tickets.py selftest exits 0 with the run-record case, and the case of a role that neither ran nor has a skip entry still refuses.
3. No regression | pass: check.py and generate --check for both hosts exit 0.
4. Scope held | pass: only T-0498 and T-0499 are closed by this goal.
Negative control: on the base tree planner.md lacks the Probe-criteria handle and tickets.py selftest has no run-record case, so rubric lines 1 and 2 are red before any ticket lands.

How to work: lane first with steps.py lane (both tickets are size L1, lane solo); one writer per file; replan cap one, then record a limit; every status claim from a command or a committed file.
A verifier fail means fix and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $5 per ticket (budget.py level L1), a rate or weekly limit, or three 529s in a row. No retry loops.

Authorization: publish, push, and tag are not implied. None of them is authorized.

Done when: rubric lines 1 to 4 pass (no Measured by command exists: none), tickets.py check exits 0 and T-0498 and T-0499 are closed on the lane branch, or the goal stopped on a limit with state written to .sdlc/notes.md.
```

Returned with the block, in place of questions (3):

```
warn: total spend cap not given; the block carries only the per-ticket cap from budget.py
warn: no measure or target given, and no active goal or KPI matches; Measured by is none
warn: authorization not given; written as none authorized
```

`plan_check.py goal` on first return, exit 0:

```
warn no-measure: Measured by is `none`: the goal cannot show the outcome moved
ok: goal plan passes
```

### Independent: fanout, old skill (`plan-fanout`), first return

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run --dry-run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
```

Returned with the block, in place of questions (1):

```
warn: spend cap not given; the level caps from budget.py apply (L1 $5 per ticket)
```

`plan_check.py fanout` on first return, exit 1:

```
FAIL overlap: T-0498 (a) and T-0499 (b) both cite docs/reports/2026-10-12-fleet-retro-12.md: put them in one lane or pass --allow-overlap
warn no-budget: T-0498 has no budget_usd; set one with budget.py set
warn no-budget: T-0499 has no budget_usd; set one with budget.py set
```

`fanout.py run --dry-run` with the same specs and flags exited 0 and printed `overlap (planned scope): none`.

### Independent: goal, new skill (`plan goal`), first return

The new skill's goal reference carries the same field list and example as the old one, so this reader wrote the same block; the one changed phrase is the source named for the per-ticket cap.

```
/goal Overnight: deliver T-0498 and T-0499, then stop.

Scope (verify with tickets.py check first):
1. T-0498 agents/planner.md: run each criterion against a reference sibling before shipping
2. T-0499 tickets.py close: no skip entry required for a role with a run record

Outcome: the planner probes each acceptance criterion before a plan ships, and tickets.py close accepts a role that has a run record. Why: a criterion that cannot pass costs a blocked build and a replan, and the false skip refusal costs four extra commands per ticket.
Measured by: none: no active goal or KPI covers both tickets (G-001 is about cost rows; G-002 and G-003 are proposed).
Rubric:
1. Planner handle | pass: a check.py item or prompt_lint.py case fails when planner.md lacks Probe-criteria and passes with it.
2. Close with run records | pass: tickets.py selftest exits 0 with the run-record case, and the case of a role that neither ran nor has a skip entry still refuses.
3. No regression | pass: check.py and generate --check for both hosts exit 0.
4. Scope held | pass: only T-0498 and T-0499 are closed by this goal.
Negative control: on the base tree planner.md lacks the Probe-criteria handle and tickets.py selftest has no run-record case, so rubric lines 1 and 2 are red before any ticket lands.

How to work: lane first with steps.py lane (both tickets are size L1, lane solo); one writer per file; replan cap one, then record a limit; every status claim from a command or a committed file.
A verifier fail means fix and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $5 per ticket (TIERS in budget.py, level L1), a rate or weekly limit, or three 529s in a row. No retry loops.

Authorization: publish, push, and tag are not implied. None of them is authorized.

Done when: rubric lines 1 to 4 pass (no Measured by command exists: none), tickets.py check exits 0 and T-0498 and T-0499 are closed on the lane branch, or the goal stopped on a limit with state written to .sdlc/notes.md.
```

Returned with the block, in place of questions (3):

```
warn: total spend cap not given; the block carries only the per-ticket cap from budget.py
warn: no measure or target given, and no active goal or KPI matches; Measured by is none
warn: authorization not given; written as none authorized
```

`plan_check.py goal` on first return, exit 0:

```
warn no-measure: Measured by is `none`: the goal cannot show the outcome moved
ok: goal plan passes
```

### Independent: fanout, new skill (`plan fanout`), first return

The new fanout reference states the same lane rules as the old skill. This block was written from that text alone, without using the overlap refusal the old run had already shown this reader, so the equal refusal count is not a second discovery.

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run --dry-run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run a=T-0498 b=T-0499 --lane auto --max-lanes 2 --gate "python3 plugins/sdlc-lite/scripts/check.py"
```

Returned with the block, in place of questions (1):

```
warn: spend cap not given; the level caps from budget.py apply (L1 $5 per ticket)
```

`plan_check.py fanout` on first return, exit 1:

```
FAIL overlap: T-0498 (a) and T-0499 (b) both cite docs/reports/2026-10-12-fleet-retro-12.md: put them in one lane or pass --allow-overlap
warn no-budget: T-0498 has no budget_usd; set one with budget.py set
warn no-budget: T-0499 has no budget_usd; set one with budget.py set
```

`fanout.py run --dry-run` with the same specs and flags exited 0.

Against the first table: every row here has the same Questions count, the same refusal count and the same last lint line as its row there (goal 3 and 0, fanout 1 and 1, old and new).

## Follow-up

- An independent replay of the five plan eval cases by a fresh-context run that did not build the skill, with the old and the new skill read by separate runs (the T-0495 pattern), so the question and refusal counts are measured and not builder-read.
- `plan_check.py fanout` reads a report both tickets cite as a shared file and fails `overlap`, while `fanout.py run --dry-run` prints `overlap (planned scope): none` for the same pair.
