---
id: T-0245
title: "Promotion helper: copy a .sdlc artifact into a docs home with source front matter"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2
depends: [T-0241]   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A small script copies a `.sdlc` artifact into a `docs/` home as a promoted document, with the `source:` front matter that links it back to its ticket.

## Intent
- Do: `promote.py <artifact path> <home> [--slug S] [--ticket T-NNNN]` copies the file to `docs/<home>/` (reports get a YYYY-MM-DD- prefix from today's date), adds front matter with `source:` (ticket id and original file name) and the kind's mandatory keys (status for planning and decisions, date for reports), refuses a home that is not one of the nine kinds or that already holds the target, refuses to overwrite, never edits the ticket's handoff.md (it is frozen once a role reads it), and may append one line to .sdlc/notes.md when asked with `--note`. Selftest with positive cases and negative controls (unknown home, existing target, handoff untouched); wire into check.sh; document the one-line usage in docs/docs-schema/design.md Promotion section.
- Non-goals: any automatic promotion, deleting the .sdlc copy, a version bump, tag, push, or publish.
- Done when: selftest passes, a real promotion of one review result into a throwaway repository produces a file that passes docs_check.py D-3 and D-4, the full check.sh passes, and an independent verifier passed.

## Context
Part of the docs schema design (docs/docs-schema/design.md v0.4 with the user's decisions of 2026-10-05 under Resolved decisions, ticket T-0240), reviewed once (v0.1) by an independent architect (docs/validation/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.
