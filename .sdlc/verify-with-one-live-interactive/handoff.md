---
id: T-0045
title: "Verify with one live interactive /chain run on a throwaway repo..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0042
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0042 (long-runs-interactive/filer-L1.md):

Verify with one live interactive /chain run on a throwaway repo that a `run_in_background` role run re-invokes the session on exit, as the T-0042 docs assume (the planner flagged this as unverified).

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: keep; one live interactive /chain run on a throwaway repo.

## Closed

2026-09-24: Verified 2026-09-24: run.sh scout L1 launched with run_in_background in a throwaway git repo; the session ended its turn, the completion notification re-invoked it at exit (12 s run), and scout-L1.md was read. Matches the chain, bench and conductor docs.
