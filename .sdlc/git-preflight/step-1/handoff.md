## Task goal
A role run in a folder that is not a git repo stops up front with a clear message instead of failing partway through. (Ticket T-0004, `.sdlc/git-preflight/handoff.md`.)

## Step 1: Git preflight in run.sh
level: L2

### Do
- In `plugins/sdlc-lite/scripts/run.sh`, after the role:level validation and handoff-exists check, and before any model call (and before the SDLC_DRY_RUN exit, so a dry run also reports it), add a preflight: if the current working directory is not inside a git work tree (`git rev-parse --is-inside-work-tree`), or the repo has no commit (`git rev-parse --verify -q HEAD`), print to stderr `not a git repo: run git init and commit first` (for the no-commit case a message that also says "commit first" is fine) and exit 2.
- Do not initialize git automatically (non-goal).
- Update the header comment of run.sh to mention the preflight, and repair any doc that describes run.sh behavior and now goes stale (repo-root `CLAUDE.md` Layout bullet for `scripts/run.sh`, `.claude/agents/sdlc-lite-author.md` if it lists run.sh behavior). Keep edits minimal. No em dashes.
- Run `plugins/sdlc-lite/scripts/check.sh` (from repo root) and fix anything you broke.

### Acceptance criteria
- In a fresh `mktemp -d` dir (not inside any git repo) with a handoff file in it, `SDLC_DRY_RUN=1 <abs path>/scripts/run.sh builder L1 handoff.md` exits non-zero and stderr contains "not a git repo".
- In a temp dir after `git init` with zero commits, the same command exits non-zero with a message containing "commit first".
- In this repo (a git work tree with commits), `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh builder L3 .sdlc/git-preflight/step-1/handoff.md` exits 0 and prints the claude command.
- An invalid role still prints usage and exits 2 (existing behavior unchanged).
- `plugins/sdlc-lite/scripts/check.sh` passes (the known validate warning about CLAUDE.md is expected).
- No commit, push, or git state change.
