<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints PASS and exits 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS`, rc=0.
- Negative control fails on (v1): pass. Evidence: in a scratch copy in /tmp, `expect.strip() != digest` was replaced with `False`. The selftest printed `FAIL, these did not bite: (v1) ... rc=0` and also `(v5) ...`. So the check can go red, and the mismatch conjunct is the one that bites.
- Temp-root CLI, dry run ends with `expect <12 hex>`: pass. Evidence: last line was `expect 0e67316813a8`.
- `--skip 2` with no `--expect` exits 1 and stderr ends `nothing written`: pass. Evidence: `--skip needs --expect <digest> ... nothing written`, rc=1.
- Reordered list with the old digest refuses and writes nothing: pass. Evidence: the stderr said `--expect 0e67... does not match the current Follow-ups in filer-L1.md ... nothing written`, rc=1. The hash of all files under `.sdlc` was identical before and after (`unchanged`).
- Unchanged list with `--skip 2 --expect <digest>` exits 0: pass. Evidence: `T-0001 done; 2 follow-up ticket(s): ...; skipped by --skip: 2`, rc=0.
- `close --help` lists `--expect DIGEST`: pass. Evidence: help output line 2 shows `[--expect DIGEST]` and line 20 shows `--expect DIGEST  the digest from the --dry-run last line`.
- `--expect` appears in the docstring Usage line and close paragraph: pass. Evidence: `grep -n expect` hits at tickets.py lines 5 and 30-34.
- Existing behavior unchanged, plain close needs no token: pass. Evidence: selftest cases (a) to (u) all pass, and case (v4) plain close returned rc 0.

## Out of scope changes
- `.sdlc/guard-close-skip-against-index/handoff.md` shows as modified in `git status`. It is task bookkeeping, not product code.
- The diff for `plugins/sdlc-lite/scripts/tickets.py` stays within the step. Untracked `.sdlc` artifacts (planner-L2.md, runs.jsonl, step-1, step-2) are expected.

## For the next attempt
None
