---
id: T-0278
title: "dispatch.py record: validate, record, and close a dispatched role"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
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

## Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` prints `dispatch selftest: PASS` and no `FAIL:` line. Its `record parity` cases run a real `run.sh` with a stub `claude` and `record` for builder, verifier, planner, and plan-reviewer, and require the `record` runs.jsonl key set to equal the `run.sh` key set plus the two documented additions `agent_id` (the Done-when line) and `cost_reason` (the Context line, null `cost_usd`), with `transport: subagent`.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest | grep -c '^ok: \(record parity\|steps.py next reads\|order.py reads\)'` prints at least 20, covering key set, header, `steps.py next` output equality (`verify L1` after the builder, `done` after the verifier), and `order.py` equality.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest | grep -c '^ok: \(invalid result\|negative control\)'` prints at least 9: each of missing key section, disallowed first value, and section order exits 3, prints `dispatch.py: <role> result <reason>; see <file>`, keeps the file, the runs.jsonl line, and a failed attempt, and has a negative control where an accept-all validator lets the same file pass.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest | grep -c '^ok: \(a failed sub-agent\|a 429\|no result file\|a later success\|CLI record\)'` prints at least 7: error text with no result exits 1 with status failed, a 429 or session-limit text writes `<role>-<level>.limit` with the `prepare` resume command, and a later success removes it.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest | grep -c '^ok: \(a changed handoff\|strays are reported\|the dispatch tmp prefix\|the outside worktrees\)'` prints 4: stale handoff, strays, and the tmp prefix removal are reported with the exit code unchanged.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints `run selftest: PASS`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `git diff HEAD --name-only -- plugins/sdlc-lite/scripts/results.py plugins/sdlc-lite/scripts/run.sh` prints nothing (no schema change, run.sh untouched).
- `git diff HEAD -- docs plugins .sdlc/0278-dispatch-record | grep '^+' | grep -c "$(printf '\xe2\x80\x94')"` prints 0 (no em dashes), and `git diff HEAD --check` exits 0.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
