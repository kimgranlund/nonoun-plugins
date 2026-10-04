---
id: T-0215
title: "Solo operator session agent: tiers S, M, L as the default lane for small and medium tickets"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A declared session agent, `solo`, delivers one ticket end to end in a single session, with tiers S, M and L, and the lane script names `solo` as the default for size S and M tickets.

## Intent
- Do: add agents/solo.md (session agent, not a run.sh role, like conductor and messenger) and its generated Codex agent; define three tiers by ticket size with a short typed brief (ticket, files, check commands, done criterion); extend the lane script (steps.py lane, T-0197) to output solo, lean or full with a reason, solo as the default for S and M; require one independent batched verifier at the end for tiers M and L on a different model family (none for S, as /fix today); extend check.py to cover the agent file and Codex mapping with a negative control; conductor.md names the lane choice (reconcile with T-0199, do not duplicate). Model and effort per tier, decided by the user 2026-10-04: solo S = Sonnet low, solo M = Sonnet xhigh, solo L = Opus xhigh. Tier effort is a launch parameter, so the planner decides where the table lives (agent front matter pins only a model, as messenger does; per-tier effort needs a launch flag or table entry); if it lands in run.sh or models.json, satisfy the T-0185 rule (a new eval file in .sdlc/evals/ plus scripts/evals.py lock, citing the benchmark result), and keep scripts/check.py agreement and level-rubric in step. Codex tiers, decided by the user 2026-10-04: solo S = gpt-6.1-sol low, solo M = gpt-6.1-sol high, solo L = gpt-6.1-sol xhigh, in adapters/codex/models.json (use the model id spelled there for sol), generated through codex_roles.py with generate --check green; the same T-0185 eval rule applies to that table change.
- Non-goals: removing the lean or full chain; changing any existing model default without an eval; a version bump, tag, push, or publish.
- Done when: the agent file, mapping, lane output and check exist, an independent verifier passed, one live run per host shows a size-M ticket delivered by solo with a batched verifier, and the lane output is recorded.

## Context
User decision 2026-10-04 after "if an orchestration-based system cannot compete with a basic single-session agent ... we have some really big problems". Evidence to read first: docs/validation/solo-vs-lean-benchmark-2026-10-04.md (in progress) and docs/other/orchestration-optimization-question.md. User decision 2026-10-04 (course correction): build NOW, do not wait for the benchmark to finish; solo becomes the default lane for S and M. Priority P1. Depends on T-0197 (merged); reconcile conductor text with T-0199 when it lands, do not block on it.

## Constraints
Keep it small and one authoritative location per fact. Philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." The solo agent file stays short.

## Closed

2026-10-04: Built via one handwritten L3 step plus one L2 docs fix step; L3 branch verifier found stale lane docs, narrow L2 verifier then passed; no live run (T-0216 is the solo live proof); no filer under burn-down.
