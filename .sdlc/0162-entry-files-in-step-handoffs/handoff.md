---
id: T-0162
title: "Planner names the entry files each step needs"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A role working on a plan step reads the entry file of each folder the step changes, on Claude Code and on Codex alike.

## Intent
- Do: for each plan step, the planner names the entry file of every folder the step changes, and that list reaches the step handoff.
- Non-goals: relying on host loading; adding a read rule to every role body; listing entries for folders the step only reads.
- Done when: in a live run on each host, a step that changes a file in a folder with an `AGENTS.md` produces a step handoff that names that entry, and the builder's transcript shows it read the file. A step in a folder without an entry names none.

## Context
Decision agreed with the user on 2026-09-29, recorded in `docs/repo-onboarding/design.md` under "How roles reach an entry".

Reason: the loading probe (`docs/validation/nested-entry-file-loading.md`) showed that Codex loads entries only from the repository root down to its working directory, and roles start at the root. Claude Code loads a nested entry only through a `CLAUDE.md` beside it.

Step handoffs are written by `scripts/steps.py split` from the newest planner result, so the list has to be part of the plan format or be added by the split. Which of the two is a plan-time decision. The planner body, the handoff-format skill, and `scripts/check.py` contracts must stay consistent, and generated Codex agents must be regenerated.

On Claude Code a folder in `docs/` with a stub loads its entry automatically as well, so the entry is in context twice. That cost is accepted in the design.

## Constraints
The merge-step template stays consistent across planner and handoff-format. `steps.py` keeps ownership of next-action decisions. Model and effort defaults are unchanged.
