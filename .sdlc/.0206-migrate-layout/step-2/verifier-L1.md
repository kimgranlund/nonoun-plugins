<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- AC1, `grep -qF 'migrate-layout [--dry-run] [--rewrite-refs]' docs/maintenance/sdlc-internals.md`: pass. Evidence: the grep printed `c1ok`. The diff against `44168d55` shows the passage added to the `scripts/tickets.py` entry, so the base lacked it and the check can go red.
- AC2, argument-hint and bullet: pass. Evidence: the combined command printed `c2ok`. The diff adds `| migrate-layout [--dry-run] [--rewrite-refs]` to the `argument-hint` (line 4). It adds one Rules bullet that holds `onboard.py setup`, `layout: flat`, the `--dry-run`, `--rewrite-refs` and commit steps, and the `docs/reports/` note.
- Doc passage matches step 1, which the Do requires. I read `tickets.py`: the docstring and code at lines 122-134 give the same preconditions, the `Path.rename` moves, `keep <file> (dated record under docs/reports/)`, the two config lines, and `nothing to migrate`. Line 1885 has the `layout: flat` warning text.
- Guard, `git diff --check`: pass. Evidence: printed `c3ok`.
- Guard, changed-files allowlist: pass. Evidence: printed `c4ok`. `git diff --stat` shows only `sdlc-internals.md`, `tickets.py` and `ticket/SKILL.md`.
- Guard, `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc 0. The tail reads `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Guard, `python3 scripts/check-packaging.py`: pass. Evidence: rc 0.
- Guard, `codex_roles.py generate --check`: pass. Evidence: rc 0.
- Guard, `tickets.py --root .sdlc check`: pass. Evidence: rc 0. It printed `ok: 309 tickets, roadmap current` and the expected flat-layout warning.

## Out of scope changes
None. The three modified files are all allowed. The untracked `.sdlc/` files are exempt from the allowlist.

## For the next attempt
None
