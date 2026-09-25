<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0083: Refuse split --only when a guard changed the work tree

## PR body
### Summary
`steps.py split --only N` runs each `(guard)` criterion of the step before the build starts. Until now, a guard with side effects could change the tree before the build, and only the planner prompt forbade that. This PR adds a code check. Split now refuses with a `plan defect:` last line that names the changed paths, and it writes no step handoff.

### Changes
1. `plugins/sdlc-lite/scripts/steps.py`
   - Added `git_toplevel`, `tree_state` and `tree_changes`.
   - `run_guards` snapshots the work tree before and after the guards, tracked and untracked. The snapshot uses `git --no-optional-locks status` plus each path's lstat size and mtime_ns.
   - On a difference, it prints one line per changed path. It then prints a single `plan defect:` last line, which also names any red guards.
   - Outside git there is no check. A tree that was already dirty before the guards is fine unless the guards change it further. This includes a guard appending to a file that was already modified, and one selftest case proves that.
   - The usage text now documents the refusal.
   - Added 7 `(o)` selftest cases. The `(n)` cases are unchanged.
2. Docs describe the refusal with the phrase `changed the work tree`:
   - CLAUDE.md (Layout, Systems, Decisions)
   - `.claude/agents/sdlc-lite-author.md`
   - `skills/chain/SKILL.md` (sections 3 and 4.2)
   - `agents/planner.md`: rule 1 now says a guard must be side-effect free. The merge-step block is untouched.
3. `scripts/check.py`: a new `PLAN_DEFECT_DOCS` entry makes the check fail if the phrase drops out of planner.md, chain/SKILL.md or steps.py.

### Verification
- **Step 1** (builder L3, verifier L2: pass)
  - All 9 criteria pass: an untracked-file guard refuses, a tracked-file guard refuses, a no-op guard passes, a pre-dirty tree passes, there are 7 `(o)` and 7 `(n)` ok lines, and there are no `(n)` body edits.
  - The verifier checked that the test fails without the fix. On a pre-fix worktree the untracked-file case wrote the handoff. After the fix it refuses.
  - The verifier also checked the combined red-guard plus changed-tree case by hand. It gave one `plan defect:` line naming both.
  - In a separate negative control, the builder stubbed out `tree_changes`, and 4 `(o)` cases failed.
- **Step 2** (builder L2, verifier L1: pass)
  - All grep criteria pass, `check.sh` exits 0, the steps selftest passes, and `skills/handoff-format` is untouched.
  - The verifier checked that the new check.py entry fails against the pre-step docs (exit 1). With the updated docs it passes.

Nothing was committed or pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py split --only N` now refuses, with a `plan defect:` line naming the paths, when a step's `(guard)` criteria change the git work tree (tracked or untracked). check.py keeps the docs describing this rule in step. (T-0083)

## Follow-ups
- steps.py split --only guard check cannot see changes guards make to gitignored files (logs, caches), so a side-effecting guard that writes only ignored paths still passes silently.
