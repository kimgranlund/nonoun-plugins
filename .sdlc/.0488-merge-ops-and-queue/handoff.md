---
id: T-0488
title: "Design: worktree per builder plus a merge queue, and merge-ops as a conductor duty"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
Should every builder work in its own new worktree and join a merge queue when done, so work keeps moving while gates and CI run behind it, and should sdlc-lite declare the logistics (queue, integration to main, gate scheduling, lane cleanup, release cutting) as a conductor duty block, a skill, or a new `merge-ops` role?

## Goal
A written design with a recommendation at `docs/planning/merge-ops-and-queue.md`. No code. It names the smallest first build with a red check.

## Intent
- Do: answer from the code and records. (1) What exists today and who does each logistics job (`fanout.py` run, land, settle, roll; `gate_lock.py`; `lanes.py`; `conductor.md` lines 9, 20, 47, 58; the maintainer by hand). Name the roles that skip worktrees (solo in the main checkout, chain steps). (2) What a merge queue adds beyond an integration branch plus the gate lock: ordering, auto-rebase, retry, a bisect-friendly record of what each gate covered. (3) Costs: more worktrees, rebase conflicts on generated files (`.sdlc/AGENTS.md`, `roadmap.md`, `notes.md`, `check.sh` headers), a red gate blocking later merges. (4) Placement of `merge-ops`: a pipeline role generated per level from `adapters/claude/levels.json`, a session agent like `conductor`, a section in `conductor.md` backed by a skill and scripts, or nothing new. Cost of a new role: a levels row (model and effort are the maintainer's decision), a Codex mapping, evals, `claude_roles.py` and `codex_roles.py` generation. (5) Boundaries: no push, tag or publish without the user; fast-forward only; never delete unmerged work. (6) The overlap and ordering with T-0480 (`docs/planning/light-merge-lane.md`, build T-0481) so the designs do not duplicate.
- Evidence to use: this session's merges (waves 40 to 44): generated-file conflicts at every wave merge, gate waits of 1800 s behind another repo's gates, the policy-reload bug T-0484, lanes left open after land. Count them from `/tmp`-free records: `git log --merges`, `.worktrees/fanout*/logs/fanout.log`, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` finding 7.
- Non-goals: any build; model or effort choices; changing the full-gate-before-ff rule in a consumer repo.
- Done when: the design file answers (1) to (6) with a recommendation each, states what stays project-side, and names the first build ticket with a red check.

## Context
Origin: maintainer question 2026-10-12 ("should we always have builders open a new worktree and add it to a merge queue ... a `merge-ops` agent that manages repo logistics, merge queues and any dev-ops cycle items"). The maintainer's lean, unverified: it is a core conductor duty, not a new agent. Pillars: cost and performance up, resilience must not drop (`docs/specs/sdlc-lite/pillars.md`).

## Constraints
Read-only design, one architect pass, no replan. Plugin size and role count are costs: prefer a section plus skill over a new role unless the evidence says otherwise.

## Closed

2026-10-12: design delivered: docs/planning/merge-ops-and-queue.md; builds filed as T-0489 to T-0492
