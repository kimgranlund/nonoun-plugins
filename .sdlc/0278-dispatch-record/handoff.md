---
id: T-0278
title: "dispatch.py record: validate, record, and close a dispatched role"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0277]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py record <dispatch.json>` takes the sub-agent result (the file the role wrote, else stdin), validates it with `results.py`, writes the header and `runs.jsonl` line, and closes the attempt.

## Intent
- Do: dispatch.py record: validate, record, and close a dispatched role.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - A valid builder, verifier, and planner result recorded by `record` produce a result file and a `runs.jsonl` line whose key set equals the line `run.sh` writes (a schema-parity selftest), with `transport: subagent` and `agent_id`.
  - An invalid result (missing key section, disallowed first value, section order) exits 3 with the same `dispatch.py: <role> result <reason>; see <file>` line shape and keeps the file and record; each reason has a negative control where an accept-all validator lets it pass.
  - A failed sub-agent (error text, no result) records status failed with exit 1; a 429 or session-limit text writes `<role>-<level>.limit` with the resume command.
  - It reports stale handoff (sha256 changed since prepare), strays (worktrees and branches that appeared), and removes the dispatch tmp prefix; the exit code is unchanged by the last two.
  - `codex-selftest.py` and `lifecycle-selftest.py` still pass; `steps.py next` and `order.py` read a recorded result exactly as they read a run.sh result (a fixture proves `steps.py next` output equal).

## Context
Design section 3. Cost fields are filled by the cost-estimate ticket; here `cost_usd` is null with `cost_reason: subagent usage not priced` until that lands.

## Constraints
No change to `results.py` schema. No em dashes. No push, tag, or publish.
