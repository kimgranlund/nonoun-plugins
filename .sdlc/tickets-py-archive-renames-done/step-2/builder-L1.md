<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None by me. The three docs already held the new archive flags in the tree at HEAD (`git status` was clean), so I edited nothing:
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `argument-hint` and the numbered-folders bullet.
- `CLAUDE.md`: the `tickets.py` Layout entry.
- `.claude/agents/sdlc-lite-author.md`: line 17.

## Checks
- `grep -qE '^argument-hint:.*archive \[--dry-run\] \[--rewrite-refs\] \[--force\]' plugins/sdlc-lite/skills/ticket/SKILL.md`: pass.
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' CLAUDE.md`: pass. Count is 1.
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' .claude/agents/sdlc-lite-author.md`: pass.
- `test "$(grep -cF ... SKILL.md)" -ge 2`: pass. Count is 2.
- `plugins/sdlc-lite/scripts/check.sh`: green. The tail showed the run, hook, hook live probe, shellcheck and plugin validate checks all passing; I did not read the full output above the last five lines.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.

## Notes
The docs looked already done, so I ran the criteria and guards without changing anything. `git status` was clean before and after.
