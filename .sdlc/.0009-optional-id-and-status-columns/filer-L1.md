<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0009: Optional ID and Ticket columns in scripts/board.py

## PR body
### Summary
`/board` now shows each task's ticket id and ticket status, so you can tie a board row to its roadmap ticket. Two new columns, `ID` and `Ticket`, appear only when at least one rendered task has ticket front matter. When no task has front matter, the table is byte-identical to before.

The header becomes `| ID | Task | Ticket | Step | Status | % |`. A task without front matter gets empty cells in both new columns. `--summary` (statusline) and the `.board-state.json` keys are unchanged.

### Changes
- `plugins/sdlc-lite/scripts/board.py`
  - Imports `tickets` and adds `ticket_of()`, which reads `id`/`status` with `tickets.parse`. Any read or parse error counts as no front matter, so tickets.py stays the only front matter parser.
  - Moves the table render into `render()`. The column gate is checked after the `--task` filter.
  - Adds a `selftest` subcommand and updates the docstring.
- `plugins/sdlc-lite/scripts/check.sh`: runs `board.py selftest || fail=1` after the tickets selftest.
- `plugins/sdlc-lite/skills/board/SKILL.md`: the description and rules now cover the optional columns and when they appear.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: line 45 now says board.py reads `id`/`status` for display only, through tickets.py's parser. It never requires, validates, or writes front matter.

### Verification
- Step 1 (builder L3, verifier L2 Fable medium): pass.
  - `board.py selftest` prints PASS with rc=0.
  - The verifier broke the code three ways and selftest failed each time with rc=1: gate forced to true, gate forced to false, and the exception guard narrowed to `KeyError`.
  - At the repo root, the board shows the 6-column header and a `T-0009 | ... | ready` row. HEAD's board.py on the same dir prints 4 columns.
  - `--root plugins/sdlc-lite/bench/results` matches `baseline-bench-board.txt` byte for byte (`cmp`).
  - `--summary` output shapes are unchanged and `summary()` is untouched. The text differs from the baseline only because the task has been planned since the baseline was captured.
  - `check.sh` exits 0.
- Step 2 (builder L1, verifier L1 Opus medium): pass.
  - The literal grep criterion also passed at HEAD, so on its own it proved nothing. The verifier used a broader grep instead: it matches the old unqualified claim at HEAD, and in the working tree that claim is gone.
  - At HEAD the board SKILL.md never mentioned `ID` or `Ticket`. It now documents both columns and their gating, and that matches board.py.
  - `check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/board` (`scripts/board.py`) shows optional `ID` and `Ticket` columns, read from ticket front matter through `tickets.py`'s parser, whenever a rendered task has front matter. Boards without ticketed tasks render exactly as before, and `--summary` is unchanged. `check.sh` now runs `board.py selftest`. (T-0009)

## Follow-ups
None
