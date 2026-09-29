---
id: T-0161
title: "Spike: read-only reorganization plan on this repository"
type: spike        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Question
Which rules let a script classify this repository's documents and produce a move plan that a person would accept, and which of the open findings in the draft design are real in practice?

## Goal
A recommendation with cited evidence, written back into this file: the rules to keep, the rules to change, and whether apply is worth building.

## Context
Draft design: `docs/repo-onboarding/reorganization.md` (v0.6). Three review rounds each found new edge cases, so the user chose on 2026-09-29 to test the rules against real files before specifying more. The design's "Open findings" section lists N1, N2, N3, N5, N8, N9, and N15 from `docs/validation/repo-onboarding-design-review-3.md`.

Build a throwaway prototype that does only the read-only part:

1. Parse `docs/layout.md` with the parser from T-0160.
2. Inventory every tracked Markdown file and build the link graph.
3. Classify the documents under `docs/` as placed, misplaced, or unplaced.
4. Print a plan: moves, link rewrites, unplaced files, frozen candidates, and links that are already broken.

Run it on this repository with a `docs/layout.md` written for the trial. The design's "First trial" section lists the known mismatches, the paths to freeze, and the two links that are already broken.

Answer at least these:

- How many documents are placed, misplaced, and unplaced, and does each proposed move look right to a person?
- How many cites of a moved document are Markdown links, and how many are backticked paths or other forms (N5)?
- Do any of the ambiguous inputs in N2 occur?
- Is a glob on a topic needed (N3)?
- What should hold the plan: a ticket, or a file outside `.sdlc/` (N1, N9, N15)?
- Is apply worth building, or is a reviewed plan that a person carries out by hand enough?

The answer unblocks a later ticket for apply, or a decision to drop it.

## Constraints
Timebox: one working session. No production code lands from a spike. The prototype stays outside the plugin's shipped folders. Nothing in this repository is moved or rewritten. No ticket is created by the prototype.
