---
id: T-0469
title: "Merge plan skills C: plan_check --summary cost line and controlled-language rules"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0468]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plan_check.py` can print a `--summary` cost line, and plan artifacts follow the controlled-language rules of T-0461, so `/plan` stops computing cost by instruction.

## Intent
- Do: ticket C of the design: `plan_check.py` `--summary` (the cost line from `budget.py` TIERS) with the controlled-language rules for plan artifacts (closed lead verbs in `Do`, declarative Outcome and Goal lines, RFC 2119 words in Authorization) each with an observed-red control; update `skills/plan/references/goal.md` example, `plan-rules.md` and the `cost:` sentence in `skills/plan/SKILL.md` to use the flag; the campaign template and worked example reworded if they fail the verb rule; the five-ask replay recorded.
- Non-goals: any change to `check.py` (C stays out of it so T-0463 can run in parallel).
- Done when: `plan_check.py selftest` with one observed-red control per rule, the item 49 phrase set, `prompt_lint.py`, `check.sh` exit 0; the replay is recorded in the ticket notes.

## Context
Approved design: `.sdlc/.0462-plan-skills-merge-design/architect-L1.md` (read all of it: Approach, Interfaces with the overlap table and the dry-run shape, Constraints, Rejected alternatives, Risks, Carry forward). Maintainer decision 2026-10-12: file A to C, and put the `compaction` kind (T-0465) after A so `skills/plan/SKILL.md` has one writer at a time. Hot files one writer at a time: `plan_check.py`, `check.py`, `core.md`. If the merged `SKILL.md` passes 130 lines, stop and report: the design lists "keep seven skills" as the first alternative to reconsider.

## Constraints
No model or effort change. Old skills stay working until B. The skill stays self-contained (`check.py` item 42). Controlled language per T-0461 for plan artifacts. State only what a file or command shows; the replay is unverified if it was not an independent run.
