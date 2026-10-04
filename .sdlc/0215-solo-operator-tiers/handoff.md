---
id: T-0215
title: "Solo operator session agent: tiers S, M, L as the default lane for small and medium tickets"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0199]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A declared session agent, `solo`, delivers one ticket end to end in a single session, with tiers S, M and L, and the lane script names `solo` as the default for size S and M tickets.

## Intent
- Do: add agents/solo.md (session agent, not a run.sh role, like conductor and messenger) and its generated Codex agent; define three tiers by ticket size with a short typed brief (ticket, files, check commands, done criterion); extend the lane script (steps.py lane, T-0197) to output solo, lean or full with a reason, solo as the default for S and M; require one independent batched verifier at the end for tiers M and L on a different model family (none for S, as /fix today); extend check.py to cover the agent file and Codex mapping with a negative control; conductor.md names the lane choice (reconcile with T-0199, do not duplicate). Model and effort per tier, decided by the user 2026-10-04: solo S = Sonnet low, solo M = Sonnet xhigh, solo L = Opus xhigh. Tier effort is a launch parameter, so the planner decides where the table lives (agent front matter pins only a model, as messenger does; per-tier effort needs a launch flag or table entry); if it lands in run.sh or models.json, satisfy the T-0185 rule (a new eval file in .sdlc/evals/ plus scripts/evals.py lock, citing the benchmark result), and keep scripts/check.py agreement and level-rubric in step. Codex equivalents follow the same tier mapping from adapters/codex/models.json, chosen by the existing Claude-tier mirror (Sonnet to luna, Opus to sol) unless the user says otherwise.
- Non-goals: removing the lean or full chain; changing any existing model default without an eval; a version bump, tag, push, or publish.
- Done when: the agent file, mapping, lane output and check exist, an independent verifier passed, one live run per host shows a size-M ticket delivered by solo with a batched verifier, and the lane output is recorded.

## Context
User decision 2026-10-04 after "if an orchestration-based system cannot compete with a basic single-session agent ... we have some really big problems". Evidence to read first: docs/validation/solo-vs-lean-benchmark-2026-10-04.md (in progress) and docs/other/orchestration-optimization-question.md. Build only after the benchmark result exists. Depends on T-0197 (merged) and T-0199 for the conductor text.

## Constraints
Keep it small and one authoritative location per fact. Philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." The solo agent file stays short.
