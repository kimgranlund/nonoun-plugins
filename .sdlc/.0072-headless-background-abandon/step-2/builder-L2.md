<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/bench.sh: `SDLC_HEADLESS=1` is added to the `claude -p` env prefix, and the header comment now mentions it.
- plugins/sdlc-lite/scripts/fanout.py: the driver env gets `SDLC_HEADLESS='1'`, the docstring's driver env list names it, and the selftest `STUB` exits 1 when it is missing.
- plugins/sdlc-lite/scripts/check.py: `SDLC_HEADLESS` is added to the words the long-run doc check requires.
- plugins/sdlc-lite/skills/chain/SKILL.md: the headless sentence now covers the hook and the `SDLC_HEADLESS=1` convention.
- plugins/sdlc-lite/skills/bench/SKILL.md: same sentence added.
- plugins/sdlc-lite/skills/fanout/SKILL.md: same sentence added.
- plugins/sdlc-lite/agents/conductor.md: same sentence added.
- CLAUDE.md: Layout gets a `hooks/block-background.sh` entry, and the check.sh list in Commands now names `hook-selftest.sh`.
- .claude/agents/sdlc-lite-author.md: the headless-foreground hazard now says the hook enforces it, and its list of required check.py words includes `SDLC_HEADLESS`.
- plugins/sdlc-lite/.claude-plugin/plugin.json: version bumped to 0.8.2.

## Checks
- `grep -q 'SDLC_HEADLESS=1' .../bench.sh`: exit 0
- STUB contains `SDLC_HEADLESS` (python one-liner): exit 0
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: prints `fanout selftest: PASS`
- grep -l over the four docs: count is 4, exit 0
- `grep -q SDLC_HEADLESS .../check.py`: exit 0
- CLAUDE.md has `block-background` and `SDLC_HEADLESS`, and sdlc-lite-author.md has `SDLC_HEADLESS`: exit 0
- plugin.json has version 0.8.2: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, including the fanout, run, and hook selftests, shellcheck, and plugin validate

## Notes
None
