<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0082: Planner: ban || fallbacks in criteria; lint them in steps.py split

## PR body
### Summary
If an acceptance criterion joins two checks with `||`, the criterion passes when either side matches, so it can hold at HEAD and never fail. This happened in a peer run (gen-ui-system-svelte-lite T-0164 step 3). The verifier failed the build twice, the chain escalated the builder to L4, and the L4 builder then blocked with a plan defect. `steps.py split` and `steps.py lint` now refuse such a criterion as a `plan defect` before any build runs, and the planner rules ban it explicitly.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`
  - Adds `or_fallback`, which finds an unquoted `||` in a criterion command span. It uses a shlex tokenizer that sets `punctuation_chars` and `commenters = ''`, so `$#` is not read as the start of a comment.
  - A `||` inside quotes is ignored. The empty-argument short circuit `test $# -eq 0 || ...` is allowed.
  - `lint_steps` reports `acceptance criterion joins two checks with ||`, followed by an indented explanation line. The existing `lint_or_fail` path adds the `plan defect` line, so `split`, `split --only`, and `lint` all refuse and write nothing.
  - The docstring is updated, and new selftest cases (k2) are added.
- `plugins/sdlc-lite/agents/planner.md`: adds a new rule under "Criteria that can pass" that bans `||` joins, notes that `split` refuses them, and names the one allowed form. The later rules are renumbered with their text unchanged.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: the steps.py Layout bullet and the author agent's plan-defect route bullet now mention the `||` check.

### Verification
- Step 1 (builder L2, verifier L1): pass.
  - A plan with `a || b` makes `lint` exit nonzero and print `plan defect`.
  - `split` refuses that plan and creates no `step-1`.
  - A quoted `||`, the `test $# -eq 0 ||` form, and an `&&` join all lint clean.
  - `steps.py selftest` passes and prints three new (k2) `ok:` lines. `check.sh` exits 0.
  - Negative control: in a throwaway worktree at the pre-change commit, the same lint command printed `steps lint: ok`, so the test is red without the fix.
- Step 2 (builder L1, verifier L1): pass.
  - The three grep criteria pass in the tree and fail at HEAD.
  - No cross-references to rule numbers are broken by the renumbering.
  - `check.sh` and `steps.py selftest` both pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py split` and `steps.py lint` now refuse, as a plan defect, any acceptance criterion that joins two checks with an unquoted `||`. The only allowed form is `test $# -eq 0 || ...`. The planner rules now ban `||` fallbacks in criteria. (T-0082)

## Follow-ups
- Check the `steps.py` `||` lint allowance against the merge guards peers actually use. It only exempts the exact form `test $# -eq 0 ||`, which was inferred from the ticket because this repo has no such form, so a peer using a different empty-argument short circuit would get its valid plan refused as a plan defect.
