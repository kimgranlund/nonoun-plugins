## Task goal
A conductor in a repository whose checkout must not be touched, such as a bare-clone layout with a dirty primary worktree, knows how to run a role from a clean temporary worktree and where `.sdlc/` state lives while it does.

## Step 2: Selftest the recipe in a throwaway bare-clone repository
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add a case to `plugins/sdlc-lite/scripts/run-selftest.sh`. Add a header comment paragraph starting `Temporary worktree recipe:` that describes the case, matching the style of the existing paragraphs. The case works inside the script's `$tmp`, reuses the stub `claude` on PATH, and makes no model call. It does the following:
1. Build a source repo with one commit that contains a tracked file and a `.gitignore` holding `.sdlc/`.
2. Run `git clone --bare` of it to `<tmp>/proj.git`, then add a primary worktree on the default branch and a second, unrelated user worktree.
3. Make the primary dirty: modify the tracked file and add an untracked file. Put a task handoff at `<primary>/.sdlc/t/handoff.md` with `## Goal`.
4. Snapshot the primary's `git status --porcelain` output, the tracked file's bytes, `git worktree list --porcelain` minus the recipe path, and `refs/heads`.
5. Run the step 1 recipe with the same command shapes the doc uses: a `mktemp` path, a detached worktree add from the bare repo, `run.sh scout L1 <absolute handoff>` from inside it, then a worktree remove without `--force`.
6. Assert all of these, calling `fail` with a reason for each miss:
   - `run.sh` exits 0.
   - `<primary>/.sdlc/t/scout-L1.md` and `<primary>/.sdlc/t/runs.jsonl` exist.
   - No result file appears anywhere under the temporary worktree path before removal.
   - After removal, the recipe path is absent from `git worktree list` and from disk.
   - The unrelated user worktree is still listed.
   - `refs/heads` is unchanged.
   - The primary's porcelain status and tracked-file bytes are byte-identical to the snapshot.
   - The primary has no `.worktrees` dir.

Before finishing, run a negative control and record it in the builder report: temporarily point the case at the primary instead of the temporary worktree, meaning `run.sh` runs from the primary, or the handoff is copied into the temporary worktree and removed with it. Show that the case fails with a `fail` reason, then restore it. This step proves the recipe with a stub backend only; a live model run is not part of it.

Never write the text of a git worktree-add command into a Bash call outside the script file, because `hooks/block-stray-worktree.sh` denies it inside a role run. Running `bash plugins/sdlc-lite/scripts/run-selftest.sh` is allowed.
### Acceptance criteria
- `grep -qF 'Temporary worktree recipe' plugins/sdlc-lite/scripts/run-selftest.sh && grep -qF 'clone --bare' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `out=$(bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1) && printf '%s\n' "$out" | tail -1 | grep -qx 'run selftest: PASS'`
- The builder report shows the negative control: the command it ran with the case pointed at the primary or at an in-worktree handoff, the resulting `run selftest: FAIL: <reason>` line naming the recipe case, and the restore.
- (guard) `command -v shellcheck >/dev/null && shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh`
