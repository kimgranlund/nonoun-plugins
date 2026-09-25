<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/chain/SKILL.md`: the intro paragraph now covers both cases. Headless runs stay in the foreground with `timeout` 600000 or more. Interactive runs use `run_in_background: true`, wait for the completion notification, never poll with `sleep`, and read `<role>-<level>.md` once notified.
- `plugins/sdlc-lite/skills/bench/SKILL.md`: same two-case text on line 11.
- `plugins/sdlc-lite/agents/conductor.md`: the first bullet under "How you run roles" now states both cases.
- `.claude/agents/sdlc-lite-author.md`: the hazard line (line 26) now matches: 15 to 30 minutes, `run_in_background: true`, read `<role>-<level>.md` once notified, and ending the turn is safe interactively.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: the first run failed with "long-run rule missing words: interactive" on all three docs, because the check is case-sensitive and my text used "Interactive:". After changing it to "In an interactive session:" it exits 0 ("ok: 18 role levels, 8 agents checked").
- `plugins/sdlc-lite/scripts/check.sh`: exits 0, with no FAIL lines in the output.
- `grep -c run_in_background` on the three docs: 1 in each.
- `grep -c "—"` on the four edited files: 0 in each.

## Notes
- I did not add a line to `CLAUDE.md`. The handoff says `plugins/sdlc-lite/CLAUDE.md`, but that path does not exist; the file is at the repo root. Its "Headless runs" bullet is about `--dangerously-skip-permissions`, not about how long runs are launched, so the new text does not fit there.
- The headless text says "do not use `run_in_background` there" instead of "never `run_in_background`", to satisfy check.py's rule against an unqualified `never run_in_background`.
