<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `! grep -n 'only allowed form' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exits 0 in the tree. It exits 1 in a throwaway worktree at HEAD ae8d9d9, where the old bullet still exists, so the check can go red. The replacement bullet is at planner.md:21 (diff).
- `! grep -n 'except after .test' CLAUDE.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD. The CLAUDE.md steps.py bullet now reads "an unquoted `||` that is a fallback join; allowed only after `test $# -eq 0` or when its right operand is a nonzero `exit`, bare or ending a `{ ...; }` group; `for`/`while`/`until`/`if`/`{` criteria are linted too".
- `grep -q 'nonzero .exit' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD. The bullet names both allowed forms and the `for f in a b; do test -f "$f" || exit 1; done` example, and says `|| echo`, `|| true` and `|| exit 0` stay refused.
- `grep -q 'nonzero .exit' CLAUDE.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD.
- `grep -q 'nonzero' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exits 0 in the tree and 1 at HEAD, and the diff adds ``'nonzero `exit`': ('agents/planner.md', 'scripts/steps.py')`` to `PLAN_DEFECT_DOCS`.
  - I also checked that the new entry itself fails when the phrase goes missing. Setup: a copy of plugins/sdlc-lite under `$SDLC_TMP_WORKTREES` with `nonzero `exit`` replaced by `nonzero exit` in agents/planner.md.
  - Mutated copy: `check.py <copy>` printed `FAIL agents/planner.md: plan-defect route missing "nonzero `exit`"`.
  - Unmutated copy: that line was absent. It failed only on CLAUDE.md-location lines, because the copy has no CLAUDE.md beside it.
  - steps.py holds the phrase at lines 41 and 432.
- `grep -q 'fallback' .claude/agents/sdlc-lite-author.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD. Line 18 now reads "joins two checks with a fallback `||` (only `test $# -eq 0 ||` and a nonzero `exit` right operand are allowed)", which matches the CLAUDE.md wording.
- (guard) `grep -qF 'test $# -eq 0' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exits 0 in the tree and 0 at HEAD, which is the expected result for a guard.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit=0 in the tree. The tail shows `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`, and no line starts with FAIL. The builder reported a flaky exit 141 in the hook selftest; it did not recur in my run.

## Out of scope changes
None from this step.
- `plugins/sdlc-lite/scripts/steps.py` and `.sdlc/check-the-steps-py-lint/handoff.md` are also modified, but they belong to step 1 and the task handoff. This step's Do says it changes "these records to match step 1". The (k2) selftest line in the check.sh output exercises the step 1 steps.py change.
- The untracked `.sdlc/check-the-steps-py-lint/` artifacts are run outputs.
- The step's own diff (`git diff` on the four files) touches only the four files the Do names.

## For the next attempt
None
