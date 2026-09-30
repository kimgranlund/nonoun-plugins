<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0151: fanout refuses to merge into a dirty integration tree, so a red-gate reset never wipes uncommitted edits

## PR body
### Summary
`fanout.py` ran `git reset --hard <pre-merge HEAD>` on the integration worktree after a red gate or a failed merge. If a human had uncommitted tracked edits there, the reset wiped them. This change stops that: `run_ticket` now checks the integration tree first and refuses to merge into it if it's dirty.

This is the fix for T-0151, from the gen-ui-system-svelte-lite overnight run on 2026-09-28 (feedback batch 3, item 7).

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - In `run_ticket`, inside the merge lock and before the pre-merge `rev-parse HEAD`, the tree is checked with `git status --porcelain --untracked-files=no`.
  - When dirty, the ticket returns `integration dirty: <first path>` with `lane_sha[:7]`. No merge, reset, or gate runs. `run_lane` then handles the ticket like any other non-merged outcome.
  - Untracked files are ignored on purpose, because `reset --hard` never removes them.
  - If the status command itself fails, the ticket returns `integration status failed: ...` instead of raising. The plan didn't ask for this outcome; the builder added it, and the verifier judged it in scope.
  - Updated the step-5 docstring.
  - Added selftest case 5d.
- `docs/maintenance/sdlc-internals.md`: the fanout paragraph now says a dirty integration tree is refused with `integration dirty`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: one sentence on the same refusal.

### Verification
- **Selftest written first.**
  - Case 5d uses a tracked file and a stub driver that edits it in the integration worktree, then runs a red gate.
  - It asserts three things: the report row is `integration dirty`, the edit is still in `git diff` in the integration tree, and there is no merge commit for the ticket.
  - Before the guard it failed with two misses. The outcome was `red: test -z ... rc=1` and the integration `git diff` was empty, so the edit had been wiped.
- **Selftest after the fix.** `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed `fanout selftest: PASS` and exited 0.
- **Independent negative control.** The verifier put the built `fanout.py` into a throwaway worktree at the base SHA and deleted only the guard lines. The selftest failed again on the outcome-row and edit-survives assertions. The merge-commit assertion did not fail, because the red gate resets the merge away either way. So it does not discriminate here.
- **Greps.** `grep -qF 'integration dirty'` passes on `fanout.py`, `sdlc-internals.md` and `SKILL.md`.
- **`check.py`.** `python3 plugins/sdlc-lite/scripts/check.py` exits 0 with `ok: 18 role levels, 8 agents checked`. The output is identical to the same command run at the base SHA.
- **Scope.** The diff touches only the three files above (verified against the base SHA). `git diff --check` is clean.
- **Verifier verdict.** pass.
- **Not run.** The artifacts show no live host run of fanout beyond the selftest, and no run of `bash plugins/sdlc-lite/scripts/check.sh` or `scripts/check-packaging.py`.

## Changelog entry
- Fixed: `fanout.py` no longer discards uncommitted tracked edits in the integration worktree. It now refuses a ticket with `integration dirty: <path>` before merging, so the red-gate `reset --hard` only ever runs on a tree that was clean when the merge began.

## Follow-ups
- note: The `integration status failed: ...` outcome in `fanout.py` was added beyond the plan, and only the dirty path has a selftest case; the status-failure path is untested.
- note: The merge-commit assertion in selftest case 5d passes even with the guard removed, so only the outcome-row and edit-survives assertions catch a regression.
- note: The guard ignores untracked files in the integration tree by design, since `reset --hard` leaves them alone.
