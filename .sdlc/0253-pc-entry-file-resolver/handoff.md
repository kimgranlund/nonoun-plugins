---
id: T-0253
title: "Entry-file resolver in onboard.py check"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Extend onboard.py check so every AGENTS.md has a CLAUDE.md importing it and every entry-file link and import resolves.

## Intent
- Do: Add the checks to plugins/sdlc-lite/scripts/onboard.py check (it already walks managed entry files, onboard.py:5,694).
- Non-goals: new script, changing templates.
- Done when: a positive case passes and negative controls (missing CLAUDE.md import, broken link) are rejected, with a selftest.

## Context
Gap analysis R4. Claude Code loads a nested AGENTS.md only through a CLAUDE.md @import (docs/repo-onboarding/layered-context-pattern.md:40; docs/validation/nested-entry-file-loading.md). Coordinate with docs-schema build tickets T-0241 to T-0245; do not duplicate their D-checks. Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.
