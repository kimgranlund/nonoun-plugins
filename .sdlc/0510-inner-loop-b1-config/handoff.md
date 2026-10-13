---
id: T-0510
title: "profile: inner-loop, local_gate and full_gate in .sdlc/config: solo_run refuses a full-suite criterion (T-0501 B1)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`.sdlc/config` lines `profile: inner-loop`, `local_gate: <cmd>` and `full_gate: <cmd>` make `solo_run.py run` refuse a criterion that names a full-suite command, and put the local gate in the brief.

## Intent
- Do: parse the three keys in `tickets.py` beside `hash_bound:` (`:272-276`, reader shape `:453`; add `profile(root)` beside `merge_gate_declared`); in `solo_run.py run` (`:111-120`) exit 2 when a `## Acceptance criteria` or `Done when:` span (`results.criterion_spans`) equals a `full_gate:` command, printing the `local_gate:` lines; append `Checks: <local_gate lines>` to the brief when it names none; in `steps.py lint` refuse a `(guard)` equal to a `full_gate:` command with `plan defect: full gate ... owned by the merge gate`. A handoff line `profile: default` opts a ticket out.
- Non-goals: any verifier change; the merge scripts; a default profile.
- Done when: a `solo_run.py selftest` case with `profile: inner-loop`, `local_gate: python3 check.py`, `full_gate: python3 suite.py` and a criterion `python3 suite.py` exits 2 with the local gate named and no record written (red first: today exit 0 and a record). Negative controls: no `profile:` line prints the dispatch JSON; the criterion `python3 check.py` prints it and the prompt holds `Checks: python3 check.py`; `profile: default` prints it. A `steps.py selftest` case: a `(guard)` on the full gate lints with the plan defect, the same plan without the profile lints clean. `check.py` exits 0.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. Evidence: agent-ui runs the full suite 2 to 3 times per ticket (solo checks, verifier, base rerun on a red gate, then the merge), and its tickets T-0075, T-0077 and T-0079 name it in Done when. The 10 to 20 extra minutes is the conductor's figure [U].

## Constraints
No model or effort change. One writer on `tickets.py`.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0 (its T-0510 cases: a full-gate criterion exits 2 naming the local gate with no record; no profile line, a local-gate criterion with `Checks:` in the prompt, and `profile: default` dispatch)
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 (its `(profile)` cases: a `(guard)` on the full gate lints with the plan defect; the same plan without the profile line lints clean)
- [ ] `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0
