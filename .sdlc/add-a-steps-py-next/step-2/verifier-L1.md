<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Section 4 of chain SKILL.md contains `steps.py next`: pass. Evidence: the sed|grep command exited 0. The section text shows the new instruction paragraph, with the action mapping and the nonzero-exit rule. The check can fail: `git show HEAD:.../chain/SKILL.md | grep -c 'steps.py next'` gives 0 at HEAD.
- conductor.md contains `steps.py next`: pass. Evidence: grep exited 0. The diff is 1 line.
- The CLAUDE.md `scripts/steps.py` line contains `next <step dir>`: pass. Evidence: exit 0. At HEAD the same pipeline counts 0 matches.
- The CLAUDE.md "Escalation is enforced" line contains `steps.py next`: pass. Evidence: exit 0.
- sdlc-lite-author.md contains `steps.py next`: pass. Evidence: exit 0.
- (guard) No em dashes in the five named files: pass. Evidence: `! grep -n '—' ...` exited 0 with no output. All five paths exist, so the check cannot pass on a bad path.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: exit 0. The tail shows the fanout, run, and hook selftests PASS, then `ok: shellcheck` and `ok: plugin validate`.

The chain section also keeps the `plan defect` phrase in the 4.2 path. The guard passed, so `Plan review` is presumably still present elsewhere in the file. I did not check that separately.

## Out of scope changes
`plugins/sdlc-lite/scripts/steps.py` shows a 231-line diff. This step did not call for it; it is presumably step 1's work. It is not in the builder's Changes list. `check.sh` is green with it in place.

## For the next attempt
None
