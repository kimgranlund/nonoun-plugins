---
id: T-0554
title: "Minimal low-cost CI on release tags, and a private backup push of main each wave"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Main always has an off-machine copy, and a release is checked on a clean machine, at the lowest GitHub-hosted CI cost.

## Intent
- Do: a GitHub Actions workflow that runs only on `v*` tag pushes and on manual `workflow_dispatch`, never on every push or PR: one ubuntu job, the fast tier of `check.sh` (T-0557) plus `scripts/check-packaging.py`, with a short timeout and pip/npm caching only if needed.
- Do: the maintainer wave routine pushes main to a private backup branch `wip/main` after each wave lands (`git push origin main:wip/main --force-with-lease`); the workflow ignores that branch. Note it in the maintainer agent file.
- Non-goals: CI on every push or PR; matrix builds; hosted runners for selftests that need a live Claude or Codex host.
- Done when: the workflow file passes `actionlint` (or a YAML parse) and its triggers are only tags and dispatch; a manual dispatch run passes once; `wip/main` exists on origin after a wave.

## Context
Maintainer 2026-10-14: "we want to keep github hosted CI work as low as possible as it costs $$$". The repo has no `.github/workflows`; main was 81 commits ahead of origin with no off-machine copy; local gates ran 47 min under load.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.
