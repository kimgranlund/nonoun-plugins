## Verdict
pass

## Criteria
- #1 `fanout.py selftest` exits 0 including case 20b: pass. Evidence: ran `python3 plugins/sdlc-lite/scripts/fanout.py selftest` in the tree, output ended `fanout selftest: PASS`, rerun with `echo rc=$?` gave rc=0. Case 20b is at fanout.py (new selftest block after case 20): gitignored `.sdlc/`, uncommitted handoff.md and plan.md, driver `test -f .../plan.md && ...`, asserts rc 0 and `| alpha | T-0001 | merged |`. Red control 1: base tree extracted with `git archive 4694d0cd` plus only the two selftest hunks applied; selftest FAIL with `case 20b ... rc=2 err='fanout: not committed at c6629ff5b8b4: .sdlc/a/handoff.md ...'`. Red control 2 (plan.md conjunct): fixed tree with the copy narrowed to handoff.md only; case 20b FAIL (rc=1, lane left open), so the plan.md-present driver check bites.
- #2 uncommitted handoff in a repo that does not ignore `.sdlc/` still refused (case 20), and `prep` still refuses a gitignored uncommitted handoff (case 22): pass. Evidence: case 20 and the new case 22 prep line (`gxp`, asserts rc 2 and `not committed at`) are both inside the passing selftest. Negative control: fixed tree with the `check-ignore` condition removed from preflight; selftest FAIL with `case 20 uncommitted handoff: refused naming git add -f, got rc=0` plus case 22 parity failures, so case 20 bites on the check-ignore conjunct. The prep refusal holds by construction: `cmd_prep` calls `preflight(a)` with `copy_ignored` defaulting False (only `cmd_run` passes True); the prep assertion passes at base as expected, so it is a guard rather than a new-behavior check.
- #3 `git diff` touches only fanout.py and sdlc-internals.md plus the ticket folder: pass. Evidence: `git status --short` and `git diff --stat` list only `plugins/sdlc-lite/scripts/fanout.py`, `docs/references/sdlc-internals.md`, and files under `.sdlc/0477-fanout-gitignored-sdlc/` (handoff.md, base-sha, skips.md, verifier-L2.*). `git diff --check` clean.

## Out of scope changes
None. The docs diff is one sentence in the fanout section describing run-vs-prep behavior (checked with word-diff). The `git add -A` tolerance for the git "ignored by one of your .gitignore" exit in `merge_gate_close` is required for case 20b to reach `merged` (a gitignored trail leaves nothing to stage), and it re-raises on any other add failure.

## For the next attempt
None
