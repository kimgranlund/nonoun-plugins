---
id: T-0031
title: "Legacy .sdlc/.board-state.json files stay in existing projects..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0019
---

## Goal
When a project still has a legacy `.sdlc/.board-state.json` (left over from before T-0019 moved the board's "· changed" cache to a per-user cache dir), the user finds out and knows it is safe to delete. Per triage, a one-line hint is enough: board.py (the /board render) prints a single hint line when that file exists, and the /board skill doc (and CLAUDE.md Feed entry if it describes board output) notes it. Code lives in this repo under `plugins/sdlc-lite/` (scripts/board.py, skills/board/SKILL.md).

## Context
Follow-up from T-0019 (move-the-board-cache-sdlc/filer-L1.md):

Legacy `.sdlc/.board-state.json` files stay in existing projects after the T-0019 cache move; consider a one-line cleanup note or a /board hint when one is found.

## Constraints
- board.py must still write nothing into the tree: never delete or modify the legacy file automatically; only hint.
- No hint when the file is absent; `--summary` output (used by statusline.sh) must stay unchanged.
- `plugins/sdlc-lite/scripts/check.sh` must pass (including the board selftest); add a selftest case for the hint if board.py has a selftest.
- Records that describe board output (CLAUDE.md Feed entry, .claude/agents/sdlc-lite-author.md, skills/board/SKILL.md) are updated in the same change if they become stale.

## Triage
2026-09-24, user-approved: keep, P3; a one-line /board hint or cleanup note is enough.
