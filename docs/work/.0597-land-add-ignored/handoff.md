---
id: T-0597
title: "fanout land's generated-file staging fails on ignored mailbox paths"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py land`, and so `lanes.py finish`, never fails while staging the regenerated `.sdlc` files: it stages tracked generated files and untracked ones that are not ignored, and nothing else.

## Repro
2026-10-15, this repo: `lanes.py finish T-0593-t0593` (after T-0565 landed) stopped at land with `git add -- .sdlc/roadmap.md ... .sdlc/messages/done/CLAUDE.md failed: The following paths are ignored by one of your .gitignore files`. `.sdlc/messages/` is git-ignored, and its router files are partly tracked.

## Expected
Land completes. Tracked files are staged (`git add -u --` or a `git ls-files` filter), untracked ignored files are skipped.

## Context
`merge_generated()` in `fanout.py` (around lines 1600 to 1626, T-0565) filters with `git check-ignore`, which reports nothing for tracked paths, then runs `git add --` over a list that still includes ignored untracked or nested paths. The T-0565 selftest fixture has no ignored mailbox, so it missed this.

## Constraints
Non-generated conflicts still stop the merge.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0. Its new case adds a fixture with `.sdlc/messages/` in `.gitignore` and some of its router files tracked, and land of two lanes succeeds; the case failed before the fix.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L1 · verdict: pass · verifier: verifier-L2 (opus) · base: 7873caf51047
- Changed: fanout land stages tracked generated files with add -u and skips ignored untracked ones
- Commits: fef76cb T-0597: land stages tracked generated files with add -u, skips ignored untracked ones
- Check: 1 `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0; its new case adds a fixture with ...: pass
- Check: 2 `git diff --check` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1625 matches git ls-files... -> notes.md
- Follow-up: note: the throwaway worktree is removed -> notes.md
