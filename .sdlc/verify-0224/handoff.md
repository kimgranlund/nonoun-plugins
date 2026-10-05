# Verify T-0224: the lane script writes the solo Skipped entries

## Goal
Independently verify `git diff main...HEAD` on branch solo-skips (T-0224).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0. Its `(lane solo close)` checks run `steps.py lane` then `tickets.py close --reason` with no fanout (T-0219 guard live): the close passes, running lane twice leaves one planner and one filer `## Skipped` entry, a size L (lane full) ticket gets none, and the negative control `SDLC_SELFTEST_NO_SKIPPED=1` makes the close refuse with `no ## Skipped entry`. Reproduce the negative control and the passing flow yourself in a throwaway repo (`tickets.py new`, set `size: M`, `steps.py lane`, `tickets.py close <slug> --reason x`).
2. `git diff main -- plugins/sdlc-lite/scripts/tickets.py` is empty (the guard is unchanged), and `write_solo_skips` writes only when the last `- lane:` line is solo, is idempotent, and writes nothing without a skips.md.
3. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 (case 16 still green) and fanout.py calls `steps.write_solo_skips` instead of holding its own writer.
4. `bash plugins/sdlc-lite/scripts/check.sh` exits 0; `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0; check.py item 25 exists with a negative control and the docstring guard numbers are unique.
5. docs/reports/solo-close-live-run.md: every number and claim (5 minutes 34 seconds, 19:08:15 to 19:13:49, exit 0, 9/9, the close exit 0 in call 8, models, token counts, $0.20 and $3.09, solo started with `--model sonnet --effort xhigh`) is backed by a committed, non-gitignored file under docs/reports/solo-close-live-run/ (`git ls-tree -r HEAD`, `git check-ignore` prints nothing for them).
6. agents/conductor.md and docs/maintenance/sdlc-internals.md say the lane script records the solo Skipped entries and stay short; `git diff --check main..HEAD` is clean and no em dash appears in the changed text files.
