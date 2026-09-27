<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None.

## PR title
T-0134: Mirror the extended planner rules into sdlc-lite-author.md

## PR body
### Summary
Extends the "Plan-defect route" bullet in `.claude/agents/sdlc-lite-author.md` with the two extended planner rules from `plugins/sdlc-lite/agents/planner.md` (rules 11 and 12), so the maintainer agent's own doc mirrors what CLAUDE.md's plan-defect decision and the planner already state: a `(guard)` is a check that can go red, seen red first (un-negated, or on a fixture) before it's written; and a file other lanes also change (a generated index, a registry, a catalog, a shared config) is checked by membership or structure, never by an exact line or whole-file comparison. This closes a follow-up from T-0123, where a step 3 builder had let this file drift out of sync with the rules it lists.

### Changes
- `.claude/agents/sdlc-lite-author.md`: appended two sentences to the existing "Plan-defect route" bullet (line 18). No existing wording was removed or altered, and no other file was touched.

### How verified
- Planner (L1) produced a single-step plan with five acceptance criteria, including two red-now content greps and a guard on `plugins/sdlc-lite/scripts/check.sh`.
- First builder attempt (L1) made the edit; the file-scope acceptance criterion, as originally written (`git diff --stat HEAD | awk '{print $1}'`), failed only because it could not distinguish the target file from the pipeline's own uncommitted `.sdlc/` artifacts — a plan defect, not a build defect.
- First verifier (L1, opus) confirmed the content and no-removed-line checks passed, traced the failing criterion to the pipeline artifacts by timestamp, and proposed a `swap`: replace the criterion with one that scopes the diff and untracked-file checks to outside `.sdlc/`. It tested the swap in a throwaway worktree (red before the fix, green after, and correctly red again on a stray or unrelated file).
- The swap was applied to the step handoff (recorded under the task's `## Plan review`).
- A second builder attempt (L1) verified the target edit was already in place and needed no further change.
- A second verifier (L1, opus) re-ran all criteria including the swapped one, confirmed the wording addition matched the planner's Do (both rule sentences present, verbatim prefix match on the unchanged text), confirmed no other file changed outside `.sdlc/`, and confirmed the `check.sh` guard passed. Verdict: pass.

## Changelog entry
- `.claude/agents/sdlc-lite-author.md` now states the extended planner rules on `(guard)` red-first checks and membership-or-structure checks for shared files, matching `plugins/sdlc-lite/agents/planner.md` rules 11 and 12.

## Follow-ups
- The step-1 acceptance criterion pattern `git diff --stat HEAD | awk '{print $1}'` (unscoped file-change check) can never pass inside a `/chain` run because the pipeline's own uncommitted `.sdlc/<task>/` artifacts are always present in the tree; the planner should default to a `.sdlc/`-excluding scoped check (as used in this task's swap) whenever a step's acceptance criteria assert "only this file changed."
