## Task goal
`/board` prints a one-line hint when a legacy `<root>/.board-state.json` exists, never touches the file, and leaves `--summary` and the no-file output unchanged.

Task constraints:
- board.py must still write nothing into the tree: never delete or modify the legacy file automatically; only hint.
- No hint when the file is absent; `--summary` output (used by statusline.sh) must stay unchanged.
- `plugins/sdlc-lite/scripts/check.sh` must pass (including the board selftest); add a selftest case for the hint if board.py has a selftest.
- Records that describe board output (CLAUDE.md Feed entry, .claude/agents/sdlc-lite-author.md, skills/board/SKILL.md) are updated in the same change if they become stale.

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

## Plan risks
- SKILL.md rule 3 says to print stdout verbatim with nothing added. The hint is part of stdout, so this stays consistent.
- The existing selftest asserts on the trailing footer text. A blank line plus the hint may break a strict "endswith" check. Step 1 should run the selftest to confirm.
