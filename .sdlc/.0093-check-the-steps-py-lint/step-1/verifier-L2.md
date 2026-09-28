<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, lint accepts `test -f a || exit 1`: pass. Evidence: I ran the handoff command verbatim through `bash -c` and got exit 0 with `steps lint: ok`. It bites: in a HEAD worktree the same span exits 1.
- Criterion 2, lint accepts `grep -q x a || { echo missing; exit 1; }`: pass. Evidence: exit 0, `steps lint: ok`. In the HEAD worktree the same span exits 1.
- Criterion 3, lint refuses the loop with `|| echo MISSING "$p"`: pass. Evidence: exit 0 under `!`. Lint printed `...cannot fail: split it into separate criteria` and `plan defect: replan this step`. In the HEAD worktree lint returned 0 for this span, so the `!` check would have failed there.
- Criterion 4, lint refuses the loop with `grep -q a "$p" || grep -q b "$p"`: pass. Evidence: exit 0 under `!`, with the same plan-defect output. In the HEAD worktree lint returned 0, so the loop was unlinted before.
- Criterion 5, `grep -q 'nonzero .exit' plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: exit 0. It matches the usage text and the docstring in the diff, and the HEAD copy has 0 matches. The docstring says a nonzero exit fails the criterion when the left side fails, so it cannot pass on either side.
- Guard, loop with `|| exit 1` still lints ok: pass. Evidence: exit 0, `steps lint: ok`.
- Guard, `grep -q a x || grep -q b x` still refused: pass. Evidence: exit 0 under `!`, plan defect printed.
- Guard, `|| exit 0` refused: pass. Evidence: exit 0 under `!`, plan defect printed.
- Guard, `|| true` refused: pass. Evidence: exit 0 under `!`, plan defect printed.
- Guard, `set -- $(ls); test $# -eq 0 || grep -q x "$@"` accepted: pass. Evidence: exit 0, `steps lint: ok`.
- Guard, prose `for each changed file` accepted: pass. Evidence: exit 0, `steps lint: ok`. `is_command` requires a trailing `done` for a `for` head.
- Guard, `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: `steps selftest: PASS`. Full `plugins/sdlc-lite/scripts/check.sh` also exits 0, ending in `ok: plugin validate`.
- `(k2)` selftest has the new cases: pass. Evidence: the `steps.py` diff in the `(k2)` block adds:
  - pass spans `test -f a || exit 1`, the two loop forms from Do item 4 (the `|| exit 1` loop and the `{ echo "missing $id"; exit 1; }` loop), and the existing quoted, `test $# -eq 0` and `&&` spans;
  - a check that both loops are command spans;
  - refuse forms `|| exit 0`, `|| true`, bare `|| exit`, `|| { exit 1; echo x; }`, the `|| echo MISSING` loop and the `grep || grep` loop (the plain `grep -q a x || grep -q b x` case was already in the block);
  - a prose control for `for each changed file`.
- Edge probes on the working tree, run by hand: these gave the expected result.
  - Refused: `|| return 1`, `|| { echo x; }`, `|| exit "$x"`, `|| exit 1 || true`, `if ... || true; then`, `{ ... || true; }` and `until ... || :; done`.
  - Accepted: `test -f a || exit 1; test -f b || exit 2` and `|| exit 1 && ...`.
  - Not linted: `while read x; do ...; done < f`. It does not end in `done`, so the spec's rule leaves it unlinted. This is a minor limit of the spec, not a defect.
- Steelman of the builder's note about `|`: `test -f a || exit 1 | cat` would be allowed, and the note's reading (the pipeline returns `cat`'s status) is correct. But Do item 1 lists `|` as a valid terminator, so the code follows the spec. I filed no finding. It is a spec gap to raise, not a build defect.

## Out of scope changes
None. `steps.py` is the only file the builder changed. `.sdlc/0093-check-the-steps-py-lint/handoff.md` is modified in the tree, but the diff shows task-level Goal, Intent and Constraints text, not step work, and the builder says it was already modified before the step. Other `.sdlc/` files are untracked artifacts.

## For the next attempt
None. The docs (`agents/planner.md`, `CLAUDE.md`, the author agent) still state the old `||` rule. That is presumably a later step and this step's Do does not include it. Consider dropping the lone `|` from `ends_command` in a follow-up, as the builder suggested.
