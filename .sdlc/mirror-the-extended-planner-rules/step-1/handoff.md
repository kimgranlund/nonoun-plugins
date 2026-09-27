## Task goal
The Plan-defect route bullet in `.claude/agents/sdlc-lite-author.md` also states the extended planner rules that CLAUDE.md's plan-defect decision and `plugins/sdlc-lite/agents/planner.md` rules 11 and 12 carry: each `(guard)` is seen red first (un-negated, or on a fixture) so it can go red, and files other lanes change are checked by membership or structure, never by an exact line.

## Step 1: Mirror rules 11 and 12 into the plan-defect route bullet
level: L1
### Do
In `.claude/agents/sdlc-lite-author.md`, extend the "Plan-defect route" bullet (line 18) to also state the two extended planner rules from `plugins/sdlc-lite/agents/planner.md` rules 11 and 12: (a) a `(guard)` is a check that can go red, and the planner sees it red first (un-negated, or on a fixture) before writing it; (b) a file other lanes also change (a generated index, a registry, a catalog, a shared config) is checked by membership or structure, never by an exact line or whole-file comparison. Add this as new sentences appended to the existing bullet (or a new bullet immediately after it), keeping all existing wording unchanged. Do not touch any other file.
### Acceptance criteria
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md` finds a match (red now: the phrase is currently absent from this file).
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md` finds a match (red now: the phrase is currently absent from this file).
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md` exits 1 (the file has uncommitted changes) and `git diff HEAD -- .claude/agents/sdlc-lite-author.md | grep -c '^-[^-]'` is `0` (no existing line was removed, only additions).
- `test "$(git diff --name-only HEAD -- . ':!.sdlc')" = ".claude/agents/sdlc-lite-author.md" && test -z "$(git ls-files --others --exclude-standard -- . ':!.sdlc')"` exits 0 (only the target file changed outside the `.sdlc/` pipeline artifacts, and no new file was added outside `.sdlc/`).
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
