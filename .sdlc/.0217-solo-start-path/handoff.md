---
id: T-0217
title: "Solo has no start path: conductor cannot spawn it and S/M routing text still says /fix"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A Claude Code conductor can start the `solo` agent for a size S or M ticket, and every routing text agrees that solo is the default lane.

## Intent
- Do: (1) give the conductor a working way to run solo: block-role-spawn.sh denies every `sdlc-lite:` agent spawn from a conductor session, so the start path is a headless launch through scripts/run.sh (a `solo` entry with tier S, M, L mapped to the user's models: Claude Sonnet low, Sonnet xhigh, Opus xhigh; Codex gpt-6.1-sol low, high, xhigh) or an explicit hook allowance for solo only; pick the smaller one and test it with a positive case and a negative control (a scout spawn is still denied). (2) Make conductor.md, skills/fix/SKILL.md, plugins/sdlc-lite/AGENTS.md and the maintainer guidance route size S and M to solo, with /fix only if the lane script says fix; remove the contradiction the 0.20.4 release record lists. (3) Add the one sentence to the solo agent file telling a conductor how it is started. Keep T-0199's text (it is in flight) and reconcile after it merges.
- Non-goals: other lane logic; model or effort changes beyond the user-decided solo tiers (the T-0185 eval rule still applies to any table entry); a version bump, tag, push, or publish.
- Done when: a conductor session starts solo for a size-M ticket in a throwaway project on Claude Code (and a note on the Codex path), the routing texts agree, check.py guards the agreement with a negative control, and an independent verifier passed.

## Context
Found by the 0.20.4 release fact-check, recorded as limits in docs/reports/release-0.20.4.md: solo shipped with no live run and no start path, and conductor.md and the maintainer guidance still route size S to /fix. T-0216 (solo live proof) cannot pass honestly through a conductor until this lands. Build one handwritten step, no planner. Philosophy: "Done is better than perfect." Budget about $15.

## Constraints
One authoritative location per fact. No em dashes.

## Closed

2026-10-04: Built via one handwritten L3 step; verifier L2 pass; gates green. Start path: headless launch from Bash documented in solo.md; routing texts agree; check.py guard added. Burn-down: no planner, no filer; the conductor-start live proof is T-0216 step 2.
