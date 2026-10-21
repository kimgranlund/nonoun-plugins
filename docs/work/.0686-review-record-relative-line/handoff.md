---
id: T-0686
title: "record prints a repo-relative Review record line; lint warns on absolute home paths in criteria"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ui-designer review leaves a repo-relative record line the conductor can paste into a ticket handoff, and `steps.py lint` warns on an absolute home path in a criterion, so no tracked record or criterion trips a repo's personal-path gate.

## Intent
- Do: in `record` (`plugins/sdlc-lite/scripts/dispatch.py:1657`), after a ui-designer attempt closes completed (the `print(result)` near line 1793) and its handoff holds `mode: review`, print one more line `- Review record: <result path relative to the git toplevel> (<verdict> at <short HEAD sha of the tree>)`, the verdict being the first value of the result's `## Verdict`. Add a `dispatch.py selftest` case for it and a control: a `mode: plan` ui-designer record prints no such line.
- Do: in `steps.py lint` (`cmd_lint`, `plugins/sdlc-lite/scripts/steps.py:2583`), add an advisory `steps lint: warning: <plan> step <n>: absolute home path in a criterion: <span>` for a criterion line holding `/Users/`, `/home/`, `/var/folders/` or `/private/tmp/` (reuse the pattern of `ABS_PATH_RE`, `plugins/sdlc-lite/scripts/tickets.py:3286`), beside `count_warnings` and `history_warnings`. Add a selftest case and a clean control.
- Do: name the new line in the record paragraph of `docs/references/sdlc-internals.md` (`scripts/dispatch.py` entry).
- Non-goals: writing into the ticket handoff; changing `tickets.py check`.
- Done when: the criteria pass.

## Context
Source: GitHub issue #22 (reopened), ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- The ui-kit-neue review runbook asks for a `Review record:` line in the ticket handoff; `prepare` prints only absolute result paths and no command writes a relative one. The conductor pasted absolute paths, the repo's `check:boundaries` failed the T-0144 verifier on `handoff.md:33: personal path`, and T-0144 and T-0148 were relativized by hand and re-verified. Criteria that grep for `/Users/` tripped the same gate (T-0158, T-0109).
- Confirmed on main: the `Review record:` runbook text is the consumer repo's own; no file under `plugins/sdlc-lite` mentions it. `record` prints the absolute result path on success (`dispatch.py:1793`). `steps.py lint` has no absolute-path warning (`count_warnings` and `history_warnings` near line 1688 are the only criterion warnings).
- Already fixed on main: the `tickets.py check` half of the proposed fix. It warns `<file>:<line>: absolute path in a tracked work record` for an open ticket handoff, notes.md and the gate ledger (T-0662; `tickets.py:1811`, help text near line 185).

## Constraints
The new line and the warning are additive: no exit code changes.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the review-record case and its plan-mode control; the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with the absolute-path warning case and its clean control; the case fails with the change reverted.
3. The existing tickets.py warning still holds: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check <base sha>` exits 0.

## Outcome
- `dispatch.py record`: a completed ui-designer record whose handoff holds `mode: review` prints `- Review record: <repo-relative result> (<verdict> at <short HEAD>)` after the result path (`review_record_line`). Selftest case plus a `mode: plan` control; the case fails with the print removed.
- `steps.py lint`: advisory `absolute home path in a criterion: <span>` warning (`abs_path_warnings`, pattern of `tickets.ABS_PATH_RE`), help text updated. Selftest case plus a repo-relative control; the case fails with the warning unhooked.
- `docs/references/sdlc-internals.md`: the record paragraph names the new line.
- Checks: dispatch.py selftest exit 0, steps.py selftest exit 0, tickets.py selftest exit 0, check.py exit 0, `git diff --check 5b758412` exit 0.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 5b758412231c
- Changed: see commits
- Commits: 8855106 T-0686: record prints a repo-relative Review record line; lint warns on absolute home paths in criteria
- Check: 1 dispatch.py selftest exits 0 with the review-record case and plan-mode control; case fails with c...: pass
- Check: 2 steps.py selftest exits 0 with the absolute-path warning case and clean control; case fails with ...: pass
- Check: 3 tickets.py selftest exits 0: pass
- Check: 4 check.py exits 0: pass
- Check: 5 `git diff --check 5b758412` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/steps.py:1746: ABS_HOME_RE copies the... -> notes.md
