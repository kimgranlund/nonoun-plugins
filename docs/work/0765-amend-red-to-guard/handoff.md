---
id: T-0765
title: "steps.py amend and swap can retag a red-at-base criterion to guard"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #73 reports no longer happens (title: steps.py amend and swap can retag a red-at-base criterion to guard).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/steps.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #73 (quoted):

> **Observed (0.35.0):** a builder blocked with `plan defect:` proving a `(red)` criterion was already green at base, and proposed `amend old:`/`amend new:` retagging it `(guard)`. `steps.py amend` refused: "the new text must carry (red) in its leading tags exactly when the old criterion line does". The task's one replan was already spent, so the docs route to "ask the user" and also say "never edit the criterion by hand". Happened twice in one day (two tickets); the conductor hand-edited the step handoff both times.
>
> **Root cause:** `check_new_text` refuses any change to the `(red)` tag (`scripts/steps.py:4246`); `swap` shares it. `amend` also refuses after `replan_used` (`steps.py:4376`, `:4441`). #17 and #62 only prevent red-at-base criteria at planning time; there is no recovery path at build time.
>
> **Proposed fix:** allow amend/swap to drop `(red)` to `(guard)` when the redck/checkpoint record proves the span was green at base (validated by the usual guard run), and do not count that retag against the replan budget.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Reproduced on main (dc548c5b): with the new selftest cases and no fix, `steps.py selftest` printed `steps selftest: FAIL` with `(amend) T-0765: a (red) line proven green at base retags to (guard) after the replan is spent, records retag applied:, and a rerun is already applied` and `swap: T-0765: a (red) line proven green at base retags to (guard)` (refused: "the new text must carry (red) in its leading tags exactly when the old criterion line does").
- Fix in `plugins/sdlc-lite/scripts/steps.py`: `red_retag` (the new text is the `(red)` line with `(red)` swapped for `(guard)`, nothing else) and `red_green_at_base` (the latest `red-checkpoint.jsonl` control bound to the line and each span is pre-edit, green, at the base sha). `check_new_text` skips only its two tag-parity checks for a proven retag. `amend` lets a proven retag past the replan cap, runs it as a `(guard)`, and records `retag applied:` (not `amend applied:`, so `replan_used` stays None). `swap` shares the exception. Already-applied detection in amend, swap and `amend_applied` now also holds when the new line still carries the old span.
- Negative controls (selftest): no control, a red control, a retrospective green control, a control for another span, and a control for another line text each refuse with "green at base" and write nothing; swap refuses a retag without a control.
- Docs: `skills/chain/references/step-rules.md` item 10, `docs/specs/sdlc-lite/cost-control.md`, `docs/references/sdlc-internals.md`, and the steps.py usage text.
- Checks: `gate_lock.py run ... steps.py selftest` exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check dc548c5b` exit 0.
- Open: `steps.py next` still prints `replan` when the replan is spent, even for a retag pair (next is T-0776's scope); the step-rules text tells the conductor to run `steps.py amend` first in that case.
