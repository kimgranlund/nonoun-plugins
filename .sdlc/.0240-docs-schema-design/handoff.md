---
id: T-0240
title: "Design: strict docs/ folder schema and the docs vs .sdlc boundary"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One design doc, docs/docs-schema/design.md, defines a strict folder schema for `docs/`, the hard boundary between `docs/` and `.sdlc/`, the fixed folder names, the override format, the deterministic checks, and a migration path, and files the build tickets for it.

## Intent
- Do: write the design from the repository's own docs, maison's docs and the `.sdlc/` router; get one independent architect review through run.sh and apply its blockers; file build tickets (proposed, one solo step each).
- Non-goals: any implementation, any file move in any repo, a version bump, tag, push, or publish.
- Done when: the design, its review record and the build tickets are merged into local main and this ticket is closed.

## Context
User request 2026-10-05: a schema for `./docs/*`, a stricter view of what lives in `.sdlc/` versus `docs/`, and the folder names to use. Related: docs/repo-onboarding/design.md (current thin default layout, `docs/layout.md` parser in onboard.py), docs/repo-onboarding/reorganization.md (draft), and the reorganization inventory being built on branch reorg-inventory.

## Constraints
Claims only from files read. No em dashes. Budget $12.

## Closed

2026-10-05: Design docs/docs-schema/design.md v0.2 written, independently reviewed (architect L1, ready after fixes, 15 findings applied; docs/validation/docs-schema-design-review.md), build tickets T-0241 to T-0245 filed. Merged into local main.
