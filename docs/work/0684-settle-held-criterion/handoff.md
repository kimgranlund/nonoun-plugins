---
id: T-0684
title: "settle a deferred: conductor held criterion so land reads it as pass"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a verifier holds a criterion as `deferred: conductor` (for example "the ui-designer review passes [owner: conductor]"), the conductor can record that it settled it with evidence, and `fanout.py land`, `steps.py open` and `tickets.py close` then read that criterion as pass, with no rewritten criterion and no second verifier.

## Intent
- Do: (1) add `dispatch.py settle-held <verifier result> --by <owner> --evidence <repo-relative path> [--ref <ref>]...` in `plugins/sdlc-lite/scripts/dispatch.py` (subparsers near line 1981): it refuses (exit 2) when the result is not a `fail` whose `## For the next attempt` first line is `deferred: <owner>` naming `--by`, when the evidence path is missing or absolute, or when a review-record evidence file lacks a `## Verdict` of `pass` or `pass-with-notes`; otherwise it appends a `## Settled by owner` section with one `- <ref> <owner>: <evidence> at <sha7>` line per held ref. (2) Make `steps.held_items` (`plugins/sdlc-lite/scripts/steps.py:2776`) treat a ref listed under `## Settled by owner` by its declared owner as pass, and make `branch_verdict` (`plugins/sdlc-lite/scripts/fanout.py:2164`) return `pass` when the newest verifier result is a held-only fail whose held refs are all settled, so land at fanout.py:2425 merges. (3) Document it: a row in the `## Arguments` table of `plugins/sdlc-lite/skills/verify/SKILL.md`, one sentence beside the `verifier fail` outcome in `plugins/sdlc-lite/skills/fanout/references/land.md`, and the settle path in `docs/specs/sdlc-lite/verifier-held-criteria.md` section 5.
- Non-goals: settling a `fail` that is not held, settling an `unmet-dependency` hold, or changing how a verifier decides to hold.
- Done when: the criteria pass.

## Context
Source: GitHub issue #35, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
T-0082: 0082-verifier-L2-2 reported `deferred conductor`; land printed `held conductor: not a defect, settle it in the owner stage`; the conductor read fanout.py to find the rule, rewrote the criterion as a grep and ran 0082-verifier-L2-3. 5 of 15 verifier fails in 0.27 came from "review passes" criteria (0067, 0070, 0073, 0076, 0082).
On main: the held message is at `plugins/sdlc-lite/scripts/fanout.py:2425` in `land_ticket`; `merge_class` reads `held <who>` at `plugins/sdlc-lite/scripts/steps.py:2939`. The only settle path today is a later verifier result with Verdict pass and a `## Settles` list (`results.settled_refs`, `plugins/sdlc-lite/scripts/results.py:265`; `held_items` at steps.py:2776), which needs another verifier run. The held states and owner grammar are in `docs/specs/sdlc-lite/verifier-held-criteria.md`.

## Constraints
A held criterion with no owner settle still blocks land and close as today. `results.py` validation of the verifier result stays green after the section is appended (`## Settled by owner` is an undeclared heading that `structure_error` ignores; confirm it).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new cases: a settle on a `deferred: conductor` result with an existing review record whose Verdict is pass exits 0 and appends the section; `--by` naming another owner, a missing evidence file and a non-held `fail` each exit 2 and leave the file unchanged.
2. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a case where a solo L2 lane whose newest verifier result is a settled `deferred: conductor` fail lands `merged`; the case fails with the change reverted.
3. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a case where `steps.py open` prints nothing for a settled ref.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check 8624f984` exits 0.
