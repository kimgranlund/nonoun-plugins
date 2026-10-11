---
id: T-0421
title: "A bounded route for a two-line plan correction after design and criteria are accepted"
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide whether a two-line plan correction after accepted design and criteria needs the full planner plus reviewer, and design a bounded route if not.

## Intent
- Do: design only, Markdown, docs/specs/sdlc-lite/bounded-plan-correction.md with a status line. Read maison's proposal (maison .sdlc/tickets/0365-bounded-plan-correction-route): immutable author revisions plus an allowlisted delta review, with semantic or criteria changes forced back to normal review. Read steps.py replan and the one-replan cap, agents/planner.md and plan-reviewer.md. Decide what counts as a bounded correction (renames, path fixes, no criterion or scope change), how it is proven bounded by a command, what review it gets, and what forces the normal route; include a negative control and the interaction with the replan cap.
- Non-goals: building it; model or effort changes.
- Done when:
  - The design names the files a build would change, the boundedness check, and the rejected alternatives; docs_check.py and check.py pass.

## Context
Maison and Codex, 2026-10-09: T-0351 (buildPrompt to assemblePrompt) needed a full fresh planner and reviewer. Not ready: needs the maintainer's go before a design lane.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- [ ] `docs/specs/sdlc-lite/bounded-plan-correction.md` exists with a `Status:` line and names the files a build would change, the boundedness check, and the rejected alternatives.
- [ ] It defines what counts as bounded, the review the correction gets, what forces the normal route, the interaction with the replan cap, and a negative control.
- [ ] `python3 plugins/sdlc-lite/scripts/docs_check.py` reports 0 errors and `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- [ ] The design contains no em or en dash, and `git diff --check` is clean.

## Closed

2026-10-11: built and verified in wave 32 (verifier L2 pass), merged
