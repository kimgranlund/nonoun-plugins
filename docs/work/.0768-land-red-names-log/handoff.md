---
id: T-0768
title: "fanout.py land names the gate log and failing line on red"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #76 reports no longer happens (title: fanout.py land names the gate log and failing line on red).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/fanout.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #76 (quoted):

> **Observed:** a failed land printed `red: { [ "$(shasum package-lock.json)" = ... ] || ...` (the whole first gate command) and nothing else. Finding the cause meant locating `<lanes>/logs/gate-<lane>-T-NNNN-1-a1.log` by hand and grepping it for `FAIL  project checks (npm run check:standards)`.
>
> **Root cause:** `scripts/fanout.py:1927` returns `red: {gate} rc={rc}` although `glog` is in scope; the sync path already prints `(log {glog})` (`fanout.py:3483`).
>
> **Proposed fix:** append `(log <glog>)` and the last failing script line found in the log.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Reproduced on main (baac64db): the gate red path in `merge_gate_close` returned `red: {gate} rc={rc}` with `glog` in scope. Fixed in `plugins/sdlc-lite/scripts/fanout.py`: the line is now `red: <gate, whitespace collapsed> rc=<n> (log <glog>): <last failure line>` (new `gate_fail_line`: last log line matching FAIL, Error, error:, not ok, or a non-zero exit/rc; log path alone when none), still one line. `references/land.md` and the fanout docstring describe it.

- Tests: case 23 gained two land cases (a gate printing `FAIL  project checks (npm run check:standards)` before failing; a gate with no failing line), and the two existing exact-match `red: false rc=1` assertions (external red gate) became prefix matches.
- Negative control: in a scratch copy of the plugin with the one `return` reverted, `fanout.py selftest` fails with `case 23 land (T-0768): a red land names the gate log and the failing line, got 'red: echo "FAIL project checks (npm run check:standards)"; echo "tail noise"; false rc=1'`.
- Checks: `fanout.py selftest` via gate_lock exit 0 (PASS), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check baac64db` exit 0.

### Outcome addendum (verifier fail, widened to the traces reader)
`traces/sources/fanout.py` `RED_RE` was anchored at `rc=<n>$`, so `_place_rc` and the `integration-reset` detector (via `hygiene._outcome_signal`) went silent on the new line. It is now `^red: (.*?) rc=(-?\d+)(?: \(log [^)]*\).*)?$` (lazy gate group, optional ` (log <path>)` tail with any failure line or hint), docstrings in `sources/fanout.py` and `detectors/hygiene.py` updated. A grep of `plugins/sdlc-lite` (scripts, hooks, adapters) found no other reader of `red:` lines; `RED_RE` is used only in those two files.
- Test: new traces case `fanout: a land red line with the log path and failing line still places its rc (T-0768)`, including a gate containing ` rc=5` and a failure line containing `rc=3`. Negative control: with the old regex in a scratch copy the case fails (the failure-line `rc=3` is placed on alpha's gate and beta's rc is lost).
- Checks: `traces.py selftest` PASS and `fanout.py selftest` PASS via gate_lock, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check baac64db` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: baac64dbd9c7
- Changed: see commits
- Commits: 571fb74 T-0768: traces red reader accepts the land line's log and failure tail; 778c7e8 T-0768: fanout land red names the gate log and failing line
- Check: 1 A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it...: pass
- Check: 2 selftest via gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff --chec...: pass
- Follow-up: fix-now: plugins/sdlc-lite/scripts/fanout.py:82 the land docstring still... -> notes.md
- Follow-up: fix-now: docs/references/sdlc-internals.md:190 still says a red gate appends... -> notes.md
- Follow-up: fix-now: plugins/sdlc-lite/scripts/fanout.py:1976 glog.read_text.. -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/traces/sources/fanout.py:39 the tail... -> notes.md
