---
id: T-0248
title: "Placement proof for the context registry"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Measure whether the context registry (docs/docs-schema/design.md, "The context registry pattern") makes fresh sessions place new documents and records in the right home more often than the same repository without it, on Claude Code and Codex, and record the result.

## Intent
- Do: (1) Build a throwaway fixture repository by hand, with no machinery: `docs/` holding one existing document in each of the nine homes, `docs/layout.md`, a parent `docs/AGENTS.md` with the registry rows, the `## Decide` list and the checklist, a card in each home's `AGENTS.md`, a `CLAUDE.md` of `@AGENTS.md` beside each, and a `.sdlc/` with its own registry in the same layout. Make a control copy with the registry blocks and cards removed and the rest unchanged. (2) Write 12 briefs, each a short request to add one document or record, with the correct home fixed in a sealed answer file before any run: at least one per docs home, 2 boundary briefs with accepted alternates declared in advance, 3 briefs that decide `.sdlc/` versus `docs/`. (3) Run every brief on fresh sessions given only a path inside the folder and the brief, no skill, no other instruction, on: Claude Code headless (`claude -p`), the `solo` agent through `run.sh`-style headless launch, Codex `codex exec` from `docs/`, a Codex native subagent, and an interactive Claude session if one can be driven. Run each brief against the registry copy and the control copy. A session type that cannot run is recorded as a limit with the reason. (4) Score exact home match per brief, per session type, per arm. (5) Write the dated record `docs/reports/placement-proof-live-run.md` (it moves with the validation rename, T-0246), with the fixture, briefs, answer key, per-run placements and the verdict.
- Pass rule, fixed before any run: for a session type, proven only if the registry arm places at least 10 of 12 briefs correctly and beats the control arm by at least 3 briefs. Proven across all types only if every type run passes. One run per cell; claim no significance and say so.
- Negative control: the control arm must misplace more briefs than the registry arm. If it does not, record that the registry is not shown to help.
- Non-goals: building render or drift machinery, editing this repository's `docs/` layout, any version bump, tag, push, or publish.
- Done when: the record is committed with every run's placement and the verdict stated per session type; the design's status line for the pattern is updated in the same change to either "proven" (all required types pass) or "grounded in the cited evidence, placement unproven" with the failing types named; an independent verifier passed.

## Context
From docs/docs-schema/design.md v0.4, "Placement proof". Evidence labels and the host loading facts are in docs/reports/nested-entry-file-loading.md (Codex does not load a nested entry by read, so the parent registry must be enough). This ticket gates the registry parts of T-0242 and T-0243. Solo lane, size M. Philosophy: "Done is better than perfect." Budget: stop and report at $15 for the ticket.

## Constraints
Hand-build the fixture; do not wait on or depend on `docs_check.py` or `render_registry`. Stop only processes you started. No em dashes. Do not touch other agents' worktrees.
