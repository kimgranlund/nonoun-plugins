<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0, and case 8b builds stale, verified and codex-owned fixture lanes and asserts each ledger column (failed before the change): pass. Evidence: on the built tree the command printed `board selftest: PASS` and exited 0. Case 8b (board.py diff, `# 8b. --lanes ledger columns`) checks Base, Stale, Verifier, Merge and Owner for the stale, verified and codex lanes, and checks that the main row is `-` throughout. I confirmed it can fail in a throwaway worktree at `$SDLC_BASE_SHA`:
  - Old board.py with the new 8b spliced in: exit 1 on `--lanes ledger header, got ['| Lane | Branch | Board |', ...]`.
  - Stale forced to `no`: exit 1 on `stale lane shows its recorded base and Stale yes`.
  - Verdict forced to `none`: exit 1 on `verified lane shows base, Stale no and Verifier pass`.
  - Owner forced to `claude`: exit 1 on `codex lane shows Owner codex`.
  - Base cut to 8 chars: exit 1 on both the stale and verified assertions.
  - With the built file restored in that worktree, the selftest exited 0.
- In a repo whose only worktree is the main one, `board.py --lanes` prints the unchanged `| Lane | Branch | Board |` table (asserted in case 8b): pass. Evidence:
  - The case 8b assertion `--lanes with no lanes keeps the three-column table` fails when `ledger = True` is forced: exit 1, and the output shows the 8-column header.
  - Separate runtime check: I made a fresh single-worktree repo under the tmp prefix and ran base board.py and built board.py with `--lanes --root`. Both exited 0 and `diff` reported IDENTICAL: `| Lane | Branch | Board |` / `|---|---|---|` / `| solo-repo | main | t not planned |`.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0: pass. Evidence: printed `fanout selftest: PASS`, exit 0.
- `check.py`, `tickets.py --root .sdlc check`, `codex_roles.py generate --check` and `claude_roles.py generate --check` all exit 0: pass. Evidence:
  - `check.py`: `ok: 19 role levels, 9 agents, 22 generated definitions checked`, exit 0.
  - `tickets.py --root .sdlc check`: exit 0, with only existing warnings about placeholders in closed tickets and the flat layout.
  - `codex_roles.py generate --check`: `Codex agent definitions verified`, exit 0.
  - `claude_roles.py generate --check`: `Claude agent definitions verified (22 files)`, exit 0.
- Constraint, no em or en dashes: pass. Evidence: a grep for U+2013 and U+2014 in `git diff` matched nothing (exit 1), and `git diff --check` was clean.
- Real-repo run: `board.py --lanes --root .sdlc` in this repo prints the 8-column ledger. The main row is all `-`. Lane rows show verdicts `pass`/`none`, Merge `n/a`, and Owner `claude` or `-`.

## Out of scope changes
- `plugins/sdlc-lite/scripts/fanout.py:2033` changes `len(c) == 3` to `>= 3`. This is not out of scope: fanout's selftest parses `--lanes` output, so it depends on the changed output format, and it needs this change to keep reading lane rows. I ran `fanout.py selftest` and it passes.
- `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/skills/board/SKILL.md` add one-line descriptions of the new columns. This is the same-change record repair AGENTS.md requires. I read both diffs: they describe only the new `--lanes` columns.
- `.sdlc/0375-lane-ledger/handoff.md`: the builder appended an `## Acceptance criteria` section. It restates the Done-when items as commands and adds no new scope. I verified against both that section and Done-when.
- In case 8, the board.py selftest changed the "rows in list order" check from an exact `['repo','alpha','beta']` to "repo first, alpha and beta in any order". This is a slightly weaker check on code the step does not touch: the row loop still iterates `entries` in `git worktree list` order. It does not affect any criterion.

## For the next attempt
None
