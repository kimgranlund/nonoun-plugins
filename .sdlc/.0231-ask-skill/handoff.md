---
id: T-0231
title: "/sdlc-lite:ask: sweep open questions and blockers, ask once with reasoned options"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

## Verification
Independent L3 verifier (`fable` `xhigh`, `.sdlc/verify-0231/verifier-L3.md`): pass on all 7 criteria, including the full `check.sh` (exit 0) and three on-disk mutations of the guard that each made `check.py` fail. Live run: `docs/reports/ask-skill-live-run.md`. The first live run found two defects in the skill (no concrete sweep searches, no plain-text fallback when `AskUserQuestion` is unavailable); both were fixed once and the rerun found all four planted items. Limits: `AskUserQuestion` itself was not exercised (unavailable in headless `claude -p`), Codex not run.

## Closed

2026-10-05: Built and independently verified (L3 pass, 7 of 7); live run recorded in docs/reports/ask-skill-live-run.md; merged into local main.
