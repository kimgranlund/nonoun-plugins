<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
`/board` prints a one-line hint when a legacy `<root>/.board-state.json` exists, never touches the file, and leaves `--summary` and the no-file output unchanged.

## Step 1: Add the legacy-file hint to board.py, with selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`, `render()`, after the `pcts` footer and before the state write, append a blank line and one hint line when `(root / '.board-state.json').exists()`. Suggested text: `Note: legacy .sdlc/.board-state.json is no longer used (the board cache moved to a per-user dir); safe to delete.` Use the actual path (`root / '.board-state.json'`) in the message. Read only: do not delete or modify the file. Leave `summary()` and `main()`'s `--summary` path untouched.

Add selftest cases near the existing "render writes no .board-state.json" check (around line 490):
- Render a root that has a `.board-state.json`. The output contains the hint, and the file's bytes are unchanged afterwards.
- Render a root without the file. The output has no hint.
- `summary(root)` on a root with the file returns the same string as without it.

Update the docstring at the top of the file (around line 25) with one sentence about the hint.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`.
- In a temp root with a task dir and a `.board-state.json`, `board.py --root <tmp>` output contains `.board-state.json` and `safe to delete`. The same root without the file prints no such line.
- `board.py --root <tmp> --summary` output is identical with and without the legacy file.
- The legacy file's checksum is unchanged after a render, and the render creates no new file under the root.
- Temporarily removing the hint code makes the selftest fail (the new case bites).

## Step 2: Update the records that describe board output
level: L1
### Do
- `plugins/sdlc-lite/skills/board/SKILL.md`: add a Rules bullet. If the render ends with a legacy `.board-state.json` hint line, print it verbatim like the rest; the file is safe to delete and board.py never touches it.
- `CLAUDE.md` (repo root), Feed entry: after "so `/board` writes nothing into the tree", add that it prints a one-line hint when a legacy `.sdlc/.board-state.json` is present (never deleted automatically, never in `--summary`).
- `.claude/agents/sdlc-lite-author.md`: only if it describes board output. The grep found no board-output description there, so likely no change.
### Acceptance criteria
- `grep -n "board-state" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` shows the new notes.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.

## Risks
- SKILL.md rule 3 says to print stdout verbatim with nothing added. The hint is part of stdout, so this stays consistent.
- The existing selftest asserts on the trailing footer text. A blank line plus the hint may break a strict "endswith" check. Step 1 should run the selftest to confirm.
