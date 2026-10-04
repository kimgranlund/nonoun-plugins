<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- lane M prints `solo` (`d=$(mktemp -d) && printf ... size: M ... steps.py lane $d | head -1 | grep -qx solo`): pass. Evidence: first line `solo`, grep exit 0. In a throwaway worktree at `main` the same fixture prints `lean`, so the check goes red on the old behavior.
- lane S prints `solo`: pass. Evidence: first line `solo`, grep exit 0. At `main` the same fixture prints `fix`, so the check bites.
- lane L prints `full`: pass. Evidence: first line `full`, grep exit 0.
- `grep -q "sdlc-solo-l2" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: pass. Evidence: exit 0. Line 44 reads "`solo` means run the `solo` session agent at the tier for the ticket size (S, M, L; the Codex agents are `sdlc-solo-l1`, `sdlc-solo-l2`, `sdlc-solo-l3`), `lean` the lean chain in the chain workflow, and `full` the chain workflow". At `main` the grep count is 0, so the check bites.
- `grep -q "## Lean chain" plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: exit 0; the heading is at chain/SKILL.md:16, and `always runs the filer` is at :25.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: exit 0, output ends `ok: 19 role levels, 9 agents checked`.
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc=0, 642 lines, no `FAIL` lines. The tail shows `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: plugin validate`, and one skip, `shellcheck not installed`. I did not run this at the pre-build SHA. It is green, so the inherited-red comparison does not apply.

Staleness check, one place at a time (the narrow task's named findings):
- `skills/sdlc-lite/SKILL.md:44` routes `solo` to the sdlc-solo agents. Checked above.
- `skills/chain/SKILL.md:27` says "prints `solo`, `lean`, or `full`". It still holds `## Lean chain` (:16) and `always runs the filer` (:25).
- `docs/lean-sdlc/design.md:68` says "prints `solo`, `lean`, or `full`". Line 283, the test-table row, says "A size-S fixture gives `solo`".
- `skills/level-rubric/SKILL.md:93` says "The `conductor`, the `solo` operator, and the `messenger` are session agents".
- Line 64 of design.md ("Today the lanes are `/fix`...") is a historical statement about the pre-change state, not a claim about the lane output. I left it, since the finding named only lines 68 and 283.
- Line 91 of design.md says `lane` prints "the same first-line contract" at three decision points and names no values, so it is not stale.

## Out of scope changes
None. `git status --short` shows only untracked run artifacts under `.sdlc/verify-t0215-narrow/step-1/`. The doc fixes were already in the tree at `4a80f6f` (the sdlc-lite SKILL.md grep passes there). The later diff from `4a80f6f` to HEAD touches `docs/lean-sdlc/cost-control.md` and `chain/SKILL.md` (a specgate sentence in the review bullet), and both come from the "Merge main into t0215" commit, not from this step. I read those diff lines and they do not touch the lane wording.

## For the next attempt
None
