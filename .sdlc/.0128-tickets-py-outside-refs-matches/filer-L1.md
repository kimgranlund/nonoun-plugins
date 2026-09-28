<!-- role=filer level=L1 model=sonnet effort=medium -->
All checks pass, single step, verifier verdict pass. Ready to draft the filer output.

## Warnings
None

## PR title
T-0128: Boundary-match tickets.py outside_refs and rewrite_files on folder-name characters

## PR body
### Summary
`tickets.py`'s `outside_refs` and `rewrite_files` matched a closing ticket's folder path as a fixed-string prefix, so `.sdlc/0001-a` also matched inside `.sdlc/0001-ab`. Closing or archiving the shorter-named ticket could then report or rewrite a citation that actually pointed at the longer-named sibling folder.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added a `literal_re(old)` helper (`re.escape(old)` plus a negative lookahead `(?![A-Za-z0-9_-])`) and switched `outside_refs`'s text search and `rewrite_files`'s replacement to use it, so a match only counts when followed by `/`, end of token, whitespace, or punctuation, never when it runs on into a longer folder name.
- Updated the literal-rule wording in the module docstring, the `outside_refs`, `rewrite_files`, and close docstrings, and on the new helper.
- Added selftest cases: a close case (`0003-x` / `0003-xy`) where a longer-name-only citation does not block, and `--rewrite-refs` rewrites only the shorter name's citation in a file citing both; a direct `outside_refs`/`rewrite_files` case with real `0001-a` and `0001-ab` folders; an archive case (`0001-alpha` / `0001-alphax`) with the same non-blocking and selective-rewrite behavior.
- `CLAUDE.md`: updated the `scripts/tickets.py` bullet to match the new wording.

### How verified
One step (L2 builder, L1 verifier), plan review, then the step. All acceptance criteria passed, including a negative control: reverting the two code lines to `old in text` / `.replace(old, new)` while keeping the new selftest cases made the selftest fail, confirming the added cases discriminate. The verifier independently reran the prefix-sibling criterion against the pre-build HEAD in a throwaway worktree and got the stated red result (`['both.md', 'only.md']`, exit 1), then confirmed it goes green post-build. `plugins/sdlc-lite/scripts/check.sh` passed in full (shellcheck, plugin validate, all selftests). `.claude/agents/sdlc-lite-author.md` was checked and correctly left unchanged, since it does not describe this scan.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed: `tickets.py` close and archive now match a citation of a ticket's own folder only up to a folder-name boundary, so a shorter ticket folder name no longer matches or gets rewritten inside a longer sibling folder name (e.g. `0001-a` inside `0001-ab`).

## Follow-ups
None
