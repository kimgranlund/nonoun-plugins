---
id: T-0161
title: "Reorganize documents: scan, plan ticket, approved apply"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A repository can bring its existing documents into its stated layout through a plan the user approves, with no broken link and no change to frozen records.

## Intent
- Do: build the reorganization mode of the `onboard` skill and its script as specified in `docs/repo-onboarding/reorganization.md` (v0.4).
  1. Inventory: tracked Markdown files, classification by path and name rules, link graph, frozen candidates. Read-only.
  2. Plan: a move plan filed as a normal ticket, carrying the inventory digest.
  3. Apply: digest recheck, `git mv`, and a new link rewriter that handles moves across directories and links inside moved files.
  4. Check: every link in every file that is not frozen resolves, and frozen files are byte-identical.
  5. The five refusals listed in the design.
- Non-goals: reusing the `tickets.py` link rewriting; moving or rewriting frozen material; a role that judges classification; applying without an approved ticket.
- Done when: every gate in the design's validation table has a passing positive case and an observed negative control, and the end-to-end run passes in a throwaway project.

## Context
Design: `docs/repo-onboarding/reorganization.md`. It reads the `## Layout` and `## Frozen paths` sections of `docs/AGENTS.md`, which T-0160 creates.

The design review (`docs/validation/repo-onboarding-design-review.md`, finding 2) showed that `tickets.py` rewriting replaces only the last path component of a cite. Running-role detection can use the `.run.lock` and `*.running` markers named in `scripts/run_lifecycle.py`.

This repository is the intended first real trial after the throwaway project. Its mismatches are listed in the design.

Unsettled: whether history stays readable with `git log --follow` after a move plus link rewrite, and what share of files the rules leave unclassified.

## Constraints
Nothing moves before the user approves the plan ticket. Frozen files stay byte-identical. No move runs while a role or benchmark is running. Ticket folders and run records under `.sdlc/` are never moved by this script.
