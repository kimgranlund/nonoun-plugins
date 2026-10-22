---
id: T-0737
title: "A carried close needs a commit that names the ticket"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py land` closes a ticket as "commits carried by merge <sha>" (T-0721) only when the carried merge brings at least one commit whose subject names that ticket id (`T-NNNN`); otherwise it keeps the old `no changes` result and leaves the ticket open.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py` (`carrying_merge` / the carried branch, about line 2551), require a commit in the merge's second-parent range whose subject contains the ticket id. Add a selftest case: two tickets in one lane where only A committed; landing B stays `no changes` and B stays open.
- Non-goals: changing how solo L2/L3 tickets require their verifier.
- Done when: the criteria pass.

## Context
T-0721 verifier-L2 (landed):
- plugins/sdlc-lite/scripts/fanout.py:2551: decide: a solo L1 or full-lane ticket that committed nothing itself, sharing a lane with a landed sibling, now closes `commits carried by merge <sha>` with no verifier check (land cannot tell its commits from the sibling's). Same trust as a normal L1 or full land, but an empty sibling is closed on the sibling's work. Consider a follow-up ticket if that is not wanted (e.g. require the ticket's folder or commits to appear in the carried merge).

## Acceptance criteria
1. The new `fanout.py` selftest case passes, case 32b (T-0721) still passes, and with the id check removed the new case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`fanout.py land` now closes a ticket as `commits carried by merge <sha>` only when a commit in the carried merge's second-parent range has a subject naming the ticket id (`merge_names_ticket`); otherwise it stays `no changes` and the ticket stays open. New selftest case 32c (two tickets, only T-0001 committed): land B gives `no changes`, T-0002 not done. Case 32b still passes. Negative control: with the id check removed the selftest fails on `case 32c carried none: land A merges, land B stays \`no changes\` and T-0002 stays open, got ... land B rc=0`. Checks: fanout selftest exit 0, check.py exit 0, check-packaging.py exit 0, `git diff --check a65f8caa` exit 0.
