---
id: T-0754
title: "steps.py lint flags a criterion that names SDLC_BASE_SHA without a guard"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan or handoff criterion that names `$SDLC_BASE_SHA` cannot pass vacuously when the variable is unset: `steps.py lint` refuses a criterion that names it without a `${SDLC_BASE_SHA:?}` guard or an `export SDLC_BASE_SHA=` in the same criterion.

## Intent
- Do: add the lint rule in `plugins/sdlc-lite/scripts/steps.py` next to the existing `SDLC_BASE_SHA` case (about line 6084), with a message that shows the guarded form. Update the planner's criterion guidance in `plugins/sdlc-lite/agents/planner.md` and `skills/handoff-format/SKILL.md` only if they show an unguarded example (keep the merge-step block identical in both; `check.py` compares them), then regenerate agents.
- Non-goals: rewriting existing closed handoffs.
- Done when: the criteria pass.

## Context
T-0735 verifier (2026-10-24): with the variable unset, `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- plugins 2>/dev/null)"` exits 0 (vacuous pass) while the bare `git diff` exits 128 `bad revision ''`. Roles launched by `dispatch.py prepare` have no SDLC_BASE_SHA; T-0735 added only a brief line telling them to export it.

## Acceptance criteria
1. A `steps.py` selftest case: lint refuses a criterion with an unguarded `$SDLC_BASE_SHA` and accepts the `${SDLC_BASE_SHA:?}` and `export SDLC_BASE_SHA=<sha> &&` forms; with the rule removed the refusal case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/steps.py lint` passes on every open handoff under `docs/work/` (fix any open one it flags).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`steps.py lint` and `split` now refuse a criterion span that names `$SDLC_BASE_SHA` with neither a `${SDLC_BASE_SHA:?}` guard nor an `export SDLC_BASE_SHA=` (or plain `SDLC_BASE_SHA=`) in the same span (`unguarded_base_sha`, beside `pins_sha`). Prose outside a command span is not read.
- Criterion 1: new selftest cases refuse the unguarded `test -z "$(git diff ... "$SDLC_BASE_SHA" ...)"` and `$SDLC_BASE_SHA..HEAD` forms, accept the `${SDLC_BASE_SHA:?}` and `export SDLC_BASE_SHA=HEAD &&` forms and prose. With the rule disabled the selftest printed `steps selftest: FAIL, these did not hold:` and exactly two lines, `(T-0754) lint refuses an unguarded $SDLC_BASE_SHA: ...` for each refusal case; restored, `steps selftest: PASS`. About 14 existing selftest fixtures were guarded to match.
- Criterion 2: no open ticket handoff has `## Step` blocks, so `steps.py lint <dir>` exits 1 on them by design (no Step blocks); the detector run over their command spans flags only prose in Context sections. The one open plan the rule flagged, `docs/work/plan-reliability-docs/planner-L3.md` (8 spans), was guarded and now lints ok.
- Guidance: `agents/planner.md` criteria examples now write `"${SDLC_BASE_SHA:?}"` and state the rule; generated planner agents and Codex TOMLs regenerated; `docs/references/sdlc-internals.md` lists the refusal. The merge-step block had no `SDLC_BASE_SHA`, so it is unchanged.
- Criterion 3: selftest exit 0, `check.py` exit 0, `check-packaging.py` PASS, `git diff --check` exit 0.
