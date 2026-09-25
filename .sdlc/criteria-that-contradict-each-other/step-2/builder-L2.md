<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: the steps.py Layout bullet describes the `split --only N` guard run (runs under `--guard-timeout` with a default of 300s, starts from the git toplevel, skips `HEAD^1` and `<placeholder>` spans, and refuses on a red guard or a timeout). The Systems line now counts three code gates. The plan-defect decision says a red guard is a plan defect.
- `.claude/agents/sdlc-lite-author.md`: the plan-defect route bullet names the `split --only N` red guard as a source and as part of steps.py.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: item 4.2 says `--only N` runs that step's guards and treats a red guard refusal like the section 3 split refusal. Section 3 says the full split executes no criteria.
- `plugins/sdlc-lite/scripts/check.py`: added `'red guard': ('skills/chain/SKILL.md', 'scripts/steps.py')` to `PLAN_DEFECT_DOCS`.

## Checks
- `test -z "$(grep -L 'red guard' CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/chain/SKILL.md)"`: exit 0
- `grep 'A plan defect goes to a replan' CLAUDE.md | grep -q 'red guard'`: exit 0
- `grep '^2\. builder Status blocked' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q 'red guard'`: exit 0
- `grep -q "'red guard'" plugins/sdlc-lite/scripts/check.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0
- `plugins/sdlc-lite/scripts/check.sh`: exit 0

## Notes
None
