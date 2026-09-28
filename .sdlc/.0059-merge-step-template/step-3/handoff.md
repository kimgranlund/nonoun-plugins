## Task goal
Merging two lanes is a standard builder step with criteria it can meet.

## Step 3: Update CLAUDE.md and the author agent
level: L1
### Do
1. In the repo root `CLAUDE.md`, add one Decisions bullet covering four points:
   - The standard `merge-step` template lives in `agents/planner.md` and `skills/handoff-format/SKILL.md`.
   - On a merge step, the builder runs `git merge --no-ff <branch>` and makes the merge commit. That is the only step kind where the builder commits. Push and publishing stay blocked, and the verifier never changes git state.
   - Its criteria are two parents, branch as ancestor, no MERGE_HEAD, no conflict markers in touched files, and gates with no new findings versus HEAD^1.
   - `check.py` keeps the two copies identical, lint-clean, and in step with builder.md.
2. Mention the new guard in the `check.sh` Commands line where it lists what the check covers.
3. In `.claude/agents/sdlc-lite-author.md`, add an Invariants bullet: keep the `merge-step` template identical across `agents/planner.md` and `skills/handoff-format/SKILL.md`, and in sync with the builder merge-commit rule, check.py, and CLAUDE.md.
### Acceptance criteria
- `grep -n 'merge-step' CLAUDE.md .claude/agents/sdlc-lite-author.md` prints at least one line for each of the two files.
- `grep -n 'git merge --no-ff' CLAUDE.md` prints at least one line.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. (guard)
