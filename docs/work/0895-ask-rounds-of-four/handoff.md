---
id: T-0895
title: "sdlc:ask asks in rounds of 4, up to 20 questions per turn"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-27
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`sdlc:ask` asks up to 20 open items in one turn, as up to 5 AskUserQuestion calls of at most 4 questions each, blockers and highest stakes first. User decision 2026-11-27: "Rounds of 4, up to 20".

## Context
- `AskUserQuestion` takes 1 to 4 questions per call (host schema `maxItems: 4`); each call waits for the answers, so calls in sequence work in one turn.
- `plugins/sdlc/skills/ask/SKILL.md` step 3 ("Ask once", line 42) says "Make exactly ONE AskUserQuestion call of 1 to 4 questions", "With more than 4 items, ask the 4 most consequential and name the rest", and "Never a second round in the same turn". Step 5 and the headless fallback refer to the round too.
- Other skills state their own one-round rules (`open-questions`, `fleet-status`, `review-traces`, `fleet-retro`, `clarify`); they are out of scope.

## Do
1. Rewrite step 3 of `plugins/sdlc/skills/ask/SKILL.md`: up to 5 calls of at most 4 questions, ordered blockers first and highest stakes first across rounds, each round's framing saying where it stands ("round 2 of 3"). More than 20 items: ask the 20 most consequential and name the rest. Skip a later round when an earlier answer settles or moots its items. Keep the plain-text fallback for headless sessions, numbered across all items.
2. Rename the heading to fit ("Ask in rounds" or similar) and update any line in the skill (description, step 5, Unattended) that says one round or 4 at most.
3. If a check or test asserts the old wording, update it.

## Constraints
- Keep the skill's description within the claude.ai limits (`scripts/check-packaging.py` checks them).
- Do not edit any CHANGELOG.

## Acceptance criteria
- `grep -n "ONE AskUserQuestion\|Never a second round" plugins/sdlc/skills/ask/SKILL.md` prints nothing.
- The skill states the 4-per-call limit, the 5-call (20-item) cap, the ordering across rounds and the skip rule.
- `python3 scripts/check-packaging.py` and `git diff --check` pass, and `bash plugins/sdlc/scripts/check.sh --changed` passes.
