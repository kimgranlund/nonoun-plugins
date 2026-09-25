<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `.NNNN-` grep finds at least one hit in each of the 4 files: pass. Evidence: I ran the check under bash with `test -f` guards, so a missing file would have been reported rather than silently passing. Current tree: CLAUDE.md 1, ticket/SKILL.md 1, handoff-format/SKILL.md 2, sdlc-lite-author.md 1. The check bites: in a throwaway worktree at HEAD all four counts were 0. Hit locations: CLAUDE.md:25, ticket/SKILL.md:15, handoff-format/SKILL.md:23 and :47, sdlc-lite-author.md:16.
- `archive` grep finds a hit in CLAUDE.md and ticket/SKILL.md: pass. Evidence: `grep -c archive` gives CLAUDE.md 1 and ticket/SKILL.md 2 (the argument-hint and the Rules line). At HEAD both counts are 0, so the check bites. The docs match the code: `tickets.py` has `cmd_archive` at line 603, and its usage line 5 lists `archive [--dry-run] [--numbered]`.
- No em dash in the 5 files: pass. Evidence: `grep -rn '—' <5 files>` printed nothing, rc=1, with every path confirmed to exist. Negative control: I appended an em dash to CLAUDE.md in the HEAD worktree and the grep then hit `CLAUDE.md:83:x — y` with rc=0.
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` returned rc=0. The tail of its output shows `steps selftest: PASS`, `order selftest: PASS`, `run selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- The Do-list content is present in each file: pass. Evidence: `git diff` shows each item.
  - CLAUDE.md tickets.py line: the close rename, "every tool treats a `.NNNN-<slug>` folder as a closed ticket", the `check` failure on a dot folder that is not done or dropped, `archive [--dry-run]`, and "`_templates` and other dot entries stay skipped".
  - ticket SKILL: `archive [--dry-run] [--numbered]` in argument-hint, and the extended numbered-folders rule.
  - handoff-format: the layout entry `.sdlc/.NNNN-<slug>/`, and the rename sentence in the Ticket front matter section.
  - file SKILL step 4: the added clause "In numbered mode the folder becomes `.NNNN-<slug>` after close."
  - author agent: the Invariants sync line.

## Out of scope changes
None for this step. `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/scripts/board.py` and `plugins/sdlc-lite/scripts/steps.py` are the code work of steps 1 to 3. The `.sdlc/dot-prefix-closed/handoff.md` edit is the task's Intent and Constraints, filled in before planning. The step-dir artifacts are role output.

## For the next attempt
None
