---
id: T-0415
title: "Lint refuses circular criteria and records every refusal"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-09
claimed_by: claude 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Lint refuses circular criteria and records every refusal. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 5 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: feature, size L3, candidate 4 of the spec (section 4). Depends on: none (it may run beside steps 2 to 4; it touches only `steps.py`).

In `plugins/sdlc-lite/scripts/steps.py`:
- `lint_steps` (`steps.py:1507-1581`): for each command span of step n, when the span holds `verifier-L` followed by a digit and holds no `step-<m>/` with m other than n, and the criterion line does not end with a held clause (`CLAUSE_RE`, `steps.py:1794`), add the finding `steps: <plan> step <n>: acceptance criterion reads this step's own verifier result, so it can pass only after the verifier passes: <span>` with the hint line `move it to a later step, or declare it held with a trailing [stage: ..., owner: ...] clause`. A span naming `step-<n>/verifier-L...` for its own n is flagged too.
- Refusal record: wherever `lint_or_fail` raises (`steps.py:1584-1587`) and wherever `split` refuses a plan defect (`run_guards`, `steps.py:865-893`, and the red-first refusal), append one JSON line `{"ts": <UTC ISO>, "tool": "steps.py lint" or "steps.py split", "plan": <plan path relative to the task dir's git toplevel>, "step": <n or null>, "text": <first line of the finding>}` per finding to `<task dir>/refusals.jsonl`, skipping a line whose `(plan, text)` is already in the file. The step-handoff link check in `cmd_lint` (`steps.py:1766-1774`) records too. Never record a clean run. Design decision: the record is append-only, lives under `.sdlc` (which every scope criterion excludes), and a write failure (read-only tree) is skipped silently, so no caller's exit code or output changes; it is the only record K-004's early count can read.
Add selftest cases with exactly these labels: `(circ) lint refuses a criterion that reads its own step verifier result`, `(circ) negative control: the same criterion with a held clause passes lint`, `(circ) negative control: a criterion that reads an earlier step verifier result passes lint`, `(circ) a lint refusal appends one line to refusals.jsonl in the task dir`, `(circ) the same refusal of the same plan is written once`. Update the module docstring's lint and split paragraphs (`steps.py:14-60`).

Contract dependents: `dispatch.py prepare` runs `steps.py lint <step dir>` for builder and verifier (`dispatch.py:603-607`); a refusal there now leaves a `refusals.jsonl` line in the task dir under `.sdlc`, which no scope criterion counts (they exclude `.sdlc`). `run_guards` treats a guard that changes the work tree as a defect, but `refusals.jsonl` is written after the guards ran, outside the snapshot. The planner's own probe of `steps.py lint` on a clean plan writes nothing. Validation scope: `steps.py selftest`.

## Read first
- `plugins/sdlc-lite/AGENTS.md`

## Done when
- (red) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && for l in '(circ) lint refuses a criterion that reads its own step verifier result' '(circ) negative control: the same criterion with a held clause passes lint' '(circ) negative control: a criterion that reads an earlier step verifier result passes lint'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && for l in '(circ) a lint refusal appends one line to refusals.jsonl in the task dir' '(circ) the same refusal of the same plan is written once'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py)"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Closed

2026-10-09: delivered by the solo agent (level L3); one independent batched verifier passed before the merge
