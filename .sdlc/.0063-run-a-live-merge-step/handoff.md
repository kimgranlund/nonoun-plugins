---
id: T-0063
title: "Run a live merge step on a throwaway repo to prove the builder..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0059
---

## Goal
A live merge step, run through run.sh on a throwaway repo, shows the builder makes exactly one two-parent merge commit and the verifier's merge-step criteria pass.

## Context
Follow-up from T-0059 (merge-step-template/filer-L1.md):

Run a live merge step on a throwaway repo to prove the builder makes exactly one two-parent merge commit and the verifier's criteria pass (only static checks were run for T-0059).

## Constraints
No change to the plugin; the run happens in a throwaway repo (/tmp/t0063-merge), and its artifacts are copied into step-1/ here.
