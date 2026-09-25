<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0059: Standard merge-branch step template for builders

## PR body
### Summary
Merging one lane into another is now a standard builder step. The planner has a fill-in `merge-step` template, and every acceptance criterion in it can go from red to green. The builder may create the merge commit on a merge step and on no other step. A new check.py guard stops the template from drifting.

This comes from a peer session. There, a merge conflict between lanes needed a hand-written handoff, and the builder correctly blocked on a criterion it could not meet.

### Changes
- `plugins/sdlc-lite/agents/planner.md`: new `## Merge steps` section with a fenced `merge-step` template. Its criteria:
  - HEAD has two parents (`git rev-list --parents -n1 HEAD | wc -w` is 3).
  - `git merge-base --is-ancestor <branch> HEAD`.
  - (guard) no `MERGE_HEAD`.
  - (guard) no conflict markers in the files the merge touched.
  - (guard) each project gate shows no new findings versus `HEAD^1`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: new `### Merge step` subsection under `## Step handoff`. It holds a byte-identical copy of the template and notes that `steps.py split` copies it like any other step.
- `plugins/sdlc-lite/agents/builder.md`: new rule 4.
  - On a merge step, the builder runs `git merge --no-ff <branch>`, resolves conflicts and creates the merge commit.
  - It never runs `git merge --abort` after resolving, and it makes no other commit.
  - It blocks if the tree has uncommitted tracked changes.
  - It never commits on any other step.
  - It never pushes, opens a PR or publishes.
- `plugins/sdlc-lite/scripts/check.py`: new guard (docstring item 6). It fails when:
  - either template block is missing or empty,
  - the two blocks differ,
  - the planner block fails `steps.py lint`,
  - `builder.md` lacks `git merge --no-ff`.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: a new Decisions bullet, the guard added to the `check.sh` Commands line, and an Invariants bullet.
- `hooks/`, `run.sh`, `steps.py` and `verifier.md` are unchanged.

### Verification
Each step was checked by a verifier. All three passed.
- Step 1, template and builder rule (builder L3, verifier L2 pass):
  - The extracted template passes `steps.py lint` with 5 command spans.
  - The two copies diff clean.
  - Every required command is present.
  - `check.sh` exits 0.
  - Negative controls failed as expected: at the base commit, with a deliberately broken span, and with a one-byte change between the copies.
- Step 2, check.py guard (builder L2, verifier L1 pass):
  - check.py fails in temp copies when the copies differ, when both copies stop parsing, and when `--no-ff` is removed from builder.md.
  - It passes on the real tree.
  - `check.sh` exits 0.
- Step 3, docs (builder L1, verifier L1 pass):
  - The greps find `merge-step` in both files and `git merge --no-ff` in CLAUDE.md. Neither grep matches at HEAD.
  - `check.sh` exits 0.

No step ran a live merge on a real repo.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added a standard `merge-step` template for planners. Each of its criteria can go from red to green (two-parent commit, branch is an ancestor, no MERGE_HEAD, no conflict markers, gates with no new findings versus the first parent). The builder may now create the merge commit, and only on a merge step. check.py keeps both copies of the template identical and lint-clean.

## Follow-ups
- Run a live merge step on a throwaway repo to prove the builder makes exactly one two-parent merge commit and the verifier's criteria pass (only static checks were run for T-0059).
- Merge-step conflict-marker guard scans the whole tree when `git diff --name-only HEAD^1 HEAD` is empty and can flag legitimate lines starting with seven `<` or `>`; make it fail safe or skip on an empty path list.
