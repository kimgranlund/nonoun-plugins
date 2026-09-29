---
id: T-0168
title: "Decide how publishing works during an unattended run"
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Question
How should `/fix`, `/chain`, and the conductor handle commit, push, and pull request steps when no person is present, for example under an overnight goal?

## Goal
A decision from the user, written back into this file: either unattended runs stop at publish and report, or a recorded approval lets them publish under the same review gate.

## Context
Source: the second report in T-0165, from the gen-ui-kit conductor session on 2026-09-29. The publish approval gate in `/fix` and `/chain` stops every task under an unattended goal, which the reporting session said pushed it toward other plugins' agents that open pull requests themselves.

`/chain` section 7 already says an unattended run publishes nothing. `/fix` step 5 requires an AskUserQuestion approval and has no unattended rule. Publishing follows the user's authorization under the repository guidance, so this is the user's decision.

## Constraints
No publishing rule changes without the user's decision.
