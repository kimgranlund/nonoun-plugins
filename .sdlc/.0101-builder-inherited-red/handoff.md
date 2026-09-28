---
id: T-0101
title: "Builder reports inherited red when a gate is already red at the merge base"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Intent
Literal ask: before claiming a failure, the builder runs the gate at the merge base; if it is already red there, Status is `inherited red: <tests>`, which routes to the conductor (not a replan, rebuild or bump). New status value in builder.md, steps.py next, board.py and chain.
Deltas:
- Which base: defaulted: the committed HEAD the builder started from (pre-build tree, which already holds any main sync), checked in a throwaway worktree under `$SDLC_TMP_WORKTREES` so the builder's own changes are untouched.
- Overlap with `plan defect:` for "findings that predate this build": defaulted: a criterion that is red at the pre-build HEAD for the same failures is `inherited red`, not `plan defect`; `plan defect` keeps parse errors, contradictions, and criteria that are wrong on their face.
- Action name in `steps.py next`: defaulted: a new action `inherited` (first line), distinct from `stop` so the conductor sees the cause; never counted as a fail, never a bump, replan, or rebuild.
- What the conductor does: defaulted: interactive, ask the user (fix main first, rebuild once main is green, or stop); unattended, stop the task and report the inherited tests. No automatic waiver of the gate.
- Verifier side: gap: whether a verifier fail on an inherited red should also route this way; default: out of scope, the verifier is unchanged.
Do: add the `inherited red: <tests>` Status to agents/builder.md (with the pre-build check procedure), teach steps.py `next` (and its selftest) to print `inherited` for it, render it on board.py as 🔴 `inherited red` (with a selftest case), document the action in skills/chain/SKILL.md step 4 and agents/conductor.md routing, update CLAUDE.md/sdlc-lite-author and any check.py guard that lists the action set or Status values.
Non-goals: fixing red gates on main; fanout.py lane behavior; verifier changes; any change to levels or models.
Done when: `plugins/sdlc-lite/scripts/check.sh` passes; `steps.py next` on a step dir whose newest builder Status is `inherited red: x` prints `inherited` and exits 0; board.py renders that step as inherited red; builder.md, chain SKILL.md, and conductor.md all name the status and its routing.

## Context
From peer setup-sdlc-lite-generative-ui, 2026-09-25: about 20 builder stops across 12 gen-ui-system-svelte-lite lanes in one day. Each class cost a stop plus a conductor decision. Ticket ids in parentheses are gen-ui's.

A gate criterion ("npm test exits 0") can go red because of a main sync. Proposal: before claiming a failure, the builder runs the gate at the merge base. If it is already red there, Status is `inherited red: <tests>`, which routes to the conductor (not a replan, rebuild or bump). Needs a new status value in builder.md, steps.py next, board.py and chain (T-0133, T-0009, T-0044).

## Constraints
Existing actions and their routing (build, verify, reverify, rebuild, bump, replan, done, stop) keep their current behavior; a builder Status of `done` or `blocked` parses exactly as before.
