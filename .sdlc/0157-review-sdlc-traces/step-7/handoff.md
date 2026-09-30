## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 7: Git reader
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/git.py`: `read(repo, integration=None, limit=2000)` collects read-only facts through `git -C <repo>` subprocesses and never writes: `worktrees` from `git worktree list --porcelain` (path, branch, and `nested` True when the path holds `.worktrees/` twice or lies under `.worktrees/tmp/`), `branches` from `git for-each-ref --format=%(refname:short) refs/heads`, `tracked_runtime` = `git ls-files` paths ending in `.log`, `.running`, `.run.lock`, or `.board-state.json`, `resets` = the `reset: moving to` entries of `git reflog show HEAD` run in `integration` when given (else in `repo`), and `commits` = (sha, subject) for subjects matching `Merge <lane>: <id>`, `close <id>`, or `wip(<id>): <outcome>` from `git log --format=%H%x09%s -n <limit>`; a repo that is not a git work tree gives empty lists and a `problems` entry. Register the `git` cases on a throwaway repo (built in a temp dir; the nested `.worktrees/x/.worktrees/tmp/builder-1` worktree is made with `git worktree add --detach` from Python and removed in `finally`; the hook sees only the Bash tool text, and the throwaway repo is invisible to this repo's worktree list): a tracked `foo.log`, a `reset: moving to` reflog entry, and a `wip(T-0001): driver failed rc=3` commit each yield their fact, and after the read `git status --porcelain` output and the reflog line count equal their values before it.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git | grep -q '^ok: git: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/git.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
