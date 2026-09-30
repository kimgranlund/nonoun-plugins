---
id: T-0157
title: "review-sdlc-traces: find SDLC-caused waste and bugs in project traces"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0155, T-0156]          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Intent
- Do: 6 stages.
  1. `traces.py ingest <repo>`: normalize `*.attempt.json` as the primary attempt source, then join .sdlc/*/ handoffs, `runs.jsonl`, builder and verifier files, base-sha, stream-json transcripts, lane and gate logs, tickets.py state, and git history into one event table (attempt_id, ticket, step, role, level, attempt, verdict, turns, cost, secs, tool calls, exit). Attempt records include interrupted and failed runs that never reached `runs.jsonl`.
  2. `traces.py detect`: deterministic detectors with thresholds, no model. Start set: replan loops and recurring findings; escalation with unchanged verdict; plan-defect refusals by lint rule and criteria that never went red; background polling past timeouts vs host load; cost per verified step vs bench baseline; stray worktrees, tracked runtime files, resets over a dirty tree; stale log lines by run id. Incremental via a cursor in .sdlc/runtime/.
  3. Diagnose: scout or archaeologist at L2 per finding cluster, reading only cited evidence; classify cause as sdlc-lite, project, host, or task text, and name the plugin file or rule at fault.
  4. Verify: an independent verifier reproduces each finding from its evidence or drops it.
  5. Propose: the planner drafts a ticket per confirmed sdlc-lite finding, each with a failing fixture or selftest check.
  6. File: only after user approval via AskUserQuestion. Non-sdlc findings go to a report for the owning repo.
- Non-goals: auto-filing or auto-fixing without approval; editing the analyzed repo.
- Done when: run against the gen-ui-system-svelte-lite overnight traces of 2026-09-28, it independently finds the sdlc-lite items of batch 3 (tickets T-0148 to T-0154) with evidence, and stages 1-2 cost no model calls.

## Context
Design agreed with the user 2026-09-28. Batch 3 was this job done by hand; its source list is in the peer's scratchpad (sdlc-feedback-batch3.md) and lane-*.log files. Fixed findings feed bench/ or selftest fixtures so each detector becomes a guard. Split into stages 1-2 and 3-6 at plan time if needed.

## Constraints
Read-only on the analyzed repo. Model calls capped per run.

## Plan review
- step 2 builder blocked (builder-L2.md, now in step-2.superseded-1/): plan defect: (guard) scope regex `^(plugins/sdlc-lite/scripts/traces/.*)$` rejects `plugins/sdlc-lite/scripts/traces.py` and step 1's `.gitignore` change, because the guard diffs from the chain base SHA, so every later step's scope guard sees earlier steps' files. Scope guards must allow files earlier steps created, or diff from the step's own start. Step 2's attempts.py work is left in the tree.
