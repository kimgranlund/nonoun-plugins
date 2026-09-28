<!-- role=filer level=L1 model=sonnet effort=medium -->
All three steps passed verification with no warnings. Now composing the final filer output.

## Warnings
None

## PR title
T-0130: Deny git worktree add without --detach in block-stray-worktree hook

## PR body
Summary: closes a DWIM gap in `hooks/block-stray-worktree.sh`. Inside a role run, `git worktree add` could implicitly create or check out a local branch (a remote-only `<name>` becomes a new tracking branch, an omitted commit-ish creates one named after the path basename), and the hook let those forms through because it only checked `not detach and len(pos) < 2`. The hook now denies any `git worktree add` that lacks `--detach`/`-d`, a purely textual rule that holds regardless of repo state since `--detach` skips all branch DWIM in git.

Changes:
- `plugins/sdlc-lite/hooks/block-stray-worktree.sh`: `check_add` now denies every add without `--detach`/`-d`, with an updated deny reason and header comment. Verified by builder and verifier in step 1: the three new-behavior criteria (remote-only name, `--no-detach ... HEAD`, `... -- feature-x`) went red (exit 0) on the pre-build tree and exit 2 on the built tree; the allowed forms (`--detach`, `-d`) still pass; `hook-selftest.sh` green.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: five new denied fixtures, three new allowed fixtures, and the bare `${SDLC_TMP_WORKTREES}/base` fixture moved from allowed to denied.
- Docs and prompts updated so no role is told to use a form the hook now denies: `plugins/sdlc-lite/agents/planner.md` (rules 3, 8, 11 and the merge-step block), `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (merge-step block, kept identical to planner.md's copy), `plugins/sdlc-lite/agents/builder.md` and `plugins/sdlc-lite/agents/verifier.md` (worktree rules now name "without `--detach`"), repo-root `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` (hook layout/hazard bullets), and `plugins/sdlc-lite/scripts/run.sh` (header comment example). Verified in step 2: each targeted grep passed on the built tree and failed at the pre-build HEAD; the two merge-step copies stayed identical (`cmp`); `check.py` passed; no em dashes introduced.
- `plugins/sdlc-lite/scripts/check.sh`: run clean, all green (merge-step copies, conflict-marker probe, hook selftest, shellcheck, plugin validate). Verified in step 3: the verifier confirmed the check would go red on the pre-change hook with the new fixtures applied, and green on the built tree.

No files were staged or committed; the plan's final step made no changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Hooks: `block-stray-worktree.sh` now denies any `git worktree add` inside a role run that lacks `--detach`/`-d`, closing gaps where git could implicitly create a branch from a remote-only name or an omitted commit-ish.

## Follow-ups
None
