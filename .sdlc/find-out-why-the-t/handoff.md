---
id: T-0105
title: "Find out why the T-0072 background hook did not stop the run in..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0103
---

## Goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Context
Follow-up from T-0103 (run-result-format-check/filer-L1.md):

Find out why the T-0072 background hook did not stop the run in T-0103 (likely an Agent or Monitor background route); confirm after T-0076 ships.

## Question
Why did the abandoned run end its turn with "Waiting for the background job to notify." without the T-0072 hook denying it? Which tool call backgrounded the work (Bash run_in_background, Agent, Monitor, Workflow, or something else), what did the hook see (was it installed, matched, was SDLC_ROLE/SDLC_HEADLESS set, which plugin version was loaded), and does the current hook set (plugins/sdlc-lite/hooks/hooks.json, block-background.sh at 0.11.1) cover that route? If not covered, name the gap precisely for a follow-up ticket.

## Evidence
- Abandoned run transcript: /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.worktrees/ports/.sdlc/sync-ports-2/step-1/builder-L2.log and builder-L2.md (peer repo, plugin 0.9.0 per T-0103). Read-only; never change that repo.
- Hook history in this repo: git log -- plugins/sdlc-lite/hooks/ (T-0072 commit 753993b, T-0076 commit 12c0c9f).
- T-0103 notes: .sdlc/run-result-format-check/filer-L1.md; T-0072: .sdlc/headless-background-abandon/; T-0076: .sdlc/headless-conductors-can-still-abandon/.
- Plugin cache for which version the peer loaded: ~/.claude/plugins (read only).

## Constraints
Read-only investigation. No edits in either repo, no git state changes.
