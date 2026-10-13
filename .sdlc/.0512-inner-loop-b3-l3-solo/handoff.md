---
id: T-0512
title: "steps.py lane routes L3 to solo under the inner-loop profile (T-0501 B3)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0510]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Under `profile: inner-loop`, a ticket of size L3 with no merge step and no security word goes to `solo-L3` with the one batched verifier instead of the chain.

## Intent
- Do: in `steps.py` `lane_action` (`:2903`, `LANE_SOLO_SIZES` `:2962`) read the profile and route L3 to solo when the title has no `merge` and the handoff has no security-sensitive word; `steps.py lane` prints the reason. L4 and L5 stay `full`; `ticket_verifier` is unchanged.
- Non-goals: any change to L4 or L5, the verifier level rules, or repos without the profile.
- Done when: a `steps.py selftest` case: L3 with the profile prints `solo`, without it `full`, an L3 titled `merge ...` prints `full`, L4 prints `full` (first case red today); `check.py` exits 0.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. Needs B1 for the profile key (T-0510). Evidence: chain L3 median $13.07 and 74 model minutes against solo L3 $10.91 and 49 (n = 5 [U]), `docs/reports/2026-10-12-ceremony-audit.md` change 3.

## Constraints
One writer on `steps.py`.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with the (lane) inner-loop cases: L3 with the profile solo, without it full, an L3 titled merge full, L4 and L5 full
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: plugins/sdlc-lite/scripts/steps.py:2859: the lane's merge test is a new `\bmerge\b` (case-insensitive, anywhere in the title) while `ticket_verifier` uses `VERIFIER_MERGE_RE = ^Merge\b` (steps.py:3155) and `docs/planning/inner-loop-profile.md:43` named that regex for the lane; an L3 titled "Fix the merge button" therefore stays on the chain under the profile while its verifier level still reads it as no merge ticket. Conservative, and the criterion only asks that a title with merge stays full, so no fail. | plugins/sdlc-lite/scripts/steps.py:2980: the L3 route sits before the `LANE_MAX_TICKET_CRITERIA` cap, which the message at :2989 scopes to L1 and L2, so an L3 profile ticket with many criteria still goes solo; the handoff names no cap for L3.
