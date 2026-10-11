---
id: PD-plan-doc-hardening
title: Plan-doc executor run-rules hardening
status: approved
goal: none: fixes found by the 2026-10-11 live run, rehearsed through the executor itself
driver: sonnet-low
approved_by: maintainer
approved_on: 2026-10-11
---
## Goal
Close two gaps the live run found in the run-plan run rules (a driver started outside the plan's repository, and a step whose work already exists), and record the findings in the design doc, as two L1 steps built by the executor.

## Outcome
Outcome: a smaller driver stops or proceeds correctly from the run rules alone in two cases that stalled the live run. Why: both cases cost a run with no rule to follow.
Measured by: M-1 (`git grep -c 'show-toplevel' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`), before: 0, target: >= 1.
Rubric:
1. Wrong-repo preflight | pass: run-rules.md names `git rev-parse --show-toplevel` in Preflight and a stop when it differs from the plan doc's repository.
2. Already-built rule | pass: run-rules.md says a solo that reports no diff possible because the (red) criterion already passes is a plan defect stop that names the commit, and the driver does not close the ticket.
3. Findings recorded | pass: docs/specs/sdlc-lite/plan-doc-executor.md section 8.1 links docs/reports/2026-10-11-plan-doc-live-run.md.
Negative control: M-1 reads 0 now, below the target of 1, so it is red before step 1.

## Measures
| id | command | read | target | direction | before | when |
|---|---|---|---|---|---|---|
| M-1 | `git grep -c 'show-toplevel' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md` | value | >= 1 | up | 0 | now |

## Authorization
None. Publish, push, tag, `onboard.py setup` and external writes are not implied.

## Budget and stop rules
Stop and write state to .sdlc/notes.md at $8 total, the per-step cap in each step, a rate or weekly limit, or three 529s in a row. replan cap: 1, then stop.

## Step 1: Two preflight and stop rules in run-rules.md
level: L1
ticket: new chore run-rules-two-rules
depends: []
executor: auto
verify: required
cap: $3
upserts: [plugins/sdlc-lite/skills/run-plan/references/run-rules.md]
### Read first
- plugins/sdlc-lite/skills/run-plan/references/run-rules.md
- docs/reports/2026-10-11-plan-doc-live-run.md
### Do
In run-rules.md, Preflight: add one numbered item: run `git rev-parse --show-toplevel`; if it is not the repository that holds the plan doc, stop with state written (the host makes sub-agent worktrees from the session's repository). In The loop, after step 4: add one sentence: a solo that reports no diff possible because the step's (red) criterion already passes is a plan defect stop that names the commit that built it; the driver never closes that ticket itself.
### Acceptance criteria
- (red) `git grep -q 'show-toplevel' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`
- (red) `git grep -qi 'already passes' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py >/dev/null`
- (guard) `git grep -q 'plan_done.py' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`

## Step 2: Link the live-run record from the design doc
level: L1
ticket: new chore design-links-live-run
depends: [1]
executor: auto
verify: auto
cap: $3
upserts: [docs/specs/sdlc-lite/plan-doc-executor.md]
### Read first
- docs/specs/sdlc-lite/plan-doc-executor.md
### Do
In section 8.1 of plan-doc-executor.md add one line: the first live run and rehearsal are recorded in docs/reports/2026-10-11-plan-doc-live-run.md.
### Acceptance criteria
- (red) `git grep -q '2026-10-11-plan-doc-live-run' -- docs/specs/sdlc-lite/plan-doc-executor.md`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root . >/dev/null`
- (guard) `git grep -q 'git grep' -- .sdlc/plan-doc-hardening/plan-doc.md`

## Upserts
| path | mode | step |
|---|---|---|
| plugins/sdlc-lite/skills/run-plan/references/run-rules.md | edit | 1 |
| docs/specs/sdlc-lite/plan-doc-executor.md | edit | 2 |

## Done when
M-1 reads >= 1 and `plan_done.py` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state.
Goal line:
```
/goal complete build and verify /Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/plan-doc-hardening/plan-doc.md by the run-plan skill: done when `python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/plan_done.py /Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/plan-doc-hardening/plan-doc.md` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state. Do not end the turn while it exits 1 and an item is open that you can work on.
```
