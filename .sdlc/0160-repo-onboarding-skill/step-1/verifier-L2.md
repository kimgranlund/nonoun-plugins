<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: pass. Evidence: I ran it on Python 3.9.6. It printed `gate layout-parsing: positive ok, negative ok` and `gate import-detection: positive ok, negative ok`, and exited 0.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate layout-parsing: positive ok, negative ok"`: pass. Evidence: I ran it and it exited 0. The check can go red: a copy of the script with the duplicate-home rule disabled in the real parser printed `gate layout-parsing: FAIL positive failed: home twice: parsed without an error` and exited 1. A copy with the error line number shifted by one printed `FAIL ... error at line 4, expected 3` and exited 1. The mutated copies lived in a temp dir and were deleted.
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qF "gate import-detection: positive ok, negative ok"`: pass. Evidence: I ran it and it exited 0. The check can go red: a copy with the fence rule broken in the real `has_import` printed `gate import-detection: FAIL positive failed: counted an import in '```\n@AGENTS.md\n```\n'`. A copy that dropped `@./AGENTS.md` from `IMPORTS` printed `FAIL positive failed: missed the import ...`. Both exited 1.

The builder's claims were checked against the tree:
- The file exists and is executable (`-rwxr-xr-x`).
- `parse_layout`, `frozen_match`, `scan_lines`, `has_import` and `LayoutError(path, line, reason)` are all in `onboard.py`. The argparse CLI has `setup`, `check` and `selftest`. `setup` and `check` print "not implemented" and return 2 (`onboard.py:303-316`).
- The code uses no `match` statements and no `X | Y` type unions, and it ran on 3.9.6.
- The import-detection negative control skips the fence rule, as the design's gate table requires (`onboard.py:269`).
- The layout-parsing gate covers missing backticks, a duplicate heading and a duplicate home, each with an asserted line number. I read these at `onboard.py:207-236`. The M2 and M3 runs above confirm they can fail.

## Out of scope changes
None. `git status` shows one new source file, `plugins/sdlc-lite/scripts/onboard.py`, and `git diff --stat` shows no tracked files modified. The other untracked files are run artifacts under `.sdlc/0160-repo-onboarding-skill/step-1/`, which the step expects.

## For the next attempt
None.

Steelman: I drafted the fail reason "`frozen_match` has no selftest gate". The builder would answer that the step's Do lists only the `layout-parsing` and `import-detection` gates, and the acceptance criteria don't mention `frozen_match`. Dropped.
