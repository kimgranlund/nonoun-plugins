---
id: T-0230
title: "fanout report says 'tier S: sonnet low' on a Codex run, and its gate can run 0 tests"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The fanout report names the backend's real model for a solo lane (gpt-6.1-sol on Codex, not Sonnet), and a fanout gate that runs zero tests is flagged instead of passing silently.

## Intent
- Do: (1) in fanout.py's report line for a solo lane, print the model and effort for the lane's backend (SDLC_BACKEND=codex gives the Codex tier from adapters/codex/models.json, claude gives the Claude tier), with a selftest that covers both. (2) when a lane gate command is a test run (the default gates), detect the 'ran 0 tests' case (unittest 'Ran 0 tests', pytest 'no tests ran', exit codes 5) and report it as gate vacuous: refuse to merge unless --allow-empty-gate is passed, with a positive and a negative control.
- Non-goals: model or effort defaults; Codex metering (cost is null by design); a version bump, tag, push, or publish.
- Done when: both are tested with negative controls and an independent verifier passed with an overall pass. Size S, solo lane, P2.

## Context
Found by the overnight Codex fanout live run (docs/reports/codex-fanout-live-run.md): the report said 'tier S: sonnet low' on a Codex run (display defect) and the gate ran 0 tests because the fixture's tests/ was not a package (vacuous gate passed). Goes in 0.20.9 or later; do not start before 0.20.8 ships. Philosophy: "Done is better than perfect."

## Constraints
No em dashes.

## Closed

2026-10-05: fanout.py report names the real solo model per backend (solo_model_label, Codex from models.json) and a vacuous gate stops the merge unless --allow-empty-gate; case 19 in the fanout selftest covers both with controls (the refusal case failed before an anchor fix); fanout and steps selftests pass; the batched wave-b verifier reads the diff.
