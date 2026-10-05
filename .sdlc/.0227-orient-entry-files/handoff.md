---
id: T-0227
title: "Orient a harness: root AGENTS.md work section, tree map, docs entry"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A harness that opens the repo root learns what is here, where to look, and how work is done, without reading the tree.

## Intent
- Do: add a "Map and how work is done here" section to the root AGENTS.md (tree map, do-not-read line, philosophy, lane rule, ticket rule), and add docs/AGENTS.md and docs/CLAUDE.md that route by folder.
- Non-goals: per-folder entry files under docs/ (a generated 100-line validation index goes stale); changing invariants or model defaults; a version bump, tag, push, or publish.
- Done when: the root file stays near 80 lines with every existing section intact, every added link resolves, check.sh and the packaging check pass, and an independent verifier confirmed it.

## Context
User request 2026-10-04: what should AGENTS.md contain to orient a harness. onboard.py setup is written for consumer repositories: its root block says to run work through /chain and /fix, which contradicts this repository's lane rule, and it generates folder entry files that would list 59 validation records. Both root AGENTS.md and docs/AGENTS.md stay hand-maintained (onboard.py check reports them unmanaged).

## Constraints
One authoritative location per fact; link instead of copying. No em dashes.

## Verification
First L3 (Fable) pass: criteria 1, 2 and 5 passed; criterion 3 failed on one real error (the `docs/AGENTS.md` row for `lean-sdlc/` called it a solo design), criterion 4 was a plan defect (the brief's own grep pattern held an em dash). Fixed in 613b251. Narrow L3 re-verification of those two criteria: pass (`.sdlc/verify-0227-b/verifier-L3.md`). check.sh, check-packaging.py and tickets.py check passed in the first pass on the same built files.

## Closed

2026-10-04: Merged into local main (branch orient, T-0227). Independent L3 verifier: criteria 1, 2, 5 passed; criterion 3 found one real error (lean-sdlc row) fixed; criterion 4 was a plan defect; narrow re-verify passed. check.sh, check-packaging, generate --check, tickets check, git diff --check pass.
