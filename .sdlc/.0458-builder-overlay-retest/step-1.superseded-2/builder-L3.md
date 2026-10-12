<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/.sdlc/0458-builder-overlay-retest/run-log.md: new, one line per cell, 3 cells so far.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/docs/reports/2026-10-12-builder-overlay-retest/cell.py: new, the driver that runs one cell (clone, setup, handoff, lint, prepare, headless run, record, verifier, grade, run-log line).
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/docs/reports/2026-10-12-builder-overlay-retest/preflight.txt: new, Haiku `--plugin-dir` init-event plugin lines for 6 runs.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/docs/reports/2026-10-12-builder-overlay-retest/budget.txt: new, the start, skip and stop budget log.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/docs/reports/2026-10-12-builder-overlay-retest/rt-rts-step10-L1-A-1/, rt-rts-step10-L1-B-1/, rt-ndc-step2-L5-A-1/: new, each holds builder.md, verifier.md (when run), rows.jsonl (priced runs.jsonl rows) and log.txt.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/.sdlc/0458-builder-overlay-retest/step-1/red-checkpoint.jsonl: written by `redck.py record` before the first edit.
- I did not write the report, docs/reports/2026-10-12-builder-overlay-retest.md.

## Checks
- `redck.py record <handoff>`, run before any edit: exit 0, 6 pre-edit controls recorded red.
- Arm diff: `diff -rq armA/plugins armB/plugins` lists only builder-L1.md and builder-L5.md. Each has one hunk, `34a35,55` (L1) and `34a35,52` (L5), and each hunk starts `## At this level`.
- Preflight: `claude -p --plugin-dir <arm>/plugins/sdlc-lite --model haiku --output-format stream-json --verbose "ok"` ran from agent-ui@0e18b708, ultimate-tokens@7f05eb50 and sdlc-lite@6a14c165 clones, for both arms. Every init event shows exactly one `sdlc-lite` plugin (`sdlc-lite@inline`), at the arm root's path.
- t0378 hidden check in a scratch clone: red at base b599114e (redck.py absent, exit 1), green at a8b39893, green at e1fa6e04.
- Base trees: `git ls-tree` at every base shows only handoff.md in the ndc step-2 dir and the three sdlc-lite ticket dirs. agent-ui at 0e18b708 has no `.sdlc` at all. No task was dropped.
- Cells (priced with `dispatch.py record --transcript`; `steps.py lint` was ok and `prepare` passed every time):
  - rts-step10 L1 A 1: builder $0.34, 1.2 min, done; verifier L1 (opus medium) pass, $0.51.
  - rts-step10 L1 B 1: builder $0.28, 1.2 min, done; verifier pass, $0.37.
  - ndc-step2 L5 A 1: builder (fable xhigh) $8.54, 22.8 min, blocked with `plan defect`; no verifier.
- Replay Spend so far: 10.04 USD over 5 priced rows.
- Guards, run once with SDLC_BASE_SHA=ebac4973:
  - plugins/specs/scripts unchanged: rc 0.
  - Scope guard: `[]`, rc 0.
  - `check.py`: rc 0.
  - `check-packaging.py`: PASS.
  - `git diff --check`: rc 0.
  - `test -s run-log.md`: rc 0.
- The (red) report criteria 1 to 5 were not run, because the report was not written.

## Notes
plan defect: criterion 3 (four L1 rep-1 tasks in both arms plus a balanced L5 pair) cannot hold together with criterion 4 (Spend <= 20) or the $20 ticket cap.
- The L5 arm A builder alone cost $8.54 (22.8 min), against Do item 5's $8.00 estimate for the whole L5 pair.
- Finishing the pair (about $8.54 more) plus three L1 rep-1 pairs (about $1.70 each) puts replay Spend at about $24.
- The two planners already spent $3.85, and my session is not metered. Running L5 arm B alone would push the ticket past $20 before any L1 pair.
- I stopped after half the L5 pair. The stop is logged in budget.txt.
- A replan needs one of: a higher cap, no L5 requirement, a cheaper L5 task, or L5 run after the L1 pairs.

Findings for the replan:
- **rts-step10:** the on-disk handoff hashes to 8974d49f, which is the second, done builder row. The blocked row is fceea3cc. The blocked version was never committed in agent-ui, so it is gone. Both arms built the fixed handoff to done with a verifier pass, so this task cannot test blocking. The mismatch is in run-log.md.
- **ndc-step2 L5 arm A:** the hash matches the blocked row. The run blocked naming the same defect as the original note: the scope guard omits `scripts/bundle.mjs`, which the mandated chart imports require. The original L3 builder cost $3.41. This is one same-defect block, arm A only.
- **t0378:** the Do's claim "red at wip a8b39893" is false. That commit already carries the relabeled selftest lines. The check is still usable: it is red at base and green at the merge. No commit keeps the pre-fix labels.
- **Arm roots and cells:** these are `git clone --shared` copies under the tmp prefix. I removed the preflight and scratch clones. armA, armB and the three rt-* cells remain, and the conductor's record will remove the prefix. The evidence has already been copied to the docs/reports folder above.
- **Run-log wording:** I wrote each run-log line after `record`, because the cost columns come from `record`. Only the cell's own tmp prefix is removed at that point.
