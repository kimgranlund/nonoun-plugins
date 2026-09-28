<!-- role=verifier level=L1 model=sonnet effort=medium -->
Only the two files changed plus the untracked `.sdlc/0004-git-preflight/` step artifacts (expected, in scope). No git state change (no commits, no stash). The sdlc-lite-author.md doesn't mention run.sh's git behavior specifically, consistent with builder's note that nothing there went stale.

All criteria pass with direct observation, including a red-then-green control against the pre-change worktree.

## Verdict
pass

## Criteria
- Fresh mktemp dir (not a repo), `SDLC_DRY_RUN=1 run.sh builder L1 handoff.md` exits non-zero with stderr containing "not a git repo": pass. Evidence: ran in `/var/folders/.../tmp.8Mdy5JEzlT`, stderr `not a git repo: run git init and commit first`, RC=2.
- Temp dir after `git init` with zero commits, same command exits non-zero with message containing "commit first": pass. Evidence: ran in `/var/folders/.../tmp.PfEvL4GJsx`, stderr `git repo has no commit: commit first`, RC=2.
- In this repo, `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh builder L3 .sdlc/0004-git-preflight/step-1/handoff.md` exits 0 and prints the claude command: pass. Evidence: command printed `claude -p --plugin-dir ... --agent sdlc-lite:builder --model opus --effort high ...`, RC=0.
- Invalid role still prints usage and exits 2: pass. Evidence: `plugins/sdlc-lite/scripts/run.sh bogus L1 x` printed `usage: run.sh <role> <level> <handoff.md> ...`, RC=2.
- `plugins/sdlc-lite/scripts/check.sh` passes: pass. Evidence: output ended `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, RC=0.
- No commit, push, or git state change: pass. Evidence: `git status --short` shows only `M CLAUDE.md`, `M plugins/sdlc-lite/scripts/run.sh`, `?? .sdlc/0004-git-preflight/` (expected step artifacts); no commits created, no stash used.
- Preflight check actually bites (red-then-green control, not in the stated criteria but required by verifier doctrine): pass. Evidence: `git worktree add /tmp/verify-preflight-check HEAD` (pre-change code) then run the same non-repo scenario against it — RC=0, no error (red). Post-change run.sh in the working tree gives RC=2 with "not a git repo" (green). Worktree removed after.

## Out of scope changes
None. Only `CLAUDE.md` (Layout bullet for run.sh) and `plugins/sdlc-lite/scripts/run.sh` were modified, both called for by the step. `.sdlc/0004-git-preflight/step-1/` is the step's own artifact directory.

## For the next attempt
None.
