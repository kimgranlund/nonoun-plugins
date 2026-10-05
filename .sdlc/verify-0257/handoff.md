# Verify T-0257 broken-links cleanup

Verify commits 5b942a2..HEAD in this worktree. Do not edit files. Run from the repository root.

Criteria:
1. `python3 plugins/sdlc-lite/scripts/rename_refs.py links` prints 8 broken, and `rename_refs.py selftest` passes.
2. The 9 edited link targets (see `git diff 5b942a2 -- .sdlc`) all resolve and changed only path text; nothing else in those dated records changed.
3. `strip_code` excludes fenced and inline-code links only: a link in prose still counts (try a temp file with one broken prose link and one in a fence, in a throwaway copy).
4. `check.py` item 32 fails on an unlisted broken link and on a stale allowlist row (observe both by editing a scratch copy, not the repo files).
5. `docs/reports/broken-links-cleanup.md` and `broken-links-allowlist.md` claims match what commands show; list any overstatement.
6. `python3 plugins/sdlc-lite/scripts/check.py`, `tickets.py check`, `python3 scripts/check-packaging.py`, `git diff --check 5b942a2` pass.

Report pass or fail with evidence per criterion.
