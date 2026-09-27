<!-- role=filer level=L1 model=sonnet effort=medium -->
All steps passed. Single-step plan, builder done, verifier pass, all criteria including check.sh green. No warnings.

## Warnings
None

## PR title
T-0131: Reference scan stops treating another tree's .sdlc/0003-x as a reference

## PR body
Summary: In numbered mode, `tickets.py`'s reference scan for `close` and `archive` treated any literal-substring match of `<rel>/<slug>` as a reference, even when the path resolved into another tree (`other/.sdlc/0003-x`, an absolute path into another repo, `../other/.sdlc/0003-x`). This contradicted the documented rule that a path resolving elsewhere is not a reference, so `close`/`archive` could refuse to run, or `--rewrite-refs` could rewrite, based on an unrelated tree's identically-named folder.

Changes:
- `plugins/sdlc-lite/scripts/tickets.py`: `literal_re` now requires the literal to start a path token (start of text or right after a `TOKEN_RE` delimiter: whitespace, quote, backtick, paren, angle or square bracket), keeping the existing trailing lookahead that already rejects `.sdlc/0003-xy` as a match for `0003-x` (T-0128). `outside_refs` and `rewrite_files` both consume the updated `literal_re`, so a non-resolving other-tree path is no longer reported and no longer rewritten, while a real cite mixed into the same file still is. `ref_tokens` (path resolution) is unchanged.
- Added `close` and `archive` selftest cases covering `other/.sdlc/0003-x`, an absolute path into another directory, `../other/.sdlc/0003-x`, and a file mixing an other-tree cite with a real one (rewrite touches only the real cite).
- Updated docstrings in `literal_re`, `outside_refs`, and `rewrite_files`, plus `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, and `plugins/sdlc-lite/skills/ticket/SKILL.md` to state the "starts a path token" rule and note the accepted limitation that a URL or a `key=` prefixed form no longer counts as a reference.

Verification: single-step plan (builder L3 opus high, verifier L2 sonnet high, verdict pass). All acceptance criteria passed, including a red-before/green-after check that patches `literal_re` back to the pre-change regex and confirms the new selftest cases fail without the fix (proving they bite), the existing real-cite cases (bare token, backticked, parenthesized, quoted, and this toplevel's absolute path) still pass, and the full `plugins/sdlc-lite/scripts/check.sh` gate is green. The verifier ran a negative control against pre-build HEAD for the first criterion and reviewed the diff for each doc-sync grep to confirm real content changes, not just incidental string matches.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed: `tickets.py close`/`archive` (numbered mode) no longer treat another tree's identically-named `.sdlc/NNNN-slug` folder as a reference to the folder being closed or archived; the literal reference match now must start a path token.

## Follow-ups
None
