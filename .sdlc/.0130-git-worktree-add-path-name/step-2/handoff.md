## Task goal
Inside a role run, `hooks/block-stray-worktree.sh` denies every `git worktree add` form that can create a local branch, including the DWIM forms where git creates one implicitly (a `<name>` that exists only as a remote-tracking branch, and, per git docs, an omitted commit-ish, which auto-creates a branch named after the path basename), while the explicit detached form under `$SDLC_TMP_WORKTREES` still passes.

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
