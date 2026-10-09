---
id: T-0412
title: "record leaves the attempt running when no result exists yet"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-09
claimed_by: claude 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
record leaves the attempt running when no result exists yet. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 2 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: bug, size L2, candidate 2 of the spec (section 2). Depends on: none; first of the three `dispatch.py` steps, which run in one lane in the order 2, 3, 4.

In `record` (`plugins/sdlc-lite/scripts/dispatch.py:865-991`): when the result file is missing or empty, stdin is empty or whitespace, and no transcript yields a result (the branch that today reaches `text, error = '', ... 'no result file at ...'` at `dispatch.py:927` with empty `said`), print `dispatch.py: no result yet at <path>; the attempt stays running: record again once the <role> writes it, or pass --no-result to close it failed` to stderr and return 2 without writing `<stem>.log`, a `runs.jsonl` line, a `.limit` marker, or a delivery, and without calling `close`. Add `record --no-result` (a store-true flag passed into `record` as `no_result=False`), which keeps today's path exactly: exit 1, the error text `no result file at <path> (the <role> must write its report there before it ends)`, attempt `failed`. Stdin holding error text and a transcript that stopped on `max_tokens` keep closing the attempt `failed` as now. Update the docstring's `failed` paragraph (`dispatch.py:90-92`) and the `record` usage line (`dispatch.py:5`).

Contract dependents (`git grep -n "no result file at\|returned no result" -- plugins`): the selftest case "a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line" (`dispatch.py:1994-1996`) records with no body; make it pass `--no-result` and keep its label. Any other selftest case that records with no file and no stdin and expects exit 1 gets `--no-result` the same way (the selftest run finds them). `run.sh:667` is the Codex runner's own failure and stays: it waits for its process, so it has no early-record window. `docs/references/sdlc-internals.md`: update only if it states that record fails with no result file. Add selftest cases with exactly these labels: `record with no result file and empty stdin exits 2 and leaves the attempt running`, `record after the late result file appears completes the attempt`, `record --no-result closes an attempt with no result file as failed, exit 1`, `negative control: error text on stdin with no result file still closes the attempt failed`. Write each label as one string literal on one line, so the (red) source grep finds it. Validation scope: `dispatch.py selftest` (about 130 s on this host under load).

## Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`

## Done when
- (red) `grep -qF 'record with no result file and empty stdin exits 2 and leaves the attempt running' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'record with no result file and empty stdin exits 2 and leaves the attempt running' 'record after the late result file appears completes the attempt' 'record --no-result closes an attempt with no result file as failed, exit 1' 'negative control: error text on stdin with no result file still closes the attempt failed'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py record --help | grep -qF -- '--no-result'`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line'`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e docs/references/sdlc-internals.md)"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
- `dispatch.py record` with no result file, empty stdin, and no transcript result prints `no result yet at <path>; the attempt stays running: ...` to stderr, exits 2, leaves the attempt `running`, and writes no `.log`, `runs.jsonl` line, `.limit` marker, or delivery.
- After the result file appears, a second `record` completes the attempt (exit 0, one `runs.jsonl` line).
- `record --no-result` with nothing to record keeps the old path: exit 1, error `no result file at <path> (the <role> must write its report there before it ends)`, attempt `failed`.
- Error text on stdin with no result file still closes the attempt `failed` (exit 1).
- The docstring `failed` paragraph and the `record` usage line describe the new behavior; only `dispatch.py` (and `docs/references/sdlc-internals.md`, unchanged) is in scope.
- `dispatch.py selftest` passes and prints `ok:` for the four new labels and for the T-0330 verifier label.
