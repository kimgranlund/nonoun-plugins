<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0066: /file flags follow-ups that restate an open ticket before filing

## PR body
### Summary
`/file` filed a follow-up as a new ticket even when it restated an open ticket in different words. In the live T-0047 run, `calc.div raises an unhandled ZeroDivisionError when b == 0` was filed as T-0003 while T-0002 `div crashes on zero divisor` was still open. `close` only skips exact duplicates (same normalized title or slug), and `/file` step 3.2 checked follow-ups only against the task's own artifacts. With this change, `close --dry-run` lists the open tickets, and `/file` marks follow-ups that likely duplicate one of them so they get dropped.

### Changes
1. **`close --dry-run` lists open tickets** (`plugins/sdlc-lite/scripts/tickets.py`)
   - The dry run prints one `open T-NNNN <title> [<slug>]` line for each other ticket that is proposed, ready, or blocked, in id order.
   - These lines sit after the follow-up lines and before the rename, ack, and `expect` lines.
   - The digest, the output of a real close, and refusals are unchanged. `expect <digest>` is still the last line.
   - Selftest: case (p) now ignores `open ` lines. New case (p2) "open tickets listed" checks that an open ticket is listed with its full title, that a dropped ticket is not listed, and that the ticket being closed is not listed.
   - The module docstring, the `--dry-run` help, `skills/ticket/SKILL.md` item 4, and the tickets.py bullet in `CLAUDE.md` describe the new lines.
2. **`/file` marks likely duplicates** (`plugins/sdlc-lite/skills/file/SKILL.md`)
   - Step 3.1 says the dry run lists open tickets.
   - Step 3.2 compares each follow-up against the `open` lines and marks a restatement `likely duplicate of T-NNNN`, with a one-line reason. It uses the T-0047/T-0002 case as its example.
   - Steps 3.3 and 3.5 leave likely duplicates out of the recommended and unattended sets and pass their indices to `--skip`.
   - Step 3.6 reports each likely duplicate with its matching id.
   - `scripts/check.py` has a new item 7 and a check that fails, naming `skills/file/SKILL.md`, when that file lacks `likely duplicate` or `open T-NNNN`.
   - The sync sentence in `.claude/agents/sdlc-lite-author.md` now covers the open-ticket listing and the likely-duplicate step.

### Verification
- **Step 1: verifier L1 pass.**
  - The repro scenario (open `div-crash`, dropped `old-crash`, closing `calc`) printed exactly one line, `open T-0001 div crashes on zero divisor [div-crash]`, and `expect` came last.
  - `tickets.py selftest` passes.
  - Negative control: with the `open` lines removed from a throwaway copy, the selftest failed on (p2).
  - `check.sh` exited 0.
- **Step 2: verifier L1 pass.**
  - Both strings are present in `skills/file/SKILL.md`.
  - In a temp copy of the repo, `check.py` passes. After `likely duplicate` is removed from the skill, it exits 1 and prints `FAIL skills/file/SKILL.md: missing "likely duplicate"`.
  - The verifier read steps 3.2, 3.3, 3.5, and 3.6 in the diff.
  - `check.sh` exited 0.

The matching itself is a judgment the model makes in the `/file` session. Only two things are checked mechanically: that the dry run provides the open-ticket list, and that the skill contains the instruction.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py close --dry-run` now lists open tickets as `open T-NNNN <title> [<slug>]` lines. `/file` uses them to mark follow-ups that restate an open ticket as `likely duplicate of T-NNNN` and skips them instead of filing them (T-0066).

## Follow-ups
- `close --dry-run` lists open tickets from the local `--root` only, so `/file` cannot catch a follow-up that duplicates an open ticket in another worktree or on an unmerged branch (T-0066 plan risk).
