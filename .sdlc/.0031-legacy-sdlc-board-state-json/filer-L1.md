<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0031: /board hints when a legacy .sdlc/.board-state.json is present

## PR body
### Summary
T-0019 moved the board's "· changed" cache out of the repo and into a per-user cache dir. Projects set up before that change can still have an old `.sdlc/.board-state.json` lying around. With this change, `/board` prints one line saying the file is no longer used and is safe to delete. board.py never deletes or edits the file, `--summary` output does not change, and nothing changes when the file is absent.

### Changes
- `plugins/sdlc-lite/scripts/board.py`: when `<root>/.board-state.json` exists, `render()` adds a blank line and then `Note: legacy <path>/.board-state.json is no longer used (the board cache moved to a per-user dir); safe to delete.` The file is only checked for existence. `summary()` and the `--summary` path are untouched. The docstring gets one sentence about the hint. New selftest case 5c checks four things:
  - no hint without the file
  - a hint with the file
  - the file's bytes are unchanged
  - `summary()` returns the same output either way
- `plugins/sdlc-lite/skills/board/SKILL.md`: new Rules bullet saying to print the hint line verbatim like the rest of the output, and that the file is safe to delete.
- `CLAUDE.md`: the Feed entry now mentions the hint, and says the file is never deleted automatically and never appears in `--summary`.
- `.claude/agents/sdlc-lite-author.md`: unchanged. It does not describe board output.

### Verification
- Step 1 (verifier L1, pass):
  - `board.py selftest` printed PASS.
  - A render diff with and without the legacy file showed that only the blank line and the hint line were added.
  - `cmp` showed identical `--summary` output with and without the file.
  - The legacy file's `shasum` was the same before and after the render, and `find` showed no new files under the root.
  - Bite test: replacing `legacy.exists()` with `False` made the selftest fail with "legacy file gets the hint".
- Step 2 (verifier L1, pass):
  - `grep board-state` finds the new notes in SKILL.md:20 and CLAUDE.md:23. The same grep on the HEAD versions finds nothing.
  - `check.sh` exited 0. Negative control: an edited level row in a throwaway worktree made it exit 1.
  - A live render confirmed the hint text, `--summary` printing only the task line, and the legacy file left unchanged.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/board` now prints a one-line hint when a leftover `.sdlc/.board-state.json` is found, saying it is unused and safe to delete. The file is never touched, and `--summary` output is unchanged. (T-0031)

## Follow-ups
None
