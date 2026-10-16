---
id: T-0586
title: "Under layout: topics, tidy, check and the router text disagree"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0586-t0586
worktree: ../sdlc-lite.worktrees/T-0586-t0586
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Under `layout: topics`, `tickets.py tidy`, `tickets.py check` and the generated router text agree on which top-level `.sdlc` entries are allowed and where tidy archives to.

## Context
Found by the T-0585 solo and verifier (2026-10-15).
- A loose root `notes.md` or `roadmap.md` is allowed by `tidy` (`TOP_ALLOWED`) but reported by `check` as a stray under topics.
- The router Procedures block (`tickets.py` around line 2233) says `tidy lists its move into archive/` for every layout; under topics it should say `work/archive/`.

## Intent
- Do: make tidy's allow list depend on the layout the same way `check` does, and render the router line from `layout_paths()`.
- Non-goals: flat-layout behavior.
- Done when: the criteria pass.

## Constraints
Flat output unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new topics case shows a loose root `notes.md` listed by `tidy` and the router naming `work/archive/`. The case failed before the change.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full; verifier notes: note: plugins/sdlc-lite/scripts/tickets.py:2443 under topics, a `top_level_allow:` name is still kept by tidy but reported by check (probe: check rc=1 on roadmap.md, keep-a.sh, keep-dir, archive). The new router line documents this on purpose, so tidy and check still differ for glob-allowed names. | note: plugins/sdlc-lite/scripts/tickets.py:2643 existing topics repos get `router block stale` from check until their roadmap/router is regenerated, because the router text changed. | note: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0586-verifier-L2 scratch probe files are left behind. The permission hook denied rm there. The throwaway worktree was removed.) · verifier: verifier-L2 (opus) · base: aefead6e10fb
- Changed: see commits
- Commits: f69b8bf T-0586: Under layout: topics, tidy, check and the router text disagree; 48f9eab T-0586: record lane T-0586-t0586
- Check: 1 `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0; its new topics case shows a loos...: pass
- Check: 2 `git diff --check` exits 0: pass
