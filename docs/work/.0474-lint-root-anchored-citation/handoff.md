---
id: T-0474
title: "steps.py lint: a citation whose prefix is exactly / is no citation (T-0470 finding 3b)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A citation whose prefix is exactly `/` is no citation, so `P + '/.sdlc/out/x.json'` no longer fails `dispatch.py prepare` link lint.

## Repro
1. Lint a step handoff holding the criterion `python3 -c "open(P + '/.sdlc/out/x.json')"` exits 0.
2. Run `python3 plugins/sdlc-lite/scripts/steps.py lint <handoff>`.

## Expected
No finding.

## Actual
`cited path does not exist` (`CITE_RE` at `steps.py:1406`, anchor at `steps.py:1436`).

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 3b. One condition in `cited_sdlc_paths` plus one `steps.py selftest` lint case. No repo keeps `.sdlc` at the filesystem root; a real absolute path has a longer prefix.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
