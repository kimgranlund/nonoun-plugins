---
id: T-0007
title: "Run the filer headless on a real task to confirm it emits..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0003
---

## Goal
Evidence that a live headless filer (run.sh filer L1) emits a Follow-ups section that `tickets.py close` accepts (top-level bullets or exactly None), so the prose-refusal path is not hit in practice. Done when a fresh live run on a real finished task closes cleanly in a scratch ticket root, recorded in `evidence.md`.

## Context
Follow-up from T-0003 (filer-follow-ups-to-tickets/filer-L1.md):

Run the filer headless on a real task to confirm it emits bullet-only Follow-ups, since `tickets.py close` refuses prose follow-ups (plan risk, untested with a live model).

## Constraints
No code changes. The real task folders and tickets stay untouched; the fresh run happens on a scratch copy.
