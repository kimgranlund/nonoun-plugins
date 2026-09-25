## Task goal
Merging two lanes is a standard builder step with criteria it can meet.

## Step 1: Add the merge step template and the builder merge rule
level: L3
### Do
1. In `plugins/sdlc-lite/agents/planner.md`, add a short `## Merge steps` section after `## Criteria that can pass` and before the final-message format.
   - It says: when a task merges one lane into another, emit this step block and fill it in. Replace `<branch>` with the lane branch. Replace `<gate command>` with the project's own check or test commands, one criterion per gate, the way the planner names them for any step. Pick the level with the rubric as usual.
   - Criterion 1 of the plan still applies. Before the merge the two-parent and ancestor criteria must be red. If `<branch>` is already an ancestor of HEAD, no merge step is needed.
   - Then comes the template as a fenced block. The opening fence line is exactly three backticks followed by `merge-step`. The closing fence line is exactly three backticks. No line inside the block may be exactly 3 characters long, because the checks find the block's end that way.
2. The block content:
   - The line `## Step <n>: Merge <branch>`.
   - The line `level: L<n>`.
   - `### Do`: run `git merge --no-ff <branch>` on a tree with no uncommitted tracked changes, resolve every conflict keeping both lanes' intent, run the gates, and create the merge commit. Never push.
   - `### Acceptance criteria`, with these bullets:
     - `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`
     - `git merge-base --is-ancestor <branch> HEAD`
     - (guard) `! git rev-parse -q --verify MERGE_HEAD`
     - (guard) `! git grep -nE '^(<<<<<<<|>>>>>>>)( |$)' -- $(git diff --name-only HEAD^1 HEAD)`
     - (guard) `<gate command>` shows no new findings versus the first parent: run the same command in a `git worktree add <tmp> HEAD^1` copy and compare.
3. In `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, under `## Step handoff`, add a `### Merge step` subsection. It says the planner emits this block and that `steps.py split` copies it like any other step. Then it holds the same fenced `merge-step` block, byte-identical to the one in planner.md.
4. In `plugins/sdlc-lite/agents/builder.md`, add a numbered rule about merge steps. A merge step is a step whose title starts with `Merge ` and whose Do runs `git merge --no-ff <branch>`.
   - On a merge step, the builder runs `git merge --no-ff <branch>`, resolves conflicts, and creates the merge commit. It never runs `git merge --abort` after resolving conflicts, and it makes no other commit.
   - If the tree has uncommitted tracked changes before the merge, Status is blocked.
   - On every other step, the builder never commits.
   - Push, PR, and publishing stay blocked. The hook is unchanged.
5. Do not touch `hooks/`, `run.sh`, `steps.py`, or `agents/verifier.md`. The verifier already never changes git state.
### Acceptance criteria
- `d=$(mktemp -d) && sed -n '/^...merge-step$/,/^...$/p' plugins/sdlc-lite/agents/planner.md | sed '1d;$d;s/<n>/1/g' > "$d/planner-L2.md" && grep -q '^## Step 1: Merge ' "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"` prints `steps lint: ok` and exits 0.
- `t=$(sed -n '/^...merge-step$/,/^...$/p' plugins/sdlc-lite/agents/planner.md) && test -n "$t" && ! for p in 'git merge --no-ff' 'git rev-list --parents -n1 HEAD' 'git merge-base --is-ancestor' 'git grep -nE' 'MERGE_HEAD' 'HEAD^1'; do grep -qF -- "$p" <<<"$t" || echo "missing $p"; done | grep missing` exits 0.
- `test -n "$(sed -n '/^...merge-step$/,/^...$/p' plugins/sdlc-lite/skills/handoff-format/SKILL.md)" && diff <(sed -n '/^...merge-step$/,/^...$/p' plugins/sdlc-lite/agents/planner.md) <(sed -n '/^...merge-step$/,/^...$/p' plugins/sdlc-lite/skills/handoff-format/SKILL.md)` exits 0.
- `grep -n 'git merge --no-ff' plugins/sdlc-lite/agents/builder.md` prints at least one line.
- Reading `plugins/sdlc-lite/agents/builder.md` shows three rules: the builder may commit only on a merge step, it makes no commit on any other step, and it never pushes or publishes.
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/agents/verifier.md` exits 0. (guard)
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. (guard)
