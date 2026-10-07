---
id: T-0333
title: "Independent verification of the sub-agent mode tickets that closed with no verifier verdict"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Each of T-0275, T-0279, T-0280, T-0284, T-0286, T-0326, T-0327, T-0328, T-0329, T-0330, T-0331 and T-0332 has an independent verifier verdict (pass or fail with evidence) against its acceptance criteria, on a different model family than the builder, so 0.21.0 does not rest on live evidence alone.

## Intent
- Do: For each ticket, read its closed folder (`.sdlc/.NNNN-*/handoff.md`) and the code it changed on main (v0.21.0), run the checks its criteria name (selftests, `check.py`, grep controls) and record one verdict file per ticket at `.sdlc/verify-subagent/<ticket>.md` with Verdict pass or fail, evidence lines, and for a fail a one-line root cause. Run the verifier as sub-agents via dispatch.py (the new mode is the thing under test) or role verifier L3 through run.sh, and say which you used. Do not fix anything: a fail becomes a new ticket per finding, not a larger one.
- Non-goals: re-deciding model or effort; the account-switch criterion; T-0288.
- Done when:
  - 12 verdict files exist and `.sdlc/verify-subagent/summary.md` lists each verdict (observed).
  - Every fail has a filed ticket; `check.py` and `tickets.py check` pass.

## Context
0.21.0 (v0.21.0, 027da15a) shipped with these tickets closed on the solo lane and no verdict file (docs/reports/release-0.21.0.md lists them). Same pattern as T-0319.

## Constraints
Read-only on plugin code. No em or en dashes. No push or publish.
