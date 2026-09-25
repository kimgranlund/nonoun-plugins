<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/board/SKILL.md`: line 10 now says "the default order is by ticket id when...", and the doubled period after "override" is fixed.
- `CLAUDE.md`: the Feed bullet now says "by default (no `--sort`) it orders by ticket id...". "`--sort recent` restores recency" is kept.

## Checks
- `grep -n "default"` on both files: the new default wording shows in each. I did not re-read the rest of the grep output. This is an inference: no line claims recency is the unconditional default.
- `scripts/check.sh`: passed, including the selftest, the tickets selftest, the board selftest, shellcheck and plugin validate.

## Notes
- The first `sed -i` failed on macOS with no error reaching the files. I re-ran it with BSD syntax (`-i ''`) and the edits applied.
- `.claude/agents/sdlc-lite-author.md` has no sort or recency mention, so I left it alone.
- `argument-hint` is unchanged.
- I did not check the handoff's risks: whether any doc or script assumes newest-last, and whether `summary()` calls `sort_tasks` with the default.
