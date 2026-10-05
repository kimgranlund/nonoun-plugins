---
id: T-0271
title: "steps.py lint should enforce plan-defect contract dependents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
steps.py lint refuses a plan that omits a path a verifier `plan defect:` line named.

## Context
Source: maison `.0130` report, draft 3. T-0105 step 3 failed on `scripts/gen-ui-harness/dependencies.json`, which step 1's verifier had already flagged. planner.md "Contract dependents" is advisory only.
Fix: in `lint_steps`, read `step-*/verifier-*.md` and `step-*/builder-*.md` beside the plan, take path tokens from lines starting `plan defect:`, add one finding per token named in no `## Step` block. split inherits it through `lint_or_fail`. Existing selftest fixtures with `plan defect:` lines must name the path or hold no token.

## Constraints
No push, tag, version bump, or publish. No em dashes.
