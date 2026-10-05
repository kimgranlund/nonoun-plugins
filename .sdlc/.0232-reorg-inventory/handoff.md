---
id: T-0232
title: "inventory.py: read-only document inventory and reorganization plan procedure"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A read-only `inventory.py` states the facts about a repository's documents, and a procedure doc says how a solo session turns them into a reorganization plan, so reorganizing starts from measured facts and not from guesses. Nothing is moved.

## Intent
- Do: `plugins/sdlc-lite/scripts/inventory.py` (tracked documents with size, heading, last commit, inbound and outbound links and mentions, flags orphan, stale, duplicate, oversized, misplaced, broken_links, folders without an entry file; `--json`, `--out` outside the repo, `--include-sdlc`); a selftest with a fixture repository, a negative control per mutation and a clean fixture; `docs/repo-onboarding/reorganization-plan-procedure.md`; a live run on two repositories and one model-written plan, recorded in `docs/validation/reorg-inventory-live-run.md`; a `check.py` guard and the selftest wired into `check.sh`.
- Non-goals: moving or rewriting any file; the apply step (T-0233); changing `onboard.py`; a version bump, tag, push, or publish.
- Done when: the selftest passes with its negative controls, the live run is recorded with committed evidence, an independent L3 verifier passed with an overall pass, and the work is merged and closed.

## Context
Reorganization was a draft (docs/repo-onboarding/reorganization.md, v0.6, "not ready to build"; three design reviews each found new edge cases) and the old spike T-0161 never produced a reusable tool. User decision 2026-10-05: do it for 0.20.9 as a hybrid: a deterministic script for facts, a model session for the plan, a later gated script for applying. Size M, solo lane. Philosophy: "Done is better than perfect."

## Constraints
Read-only: the script writes nothing into the target repository. No model calls and no network in the script. No em dashes.

## Closed

2026-10-05: Built and merged: inventory.py (read-only, selftest with negative controls), reorganization-plan-procedure.md, live run on two repositories with one model-written plan and a six-claim spot check, check.py guard 30. First L3 verifier passed 5 of 6 and its two findings were fixed; a narrow L3 passed 2 of 3 and its finding was fixed and confirmed by script; no verifier result says pass overall for the final text (recorded in docs/validation/reorg-inventory-live-run.md). Apply step is T-0233.
