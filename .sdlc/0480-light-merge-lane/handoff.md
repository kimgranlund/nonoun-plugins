---
id: T-0480
title: "Design: a light merge lane with a cadence full gate (from maison, after T-0470)"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
The exact question this spike answers.

## Goal
A written design, with a recommendation, for a light merge lane: self-contained work lands on a targeted gate and the full gate runs on a cadence with a ledger of the merges it covers. The output is `docs/planning/light-merge-lane.md`; no code.

## Intent
- Do: answer the four questions below from the code (`steps.py lane` at `steps.py:3084`, `fanout.py` `--gate` and `land`, `gate_lock.py`, `tickets.py close`), state what a consumer must declare, and name the smallest first build with a red check.
- Non-goals: loosening the full-gate-before-ff rule in any repo (the maison user decides that); wording changes; any build.
- Done when: the design file answers (1) to (4) with a recommendation each, lists what stays project-side, and names the first build ticket.
- Questions from the maison conductor (2026-10-12): (1) expose lane types full and light, with a `steps.py lane` rule that picks light when the diff touches one component folder plus declared registration files; (2) where the "full gate covers merges X..Y" ledger lives (per-ticket `runs.jsonl` or one repo-level file); (3) can `steps.py lane` and `fanout.py land` take a per-lane gate command set instead of one `--gate` list; (4) does a "wave count fixture" owner step (one writer binds shared counts after the lane set is chosen) belong in the plugin or project-side.
- First leanings, unverified: (1) a declared opt-in in `.sdlc/config`, never inferred from the diff alone; (2) one repo-level append-only file, because a cadence run covers many tickets; (3) likely yes as a per-lane override, check how `fanout.py` threads gates; (4) project-side, the plugin cannot know the fixtures; at most it offers an owner-step slot, which T-0472 (deferred to a stage) already half-covers.

## Context
Origin: maison conductor message after the T-0470 report (`docs/reports/2026-10-12-maison-wave-7b-mechanics.md`), floor per merge of a 75 to 90 minute full gate. Related: T-0456 (cheap gates declare a weight), T-0472 (stage-owned deferred criteria), T-0464 (ceremony audit). This design must name its pillar effect: cost and performance up, resilience down unless the cadence gate and ledger are bisect-friendly.

## Constraints
Read-only design. One architect pass; no replan. A repo adopts the light lane only with its owner's written approval.
