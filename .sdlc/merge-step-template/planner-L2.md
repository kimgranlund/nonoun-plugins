<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Planner guidance and the handoff-format docs carry a standard `merge <branch>` step template whose criteria can actually be met and that passes `steps.py lint`; the builder may create the merge commit only on a merge step; and a check.py guard keeps all of this from drifting.

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

## Step 2: Guard the template in check.py
level: L2
### Do
Add a check to `plugins/sdlc-lite/scripts/check.py`, next to the plan-defect route checks, and add a line for it to the module docstring. The check does five things:
1. It extracts the fenced `merge-step` block from `agents/planner.md` and from `skills/handoff-format/SKILL.md`. Each block runs from the fence line that is three backticks plus `merge-step` to the next line that is exactly three backticks.
2. It fails if either block is missing or empty, or if the two blocks differ.
3. It replaces `<n>` with `1`, writes the planner block to `planner-L2.md` in a temp dir, and runs `python3 <root>/scripts/steps.py lint` on that file. It fails on a nonzero exit, and the error message includes the lint's stderr.
4. It fails if `agents/builder.md` lacks `git merge --no-ff`.
5. It removes the temp dir.

Every failure goes into `errors` with the same `FAIL` output format the file already uses.
### Acceptance criteria
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/merge-base --is-ancestor/merge-base/' "$d/a/p/skills/handoff-format/SKILL.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0. The two blocks now differ, so check.py fails.
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/wc -w\)/wc -w/' "$d/a/p/agents/planner.md" "$d/a/p/skills/handoff-format/SKILL.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0. The blocks are still identical but no longer parse, so the lint fails.
- `d=$(mktemp -d) && mkdir -p "$d/a" && cp -R plugins/sdlc-lite "$d/a/p" && cp CLAUDE.md "$d/" && perl -pi -e 's/git merge --no-ff/git merge/g' "$d/a/p/agents/builder.md" && ! python3 "$d/a/p/scripts/check.py" "$d/a/p"` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` exits 0 on the real tree.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. (guard)

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

## Risks
- On a real merge where `git diff --name-only HEAD^1 HEAD` is empty, the conflict-marker grep scans the whole tree. It could flag a legitimate doc line that starts with seven `<` or `>` characters. The planner can narrow the path list in that case.
- The block extraction finds the end of the template by the first 3-character line after the opening fence. If a builder adds a 3-character line inside the block, the extracted block is cut short. The Step 1 and Step 2 criteria catch this: the lint, the missing-pattern loop, and the diff all fail.
- Allowing the builder to commit is a behavior change for a role. The author agent's rule 3 asks for one live run on a throwaway repo, and that run is outside this plan's automated criteria.
- `check.sh` also depends on `claude plugin validate` and shellcheck. A failure in either that has nothing to do with this work would make the guard criteria red.
