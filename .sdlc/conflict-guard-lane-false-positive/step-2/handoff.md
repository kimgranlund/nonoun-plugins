## Task goal
The merge-step conflict-marker guard (the `(guard)` line with `<<<<<<<` in the `merge-step` template) fails only on conflict markers the merge itself introduced, and passes a merge whose lane branch legitimately added a line starting with seven `<` or `>` to a touched file. Done when check.py's behavior probe proves both: the legit-lane-line merge passes, and a merge commit that kept real git conflict markers still fails, alongside the existing empty, marker, and clean probes.

## Step 2: Update the docs that describe the guard's criterion
level: L1
### Do
1. In the repo-root `CLAUDE.md`, in the "A merge is a standard builder step" decision, replace "no conflict markers in touched files" with wording that says the guard fails only on conflict-marker lines the merge itself added. Those are the lines `git diff-tree --cc` marks as new versus both parents, so a lane line that starts with seven `<` or `>` passes.
2. In `.claude/agents/sdlc-lite-author.md`, under `## Hazards learned`, add one line. It says the merge-step conflict-marker guard reads `git diff-tree --cc HEAD` (`++` lines only), so a lane's own marker-like lines pass. It also says the check.py probe holds the empty, marker, legit lane line, real conflict kept, and clean cases.
3. Use no em dashes.
### Acceptance criteria
- `! grep -q 'no conflict markers in touched files' CLAUDE.md`
- `grep -q 'diff-tree --cc' CLAUDE.md`
- `grep -q 'diff-tree --cc' .claude/agents/sdlc-lite-author.md`
- `! grep -n '—' CLAUDE.md .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
