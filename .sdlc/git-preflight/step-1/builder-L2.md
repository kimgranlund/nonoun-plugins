<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: added a git preflight right after the handoff-exists check and before the dry-run exit. Outside a git work tree it prints `not a git repo: run git init and commit first` and exits 2. In a repo with no commit it prints `git repo has no commit: commit first` and exits 2. Also updated the header comment.
- `CLAUDE.md`: the Layout bullet for `scripts/run.sh` now mentions the git preflight.

## Checks
- Fresh `mktemp -d` dir, not a repo, `SDLC_DRY_RUN=1 run.sh builder L1 handoff.md`: stderr `not a git repo: run git init and commit first`, rc=2.
- Same dir after `git init` with no commits: stderr `git repo has no commit: commit first`, rc=2.
- This repo, `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh builder L3 .sdlc/git-preflight/step-1/handoff.md`: printed the `claude -p ...` command, rc=0.
- `run.sh bogus L1 x`: printed usage, rc=2.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0, output ended with "18 role levels, 8 agents checked", "selftest: PASS", "shellcheck" ok and "plugin validate" ok.
- `git status --short`: only the two modified files plus the untracked `.sdlc/git-preflight/`. No commit and no git state change.

## Notes
- `.claude/agents/sdlc-lite-author.md` does not describe what `run.sh` does step by step, so nothing there went stale. I left it unchanged.
- The preflight checks the current directory, not the handoff's directory. That matches the handoff, which says "current working directory".
