---
id: T-0766
title: "An inherited red from an earlier step of the same lane routes back into the task"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #74 reports no longer happens (title: An inherited red from an earlier step of the same lane routes back into the task).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/steps.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #74 (quoted):

> **Observed:** step 5's builder reported `inherited red: historical-browser-verification.test.ts ...` and `steps.py next` printed `inherited`, which the conductor rules route to "fix main first / ask the user". The red was caused by step 3 of the same lane (it renamed `.mjs` files to `.ts` while a JSON evidence list still named the `.mjs` paths). Main was green.
>
> **Root cause:** builder rule 8 compares only against `$SDLC_BASE_SHA`, the HEAD the step's build started from (`agents/builder.md:25-26`, same in every level variant); nothing checks the lane's merge-base with its target. `steps.py next` trusts the Status line (`scripts/steps.py:3233-3236`). Guidance: `skills/fanout/SKILL.md:72`, `agents/conductor.md:46`, step-rules item 7.
>
> **Proposed fix:** the builder also runs the failing check at the lane's merge-base with its target branch; green there means a distinct `lane red` status that routes back into the task (rebuild or replan). Keep "fix main first" only when main itself is red.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Reproduced on main: the new selftest cases failed before the fix (an inherited red on a lane-committed base printed `inherited`). Fixed by a mechanism in `steps.py next`, not a new builder Status: on a builder Status or verifier Verdict `inherited red: <tests>`, `lane_red()` checks the step's recorded base-sha against the `into` branch named by `.lane.json` at the base-sha checkout's toplevel. Not an ancestor (an earlier lane step committed under the base) prints `lane red` with the base, `into` and fork point; the conductor replans. No lane record, no base-sha, or a git error keeps `inherited`. No builder rule, `results.py` schema or generated builder changed; `conductor.md` (and its generated Codex TOML), the chain skill, step-rules item 7, `sdlc-internals.md` and the `steps.py` docstring describe the route. The fanout SKILL.md line was left as is: the file is 3 characters under its 18,000 limit, and a lane red never reaches fanout as an inherited outcome.
- Criterion 1: cases `next lane red (T-0766): inherited red on a base an earlier lane step committed, off into -> lane red`, the verifier variant, and an on-`into` control that stays `inherited`. Before the change the selftest printed `steps selftest: FAIL, these did not hold:` with `- next lane red (T-0766): inherited red on a base an earlier lane step committed, off into -> lane red` and `- next lane red (T-0766): a verifier inherited red on a base off into -> lane red`; the control passed.
- Criterion 2: `steps.py selftest` under gate_lock exit 0, `check.py` exit 0, `check-packaging.py` PASS, `git diff --check 73aefc97` exit 0.
- Residual: the selftest does not run a real step through a lane; the records `steps.py next` reads cannot rerun the failing span, so the rule is base provenance, not a rerun at the fork point. A step base that is a resync merge from main is also off `into` and reads `lane red`; the reason prints the fork point so the conductor can confirm.
