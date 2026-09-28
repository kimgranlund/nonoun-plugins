<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0093: Let the steps.py lint accept fail-fast `|| exit N` and lint loop criteria

## PR body
### Summary
The `steps.py` `||` lint refused every unquoted `||` except `test $# -eq 0 ||`. Peer plans use fail-fast forms such as `for f in a b; do test -f "$f" || exit 1; done`. The ticket's evidence says the lint would send these valid plans to a replan as plan defects. This change allows a `||` whose right operand is a nonzero `exit`. It keeps refusing real fallbacks and vacuous forms.

While planning, the planner found that `is_command` never linted `for`/`while`/`until`/`if`/`{` criteria, because it judged only the head token. Loop criteria therefore passed unchecked, including ones with a real fallback or `|| echo MISSING`. This change closes that gap too.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`
  - An unquoted `||` now passes when its right operand is `exit N` with N nonzero, bare or as the last command of a `{ ...; }` group. The `test $# -eq 0 ||` exemption is kept.
  - `|| exit 0`, bare `|| exit`, `|| true`, `|| false`, `|| return N`, `|| echo ...`, `|| { exit 1; echo x; }` and `grep a x || grep b x` are still refused.
  - The builder tightened the rule beyond the plan: an exit code counts only if `N % 256 != 0`, a lone `&` after `exit N` does not end the command, and a brace-group's final exit must not follow `||`.
  - `is_command` now treats `for`/`while`/`until` ending in `done`, `if` ending in `fi`, and `{` ending in `}` as commands. Prose such as `for each changed file` stays non-command.
  - The `lint` usage text and `or_fallback` docstring state the allowance and the reason.
  - The `(k2)` selftest has new pass, refuse and prose controls.
- `plugins/sdlc-lite/agents/planner.md`: rule 5 lists both allowed `||` forms with a loop example.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: the rule wording is updated to match, and CLAUDE.md now says loop, `if` and `{` criteria are linted.
- `plugins/sdlc-lite/scripts/check.py`: the phrase ``nonzero `exit` `` is added to `PLAN_DEFECT_DOCS`, so it cannot drift out of `planner.md` or `steps.py`.

Plans with vacuous `|| echo MISSING` loops, which passed silently before, are now refused. This is new strictness by design.

### Verification
- Step 1 (steps.py), verifier L2: pass.
  - All acceptance criteria and guards were run verbatim.
  - In a worktree at HEAD, the pass cases exit 1 and the refuse cases return 0, so the checks discriminate.
  - Edge probes behaved as expected. Refused: `|| return 1`, `|| { echo x; }`, `|| exit "$x"`, `|| exit 1 || true`. Accepted: `test -f a || exit 1; test -f b || exit 2` and `|| exit 1 && ...`.
  - `steps.py selftest` passed and full `check.sh` exited 0.
- Step 2 (records), verifier L1: pass.
  - The old wording greps are red at HEAD and green in the tree.
  - The `check.py` entry was mutation-checked: replacing the phrase in `planner.md` printed `FAIL agents/planner.md: plan-defect route missing "nonzero `exit`"`.
  - `check.sh` exited 0 with no FAIL lines.
- The step 2 builder's first `check.sh` run failed once on `hook selftest: block-pattern-kill without role: exit 141` (SIGPIPE) in a hook this change did not touch. It did not recur in three reruns or in the verifier's run.

## Changelog entry
- The `steps.py` `||` lint now accepts a fail-fast `|| exit N` (N nonzero, bare or ending a `{ ...; }` group) and still refuses real fallback joins. It also now lints `for`/`while`/`until`/`if`/`{` criteria, which were previously skipped.

## Follow-ups
- The steps.py `||` lint accepts `test -f a || exit 1 | cat`, which is really `a || (exit 1 | cat)` and returns cat's status 0, so the criterion passes when the left side fails. Drop the lone `|` from `ends_command`, and the planner spec in Do item 1 that lists it.
- The steps.py lint does not check compound criteria with a trailing redirect, such as `while read x; do ...; done < f`, because they do not end in `done`. Such a criterion can hold an unlinted `||` fallback.
