---
id: T-0258
title: "fanout numbered close ignores ticket_root"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
fanout numbered mode closes a merged ticket at the folder path that includes `ticket_root`, so the lane continues.

## Context
After a merge fanout prints `T-NNNN merged, close refused: .sdlc/NNNN-slug/handoff.md: missing or has no front matter, so it is not a ticket; nothing written`. The path lacks `/tickets/` although `.sdlc/config` has `ticket_root: tickets`. The lane then stops and later tickets in it are skipped.
Evidence: maison `.worktrees/fanout2/report.md` (T-0081, merge 05bb06a), `.worktrees/fanout3/report.md` (T-0079, merge a29ed03); 0.20.7 and 0.20.8 field use.
Fix: resolve the close path through ticket_root. Regression test in the fanout selftest: numbered `<root>/tickets/NNNN-slug/handoff.md` closes after a merge.

## Constraints
No push, tag, version bump, or publish. No em dashes.
