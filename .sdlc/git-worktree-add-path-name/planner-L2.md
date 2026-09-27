<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Inside a role run, `hooks/block-stray-worktree.sh` denies every `git worktree add` that lacks `--detach`/`-d`. That closes the DWIM gaps: a remote-only `<name>` that git turns into a new tracking branch, a local branch checked out by name, and an omitted commit-ish. The detached form under `$SDLC_TMP_WORKTREES` keeps passing, and every prompt and doc shows only that form.

## Step 1: Require --detach on every worktree add in the hook
level: L2
### Do
Pick a purely textual rule: every `git worktree add` inside a role run must carry `--detach` or `-d`. The reason: with `--detach`, git's `worktree add` skips all branch DWIM (no remote-tracking guess, no basename branch, no checkout of an existing branch). That property holds no matter which refs exist, so the hook never has to query the repo, which it cannot do reliably before git runs. The rule "allow only a commit-ish git cannot DWIM" was rejected because whether `<name>` is a remote-only branch depends on repo state.

In `plugins/sdlc-lite/hooks/block-stray-worktree.sh`, inside the Python `check_add`:
- Replace the final check `if not detach and len(pos) < 2` with `if not detach`.
- Give it a reason that says git can create or check out a branch without `--detach`, for example: "without --detach git can create a branch (a name that exists only on a remote becomes a new tracking branch, no commit makes one named after the path) or check out an existing branch".
- Keep the existing option parsing. `--no-detach` must not count as detach, and today it already does not. `-d` inside a combined short flag such as `-fd` still counts.
- Keep the prefix check, the `-b`/`-B`/`--orphan` checks, the unset-prefix check, the fail-closed raw scan, and the `SDLC_ROLE` unset exit unchanged.
- Update the header comment so it describes the new rule and the reason.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, in the block-stray-worktree section:
- Add to the denied loop: `git worktree add "$tw/x" feature-x` (remote-only-name DWIM), `git worktree add "$tw/x" HEAD`, `git worktree add --no-detach "$tw/x" HEAD`, `git worktree add "$tw/x" -- feature-x`, and `git worktree add "${SDLC_TMP_WORKTREES}/base" HEAD`.
- Move that last fixture from the allowed loop to the denied loop.
- Add to the allowed loop: `git worktree add -d "$tw/x" HEAD`, `git worktree add --detach "$tw/x" origin/feature-x`, and `git worktree add --detach "${SDLC_TMP_WORKTREES}/base" HEAD`.
- Keep the no-role fixture.

Do not touch other files in this step.
### Acceptance criteria
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add --no-detach \"$SDLC_TMP_WORKTREES/x\" HEAD"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" -- feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>&1 >/dev/null | grep -q -- '--detach'`
- `grep -q 'feature-x' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF -- '--no-detach' plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add --detach \"$SDLC_TMP_WORKTREES/x\" origin/feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add -d \"$SDLC_TMP_WORKTREES/x\" HEAD"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `plugins/sdlc-lite/scripts/hook-selftest.sh`

## Step 2: Show only the detached form in prompts and docs
level: L1
### Do
Update every prompt and doc that shows or describes a worktree add, so no role is told to use a form the hook now denies:
- `plugins/sdlc-lite/agents/planner.md`: in rules 3, 8, and 11, change `git worktree add <tmp> HEAD` to `git worktree add --detach <tmp> HEAD`. In the fenced `merge-step` block, change `git worktree add <tmp> HEAD^1` to `git worktree add --detach <tmp> HEAD^1`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: make the same change in its `merge-step` block, so it stays byte-identical to the planner.md copy. `check.py` compares the two copies.
- `plugins/sdlc-lite/agents/builder.md` (rule 5) and `plugins/sdlc-lite/agents/verifier.md` (rule 3): change "A hook denies `-b`, `-B`, `--orphan`, and any path outside the prefix" so it also names any add without `--detach` (wording containing "without `--detach`").
- Repo-root `CLAUDE.md`, `hooks/block-stray-worktree.sh` layout bullet: say it also denies any worktree add without `--detach`/`-d`, because git can otherwise create a branch (a remote-only name becomes a tracking branch) or check one out. Use wording containing "without `--detach`".
- `.claude/agents/sdlc-lite-author.md`, the learned-hazard line about `block-stray-worktree.sh`: same addition, with wording containing "without `--detach`".
- `plugins/sdlc-lite/scripts/run.sh`: in the header comment, change `git worktree add "$SDLC_TMP_WORKTREES/<name>"` to `git worktree add --detach "$SDLC_TMP_WORKTREES/<name>"`.

No em dashes.
### Acceptance criteria
- `! grep -qF 'worktree add <tmp>' plugins/sdlc-lite/agents/planner.md`
- `! grep -qF 'worktree add <tmp>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'git worktree add --detach <tmp> HEAD^1' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'git worktree add --detach <tmp> HEAD^1' plugins/sdlc-lite/agents/planner.md`
- `for f in CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md; do grep -q 'without .--detach' "$f" || exit 1; done`
- `grep -qF 'git worktree add --detach "$SDLC_TMP_WORKTREES/<name>"' plugins/sdlc-lite/scripts/run.sh`

## Step 3: Gates green
level: L1
### Do
Run the repo check script `plugins/sdlc-lite/scripts/check.sh`. It covers:
- the merge-step copies being identical and lint-clean
- the conflict-marker probe
- the hook selftest
- shellcheck
- plugin validate

Fix any red that steps 1 and 2 introduced. The expected validate warning about CLAUDE.md is fine. Never commit.
### Acceptance criteria
- (guard) `plugins/sdlc-lite/scripts/check.sh`

## Risks
- Requiring `--detach` also denies `git worktree add <prefix>/x <local-branch>`, which checks out an existing branch without creating one. This is intended, because the rule stays textual and the ticket allows "require `--detach`". A role that relied on it must switch to the detached form.
- The step 1 guards were each green at plan time. Their red form was not run one by one, but it is covered by the existing selftest's denied fixtures (the same invocation with a `/tmp/x` path exits 2).
- Criteria that pipe hook JSON hold the phrase `git worktree add` inside a single-quoted string. The live hook in a verifier run parses that as one quoted word and passes it, which was observed at plan time. Wrapping any of these commands in `bash -c` would trip the hook's fail-closed scan.
- `git worktree add` parses options by git's abbreviation rules. The hook keeps its existing prefix matching for `--detach`, so an abbreviation such as `--det` still counts as detached, as it does in git.
