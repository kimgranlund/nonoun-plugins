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
A repository can bring its existing documents into its stated layout through a generated plan the user approves, with no new broken link and no change to frozen files.

## Intent
- Do: build the plan and apply modes of the `onboard` skill and its script as specified in `docs/repo-onboarding/reorganization.md` (v0.5).
  1. The `docs/layout.md` parser with the grammar and stop conditions in the design.
  2. Inventory: link graph over every tracked Markdown file, and candidates classified as placed, misplaced, or unplaced by globs.
  3. `onboard plan`: one ticket plus `plan.json` with the fields and digest the design defines. Planning again replaces both in the same ticket.
  4. `onboard apply`: the six refusals, `git mv`, the new link rewriter, the final check against the baseline, and restore on failure.
- Non-goals: reusing the `tickets.py` link rewriting; reading content to guess a document type; a role that judges classification or applies the plan; editing `plan.json` by hand; moving or rewriting frozen files; moving documents outside `docs/`.
- Done when: every gate in the design's validation table has a passing positive case and an observed negative control in the script's selftest, and the end-to-end gate passes in a throwaway project.

## Context
Design: `docs/repo-onboarding/reorganization.md`. It depends on `docs/layout.md`, which T-0160 creates.

Evidence: `docs/validation/repo-onboarding-design-review.md` finding 2 showed that `tickets.py` rewriting replaces only the last path component of a cite. `docs/validation/repo-onboarding-design-review-2.md` findings 1 to 4 led to the current running check, plan format, layout grammar, and link baseline.

A run holds a non-blocking exclusive lock on `.run.lock` in its handoff directory (`scripts/run_lifecycle.py`, function `lock`). The file is never deleted, so only a failed lock attempt shows an active run.

This repository is the intended first real trial after the throwaway project. Its mismatches, the paths to list as frozen, and the two links for the baseline are in the design.

Unsettled: whether history stays readable with `git log --follow` after a move plus link rewrite, what share of files the globs leave unplaced, and whether restore is reliable in every failure case.

## Constraints
Nothing moves unless the plan ticket's status is `ready`. Frozen files keep the same content hash. Apply is run in the user's session and never by a role. The script writes nothing under `.sdlc/` except the plan ticket it created.
