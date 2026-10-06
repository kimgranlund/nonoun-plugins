---
id: T-0307
title: "fleet-retro interview template and environment fingerprint"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fixed, short interview template for conductors, so judgment answers arrive in one shape and always carry an environment fingerprint.

## Intent
- Do: Add plugins/sdlc-lite/skills/fleet-retro/interview.md: the exact message a conductor receives. It first asks for the plugin version path in use, claude version, time and a load snapshot; then at most 5 questions (top stalls with cause and what would have prevented them; friction by cost in dollars or minutes; decisions blocked on the user; what the plugin made faster or slower; anything unverified marked [U]). Answer format: one row per finding with symptom, evidence (command or log path), mechanism, cost, [V] or [U], prevention; ranked by cost; at most 7 rows; written to a fixed path `.sdlc/fleet-retro-<date>.md` (max 80 lines); one-line reply with the path and top three. Include the rule: measure only, start no new work, and never edit another repo.
- Non-goals: A collector or detect script; any model or effort change.
- Done when:
  - The file exists, is under 60 lines, has no em dashes, and `check.py` finds the skill folder valid.
  - A dry read-through against the three existing reports shows each of their findings fits one row of the answer format (list any that do not in the ticket notes).
  - It names that counts and costs come from the collector, not from the conductor.

## Context
Decided by the user on 2026-10-06 after three repo root-cause reports (maison, agent-ui, gen-ui-kit, each at root-cause-2026-10-06.md in its repo). Design: a thin skill `/sdlc-lite:fleet-retro` on top of the existing `review-traces` skill: a deterministic collector, mechanical detect rules, a 5-question conductor interview, one cross-repo ranked report, a sampled verifier, then filing through review-traces. Existing pieces to reuse: runs.jsonl dedupe by attempt_id (agent-ui's method), scripts/budget.py cost sums, skills/review-traces/SKILL.md, scripts/footprint.py. Build after the 0.20.11 batch ships; target release 0.21.1.

## Constraints
No model call inside collect or detect. Read-only on every repo it inspects. No em dashes. No change to any model or effort value. No push, tag or publish.
