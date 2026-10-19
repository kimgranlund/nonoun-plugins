---
id: T-0257
title: "Fix moved-target Markdown links, exclude code from the link counter, guard the baseline"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Markdown link counter reports real broken links only, and a baseline guard keeps the remainder explicit.

## Intent
- Do: exclude code from the counter, allowlist what remains, add check.py item 32.
- Non-goals: editing dated records.
- Done when: `rename_refs.py links` equals the allowlist and the guard's negative controls fire.

## Context
See docs/reports/broken-links-cleanup.md. Counter before: 829 checked, 96 broken.

## Constraints
What must not change. "None" if none.

## Closed

2026-10-05: Counter excludes code; 12 allowlisted; check.py item 32 guard; independent L3 verifier passed on attempt 2
