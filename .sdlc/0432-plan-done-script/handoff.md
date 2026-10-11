---
id: T-0432
title: "plan_done.py: the condition a /goal stop hook evaluates"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0431]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Ticket B of the design: `plan_done.py <plan-doc>` exits 0 only when every step ticket is closed with an independent verifier pass, no criterion is held or deferred, and each measure reads on the right side of its target.

## Intent
- Do: build exactly row B of section 8 and the truth table of section 4.2: new `plugins/sdlc-lite/scripts/plan_done.py` (it imports plan_doc.py from ticket A), `check.sh` and `check.py` wiring, one paragraph in docs/references/sdlc-internals.md. It prints what is open and why; `stop` and `replan` second-call refusal per section 4.
- Non-goals: the skills; any change to dispatch.py, steps.py, fanout.py, tickets.py or results.py.
- Done when:
  - `plan_done.py selftest` runs one case per row and per control of section 4.2, each observed failing first; the unstarted goal 002 plan exits 1 and lists every step open; a second `replan` refuses and writes the stop record.
  - plan_done.py selftest, check.py, check.sh and tickets.py check pass.

## Context
Maintainer approved building T-0410 on 2026-10-10 (the plan-doc workflow: plan with a session, then tell a smaller faster model `/goal complete build and verify <plan-doc.md>`). Design: docs/specs/sdlc-lite/plan-doc-executor.md (sections 3 to 8). Defaults taken from its section 10: the driver for the first run is Sonnet high, Haiku 5.5 is not added as a worker row, an L1 step has no independent verifier by default.

## Constraints
No em or en dashes. No push or publish. No model, effort, levels.json or models.json change. The design is the contract; if it is wrong or silent, stop and report a plan defect. One writer at a time on check.py and check.sh: this ticket runs in the same lane as its predecessors. Close-first: run the Done-when checks once, fix what fails, report.

verifier: L3

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/plan_done.py selftest` exits 0 and prints one `ok: plan_done: ...` case per truth-table row and control of section 4.2 (C1 to C5, the stop row, `--records-only` exit 3, plan defect exit 2, the unstarted plan, the replan cap) and `plan_done selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/plan_done.py selftest` prints `ok: plan_done: C1 a step ticket at status ready exits 1 naming that step`, and its all-green fixture exits 0 and prints `plan done`; a fixture with any one condition changed does not exit 0.
- `python3 plugins/sdlc-lite/scripts/plan_done.py selftest` prints `ok: plan_done: unstarted lists every step open` and `ok: plan_done: a second replan refuses (exit 2), prints replan cap reached: stopped and writes the stop record`.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 (item 50 names plan_done.py and its negative controls).
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0 and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
- `git diff --name-only 00e983b2d9972d6e2d686452d97dd326385bbb48` lists no dispatch.py, steps.py, fanout.py, tickets.py or results.py, and `git grep -nP '[\x{2013}\x{2014}]' -- plugins/sdlc-lite/scripts/plan_done.py` prints nothing.
