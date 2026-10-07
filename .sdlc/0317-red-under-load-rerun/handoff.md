---
id: T-0317
title: "Verifier policy: a browser-test red under measured load re-runs once alone before it counts"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier does not fail a ticket for a browser-test red that only appears under machine load: it re-runs that test once, alone, before the red counts.

## Intent
- Do: Approved by the user on 2026-10-06 (AskUserQuestion: "Approve, once, alone"). Add the rule to the verifier flow: when a browser or timing-sensitive test fails and the machine load at the time of the run (recorded as the `uptime` line in the verifier's evidence) was above the stop line (default 14, one config value shared with gate_lock.py), re-run only that test once with `gate_lock.py run --slots 1`; green alone is recorded as a `load flake` with both loads and does not fail the criterion; red alone stays a failure. Put the rule in the verifier agent body and the generated per-level agents, the verify skill and the level rubric text, and record the load in `runs.jsonl` for verifier runs (field `load1`). Add a small helper `scripts/load_gate.py` (`load_gate.py status` prints load1 and `over|ok`) used by the verifier text and by T-0306's detect rules.
- Non-goals: skipping or weakening any check; a retry of unit-test failures that are red in isolation; any model or effort change; retrying more than once.
- Done when:
  - `load_gate.py selftest` passes: above the line prints `over`, below prints `ok`, the line is read from one config value (observed).
  - A verifier fixture where a test fails at base load and passes alone at high load records `load flake` and passes the criterion; a test red alone fails the criterion (both observed).
  - A failure at normal load is never retried (observed negative control).
  - `check.py`, `codex_roles.py generate --check`, `claude_roles.py generate --check` (if present) and `tickets.py check` pass.

## Context
Evidence: maison's only flake of its run happened at load 20: a popover spec was red in the full gate and green alone (root-cause report, .sdlc/root-cause-2026-10-06.md in ui-kit-maison). The `flaky-gates` skill describes the method (red under load versus green in isolation). Related: gate_lock.py (T-0303) and the load stop line in the conductor text.

## Constraints
No em dashes. No change to any model or effort value. No push, tag or publish. Independent verifier; positive case and observed negative control.
