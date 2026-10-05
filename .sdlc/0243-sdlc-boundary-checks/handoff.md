---
id: T-0243
title: "The .sdlc boundary checks B-1a, B-2a, B-3a in docs_check.py"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2
depends: [T-0242]   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
docs_check.py also enforces the docs versus .sdlc boundary with checks B-1a, B-2a and B-3a.

## Intent
- Do: add B-1a (a generated-file name under docs/: runs.jsonl, skips.md, <role>-L<n>.md and retries <role>-L<n>-<k>.md, budget-ack.md, *.attempt.json, *.request.json, *.running, *.log), B-2a (in .sdlc/, a Markdown file outside the record types: ticket folders, task folders with a root handoff.md or step-<n>/ folders, messages/, evals/, proposals/, supervisor/, _templates/, a role's decompose/ folder, and loose AGENTS.md, CLAUDE.md, notes.md, roadmap.md, board.md; reported as warning candidates, never blocking) and B-3a (a docs/ file that links to a path under .sdlc/; warning), with selftest positive cases and negative controls, `--only boundary` selection, check.sh wiring, and a check.py guard. Read-only on the target.
- Non-goals: moving or editing files, deciding what a file is for, a version bump, tag, push, or publish.
- Done when: selftest passes, a read-only run on this repository reports the 49 retry files only under .sdlc/ (not as B-1a violations) and counts the B-3a candidates, the full check.sh passes, and an independent verifier passed.

## Context
Part of the docs schema design (docs/docs-schema/design.md v0.4 with the user's decisions of 2026-10-05 under Resolved decisions, ticket T-0240), reviewed once (v0.1) by an independent architect (docs/reports/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
The `.sdlc/layout.md` record-type registry (rows for `NNNN-slug/`, task folders, `.NNNN-slug/`, `messages/`, `evals/`, `proposals/`, `supervisor/`, `notes.md`, `roadmap.md`, `config`), its rendering into `.sdlc/AGENTS.md` by `tickets.py roadmap` through the same `render_registry` function T-0242 builds, the R-1 and R-2 checks on it, and the collapse of long stage ticket lists to counts so the block stays near 60 lines, start only after T-0248 reports a pass. B-1a, B-2a and B-3a do not wait.
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.
