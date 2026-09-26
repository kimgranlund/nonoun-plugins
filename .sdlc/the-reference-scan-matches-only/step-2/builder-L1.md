<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: the `close` and `archive` help paragraphs now describe the widened scan and its limits.
- `CLAUDE.md`: the `scripts/tickets.py` Layout entry describes the widened scan and its limits.
- `.claude/agents/sdlc-lite-author.md`: the numbered close/archive scan mention notes the widened scan.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the scan description matches the new rule (the skill does describe the scan).

## Checks
- `grep -qF "relative to the citing file"` passes on CLAUDE.md, tickets.py and sdlc-lite-author.md. I ran it as a count (`grep -c`) and it was at least 1 in all three, and it is also in SKILL.md.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS. I re-ran it after the final wording edit and it still passes.
- `plugins/sdlc-lite/scripts/check.sh`: all sections passed, including the hook selftests, shellcheck and plugin validate. I only read the last few lines of output, so I did not see the earlier sections.
- The em dash count on added lines in the diff is 0.

## Notes
None
