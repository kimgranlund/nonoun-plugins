---
id: T-0218
title: "Renumber check.py guards uniquely and guard it"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
check.py guard numbers are unique and sequential, and a guard keeps them that way.

## Intent
- Do: Renumbered the docstring guards to 1..23 once each (Spec gate 16, Carry forward 17, Solo agent 18, Conductor rules 19, Handoff freeze 20, Solo start path 21, Ticket budget 22), fixed every `docstring item N` comment, fixed docs/maintenance/sdlc-internals.md (Solo agent guard is item 18), and added guard 23: the numbers must run 1..N once each and every cited item must exist, with two negative controls inside check.py. Dated validation records are historical and keep the old numbers.
- Non-goals: model or effort defaults; a version bump, tag, push, or publish.
- Done when: the change is merged into local main with checks green and an independent verifier passed.

## Context
Closes a known limit listed in docs/validation/release-0.20.5.md. Built under the burn-down rules (one handwritten step, one L2 verifier).

## Evidence
Independent L2 verifier: pass on the rerun (`.sdlc/verify-0218/step-1/verifier-L2.md`). The first pass failed on a stale doc reference and two vacuous controls (`.sdlc/verify-0218/first-pass-note.md`); both fixed, then the rerun passed, showing each control exits 1 at 244d0af. check.sh, check-packaging, generate --check and tickets.py check passed on the merged branch.

## Constraints
None beyond the repository guidance.

## Closed

2026-10-04: Built and verified on branch limits (L2 verifier pass, evidence in the ticket); merged into local main in the limits merge.
