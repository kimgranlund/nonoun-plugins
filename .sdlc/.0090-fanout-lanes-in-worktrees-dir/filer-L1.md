<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0090: fanout default lanes dir becomes <toplevel>/.worktrees/fanout/<lane>

## PR body
### Summary
Fanout lane worktrees now live inside the repo, under a gitignored `<toplevel>/.worktrees/fanout/<lane>`, instead of in a sibling `<toplevel>-fanout` dir. `--lanes-dir` still overrides the default. When the lanes dir would sit inside the tree but is not git-ignored, preflight refuses with exit 2 and names the fix.

### Changes
**Step 1: `plugins/sdlc-lite/scripts/fanout.py`**
- The default lanes dir is now `top/.worktrees/fanout`. The integration worktree goes at `<lanes-dir>/integration` and each lane at `<lanes-dir>/<lane>`.
- Preflight rules. They run before any write, so `--dry-run` refuses too:
  - `--lanes-dir` equal to the toplevel is refused.
  - With the default dir, preflight runs `git check-ignore -q .worktrees/x`. If that path is not ignored, it refuses with exit 2 and says to add `.worktrees/` to `.gitignore`.
  - An explicit `--lanes-dir` inside the tree gets the same check on `<rel>/x`, and the refusal names `<rel>/`.
  - An explicit `--lanes-dir` outside the tree is not checked, as before.
  - If `git check-ignore` returns something other than 0 or 1, preflight refuses with its own message.
- The module docstring and the `--lanes-dir` help describe the new default and the ignore rule.
- Selftest:
  - `make_repo` can now take extra files.
  - The `rr` fixture commits a `.gitignore` containing `.worktrees/`.
  - The default-dir expectations now point to `rr/.worktrees/fanout`.
  - New case 3: a repo with no `.gitignore` must exit 2 with `.gitignore` and `.worktrees/` on stderr and no Traceback. It must also create no `.worktrees` dir, no `fanout/*` branch and no extra worktree.
- Lane branch naming, sync, merge, gates and close behavior are unchanged.

**Step 2: docs**
- `CLAUDE.md`: the fanout bullet now covers the new default, the refusal, and the rule that an in-tree `--lanes-dir` must be ignored too. It also adds a caveat: `.gitignore` does not exclude `.worktrees/` from vitest, tsc or file watchers, and Node module resolution walks up from a lane worktree into the main tree's `node_modules`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: new paragraph on the default dir, the `.gitignore` requirement, the refusal, and the same caveat. The words check.py enforces are unchanged.
- `.claude/agents/sdlc-lite-author.md`: new learned-hazard line about the new lanes dir and the same caveat.

### Verification
**Step 1** (builder L3, verifier L2): pass.
- `fanout.py selftest` passes.
- The verifier broke the refusal branch in a temp copy, and the selftest then failed on the new stderr check.
- Each acceptance command was run exactly as written:
  - default-dir dry run lists paths under `<repo>/.worktrees/fanout`
  - an unignored repo gets exit 2 with the fix named, and no `.worktrees` is created
  - an explicit outside `--lanes-dir` still works and creates nothing
  - no sibling-dir strings remain in fanout.py
- Each non-guard command was confirmed to fail at HEAD, so it can catch a regression.
- Checked by hand: `--lanes-dir lanes/here` and `--lanes-dir .` are both refused.

**Step 2** (builder L2, verifier L1): pass.
- `git grep` finds `<toplevel>-fanout` in no tracked doc outside `.sdlc/`.
- Greps confirm `.worktrees/fanout`, `vitest`, `tsc`, `node_modules` and `.gitignore` in the files each criterion names.
- `scripts/check.sh` exits 0.

### Notes
- `<toplevel>` is the toplevel of the worktree fanout runs from. Run from a linked worktree, fanout puts the lanes under that worktree's own `.worktrees/fanout`.
- The user-level git-bare-repo-setup skill is outside this repo and was not edited or checked. It may still describe the sibling-dir convention.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Changed: `fanout.py` now puts lane worktrees in `<toplevel>/.worktrees/fanout/<lane>` instead of a sibling `<toplevel>-fanout` dir. Preflight refuses with exit 2 when `.worktrees/` (or an in-tree `--lanes-dir`) is not git-ignored. Add `.worktrees/` to `.gitignore`, and exclude it in vitest, tsc and file-watcher config.

## Follow-ups
- fanout selftest covers the default `.worktrees/fanout` lanes dir only with `--dry-run`; add a full stub-driver run there that checks lane commits, merge and close keep `git status` clean in the main tree.
