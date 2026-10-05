---
id: T-0231
title: "/sdlc-lite:ask: sweep open questions and blockers, ask once with reasoned options"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:ask` sweeps the thread, task folder, tickets and notes for open questions and blockers and asks them in one AskUserQuestion round with reasoned options, with no dependency on any other plugin.

## Intent
- Do: add plugins/sdlc-lite/skills/ask/SKILL.md (sweep with cited sources, 2 to 4 options each with a one-line consequence, a recommendation only where evidence supports one, one round of 1 to 4 questions with leftover count, a rich-input path because AskUserQuestion has only a plain free-text Other, resolve step); a check.py guard with negative controls; a one-line pointer from skills/open-questions/SKILL.md; the skill listing where the repo lists skills; a live proof.
- Non-goals: any dependency on a harness skill or agent; model or effort defaults; a version bump, tag, push, or publish.
- Done when: the guard bites, check.sh passes, an independent verifier passed with an overall pass, and the live run shows one AskUserQuestion call citing all four planted sources.

## Context
User request 2026-10-05: an improved AskUserQuestion that sweeps for unanswered questions and blockers, reasons its options, and asks for rich text when needed; it must not rely on /harness:... being installed. Size S, solo lane. Philosophy: "Done is better than perfect."

## Constraints
Self-contained. One authoritative place per fact. No em dashes.
