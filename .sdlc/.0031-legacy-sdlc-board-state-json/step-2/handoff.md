## Task goal
`/board` prints a one-line hint when a legacy `<root>/.board-state.json` exists, never touches the file, and leaves `--summary` and the no-file output unchanged.

Task constraints:
- board.py must still write nothing into the tree: never delete or modify the legacy file automatically; only hint.
- No hint when the file is absent; `--summary` output (used by statusline.sh) must stay unchanged.
- `plugins/sdlc-lite/scripts/check.sh` must pass (including the board selftest); add a selftest case for the hint if board.py has a selftest.
- Records that describe board output (CLAUDE.md Feed entry, .claude/agents/sdlc-lite-author.md, skills/board/SKILL.md) are updated in the same change if they become stale.

## Step 2: Update the records that describe board output
level: L1
### Do
- `plugins/sdlc-lite/skills/board/SKILL.md`: add a Rules bullet. If the render ends with a legacy `.board-state.json` hint line, print it verbatim like the rest; the file is safe to delete and board.py never touches it.
- `CLAUDE.md` (repo root), Feed entry: after "so `/board` writes nothing into the tree", add that it prints a one-line hint when a legacy `.sdlc/.board-state.json` is present (never deleted automatically, never in `--summary`).
- `.claude/agents/sdlc-lite-author.md`: only if it describes board output. The grep found no board-output description there, so likely no change.
### Acceptance criteria
- `grep -n "board-state" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` shows the new notes.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.

## Plan risks
- SKILL.md rule 3 says to print stdout verbatim with nothing added. The hint is part of stdout, so this stays consistent.
- The existing selftest asserts on the trailing footer text. A blank line plus the hint may break a strict "endswith" check. Step 1 should run the selftest to confirm.
