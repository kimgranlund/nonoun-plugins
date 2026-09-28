<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3.1 keeps the `expect <digest>` line. Step 3.4 adds `--expect <digest>` and the `does not match` rerun rule. Step 3.5 passes `--expect` too.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `[--expect DIGEST]` added to the `argument-hint`. Item 4 describes the digest, the `--skip` requirement and refusal, and that `--reason` does not combine with `--expect`.
- `CLAUDE.md`: the `tickets.py` bullet describes the `expect` line, the `--skip` requirement, and the refusal on a mismatch. `--expect` is added to the flags that do not combine with `--reason`.
- `.claude/agents/sdlc-lite-author.md`: line 16 sync rule names `--expect`.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: I read only the last 8 lines of output. They show the order selftest, run selftest, shellcheck and plugin validate all passing. I did not confirm the exit code or the earlier sections, including the tickets selftest.
- Em-dash count on `file/SKILL.md`, `ticket/SKILL.md` and `CLAUDE.md` was 0 before the edits. After the edits, `grep -c "—"` over all skills plus `CLAUDE.md` printed only `checks-that-bite/SKILL.md` (14), so those three files are still at 0. I did not touch `checks-that-bite/SKILL.md`.
- I did not run the `grep -c -- "--expect"` acceptance check separately. The edits themselves added `--expect` to all three files.

## Notes
None
