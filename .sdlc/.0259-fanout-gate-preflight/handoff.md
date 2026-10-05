---
id: T-0259
title: "fanout needs committed handoffs and node_modules in the gate worktree"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Document, or check up front with a clear message, what the fanout gate worktree needs.

## Context
fanout needs handoffs committed because `.sdlc` is gitignored. Its gate runs in a fresh worktree without `node_modules`; a `node_modules` symlink makes `build-editor-demo --check` fail. Evidence: maison `.worktrees/fanout/logs/gate-a-T-0066-1-a1.log` (`marked/package.json` ENOENT).
Scope: docs or a preflight message only. No fix of the gate itself.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-05: fanout preflight names the force-add and npm ci; fanout selftest case 20; verifier L3 pass in verify-defect-fixes-0.20.10
