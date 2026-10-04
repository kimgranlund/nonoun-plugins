<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `.sdlc/evals/CLAUDE.md`: new file containing `@AGENTS.md` and a newline.
- `.sdlc/evals/AGENTS.md`: new self-contained guide with these sections: Evals intro, File format (field table, an example eval), Table lock, Procedures, Limits.
- `.sdlc/evals/0000-baseline.md`: new baseline eval, written by `evals.py add baseline ...` with the method and result text from the handoff. No hand edits afterwards.
- `.sdlc/evals/table-lock.json`: written by `evals.py lock --eval .sdlc/evals/0000-baseline.md`. `previous_eval` is null and sha256 is `ab3aa58b...6ecd`.
- `.sdlc/AGENTS.md`: added the `## Other records` evals router line after `<!-- sdlc-lite:managed:end -->`. Nothing inside the managed block changed.

## Checks
- Criterion 1 (CLAUDE.md content): PASS
- Criterion 2 (required strings in AGENTS.md): PASS
- Criterion 3 (`validate_eval` on the baseline returns None): PASS
- Criterion 4 (baseline field and evidence greps): PASS
- Criterion 5 (lock keys, eval, `previous_eval` null): PASS
- Criterion 6 (lock sha equals the independently computed table hash): PASS
- `python3 plugins/sdlc-lite/scripts/evals.py check`: rc 0, "ok (1 evals, lock cites .sdlc/evals/0000-baseline.md)"
- `evals.py list | grep -q '^0000-baseline\.md'`: rc 0
- awk check that the router line sits after the end marker: rc 0
- (guard) `tickets.py --root .sdlc check`: rc 0, "ok: 208 tickets, roadmap current"
- (guard) git check-ignore on the four files: none are ignored
- (guard) run.sh and models.json have no diff against base: rc 0
- (guard) no changes outside `.sdlc` other than evals.py and check.sh: rc 0
- grep for em dashes in the changed files: 0 found. `git diff --check`: clean.

## Notes
AGENTS.md says, as the handoff requires, that `check.py` fails on a stale lock. At this point `check.py` does not call evals yet; only `check.sh` runs `evals.py selftest`. I assume a later step wires `evals.py check` into `check.py`.
