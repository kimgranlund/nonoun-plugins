## Task goal
Builders never touch files or processes outside their own work.

## Step 2: Builder scope rules, check.py guard, and docs
level: L2
### Do
Add two numbered rules to `plugins/sdlc-lite/agents/builder.md` after rule 5:
- Run formatters, `--fix` linters, and code generators only on the files this step changed, and pass those paths explicitly (for example `prettier --write <paths>`). Never run a repo-wide `--write` or `--fix`. If the tool writes a file the step did not ask for, restore it.
- Stop only the PIDs you started (save `$!` when you launch a server, then `kill <pid>`). Never run `pkill`, `killall`, or `kill $(pgrep ...)`, because they hit other sessions' processes. `hooks/block-pattern-kill.sh` blocks these in role runs.

The rules must contain the exact phrases `files this step changed` and `PIDs you started`.

In `plugins/sdlc-lite/scripts/check.py`, add a guard that fails when `agents/builder.md` lacks either phrase. Add a negative control, the way the step 3.3 guard does: the guard function run on the text with the phrase removed must flag it, or check.py reports `check.py: builder scope guard negative control not flagged`.

Document the hook:
- Repo-root `CLAUDE.md` Layout gets a `hooks/block-pattern-kill.sh` bullet next to the other hooks, and the `check.sh` command line mentions it.
- `.claude/agents/sdlc-lite-author.md` gets the same.

Do not commit.
### Acceptance criteria
Run these from the repo root:
- `grep -q 'files this step changed' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'PIDs you started' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'files this step changed' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'PIDs you started' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'builder scope guard negative control' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'block-pattern-kill.sh' CLAUDE.md`
- `grep -q 'block-pattern-kill.sh' .claude/agents/sdlc-lite-author.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py "$PWD/plugins/sdlc-lite"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- The verifier observes that the guard bites. In a throwaway worktree under `$SDLC_TMP_WORKTREES` holding the built tree, it deletes the `PIDs you started` phrase from `agents/builder.md` and runs that copy's check.py, which must exit 1 and name `agents/builder.md`.
