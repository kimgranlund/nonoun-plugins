## Task goal
The solo operator is the default lane for size S and M tickets. Read `.sdlc/0215-solo-operator-tiers/handoff.md` and the branch verifier's finding in `.sdlc/verify-t0215/step-1/verifier-L3.md` (section For the next attempt).

## Step 2: Update the lane documentation the new output left stale
level: L2

### Read first
- .sdlc/verify-t0215/step-1/verifier-L3.md (the finding, with exact lines)
- plugins/sdlc-lite/skills/sdlc-lite/SKILL.md
- plugins/sdlc-lite/skills/chain/SKILL.md

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests or doc edits outside this step. Report blocked instead of looping. `steps.py lane` now prints `solo` for size S and M before planning and never `fix`; after planning it prints `lean` or `full`.
1. plugins/sdlc-lite/skills/sdlc-lite/SKILL.md line 44 (the Codex host entry skill): the first-line mapping becomes `solo` means run the `solo` session agent at the tier for the ticket size (S, M, L; the Codex agents are `sdlc-solo-l1`, `sdlc-solo-l2`, `sdlc-solo-l3`), `lean` the lean chain in the chain workflow, `full` the chain workflow. Keep the rest of the line.
2. plugins/sdlc-lite/skills/chain/SKILL.md line 27: say `lane` prints `solo`, `lean`, or `full`. Keep the phrases `## Lean chain` and `always runs the filer` (check.py pins them).
3. docs/lean-sdlc/design.md lines 68 and 283: replace `fix` with `solo` where they describe the lane output for a size-S fixture and the output list.
4. plugins/sdlc-lite/skills/level-rubric/SKILL.md line 93: name `solo` among the session agents.

### Acceptance criteria
- `grep -q "solo" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -q "sdlc-solo-l2" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -q "prints .solo., .lean., or .full." plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "## Lean chain" plugins/sdlc-lite/skills/chain/SKILL.md && grep -q "always runs the filer" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "solo" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs`
