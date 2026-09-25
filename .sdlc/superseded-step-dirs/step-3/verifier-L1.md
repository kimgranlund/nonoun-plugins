<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -n 'superseded'` shows the layout entry, the rule line, and the step 4.2 rename instruction: pass. Evidence: `grep -n superseded plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md` prints three lines:
  - handoff-format/SKILL.md:22 `step-2.superseded-1/   a step replaced by a replan; ignored as a step, still counted for cost`. This is the layout entry, placed right after `step-2/ ...`.
  - handoff-format/SKILL.md:29 `A live step dir is exactly \`step-<digits>\`; a replan renames replaced dirs to \`step-<n>.superseded-<k>/\` (k is the first free number); the board and scripts do not count these as steps.` This is the rule line.
  - chain/SKILL.md:30, step 4.2, reads "move each `step-<n>/` with n at or above the blocked step that already holds builder or verifier output to `step-<n>.superseded-<k>/` (first free k), then write fresh `step-<n>/handoff.md` files". It comes before "rewriting the remaining step handoffs from the newest planner file".
  - The check can fail: the same grep on HEAD's copies of both files (`git show HEAD:...` to /tmp) matched nothing and exited with rc=1.
- `plugins/sdlc-lite/scripts/check.sh` passes end to end: pass. Evidence: I ran it and it exited with rc=0. Its output:
  - `ok: 18 role levels, 8 agents checked`
  - `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `run selftest: PASS`
  - `ok: shellcheck`, `ok: plugin validate`
  - `grep -i 'warn|fail|error'` on the output found no warnings or failures.

## Out of scope changes
None for this step. The step 3 diff touches only the two skill files the handoff names. `scripts/board.py`, `scripts/bench-summary.sh`, and `.sdlc/superseded-step-dirs/handoff.md` are also modified in the tree, but they belong to earlier steps of this task (step-1 and step-2 already have builder and verifier output) and to its planning.

## For the next attempt
None
