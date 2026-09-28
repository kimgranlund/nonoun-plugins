<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: this is the only file I changed. The edits:
  - New helpers `or_tokens`, `nonzero_exit_at`, `ends_command` and `fails_fast`.
  - `or_fallback` now also allows a `||` whose right operand is a nonzero `exit`: either `exit N` ending the command, or a brace group `{ ...; exit N; }` whose last command is that exit. The `test $# -eq 0` case is unchanged, and the docstring is updated.
  - `is_command` now treats compound commands as commands, via a new `COMPOUND_END` table: `for`, `while` or `until` ending in `done`, `if` ending in `fi`, and `{` ending in `}`. Prose like `for each changed file` still reads as prose.
  - The `lint` usage text now names the allowance with the phrase ``nonzero `exit` `` and says why it is allowed.
  - The `(k2)` selftest has the new pass and refuse controls and a prose control.

The `.sdlc/0093-check-the-steps-py-lint/handoff.md` modification and the untracked `.sdlc/0093-check-the-steps-py-lint/*` files were already in the tree before this step. I did not touch them.

## Checks
- I ran all 12 acceptance-criterion commands verbatim from the handoff, from the repo root, through `bash -c`. All 12 exited 0:
  - The pass cases lint ok: `test -f a || exit 1`, the brace-group exit, the loop with `|| exit 1`, the `test $# -eq 0` span, and `for each changed file`.
  - The refuse cases, run under `!`, are refused: the loop with `|| echo MISSING`, the loop with `grep || grep`, `grep -q a x || grep -q b x`, `|| exit 0`, and `|| true`.
  - `grep -q 'nonzero .exit' plugins/sdlc-lite/scripts/steps.py` matches the usage text and the docstring.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS. It includes the new `(k2)` cases:
  - Pass: `test -f a || exit 1`, both loop forms from Do item 4, the quoted `||` spans, `test $# -eq 0 ||`, and `&&`. A separate check confirms both loops are now picked up as command spans.
  - Refuse: `|| exit 0`, `|| true`, bare `|| exit`, `|| { exit 1; echo x; }`, the loop with `|| echo MISSING`, and the loop with `grep || grep`. `grep -q a x || grep -q b x` was already covered.
  - Prose: `for each changed file` gives no command spans and lints ok.
- I also called `or_fallback` and `is_command` directly on edge cases:
  - `|| exit 256`, `|| exit $x`, `|| exit 1 &`, `|| return 1`, `|| { echo x; }` and `|| { echo x || exit 1; }` are findings.
  - `|| exit 1 && b` and `|| exit 2; done` are allowed.
  - `until x` stays a non-command.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- The handoff lists a pipe `|` as a valid end for `exit N`, and I built it that way. But `test -f a || exit 1 | cat` is really `a || (exit 1 | cat)`: the pipeline returns `cat`'s status (0), so the criterion passes even when `a` fails. The linter lets this through. To close it, drop the lone `|` from `ends_command` and keep `;`, `&&`, `||`, `}`, newline and end of span. That is the planner's call.
- I tightened the rule in three places:
  - An exit code counts as nonzero only if `N % 256 != 0`, because `exit 256` exits 0.
  - A lone `&` after `exit N` does not end the command, because `exit 1 &` runs in the background and returns 0.
  - Inside a brace group, the final `exit N` must follow `{`, `;`, a newline or `&&`, never `||`.
- `is_command` now lints loop, `if` and `{ }` spans that ending in `done`, `fi` or `}`. A plan that already has such a span that does not parse, or that has a real `||` fallback, will now be refused where it passed before. That is the gap Do item 2 asked to close.
