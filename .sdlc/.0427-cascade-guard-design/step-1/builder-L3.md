<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/c/docs/specs/sdlc-lite/cascade-guard.md (new): the design, sections 1 to 11, including the eight required H2 headings.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/c/docs/specs/sdlc-lite/README.md: added one `Cascade guard` bullet after the `Lane lifecycle` bullet.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/c/docs/specs/sdlc-lite/AGENTS.md: added `- [cascade-guard.md](cascade-guard.md)` between bounded-plan-correction and cost-control. The managed start marker hash is now `sha256:b1bbe59b7bf5`, which matches the handoff's cross-check value.
- Index: `cascade-guard.md` is marked intent-to-add (`git add -N`). Nothing was committed.

## Checks
- `python3 .../redck.py record <handoff>` ran before any edit and printed `recorded 1 pre-edit control(s) red`.
- (red) `test -f docs/specs/sdlc-lite/cascade-guard.md`: exit 0.
- The heading and Status python check printed `[] True` and exited 0.
- The dash check printed `[]` and exited 0.
- The README and AGENTS.md index grep exited 0.
- (guard) The managed-block hash check printed `True` and exited 0.
- (guard) The docs_check check for no D-10 or B-3a warning on cascade-guard.md exited 0.
- The scope check against base 4e77062d exited 0. I ran it once before and once after the `git add -N`.
- (guard) The `docs_check: 0 errors` check exited 0. docs_check reports 0 errors and 25 warnings, and none of the warnings is in cascade-guard.md.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`:
  - First run: exit 1, with exactly two failures: `unlisted broken link docs/specs/sdlc-lite/AGENTS.md -> cascade-guard.md` and the same for README.md.
  - After `git add -N docs/specs/sdlc-lite/cascade-guard.md`: exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- `git diff --check`: exit 0.

## Notes
1. **Why the new doc is intent-to-add.** check.py's broken-link check (`rename_refs.link_report`) only counts files git tracks. So any link to a new, untracked doc reads as broken until it is committed. The handoff expected this only for `onboard.py check`.
   - There is precedent: the T-0422 verifier saw `A docs/specs/sdlc-lite/lane-lifecycle.md` staged.
   - To put the index back as it was: `git reset -q -- docs/specs/sdlc-lite/cascade-guard.md`. The lane merge commits the file either way.
   - I could not test this in a throwaway worktree: the stray-worktree hook blocked creating one because `SDLC_TMP_WORKTREES` is unset in this session. I tried a temporary `GIT_INDEX_FILE` instead, but that variable also reached git calls into other repos and produced false failures, so I don't count that run. No worktree was created.
2. **The handoff's premise does not hold under the proof.** I ran the mechanical-copy command on T-0362 `planner-L3-4.md` (the plan that passed) against T-0378 `planner-L3-2.md`.
   - It printed `44 lines differ by sha, count or id only; 22 other lines` and exited 1. Against `planner-L3-3.md` it printed 41 and 40, exit 1.
   - The first T-0378 review's step 2 defect (an expected count of 10 merge commits where a correct build makes 11) is in one of those other lines.
   - Section 4 of the doc reports that the route would have refused T-0378. The maintainer should read section 4 before approving.
3. **The cap N = 6.** It is based on the per-step count (the task's runs plus that step's runs), not the collector's per-ticket `by_ticket` total.
   - On that count, T-0378 is at 7 runs per step and T-0362 step 1 is at 8, so both trip the cap. T-0379 is at 6 and passes.
   - The collector's 10 runs and maison's own count of 11 are both cited and left unreconciled, as the handoff asked.
   - `conductor.md` line 9 still says "6 until T-0427 sets it". That wording belongs to T-0428 and is untouched.
4. **Collector rerun.** Maison now shows 1895 runs (1894 at plan time; one run landed since). Agent-ui shows 218.
5. **Measures.** The measures are per ticket, from `by_ticket`. A per-step measure needs a collector change (`runs.by_step`), which is build ticket 4.
6. **Open questions.** Section 11 of the doc holds two: which roles count toward the cap, and whether a verifier's own test run changing the tree counts as "a verified file changed since".
