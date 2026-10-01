<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (`.gitignore` is `*\n`; each of root, `new`, `read` and `done` has a non-empty `AGENTS.md` and a `CLAUDE.md` of `@AGENTS.md\n`): pass. Evidence: I extracted every criterion from handoff.md and ran each verbatim with `bash -c`, with `SDLC_BASE_SHA` set. It exited 0. At base `caf98aa`, in a throwaway worktree, a probe send leaves no `.sdlc/messages/AGENTS.md` (exit 1), so the check can go red.
- AC2 (exactly ten `#` headings, no `{{`, rendered quoted script path): pass. Evidence: exit 0. I read `ENTRY_TEMPLATE` in the diff and it has the ten headings in order.
- AC3 (three `python3 ` spans in "Handle a message you were given", tails match): pass. Evidence: exit 0. Diff lines show read, reply and ack as the three spans.
- AC4 (required strings in the root `AGENTS.md`): pass. Evidence: exit 0 across the 19 `grep -qF` strings. The diff has the Messenger, Host limits and Trust text matching the handoff.
- AC5 (stage files: 3 lines each, `../AGENTS.md`, their commands): pass. Evidence: exit 0. `STAGE_TEMPLATES` in the diff matches the handoff's three lines per stage.
- AC6 (`reply` rewrites removed entry files): pass. Evidence: exit 0. `cmd_reply` calls `write_entries(mbox)` after `compose` and before `deliver`.
- AC7 (`count`, `list` and `expire` ignore the entry files): pass. Evidence: exit 0.
- AC8 (six new selftest labels print `ok:` and the run ends in PASS): pass. Evidence: exit 0. At base the same selftest prints 0 lines matching "entry files", so it bites.
- AC9 (copied file passes its selftest, then fails after the `ack` to `acknowledge` sed): pass. Evidence: exit 0. This shows the selftest's parse and scripted-run cases can go red.
- AC10 (`Entry files` line in `--help`): pass. Evidence: exit 0 on the built tree, and exit 1 at base.
- AC11 (old "send and reply create only new/<receiver>/" sentence gone from `--help`): pass. Evidence: exit 0. At base the old sentence is present (grep exit 0), so the negation bites.
- (guard) refused sends write no mailbox: pass. Evidence: exit 0. Both refusal paths occur before `write_entries` in `cmd_send`.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: exit 0 on the built tree, so no pre-build comparison was needed.
- (guard) no em dash in added lines of `messages.py`: pass. Evidence: exit 0. `git diff caf98aa -- plugins/sdlc-lite/scripts/messages.py | grep '^+' | grep -c <U+2014>` printed 0.
- (guard) only `messages.py` changed outside `.sdlc`: pass. Evidence: exit 0. `git status --short plugins` shows only ` M plugins/sdlc-lite/scripts/messages.py`.

## Out of scope changes
None. The builder edited the existing `race: one winner` leftovers check so it skips the state-level `AGENTS.md` and `CLAUDE.md`. That edit is in `messages.py` and the new entry files make it necessary. Receiver folders are still checked, so a torn claim is still caught (diff, `st_race`). `git diff --check` is clean.

## For the next attempt
None. One forward reference is by design: the `Entry files` docstring says `tickets.py roadmap` writes these files, and the handoff asked for that wording. That writer belongs to step 2.
