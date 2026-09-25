<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/bench/SKILL.md`: added the first instruction to resolve `BENCH` via `bench-dir.sh` before any `cd`. Task, README and results paths now use `$BENCH`. The summary call passes `--bench-dir "$BENCH"`.
- `plugins/sdlc-lite/skills/board/SKILL.md`: line 10 now says `<bench dir>/results` for benchmark runs, with a pointer to `scripts/bench-dir.sh`.
- `CLAUDE.md`: the Benchmark line now gives the resolve order and says the dev bench stays at `plugins/sdlc-lite/bench/`.
- `plugins/sdlc-lite/bench/tasks/README.md`: added one line about project-local tasks in `<project>/bench/tasks/`.

## Checks
- `grep -n 'CLAUDE_PLUGIN_ROOT}/bench'` on the bench SKILL.md returns nothing.
- The `bench-dir.sh` grep matches in the bench SKILL.md, in the first paragraph before the worktree `cd` in step 1.
- The `summary.sh --bench-dir` grep matches in the bench SKILL.md.
- `SDLC_BENCH_DIR` matches in `CLAUDE.md`, and `bench-dir.sh` matches in the board SKILL.md.
- `<project>/bench` matches in the bench tasks README.
- `git diff | grep '^+' | grep -c '—'` prints 0.
- `plugins/sdlc-lite/scripts/check.sh` exits 0 (selftests, shellcheck and plugin validate all ok).

## Notes
- `git diff --stat` shows 7 files changed, but I edited only 4. The other 3 are presumably uncommitted work from step 1, such as `bench-dir.sh` and its callers.
- `.claude/agents/sdlc-lite-author.md` is unchanged, as the handoff specified.
