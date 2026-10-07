---
id: T-0114
title: "Verifier fail on a gate that is already red at the pre-build HEAD..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0101
---

## Goal
A gate that is already red at the pre-build HEAD is reported as inherited whether the builder or the verifier finds it, so it never costs a rebuild, a level bump, or a replan.

## Intent
Literal ask: decide whether a verifier fail on a gate that is already red at the pre-build HEAD should route to `inherited` too (T-0101 left the verifier unchanged).
Deltas:
- Decide yes or no: gap: the ticket asks for a decision and no person is present; default: yes, mirror the builder. Reason: T-0101's goal is that a gate main already made red is never a build failure or a plan defect, and today agents/verifier.md still sends "fails only on findings that predate the build" to `plan defect:` (a planner L3 replan) and any other red gate to an ordinary fail (rebuild, then bump).
- Verifier output shape: defaulted: the first line under `## Verdict` may be `inherited red: <tests>` (in addition to `pass` and `fail`), listing the failing tests, the same shape as the builder Status; a bare `inherited red` with no colon is a no-verdict (reverify), as for the builder.
- Verifier procedure: defaulted: before failing a gate criterion (a check meant to hold before and after the step, such as a `(guard)` or a repo-wide suite or lint; never a criterion for the step's new behavior), run the same command at the committed HEAD the build started from in a throwaway worktree under `$SDLC_TMP_WORKTREES` (for a merge step, `HEAD^1`), without changing git state; red there with the same failures → `inherited red: <tests>` with both runs as evidence; green there, or different failures → an ordinary fail. The pre-build HEAD is the commit the builder started from; when the builder made no commit it is HEAD.
- Interaction with other criteria: defaulted: if any non-gate criterion also fails, the verdict is `fail` (the build still has work to do); `inherited red` only when every failing criterion is an inherited gate.
- `plan defect:` overlap: defaulted: the verifier's "fails only on findings that predate the build" clause moves from `plan defect` to `inherited red`; `plan defect` keeps criteria that do not parse, contradict another, or are vacuous.
- Routing: defaulted: `steps.py next` prints `inherited` (same action as the builder case) for a newest verifier Verdict `inherited red: ...`; never counted as a fail, never a rebuild, bump, replan, or reverify; conductor handling is the existing `inherited` rule (interactive ask, unattended stop and report).
- run.sh required-section check: defaulted: accepts the new verifier Verdict value.
- board.py: defaulted: renders that step 🔴 inherited red, as for the builder case.
Do: add the pre-build gate check and the `inherited red: <tests>` Verdict to agents/verifier.md (replacing the "predate the build" plan-defect clause); teach steps.py `next` and its selftest to map it to `inherited`; make run.sh accept it; render it in board.py with a selftest case; update skills/chain/SKILL.md step 4, agents/conductor.md, skills/handoff-format (if it lists Verdict values), CLAUDE.md, .claude/agents/sdlc-lite-author.md, and any check.py guard listing Verdict values or the plan-defect clause.
Non-goals: fixing red gates on main; builder changes; fanout.py lane behavior beyond what `steps.py next` already gives it; levels or models.
Done when: `plugins/sdlc-lite/scripts/check.sh` passes; `steps.py next` on a step dir whose newest verifier Verdict is `inherited red: x` prints `inherited` and exits 0, and a verifier `fail` still prints `rebuild`; board.py renders that step as inherited red; verifier.md, chain SKILL.md, and conductor.md name the verdict and its routing.

## Context
Follow-up from T-0101 (builder-inherited-red/filer-L1.md):

Verifier fail on a gate that is already red at the pre-build HEAD still routes as an ordinary fail; T-0101 left the verifier unchanged, so decide whether it should route to `inherited` too.

## Constraints
Existing verdicts and actions keep their routing: a verifier `pass` or `fail` parses exactly as before, and the builder `inherited red` path is unchanged.
