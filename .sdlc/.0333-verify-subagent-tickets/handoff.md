---
id: T-0333
title: "Independent verification of the sub-agent mode tickets that closed with no verifier verdict"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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
0.21.0 (v0.21.0, 027da15a) shipped with these tickets closed on the solo lane and no verdict file (docs/reports/2026-10-06-release-0-21-0.md lists them). Same pattern as T-0319.

## Constraints
Read-only on plugin code. No em or en dashes. No push or publish.

## Acceptance criteria
- A1: twelve verdict files exist, one per ticket, each with a `## Verdict` section holding `pass` or `fail`: `for t in T-0275 T-0279 T-0280 T-0284 T-0286 T-0326 T-0327 T-0328 T-0329 T-0330 T-0331 T-0332; do test "$(sed -n '/^## Verdict$/{n;p;}' .sdlc/verify-subagent/$t.md | grep -c -x -E 'pass|fail')" -eq 1 || echo "BAD $t"; done` prints nothing.
- A2: `.sdlc/verify-subagent/summary.md` lists each verdict, and each row agrees with its ticket file: `for t in T-0275 T-0279 T-0280 T-0284 T-0286 T-0326 T-0327 T-0328 T-0329 T-0330 T-0331 T-0332; do v=$(sed -n '/^## Verdict$/{n;p;}' .sdlc/verify-subagent/$t.md); grep -q "^| $t | $v |" .sdlc/verify-subagent/summary.md || echo "BAD $t"; done` prints nothing.
- A3: each verdict file holds its ticket's criteria lines verbatim from the batch verifier result, and each fail carries a one-line root cause; the criteria lines in a file are exactly the `- Tnnnn-` lines of the batch result named in it (spot check `.sdlc/verify-subagent/T-0331.md` against `.sdlc/verify-subagent/cost-b/verifier-L3.md`), and every file with `fail` has a `## Root cause` section.
- A4: every fail has a filed ticket: each ticket named under `## Filed` of a fail verdict exists as `.sdlc/03NN-*/handoff.md` with a filled body (T-0334, T-0335, T-0336), and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
- A5: the verifiers were independent and ran as sub-agents through dispatch.py: each `.sdlc/verify-subagent/<batch>/runs.jsonl` has one `role verifier` line with `transport subagent`, `model fable`, `shared_with_builder` false, and the builders were sonnet (`.sdlc/.0284-solo-subagent/runs.jsonl`).
- A6 (guard): `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `git diff --name-only HEAD -- plugins` prints nothing, and `grep -rn -P '\x{2014}|\x{2013}' .sdlc/verify-subagent .sdlc/.0334-skills-record-transcript-flag .sdlc/.0335-cost-basis-label-drift .sdlc/.0336-l3-verifier-row-outside-band` finds nothing.

## Closed

2026-10-06: 12 verdicts recorded in .sdlc/verify-subagent/summary.md (9 pass, 3 fail filed as T-0334 to T-0336)
