---
id: T-0539
title: "Lean work records: a ticket leaves its handoff plus one Outcome; no ceremony files (0.23.0 design)"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L4             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
What is the smallest set of changes that makes a finished ticket leave only its `handoff.md` with an Outcome section in git, stops the ceremony files listed below, and keeps independent verification, cost reporting and recovery working?

## Goal
A build plan for SDLC Lite 0.23.0: lean work records. The objective a role serves is to complete the task, update the ticket, and hand off a clean merge-ready worktree, with minimal documentation.

## Intent
- Do: inventory every file the plugin writes per ticket and outside ticket folders (task folders, step folders, `.sdlc/` top level, project root, `docs/reports/`), naming the writer (script or role brief) and the reader of each. Start from `plugins/sdlc-lite/scripts/` (`dispatch.py`, `run.sh`, `solo_run.py`, `steps.py`, `tickets.py`, `fanout.py`, `redck.py`, `results.py`, `report.py`, `solo_stats.py`) and the role and skill bodies.
- Do: design to the maintainer decisions in `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)": committed = `handoff.md` with an `## Outcome` section; JSON bookkeeping, `runs.jsonl`, `base-sha`, `skips.md` move to a gitignored runtime folder; no filer drafts by default (close writes the Outcome; release notes come from commit subjects); no per-ticket `docs/reports` files; no side files (`process-deviations.md`, `refusals.jsonl`, `red-checkpoint.jsonl`, `hints.md`; a deviation is one Outcome line); roles and skills write nothing at the top of `.sdlc/` or the project root (fleet-retro interview answers go by message).
- Do: say for each reader what replaces its input: `report.py` and `solo_stats.py` cost views, `steps.py` next-action decisions, `dispatch.py` resume and recover, `tickets.py close` checks (filer warnings, skip records, red checkpoint audit), `fleet_collect.py` (it reads other repos' run records), the verifier's evidence.
- Do: review the open queue against this: T-0528, T-0529, T-0530, T-0533, T-0534, T-0535, T-0536, T-0537 (`.sdlc/roadmap.md`). For each: keep, merge into a 0.23.0 ticket, or drop, with one reason. T-0530 adds a lane record and T-0529 adds writing rules, so check them hardest.
- Do: migration for consumer repos: what happens to existing closed ticket folders (leave them), and a one-time command that moves loose top-level `.sdlc` files a role wrote into a place the new rule allows, dry run by default.
- Do: break the build into 3 to 6 tickets with size, files, order and a runnable done-when each, so they can run in waves.
- Non-goals: removing independent verification; changing models; editing any consumer repo.
- Done when: the architect result has the inventory table, the per-reader replacement, the queue verdicts, the migration, and the ticket list; every file in the inventory has a fate (keep, move to runtime, stop).

## Context
Evidence 2026-10-13: a solo ticket here leaves 8 to 10 committed files (`.sdlc/.0531-*`, `.sdlc/.0527-*`); full-chain T-0520 left 34 files, 166 KB (`.sdlc/.0520-ui-designer-agent`). Consumer `.sdlc/` top levels hold 17 to 25 loose files: ui-kit-maison (`/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc`), agent-ui and ultimate-tokens (`fleet-retro-<date>.md` written per our `skills/fleet-retro/interview.md`, plus root-cause, pause, rollout and review notes). Maison's T-0546 items 33 and 42 ask for the same layout rule; its own `.sdlc/AGENTS.md` "Folder layout" section is the working reference. Full chain reason: cross-cutting across scripts, roles, skills and consumer repos.

## Constraints
Preserve independent verification (one verifier per ticket), the recorded build base (`SDLC_BASE_SHA`, which may live in runtime), reference-safe closure and recovery after a host restart. Keep one authoritative location per fact.

## Closed

2026-10-13: design done: build tickets T-0540 to T-0545; T-0529, T-0534, T-0535 merged into them
