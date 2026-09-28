## Task goal
Stop run.sh from overwriting results: a rerun of the same role and level (a replan, or a rebuild at the same level) writes a new numbered file, the first file stays as it was, and /board, /chain, and the docs read the newest file.

All paths are in the worktree /Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets7. If you use git stash, use a unique tag and apply by SHA (the stash stack is shared with other sessions).

## Step 2: Docs and skills describe numbered reruns
level: L1
### Do
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` line 25: replace "Rerunning the same role and level overwrites them" with: a rerun writes `<role>-<level>-<k>.md`/`.log` (k = 2, 3, ...), the first result is never overwritten, and the newest file by mtime is the current one. Add `planner-L3-2.md` (a replan) to the layout example.
- `plugins/sdlc-lite/skills/chain/SKILL.md` §4.2: the replan writes a new `planner-L3[-k].md`, and /chain rewrites the remaining step handoffs from the newest planner file, leaving earlier plans in place. §4.4: a same-level rebuild writes `builder-L<n>-<k>.md`, so earlier attempts stay for the rubric's "earlier builder-*.md with Status blocked" count.
- Repo-root `CLAUDE.md`:
  - The "Run one role directly" line should note that a rerun writes `<role>-<level>-<k>.md` and never overwrites.
  - The Commands "Check everything" list should mention the run selftest.
- `.claude/agents/sdlc-lite-author.md` line 19: add the run selftest to the list of things check.sh runs.
### Acceptance criteria
- `grep -rn "overwrites" plugins/sdlc-lite/skills plugins/sdlc-lite/scripts CLAUDE.md` finds no line saying a rerun overwrites a result.
- `grep -n "<role>-<level>-<k>" plugins/sdlc-lite/skills/handoff-format/SKILL.md CLAUDE.md` matches in both files.
- `grep -n "newest" plugins/sdlc-lite/skills/chain/SKILL.md` matches the replan instruction.
- `grep -n "run selftest\|run-selftest" CLAUDE.md .claude/agents/sdlc-lite-author.md` matches in both.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.
