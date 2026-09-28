<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0115: fanout reports an inherited red builder stop and skips commit, merge, and close

## PR body
### Summary
When a fanout lane's ticket stops on an `inherited red` builder, `fanout.py` used to commit the half-done lane, merge it, and then report `merged, close refused: ...` or `red: <gate>`. It now detects the stop right after the driver exits 0. It reports `inherited red: step-<n>: <tests>` and skips the lane commit, merge, gates, and close. The lane stops, later tickets are `skipped`, the run exits 1, and the uncommitted work stays in the lane worktree.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Adds `import steps`, `STEP_DIR_RE`, and `inherited_red(ticket_dir)`. It scans `step-<n>` dirs in numeric order and ignores `step-<n>.superseded-<k>`. It calls `steps.next_action` on each, and treats a `steps.Fail` or any exception as "not inherited".
  - At the first `inherited` step it reads the tests from the newest builder result's `## Status` line.
  - `run_ticket` calls it after the `driver failed` check and before `git add -A`.
  - The module docstring gains a per-ticket step and names the new selftest case.
  - Selftest case 5 covers an inherited-red lane, plus a negative control with a `done` builder that merges and closes normally.
- `CLAUDE.md`: the `scripts/fanout.py` bullet describes the new outcome.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: the Report section says the outcome means those tests were already red on the base, so fix main first. Nothing from that ticket was merged.
- `.claude/agents/sdlc-lite-author.md`: the `Inherited-red route:` line and its keep-in-sync list now include `fanout.py` and the /fanout skill.
- `plugins/sdlc-lite/scripts/check.py`: `INHERITED_RED_DOCS` gains `scripts/fanout.py` and `skills/fanout/SKILL.md`, and docstring item 8 names both.

Other fanout outcomes, the lane commit message, and the merge, gate, and close flow for merged tickets are unchanged. The chain SKILL and `conductor.md` are unchanged.

### How each was verified
Both steps passed independent verification (step 1 verifier L2, step 2 verifier L1).
- Step 1:
  - The verifier ran the three `python3 -c` and grep criteria and the `fanout.py selftest`. All passed.
  - `scripts/check.sh` exited 0.
  - The selftest reads case 5 as asserting exit 1, the exact outcome `inherited red: step-1: test_a`, T-0002 `skipped`, zero merge commits, no work file on the integration branch, the handoff still `status: ready`, and the uncommitted step file kept in the lane.
  - The negative control asserts `merged` and `status: done`.
  - The case bites: in a temp copy where `inherited_red` returns `None`, the selftest failed with 7 misses, all from case 5.
  - Only `fanout.py` changed under `plugins/sdlc-lite/scripts`.
- Step 2:
  - The four doc and guard greps passed, and `check.sh` exited 0.
  - The `check.py` guard can go red: in a throwaway copy, changing the phrase in the fanout SKILL made `check.py` print `FAIL skills/fanout/SKILL.md: inherited-red route missing "inherited red"`.
  - `git diff` on the chain skill and agents was empty.

## Changelog entry
- fanout: a lane whose ticket stops on an `inherited red` builder now reports `inherited red: step-<n>: <tests>` and skips the lane commit, merge, and close. Later tickets in the lane are skipped and the work stays in the lane worktree. `check.py` guards the fanout docs for this route.

## Follow-ups
- fanout.py still reports only `driver failed rc=<n>` when a lane's conductor exits non-zero after an inherited-red stop, so the inherited-red cause stays hidden in that case; detect it there too.
