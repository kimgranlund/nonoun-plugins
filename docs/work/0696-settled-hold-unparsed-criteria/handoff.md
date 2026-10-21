---
id: T-0696
title: "A settled hold must not pass a result with an unparsed criterion line"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0684]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A verifier result whose `## Criteria` holds a line `results.criteria_states` cannot parse never reads as pass through a settled hold, so a real failure can never land behind `settle-held`.

## Intent
- Do: in `owner_settled_hold` (`plugins/sdlc-lite/scripts/steps.py`, added by T-0684), return not-settled when any `## Criteria` bullet line is not parsed by `results.criteria_states`; apply the same rule wherever `fanout.branch_verdict` reads a settled hold as pass (it should reuse the same helper). Add a selftest case built from the verifier's probe.
- Non-goals: changing `results.criteria_states` or `results.py validate`.
- Done when: the criteria pass.

## Context
Found by the T-0684 verifier: "a Criteria line that `results.criteria_states` cannot parse (for example `- #2 y FAILED no evidence`, no `: fail. Evidence:`) is ignored, so a result with such a line plus a settled `deferred:` hold reads as `pass` (probe returned True, and `results.py validate` accepts the file)." Before T-0684 a held-only fail never landed as pass, so this path is new.

## Constraints
A result whose criteria all parse, with every hold settled, still reads as pass.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a new case: a result with a settled `deferred: conductor` hold plus the line `- #2 y FAILED no evidence` is not settled; the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.

## Outcome
`steps.owner_settled_hold` now returns False when any `## Criteria` bullet line does not match `results.CRITERION_RE`; `fanout.branch_verdict` already calls that helper, so it needed no change. New selftest cases (fully parsed result True, plus `- #2 y FAILED no evidence` False); the False case fails with the guard disabled. `steps.py selftest`, `fanout.py selftest`, `check.py`, `check-packaging.py` and `git diff --check 7f60309a` exit 0.
