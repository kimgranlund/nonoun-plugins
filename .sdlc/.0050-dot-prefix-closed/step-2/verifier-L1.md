<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints PASS: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS`. The check can go red: in a throwaway worktree I no-oped the rename in `cmd_archive`, and the selftest printed `FAIL` on "archive moves done and dropped, keeps ready" and "second archive reports nothing to archive".
- Temp numbered root, `archive --dry-run`: pass. Evidence: on a root with `0001-a` done, `0002-b` dropped, `0003-c` proposed, and `check` ok beforehand, it exited 0 and printed `0001-a -> .0001-a` and `0002-b -> .0002-b`. `ls -A` was identical before and after.
- `archive` renames the closed folders: pass. Evidence: exit 0 with `archived 2 folder(s): ...`. `ls -A` then showed `.0001-a`, `.0002-b`, `0003-c`, `config` and `roadmap.md`.
- `check` after archive: pass. Evidence: `ok: 3 tickets, roadmap current`, exit 0.
- Second `archive`: pass. Evidence: printed `nothing to archive`, exit 0.
- Plain root refuses: pass. Evidence: exit 1 with `archive renames NNNN-<slug> folders and needs numbered mode (--numbered or ticket_folders: numbered in .../config); nothing written`.
- `archive --help`: pass. Evidence: it lists `--dry-run` and `--numbered`.
- Selftest `expect`s cover the required cases: pass. Evidence: the diff has expects for the dry run (writes nothing), done and dropped moving while ready stays, `check` after archive, the second run, the collision refusal (writes nothing) and plain-mode refusal (writes nothing). Only the no-op-rename mutation was run. The collision and plain-mode expects were checked by reading the diff, not mutated.
- `main` kw tuple, dispatch, subparser and Usage line: pass. Evidence: the diff shows `archive` in the kw tuple, `if cmd == 'archive'` in `run()`, the subparser, and the Usage and docstring lines.

## Out of scope changes
The tracked changes are `.sdlc/0050-dot-prefix-closed/handoff.md` and `plugins/sdlc-lite/scripts/tickets.py`. The `tickets.py` diff is larger than this step alone (it also holds the `close` archiving from step 1), which looks like uncommitted earlier-step work. Untracked files under `.sdlc/0050-dot-prefix-closed/` are task artifacts. The builder left CLAUDE.md and the `/ticket` docs alone, so `archive` is not documented there.

## For the next attempt
None
