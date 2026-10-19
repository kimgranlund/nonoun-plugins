---
id: T-0019
title: "Move the board cache .sdlc/.board-state.json out of the working..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0018
---

## Goal
Rendering `/board` (board.py) never creates or modifies any file inside the repo's working tree, in any project, whether or not it ignores `.sdlc/.board-state.json`, while the "· changed" markers keep working between renders.

## Intent
Literal ask: Move the board cache `.sdlc/.board-state.json` out of the working tree so `/board` never dirties a repo, even one that doesn't use the recommended ignore lines (needs changes to board.py and statusline.sh).
Deltas:
- Where the cache goes: defaulted: a per-user cache dir outside the repo, `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state/<key>.json`, where `<key>` is a stable hash of the resolved absolute `--root` path (so two roots, two worktrees, or two repos never share state). An env override `SDLC_BOARD_STATE_DIR` sets the directory (used by the selftest so it never touches the real user cache). Rejected: `.git/` (fails outside git and for `--root bench/results` style roots needs extra keying anyway).
- statusline.sh: defaulted: needs no change, because `board.py --summary` already writes no state; the builder confirms this and leaves statusline.sh untouched unless it finds a write.
- Legacy `.sdlc/.board-state.json` files in existing projects: defaulted: board.py stops reading and writing it and never deletes it (deleting a tracked file would itself dirty the tree).
- Docs: defaulted: update board.py's docstring, `skills/handoff-format/SKILL.md` (the recommended ignore block drops the board cache line, or notes it only matters for older versions), and the Feed line in the repo root CLAUDE.md if it mentions the cache; keep this repo's root `.gitignore` line harmless (may stay).
Do: change board.py so its state file lives in the per-user cache dir above (created on demand, write failures still ignored), update the selftest so it isolates state via `SDLC_BOARD_STATE_DIR` in a temp dir and adds a check that a render leaves no new file under the root, and update the docs listed.
Non-goals: changing the `.running`/`.log` ignore advice; changing board output format; changing statusline.sh behavior.
Done when: after `board.py --root <tmp>/.sdlc` renders twice on a fixture repo, `git status --porcelain` in that repo is empty (no `.board-state.json` anywhere under it) and the second render still shows "· changed" for a row whose status changed between renders; `board.py selftest` and `plugins/sdlc-lite/scripts/check.sh` pass.

## Context
Follow-up from T-0018 (gitignore-board-state/filer-L1.md):

Move the board cache `.sdlc/.board-state.json` out of the working tree so `/board` never dirties a repo, even one that doesn't use the recommended ignore lines (needs changes to board.py and statusline.sh).

## Constraints
- Board table output (columns, glyphs, %, "· changed" semantics) does not change.
- `--summary` still writes no state.
- No new dependencies; Python stdlib only.
- No em dashes in any edited file.
