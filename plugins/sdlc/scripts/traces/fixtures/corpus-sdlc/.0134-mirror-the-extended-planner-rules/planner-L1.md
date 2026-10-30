<!-- role=planner level=L1 model=sonnet effort=medium -->
Good: check.sh currently green (guard), and the target phrases are absent (red for the new-behavior criterion). Now write the plan.

## Goal
Add the extended planner-rule wording (a `(guard)` seen red first, and files other lanes change checked by membership or structure) to the plan-defect route bullet in `.claude/agents/sdlc-lite-author.md`.

## Step 1: Mirror rules 11 and 12 into the plan-defect route bullet
level: L1
### Do
In `.claude/agents/sdlc-lite-author.md`, extend the "Plan-defect route" bullet (line 18) to also state the two extended planner rules from `plugins/sdlc/agents/planner.md` rules 11 and 12: (a) a `(guard)` is a check that can go red, and the planner sees it red first (un-negated, or on a fixture) before writing it; (b) a file other lanes also change (a generated index, a registry, a catalog, a shared config) is checked by membership or structure, never by an exact line or whole-file comparison. Add this as new sentences appended to the existing bullet (or a new bullet immediately after it), keeping all existing wording unchanged. Do not touch any other file.
### Acceptance criteria
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md` finds a match (red now: the phrase is currently absent from this file).
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md` finds a match (red now: the phrase is currently absent from this file).
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md` exits 1 (the file has uncommitted changes) and `git diff HEAD -- .claude/agents/sdlc-lite-author.md | grep -c '^-[^-]'` is `0` (no existing line was removed, only additions).
- `git diff --stat HEAD | awk '{print $1}'` lists only `.claude/agents/sdlc-lite-author.md` as changed, and `git ls-files --others --exclude-standard` prints nothing (no other file touched, no new file added).
- (guard) `plugins/sdlc/scripts/check.sh` exits 0.

## Risks
None: this is a wording addition to one non-shipped, non-checked doc file, with no code path depending on its exact contents.
