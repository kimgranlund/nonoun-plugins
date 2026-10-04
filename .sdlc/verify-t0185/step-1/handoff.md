## Task goal
Independently verify branch t0185 (T-0185: `.sdlc/evals/`, `scripts/evals.py`, the model-table lock and its `check.py` guard) against main before it merges.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion. In a throwaway copy under $SDLC_TMP_WORKTREES show these defects are caught: (a) one model row of `plugins/sdlc-lite/scripts/run.sh` changed with the lock untouched, (b) a `models.json` model changed with the lock untouched, (c) the lock updated to cite an eval file that does not exist, (d) the lock updated with an eval that is not later than `previous_eval`, (e) `evals.py` with the hash comparison skipped. Confirm `git diff main -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json` shows no model or effort change (this branch changes no model default). Read `docs/validation/evals-live-run.md` against its evidence. Confirm the check.py guard coexists with main's lean-lane guard (both numbered, both run). No em dashes in new text.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/evals.py selftest`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
