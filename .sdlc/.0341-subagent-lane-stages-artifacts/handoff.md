---
id: T-0341
title: "Sub-agent lane commits (fanout prep commit command, the fanout skill's verifier commit, solo sub-agent commits) still use git add -A and can stage *.log and .run.lock"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No lane commit path stages run artifacts that fail repo gates (*.log, .run.lock, *.running), including the sub-agent paths T-0339 left out.

## Intent
- Do: T-0339 fixed only the headless fanout.py lane commit. Replace `git add -A` in the `fanout.py prep` commit command, the fanout skill's verifier commit instruction, and the solo sub-agent commit guidance with a path list or an exclude pathspec (`git add -A -- . ':!*.log' ':!.run.lock' ':!*.running'`), and add a selftest that plants a log and a lock file in a lane tree and checks they are not staged by each path. Update the fanout.py docstring item 4 that still says git add -A.
- Non-goals: model or effort changes.
- Done when:
  - A selftest shows each commit path leaves a planted log and lock unstaged, and fails on the old command (observed).
  - check.py, tickets.py check, fanout and dispatch selftests pass.

## Context
Gap named in docs/reports/2026-10-07-release-0-21-1.md (fact-check pass 5). Origin: ultimate-tokens retro, lane commits staged verifier-L3.log and .run.lock and failed its em-dash gate.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
