---
id: T-0295
title: "steps lint names the handoff heading it found"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When the task handoff lacks the exact heading `steps.py` needs, the refusal names the heading it found instead.

## Context
Maison lost two hours to plan-review loops over `## Task goal` vs `## Goal`. File: plugins/sdlc-lite/scripts/steps.py (lint, precheck, split paths that read the handoff headings). Find where the missing-heading refusal is raised.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a new case: a handoff with `## Task goal` and no `## Goal` makes lint (and the precheck path that reads it) fail with a message naming `## Task goal` as found and `## Goal` as expected.
- [ ] Negative control shown once: without the new message the case fails.
- [ ] The existing message is unchanged when no near heading exists. docs/maintenance/sdlc-internals.md `scripts/steps.py` entry mentions it in one sentence.
