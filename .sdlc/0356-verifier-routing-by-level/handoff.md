---
id: T-0356
title: "Route the L3 Fable verifier to L4, L5, merge and security tickets only; replay T-0333 on L2 first"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The L3 Fable verifier runs only for L4, L5, merge and security tickets; L1 and L2 tickets use the L2 Sonnet verifier.

## Intent
- Do: (1) Replay the 12 T-0333 verifications with verifier L2 (sonnet, high) in a throwaway tree and compare with the recorded L3 verdicts, including the 3 true fails (T-0334 to T-0336); budget about $5 to $10. (2) Add maison and agent-ui tickets to the replay only if the sdlc-lite replay is clean. (3) If L2 catches every recorded fail with no new false fail, change the routing in the level rubric and steps.py or adapters/claude/levels.json, lock an eval with evals.py, and regenerate agents. Stop and report before step 3 if the replay misses a fail.
- Non-goals: Changing the model or effort of any row without the replay result and the user's go-ahead on step 3.
- Done when:
  - A dated report in docs/reports/ with the per-ticket L2 versus L3 comparison.
  - If routing changes: eval record locked, generated agents and Codex TOML current, check.sh passes.

## Context
Replay done (docs/reports/2026-10-07-verifier-l2-replay.md, uncommitted in main; commit it with this ticket): L2 matched L3 on 41 of 43 criteria, missed T0280-2 (literal label match), one false fail; $6.19 vs about $36.56. The user approved shipping on 2026-10-07: verifier L3 only for L4, L5, merge and security tickets, plus any ticket with a criterion that pins an exact label or string; L1 and L2 tickets use verifier L2. Find where verifier level is chosen (steps.py lane/split, the level rubric, conductor.md and the verify skill) and make that the rule, with a selftest positive and negative control. No levels.json model or effort row changes.
Fleet cost analysis of 2026-10-07 (all-time deduped run records, five repos): verifier L3 Fable $1,291 over 198 runs (about $6.5 each) versus verifier L2 Sonnet about $0.50 each; solo L2 Sonnet xhigh about $406 ($3.31 to $5.53 per run). The user approved these four proposals on 2026-10-07.

## Constraints
Model and effort defaults are the user's decision: the user approved the replay and the proposal, step 3 reports before shipping. No em or en dashes.
