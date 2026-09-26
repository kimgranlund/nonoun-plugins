<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- 3.3 line contains "at most 4 options per question": pass. Evidence: the `grep -n "When a person is present" ... | grep -q` pipeline exited 0. The SKILL.md diff shows the phrase on the step 3.3 line.
- check.py contains the phrase: pass. Evidence: `grep -q` exited 0. The `step33_bad` guard is in the diff of plugins/sdlc-lite/scripts/check.py.
- Pre-change text lacks the phrase (guard): pass. Evidence: the `git show HEAD:... | grep ... | grep -vq` pipeline exited 0.
- (guard) `at most 4 options` in SKILL.md: pass. Evidence: `grep -q` exited 0.
- (guard) `--expect` in SKILL.md: pass. Evidence: `grep -q` exited 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass. Evidence: exit 0, output "ok: 18 role levels, 8 agents checked".
- `plugins/sdlc-lite/scripts/check.sh` exits 0 with no new findings: pass. Evidence: exit 0. The output ends with the order, fanout, run and hook selftests PASS, then "ok: shellcheck" and "ok: plugin validate". No FAIL lines were seen in the tail. I did not run check.sh at HEAD for a baseline, so "no new findings" rests on the output ending in all-ok.
- No em dashes added to SKILL.md: pass. Evidence: the `git diff -U0 ... | grep '^+' | grep -c "—"` pipeline printed 0.
- The 3.3 text states the batching rules: pass. Evidence: read the SKILL.md diff.
  - At most 4 options per question, and at most 4 questions per call.
  - Follow-ups split in order, recommended items first.
  - No question has fewer than 2 options ("5 follow-ups become 3 and 2, never 4 and 1").
  - A lone follow-up gets "File it" and "Skip it".
  - Past 16 follow-ups, the rest go to further calls.
  - Unselected items are skipped.
- The check bites: pass. Evidence: in a throwaway worktree at HEAD with the new check.py copied in, check.py printed `FAIL skills/file/SKILL.md: step 3.3 missing "at most 4 options per question"` and exited 1. On the changed tree it exits 0. The in-memory negative control (phrase removed, predicate must flag it) is in the check.py diff. I did not run it separately. The HEAD run above is the observed red.

## Out of scope changes
- `.sdlc/file-step-3-3-follow/handoff.md` is modified (Goal, Constraints and a Scope section filled in). This is the pipeline's clarify step, not the builder's work, and it changes no plugin file. Not a defect.
- Untracked files under `.sdlc/file-step-3-3-follow/` (planner-L1.md, runs.jsonl, step-1/) are pipeline artifacts.
- The only plugin files changed are SKILL.md (step 3.3 line only) and check.py (one block before the step 4 guards). `git diff --stat` shows 1 line changed in SKILL.md and 6 added in check.py, so nothing outside step 3.3 or the step 4 guards was touched.

## For the next attempt
None
