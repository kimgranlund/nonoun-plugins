<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- CLAUDE.md: in the `scripts/fanout.py` bullet, the default lanes dir is now `<toplevel>/.worktrees/fanout/<lane>` (`--lanes-dir` overrides). The bullet now also covers the preflight refusal when `.worktrees/` is not git-ignored (exit 2, says to add it to `.gitignore`), the rule that an in-tree `--lanes-dir` must be ignored too, and the caveat about vitest, tsc, file watchers and `node_modules`.
- plugins/sdlc-lite/skills/fanout/SKILL.md: added a paragraph after the "Run from the project root" paragraph covering the default lanes dir, the `.gitignore` requirement, the refusal, and the same caveat. The words check.py enforces are unchanged.
- .claude/agents/sdlc-lite-author.md: added a learned-hazard line saying lanes live in the gitignored `<toplevel>/.worktrees/fanout`, not a sibling dir, plus the same caveat. The existing sync line is unchanged.

## Checks
- `! git grep -n -e '<toplevel>-fanout' -- . ':!.sdlc'`: pass
- `grep -q '\.worktrees/fanout'` on CLAUDE.md, the fanout SKILL.md and sdlc-lite-author.md: all pass
- `grep -q` for vitest and node_modules in CLAUDE.md: pass
- `grep -q` for vitest, node_modules, tsc and `\.gitignore` in the fanout SKILL.md: all pass
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0

## Notes
In the CLAUDE.md bullet, the text after the caveat now starts with "Each lane is on branch `<integration>-<lane>`" so the sentence still reads correctly after the insertion.
