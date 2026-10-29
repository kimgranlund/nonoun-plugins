---
id: T-0807
title: "gate_lock lets one repo's full-capacity jobs starve other repos' gates"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`gate_lock.py` admission keeps one repo's large jobs from holding all compute units back to back, so a small queued gate from another repo is admitted within a bounded wait.

## Repro
1. From repo A, queue gate jobs one after another, each with `--need compute_units=<capacity>`.
2. From repo B, queue a gate with the default need.

## Expected
B's gate is admitted within a bounded wait (aging or a per-job cap below capacity).

## Actual
The agent-ui conductor reports merge gates and verifiers waiting 30 min to 2 h while gen-ui-kit jobs held 16 compute units back to back [U]. Its cited log `/tmp/claude-501/qm-dogfood-2348.log` does not contain the quoted timeout line, so the wait is unmeasured. The collector's longest agent-ui verifier attempt was 148.7 min (`.sdlc/runtime/tasks/fleet-retro-2026-10-29/agent-ui.json :: attempts.by_role.verifier.max_min`).

## Context
- Fleet retro row 2: `docs/reports/2026-10-29-fleet-retro.md`.
- `plugins/sdlc-lite/scripts/gate_lock.py` admission and policy (`capacity`, `default_need`).
- Filed by the user's choice although the row failed rubric gate G3; measure the wait first (gate_lock ledger or status rows) and close as not reproduced if it does not starve.

## Constraints
- Red check: a `gate_lock.py` selftest where back-to-back full-capacity jobs from one repo keep a default-need job queued past the bound; it fails before the fix and passes after.
- outcome metric: longest queued wait for a default-need gate under contention, before: unmeasured (reported 30 to 120 min).

## Outcome

2026-10-29 · lane: solo L2 · verdict: closed by reason (already fixed: gate_lock round robin across repos (T-0409) admits another repo's default-need gate after at most one more busy-repo grant; selftest case_rr and scratch sims confirm. Remaining waits come from the load cap (max_load 16 on 20 CPUs), a policy setting, not admission order) · verifier: none · base: ff69a090c740
- Changed: see commits
- Commits: 9db6d05 T-0807: record lane T-0807-t0807
