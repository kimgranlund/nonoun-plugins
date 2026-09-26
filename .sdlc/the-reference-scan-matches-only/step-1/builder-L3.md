<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `outside_refs` now runs one `git grep` for the folder name `<slug>`. It keeps a file only if the file has the literal `<rel>/<slug>` (unchanged rule) or a path token that resolves to the folder.
  - New `TOKEN_RE` and `ref_tokens`: the path-token matcher and the check that a token resolves to the folder.
  - `rewrite_files` does the same byte replace as before, then rewrites only the `<slug>` part of each resolving token to `.<slug>`. Its signature and both callers are unchanged.
  - Updated the docstrings of `outside_refs`, `rewrite_files` and `cmd_close`.
  - Added new selftest cases after the existing `(u) refs` and `archive refs` blocks.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: exit 0, `tickets selftest: PASS`.
- Criteria 2 to 7 (the six shell commands in the handoff), each run with `bash -c`: all exit 0.
  - close refuses the relative ref
  - close `--rewrite-refs` keeps the relative form
  - archive `--dry-run --rewrite-refs` lists the file
  - `./` link rewritten
  - (guard) absolute ref refused, then rewritten
  - (guard) negative controls untouched
- Red before, green after:
  - Setup: `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`, copied the new tickets.py in, then swapped `outside_refs` and `rewrite_files` back to the HEAD versions.
  - Result: selftest FAIL, and only the 12 new `../` and `./` cases fail (3 per form for close and for archive).
  - The absolute cases, the negative controls and every existing case pass there.
  - Worktree removed and pruned afterwards.
- `git diff HEAD -U0 -- plugins/sdlc-lite/scripts/tickets.py`: the two selftest hunks (`@@ -1649,0` and `@@ -1830,0`) only add lines. All removed lines are in `outside_refs`, `rewrite_files` and the `cmd_close` docstring.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 (all selftests, shellcheck, plugin validate).

## Notes
- A token must contain a `/` to count as a reference. That keeps a bare `0003-x` word out, even in a file directly in the ticket root, where it would otherwise resolve to the folder.
- Resolution is by path text only, so it still works in close after the rename. For absolute tokens it also resolves symlinks (`os.path.realpath`), so a macOS `/var` path matches `/private/var`.
- The absolute-path guard and its selftest cases also pass at base: the old literal `<rel>/<slug>` rule already finds an absolute path that contains `.sdlc/0003-x`. That is expected for a guard.
- A file that git grep finds but that can't be read is kept as a hit, so the close refuses rather than passing silently.
- The module help text still describes the old scan; that is left for Step 2.
- `.sdlc/the-reference-scan-matches-only/handoff.md` already had uncommitted changes before this run; I did not touch it.
