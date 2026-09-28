<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, bare pinned sha in a `(guard)` span refused by lint: pass. Evidence: I ran each criterion span from the handoff under `bash -c`, and all exited 0 (the `check.sh` criterion was run separately, below). In a throwaway worktree at HEAD, `steps.py lint` on the same plan (`git diff --quiet 3f9c2ab -- src`) printed `steps lint: ok` with rc 0. So the criterion fails before the change and passes after it.
- Criterion 2, `<sha>..HEAD` range refused with "pins a commit sha fixed at plan time": pass. Evidence: exit 0 on the tree. The code is `pins_sha` / `SHA_RE` at steps.py `lint_steps`. I also probed `3f9c2ab^` and `3f9c2ab~2`, and both are flagged.
- Criterion 3, glob count compared with 26 refused with "compares a count over a changing set with a fixed number": pass. Evidence: exit 0. Probes of `find | wc -l -eq 3`, `grep --count ... -ge 2` and `ls d/* | wc -l == 10` are all flagged.
- Criterion 4, `git diff --quiet HEAD` and `%H HEAD~1` still lint clean: pass. Evidence: exit 0, `steps lint: ok`. Probes on `git diff HEAD~1` and `git status` are not flagged as a pinned sha.
- Criterion 5, `grep -c` on one file with `-eq 2` passes: pass. Evidence: exit 0, `steps lint: ok`.
- Criterion 6, glob count `-eq 0` passes: pass. Evidence: exit 0, `steps lint: ok`.
- Criteria 7 to 9, selftest output holds "pins a commit sha" and "fixed number", and the selftest is green: pass. Evidence: all three exit 0. At HEAD in the throwaway worktree, `steps.py selftest | grep -c "pins a commit sha"` gave 0, so the check fails before the change. The new cases are (k3), (k4) and (k5) in steps.py.
- Criteria 10 to 12, planner.md holds `sha fixed at plan time`, `derive the set at run time` and `owns that budget`: pass. Evidence: all three greps exit 0. Rules 6, 7 and 8 sit at planner.md lines 6 to 8 of the section, and the last sentence of rule 7 forms `derive the set at run time` in the file.
- Criteria 13 and 14, check.py holds `sha fixed at plan time` and `owns that budget`: pass. Evidence: both greps exit 0. `PLAN_DEFECT_DOCS` has the entries `('agents/planner.md', 'scripts/steps.py')` and `('agents/planner.md',)`. The header item 5 is updated.
- Criteria 15 and 16, `pins a commit sha` in CLAUDE.md and `.claude/agents/sdlc-lite-author.md`: pass. Evidence: both greps exit 0. The diff shows the steps.py bullet and the Plan-defect route line naming both new checks.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: I ran it and it printed `check.sh exit 0`. Its output includes the order, fanout, run, hook and hook-live-probe selftests, `ok: shellcheck` and `ok: plugin validate`.
- Observable: rules under `## Criteria that can pass` are numbered 1 to 10 with no gaps, and no stale "rule 6" or "rule 7" reference to the replan rules: pass. Evidence: the numbered listing of that section shows 1 to 10 in order, with the replan rules at 9 and 10. `grep -rnE "planner.*rule (6|7)|rule (6|7).*(replan|recurring)|(replan|recurring).*rule (6|7)" plugins .claude CLAUDE.md` returned nothing. The only in-file reference, "as in rule 3" in rule 8, points to the correct rule.

## Out of scope changes
None. The five modified files are the ones the step names. The untracked `.sdlc/0100-planner-parallel-safe-criteria/` entries (`planner-L2.md`, `runs.jsonl`, `step-1/`) are pipeline artifacts. One small change beyond the letter of the Do: in `lint_steps`, a `ValueError` from `or_fallback` now sets `joined = False` instead of `continue`, so the new checks still run on that span. I judge this in scope because the new checks would otherwise be skipped, and the selftest and check.sh stay green.

## For the next attempt
None
