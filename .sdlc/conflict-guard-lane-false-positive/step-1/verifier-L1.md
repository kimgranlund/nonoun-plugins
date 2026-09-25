<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'git diff-tree --cc HEAD'` in planner.md: pass. Evidence: I ran it and it exited 0. The diff shows the new guard line at planner.md:36.
- Same grep in handoff-format/SKILL.md: pass. Evidence: it exited 0.
- `! grep -q 'xargs -0 sh -c'` in planner.md: pass. Evidence: it exited 0. The diff removes the old line.
- Negative control (old guard fails the legit case): pass. Evidence: I ran check.py against the 7e51f1b archive, and it printed `FAIL merge-step conflict-marker guard: legit lane line flagged`. The grep exited 0.
- Negative control for the kept-conflict case: pass. Evidence: I copied plugins and CLAUDE.md to a temp dir and replaced the guard span with `true "<<<<<<<"` in both blocks. check.py then printed `FAIL merge-step conflict-marker guard: kept conflict markers not flagged`. It also printed the marker FAIL, which is expected with an always-true guard.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: it printed `ok: 18 role levels, 8 agents checked` and exited 0. The probe now covers the empty, marker, legit lane line, kept conflict and clean cases.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: it exited 0.
- (guard) `git diff --quiet HEAD -- steps.py builder.md`: pass. Evidence: it exited 0.
- The two merge-step blocks are byte-identical: pass. Evidence: a diff of the fenced blocks in the two files printed `same`. The diff shows only the guard line changed in each file.

## Out of scope changes
`.sdlc/conflict-guard-lane-false-positive/handoff.md` is modified. The rest is untracked `.sdlc` task artifacts, which are pipeline bookkeeping. The plugin changes are limited to planner.md, SKILL.md and check.py.

## For the next attempt
None
