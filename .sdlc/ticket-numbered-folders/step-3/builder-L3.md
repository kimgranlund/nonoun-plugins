<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `problems(ts, numbered=False)` now has the NNNN-/id rule, and it fires only when `numbered` is true.
  - `cmd_check(root, numbered=False)` also turns numbered mode on when `<root>/config` asks for it.
  - `cmd_new`, `cmd_close` and `stamp()` pass `numbered` to their `problems()` calls.
  - `run()` passes `**kw` to `check`.
  - `check` accepts `--numbered`, and `main()` reads the flag with `getattr(a, 'numbered', False)`.
  - The module docstring has the new Usage line and the extra clause for `check`.
  - Added selftest cases 1 to 8, and extended `numbered_ok` to also require `check numbered=True` to pass.
  - Moved the `both` helper up unchanged so the new block can use it.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS`, rc 0.
- `grep -c "prefix mismatch" plugins/sdlc-lite/scripts/tickets.py`: 4.
- The four-label grep finds 3 of the 4 labels:
  - Found: `plain mode still takes a digit-led slug as-is`, `(i) numbered close`, `(i) plain close keeps bare slugs`.
  - Not found: `new --numbered: folder` (explained in Notes).
- Red-then-green, run on copies placed next to `tickets.py` and then deleted:
  - Rule removed: FAIL. It lists `prefix mismatch (flag)` and `prefix mismatch (config)`. It also lists `digit-led plain slug: ... check --numbered names it` and the numbered `new` and `close` refusal cases.
  - Rule unconditional: FAIL. It lists `plain mode still takes a digit-led slug as-is`, `prefix mismatch is not checked in plain mode` and `(i) plain close keeps bare slugs`. It also lists `digit-led plain slug...` and `plain new ignores an existing prefix mismatch`.
- CLI sequence in a temp dir, all results as the criteria state:
  - `new feature foo "Foo" --numbered` created `0001-foo/handoff.md` with `id: T-0001`. `check --numbered` printed `ok: 1 tickets, roadmap current`, rc 0.
  - After changing the id to T-0009 and running `roadmap`:
    - `check` printed `ok: 1 tickets, roadmap current`, rc 0.
    - `check --numbered` exited 1 with `0001-foo: folder prefix 0001- does not match id 'T-0009' (want T-0001)`.
  - With `config` set to numbered:
    - `check` exited 1 with the same line.
    - `new feature bar` exited 1 with that line plus `refusing to add a ticket: fix the problems above first`.
    - `ls` showed only `0001-foo`, `config`, `roadmap.md`.
- `tickets.py --root .sdlc check` and `tickets.py --root .sdlc` (no subcommand) both printed `ok: 21 tickets, roadmap current`, rc 0.
- `plugins/sdlc-lite/scripts/check.sh`: rc 0. Level table, selftest, tickets selftest, board selftest, shellcheck and plugin validate all passed.
- `git status --short`: changes only in `plugins/sdlc-lite/scripts/tickets.py` and `.sdlc/ticket-numbered-folders/` (the `handoff.md` edit came before this step).

## Notes
- The grep criterion has a mistake: `new --numbered: folder` has never been literal text in `tickets.py`, including in step 1's version and the pre-step-3 copy. The selftest builds that label at runtime as `f'{label}: folder 0003-...'` from `numbered_ok('new --numbered', ...)`, which is still at line 595. So step 1 is intact. I did not add the string just to make the grep match. The verifier should grep `numbered_ok('new --numbered'` instead.
- Case 8's label is `plain new ignores an existing prefix mismatch`, because the handoff gave it no name.
- `cmd_roadmap` is unchanged, as specified. The planner's risk still applies: with the config on, `roadmap` can regenerate the file while `check` fails.
- `git checkout`, `restore` and `stash` were never run. Steps 1 and 2 are still in the working tree.
