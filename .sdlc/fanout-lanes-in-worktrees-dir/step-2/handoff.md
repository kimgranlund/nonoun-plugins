## Task goal
A repo's fanout lane worktrees live inside it, under a gitignored `.worktrees/fanout/<lane>`, not in a sibling `<toplevel>-fanout` dir.

## Step 2: Repair docs for the new lanes dir
level: L2
### Do
- `CLAUDE.md`, the `scripts/fanout.py` bullet (line 31):
  - Replace "under the sibling `<toplevel>-fanout` (`--lanes-dir` overrides)" with the new default `<toplevel>/.worktrees/fanout/<lane>`, where `--lanes-dir` overrides.
  - State that preflight refuses (exit 2, naming the fix of adding `.worktrees/` to `.gitignore`) when `.worktrees/` is not git-ignored. An explicit `--lanes-dir` inside the tree must be ignored too.
  - Add the caveat: `.gitignore` does not exclude `.worktrees/` from vitest, tsc, or file watchers, so a project must exclude it in their config. Node module resolution walks up from a lane worktree into the main tree's `node_modules`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`:
  - Near the "Run from the project root" paragraph, name the default lanes dir `.worktrees/fanout/<lane>`, the `.gitignore` requirement, and the refusal. Step 1 already shows a refusal from the dry run.
  - Add the same vitest/tsc/file-watcher and `node_modules` caveat.
  - Keep the words `interactive`, `run_in_background`, `notification`, `sleep`, and `SDLC_HEADLESS` intact, because check.py enforces them.
- `.claude/agents/sdlc-lite-author.md`: add a learned-hazard line saying fanout lanes live in the gitignored `<toplevel>/.worktrees/fanout`, not a sibling dir, and repeating the vitest/tsc/watcher and `node_modules` caveat. Keep the existing sync line (line 20).
- Do not edit the user-level git-bare-repo-setup skill.
### Acceptance criteria
- No tracked doc outside `.sdlc/` names the sibling default: `! git grep -n -e '<toplevel>-fanout' -- . ':!.sdlc'`
- `grep -q '\.worktrees/fanout' CLAUDE.md`
- `grep -q '\.worktrees/fanout' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q '\.worktrees/fanout' .claude/agents/sdlc-lite-author.md`
- `grep -q 'vitest' CLAUDE.md`
- `grep -q 'node_modules' CLAUDE.md`
- `grep -q 'vitest' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q 'node_modules' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q 'tsc' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q '\.gitignore' plugins/sdlc-lite/skills/fanout/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
