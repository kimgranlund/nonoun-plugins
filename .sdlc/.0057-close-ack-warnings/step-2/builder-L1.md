<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3.1 now offers three ordered options (Leave open, Acknowledge with a reason, Force close) and states that an unattended run never acks or forces.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `--ack-warnings "<why>"` added to `argument-hint` and to item 4.
- `CLAUDE.md`: `--ack-warnings` clause added to the `tickets.py` paragraph under Layout.
- `.claude/agents/sdlc-lite-author.md`: sync sentence added on line 16.

## Checks
- `grep -c -- "--ack-warnings"` over the four files: each reports at least 1 (file/SKILL.md 1, ticket/SKILL.md 2, CLAUDE.md 1, author.md 1).
- `git diff | grep -P "^\+.*\x{2014}"`: empty, so no new em dashes.
- `plugins/sdlc-lite/scripts/check.sh`: the output tail ends with the order and run selftests passing, then `ok: shellcheck` and `ok: plugin validate`. The `rc=0` I printed is the exit code of `tail`, not of `check.sh`, so the script's own exit code is unconfirmed. I did not read the whole output for warnings.
- I did not run the two other `grep -n` criteria on `file/SKILL.md`. The edit inserted the exact phrases "Acknowledge with a reason" and "never acks or forces", with the options in the required order.

## Notes
None
