---
id: T-0141
title: "Scope criteria need a build-start base: run.sh exports SDLC_BASE_SHA"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
A step's scope criteria compare against the tree the build started from, and that works whether or not anything gets committed later.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui (gen-ui T-0271): the criterion `git diff --name-only HEAD~1 HEAD` assumed the builder commits, but builders commit only on Merge steps, so it failed. The fix, `git diff --name-only HEAD`, became vacuous once the work was committed separately. It took 2 verifier fails and 2 conductor decisions to fix.

Tension: planner rule 6 (T-0100) bans shas pinned at plan time and says to compare against HEAD at build start, but a criterion has no name for "HEAD at build start" once HEAD moves.

Proposal: run.sh records `SDLC_BASE_SHA` (HEAD when a step's first builder run starts, stored in the step dir so the verifier and reruns use the same one) and exports it to builder and verifier. The planner rubric then says builders never commit (except on Merge steps), and scope checks use `git diff --name-only "$SDLC_BASE_SHA"`. The pins_sha lint allows `$SDLC_BASE_SHA`. Include a selftest.

Addendum from the peer (gen-ui T-0271): after the lane resynced main, `git diff --name-only <plan sha>` listed 18 files. So SDLC_BASE_SHA must be refreshed after every resync, or defined as the merge-base with the target branch (`git merge-base HEAD <target>`), not captured once.

## Constraints
The failing test lands before or with the fix, never after.
