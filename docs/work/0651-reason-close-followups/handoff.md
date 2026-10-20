---
id: T-0651
title: "A reason close routes follow-ups like a verified close"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket closed with `--reason` keeps its follow-ups: the verifier `## Notes` items and the handoff `## Follow-ups` bullets reach NOTES.md or a ticket exactly as on a verified close, instead of being folded into the Outcome verdict line or lost.

## Intent
- Do: (1) In `cmd_close` (`plugins/sdlc-lite/scripts/tickets.py`), the `--reason` route collects the same follow-up items as the default route (each gated verifier's newest `## Notes` lines via `results.notes_lines`, task level last) plus the handoff body's `## Follow-ups` bullets, appends every item not filed as a ticket to NOTES.md through `append_notes`, and writes one `- Follow-up:` Outcome line per item. (2) `--reason` combines with `--dry-run`, `--ticket N` and `--expect DIGEST` (same digest rules as the default route), so the one `decide:` item worth a ticket can be filed. (3) `close_reason` in `plugins/sdlc-lite/scripts/fanout.py` stops appending `; verifier notes: ...` to the reason, since close now files them; the router text step 4 (`ROUTER_TEMPLATE`, `tickets.py` around line 2601) and the usage text (line 103) and the `--reason` help (line 8557) say a reason close files follow-ups to NOTES.md.
- Non-goals: a `--defer` flag or a forced per-item decision for each `decide:` item; the Lessons line (T-0652); the roadmap follow-ups register (T-0653); deriving the reason's lane (T-0670).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #13, ui-kit-neue audit 2026-10-20. This ticket is part (a) of #13 (reason close drops follow-ups); parts (b) and (c) are T-0652 and T-0653.
- ui-kit-neue: 87 of 90 closed handoffs carry `verdict: closed by reason`; 55 verifier `note:`/`decide:` items sit inside 43 Outcome verdict lines; 12 follow-up bullets exist only in three closed handoffs.
- The full chain lane closes with a reason when there is no filer: `close_reason` at `plugins/sdlc-lite/scripts/fanout.py:951`, the `delivered by the full chain lane; no filer by default (lean records)` text at `plugins/sdlc-lite/scripts/fanout.py:961`, verifier notes squeezed into the reason at the call site `plugins/sdlc-lite/scripts/fanout.py:1727-1729`, selftest case 15 at `plugins/sdlc-lite/scripts/fanout.py:3909-3919` (the last expect asserts `verifier notes:` rides in the reason; change it with the behavior).
- `plugins/sdlc-lite/scripts/tickets.py:101-104` (usage), the `cmd_close` docstring at `plugins/sdlc-lite/scripts/tickets.py:3277` and the `--reason` help at `plugins/sdlc-lite/scripts/tickets.py:8557` say a reason close "files no follow-ups"; `plugins/sdlc-lite/scripts/tickets.py:3351-3354` refuses `--reason` with `--dry-run`, `--skip`, `--expect` or `--ticket`; the reason branch writes at `plugins/sdlc-lite/scripts/tickets.py:3489-3515` and returns `no follow-ups filed` (line 3514).
- The verified route's items and NOTES.md writer: `gated_verifiers` (`tickets.py:3182`), `append_notes` (`tickets.py:3156`), `follow_tag` (`tickets.py:3150`, tags `fix-now`, `decide`, `note`; untagged is decide), `outcome_section` follow lines (`tickets.py:3249`).
- Router: `.sdlc/AGENTS.md:81` (generated from `ROUTER_TEMPLATE` at `plugins/sdlc-lite/scripts/tickets.py:2683`, step 4 at line 2601) documents `--reason` only for "work already done by another ticket".

## Constraints
A reason close still skips the verdict gate and the filer, and still refuses an empty reason and an unmerged `on main`/`landed` claim (`landing_claim_problem`). A reason close with no verifier result and no `## Follow-ups` section writes the same Outcome as today. The verified and filer routes are unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: a ticket with a verifier result whose `## Notes` holds `- note: a` and `- decide: b` and a handoff `## Follow-ups` bullet `- note: c`, closed with `--reason "x"`, appends three items to NOTES.md and three `- Follow-up:` Outcome lines. The case fails with the change reverted.
2. The same selftest covers `close --reason x --dry-run` printing `expect <digest>` and `close --reason x --ticket 2 --expect <digest>` filing item 2 as a ticket; with the change reverted the combination refuses with `--reason files no follow-ups`.
3. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and case 15 asserts the close reason no longer carries `verifier notes:`.
4. `grep -n 'no follow-ups' plugins/sdlc-lite/scripts/tickets.py` finds no reason-close claim in the usage text, the `--reason` help or the router step (selftest strings excepted).
5. `git diff --check` exits 0.
