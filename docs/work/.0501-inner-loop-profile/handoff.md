---
id: T-0501
title: "Design: an inner-loop conductor profile (local gate setting, pass with notes, UI parity criterion, single merge path) from agent-ui"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
Should SDLC Lite ship a documented conductor profile for iteration, style and fix work (an "inner loop") that sets solo by default, one short brief, a per-repo local gate (check plus touched tests, never the full suite), one light verifier, nits as notes, and a single serial merge path, and what is the smallest first build for each part?

## Goal
A written design with a recommendation per part at `docs/planning/inner-loop-profile.md`. No code.

## Intent
- Do: answer from the code and records, one recommendation each. (1) A per-repo setting in `.sdlc/config` naming the local gate command(s); planner, solo, builder and verifier prompts use it instead of any full-suite `(guard)`; `plan_check.py`/`steps.py lint` refuses a full-suite guard when the setting is present (evidence: 3 to 4 full runs per ticket, 10 to 20 extra minutes at load 30+). (2) A verdict class `pass with notes` in `results.py` for em-dash, stale-count and comment nits: list them, never a rebuild; `fail` only for a red criterion or a real defect (evidence: 4 agent-ui tickets failed only on nits). Compare with T-0496 (tests-gate pilot) so the two do not overlap. (3) Plan criteria that cannot pass: T-0498 covers it, add the agent-ui evidence (T-0069). (4) Stalled agents: `dispatch.py status` already flags `silent` (T-0476, in 0.22.5); decide whether `prepare` should offer a relaunch at a lower level after a silent stop. (5) Merge path: `fanout.py settle --forward` (T-0489, in 0.22.5) as the documented single merge path; decide whether the CI wait that polls until no check is pending is plugin or project side (the agent-ui conductor's first version returned early and left PRs open), and what the stale-base squash needs. (6) A UI-parity criterion type (a screenshot pair, mockup vs real, viewed by the verifier) for tickets with a styling approval: what the handoff form is and what the verifier does. (7) The profile itself: how it is declared (a `profile: inner-loop` line in `.sdlc/config`, or per ticket) and what it sets.
- Non-goals: any build; changing the default profile for repos that do not opt in; model or effort rows; items 7 of the message (lane settings copy: T-filed separately) and 8 (T-0499, done).
- Done when: the design answers (1) to (7), names what stays project-side, orders the builds, and names the first build ticket with a red check. Cost and pillar stated for each part; the profile is opt-in and raises no verification risk for L3 and above.

## Context
Origin: agent-ui conductor message 2026-10-12 and /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-12-12.md. The peer offers to test the profile on agent-ui. Related: T-0496 (verifier by exception pilot), T-0498, T-0476, T-0489, T-0499, `docs/reports/2026-10-12-industry-alternatives-review.md`, `docs/reports/2026-10-12-ceremony-audit.md`.

## Constraints
Read-only design, one architect pass, no replan. Prefer config and existing scripts to new roles.

## Closed

2026-10-12: design delivered: docs/planning/inner-loop-profile.md; builds filed as B1 to B6
