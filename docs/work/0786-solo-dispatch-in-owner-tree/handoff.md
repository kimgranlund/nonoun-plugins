---
id: T-0786
title: "The solo dispatch record lives in the tree that owns the solo's records"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A prep solo's dispatch record ends up in the same tree as its report and verifier results (the owner twin, T-0750), so readers need no cross-tree fallback for it.

## Intent
- Do: when `dispatch.py record --agent-id` or `advance` rebinds a prep solo's host record (T-0763), also move or copy `<id>-solo.dispatch.json` (and its attempt file) into the owner twin's records dir. Then decide whether the T-0785 reader fallback in `steps.solo_report` can go; keep it if older lanes need it. Also replace the mtime choice of the newest dispatch record in `steps.solo_report` with order.py's newest rule (the plugin rule: never file mtime).
- Non-goals: other record kinds.
- Done when: the criteria pass.

## Context
T-0785 verifier (2026-10-25): prepare writes the solo dispatch record in main before any lane exists; T-0750 routes later records to the owner twin; T-0785 fixed the reader. The steps.py dispatch-record pick uses mtime (steps.py about 3296-3303), against the order.py rule in plugins/sdlc-lite/AGENTS.md.

## Acceptance criteria
1. A `dispatch.py` selftest case: after `record --agent-id` on a prep solo with a host twin, the dispatch record is in the twin's records dir; with the change reverted it fails (state the FAIL line).
2. A `steps.py` case shows the newest dispatch record is chosen by order.py, not mtime (two records with mtimes reversed against their order).
3. The dispatch and steps selftests through gate_lock exit 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `dispatch.py`: new `solo_dispatch_to_owner`, called in `record`/`advance` right after `rebind_solo_host` (T-0763). It copies `<name>.dispatch.json` (and `<name>.attempt.json` when one exists) into the records dir `owned_records` (T-0750, `wtroot.owner_tree`) names for the ticket; nothing when main owns them. A copy, not a move: record and advance keep reading the original, and `.sdlc/runtime/` is gitignored, so land sees no conflict.
- `steps.py` `solo_report`: the newest solo dispatch record ranks by its attempt_id's row in runs.jsonl (order.py's rule: recorded rows by line, after unrecorded ones by name), never mtime.
- T-0785 reader fallback: kept. Lanes prepped before this change hold their dispatch record only in main, and a twin copy is made only once `record --agent-id` or `advance --agent-id` runs.
- Cases: dispatch `T-0786 record --agent-id on B's prep solo with a host twin puts T-0764-solo.dispatch.json in the twin's records dir`; steps `solo report newest dispatch (T-0786): two records with mtimes reversed against runs.jsonl order`. Negative control (each change reverted): dispatch prints `FAIL: T-0786 record --agent-id on B's prep solo with a host twin puts T-0764-solo.dispatch.json in the twin's records dir ...` and `dispatch selftest: FAIL`; steps prints `steps selftest: FAIL` with the T-0786 case `got (None, 1, False)`.
- Checks: dispatch and steps selftests through gate_lock exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 66f650ed` exit 0.
