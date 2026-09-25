## Task goal
Define `step-<n>.superseded-<k>/` as the name for a step dir replaced by a replan. `board.py` and `bench-summary.sh` skip it when counting steps, but still count its cost, and `/chain` and `handoff-format` document and perform the rename.

## Step 3: Document the name and perform the rename in /chain
level: L1
### Do
- In `plugins/sdlc-lite/skills/handoff-format/SKILL.md`:
  - Add `step-2.superseded-1/   a step replaced by a replan; ignored as a step, still counted for cost` to the layout block after `step-2/ ...` (~line 21).
  - Add one rule line: a live step dir is exactly `step-<digits>`; a replan renames replaced dirs to `step-<n>.superseded-<k>/` (k is the first free number); the board and scripts do not count these as steps.
- In `plugins/sdlc-lite/skills/chain/SKILL.md`, in step 4.2 (line 30):
  - Before "rewrite the remaining step handoffs", add that the conductor moves each `step-<n>/` with n at or above the blocked step that already holds builder or verifier output to `step-<n>.superseded-<k>/`, taking the first free k.
  - Then it writes fresh `step-<n>/handoff.md`.

### Acceptance criteria
- `grep -n 'superseded' plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md` shows the layout entry, the rule line, and the step 4.2 rename instruction.
- `plugins/sdlc-lite/scripts/check.sh` passes end to end, apart from the expected CLAUDE.md validate warning.

## Paths
Edit only files in this worktree (/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets7/plugins/sdlc-lite). Do not commit.
