---
id: T-0561
title: "Bare-clone repos: worktree root falls back to the current lane's toplevel and nests again"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
In a bare-clone repo (a bare git dir with lanes beside it and no main checkout the agents may use), every SDLC Lite worktree goes to one fixed root outside any lane, and `migrate-0.23.sh` reports the layout instead of finding nothing.

## Repro
1. A bare clone with lanes at `ui-kit/lanes/<lane>` (gen-ui-kit's layout) and the owner's checkout at `main/`, where conductors never run git.
2. From inside a lane, run `python3 <plugin>/scripts/wtroot.py` or open a role's tmp prefix through `dispatch.py prepare`.

## Expected
A root outside every lane: a `worktree_root:` line in `.sdlc/config` when set, else the bare repo's lanes dir (`<bare parent>/lanes` or the dir holding existing lanes).

## Actual
`wtroot.py` falls back to `--show-toplevel` for a bare or non-`.git` common dir (wtroot.py:16-17), which inside a lane is the lane itself, so role tmp trees nest under `<lane>/.claude/worktrees/` again. gen-ui-kit (0.23.0 installed, 2026-10-15): "this repo is a bare clone with lanes at ui-kit/lanes/ (no .worktrees/ under a main checkout) ... the script has nothing in scope here."

## Context
T-0550 made the main checkout the root; a bare clone has none the agents may write to. Fix with a `worktree_root:` config line plus a bare-clone default, and teach `migrate-0.23.sh` to print the chosen root and exit 0 with "nothing to move" for this layout.

## Constraints
The failing selftest (a bare-clone fixture with a lane, prefix outside the lane) lands with the fix. Target 0.23.1.
