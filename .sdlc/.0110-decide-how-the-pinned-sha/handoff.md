---
id: T-0110
title: "Decide how the pinned-sha lint should handle a deliberate commit..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0100
---

## Goal
A plan may keep a deliberate ancestry check against a real commit (`git merge-base --is-ancestor <sha> HEAD`) without `steps.py` refusing it, while every other criterion that pins a commit sha is still refused.

## Context
Follow-up from T-0100 (planner-parallel-safe-criteria/filer-L1.md):

Decide how the pinned-sha lint should handle a deliberate commit reference such as `git merge-base --is-ancestor <real sha> HEAD`, which is now refused with no escape hatch.

## Decision (user, 2026-09-26)
Exempt only the ancestry form: `git merge-base --is-ancestor <sha> HEAD` passes the `pins_sha` lint (scripts/steps.py). Every other pinned sha (`diff`, `<sha>..HEAD`, `<sha>^`, and so on) is still refused. Add selftest cases for both, and update planner rule 6 and CLAUDE.md to match.

## Constraints
- Only the `git merge-base --is-ancestor <sha> HEAD` form is exempt; `git diff <sha>`, `<sha>..HEAD`, `<sha>^`, and any other pinned sha stay refused, including a span that holds the ancestry form plus another pinned sha.
- The other lints (`||` join, fixed-set count, clean porcelain status) and the `bash -n` parse check do not change.
- Paths are under `plugins/sdlc-lite/`. Docs that describe the pinned-sha rule (planner rule 6 in `agents/planner.md`, the steps.py line in the repo `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` if it states the rule) are updated in the same change.
- `plugins/sdlc-lite/scripts/check.sh` stays green.
