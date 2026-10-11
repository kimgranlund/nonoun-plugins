---
id: T-0442
title: "Replay A/B of builder overlays on the five bench tasks"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0441]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
Do the builder L1 and L5 overlays improve cost, first-pass rate, blocked rate or verifier minutes on a fixed task set?

## Question
Do the builder L1 and L5 overlays improve cost, first-pass rate, blocked rate or verifier minutes on a fixed task set, or should the idea be dropped?

## Goal
A dated report with a keep, extend or drop verdict backed by priced runs.

## Intent
- Do: run the architect's replay A/B (Approach "Proof" paragraph): the five bench tasks under `plugins/sdlc-lite/bench/tasks/`, one step handoff each at the task's base in a throwaway worktree, with and without the overlay, two repetitions, `dispatch.py prepare builder <level>` and `record --transcript` so each row is priced, graded by the hidden `check:` command, one verifier per arm; record `.sdlc/evals/0005-builder-overlays.md` and `docs/reports/<date>-builder-overlay-ab.md`. Fix the bench task repo paths (`/Users/kimba/...`) for this machine first. Apply the design's drop rules.
- Non-goals: changing overlays during the run; extending to other roles.
- Done when: the report states the verdict and numbers, and whether the result is a null at this sample size.

## Context
Design: `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` (Proof, drop rules, Risks). Depends on T-0441. Cost budget: state a dollar cap in the ticket before starting and stop at it.

## Constraints
No model or effort change. Report unverified anything not run. One ticket, one lane.
