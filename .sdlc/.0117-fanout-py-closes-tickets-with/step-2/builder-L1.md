<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: added `[--rewrite-refs]` to `argument-hint`. Step 1 now says the `close:` line shows numbered mode. Step 2 offers `--rewrite-refs` as a separate choice in numbered mode only, never added without the user's pick, and notes what a `merged, close refused` outcome naming the flag means.
- `CLAUDE.md`: `scripts/fanout.py` bullet has the flag in its usage plus one sentence describing it.
- `.claude/agents/sdlc-lite-author.md`: new line under the fanout sync line describing the flag.

## Checks
- The four grep acceptance criteria: all pass (ran chained, printed `ok`).
- `bash plugins/sdlc-lite/scripts/check.sh`: passes. I read only the last 8 lines (`tail -8`): fanout, run, hook and live-probe selftests, shellcheck, and plugin validate all show PASS/ok.

## Notes
`git diff --stat` also shows `fanout.py` and the ticket `handoff.md` as modified. Those changes came from earlier work and I did not touch them.
