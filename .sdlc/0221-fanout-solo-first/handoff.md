---
id: T-0221
title: "fanout.py runs each lane by steps.py lane: solo for S and M, chain for full, with a lane cap and stagger"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py` runs each ticket by the lane `steps.py lane` picks: solo for size S and M, the headless /chain for the rest, with a lane cap, a stagger, and an overlap refusal, so a fanout is solo-first by default.

## Intent
- Do: per ticket in its lane worktree run `steps.py lane`, start `solo` at the tier's model and effort (Claude `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`, Codex `codex_exec.py solo L1|L2|L3`), require one independent batched verifier for tier M and L before merging, keep the conductor chain for full, add `--lane`, `--max-lanes` (default 4, above 16 needs `--yes-many`), `--stagger` (default 20 s), `--allow-overlap`; print each ticket's lane in the plan and the report; selftest, check.py guard item 24, docs, and a live proof.
- Non-goals: any model or effort default change; a version bump, tag, push, or publish; building the supervisor or board work.
- Done when: selftest and check.sh pass, an independent verifier passed, the live record docs/validation/fanout-solo-live-run.md exists, and the branch is merged into main.

## Context
User decision 2026-10-05: fanout should follow the same solo-first default as the conductor. Evidence: docs/validation/solo-vs-lean-benchmark-2026-10-04.md (solo about $1 and 6 minutes per task; the chain about 10 times the cost). Burn-down rules: one handwritten step, one verifier, no planner.

## Constraints
Keep `--driver CMD` overriding everything for selftests. Do not touch the limits agent's worktree. No em dashes.
