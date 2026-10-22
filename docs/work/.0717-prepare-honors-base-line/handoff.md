---
id: T-0717
title: "dispatch.py prepare uses the handoff base: line for Base sha"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `base: <sha>` line in the ticket or step handoff (and a written `<artifacts>/base-sha`) sets the brief's Base sha, as prepare's own hint promises, including in a lane whose HEAD moved past its start after a main merge.

## Intent
- Do: Find why `dispatch.py` (the base resolution about line 499 and 3146, the "nothing recorded for this step" hint about line 560) ignores the line in the reported case (`prepare --tree <lane> verifier L3 <handoff>` after a main merge); fix it so the named base wins.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #49 (quoted):

> **Repro**
> 1. Open a fanout lane, then merge main into it (lane HEAD moves past the lane start).
> 2. A worker builds on the new HEAD. Add `base: <new HEAD>` to the ticket handoff (as prepare's own hint says) and/or write `<artifacts>/base-sha`.
> 3. `dispatch.py prepare --tree <lane> verifier L3 <handoff>`.
>
> **Expected**: the brief's Base sha is the named base (the commit the build started from).
>
> **Actual**: prepare prints `nothing recorded for this step: Base sha is the lane start d767131f273d, not its HEAD 7a68a2e6422e; name another with a line 'base: <sha>'` and still emits `Base sha: d767131f...` after the `base:` line and the base-sha file were added. All five verifier dispatches of the ticket carried d767131f, so verifiers diffed the main merge as if it were build scope.
>
> **Evidence**: `.sdlc/runtime/tasks/0039-ts-semantic-systems/verifier-L3{,-2,-3,-4,-5}.dispatch.json` → `base_sha` d767131f on every try.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Root cause: with `prepare --tree <lane>` for a main-checkout handoff, `build_base` read the `base:` line and `base-sha` only from the main checkout's handoff and records dir. A lane worker writes both in the lane's copy (the twin dir at the same repo path), so prepare saw nothing and fell to the lane start. Second path: `ready_review` replaced any base with the ready snapshot's `Lane-Base:` (the `.lane.json` start), even a named one.

Fix (`plugins/sdlc-lite/scripts/dispatch.py`): `build_base` also reads the twin's handoff (and its task handoff) for a `base:` line, and the twin's `base-sha` when it is a valid base of the execution tree (an ancestor of HEAD past the fork floor, so a stale lane record does not displace the lane start). It returns a `named` flag, and `ready_review` keeps a named base over `Lane-Base:`.

Selftest cases added: a lane that merged main after its start, `base:` in the lane handoff copy, then in the lane's `base-sha`, each with `prepare --tree <lane> verifier`; a negative control with nothing in either tree (lane start, "nothing recorded"); a ready ref with `Lane-Base:` and a named base.

Negative control (fix reverted, tests kept), `dispatch.py selftest` exit 1:
- `FAIL: prepare --tree <lane> verifier after a main merge: a base the lane copy of the handoff names wins over the lane start`
- `FAIL: prepare --tree <lane> verifier after a main merge: the lane's base-sha wins over the lane start`
- `FAIL: a ready ref with a Lane-Base: line: a base the handoff names still wins (T-0717)`

Checks: `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0 (PASS); `git diff --check 83a3a4e6` exit 0.

## Outcome

2026-10-22 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 83a3a4e63e21
- Changed: see commits
- Commits: 8e4348e T-0717: dispatch.py prepare uses the handoff base: line for Base sha
- Check: 1 selftest case reproduces the repro, fails with the change reverted: pass
- Check: 2 gate_lock selftest exits 0: pass
- Check: 3 check.py, check-packaging.py, git diff --check: pass
- Check: 4 Conductor note, a named base that is not an ancestor is refused: pass
- Check: 5 Conductor note, ready_review still prefers `Lane-Base:` when no base is named: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:3086-3094: the new ready-ref... -> notes.md
- Follow-up: decide: Red-checkpoint deviation check printed no process deviation: line. -> notes.md
