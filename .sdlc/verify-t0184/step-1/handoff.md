## Task goal
Independently verify branch t0184 (T-0184: one declared result schema per role, `scripts/results.py`, used by `run.sh` and `steps.py`) against main before it merges.

## Step 1: Verify the branch
level: L3

### Do
Read-only verification. Run every criterion. Then inject defects in a throwaway copy under $SDLC_TMP_WORKTREES and show each is caught: (a) `results.py validate` accepts everything, (b) the required-section check removed for one role, (c) `steps.py next` ignoring an invalid result (still prints verify), (d) `run.sh` reverted to carry its own section table so the two tables can differ. Confirm no copy of the schema table remains in `run.sh` or `steps.py`, that every previously valid result form still validates (run `results.py validate` over every `*-L*.md` result under `.sdlc/` of this branch and list any refusal with its reason: a refusal of a result that earlier passed is a regression), and read `docs/reports/role-result-schema-live-run.md` against its evidence. No em dashes in new text.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/results.py selftest`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
