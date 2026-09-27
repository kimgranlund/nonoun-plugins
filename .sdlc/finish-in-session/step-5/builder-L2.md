<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- CLAUDE.md: added a `## Decisions` bullet for T-0142 (finish small related work in the session that found it: the `Loose ends` step, the `/fix` fast lane, the `fix-now:`/`decide:`/`note:` tags, the `--ticket N` one-ticket cap, the `.sdlc/notes.md` sink, and check.py's guard). I re-read the existing tickets.py, Launcher skills, and `/chain` bullets. They already match what shipped, so they stay as they are.
- .claude/agents/sdlc-lite-author.md: added a sentence to the tickets sync invariant covering the tags, `close --ticket N`/`--expect`, the cap, and notes.md. Added a new "Finish in session" invariant for `Loose ends` and `/fix`. I left the After every change list alone because check.sh's contents did not change.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh` before my edits: exit 0.
- `grep -q 'T-0142' CLAUDE.md`: pass.
- `grep -qF -- '--ticket' .claude/agents/sdlc-lite-author.md`: pass.
- `grep -q 'Loose ends' .claude/agents/sdlc-lite-author.md`: pass.
- `grep -qF '/fix' .claude/agents/sdlc-lite-author.md`: pass.
- `bash plugins/sdlc-lite/scripts/check.sh` after my edits, first run: exit 1. The only failure was `hook selftest: FAIL: block-stray-worktree without role: exit 141, want 0`.
- `bash plugins/sdlc-lite/scripts/check.sh`, second run: exit 0, no FAIL lines.

## Notes
- The exit 1 on the first post-edit check.sh run was exit 141 (SIGPIPE) in the block-stray-worktree hook selftest. This step changed only CLAUDE.md and the author agent file, no hook or selftest. The run before my edits and the rerun after both passed. It looks like a flaky selftest under host load, so a verifier may see it once.
- The step's Do said /fanout is kept in sync on the tags, but check.py's finish-in-session guard does not cover the /fanout skill. The CLAUDE.md bullet names only the files check.py actually guards. The author invariant lists /fanout because the step asked for it.
