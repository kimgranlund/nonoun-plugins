<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
No role run leaves a git worktree behind, on success or on failure. To get there, `run.sh` gives each role a private throwaway-worktree prefix, removes that prefix on every exit, and the role prompts send roles there.

## Step 1: run.sh owns and cleans a per-run throwaway worktree prefix, with a selftest
level: L3
### Do
In `plugins/sdlc-lite/scripts/run.sh`:
- After the dry-run exit, and only on a real run so that `SDLC_DRY_RUN=1` creates nothing, set `wt_tmp="$(git rev-parse --show-toplevel)/.worktrees/tmp/$role-$$"`. Export it to the role as `SDLC_TMP_WORKTREES`, the same way `SDLC_ROLE` is passed on the `claude` invocation.
- Do not create the directory. Roles create it with `git worktree add "$SDLC_TMP_WORKTREES/<name>" HEAD`, which makes parents.
- Add a cleanup function to the existing EXIT trap, keeping the `.running` and skill-file removal. The function must:
  1. Run `git worktree remove --force` on every entry in `git worktree list --porcelain` whose path is under `$wt_tmp`. Compare the realpath of the path, because macOS reports `/private/var/...` for a `/var/...` mktemp dir.
  2. Run `rm -rf "$wt_tmp"`.
  3. Run `git worktree prune`.
  4. Run `rmdir` on `.worktrees/tmp` and then `.worktrees` only when they are empty, ignoring errors.
  5. Never change the exit code.
- Also trap INT, TERM and HUP so that cleanup runs when the run is killed, then exit non-zero.
- Scope cleanup to this run's prefix only, never to "worktrees that appeared during the run". Concurrent fanout lanes run other role runs at the same time.
- Document all of this in the header comment, including the new env var and the cleanup-on-failure rule.

In `plugins/sdlc-lite/scripts/run-selftest.sh`, add cases using a stub `claude` that runs `git worktree add --detach "$SDLC_TMP_WORKTREES/w" HEAD`:
- (a) A successful role run.
- (b) A failing role run: the stub exits 1.
- (c) A run whose result lacks its section: exit 3.
- For each case, assert all of these:
  - `git worktree list` has only the main tree afterwards.
  - `.worktrees/tmp` does not exist.
  - The stub saw a non-empty `SDLC_TMP_WORKTREES` under `<toplevel>/.worktrees/tmp/`.
- Assert that a dry run creates no `.worktrees`.
- Update the header comment to list the new cases.

### Acceptance criteria
- A failing role run leaves no worktree behind. Run from the repo root: `p=$PWD/plugins/sdlc-lite/scripts/run.sh; t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && printf '#!/bin/sh\ngit worktree add -q --detach "${SDLC_TMP_WORKTREES:-$PWD/.worktrees/tmp/x}/w" HEAD\nexit 1\n' >"$t/bin/claude" && chmod +x "$t/bin/claude" && cd "$t/r" && git init -q && echo x >h.md && git add h.md && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && ! PATH="$t/bin:$PATH" bash "$p" builder L1 h.md && test "$(git worktree list | wc -l)" -eq 1 && test ! -e .worktrees/tmp`
- A successful role run leaves no worktree behind. Run from the repo root: `p=$PWD/plugins/sdlc-lite/scripts/run.sh; t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && jq -n '{is_error:false,result:"## Status\ndone"}' >"$t/ok.json" && printf '#!/bin/sh\ngit worktree add -q --detach "${SDLC_TMP_WORKTREES:-$PWD/.worktrees/tmp/x}/w" HEAD\ncat "%s"\n' "$t/ok.json" >"$t/bin/claude" && chmod +x "$t/bin/claude" && cd "$t/r" && git init -q && echo x >h.md && git add h.md && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && PATH="$t/bin:$PATH" bash "$p" builder L1 h.md && test "$(git worktree list | wc -l)" -eq 1 && test ! -e .worktrees/tmp`
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run.sh`
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `p=$PWD/plugins/sdlc-lite/scripts/run.sh; t=$(mktemp -d) && mkdir -p "$t/r" && cd "$t/r" && git init -q && echo x >h.md && git add h.md && git -c user.name=a -c user.email=a@b.invalid -c commit.gpgsign=false commit -qm i && SDLC_DRY_RUN=1 bash "$p" builder L1 h.md >/dev/null && test ! -e .worktrees`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
- The new selftest bites. Copy the new `run-selftest.sh` into a throwaway worktree of HEAD and run it there against HEAD's `run.sh`. It prints `run selftest: FAIL`, naming a leftover worktree or a missing `SDLC_TMP_WORKTREES`. Remove the worktree afterwards.

## Step 2: Point role prompts and docs at the prefix
level: L2
### Do
- In `plugins/sdlc-lite/agents/verifier.md` rule 3, replace `git worktree add <tmp dir> HEAD` with a worktree created only under `$SDLC_TMP_WORKTREES`, for example `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`. State that run.sh removes everything under that prefix when the run exits, and that the verifier still removes its own worktree when done. The later paragraph's "throwaway worktree at HEAD" should refer to the same place.
- In `plugins/sdlc-lite/agents/builder.md`, add one rule: any throwaway worktree goes only under `$SDLC_TMP_WORKTREES`, never `/tmp` or a sibling dir.
- `skills/checks-that-bite` names no location, so leave it alone.
- Leave the `merge-step` template's `<tmp>` placeholder unchanged. check.py keeps its two copies identical, and the verifier prompt now resolves `<tmp>`.
- Repair the stale records:
  - Add one sentence to the `scripts/run.sh` Layout bullet in the repo-root `CLAUDE.md`: run.sh exports `SDLC_TMP_WORKTREES=<toplevel>/.worktrees/tmp/<role>-<pid>` and removes every worktree under it on any exit, then runs `git worktree prune`.
  - Add the matching line to `.claude/agents/sdlc-lite-author.md`, next to the "throwaway worktrees" invariant on line 36.
### Acceptance criteria
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/verifier.md`
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/builder.md`
- `! grep -q 'git worktree add <tmp dir> HEAD' plugins/sdlc-lite/agents/verifier.md`
- `grep -q SDLC_TMP_WORKTREES CLAUDE.md`
- `grep -q SDLC_TMP_WORKTREES .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- **Unignored `.worktrees/`:** in a target repo where `.worktrees/` is not git-ignored, a live temp worktree shows up as untracked `.worktrees/` in `git status` during the run. The verifier could flag it as out of scope. Cleanup removes it at exit, so no trace is left.
- **SIGKILL:** a `kill -9` of run.sh skips every trap. The dir stays until a later `git worktree prune` after manual removal.
- **Stray paths and branches:** a role that ignores the prompt and adds a worktree elsewhere, such as `/tmp`, is not cleaned. Scoping to the prefix is deliberate, because of concurrent fanout lanes. A worktree created with `-b` also leaves its branch behind.
- **Path comparison:** it must use realpaths. The macOS `/var` vs `/private/var` mismatch showed up while probing.
- **Timing:** the step 2 guard, `check.sh`, takes about 90 seconds, under the 300-second guard timeout.
