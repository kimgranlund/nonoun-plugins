<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `literal_re(old)`, which is `re.escape(old)` plus `(?![A-Za-z0-9_-])`. `outside_refs` now uses it for `search` and `rewrite_files` for `sub`. The literal-rule wording is updated in the module docstring, the `outside_refs`, `rewrite_files` and close docstrings, and a docstring on the new helper. Added selftest cases:
  - Close (`0003-x` / `0003-xy`): a cite of only the longer name does not block. With `--rewrite-refs`, a file citing both gets only the `0003-x` cite rewritten.
  - A direct `outside_refs`/`rewrite_files` case with real `0001-a` and `0001-ab` folders.
  - Archive (`0001-alpha` / `0001-alphax`): a cite of only the longer name does not block, and `--rewrite-refs` rewrites only the `0001-alpha` cite.
- `CLAUDE.md`: the `scripts/tickets.py` bullet now says the literal ends at `/`, the end of a token, or punctuation, and never runs on into a longer folder name.

## Checks
- Criterion 1 (prefix sibling via `outside_refs`/`rewrite_files`): printed `['both.md']`, exit 0.
- Criterion 2 (guard: end of line, punctuation, `/`): printed `['e.md', 'p.md', 'q.md', 's.md']`, exit 0.
- `grep -qF "0001-ab" plugins/sdlc-lite/scripts/tickets.py`: exit 0.
- `python3 -B plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, exit 0.
- Negative control: with only the two code lines put back to `old in text` and `.replace(old, new)`, and the new selftest cases kept, the selftest reported FAIL. The file was then restored.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (all selftests, shellcheck and plugin validate ok).
- `git diff --stat HEAD`: shows the docstring and CLAUDE.md wording changes.

## Notes
- `.claude/agents/sdlc-lite-author.md` does not describe the literal rule, so I left it unchanged.
- `git diff` also shows `.sdlc/tickets-py-outside-refs-matches/handoff.md` as modified. That change was already in the tree before this step, and this step did not touch the file.
