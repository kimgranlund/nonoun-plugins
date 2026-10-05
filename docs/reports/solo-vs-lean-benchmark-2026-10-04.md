# Solo vs lean benchmark

Recorded: 2026-10-04. Three real tickets from this repository, each run two ways in a throwaway worktree at the ticket's base commit, then graded by a hidden check and `check.sh`. The question: does a single-session solo agent match the orchestrated chain on pass rate at lower cost and time? The runs were made earlier the same day; this record was written afterwards from the files left on disk. Raw evidence is in [`solo-vs-lean-benchmark-2026-10-04/`](solo-vs-lean-benchmark-2026-10-04/).

## Result

All six cells passed the hidden check and `check.sh`. Solo was cheaper and faster on every task.

| Task (base, real solution) | Arm | Hidden check | `check.sh` | Wall time | Cost | Roles or turns | Replans | Files under `.sdlc/bench-*` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| footprint (433125d, 7b7096e) | solo | pass | pass | 414 s (7 min) | $0.86 | 18 turns | 0 | 0 |
| footprint | lean | pass | pass | 1082 s (18 min) | $1.83 | 3 roles | 0 | 17 |
| scout-pin (cc844f7, 3ec05af) | solo | pass | pass | 303 s (5 min) | $0.43 | 12 turns | 0 | 0 |
| scout-pin | lean | pass | pass | 2116 s (35 min) | $7.95 | 5 roles | 1 | 22 |
| wait (2a428cc, cf3d43f) | solo | pass | pass | 367 s (6 min) | $1.37 | 25 turns | 0 | 0 |
| wait | lean | pass | pass | 3997 s (67 min) | $17.05 | 5 roles | 1 | 22 |
| Total | solo | 3 of 3 | 3 of 3 | 1084 s (18 min) | $2.66 | | 0 | 0 |
| Total | lean | 3 of 3 | 3 of 3 | 7195 s (120 min) | $26.83 | | 2 | 61 |

Lean cost and role counts are from each arm's `runs.jsonl`, deduplicated by attempt id (`cells/<task>-lean/runs-summary.tsv`). Solo cost and turns are from the `claude -p` JSON result (`cells/<task>-solo/claude-result.json`). Lean wall time for scout-pin and wait is the sum of three recorded segments (first drive, replan, resume), taken from each cell's `summary.txt` and `replan.txt`: scout-pin 302 + 756 + 1058 s, wait 407 + 1828 + 1762 s.

Where the lean cost went:

| Task | Planner L2 | Planner L3 replan | Plan review (Fable high) | Builder | Verifier |
| --- | --- | --- | --- | --- | --- |
| footprint | $0.78 | none | none | $0.74 | $0.32 |
| scout-pin | $0.72 | $3.29 | $3.39 | $0.35 | $0.20 |
| wait | $0.90 | $7.91 | $6.50 | $1.38 | $0.37 |

On the two harder tasks the planner L2 plan was refused at `steps.py split` as a plan defect, so a planner L3 replan and a Fable plan review followed. Those two roles were about 84% of the lean spend on both scout-pin and wait. On footprint, which needed no replan, lean cost $1.83 against solo's $0.86, so even the unreplanned chain cost about twice as much.

The solo runs used `claude -p --model opus --effort high` with the ticket goal and the repository guidance, no sdlc-lite roles, a $15 budget cap and a 45 minute limit. The lean runs used a minimal `/chain` driver (`harness/drive.sh`): planner L2, plan review when required, split, then build and verify each step, from a frozen runner checkout.

## What this shows and what it does not

- Solo delivered the same checked outcome in about one seventh of the wall time (18 against 120 minutes) and one tenth of the cost ($2.66 against $26.83) across the three tasks.
- The lean arm's extra cost came mostly from planning and plan review, not from building. Both replans followed a planner L2 plan refused at `steps.py split` as a plan defect.
- It does not show that solo is as good on quality. The hidden checks are behavior checks written for these tasks. Solo has no independent verifier, so a wrong-but-passing change is possible and this run could not detect one.
- It does not cover size S or size L tickets, Codex, or any task outside this repository.

## Caveats

- n=3 tasks and one run per cell. No variance estimate.
- Not blind: the author chose the tasks, wrote the hidden checks and the prompts, and knew both arms.
- Tasks were taken from this repository's own closed tickets, so they suit this repository's agents. One task (footprint) was small enough that the lean arm needed no replan.
- The lean arm ran a minimal driver, not the lean lane as released in 0.20.4 and 0.20.5 (`steps.py lane`, coarse steps, batched verification). Its planning overhead is an upper bound for the lean lane. The lane output was not used to choose the arm.
- Planner L2 was used for every lean arm, as the lean lane would, and the replans escalated to L3 under the chain's own rules. No model or effort setting was changed for the benchmark.
- Each lean cell's `diffstat.txt` and `status.txt` were written after the resumed run and are empty for scout-pin and wait. The diffs were recomputed against each base commit afterwards: scout-pin 8 files, 14 insertions and 12 deletions, and wait 2 files, 222 insertions and 20 deletions. The first drive of each of those two arms ended at `STOP split refused` (hidden check exit 1, as recorded in `summary.txt`); the resumed run is the graded outcome.
- Some lean roles reported stray worktrees or branches created by other work in the same repository during the run (visible in `drive.log`). They did not change any result.
- Solo cost excludes the time and tokens of the benchmark author's own session. Lean cost excludes the driver's shell time.
- The benchmark did not run Codex.

## What it implies for the default lane

Recommendation only; no default was changed.

- For a size S or M ticket in this repository, solo should be the default lane. That is what the lane script has printed since 0.20.5 (`steps.py lane` prints `solo` for sizes S and M), and this run supports it on cost and time.
- Keep one independent verifier at the end for tiers M and L. Solo had none here, and the claim that quality is equal is untested.
- The full chain should stay opt-in for L4 and L5 steps, merge steps, cross-cutting plans and security-sensitive changes, which this benchmark did not include.
- A planner L2 plan that fails `steps.py split` is the expensive path: it triggers a planner L3 replan plus a Fable review, about $7 to $14 per task here. Making that outcome rarer (the spec gate, T-0210, runs before the reviewer) is worth more than tuning the build and verify roles.
- To settle the quality question, rerun with a second solo trial per task, an independent verifier on the solo arm, and at least one size L task. That costs roughly $5 for the solo arms and $30 for the chain arms.

## Evidence

- Harness: [`harness/arm.sh`](solo-vs-lean-benchmark-2026-10-04/harness/arm.sh) (one arm), [`drive.sh`](solo-vs-lean-benchmark-2026-10-04/harness/drive.sh) (minimal chain driver), [`hidden.sh`](solo-vs-lean-benchmark-2026-10-04/harness/hidden.sh), [`replan.sh`](solo-vs-lean-benchmark-2026-10-04/harness/replan.sh), [`resume.sh`](solo-vs-lean-benchmark-2026-10-04/harness/resume.sh), the task files in `harness/tasks/` and the hidden checks in `harness/tests/`.
- Per cell, under `cells/<task>-<arm>/`: `summary.txt`, `hidden.txt`, `check-sh.rc`, `status.txt`, `diffstat.txt`, and for solo the `prompt.txt` and `claude-result.json` (cost, turns, usage), and for lean `drive.log`, `drive2.log`, `replan.txt` and `runs-summary.tsv`.
- Not kept: the arm worktrees, role transcripts and full `check.sh` output (under `/tmp/bench-sl`, which is temporary).
