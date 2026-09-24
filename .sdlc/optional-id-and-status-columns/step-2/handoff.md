## Task goal
`/board` shows each task's ticket id and ticket status without changing the board for task dirs that have no ticket front matter. (Ticket T-0009, `.sdlc/optional-id-and-status-columns/handoff.md`; read its Intent and Constraints.)

Repo root: the git work tree containing this `.sdlc/`. All commands run from there.

## Step 2: Update board and handoff-format skill docs to describe the new columns
level: L1
### Do
- `plugins/sdlc-lite/skills/board/SKILL.md`: change the frontmatter `description` (and any body text) describing the table as `(Task, Step, Status, %)` to also mention the optional `ID`/`Ticket` columns and when they appear (only when a rendered task has ticket front matter).
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: fix the line (around line 45) stating "board.py does not parse front matter" — board.py now reads `id`/`status` via `tickets.py`'s parser for display only; it still does not validate or write front matter, and `tickets.py` remains the sole parser/writer of ticket semantics. State this precisely so the doc doesn't contradict the code.
### Acceptance criteria
- `grep -n "does not parse" plugins/sdlc-lite/skills/handoff-format/SKILL.md` no longer matches an unqualified claim that board.py never touches front matter (or the line is rewritten to accurately describe display-only reads).
- `grep -n "Task, Step, Status" plugins/sdlc-lite/skills/board/SKILL.md` either no longer matches, or the surrounding text now also documents the optional `ID`/`Ticket` columns.
- `plugins/sdlc-lite/scripts/check.sh` still exits 0 (docs changes don't break `claude plugin validate` or shellcheck).
