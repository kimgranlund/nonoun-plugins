---
id: T-0229
title: "Solo start has no budget gate, and /agent solo without a ticket is unmetered"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Starting a solo session (conductor Bash start, fanout solo lane, `/agent solo`) checks the ticket's budget first and stops at 80 percent as `run.sh` does for roles, and `/agent solo` without a named ticket still records its cost.

## Intent
- Do: (1) in `solo_run.py` (and fanout's solo start, which goes through it) call the same budget check `run.sh` uses (`budget.py status`, exit 4 at 80 percent, `budget.py ack` to continue) before launching the session, with the same messages and an `--ack` path; a ticket with no budget field is not blocked. (2) `/agent solo` with instructions that name no ticket: have the skill create a small task folder with a `handoff.md` from the instructions (as it already does for the read-only roles) so the wrapper can write a record, or record cost in a documented fallback location that `budget.py` and the board read; pick the smaller. (3) Selftests with negative controls: a ticket seeded past 80 percent refuses to start a solo session and an acked one starts; `/agent solo` leaves a `role solo` record. (4) Update agents/solo.md and docs/maintenance/sdlc-internals.md only where they claim the budget gate counts or stops the default lane. check.py guard with the next free item number.
- Non-goals: model or effort defaults; a version bump, tag, push, or publish.
- Done when: both behaviors are tested with negative controls, a real headless solo start on a throwaway over-budget ticket is refused and an acked one runs (about $3), and an independent verifier passed with an overall pass.

## Context
Found by the post-publish fact-check of release 0.20.7 (findings 7 and 8): metering happens only after a solo session ends, and no stop applies before it starts, so a ticket already over budget still starts solo; the release notes read as if the 80 percent stop applies to the default lane. Size M, solo lane, P1. Goes in 0.20.8. Philosophy: "Done is better than perfect."

## Constraints
Reuse the existing budget code, do not fork it. No em dashes.

## Result
Built on branch solo-budget (1a1d903, record aeb55f1, evidence fix 0776112). `solo_run.py` runs `budget_hold` before it starts a session: at 80 percent of `budget_usd` or more with no ack it exits 4 (`solo_run.py: budget <pct>%: ask the user; budget.py ack`) with no session and no record; no budget, or a task folder with no ticket id, is never blocked. Fanout solo lanes inherit it and stop as `driver failed rc=4 (budget gate: budget.py ack)` (selftest case 18, with a control). `--new-task [slug]` creates a task folder from the brief so `/agent solo` with no ticket still leaves a `role solo` record. `check.py` item 28 guards the phrases with a negative control each. Text updated in agents/solo.md, skills/agent/SKILL.md, skills/fanout/SKILL.md and docs/maintenance/sdlc-internals.md; the three Codex solo agents regenerated (Codex users need `codex_roles.py install <project>`).

## Verification
- Live proof, about $0.25: an over-budget ticket refused, an acked one ran and was recorded ($0.1274), `--new-task` left a record ($0.1215); docs/validation/solo-budget-gate-live-run.md with committed evidence.
- Mutants on disk: gate disabled gives nine FAIL lines in the solo_run selftest and three in fanout case 18.
- Independent L3 verifier (Fable): first pass failed criterion 6 (three file-content claims in the record had no committed file; fixed by committing hello.txt and note.txt and rewording) and criterion 7 (a plan defect: the scope command compared against a moving main; corrected to `main...HEAD`). Narrow L3 re-verification of both: pass (.sdlc/verify-0229-b). Full check.sh, check-packaging.py, generate --check, tickets.py check and the budget, board, solo_run, steps, tickets and fanout selftests pass on the merged branch.

## Limits
One trial of each live step on Claude only; no Codex run (a Codex solo records cost null, so the gate cannot see its spend); the gate reads recorded cost, so one session is not capped while it runs; a full fanout lane and the raw command in solo.md skip the gate and the record; a fanout lane hitting the gate is covered by the selftest only; no model has followed the new /agent solo text yet.

## Closed

2026-10-04: Built and verified on branch solo-budget; merged into local main. Independent L3 passed after one fix round; see the ticket Result and Verification sections.
