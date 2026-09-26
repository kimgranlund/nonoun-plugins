---
id: T-0099
title: "Add a hook-live-probe.sh selftest case where the hook exits with a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0075
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0075 (confirm-with-a-live-claude/filer-L1.md):

Add a hook-live-probe.sh selftest case where the hook exits with a code other than 2; the step 1 verifier found that removing the rc==2 check leaves the selftest green.

## Constraints
What must not change. "None" if none.
